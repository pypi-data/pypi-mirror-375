"""
Fixed Window Counter algorithm implementation.

This algorithm uses a simple counter that resets every window period.
"""

import time
from typing import Any, Dict, Tuple
from .base import BaseAlgorithm
from ..backends.base import BaseBackend


class FixedWindow(BaseAlgorithm):
    """
    Fixed Window Counter rate limiting algorithm.
    
    This algorithm uses a simple counter that resets every window period.
    It's simple but can allow bursts at window boundaries.
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        """
        Initialize the fixed window algorithm.
        
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
    
    def _get_window_key(self, key: str, current_time: float) -> str:
        """Get the window key based on current time."""
        window_start = int(current_time // self.window_seconds)
        return f"{key}:window:{window_start}"
    
    async def allow(self, backend: BaseBackend, key: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request is allowed within the current window.
        
        Args:
            backend: The backend storage system
            key: The key to check
            
        Returns:
            Tuple of (allowed: bool, stats: Dict[str, Any])
        """
        current_time = time.time()
        window_key = self._get_window_key(key, current_time)
        
        # Lua script for atomic fixed window operation
        script = """
        local window_key = KEYS[1]
        local max_requests = tonumber(ARGV[1])
        local window_seconds = tonumber(ARGV[2])
        
        -- Get current count
        local current_count = redis.call('GET', window_key)
        if current_count == false then
            current_count = 0
        else
            current_count = tonumber(current_count)
        end
        
        -- Check if we can allow the request
        if current_count < max_requests then
            -- Increment counter
            redis.call('INCR', window_key)
            -- Set expiration for the window
            redis.call('EXPIRE', window_key, window_seconds)
            
            return cjson.encode({
                allowed = true,
                current_count = current_count + 1,
                max_requests = max_requests,
                window_seconds = window_seconds
            })
        else
            return cjson.encode({
                allowed = false,
                current_count = current_count,
                max_requests = max_requests,
                window_seconds = window_seconds
            })
        end
        """
        
        # Execute the Lua script
        result = await backend.execute_lua(
            script,
            [window_key],
            [str(self.max_requests), str(self.window_seconds)]
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
            "window_start": int(current_time // self.window_seconds) * self.window_seconds,
            "current_time": current_time,
            "window_end": (int(current_time // self.window_seconds) + 1) * self.window_seconds
        }
        
        return data["allowed"], stats
    
    async def get_stats(self, backend: BaseBackend, key: str) -> Dict[str, Any]:
        """
        Get current window statistics.
        
        Args:
            backend: The backend storage system
            key: The key to get stats for
            
        Returns:
            Dictionary containing window statistics
        """
        current_time = time.time()
        window_key = self._get_window_key(key, current_time)
        
        # Get current count
        current_count = await backend.get(window_key)
        count = int(current_count) if current_count else 0
        
        window_start = int(current_time // self.window_seconds) * self.window_seconds
        window_end = window_start + self.window_seconds
        
        return {
            "current_count": count,
            "max_requests": self.max_requests,
            "window_seconds": self.window_seconds,
            "window_start": window_start,
            "current_time": current_time,
            "window_end": window_end,
            "requests_remaining": max(0, self.max_requests - count),
            "is_limit_exceeded": count >= self.max_requests
        }
