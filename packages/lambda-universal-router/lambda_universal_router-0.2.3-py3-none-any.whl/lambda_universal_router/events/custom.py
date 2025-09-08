from __future__ import annotations
from typing import Any, Dict
from ..base import BaseEvent

class CustomEvent(BaseEvent):
    """Represents a custom or unknown event type."""
    
    def _parse_event(self, event_dict: Dict[str, Any]) -> None:
        # Store the entire event dictionary as-is
        self.event_data = event_dict
