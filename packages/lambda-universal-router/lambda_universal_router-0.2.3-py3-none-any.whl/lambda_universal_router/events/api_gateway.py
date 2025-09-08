from __future__ import annotations
from typing import Any, Dict
from dataclasses import dataclass
from ..base import BaseEvent

@dataclass
class APIGatewayRequestContext:
    http_method: str
    path: str
    stage: str
    request_id: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> APIGatewayRequestContext:
        return cls(
            http_method=data.get('httpMethod', ''),
            path=data.get('path', ''),
            stage=data.get('stage', ''),
            request_id=data.get('requestId', '')
        )

class APIGatewayEvent(BaseEvent):
    """Represents an API Gateway event."""
    
    def _parse_event(self, event_dict: Dict[str, Any]) -> None:
        self.http_method = event_dict.get('httpMethod', '')
        self.path = event_dict.get('path', '')
        self.headers = event_dict.get('headers', {})
        self.query_string_parameters = event_dict.get('queryStringParameters', {})
        self.path_parameters = event_dict.get('pathParameters', {})
        self.body = event_dict.get('body', '')
        self.request_context = APIGatewayRequestContext.from_dict(
            event_dict.get('requestContext', {})
        )
