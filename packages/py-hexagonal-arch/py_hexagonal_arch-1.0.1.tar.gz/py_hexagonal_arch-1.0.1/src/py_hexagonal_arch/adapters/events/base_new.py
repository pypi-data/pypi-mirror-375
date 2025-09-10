"""
Base Event module with Multi-Backend Messaging Support
"""

import json
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, Any, Type, Dict, List, Callable, AsyncGenerator
from pydantic import BaseModel

from ...ports.event import EventPort
from ...config.settings import settings

T = TypeVar('T', bound=BaseModel)


# ============================================================================
# Event Messaging Abstraction Layer
# ============================================================================

class EventMessage:
    """Event message wrapper"""
    
    def __init__(
        self,
        topic: str,
        data: Any,
        key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timestamp: Optional[int] = None
    ):
        self.topic = topic
        self.data = data
        self.key = key
        self.headers = headers or {}
        self.timestamp = timestamp


class EventAdapter(ABC):
    """Abstract event messaging adapter"""
    
    @abstractmethod
    async def connect(self) -> None:
        """Connect to the messaging system"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the messaging system"""
        pass
    
    @abstractmethod
    async def publish(self, message: EventMessage) -> None:
        """Publish a message to a topic"""
        pass
    
    @abstractmethod
    async def subscribe(
        self, 
        topic: str, 
        callback: Callable[[EventMessage], None],
        **kwargs: Any
    ) -> None:
        """Subscribe to a topic with a callback"""
        pass
    
    @abstractmethod
    async def consume(self, topic: str, **kwargs: Any) -> AsyncGenerator[EventMessage, None]:
        """Consume messages from a topic"""
        pass
    
    @abstractmethod
    async def create_topic(self, topic: str, **kwargs: Any) -> None:
        """Create a topic if supported"""
        pass
    
    @abstractmethod
    async def delete_topic(self, topic: str) -> None:
        """Delete a topic if supported"""
        pass
    
    @abstractmethod
    async def list_topics(self) -> List[str]:
        """List available topics"""
        pass


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


class KinesisAdapter(EventAdapter):
    """AWS Kinesis adapter"""
    
    def __init__(
        self,
        region_name: str = 'us-east-1',
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        **kwargs: Any
    ):
        try:
            import aioboto3
            self.aioboto3 = aioboto3
        except ImportError:
            raise ImportError("aioboto3 is not installed. Please install it with: pip install aioboto3")
        
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.config = kwargs
        self.session = None
    
    async def connect(self) -> None:
        """Connect to AWS Kinesis"""
        if not self.session:
            self.session = self.aioboto3.Session()
    
    async def disconnect(self) -> None:
        """Disconnect from AWS Kinesis"""
        self.session = None
    
    async def publish(self, message: EventMessage) -> None:
        """Publish message to Kinesis stream"""
        if not self.session:
            await self.connect()
        
        async with self.session.client(
            'kinesis',
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        ) as kinesis:
            data = json.dumps(message.data, default=str)
            
            await kinesis.put_record(
                StreamName=message.topic,
                Data=data,
                PartitionKey=message.key or 'default'
            )
    
    async def subscribe(
        self, 
        topic: str, 
        callback: Callable[[EventMessage], None],
        **kwargs: Any
    ) -> None:
        """Subscribe to Kinesis stream with callback"""
        async for message in self.consume(topic, **kwargs):
            await callback(message)
    
    async def consume(self, topic: str, **kwargs: Any) -> AsyncGenerator[EventMessage, None]:
        """Consume messages from Kinesis stream"""
        if not self.session:
            await self.connect()
        
        async with self.session.client(
            'kinesis',
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        ) as kinesis:
            
            # Get shard iterator for latest records
            shards = await kinesis.list_shards(StreamName=topic)
            
            for shard in shards['Shards']:
                shard_iterator_response = await kinesis.get_shard_iterator(
                    StreamName=topic,
                    ShardId=shard['ShardId'],
                    ShardIteratorType='LATEST'
                )
                
                shard_iterator = shard_iterator_response['ShardIterator']
                
                while shard_iterator:
                    records_response = await kinesis.get_records(
                        ShardIterator=shard_iterator,
                        Limit=kwargs.get('limit', 100)
                    )
                    
                    for record in records_response['Records']:
                        data = json.loads(record['Data'])
                        yield EventMessage(
                            topic=topic,
                            data=data,
                            key=record['PartitionKey'],
                            timestamp=int(record['ApproximateArrivalTimestamp'].timestamp())
                        )
                    
                    shard_iterator = records_response.get('NextShardIterator')
                    
                    if not records_response['Records']:
                        break
    
    async def create_topic(self, topic: str, **kwargs: Any) -> None:
        """Create Kinesis stream"""
        if not self.session:
            await self.connect()
        
        async with self.session.client(
            'kinesis',
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        ) as kinesis:
            await kinesis.create_stream(
                StreamName=topic,
                ShardCount=kwargs.get('shard_count', 1)
            )
    
    async def delete_topic(self, topic: str) -> None:
        """Delete Kinesis stream"""
        if not self.session:
            await self.connect()
        
        async with self.session.client(
            'kinesis',
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        ) as kinesis:
            await kinesis.delete_stream(StreamName=topic)
    
    async def list_topics(self) -> List[str]:
        """List Kinesis streams"""
        if not self.session:
            await self.connect()
        
        async with self.session.client(
            'kinesis',
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        ) as kinesis:
            response = await kinesis.list_streams()
            return response['StreamNames']


