from __future__ import annotations
from typing import Any, Dict
from dataclasses import dataclass
from ..base import BaseEvent

@dataclass
class EventBridgeDetail:
    """Represents the detail field of an EventBridge event."""
    raw_detail: Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EventBridgeDetail:
        return cls(raw_detail=data)

class EventBridgeEvent(BaseEvent):
    """Represents an EventBridge/CloudWatch Events event."""
    
    def _parse_event(self, event_dict: Dict[str, Any]) -> None:
        self.version = event_dict.get('version', '')
        self.id = event_dict.get('id', '')
        self.detail_type = event_dict.get('detail-type', '')
        self.source = event_dict.get('source', '')
        self.account = event_dict.get('account', '')
        self.time = event_dict.get('time', '')
        self.region = event_dict.get('region', '')
        self.resources = event_dict.get('resources', [])
        self.detail = EventBridgeDetail.from_dict(event_dict.get('detail', {}))
