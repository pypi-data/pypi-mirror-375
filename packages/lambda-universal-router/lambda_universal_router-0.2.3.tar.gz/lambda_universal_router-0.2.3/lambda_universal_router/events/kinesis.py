from __future__ import annotations
from typing import Any, Dict, List
from dataclasses import dataclass
from ..base import BaseEvent

@dataclass
class KinesisRecord:
    """Represents a single Kinesis Stream record."""
    kinesis_schema_version: str
    partition_key: str
    sequence_number: str
    data: bytes  # Base64-decoded data
    approximate_arrival_timestamp: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> KinesisRecord:
        kinesis_data = data.get('kinesis', {})
        return cls(
            kinesis_schema_version=kinesis_data.get('kinesisSchemaVersion', ''),
            partition_key=kinesis_data.get('partitionKey', ''),
            sequence_number=kinesis_data.get('sequenceNumber', ''),
            data=kinesis_data.get('data', b''),  # Note: This will be base64 encoded
            approximate_arrival_timestamp=kinesis_data.get('approximateArrivalTimestamp', 0.0)
        )

class KinesisStreamEvent(BaseEvent):
    """Represents a Kinesis Stream event."""
    
    def _parse_event(self, event_dict: Dict[str, Any]) -> None:
        self.records = [
            KinesisRecord.from_dict(record)
            for record in event_dict.get('Records', [])
        ]
