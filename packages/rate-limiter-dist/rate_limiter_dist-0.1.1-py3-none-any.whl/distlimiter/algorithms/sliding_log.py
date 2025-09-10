"""
Sliding Log algorithm implementation.

This algorithm stores individual timestamps of requests for precise rate limiting.
It's memory-heavy but very accurate.
"""

import time
from typing import Any, Dict, Tuple
from .base import BaseAlgorithm
from ..backends.base import BaseBackend


class SlidingLog(BaseAlgorithm):
    """
    Sliding Log rate limiting algorithm.
    
    This algorithm stores individual timestamps of requests for precise rate limiting.
    It's memory-heavy but very accurate. Uses Redis sorted sets for efficient storage.
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        """
        Initialize the sliding log algorithm.
        
        Args:
            max_requests: Maximum number of requests allowed per window
            window_seconds: Window size in seconds
        """
        if max_requests <= 0:
            raise ValueError("Max requests must be positive")
        if window_seconds <= 0:
            raise ValueError("Window seconds must be positive")
        
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get algorithm parameters."""
        return {
            "max_requests": self.max_requests,
            "window_seconds": self.window_seconds
        }
    
    async def allow(self, backend: BaseBackend, key: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request is allowed using sliding log logic.
        
        Args:
            backend: The backend storage system
            key: The key to check
            
        Returns:
            Tuple of (allowed: bool, stats: Dict[str, Any])
        """
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds
        
        # Lua script for atomic sliding log operation
        script = """
        local key = KEYS[1]
        local current_time = tonumber(ARGV[1])
        local cutoff_time = tonumber(ARGV[2])
        local max_requests = tonumber(ARGV[3])
        local window_seconds = tonumber(ARGV[4])
        
        -- Remove old entries outside the window
        redis.call('ZREMRANGEBYSCORE', key, 0, cutoff_time)
        
        -- Count current entries in the window
        local current_count = redis.call('ZCARD', key)
        
        -- Check if we can allow the request
        if current_count < max_requests then
            -- Add current timestamp
            redis.call('ZADD', key, current_time, tostring(current_time))
            -- Set expiration for the key
            redis.call('EXPIRE', key, window_seconds * 2)
            
            return cjson.encode({
                allowed = true,
                current_count = current_count + 1,
                max_requests = max_requests,
                window_seconds = window_seconds,
                cutoff_time = cutoff_time
            })
        else
            return cjson.encode({
                allowed = false,
                current_count = current_count,
                max_requests = max_requests,
                window_seconds = window_seconds,
                cutoff_time = cutoff_time
            })
        end
        """
        
        # Execute the Lua script
        result = await backend.execute_lua(
            script,
            [key],
            [str(current_time), str(cutoff_time), str(self.max_requests), str(self.window_seconds)]
        )
        
        # Parse the result
        if isinstance(result, bytes):
            result = result.decode('utf-8')
        
        import json
        data = json.loads(result)
        
        stats = {
            "current_count": data["current_count"],
            "max_requests": self.max_requests,
            "window_seconds": self.window_seconds,
            "cutoff_time": cutoff_time,
            "current_time": current_time,
            "requests_remaining": max(0, self.max_requests - data["current_count"])
        }
        
        return data["allowed"], stats
    
    async def get_stats(self, backend: BaseBackend, key: str) -> Dict[str, Any]:
        """
        Get current sliding log statistics.
        
        Args:
            backend: The backend storage system
            key: The key to get stats for
            
        Returns:
            Dictionary containing sliding log statistics
        """
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds
        
        # Remove old entries and get current count
        await backend.zremrangebyscore(key, 0, cutoff_time)
        current_count = await backend.zcard(key)
        
        # Get all timestamps in the window
        timestamps = await backend.zrangebyscore(key, cutoff_time, current_time)
        timestamps = [float(ts) for ts in timestamps]
        
        return {
            "current_count": current_count,
            "max_requests": self.max_requests,
            "window_seconds": self.window_seconds,
            "cutoff_time": cutoff_time,
            "current_time": current_time,
            "timestamps": timestamps,
            "requests_remaining": max(0, self.max_requests - current_count),
            "is_limit_exceeded": current_count >= self.max_requests
        }
