"""
Event Port module
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, Any, Callable, List, AsyncGenerator

T = TypeVar('T')

class EventPort(Generic[T], ABC):
    """Event port interface"""
    
    @abstractmethod
    async def push(self, topic: str, data: T, key: Optional[str] = None) -> None:
        """Publish event to topic"""
        pass
    
    @abstractmethod
    async def pull(
        self, 
        topic: str, 
        callback: Optional[Callable[[T], None]] = None
    ) -> AsyncGenerator[T, None]:
        """Subscribe to topic and pull events"""
        pass
    
    @abstractmethod
    async def create_topic(self, topic: str, **kwargs: Any) -> None:
        """Create topic"""
        pass
    
    @abstractmethod
    async def delete_topic(self, topic: str) -> None:
        """Delete topic"""
        pass
    
    @abstractmethod
    async def list_topics(self) -> List[str]:
        """List topics"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from event system"""
        pass