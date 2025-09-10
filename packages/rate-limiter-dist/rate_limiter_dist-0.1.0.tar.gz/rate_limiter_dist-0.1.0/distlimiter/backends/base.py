"""
Base backend interface for storage systems.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional


class BaseBackend(ABC):
    """
    Base class for all backend storage systems.
    
    All backends must implement the basic storage operations and Lua script execution.
    """
    
    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """
        Get a value from the backend.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The value as a string, or None if not found
        """
        pass
    
    @abstractmethod
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """
        Set a value in the backend.
        
        Args:
            key: The key to set
            value: The value to store
            ttl: Optional TTL in seconds
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """
        Delete a key from the backend.
        
        Args:
            key: The key to delete
        """
        pass
    
    @abstractmethod
    async def execute_lua(self, script: str, keys: List[str], args: List[str]) -> Any:
        """
        Execute a Lua script on the backend.
        
        Args:
            script: The Lua script to execute
            keys: List of keys to pass to the script
            args: List of arguments to pass to the script
            
        Returns:
            The result of the script execution
        """
        pass
    
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in the backend.
        
        Args:
            key: The key to check
            
        Returns:
            True if the key exists, False otherwise
        """
        value = await self.get(key)
        return value is not None
    
    async def increment(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> int:
        """
        Increment a counter in the backend.
        
        Args:
            key: The key to increment
            amount: Amount to increment by (default: 1)
            ttl: Optional TTL in seconds
            
        Returns:
            The new value after increment
        """
        current = await self.get(key)
        if current is None:
            new_value = amount
        else:
            new_value = int(current) + amount
        
        await self.set(key, str(new_value), ttl)
        return new_value
    
    async def expire(self, key: str, ttl: int) -> None:
        """
        Set expiration time for a key.
        
        Args:
            key: The key to set expiration for
            ttl: TTL in seconds
        """
        # This is a default implementation
        # Backends should override if they have a more efficient way
        value = await self.get(key)
        if value is not None:
            await self.set(key, value, ttl)
    
    async def close(self) -> None:
        """
        Close the backend connection.
        
        This method should be called when the backend is no longer needed.
        """
        pass
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
