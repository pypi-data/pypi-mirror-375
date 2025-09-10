"""
Google Cloud Pub/Sub Event Adapter
"""

import json
from typing import Any, Optional, List, Callable, AsyncGenerator

from .base import EventAdapter, EventMessage


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
