"""
Base Event module with Multi-Backend Messaging Support
"""

import json
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, Any, Type, Dict, List, Callable, AsyncGenerator
from pydantic import BaseModel

from ports.event import EventPort
from config.settings import settings

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


class EventFactory:
    """Factory for creating event messaging adapters"""
    
    _adapters: Dict[str, Type[EventAdapter]] = {}
    
    @classmethod
    def create_adapter(cls, event_type: str, **config: Any) -> EventAdapter:
        """Create an event messaging adapter"""
        if event_type.lower() not in cls._adapters:
            # Try to import the adapter dynamically
            cls._try_import_adapter(event_type)
            
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
    
    @classmethod
    def _try_import_adapter(cls, event_type: str) -> None:
        """Try to import an adapter dynamically"""
        try:
            if event_type.lower() == 'kafka':
                from .kafka import KafkaAdapter
                cls.register_adapter('kafka', KafkaAdapter)
            elif event_type.lower() == 'rabbitmq':
                from .rabbitmq import RabbitMQAdapter
                cls.register_adapter('rabbitmq', RabbitMQAdapter)
            elif event_type.lower() == 'kinesis':
                from .kinesis import KinesisAdapter
                cls.register_adapter('kinesis', KinesisAdapter)
            elif event_type.lower() == 'pubsub':
                from .pubsub import PubSubAdapter
                cls.register_adapter('pubsub', PubSubAdapter)
            elif event_type.lower() == 'memory':
                from .memory import InMemoryAdapter
                cls.register_adapter('memory', InMemoryAdapter)
        except ImportError:
            pass  # Adapter not available


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
        
        # Use settings default if not specified
        event_type = event_type or settings.event_type
        
        # Apply automatic configuration based on event type
        self._apply_default_config(event_type, event_config)
        
        self.event_adapter = EventFactory.create_adapter(event_type, **event_config)
        self._connected = False
    
    def _apply_default_config(self, event_type: str, event_config: Dict[str, Any]) -> None:
        """Apply default configuration based on event type"""
        if event_type == "rabbitmq" and "connection_url" not in event_config:
            event_config["connection_url"] = settings.rabbitmq_url
        elif event_type == "kinesis":
            if "region_name" not in event_config:
                event_config["region_name"] = settings.aws_region
            if "aws_access_key_id" not in event_config:
                event_config["aws_access_key_id"] = settings.aws_access_key_id
            if "aws_secret_access_key" not in event_config:
                event_config["aws_secret_access_key"] = settings.aws_secret_access_key
        elif event_type == "pubsub":
            if "project_id" not in event_config:
                event_config["project_id"] = settings.gcp_project_id
            if "credentials_path" not in event_config:
                event_config["credentials_path"] = settings.gcp_credentials_path
    
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