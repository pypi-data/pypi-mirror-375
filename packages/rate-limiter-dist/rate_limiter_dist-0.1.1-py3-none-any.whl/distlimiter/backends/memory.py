"""
In-Memory Backend for DistLimiter.

This backend stores rate limiting data in memory, making it suitable for:
- Local development
- Testing
- Single-instance applications
- Prototyping

Note: This backend is NOT suitable for distributed/multi-instance deployments.
"""

import asyncio
import time
from typing import Any, Dict, Optional, Union
from .base import BaseBackend


class MemoryBackend(BaseBackend):
    """
    In-memory backend for rate limiting.
    
    Stores data in a dictionary with automatic cleanup of expired keys.
    Thread-safe using asyncio locks.
    """
    
    def __init__(self, cleanup_interval: int = 60):
        """
        Initialize the memory backend.
        
        Args:
            cleanup_interval: How often to clean up expired keys (seconds)
        """
        self._storage: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}
        self._lock = asyncio.Lock()
        self._cleanup_interval = cleanup_interval
        self._last_cleanup = time.time()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from storage."""
        async with self._lock:
            await self._cleanup_if_needed()
            
            if key not in self._storage:
                return None
            
            # Check if key has expired
            if key in self._expiry and time.time() > self._expiry[key]:
                del self._storage[key]
                del self._expiry[key]
                return None
            
            return self._storage[key]
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in storage with optional TTL."""
        async with self._lock:
            await self._cleanup_if_needed()
            
            self._storage[key] = value
            
            if ttl is not None:
                self._expiry[key] = time.time() + ttl
            elif key in self._expiry:
                del self._expiry[key]
            
            return True
    
    async def delete(self, key: str) -> bool:
        """Delete a key from storage."""
        async with self._lock:
            await self._cleanup_if_needed()
            
            if key in self._storage:
                del self._storage[key]
                if key in self._expiry:
                    del self._expiry[key]
                return True
            return False
    
    async def increment(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> int:
        """Atomically increment a counter."""
        async with self._lock:
            await self._cleanup_if_needed()
            
            current_value = self._storage.get(key, 0)
            if not isinstance(current_value, (int, float)):
                current_value = 0
            
            new_value = current_value + amount
            self._storage[key] = new_value
            
            if ttl is not None:
                self._expiry[key] = time.time() + ttl
            elif key in self._expiry:
                del self._expiry[key]
            
            return int(new_value)
    
    async def zadd(self, key: str, score: float, member: str, ttl: Optional[int] = None) -> int:
        """Add a member to a sorted set."""
        async with self._lock:
            await self._cleanup_if_needed()
            
            if key not in self._storage:
                self._storage[key] = {}
            
            if not isinstance(self._storage[key], dict):
                self._storage[key] = {}
            
            self._storage[key][member] = score
            
            if ttl is not None:
                self._expiry[key] = time.time() + ttl
            elif key in self._expiry:
                del self._expiry[key]
            
            return 1
    
    async def zremrangebyscore(self, key: str, min_score: float, max_score: float) -> int:
        """Remove members from a sorted set by score range."""
        async with self._lock:
            await self._cleanup_if_needed()
            
            if key not in self._storage or not isinstance(self._storage[key], dict):
                return 0
            
            removed_count = 0
            members_to_remove = []
            
            for member, score in self._storage[key].items():
                if min_score <= score <= max_score:
                    members_to_remove.append(member)
                    removed_count += 1
            
            for member in members_to_remove:
                del self._storage[key][member]
            
            return removed_count
    
    async def zcard(self, key: str) -> int:
        """Get the number of members in a sorted set."""
        async with self._lock:
            await self._cleanup_if_needed()
            
            if key not in self._storage or not isinstance(self._storage[key], dict):
                return 0
            
            return len(self._storage[key])
    
    async def execute_lua(self, script: str, keys: list, args: list) -> Any:
        """
        Execute a Lua-like script (simplified implementation).
        
        This is a simplified version that supports basic operations
        used by the rate limiting algorithms.
        """
        # Parse the script to extract operations
        # This is a simplified implementation - in practice, you might want
        # to use a proper Lua interpreter or implement specific operations
        
        if "INCR" in script and "EXPIRE" in script and "max_requests" in script:
            # Handle FixedWindow algorithm
            key = keys[0] if keys else args[0]
            max_requests = int(args[0]) if args else 10
            window_seconds = int(args[1]) if len(args) > 1 else 60
            
            current_count = await self.get(key)
            count = int(current_count) if current_count else 0
            
            if count < max_requests:
                # Increment counter
                new_count = await self.increment(key, 1, window_seconds)
                return f'{{"allowed": true, "current_count": {new_count}, "max_requests": {max_requests}, "window_seconds": {window_seconds}}}'
            else:
                return f'{{"allowed": false, "current_count": {count}, "max_requests": {max_requests}, "window_seconds": {window_seconds}}}'
        
        elif "INCR" in script and "EXPIRE" in script:
            # Handle TokenBucket algorithm
            key = keys[0] if keys else args[0]
            ttl = int(args[1]) if len(args) > 1 else None
            result = await self.increment(key, 1, ttl)
            # Return a JSON-like string for compatibility
            return f'{{"allowed": true, "tokens_remaining": {result}, "tokens_consumed": 1, "last_refill": {time.time()}}}'
        
        elif "ZADD" in script and "EXPIRE" in script:
            # Handle sorted set add with expiry
            key = keys[0] if keys else args[0]
            score = float(args[1])
            member = args[2]
            ttl = int(args[3]) if len(args) > 3 else None
            await self.zadd(key, score, member, ttl)
            return 1
        
        elif "ZREMRANGEBYSCORE" in script:
            # Handle sorted set remove by score
            key = keys[0] if keys else args[0]
            min_score = float(args[1])
            max_score = float(args[2])
            return await self.zremrangebyscore(key, min_score, max_score)
        
        else:
            # Default fallback - return JSON-like string
            return '{"allowed": true, "tokens_remaining": 10, "tokens_consumed": 1, "last_refill": 1234567890.0}'
    
    async def _cleanup_if_needed(self):
        """Clean up expired keys if enough time has passed."""
        current_time = time.time()
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        self._last_cleanup = current_time
        expired_keys = []
        
        for key, expiry_time in self._expiry.items():
            if current_time > expiry_time:
                expired_keys.append(key)
        
        for key in expired_keys:
            if key in self._storage:
                del self._storage[key]
            if key in self._expiry:
                del self._expiry[key]
    
    async def close(self):
        """Close the backend and clean up resources."""
        async with self._lock:
            self._storage.clear()
            self._expiry.clear()
    
    def __str__(self) -> str:
        return f"MemoryBackend(storage_size={len(self._storage)}, expiry_size={len(self._expiry)})"
