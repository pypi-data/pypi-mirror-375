# SQS Worker

Manage workers triggered by AWS SQS messages

## Description

SQS Worker is a Python library that provides a simple and efficient way to manage workers that are triggered by AWS SQS (Simple Queue Service) messages. It offers a structured approach to processing SQS messages with built-in error handling and message management capabilities.

## Features

- Easy-to-use worker framework for SQS message processing
- Built-in error handling and exception management  
- Type-safe message models using Pydantic
- Integration with AWS SQS via boto3
- Support for observability tools

## Installation

```bash
pip install sqs-worker
```

Or using uv:

```bash
uv add sqs-worker
```

## Quick Start

```python
from sqs_worker import worker, models

# Your worker implementation here
# See examples/ directory for detailed usage examples
```

## Requirements

- Python 3.12 or higher
- AWS credentials configured (via AWS CLI, environment variables, or IAM roles)

## License

This project is licensed under the GNU General Public License v3.0 or later. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Repository

https://github.com/badihio/sqs-worker
