"""
Sliding Window Counter algorithm implementation.

This algorithm provides more accurate rate limiting than fixed window by
considering the overlap between windows.
"""

import time
from typing import Any, Dict, Tuple
from .base import BaseAlgorithm
from ..backends.base import BaseBackend


class SlidingWindow(BaseAlgorithm):
    """
    Sliding Window Counter rate limiting algorithm.
    
    This algorithm provides more accurate rate limiting than fixed window
    by considering the overlap between windows and avoiding bursts at boundaries.
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        """
        Initialize the sliding window algorithm.
        
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
    
    def _get_window_keys(self, key: str, current_time: float) -> Tuple[str, str]:
        """Get current and previous window keys."""
        window_size = self.window_seconds
        current_window = int(current_time // window_size)
        previous_window = current_window - 1
        
        current_key = f"{key}:window:{current_window}"
        previous_key = f"{key}:window:{previous_window}"
        
        return current_key, previous_key
    
    async def allow(self, backend: BaseBackend, key: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request is allowed using sliding window logic.
        
        Args:
            backend: The backend storage system
            key: The key to check
            
        Returns:
            Tuple of (allowed: bool, stats: Dict[str, Any])
        """
        current_time = time.time()
        current_key, previous_key = self._get_window_keys(key, current_time)
        
        # Lua script for atomic sliding window operation
        script = """
        local current_key = KEYS[1]
        local previous_key = KEYS[2]
        local max_requests = tonumber(ARGV[1])
        local window_seconds = tonumber(ARGV[2])
        local current_time = tonumber(ARGV[3])
        
        -- Get current window count
        local current_count = redis.call('GET', current_key)
        if current_count == false then
            current_count = 0
        else
            current_count = tonumber(current_count)
        end
        
        -- Get previous window count
        local previous_count = redis.call('GET', previous_key)
        if previous_count == false then
            previous_count = 0
        else
            previous_count = tonumber(previous_count)
        end
        
        -- Calculate sliding window count
        local window_start = math.floor(current_time / window_seconds) * window_seconds
        local time_in_current_window = current_time - window_start
        local weight = time_in_current_window / window_seconds
        
        local sliding_count = current_count + (previous_count * (1 - weight))
        
        -- Check if we can allow the request
        if sliding_count < max_requests then
            -- Increment current window counter
            redis.call('INCR', current_key)
            -- Set expiration for current window
            redis.call('EXPIRE', current_key, window_seconds * 2)
            
            return cjson.encode({
                allowed = true,
                current_count = current_count + 1,
                previous_count = previous_count,
                sliding_count = sliding_count,
                max_requests = max_requests,
                window_seconds = window_seconds,
                weight = weight
            })
        else
            return cjson.encode({
                allowed = false,
                current_count = current_count,
                previous_count = previous_count,
                sliding_count = sliding_count,
                max_requests = max_requests,
                window_seconds = window_seconds,
                weight = weight
            })
        end
        """
        
        # Execute the Lua script
        result = await backend.execute_lua(
            script,
            [current_key, previous_key],
            [str(self.max_requests), str(self.window_seconds), str(current_time)]
        )
        
        # Parse the result
        if isinstance(result, bytes):
            result = result.decode('utf-8')
        
        import json
        data = json.loads(result)
        
        window_start = int(current_time // self.window_seconds) * self.window_seconds
        window_end = window_start + self.window_seconds
        
        stats = {
            "current_count": data["current_count"],
            "previous_count": data["previous_count"],
            "sliding_count": data["sliding_count"],
            "max_requests": self.max_requests,
            "window_seconds": self.window_seconds,
            "window_start": window_start,
            "current_time": current_time,
            "window_end": window_end,
            "weight": data["weight"],
            "requests_remaining": max(0, self.max_requests - data["sliding_count"])
        }
        
        return data["allowed"], stats
    
    async def get_stats(self, backend: BaseBackend, key: str) -> Dict[str, Any]:
        """
        Get current sliding window statistics.
        
        Args:
            backend: The backend storage system
            key: The key to get stats for
            
        Returns:
            Dictionary containing sliding window statistics
        """
        current_time = time.time()
        current_key, previous_key = self._get_window_keys(key, current_time)
        
        # Get current and previous window counts
        current_count = await backend.get(current_key)
        previous_count = await backend.get(previous_key)
        
        current_count = int(current_count) if current_count else 0
        previous_count = int(previous_count) if previous_count else 0
        
        # Calculate sliding window count
        window_start = int(current_time // self.window_seconds) * self.window_seconds
        time_in_current_window = current_time - window_start
        weight = time_in_current_window / self.window_seconds
        
        sliding_count = current_count + (previous_count * (1 - weight))
        window_end = window_start + self.window_seconds
        
        return {
            "current_count": current_count,
            "previous_count": previous_count,
            "sliding_count": sliding_count,
            "max_requests": self.max_requests,
            "window_seconds": self.window_seconds,
            "window_start": window_start,
            "current_time": current_time,
            "window_end": window_end,
            "weight": weight,
            "requests_remaining": max(0, self.max_requests - sliding_count),
            "is_limit_exceeded": sliding_count >= self.max_requests
        }
