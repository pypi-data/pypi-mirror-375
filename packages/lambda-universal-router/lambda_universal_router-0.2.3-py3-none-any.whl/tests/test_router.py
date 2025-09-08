from __future__ import annotations
import json
import pytest
from lambda_universal_router import Router
from lambda_universal_router.events import (
    APIGatewayEvent, SQSEvent, S3Event,
    DynamoDBStreamEvent, KinesisStreamEvent,
    SNSEvent, EventBridgeEvent, CustomEvent
)

@pytest.fixture
def router():
    return Router()

def test_api_gateway_routing(router):
    @router.apigateway("/test", method="GET")
    def handler(event: APIGatewayEvent, context):
        assert isinstance(event, APIGatewayEvent)
        assert event.http_method == "GET"
        assert event.path == "/test"
        return {"statusCode": 200, "body": "test"}

    event = {
        "httpMethod": "GET",
        "path": "/test",
        "requestContext": {
            "httpMethod": "GET",
            "path": "/test",
            "stage": "prod",
            "requestId": "test-id"
        },
        "headers": {"Content-Type": "application/json"},
        "queryStringParameters": {"param": "value"},
        "pathParameters": {"id": "123"}
    }

    result = router.dispatch(event, {})
    assert result["statusCode"] == 200
    assert result["body"] == "test"

def test_sqs_routing(router):
    @router.sqs()
    def handler(event: SQSEvent, context):
        assert isinstance(event, SQSEvent)
        assert len(event.records) == 1
        assert event.records[0].message_id == "test"
        assert event.records[0].body == "test message"
        return "processed"

    event = {
        "Records": [{
            "messageId": "test",
            "body": "test message",
            "messageAttributes": {"attr": "value"},
            "eventSource": "aws:sqs"
        }]
    }

    result = router.dispatch(event, {})
    assert result == "processed"

def test_s3_routing(router):
    @router.s3()
    def handler(event: S3Event, context):
        assert isinstance(event, S3Event)
        assert len(event.records) == 1
        assert event.records[0].s3_object.key == "test.txt"
        return "processed"

    event = {
        "Records": [{
            "eventName": "ObjectCreated:Put",
            "eventTime": "2024-03-17T12:00:00.000Z",
            "s3": {
                "bucket": {
                    "name": "test-bucket",
                    "arn": "arn:aws:s3:::test-bucket"
                },
                "object": {
                    "key": "test.txt",
                    "size": 123,
                    "eTag": "abc123"
                }
            },
            "eventSource": "aws:s3"
        }]
    }

    result = router.dispatch(event, {})
    assert result == "processed"

def test_dynamodb_stream_routing(router):
    @router.dynamodb()
    def handler(event: DynamoDBStreamEvent, context):
        assert isinstance(event, DynamoDBStreamEvent)
        assert len(event.records) == 1
        assert event.records[0].event_name == "INSERT"
        return "processed"

    event = {
        "Records": [{
            "eventID": "1",
            "eventName": "INSERT",
            "eventVersion": "1.0",
            "eventSource": "aws:dynamodb",
            "awsRegion": "us-east-1",
            "dynamodb": {
                "Keys": {"id": {"S": "123"}},
                "NewImage": {"id": {"S": "123"}, "name": {"S": "test"}},
                "SequenceNumber": "123",
                "SizeBytes": 123,
                "StreamViewType": "NEW_AND_OLD_IMAGES"
            }
        }]
    }

    result = router.dispatch(event, {})
    assert result == "processed"

def test_kinesis_stream_routing(router):
    @router.kinesis()
    def handler(event: KinesisStreamEvent, context):
        assert isinstance(event, KinesisStreamEvent)
        assert len(event.records) == 1
        assert event.records[0].partition_key == "test"
        return "processed"

    event = {
        "Records": [{
            "kinesis": {
                "partitionKey": "test",
                "kinesisSchemaVersion": "1.0",
                "data": "SGVsbG8gV29ybGQ=",  # Base64 encoded "Hello World"
                "sequenceNumber": "123",
                "approximateArrivalTimestamp": 1234567890.123
            },
            "eventSource": "aws:kinesis"
        }]
    }

    result = router.dispatch(event, {})
    assert result == "processed"

def test_sns_routing(router):
    @router.sns()
    def handler(event: SNSEvent, context):
        assert isinstance(event, SNSEvent)
        assert len(event.records) == 1
        assert event.records[0].message == "test message"
        return "processed"

    event = {
        "Records": [{
            "EventSource": "aws:sns",
            "Sns": {
                "MessageId": "test",
                "Message": "test message",
                "Subject": "Test",
                "TopicArn": "arn:aws:sns:us-east-1:123456789012:test",
                "Timestamp": "2024-03-17T12:00:00.000Z",
                "MessageAttributes": {}
            }
        }]
    }

    result = router.dispatch(event, {})
    assert result == "processed"

def test_eventbridge_routing(router):
    @router.eventbridge()
    def handler(event: EventBridgeEvent, context):
        assert isinstance(event, EventBridgeEvent)
        assert event.source == "aws.events"
        assert event.detail_type == "Scheduled Event"
        return "processed"

    event = {
        "version": "0",
        "id": "test",
        "detail-type": "Scheduled Event",
        "source": "aws.events",
        "account": "123456789012",
        "time": "2024-03-17T12:00:00Z",
        "region": "us-east-1",
        "resources": ["arn:aws:events:us-east-1:123456789012:rule/test"],
        "detail": {"test": "value"}
    }

    result = router.dispatch(event, {})
    assert result == "processed"

def test_custom_handler(router):
    @router.custom()
    def handler(event: CustomEvent, context):
        assert isinstance(event, CustomEvent)
        assert event.event_data["custom_field"] == "custom_value"
        return "custom processed"

    event = {
        "custom_field": "custom_value",
        "another_field": 123
    }

    result = router.dispatch(event, {})
    assert result == "custom processed"

def test_custom_handler_fallback(router):
    @router.custom()
    def handler(event: CustomEvent, context):
        return "fallback"

    # Unknown event type will be handled by custom handler
    event = {
        "unknown_event_type": True,
        "data": "test"
    }

    result = router.dispatch(event, {})
    assert result == "fallback"

def test_multiple_custom_handlers_error(router):
    @router.custom()
    def handler1(event: CustomEvent, context):
        return "handler1"

    # Attempting to register a second custom handler should raise an error
    with pytest.raises(ValueError, match="Only one custom handler can be registered"):
        @router.custom()
        def handler2(event: CustomEvent, context):
            return "handler2"

def test_no_handler_found(router):
    # No handlers registered, including custom handler
    event = {"test": "value"}
    
    with pytest.raises(ValueError, match="No handler found for the given event type"):
        router.dispatch(event, {})