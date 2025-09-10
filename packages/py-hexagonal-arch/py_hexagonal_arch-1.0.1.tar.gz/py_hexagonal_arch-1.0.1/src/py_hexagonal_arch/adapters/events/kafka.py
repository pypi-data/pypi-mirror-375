"""
Apache Kafka Event Adapter
"""

import json
from typing import Any, Optional, List, Callable, AsyncGenerator

from .base import EventAdapter, EventMessage


class KafkaAdapter(EventAdapter):
    """Apache Kafka adapter"""
    
    def __init__(
        self, 
        bootstrap_servers: str,
        **kwargs: Any
    ):
        try:
            from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
            from aiokafka.admin import AIOKafkaAdminClient, NewTopic
            self.AIOKafkaProducer = AIOKafkaProducer
            self.AIOKafkaConsumer = AIOKafkaConsumer
            self.AIOKafkaAdminClient = AIOKafkaAdminClient
            self.NewTopic = NewTopic
        except ImportError:
            raise ImportError("aiokafka is not installed. Please install it with: pip install aiokafka")
        
        self.bootstrap_servers = bootstrap_servers
        self.config = kwargs
        self.producer = None
        self.admin_client = None
    
    async def connect(self) -> None:
        """Connect to Kafka"""
        if not self.producer:
            self.producer = self.AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=self._serialize_value,
                key_serializer=self._serialize_key,
                **self.config
            )
            await self.producer.start()
        
        if not self.admin_client:
            self.admin_client = self.AIOKafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers
            )
            await self.admin_client.start()
    
    async def disconnect(self) -> None:
        """Disconnect from Kafka"""
        if self.producer:
            await self.producer.stop()
            self.producer = None
        
        if self.admin_client:
            await self.admin_client.close()
            self.admin_client = None
    
    async def publish(self, message: EventMessage) -> None:
        """Publish message to Kafka"""
        if not self.producer:
            await self.connect()
        
        await self.producer.send_and_wait(
            topic=message.topic,
            value=message.data,
            key=message.key,
            headers=[(k, v.encode()) for k, v in message.headers.items()] if message.headers else None,
            timestamp_ms=message.timestamp
        )
    
    async def subscribe(
        self, 
        topic: str, 
        callback: Callable[[EventMessage], None],
        **kwargs: Any
    ) -> None:
        """Subscribe to Kafka topic with callback"""
        consumer = self.AIOKafkaConsumer(
            topic,
            bootstrap_servers=self.bootstrap_servers,
            value_deserializer=self._deserialize_value,
            key_deserializer=self._deserialize_key,
            **kwargs
        )
        
        await consumer.start()
        try:
            async for msg in consumer:
                headers = {k: v.decode() for k, v in msg.headers} if msg.headers else {}
                event_msg = EventMessage(
                    topic=msg.topic,
                    data=msg.value,
                    key=msg.key,
                    headers=headers,
                    timestamp=msg.timestamp
                )
                await callback(event_msg)
        finally:
            await consumer.stop()
    
    async def consume(self, topic: str, **kwargs: Any) -> AsyncGenerator[EventMessage, None]:
        """Consume messages from Kafka topic"""
        consumer = self.AIOKafkaConsumer(
            topic,
            bootstrap_servers=self.bootstrap_servers,
            value_deserializer=self._deserialize_value,
            key_deserializer=self._deserialize_key,
            **kwargs
        )
        
        await consumer.start()
        try:
            async for msg in consumer:
                headers = {k: v.decode() for k, v in msg.headers} if msg.headers else {}
                yield EventMessage(
                    topic=msg.topic,
                    data=msg.value,
                    key=msg.key,
                    headers=headers,
                    timestamp=msg.timestamp
                )
        finally:
            await consumer.stop()
    
    async def create_topic(self, topic: str, **kwargs: Any) -> None:
        """Create Kafka topic"""
        if not self.admin_client:
            await self.connect()
        
        num_partitions = kwargs.get('num_partitions', 1)
        replication_factor = kwargs.get('replication_factor', 1)
        
        topic_obj = self.NewTopic(
            name=topic,
            num_partitions=num_partitions,
            replication_factor=replication_factor
        )
        
        await self.admin_client.create_topics([topic_obj])
    
    async def delete_topic(self, topic: str) -> None:
        """Delete Kafka topic"""
        if not self.admin_client:
            await self.connect()
        
        await self.admin_client.delete_topics([topic])
    
    async def list_topics(self) -> List[str]:
        """List Kafka topics"""
        if not self.admin_client:
            await self.connect()
        
        metadata = await self.admin_client.list_consumer_groups()
        return list(metadata.keys())
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for Kafka"""
        if hasattr(value, 'model_dump'):
            return json.dumps(value.model_dump(), default=str).encode('utf-8')
        return json.dumps(value, default=str).encode('utf-8')
    
    def _serialize_key(self, key: Any) -> Optional[bytes]:
        """Serialize key for Kafka"""
        if key is None:
            return None
        return str(key).encode('utf-8')
    
    def _deserialize_value(self, value: bytes) -> Any:
        """Deserialize value from Kafka"""
        if value is None:
            return None
        return json.loads(value.decode('utf-8'))
    
    def _deserialize_key(self, key: bytes) -> Optional[str]:
        """Deserialize key from Kafka"""
        if key is None:
            return None
        return key.decode('utf-8')
