"""
Repository Port module
"""

from abc import abstractmethod
from typing import TypeVar, Generic, List, Optional, Any
from dataclasses import dataclass

T = TypeVar('T')

@dataclass
class FilterCondition:
    """Filter condition structure"""
    attribute: str
    operator: str
    value: Any

FilterList = List[FilterCondition]

class RepositoryPort(Generic[T]):
    """Repository port interface"""
    
    @abstractmethod
    async def create(self, item: T) -> T:
        """Create a new item"""
        pass
    
    @abstractmethod
    async def list(self, filters: Optional[FilterList] = None) -> List[T]:
        """List all items with optional filters"""
        pass
    
    @abstractmethod
    async def detail(self, pk: str) -> Optional[T]:
        """Get item by primary key"""
        pass
    
    @abstractmethod
    async def update(self, pk: str, item_update: T) -> T:
        """Update an item"""
        pass
    
    @abstractmethod
    async def delete(self, pk: str) -> None:
        """Delete an item"""
        pass 