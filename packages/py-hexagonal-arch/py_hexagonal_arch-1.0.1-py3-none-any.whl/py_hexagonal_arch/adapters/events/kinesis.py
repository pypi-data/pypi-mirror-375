"""
AWS Kinesis Event Adapter
"""

import json
from typing import Any, Optional, List, Callable, AsyncGenerator

from .base import EventAdapter, EventMessage


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
