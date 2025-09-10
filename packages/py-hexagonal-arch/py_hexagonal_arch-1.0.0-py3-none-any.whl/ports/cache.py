"""
Cache Port module
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional

T = TypeVar('T')

class CachePort(Generic[T], ABC):
    """Cache port interface"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[T]:
        """Get item from cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, data: T) -> None:
        """Set item in cache"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete item from cache"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Clear all cache entries"""
        pass