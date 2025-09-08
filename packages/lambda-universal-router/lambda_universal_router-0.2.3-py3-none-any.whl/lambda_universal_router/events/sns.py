from __future__ import annotations
from typing import Any, Dict, List
from dataclasses import dataclass
from ..base import BaseEvent

@dataclass
class SNSMessage:
    """Represents a single SNS message."""
    message_id: str
    topic_arn: str
    message: str
    subject: str
    timestamp: str
    message_attributes: Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SNSMessage:
        sns = data.get('Sns', {})
        return cls(
            message_id=sns.get('MessageId', ''),
            topic_arn=sns.get('TopicArn', ''),
            message=sns.get('Message', ''),
            subject=sns.get('Subject', ''),
            timestamp=sns.get('Timestamp', ''),
            message_attributes=sns.get('MessageAttributes', {})
        )

class SNSEvent(BaseEvent):
    """Represents an SNS event."""
    
    def _parse_event(self, event_dict: Dict[str, Any]) -> None:
        self.records = [
            SNSMessage.from_dict(record)
            for record in event_dict.get('Records', [])
        ]
