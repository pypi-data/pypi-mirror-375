"""
RabbitMQ Event Adapter
"""

import json
from typing import Any, Optional, List, Callable, AsyncGenerator

from .base import EventAdapter, EventMessage


class RabbitMQAdapter(EventAdapter):
    """RabbitMQ adapter"""
    
    def __init__(
        self,
        connection_url: str,
        **kwargs: Any
    ):
        try:
            import aio_pika
            self.aio_pika = aio_pika
        except ImportError:
            raise ImportError("aio-pika is not installed. Please install it with: pip install aio-pika")
        
        self.connection_url = connection_url
        self.config = kwargs
        self.connection = None
        self.channel = None
    
    async def connect(self) -> None:
        """Connect to RabbitMQ"""
        if not self.connection:
            self.connection = await self.aio_pika.connect_robust(self.connection_url)
            self.channel = await self.connection.channel()
    
    async def disconnect(self) -> None:
        """Disconnect from RabbitMQ"""
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.channel = None
    
    async def publish(self, message: EventMessage) -> None:
        """Publish message to RabbitMQ"""
        if not self.channel:
            await self.connect()
        
        # Declare exchange and queue
        exchange = await self.channel.declare_exchange(
            message.topic, 
            self.aio_pika.ExchangeType.TOPIC,
            durable=True
        )
        
        # Serialize message
        body = json.dumps(message.data, default=str).encode('utf-8')
        
        # Create message with headers
        msg = self.aio_pika.Message(
            body,
            headers=message.headers,
            message_id=message.key,
            timestamp=message.timestamp
        )
        
        await exchange.publish(msg, routing_key=message.topic)
    
    async def subscribe(
        self, 
        topic: str, 
        callback: Callable[[EventMessage], None],
        **kwargs: Any
    ) -> None:
        """Subscribe to RabbitMQ topic with callback"""
        if not self.channel:
            await self.connect()
        
        exchange = await self.channel.declare_exchange(
            topic, 
            self.aio_pika.ExchangeType.TOPIC,
            durable=True
        )
        
        queue = await self.channel.declare_queue(
            f"{topic}_queue",
            durable=True
        )
        
        await queue.bind(exchange, topic)
        
        async def message_handler(message):
            async with message.process():
                headers = dict(message.headers) if message.headers else {}
                event_msg = EventMessage(
                    topic=topic,
                    data=json.loads(message.body.decode('utf-8')),
                    key=message.message_id,
                    headers=headers,
                    timestamp=message.timestamp.timestamp() if message.timestamp else None
                )
                await callback(event_msg)
        
        await queue.consume(message_handler)
    
    async def consume(self, topic: str, **kwargs: Any) -> AsyncGenerator[EventMessage, None]:
        """Consume messages from RabbitMQ topic"""
        if not self.channel:
            await self.connect()
        
        exchange = await self.channel.declare_exchange(
            topic, 
            self.aio_pika.ExchangeType.TOPIC,
            durable=True
        )
        
        queue = await self.channel.declare_queue(
            f"{topic}_queue",
            durable=True
        )
        
        await queue.bind(exchange, topic)
        
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    headers = dict(message.headers) if message.headers else {}
                    yield EventMessage(
                        topic=topic,
                        data=json.loads(message.body.decode('utf-8')),
                        key=message.message_id,
                        headers=headers,
                        timestamp=message.timestamp.timestamp() if message.timestamp else None
                    )
    
    async def create_topic(self, topic: str, **kwargs: Any) -> None:
        """Create RabbitMQ exchange (topic)"""
        if not self.channel:
            await self.connect()
        
        await self.channel.declare_exchange(
            topic,
            self.aio_pika.ExchangeType.TOPIC,
            durable=kwargs.get('durable', True)
        )
    
    async def delete_topic(self, topic: str) -> None:
        """Delete RabbitMQ exchange"""
        if not self.channel:
            await self.connect()
        
        exchange = await self.channel.get_exchange(topic)
        await exchange.delete()
    
    async def list_topics(self) -> List[str]:
        """List RabbitMQ exchanges (topics)"""
        # RabbitMQ doesn't provide direct API for listing exchanges
        # This would require management API integration
        return []
