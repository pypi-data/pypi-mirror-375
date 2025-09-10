"""
Base algorithm interface for rate limiting algorithms.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple
from ..backends.base import BaseBackend


class BaseAlgorithm(ABC):
    """
    Base class for all rate limiting algorithms.
    
    All algorithms must implement the allow() and get_stats() methods.
    """
    
    @abstractmethod
    async def allow(self, backend: BaseBackend, key: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request is allowed.
        
        Args:
            backend: The backend storage system
            key: The key to check
            
        Returns:
            Tuple of (allowed: bool, stats: Dict[str, Any])
        """
        pass
    
    @abstractmethod
    async def get_stats(self, backend: BaseBackend, key: str) -> Dict[str, Any]:
        """
        Get statistics for a key.
        
        Args:
            backend: The backend storage system
            key: The key to get stats for
            
        Returns:
            Dictionary containing statistics
        """
        pass
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get the algorithm parameters.
        
        Returns:
            Dictionary containing algorithm parameters
        """
        return {}
    
    def __str__(self) -> str:
        """String representation of the algorithm."""
        return f"{self.__class__.__name__}({self.get_parameters()})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the algorithm."""
        return self.__str__()
