"""
Hybrid Token + Sliding Window algorithm implementation.

This algorithm combines Token Bucket and Sliding Window for burst + fairness control.
"""

import time
from typing import Any, Dict, Tuple
from .base import BaseAlgorithm
from ..backends.base import BaseBackend
from .token_bucket import TokenBucket
from .sliding_window import SlidingWindow


class Hybrid(BaseAlgorithm):
    """
    Hybrid Token + Sliding Window rate limiting algorithm.
    
    This algorithm combines Token Bucket and Sliding Window for burst + fairness control.
    It allows bursts (via token bucket) while ensuring fairness (via sliding window).
    """
    
    def __init__(self, token_bucket: TokenBucket, sliding_window: SlidingWindow):
        """
        Initialize the hybrid algorithm.
        
        Args:
            token_bucket: Token bucket algorithm for burst control
            sliding_window: Sliding window algorithm for fairness control
        """
        if not isinstance(token_bucket, TokenBucket):
            raise ValueError("token_bucket must be a TokenBucket instance")
        if not isinstance(sliding_window, SlidingWindow):
            raise ValueError("sliding_window must be a SlidingWindow instance")
        
        self.token_bucket = token_bucket
        self.sliding_window = sliding_window
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get algorithm parameters."""
        return {
            "token_bucket": self.token_bucket.get_parameters(),
            "sliding_window": self.sliding_window.get_parameters()
        }
    
    async def allow(self, backend: BaseBackend, key: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request is allowed using both token bucket and sliding window.
        
        Args:
            backend: The backend storage system
            key: The key to check
            
        Returns:
            Tuple of (allowed: bool, stats: Dict[str, Any])
        """
        # Create separate keys for each algorithm
        token_key = f"{key}:token_bucket"
        window_key = f"{key}:sliding_window"
        
        # Check both algorithms
        token_allowed, token_stats = await self.token_bucket.allow(backend, token_key)
        window_allowed, window_stats = await self.sliding_window.allow(backend, window_key)
        
        # Request is allowed only if both algorithms allow it
        allowed = token_allowed and window_allowed
        
        stats = {
            "allowed": allowed,
            "token_bucket": {
                "allowed": token_allowed,
                **token_stats
            },
            "sliding_window": {
                "allowed": window_allowed,
                **window_stats
            },
            "current_time": time.time()
        }
        
        return allowed, stats
    
    async def get_stats(self, backend: BaseBackend, key: str) -> Dict[str, Any]:
        """
        Get statistics for both algorithms.
        
        Args:
            backend: The backend storage system
            key: The key to get stats for
            
        Returns:
            Dictionary containing statistics for both algorithms
        """
        # Create separate keys for each algorithm
        token_key = f"{key}:token_bucket"
        window_key = f"{key}:sliding_window"
        
        # Get stats from both algorithms
        token_stats = await self.token_bucket.get_stats(backend, token_key)
        window_stats = await self.sliding_window.get_stats(backend, window_key)
        
        return {
            "token_bucket": token_stats,
            "sliding_window": window_stats,
            "current_time": time.time()
        }
