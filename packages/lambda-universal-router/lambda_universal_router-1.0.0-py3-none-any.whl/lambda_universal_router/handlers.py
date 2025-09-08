from typing import Any, Dict
from .base import EventHandler, BaseEvent
from .events import (
    APIGatewayEvent, SQSEvent, S3Event,
    DynamoDBStreamEvent, KinesisStreamEvent,
    SNSEvent, EventBridgeEvent, CustomEvent,
    KafkaEvent
)

class APIGatewayHandler(EventHandler):
    """Handler for API Gateway events."""
    
    def can_handle(self, event: Dict[str, Any]) -> bool:
        return (
            'httpMethod' in event and
            'path' in event and
            'requestContext' in event
        )
    
    def parse_event(self, event: Dict[str, Any]) -> APIGatewayEvent:
        return APIGatewayEvent(event)

class SQSHandler(EventHandler):
    """Handler for SQS events."""
    
    def can_handle(self, event: Dict[str, Any]) -> bool:
        return (
            'Records' in event and
            len(event['Records']) > 0 and
            'eventSource' in event['Records'][0] and
            event['Records'][0]['eventSource'] == 'aws:sqs'
        )
    
    def parse_event(self, event: Dict[str, Any]) -> SQSEvent:
        return SQSEvent(event)

class S3Handler(EventHandler):
    """Handler for S3 events."""
    
    def can_handle(self, event: Dict[str, Any]) -> bool:
        return (
            'Records' in event and
            len(event['Records']) > 0 and
            'eventSource' in event['Records'][0] and
            event['Records'][0]['eventSource'] == 'aws:s3'
        )
    
    def parse_event(self, event: Dict[str, Any]) -> S3Event:
        return S3Event(event)

class DynamoDBStreamHandler(EventHandler):
    """Handler for DynamoDB Stream events."""
    
    def can_handle(self, event: Dict[str, Any]) -> bool:
        return (
            'Records' in event and
            len(event['Records']) > 0 and
            'eventSource' in event['Records'][0] and
            event['Records'][0]['eventSource'] == 'aws:dynamodb'
        )
    
    def parse_event(self, event: Dict[str, Any]) -> DynamoDBStreamEvent:
        return DynamoDBStreamEvent(event)

class KinesisStreamHandler(EventHandler):
    """Handler for Kinesis Stream events."""
    
    def can_handle(self, event: Dict[str, Any]) -> bool:
        return (
            'Records' in event and
            len(event['Records']) > 0 and
            'eventSource' in event['Records'][0] and
            event['Records'][0]['eventSource'] == 'aws:kinesis'
        )
    
    def parse_event(self, event: Dict[str, Any]) -> KinesisStreamEvent:
        return KinesisStreamEvent(event)

class SNSHandler(EventHandler):
    """Handler for SNS events."""
    
    def can_handle(self, event: Dict[str, Any]) -> bool:
        return (
            'Records' in event and
            len(event['Records']) > 0 and
            'EventSource' in event['Records'][0] and
            event['Records'][0]['EventSource'] == 'aws:sns'
        )
    
    def parse_event(self, event: Dict[str, Any]) -> SNSEvent:
        return SNSEvent(event)

class EventBridgeHandler(EventHandler):
    """Handler for EventBridge/CloudWatch Events."""
    
    def can_handle(self, event: Dict[str, Any]) -> bool:
        return (
            'source' in event and
            'detail-type' in event and
            'detail' in event
        )
    
    def parse_event(self, event: Dict[str, Any]) -> EventBridgeEvent:
        return EventBridgeEvent(event)

class KafkaHandler(EventHandler):
    """Handler for Amazon MSK (Kafka) events."""
    
    def can_handle(self, event: Dict[str, Any]) -> bool:
        return (
            'eventSource' in event and
            event['eventSource'] in ['aws:kafka', 'aws:self-managed-kafka'] and
            'records' in event
        )
    
    def parse_event(self, event: Dict[str, Any]) -> KafkaEvent:
        return KafkaEvent(event)

class CustomHandler(EventHandler):
    """Handler for custom or unknown event types."""
    
    def can_handle(self, event: Dict[str, Any]) -> bool:
        # Custom handler accepts any event
        return True
    
    def parse_event(self, event: Dict[str, Any]) -> CustomEvent:
        return CustomEvent(event)