"""
Core rate limiter implementation.
"""

import time
from typing import Any, Callable, Dict, Optional, Union
from .algorithms.base import BaseAlgorithm
from .backends.base import BaseBackend


class RateLimiter:
    """
    Main rate limiter class that orchestrates algorithms and backends.
    
    This class provides a unified interface for rate limiting using various
    algorithms with different backend storage systems.
    """
    
    def __init__(
        self,
        algorithm: BaseAlgorithm,
        backend: BaseBackend,
        key_prefix: str = "distlimiter",
        default_ttl: int = 3600,
        key_extractor: Optional[Callable] = None
    ):
        """
        Initialize the rate limiter.
        
        Args:
            algorithm: The rate limiting algorithm to use
            backend: The backend storage system
            key_prefix: Prefix for Redis keys to avoid collisions
            default_ttl: Default TTL for keys in seconds
            key_extractor: Optional function to extract key from request object
        """
        self.algorithm = algorithm
        self.backend = backend
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl
        self.key_extractor = key_extractor
    
    def _make_key(self, key: str) -> str:
        """Create a namespaced key for the backend."""
        return f"{self.key_prefix}:{self.algorithm.__class__.__name__.lower()}:{key}"
    
    async def allow(self, key: Union[str, Any]) -> bool:
        """
        Check if a request is allowed based on the rate limiting algorithm.
        
        Args:
            key: The key to check (string or object if key_extractor is provided)
            
        Returns:
            True if the request is allowed, False otherwise
        """
        # Extract key if key_extractor is provided
        if self.key_extractor and not isinstance(key, str):
            key = self.key_extractor(key)
        
        if not isinstance(key, str):
            raise ValueError("Key must be a string or key_extractor must be provided")
        
        # Make the namespaced key
        namespaced_key = self._make_key(key)
        
        # Check with the algorithm
        allowed, stats = await self.algorithm.allow(self.backend, namespaced_key)
        
        return allowed
    
    async def get_stats(self, key: Union[str, Any]) -> Dict[str, Any]:
        """
        Get statistics for a key.
        
        Args:
            key: The key to get stats for
            
        Returns:
            Dictionary containing statistics
        """
        # Extract key if key_extractor is provided
        if self.key_extractor and not isinstance(key, str):
            key = self.key_extractor(key)
        
        if not isinstance(key, str):
            raise ValueError("Key must be a string or key_extractor must be provided")
        
        # Make the namespaced key
        namespaced_key = self._make_key(key)
        
        # Get stats from the algorithm
        stats = await self.algorithm.get_stats(self.backend, namespaced_key)
        
        return {
            "key": key,
            "algorithm": self.algorithm.__class__.__name__,
            "timestamp": time.time(),
            **stats
        }
    
    async def reset(self, key: Union[str, Any]) -> None:
        """
        Reset the rate limit for a key.
        
        Args:
            key: The key to reset
        """
        # Extract key if key_extractor is provided
        if self.key_extractor and not isinstance(key, str):
            key = self.key_extractor(key)
        
        if not isinstance(key, str):
            raise ValueError("Key must be a string or key_extractor must be provided")
        
        # Make the namespaced key
        namespaced_key = self._make_key(key)
        
        # Delete the key from backend
        await self.backend.delete(namespaced_key)
    
    async def get_algorithm_info(self) -> Dict[str, Any]:
        """
        Get information about the current algorithm.
        
        Returns:
            Dictionary containing algorithm information
        """
        return {
            "name": self.algorithm.__class__.__name__,
            "parameters": getattr(self.algorithm, 'get_parameters', lambda: {})(),
            "backend": self.backend.__class__.__name__,
            "key_prefix": self.key_prefix,
            "default_ttl": self.default_ttl
        }
