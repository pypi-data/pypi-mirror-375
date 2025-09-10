"""
Redis backend implementation.
"""

import json
import time
from typing import Any, List, Optional
import redis.asyncio as aioredis
from .base import BaseBackend


class RedisBackend(BaseBackend):
    """
    Redis backend implementation using aioredis.
    
    This backend provides atomic operations via Lua scripts and connection pooling
    for efficient distributed rate limiting.
    """
    
    def __init__(
        self,
        url: str = "redis://localhost:6379",
        max_connections: int = 20,
        key_prefix: str = "distlimiter",
        default_ttl: int = 3600,
        **kwargs
    ):
        """
        Initialize the Redis backend.
        
        Args:
            url: Redis connection URL
            max_connections: Maximum number of connections in the pool
            key_prefix: Prefix for all keys to avoid collisions
            default_ttl: Default TTL for keys in seconds
            **kwargs: Additional arguments passed to aioredis.from_url
        """
        self.url = url
        self.max_connections = max_connections
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl
        self.kwargs = kwargs
        self._redis: Optional[aioredis.Redis] = None
        self._connection_pool: Optional[aioredis.ConnectionPool] = None
    
    async def _get_redis(self) -> aioredis.Redis:
        """Get or create the Redis connection."""
        if self._redis is None:
            self._connection_pool = aioredis.ConnectionPool.from_url(
                self.url,
                max_connections=self.max_connections,
                **self.kwargs
            )
            self._redis = aioredis.Redis(connection_pool=self._connection_pool)
        return self._redis
    
    def _make_key(self, key: str) -> str:
        """Create a namespaced key."""
        return f"{self.key_prefix}:{key}"
    
    async def get(self, key: str) -> Optional[str]:
        """Get a value from Redis."""
        redis = await self._get_redis()
        result = await redis.get(self._make_key(key))
        return result.decode('utf-8') if result else None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set a value in Redis with optional TTL."""
        redis = await self._get_redis()
        ttl = ttl or self.default_ttl
        await redis.setex(self._make_key(key), ttl, value)
    
    async def delete(self, key: str) -> None:
        """Delete a key from Redis."""
        redis = await self._get_redis()
        await redis.delete(self._make_key(key))
    
    async def execute_lua(self, script: str, keys: List[str], args: List[str]) -> Any:
        """Execute a Lua script on Redis."""
        redis = await self._get_redis()
        # Add prefix to keys
        prefixed_keys = [self._make_key(key) for key in keys]
        return await redis.eval(script, len(prefixed_keys), *prefixed_keys, *args)
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in Redis."""
        redis = await self._get_redis()
        return bool(await redis.exists(self._make_key(key)))
    
    async def increment(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> int:
        """Increment a counter in Redis atomically."""
        redis = await self._get_redis()
        ttl = ttl or self.default_ttl
        
        # Use Lua script for atomic increment with TTL
        script = """
        local key = KEYS[1]
        local amount = tonumber(ARGV[1])
        local ttl = tonumber(ARGV[2])
        
        local current = redis.call('GET', key)
        if current == false then
            redis.call('SETEX', key, ttl, amount)
            return amount
        else
            local new_value = tonumber(current) + amount
            redis.call('SETEX', key, ttl, new_value)
            return new_value
        end
        """
        
        result = await redis.eval(script, 1, self._make_key(key), amount, ttl)
        return int(result)
    
    async def expire(self, key: str, ttl: int) -> None:
        """Set expiration time for a key."""
        redis = await self._get_redis()
        await redis.expire(self._make_key(key), ttl)
    
    async def zadd(self, key: str, score: float, member: str, ttl: Optional[int] = None) -> None:
        """Add a member to a sorted set with score."""
        redis = await self._get_redis()
        ttl = ttl or self.default_ttl
        await redis.zadd(self._make_key(key), {member: score})
        await redis.expire(self._make_key(key), ttl)
    
    async def zremrangebyscore(self, key: str, min_score: float, max_score: float) -> int:
        """Remove members from a sorted set by score range."""
        redis = await self._get_redis()
        return await redis.zremrangebyscore(self._make_key(key), min_score, max_score)
    
    async def zcard(self, key: str) -> int:
        """Get the number of members in a sorted set."""
        redis = await self._get_redis()
        return await redis.zcard(self._make_key(key))
    
    async def zrange(self, key: str, start: int = 0, end: int = -1) -> List[str]:
        """Get members from a sorted set by index range."""
        redis = await self._get_redis()
        result = await redis.zrange(self._make_key(key), start, end)
        return [item.decode('utf-8') for item in result]
    
    async def zrangebyscore(self, key: str, min_score: float, max_score: float) -> List[str]:
        """Get members from a sorted set by score range."""
        redis = await self._get_redis()
        result = await redis.zrangebyscore(self._make_key(key), min_score, max_score)
        return [item.decode('utf-8') for item in result]
    
    async def close(self) -> None:
        """Close the Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None
        
        if self._connection_pool:
            await self._connection_pool.disconnect()
            self._connection_pool = None
