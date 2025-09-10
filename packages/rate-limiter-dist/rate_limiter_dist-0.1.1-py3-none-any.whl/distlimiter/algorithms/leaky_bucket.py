"""
Leaky Bucket algorithm implementation.

This algorithm enforces a constant rate and smooths bursts by using a queue
that leaks at a steady rate.
"""

import json
import time
from typing import Any, Dict, Tuple, Optional
from .base import BaseAlgorithm
from ..backends.base import BaseBackend


class LeakyBucket(BaseAlgorithm):
    """
    Leaky Bucket rate limiting algorithm.
    
    This algorithm enforces a constant rate and smooths bursts by using a queue
    that leaks at a steady rate. It's good for smoothing traffic patterns.
    """
    
    def __init__(self, rate: float, capacity: Optional[int] = None):
        """
        Initialize the leaky bucket algorithm.
        
        Args:
            rate: Requests per second (leak rate)
            capacity: Maximum capacity of the bucket (defaults to rate * 2)
        """
        if rate <= 0:
            raise ValueError("Rate must be positive")
        
        self.rate = rate
        self.capacity = capacity or int(rate * 2)
        
        if self.capacity <= 0:
            raise ValueError("Capacity must be positive")
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get algorithm parameters."""
        return {
            "rate": self.rate,
            "capacity": self.capacity
        }
    
    async def allow(self, backend: BaseBackend, key: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request is allowed by adding it to the leaky bucket.
        
        Args:
            backend: The backend storage system
            key: The key to check
            
        Returns:
            Tuple of (allowed: bool, stats: Dict[str, Any])
        """
        current_time = time.time()
        
        # Lua script for atomic leaky bucket operation
        script = """
        local key = KEYS[1]
        local rate = tonumber(ARGV[1])
        local capacity = tonumber(ARGV[2])
        local current_time = tonumber(ARGV[3])
        
        -- Get current bucket state
        local bucket_data = redis.call('GET', key)
        local water_level, last_leak_time
        
        if bucket_data == false then
            -- Initialize bucket
            water_level = 0
            last_leak_time = current_time
        else
            -- Parse existing bucket data
            local data = cjson.decode(bucket_data)
            water_level = data.water_level
            last_leak_time = data.last_leak_time
        end
        
        -- Calculate leaked water
        local time_passed = current_time - last_leak_time
        local leaked_water = time_passed * rate
        water_level = math.max(0, water_level - leaked_water)
        
        -- Check if we can add water (request)
        if water_level < capacity then
            water_level = water_level + 1
            last_leak_time = current_time
            
            -- Save updated bucket state
            local new_data = cjson.encode({
                water_level = water_level,
                last_leak_time = last_leak_time
            })
            redis.call('SETEX', key, 3600, new_data)
            
            return cjson.encode({
                allowed = true,
                water_level = water_level,
                capacity = capacity,
                rate = rate,
                last_leak_time = last_leak_time
            })
        else
            -- Bucket is full
            return cjson.encode({
                allowed = false,
                water_level = water_level,
                capacity = capacity,
                rate = rate,
                last_leak_time = last_leak_time
            })
        end
        """
        
        # Execute the Lua script
        result = await backend.execute_lua(
            script,
            [key],
            [str(self.rate), str(self.capacity), str(current_time)]
        )
        
        # Parse the result
        if isinstance(result, bytes):
            result = result.decode('utf-8')
        
        data = json.loads(result)
        
        stats = {
            "water_level": data["water_level"],
            "capacity": self.capacity,
            "rate": self.rate,
            "last_leak_time": data["last_leak_time"],
            "current_time": current_time,
            "space_remaining": self.capacity - data["water_level"]
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
                "water_level": 0,
                "capacity": self.capacity,
                "rate": self.rate,
                "last_leak_time": current_time,
                "current_time": current_time,
                "space_remaining": self.capacity,
                "is_full": False
            }
        
        # Parse bucket data
        data = json.loads(bucket_data)
        water_level = data["water_level"]
        last_leak_time = data["last_leak_time"]
        
        # Calculate current water level with leakage
        time_passed = current_time - last_leak_time
        leaked_water = time_passed * self.rate
        current_water_level = max(0, water_level - leaked_water)
        
        return {
            "water_level": current_water_level,
            "capacity": self.capacity,
            "rate": self.rate,
            "last_leak_time": last_leak_time,
            "current_time": current_time,
            "space_remaining": self.capacity - current_water_level,
            "is_full": current_water_level >= self.capacity
        }
