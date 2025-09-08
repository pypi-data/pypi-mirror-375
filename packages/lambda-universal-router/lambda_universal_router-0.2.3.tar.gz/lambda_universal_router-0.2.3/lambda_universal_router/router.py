from typing import Any, Dict, List, Optional, Callable
from .base import EventHandler, HandlerRegistration, BaseEvent
from .handlers import (
    APIGatewayHandler, SQSHandler, S3Handler,
    DynamoDBStreamHandler, KinesisStreamHandler,
    SNSHandler, EventBridgeHandler, KafkaHandler,
    CustomHandler
)

class Router:
    """Main router class that handles Lambda event routing."""
    
    def __init__(self):
        self._handlers: List[HandlerRegistration] = []
        self._custom_handler: Optional[HandlerRegistration] = None
        self._event_handlers = {
            'apigateway': APIGatewayHandler(),
            'sqs': SQSHandler(),
            's3': S3Handler(),
            'dynamodb': DynamoDBStreamHandler(),
            'kinesis': KinesisStreamHandler(),
            'sns': SNSHandler(),
            'eventbridge': EventBridgeHandler(),
            'kafka': KafkaHandler(),
            'custom': CustomHandler()
        }
    
    def apigateway(self, path: str, method: str = "GET") -> Callable:
        """Decorator for API Gateway event handlers."""
        def decorator(func: Callable) -> Callable:
            self._handlers.append(
                HandlerRegistration(
                    func=func,
                    handler=self._event_handlers['apigateway'],
                    path=path,
                    method=method.upper()
                )
            )
            return func
        return decorator
    
    def sqs(self) -> Callable:
        """Decorator for SQS event handlers."""
        def decorator(func: Callable) -> Callable:
            self._handlers.append(
                HandlerRegistration(
                    func=func,
                    handler=self._event_handlers['sqs']
                )
            )
            return func
        return decorator
    
    def s3(self) -> Callable:
        """Decorator for S3 event handlers."""
        def decorator(func: Callable) -> Callable:
            self._handlers.append(
                HandlerRegistration(
                    func=func,
                    handler=self._event_handlers['s3']
                )
            )
            return func
        return decorator
    
    def dynamodb(self) -> Callable:
        """Decorator for DynamoDB Stream event handlers."""
        def decorator(func: Callable) -> Callable:
            self._handlers.append(
                HandlerRegistration(
                    func=func,
                    handler=self._event_handlers['dynamodb']
                )
            )
            return func
        return decorator
    
    def kinesis(self) -> Callable:
        """Decorator for Kinesis Stream event handlers."""
        def decorator(func: Callable) -> Callable:
            self._handlers.append(
                HandlerRegistration(
                    func=func,
                    handler=self._event_handlers['kinesis']
                )
            )
            return func
        return decorator
    
    def sns(self) -> Callable:
        """Decorator for SNS event handlers."""
        def decorator(func: Callable) -> Callable:
            self._handlers.append(
                HandlerRegistration(
                    func=func,
                    handler=self._event_handlers['sns']
                )
            )
            return func
        return decorator
    
    def eventbridge(self) -> Callable:
        """Decorator for EventBridge/CloudWatch Events handlers."""
        def decorator(func: Callable) -> Callable:
            self._handlers.append(
                HandlerRegistration(
                    func=func,
                    handler=self._event_handlers['eventbridge']
                )
            )
            return func
        return decorator

    def kafka(self) -> Callable:
        """Decorator for Amazon MSK (Kafka) event handlers."""
        def decorator(func: Callable) -> Callable:
            self._handlers.append(
                HandlerRegistration(
                    func=func,
                    handler=self._event_handlers['kafka']
                )
            )
            return func
        return decorator

    def custom(self) -> Callable:
        """
        Decorator for custom event handlers.
        This handler will be used as a fallback when no other handler matches.
        Only one custom handler can be registered.
        """
        def decorator(func: Callable) -> Callable:
            if self._custom_handler is not None:
                raise ValueError("Only one custom handler can be registered")
            
            self._custom_handler = HandlerRegistration(
                func=func,
                handler=self._event_handlers['custom']
            )
            return func
        return decorator
    
    def dispatch(self, event: Dict[str, Any], context: Any) -> Any:
        """Dispatch the event to the appropriate handler."""
        # Try all registered handlers first
        for registration in self._handlers:
            if registration.handler.can_handle(event):
                parsed_event = registration.handler.parse_event(event)
                return registration.func(parsed_event, context)
        
        # If no handler matches and we have a custom handler, use it
        if self._custom_handler is not None:
            parsed_event = self._custom_handler.handler.parse_event(event)
            return self._custom_handler.func(parsed_event, context)
        
        raise ValueError("No handler found for the given event type")