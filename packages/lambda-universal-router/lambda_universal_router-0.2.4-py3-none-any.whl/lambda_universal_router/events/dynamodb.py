from __future__ import annotations
from typing import Any, Dict, List
from dataclasses import dataclass
from ..base import BaseEvent

@dataclass
class DynamoDBStreamRecord:
    """Represents a single DynamoDB Stream record."""
    event_id: str
    event_name: str  # INSERT | MODIFY | REMOVE
    event_version: str
    event_source: str
    aws_region: str
    dynamodb: Dict[str, Any]  # Contains keys, old/new images, etc.
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DynamoDBStreamRecord:
        return cls(
            event_id=data.get('eventID', ''),
            event_name=data.get('eventName', ''),
            event_version=data.get('eventVersion', ''),
            event_source=data.get('eventSource', ''),
            aws_region=data.get('awsRegion', ''),
            dynamodb=data.get('dynamodb', {})
        )

class DynamoDBStreamEvent(BaseEvent):
    """Represents a DynamoDB Stream event."""
    
    def _parse_event(self, event_dict: Dict[str, Any]) -> None:
        self.records = [
            DynamoDBStreamRecord.from_dict(record)
            for record in event_dict.get('Records', [])
        ]
