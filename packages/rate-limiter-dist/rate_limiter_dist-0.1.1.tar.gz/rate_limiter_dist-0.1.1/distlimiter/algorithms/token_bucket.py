"""
Token Bucket algorithm implementation.

This algorithm allows bursts up to the bucket capacity and refills at a steady rate.
"""

import json
import time
from typing import Any, Dict, Tuple
from .base import BaseAlgorithm
from ..backends.base import BaseBackend


class TokenBucket(BaseAlgorithm):
    """
    Token Bucket rate limiting algorithm.
    
    This algorithm maintains a bucket of tokens that are consumed by requests.
    The bucket refills at a steady rate and can handle bursts up to its capacity.
    """
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize the token bucket algorithm.
        
        Args:
            capacity: Maximum number of tokens in the bucket
            refill_rate: Tokens refilled per second
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        if refill_rate <= 0:
            raise ValueError("Refill rate must be positive")
        
        self.capacity = capacity
        self.refill_rate = refill_rate
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get algorithm parameters."""
        return {
            "capacity": self.capacity,
            "refill_rate": self.refill_rate
        }
    
    async def allow(self, backend: BaseBackend, key: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request is allowed by consuming a token from the bucket.
        
        Args:
            backend: The backend storage system
            key: The key to check
            
        Returns:
            Tuple of (allowed: bool, stats: Dict[str, Any])
        """
        current_time = time.time()
        
        # Lua script for atomic token bucket operation
        script = """
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local current_time = tonumber(ARGV[3])
        local tokens_to_consume = tonumber(ARGV[4])
        
        -- Get current bucket state
        local bucket_data = redis.call('GET', key)
        local tokens, last_refill
        
        if bucket_data == false then
            -- Initialize bucket
            tokens = capacity
            last_refill = current_time
        else
            -- Parse existing bucket data
            local data = cjson.decode(bucket_data)
            tokens = data.tokens
            last_refill = data.last_refill
        end
        
        -- Calculate refill
        local time_passed = current_time - last_refill
        local tokens_to_add = time_passed * refill_rate
        tokens = math.min(capacity, tokens + tokens_to_add)
        
        -- Check if we can consume tokens
        if tokens >= tokens_to_consume then
            tokens = tokens - tokens_to_consume
            last_refill = current_time
            
            -- Save updated bucket state
            local new_data = cjson.encode({
                tokens = tokens,
                last_refill = last_refill
            })
            redis.call('SETEX', key, 3600, new_data)
            
            return cjson.encode({
                allowed = true,
                tokens_remaining = tokens,
                tokens_consumed = tokens_to_consume,
                last_refill = last_refill
            })
        else
            -- Cannot consume tokens
            return cjson.encode({
                allowed = false,
                tokens_remaining = tokens,
                tokens_consumed = 0,
                last_refill = last_refill
            })
        end
        """
        
        # Execute the Lua script
        result = await backend.execute_lua(
            script,
            [key],
            [str(self.capacity), str(self.refill_rate), str(current_time), "1"]
        )
        
        # Parse the result
        if isinstance(result, bytes):
            result = result.decode('utf-8')
        
        data = json.loads(result)
        
        stats = {
            "tokens_remaining": data["tokens_remaining"],
            "tokens_consumed": data["tokens_consumed"],
            "capacity": self.capacity,
            "refill_rate": self.refill_rate,
            "last_refill": data["last_refill"],
            "current_time": current_time
        }
        
        return data["allowed"], stats
    
    async def get_stats(self, backend: BaseBackend, key: str) -> Dict[str, Any]:
        """
        Get current bucket statistics.
        
        Args:
            backend: The backend storage system
            key: The key to get stats for
            
        Returns:
            Dictionary containing bucket statistics
        """
        current_time = time.time()
        
        # Get current bucket state
        bucket_data = await backend.get(key)
        
        if bucket_data is None:
            return {
                "tokens_remaining": self.capacity,
                "capacity": self.capacity,
                "refill_rate": self.refill_rate,
                "last_refill": current_time,
                "current_time": current_time,
                "is_empty": False
            }
        
        # Parse bucket data
        data = json.loads(bucket_data)
        tokens = data["tokens"]
        last_refill = data["last_refill"]
        
        # Calculate current tokens with refill
        time_passed = current_time - last_refill
        tokens_to_add = time_passed * self.refill_rate
        current_tokens = min(self.capacity, tokens + tokens_to_add)
        
        return {
            "tokens_remaining": current_tokens,
            "capacity": self.capacity,
            "refill_rate": self.refill_rate,
            "last_refill": last_refill,
            "current_time": current_time,
            "is_empty": current_tokens == 0
        }