class PubSubAdapter(EventAdapter):
    """Google Cloud Pub/Sub adapter"""
    
    def __init__(
        self,
        project_id: str,
        credentials_path: Optional[str] = None,
        **kwargs: Any
    ):
        try:
            from google.cloud import pubsub_v1
            from google.auth import load_credentials_from_file
            self.pubsub_v1 = pubsub_v1
            self.load_credentials_from_file = load_credentials_from_file
        except ImportError:
            raise ImportError("google-cloud-pubsub is not installed. Please install it with: pip install google-cloud-pubsub")
        
        self.project_id = project_id
        self.credentials_path = credentials_path
        self.config = kwargs
        self.publisher = None
        self.subscriber = None
    
    async def connect(self) -> None:
        """Connect to Google Cloud Pub/Sub"""
        credentials = None
        if self.credentials_path:
            credentials, _ = self.load_credentials_from_file(self.credentials_path)
        
        self.publisher = self.pubsub_v1.PublisherClient(credentials=credentials)
        self.subscriber = self.pubsub_v1.SubscriberClient(credentials=credentials)
    
    async def disconnect(self) -> None:
        """Disconnect from Google Cloud Pub/Sub"""
        if self.publisher:
            self.publisher.close()
            self.publisher = None
        if self.subscriber:
            self.subscriber.close()
            self.subscriber = None
    
    async def publish(self, message: EventMessage) -> None:
        """Publish message to Pub/Sub topic"""
        if not self.publisher:
            await self.connect()
        
        topic_path = self.publisher.topic_path(self.project_id, message.topic)
        data = json.dumps(message.data, default=str).encode('utf-8')
        
        future = self.publisher.publish(
            topic_path,
            data,
            **message.headers
        )
        
        # Wait for publish to complete
        future.result()
    
    async def subscribe(
        self, 
        topic: str, 
        callback: Callable[[EventMessage], None],
        **kwargs: Any
    ) -> None:
        """Subscribe to Pub/Sub topic with callback"""
        if not self.subscriber:
            await self.connect()
        
        subscription_name = kwargs.get('subscription', f"{topic}_subscription")
        subscription_path = self.subscriber.subscription_path(self.project_id, subscription_name)
        
        def message_handler(message):
            data = json.loads(message.data.decode('utf-8'))
            headers = dict(message.attributes)
            
            event_msg = EventMessage(
                topic=topic,
                data=data,
                key=message.message_id,
                headers=headers,
                timestamp=message.publish_time.timestamp()
            )
            
            # Execute callback (need to handle async)
            import asyncio
            asyncio.create_task(callback(event_msg))
            message.ack()
        
        flow_control = self.pubsub_v1.types.FlowControl(max_messages=kwargs.get('max_messages', 100))
        
        streaming_pull_future = self.subscriber.subscribe(
            subscription_path,
            callback=message_handler,
            flow_control=flow_control
        )
        
        try:
            streaming_pull_future.result()
        except KeyboardInterrupt:
            streaming_pull_future.cancel()
    
    async def consume(self, topic: str, **kwargs: Any) -> AsyncGenerator[EventMessage, None]:
        """Consume messages from Pub/Sub topic"""
        # Pub/Sub doesn't support pull-based consumption in the same way
        # This would typically use the subscribe method instead
        raise NotImplementedError("Pub/Sub uses push-based subscriptions. Use subscribe() instead.")
    
    async def create_topic(self, topic: str, **kwargs: Any) -> None:
        """Create Pub/Sub topic"""
        if not self.publisher:
            await self.connect()
        
        topic_path = self.publisher.topic_path(self.project_id, topic)
        self.publisher.create_topic(request={"name": topic_path})
    
    async def delete_topic(self, topic: str) -> None:
        """Delete Pub/Sub topic"""
        if not self.publisher:
            await self.connect()
        
        topic_path = self.publisher.topic_path(self.project_id, topic)
        self.publisher.delete_topic(request={"topic": topic_path})
    
    async def list_topics(self) -> List[str]:
        """List Pub/Sub topics"""
        if not self.publisher:
            await self.connect()
        
        project_path = f"projects/{self.project_id}"
        topics = self.publisher.list_topics(request={"project": project_path})
        
        return [topic.name.split('/')[-1] for topic in topics]


