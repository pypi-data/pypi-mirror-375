"""
Base Controller module
"""

from typing import TypeVar, Generic, Optional, Any

from pydantic import BaseModel

from ..ports.repository import RepositoryPort, FilterList
from ..ports.cache import CachePort
from ..ports.event import EventPort

T = TypeVar('T', bound=BaseModel)


class BaseController(Generic[T]):
    """Base controller class"""

    def __init__(
        self,
        repository: RepositoryPort[T] | None = None,
        cache: CachePort[T] | None = None,
        event: EventPort[T] | None = None,
    ):
        """..."""

        self.repository = repository
        self.cache = cache
        self.event = event

    async def list(self, filters: Optional[FilterList] = None) -> list[T]:
        """List all items with optional filters"""

        if self.repository is None:
            raise ValueError("Repository is not configured")
        return await self.repository.list(filters)

    async def detail(self, pk: str) -> T:
        """Get item by primary key"""

        if self.cache is not None:
            cached_item = await self.cache.get(pk)
            if cached_item:
                return cached_item

        if self.repository is None:
            raise ValueError("Repository is not configured")
        item = await self.repository.detail(pk)
        
        if item is None:
            raise ValueError(f"Item with pk {pk} not found")
        
        if self.cache is not None:
            await self.cache.set(pk, item)

        return item

    async def create(self, item: T) -> T:
        """Create new item"""

        if self.repository is None:
            raise ValueError("Repository is not configured")
        item = await self.repository.create(item)

        if self.cache is not None:
            await self.cache.set(
                getattr(item, getattr(item, "pk_field")),
                item
            )

        if self.event is not None:
            await self.event.push("create", item.model_dump())

        return item

    async def update(self, pk: str, item_update: Any) -> T:
        """Update item"""

        if self.repository is None:
            raise ValueError("Repository is not configured")
        item = await self.repository.update(pk, item_update)
        
        if self.cache is not None:
            await self.cache.set(pk, item)
        if self.event is not None:
            await self.event.push("update", item.model_dump())

        return item

    async def delete(self, pk: str) -> None:
        """Delete item"""

        if self.repository is None:
            raise ValueError("Repository is not configured")
        await self.repository.delete(pk)
        
        if self.cache is not None:
            await self.cache.delete(pk)
        if self.event is not None:
            await self.event.push("delete", pk)