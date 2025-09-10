"""
In-Memory Event Adapter
"""

from typing import Any, Dict, List, Callable, AsyncGenerator

from .base import EventAdapter, EventMessage


class InMemoryAdapter(EventAdapter):
    """In-memory event adapter for testing"""
    
    def __init__(self):
        self.topics: Dict[str, List[EventMessage]] = {}
        self.subscribers: Dict[str, List[Callable]] = {}
    
    async def connect(self) -> None:
        """Connect (no-op for in-memory)"""
        pass
    
    async def disconnect(self) -> None:
        """Disconnect (no-op for in-memory)"""
        pass
    
    async def publish(self, message: EventMessage) -> None:
        """Publish message to in-memory topic"""
        if message.topic not in self.topics:
            self.topics[message.topic] = []
        
        self.topics[message.topic].append(message)
        
        # Notify subscribers
        if message.topic in self.subscribers:
            for callback in self.subscribers[message.topic]:
                await callback(message)
    
    async def subscribe(
        self, 
        topic: str, 
        callback: Callable[[EventMessage], None],
        **kwargs: Any
    ) -> None:
        """Subscribe to in-memory topic"""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        
        self.subscribers[topic].append(callback)
    
    async def consume(self, topic: str, **kwargs: Any) -> AsyncGenerator[EventMessage, None]:
        """Consume messages from in-memory topic"""
        if topic in self.topics:
            for message in self.topics[topic]:
                yield message
    
    async def create_topic(self, topic: str, **kwargs: Any) -> None:
        """Create in-memory topic"""
        if topic not in self.topics:
            self.topics[topic] = []
    
    async def delete_topic(self, topic: str) -> None:
        """Delete in-memory topic"""
        self.topics.pop(topic, None)
        self.subscribers.pop(topic, None)
    
    async def list_topics(self) -> List[str]:
        """List in-memory topics"""
        return list(self.topics.keys())