class EventFactory:
    """Factory for creating event messaging adapters"""
    
    _adapters = {
        'kafka': KafkaAdapter,
        'rabbitmq': RabbitMQAdapter,
        'kinesis': KinesisAdapter,
        'pubsub': PubSubAdapter,
        'memory': InMemoryAdapter,
    }
    
    @classmethod
    def create_adapter(cls, event_type: str, **config: Any) -> EventAdapter:
        """Create an event messaging adapter"""
        if event_type.lower() not in cls._adapters:
            raise ValueError(f"Unsupported event type: {event_type}. Supported: {list(cls._adapters.keys())}")
        
        adapter_class = cls._adapters[event_type.lower()]
        
        if event_type.lower() == 'kafka':
            bootstrap_servers = config.get('bootstrap_servers', settings.kafka_server)
            return adapter_class(bootstrap_servers=bootstrap_servers, **config)
        elif event_type.lower() == 'rabbitmq':
            connection_url = config.get('connection_url', getattr(settings, 'rabbitmq_url', 'amqp://localhost'))
            return adapter_class(connection_url=connection_url, **config)
        elif event_type.lower() == 'kinesis':
            region_name = config.get('region_name', getattr(settings, 'aws_region', 'us-east-1'))
            aws_access_key_id = config.get('aws_access_key_id', getattr(settings, 'aws_access_key_id', None))
            aws_secret_access_key = config.get('aws_secret_access_key', getattr(settings, 'aws_secret_access_key', None))
            return adapter_class(
                region_name=region_name,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                **config
            )
        elif event_type.lower() == 'pubsub':
            project_id = config.get('project_id', getattr(settings, 'gcp_project_id', ''))
            credentials_path = config.get('credentials_path', getattr(settings, 'gcp_credentials_path', None))
            return adapter_class(
                project_id=project_id,
                credentials_path=credentials_path,
                **config
            )
        elif event_type.lower() == 'memory':
            return adapter_class()
        
        return adapter_class(**config)
    
    @classmethod
    def register_adapter(cls, name: str, adapter_class: Type[EventAdapter]) -> None:
        """Register a new event adapter"""
        cls._adapters[name.lower()] = adapter_class


# ============================================================================
# Base Event Implementation
# ============================================================================

class BaseEvent(EventPort[T], Generic[T]):
    """Base event class with multi-backend support"""
    
    def __init__(
        self,
        model: Type[T],
        event_type: str = "kafka",
        topic_prefix: Optional[str] = None,
        **event_config: Any
    ):
        """Initialize event system with model and adapter"""
        self.model = model
        self.topic_prefix = topic_prefix or model.__name__.lower()
        self.event_adapter = EventFactory.create_adapter(event_type, **event_config)
        self._connected = False
    
    async def _ensure_connected(self) -> None:
        """Ensure adapter is connected"""
        if not self._connected:
            await self.event_adapter.connect()
            self._connected = True
    
    async def push(self, topic: str, data: T, key: Optional[str] = None) -> None:
        """Publish event to topic"""
        await self._ensure_connected()
        
        full_topic = f"{self.topic_prefix}.{topic}"
        
        message = EventMessage(
            topic=full_topic,
            data=data.model_dump() if hasattr(data, 'model_dump') else data,
            key=key,
            headers={"model": self.model.__name__}
        )
        
        await self.event_adapter.publish(message)
    
    async def pull(
        self, 
        topic: str, 
        callback: Optional[Callable[[T], None]] = None
    ) -> AsyncGenerator[T, None]:
        """Subscribe to topic and pull events"""
        await self._ensure_connected()
        
        full_topic = f"{self.topic_prefix}.{topic}"
        
        if callback:
            async def wrapper(message: EventMessage):
                try:
                    if hasattr(self.model, 'model_validate'):
                        event_data = self.model.model_validate(message.data)
                    else:
                        event_data = message.data
                    await callback(event_data)
                except Exception as e:
                    print(f"Error processing event: {e}")
            
            await self.event_adapter.subscribe(full_topic, wrapper)
        else:
            async for message in self.event_adapter.consume(full_topic):
                try:
                    if hasattr(self.model, 'model_validate'):
                        event_data = self.model.model_validate(message.data)
                    else:
                        event_data = message.data
                    yield event_data
                except Exception as e:
                    print(f"Error processing event: {e}")
    
    async def create_topic(self, topic: str, **kwargs: Any) -> None:
        """Create topic"""
        await self._ensure_connected()
        full_topic = f"{self.topic_prefix}.{topic}"
        await self.event_adapter.create_topic(full_topic, **kwargs)
    
    async def delete_topic(self, topic: str) -> None:
        """Delete topic"""
        await self._ensure_connected()
        full_topic = f"{self.topic_prefix}.{topic}"
        await self.event_adapter.delete_topic(full_topic)
    
    async def list_topics(self) -> List[str]:
        """List topics"""
        await self._ensure_connected()
        topics = await self.event_adapter.list_topics()
        prefix = f"{self.topic_prefix}."
        return [topic.replace(prefix, '') for topic in topics if topic.startswith(prefix)]
    
    async def disconnect(self) -> None:
        """Disconnect from event system"""
        if self._connected:
            await self.event_adapter.disconnect()
            self._connected = False
