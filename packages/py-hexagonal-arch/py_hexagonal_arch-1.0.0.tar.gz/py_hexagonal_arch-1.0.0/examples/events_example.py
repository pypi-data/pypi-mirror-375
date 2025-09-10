"""
Event System Usage Examples

This example demonstrates how to use the refactored event system
with different messaging backends (Kafka, RabbitMQ, Kinesis, Pub/Sub).
"""

import asyncio
from typing import Optional
from pydantic import BaseModel

# Import the event components
from src.adapters.events import BaseEvent, EventFactory, EventMessage
from src.adapters.events.user import UserEvent
from src.models.user import User


class OrderEvent(BaseModel):
    """Example order event model"""
    id: str
    user_id: str
    product_id: str
    quantity: int
    total: float
    status: str


class OrderEventHandler(BaseEvent[OrderEvent]):
    """Order-specific event handler"""
    
    def __init__(self, event_type: str = "kafka", **kwargs):
        super().__init__(
            model=OrderEvent,
            event_type=event_type,
            topic_prefix="order",
            **kwargs
        )
        # Note: Automatic configuration for AWS, GCP, etc. is now handled by BaseEvent


async def example_kafka_events():
    """Example using Kafka events"""
    print("=== Kafka Event System Example ===")
    
    try:
        # Create user event handler
        user_events = UserEvent(event_type="kafka")
        
        # Create a test user event
        user = User(id="1", name="John Doe", email="john@example.com")
        
        # Publish user created event
        await user_events.push("created", user, key=user.id)
        print(f"Published user created event: {user.name}")
        
        # Create topic for user updates
        await user_events.create_topic("updated")
        print("Created user.updated topic")
        
        # List topics
        topics = await user_events.list_topics()
        print(f"Available topics: {topics}")
        
        # Subscribe to user events with callback
        async def user_callback(user_data: User):
            print(f"Received user event: {user_data.name} ({user_data.email})")
        
        # Note: In real usage, this would run in a separate task
        # await user_events.pull("created", callback=user_callback)
        
        await user_events.disconnect()
        
    except ImportError as e:
        print(f"Kafka not available: {e}")
    except Exception as e:
        print(f"Kafka error (server might not be running): {e}")
    
    print()


async def example_rabbitmq_events():
    """Example using RabbitMQ events"""
    print("=== RabbitMQ Event System Example ===")
    
    try:
        # Create order event handler with RabbitMQ
        order_events = OrderEventHandler(
            event_type="rabbitmq",
            connection_url="amqp://localhost:5672"
        )
        
        # Create a test order event
        order = OrderEvent(
            id="order-123",
            user_id="user-1",
            product_id="prod-456",
            quantity=2,
            total=99.98,
            status="pending"
        )
        
        # Publish order created event
        await order_events.push("created", order, key=order.id)
        print(f"Published order created event: {order.id}")
        
        # Publish order updated event
        order.status = "confirmed"
        await order_events.push("updated", order, key=order.id)
        print(f"Published order updated event: {order.id}")
        
        await order_events.disconnect()
        
    except ImportError as e:
        print(f"RabbitMQ not available: {e}")
    except Exception as e:
        print(f"RabbitMQ error (server might not be running): {e}")
    
    print()


async def example_kinesis_events():
    """Example using AWS Kinesis events"""
    print("=== AWS Kinesis Event System Example ===")
    
    try:
        # Create user event handler with Kinesis
        # Credentials are automatically loaded from settings/environment
        user_events = UserEvent(event_type="kinesis")
        
        # Create a test user event
        user = User(id="2", name="Alice Smith", email="alice@example.com")
        
        # Create stream (topic)
        await user_events.create_topic("profile_updates", shard_count=1)
        print("Created user.profile_updates stream")
        
        # Publish user profile update event
        await user_events.push("profile_updates", user, key=user.id)
        print(f"Published user profile update to Kinesis: {user.name}")
        
        # List streams
        streams = await user_events.list_topics()
        print(f"Available streams: {streams}")
        
        await user_events.disconnect()
        
    except ImportError as e:
        print(f"AWS Kinesis not available: {e}")
    except Exception as e:
        print(f"Kinesis error (AWS credentials or region might be invalid): {e}")
    
    print()


async def example_pubsub_events():
    """Example using Google Cloud Pub/Sub events"""
    print("=== Google Cloud Pub/Sub Event System Example ===")
    
    try:
        # Create order event handler with Pub/Sub
        # Project ID and credentials are automatically loaded from settings/environment
        order_events = OrderEventHandler(event_type="pubsub")
        
        # Create a test order event
        order = OrderEvent(
            id="order-789",
            user_id="user-2",
            product_id="prod-123",
            quantity=1,
            total=49.99,
            status="processing"
        )
        
        # Create topic
        await order_events.create_topic("status_updates")
        print("Created order.status_updates topic")
        
        # Publish order status update
        await order_events.push("status_updates", order, key=order.id)
        print(f"Published order status update to Pub/Sub: {order.id}")
        
        # List topics
        topics = await order_events.list_topics()
        print(f"Available topics: {topics}")
        
        await order_events.disconnect()
        
    except ImportError as e:
        print(f"Google Cloud Pub/Sub not available: {e}")
    except Exception as e:
        print(f"Pub/Sub error (GCP credentials might be invalid): {e}")
    
    print()


