# Lambda Universal Router

[![PyPI version](https://badge.fury.io/py/lambda-universal-router.svg)](https://badge.fury.io/py/lambda-universal-router)
[![Python Support](https://img.shields.io/pypi/pyversions/lambda-universal-router.svg)](https://pypi.org/project/lambda-universal-router/)
[![License](https://img.shields.io/github/license/raumildhandhukia/lambda-universal-router.svg)](https://github.com/raumildhandhukia/lambda-universal-router/blob/main/LICENSE)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://raumildhandhukia.github.io/lambda-universal-router/)

A flexible and type-safe router for AWS Lambda functions that supports multiple event sources. This library makes it easy to handle different types of AWS Lambda events in a clean and organized way.

## Documentation

📚 **[Full Documentation](https://raumildhandhukia.github.io/lambda-universal-router/)**

- [API Reference](https://raumildhandhukia.github.io/lambda-universal-router/api)
- [Examples](https://raumildhandhukia.github.io/lambda-universal-router/examples)
- [Event Types](https://raumildhandhukia.github.io/lambda-universal-router/#event-sources)
- [Contributing Guide](https://raumildhandhukia.github.io/lambda-universal-router/contributing)
- [Changelog](https://raumildhandhukia.github.io/lambda-universal-router/changelog)

## Features

- 🎯 Type-safe event handling with proper Python type hints
- 🔄 Support for multiple AWS event sources
- 🎨 Clean decorator-based routing
- 📦 Easy to extend with new event sources
- 🔒 Structured event objects with proper typing
- 🔍 Custom event handler support for unknown event types

## Installation

```bash
pip install lambda-universal-router
```

## Quick Start

```python
from lambda_universal_router import Router
from lambda_universal_router.events import APIGatewayEvent, SQSEvent, CustomEvent

router = Router()

@router.apigateway("/hello", method="GET")
def hello(event: APIGatewayEvent, context):
    name = event.query_string_parameters.get('name', 'World')
    return {
        "statusCode": 200,
        "body": f"Hello, {name}!"
    }

@router.sqs()
def process_queue(event: SQSEvent, context):
    for msg in event.records:
        print(f"Processing message {msg.message_id}: {msg.body}")

@router.custom()
def handle_unknown(event: CustomEvent, context):
    print(f"Handling unknown event type: {event.event_data}")

def lambda_handler(event, context):
    return router.dispatch(event, context)
```

## Supported Event Sources

- [API Gateway](https://raumildhandhukia.github.io/lambda-universal-router/events/api-gateway) (REST/HTTP APIs)
- [SQS](https://raumildhandhukia.github.io/lambda-universal-router/events/sqs) (Simple Queue Service)
- [S3](https://raumildhandhukia.github.io/lambda-universal-router/events/s3) (Object Storage)
- [DynamoDB Streams](https://raumildhandhukia.github.io/lambda-universal-router/events/dynamodb)
- [Kinesis Streams](https://raumildhandhukia.github.io/lambda-universal-router/events/kinesis)
- [SNS](https://raumildhandhukia.github.io/lambda-universal-router/events/sns) (Simple Notification Service)
- [EventBridge](https://raumildhandhukia.github.io/lambda-universal-router/events/eventbridge) (CloudWatch Events)
- [Custom Events](https://raumildhandhukia.github.io/lambda-universal-router/events/custom)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

See our [Contributing Guide](https://raumildhandhukia.github.io/lambda-universal-router/contributing) for more details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.