from __future__ import annotations
from typing import Any, Dict, List
from dataclasses import dataclass
from ..base import BaseEvent

@dataclass
class SQSMessage:
    """Represents a single SQS message."""
    message_id: str
    body: str
    attributes: Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SQSMessage:
        return cls(
            message_id=data.get('messageId', ''),
            body=data.get('body', ''),
            attributes=data.get('messageAttributes', {})
        )

class SQSEvent(BaseEvent):
    """Represents an SQS event."""
    
    def _parse_event(self, event_dict: Dict[str, Any]) -> None:
        self.records = [
            SQSMessage.from_dict(record)
            for record in event_dict.get('Records', [])
        ]
