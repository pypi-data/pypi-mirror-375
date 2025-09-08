from __future__ import annotations
from typing import Any, Dict, List
from dataclasses import dataclass
from ..base import BaseEvent

@dataclass
class S3Object:
    """Represents an S3 object in the event."""
    key: str
    size: int
    etag: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> S3Object:
        return cls(
            key=data.get('key', ''),
            size=data.get('size', 0),
            etag=data.get('eTag', '')
        )

@dataclass
class S3Bucket:
    """Represents an S3 bucket in the event."""
    name: str
    arn: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> S3Bucket:
        return cls(
            name=data.get('name', ''),
            arn=data.get('arn', '')
        )

@dataclass
class S3Record:
    """Represents a single S3 record in the event."""
    event_name: str
    event_time: str
    bucket: S3Bucket
    s3_object: S3Object
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> S3Record:
        s3_data = data.get('s3', {})
        return cls(
            event_name=data.get('eventName', ''),
            event_time=data.get('eventTime', ''),
            bucket=S3Bucket.from_dict(s3_data.get('bucket', {})),
            s3_object=S3Object.from_dict(s3_data.get('object', {}))
        )

class S3Event(BaseEvent):
    """Represents an S3 event."""
    
    def _parse_event(self, event_dict: Dict[str, Any]) -> None:
        self.records = [
            S3Record.from_dict(record)
            for record in event_dict.get('Records', [])
        ]
