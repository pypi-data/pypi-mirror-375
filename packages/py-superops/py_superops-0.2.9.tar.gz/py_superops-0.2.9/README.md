# py-superops

Python client library for the SuperOps GraphQL API.

## Overview

This package provides a comprehensive Python SDK for interacting with the SuperOps GraphQL API, featuring async/await support, comprehensive error handling, rate limiting, and type safety.

## Features

- **Async/await support** for high-performance applications
- **Comprehensive error handling** with custom exception hierarchy
- **Built-in rate limiting** and retry logic
- **Type safety** with full type hint support
- **Configuration management** with environment variable support
- **Authentication handling** with token validation
- **Connection pooling** and resource management

## Installation

```bash
pip install py-superops
```

## Quick Start

### Basic Usage

```python
import asyncio
from py_superops import SuperOpsClient, SuperOpsConfig

async def main():
    # Create configuration
    config = SuperOpsConfig(
        api_key="your-api-key",
        base_url="https://api.superops.com/v1"
    )

    # Create and use the client
    async with SuperOpsClient(config) as client:
        # Test connection
        connection_info = await client.test_connection()
        print(f"Connected: {connection_info['connected']}")

        # Execute a query
        query = '''
        query GetClients {
            clients {
                id
                name
                email
            }
        }
        '''

        response = await client.execute_query(query)
        clients = response['data']['clients']

        for client in clients:
            print(f"Client: {client['name']} ({client['email']})")

if __name__ == "__main__":
    asyncio.run(main())
```

### Configuration from Environment

```python
import os
from py_superops import create_client

# Set environment variable
os.environ["SUPEROPS_API_KEY"] = "your-api-key"

# Create client from environment
client = create_client()
```

### Advanced Configuration

```python
from py_superops import SuperOpsConfig, SuperOpsClient

config = SuperOpsConfig(
    api_key="your-api-key",
    base_url="https://api.superops.com/v1",
    timeout=60.0,
    max_retries=5,
    rate_limit_per_minute=120,
    enable_caching=True,
    cache_ttl=600,
    debug=True
)

async with SuperOpsClient(config) as client:
    # Your code here
    pass
```

## Configuration

The client can be configured through multiple methods:

1. **Direct instantiation**
2. **Environment variables** (prefixed with `SUPEROPS_`)
3. **Configuration files** (JSON or YAML)

### Environment Variables

- `SUPEROPS_API_KEY` - Your SuperOps API key (required)
- `SUPEROPS_BASE_URL` - API base URL (default: https://api.superops.com/v1)
- `SUPEROPS_TIMEOUT` - Request timeout in seconds (default: 30.0)
- `SUPEROPS_MAX_RETRIES` - Maximum request retries (default: 3)
- `SUPEROPS_RATE_LIMIT_PER_MINUTE` - Rate limit (default: 60)
- `SUPEROPS_DEBUG` - Enable debug mode (default: false)

### Configuration File

```yaml
# superops.yaml
api_key: "your-api-key"
base_url: "https://api.superops.com/v1"
timeout: 30.0
max_retries: 3
rate_limit_per_minute: 60
enable_caching: true
cache_ttl: 300
debug: false
```

```python
from py_superops import SuperOpsConfig

config = SuperOpsConfig.from_file("superops.yaml")
```

## Error Handling

The library provides a comprehensive exception hierarchy:

```python
from py_superops import (
    SuperOpsError,
    SuperOpsAPIError,
    SuperOpsAuthenticationError,
    SuperOpsRateLimitError,
    SuperOpsNetworkError,
    SuperOpsValidationError,
)

try:
    response = await client.execute_query(query)
except SuperOpsAuthenticationError:
    print("Authentication failed - check your API key")
except SuperOpsRateLimitError as e:
    print(f"Rate limit exceeded - retry after {e.retry_after} seconds")
except SuperOpsAPIError as e:
    print(f"API error: {e.message} (status: {e.status_code})")
except SuperOpsNetworkError:
    print("Network error - check your connection")
```

## GraphQL Operations

### Queries

```python
query = '''
query GetClients($limit: Int) {
    clients(limit: $limit) {
        id
        name
        email
        sites {
            id
            name
        }
    }
}
'''

variables = {"limit": 10}
response = await client.execute_query(query, variables=variables)
```

### Mutations

```python
mutation = '''
mutation CreateClient($input: ClientInput!) {
    createClient(input: $input) {
        id
        name
        email
    }
}
'''

variables = {
    "input": {
        "name": "New Client",
        "email": "client@example.com"
    }
}

response = await client.execute_mutation(mutation, variables=variables)
```

## Development

### Requirements

- Python 3.8+
- httpx
- pydantic
- pydantic-settings

### Optional Dependencies

- PyYAML (for YAML configuration files)

### Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=py_superops --cov-report=html
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

## API Documentation

### SuperOpsClient

Main client class for interacting with the SuperOps API.

#### Methods

- `execute_query(query, variables=None, operation_name=None)` - Execute a GraphQL query
- `execute_mutation(mutation, variables=None, operation_name=None)` - Execute a GraphQL mutation
- `test_connection()` - Test API connection and authentication
- `get_schema()` - Get GraphQL schema information
- `close()` - Close HTTP client connections

### SuperOpsConfig

Configuration class for the SuperOps client.

#### Class Methods

- `from_env()` - Load configuration from environment variables
- `from_file(path)` - Load configuration from file

#### Methods

- `validate_config()` - Validate current configuration
- `get_headers()` - Get HTTP headers for requests
- `is_us_datacenter()` - Check if using US datacenter
- `is_eu_datacenter()` - Check if using EU datacenter

### Convenience Functions

- `create_client(**kwargs)` - Create client with minimal configuration
- `get_version()` - Get package version
- `get_package_info()` - Get package metadata

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:

- GitHub Issues: https://github.com/superops/py-superops/issues
- Documentation: https://py-superops.readthedocs.io
- SuperOps Support: https://support.superops.com

## Changelog

See CHANGELOG.md for version history and changes.
