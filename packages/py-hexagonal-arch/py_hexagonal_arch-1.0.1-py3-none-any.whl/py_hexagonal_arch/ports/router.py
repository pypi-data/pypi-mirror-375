"""
Router Port module
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List

T = TypeVar('T')

class RouterPort(Generic[T], ABC):
    """Router port interface"""
    
    @abstractmethod
    def get_router(self) -> T:
        """Get the FastAPI router instance"""
        pass

    @abstractmethod
    async def create(self, item: T) -> T:
        """Create endpoint handler"""
        pass

    @abstractmethod
    async def list(self) -> List[T]:
        """List endpoint handler"""
        pass

    @abstractmethod
    async def detail(self, pk: str) -> T:
        """Detail endpoint handler"""
        pass

    @abstractmethod
    async def update(self, pk: str, item_update: T) -> T:
        """Update endpoint handler"""
        pass

    @abstractmethod
    async def delete(self, pk: str) -> None:
        """Delete endpoint handler"""
        pass 