async def example_memory_events():
    """Example using in-memory events"""
    print("=== In-Memory Event System Example ===")
    
    # Create user event handler with in-memory backend
    user_events = UserEvent(event_type="memory")
    
    # Create test users
    users = [
        User(id="1", name="Bob Wilson", email="bob@example.com"),
        User(id="2", name="Carol Davis", email="carol@example.com"),
        User(id="3", name="David Brown", email="david@example.com")
    ]
    
    # Publish multiple user events
    for user in users:
        await user_events.push("registered", user, key=user.id)
        print(f"Published user registered event: {user.name}")
    
    # Set up subscription with callback
    received_events = []
    
    async def user_callback(user_data: User):
        received_events.append(user_data)
        print(f"Callback received: {user_data.name}")
    
    # Subscribe to events (in-memory will immediately call callback for existing events)
    await user_events.event_adapter.subscribe("user.registered", lambda msg: user_callback(User.model_validate(msg.data)))
    
    # Consume events using async generator
    print("\nConsuming events:")
    async for user_data in user_events.pull("registered"):
        print(f"Consumed event: {user_data.name}")
        break  # Just show first one to avoid infinite loop
    
    # List topics
    topics = await user_events.list_topics()
    print(f"Available topics: {topics}")
    
    await user_events.disconnect()
    print()


async def example_factory_usage():
    """Example showing direct factory usage"""
    print("=== Factory Usage Example ===")
    
    # Create different event adapters directly
    kafka_adapter = EventFactory.create_adapter("kafka", bootstrap_servers="localhost:9092")
    memory_adapter = EventFactory.create_adapter("memory")
    
    # Use adapters directly (lower-level operations)
    # EventMessage already imported above
    
    # Create test message
    message = EventMessage(
        topic="test.direct",
        data={"message": "Hello from factory!", "timestamp": "2024-01-01T12:00:00Z"},
        key="test-key",
        headers={"source": "factory_example"}
    )
    
    # Publish to memory adapter
    await memory_adapter.connect()
    await memory_adapter.publish(message)
    print("Published message via memory adapter")
    
    # Consume from memory adapter
    async for received_message in memory_adapter.consume("test.direct"):
        print(f"Received via memory adapter: {received_message.data}")
        break
    
    await memory_adapter.disconnect()
    print()


async def example_custom_adapter():
    """Example showing how to register a custom adapter"""
    print("=== Custom Adapter Example ===")
    
    from src.adapters.events import EventAdapter
    from typing import AsyncGenerator, Callable
    
    class LoggingEventAdapter(EventAdapter):
        """An event adapter that logs all operations"""
        
        def __init__(self):
            self.events = []
        
        async def connect(self) -> None:
            print("[LOG] Connecting to logging adapter")
        
        async def disconnect(self) -> None:
            print("[LOG] Disconnecting from logging adapter")
        
        async def publish(self, message: EventMessage) -> None:
            print(f"[LOG] Publishing to {message.topic}: {message.data}")
            self.events.append(message)
        
        async def subscribe(
            self, 
            topic: str, 
            callback: Callable[[EventMessage], None],
            **kwargs
        ) -> None:
            print(f"[LOG] Subscribing to {topic}")
            for event in self.events:
                if event.topic == topic:
                    await callback(event)
        
        async def consume(self, topic: str, **kwargs) -> AsyncGenerator[EventMessage, None]:
            print(f"[LOG] Consuming from {topic}")
            for event in self.events:
                if event.topic == topic:
                    yield event
        
        async def create_topic(self, topic: str, **kwargs) -> None:
            print(f"[LOG] Creating topic: {topic}")
        
        async def delete_topic(self, topic: str) -> None:
            print(f"[LOG] Deleting topic: {topic}")
        
        async def list_topics(self) -> list:
            topics = list(set(event.topic for event in self.events))
            print(f"[LOG] Available topics: {topics}")
            return topics
    
    # Register the custom adapter
    EventFactory.register_adapter("logging", LoggingEventAdapter)
    
    # Use the custom adapter
    user_events = UserEvent(event_type="logging")
    
    user = User(id="1", name="Test User", email="test@example.com")
    await user_events.push("custom_event", user)
    await user_events.list_topics()
    await user_events.disconnect()
    
    print()


async def example_event_patterns():
    """Example showing common event patterns"""
    print("=== Event Patterns Example ===")
    
    # Event Sourcing Pattern
    user_events = UserEvent(event_type="memory")
    
    # Simulate user lifecycle events
    user = User(id="123", name="Pattern User", email="pattern@example.com")
    
    # User registration
    await user_events.push("registered", user)
    print(f"Event: User {user.name} registered")
    
    # User profile update
    user.email = "new_email@example.com"
    await user_events.push("profile_updated", user)
    print(f"Event: User {user.name} profile updated")
    
    # User deactivation
    await user_events.push("deactivated", user)
    print(f"Event: User {user.name} deactivated")
    
    # CQRS Pattern - Command and Query separation
    # Commands would use events for state changes
    # Queries would read from projections built from events
    
    print("\nEvent History:")
    topics = await user_events.list_topics()
    for topic in topics:
        print(f"Topic: user.{topic}")
        async for event_data in user_events.pull(topic):
            print(f"  - {event_data.model_dump()}")
            break  # Just show first event per topic
    
    await user_events.disconnect()
    print()


async def main():
    """Run all examples"""
    print("Event System Examples")
    print("=" * 50)
    
    # Run examples
    await example_kafka_events()
    await example_rabbitmq_events()
    await example_kinesis_events()
    await example_pubsub_events()
    await example_memory_events()
    await example_factory_usage()
    await example_custom_adapter()
    await example_event_patterns()
    
    print("All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
