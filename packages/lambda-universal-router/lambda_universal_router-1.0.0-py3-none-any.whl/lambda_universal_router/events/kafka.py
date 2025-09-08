from __future__ import annotations
from typing import Any, Dict, List
from dataclasses import dataclass
from ..base import BaseEvent

@dataclass
class KafkaRecord:
    """Represents a single Kafka record."""
    topic: str
    partition: int
    offset: int
    timestamp: int
    timestamp_type: str
    key: bytes
    value: bytes
    headers: List[Dict[str, str]]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> KafkaRecord:
        return cls(
            topic=data.get('topic', ''),
            partition=data.get('partition', 0),
            offset=data.get('offset', 0),
            timestamp=data.get('timestamp', 0),
            timestamp_type=data.get('timestampType', ''),
            key=data.get('key', b''),  # Base64 decoded
            value=data.get('value', b''),  # Base64 decoded
            headers=data.get('headers', [])
        )

class KafkaEvent(BaseEvent):
    """Represents an Amazon MSK (Kafka) event."""
    
    def _parse_event(self, event_dict: Dict[str, Any]) -> None:
        self.event_source = event_dict.get('eventSource', '')
        self.event_source_arn = event_dict.get('eventSourceArn', '')
        self.bootstrap_servers = event_dict.get('bootstrapServers', '')
        records = event_dict.get('records', [])
        if isinstance(records, dict):
            # Handle old format where records was a dict
            records = list(records.values())
        self.records = [KafkaRecord.from_dict(record) for record in records]
