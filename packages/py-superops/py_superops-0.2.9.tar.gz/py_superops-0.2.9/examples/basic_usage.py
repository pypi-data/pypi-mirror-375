#!/usr/bin/env python3
"""Basic usage example for the py-superops client library."""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to Python path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from py_superops import SuperOpsClient, SuperOpsConfig, create_client


async def test_with_environment_config():
    """Test client creation with environment variables."""
    print("=== Testing with Environment Configuration ===")

    try:
        # This will use environment variables (SUPEROPS_API_KEY, etc.)
        config = SuperOpsConfig.from_env()
        print(f"Configuration loaded: {config.base_url}")
        print(f"API Key masked: {config.api_key[:8]}***")

        async with SuperOpsClient(config) as client:
            # Test connection
            connection_info = await client.test_connection()
            print(f"Connection test: {connection_info}")

    except Exception as e:
        print(f"Error with environment config: {e}")
        print("Make sure to set SUPEROPS_API_KEY environment variable")


async def test_with_direct_config():
    """Test client creation with direct configuration."""
    print("\n=== Testing with Direct Configuration ===")

    # Example with placeholder values - replace with real credentials
    api_key = os.getenv("SUPEROPS_API_KEY", "your-api-key-here")

    if api_key == "your-api-key-here":
        print("Skipping direct config test - no API key provided")
        return

    try:
        config = SuperOpsConfig(
            api_key=api_key,
            base_url="https://api.superops.com/v1",
            timeout=30.0,
            debug=True,
        )

        async with SuperOpsClient(config) as client:
            # Test connection
            connection_info = await client.test_connection()
            print(f"Connection successful: {connection_info['connected']}")
            print(f"Response time: {connection_info['response_time_seconds']:.3f}s")
            print(f"Datacenter: {connection_info['datacenter']}")

    except Exception as e:
        print(f"Error with direct config: {e}")


async def test_convenience_function():
    """Test the convenience create_client function."""
    print("\n=== Testing Convenience Function ===")

    api_key = os.getenv("SUPEROPS_API_KEY")
    if not api_key:
        print("Skipping convenience function test - no API key provided")
        return

    try:
        # Create client using convenience function
        client = create_client(
            api_key=api_key,
            timeout=15.0,
            debug=True,
        )

        async with client:
            connection_info = await client.test_connection()
            print(f"Convenience client connected: {connection_info['connected']}")

    except Exception as e:
        print(f"Error with convenience function: {e}")


async def test_schema_introspection():
    """Test GraphQL schema introspection."""
    print("\n=== Testing Schema Introspection ===")

    api_key = os.getenv("SUPEROPS_API_KEY")
    if not api_key:
        print("Skipping schema test - no API key provided")
        return

    try:
        client = create_client(api_key=api_key)

        async with client:
            schema = await client.get_schema()

            query_type = schema.get("queryType", {}).get("name", "Unknown")
            mutation_type = schema.get("mutationType", {}).get("name", "Unknown")

            print(f"Schema loaded successfully")
            print(f"Query type: {query_type}")
            print(f"Mutation type: {mutation_type}")

            # Count types
            types = schema.get("types", [])
            print(f"Total types in schema: {len(types)}")

    except Exception as e:
        print(f"Error with schema introspection: {e}")


async def test_configuration_validation():
    """Test configuration validation."""
    print("\n=== Testing Configuration Validation ===")

    # Test valid configuration
    try:
        config = SuperOpsConfig(
            api_key="test-api-key-123456789",
            base_url="https://api.superops.com/v1",
        )
        config.validate_config()
        print("✓ Valid configuration passed validation")
    except Exception as e:
        print(f"✗ Valid configuration failed: {e}")

    # Test invalid configurations
    invalid_configs = [
        {"api_key": "", "base_url": "https://api.superops.com/v1"},
        {"api_key": "test-key", "base_url": ""},
        {"api_key": "test-key", "base_url": "invalid-url"},
        {
            "api_key": "test-key",
            "base_url": "https://api.superops.com/v1",
            "burst_limit": 100,
            "rate_limit_per_minute": 50,
        },
    ]

    for i, config_data in enumerate(invalid_configs, 1):
        try:
            config = SuperOpsConfig(**config_data)
            config.validate_config()
            print(f"✗ Invalid configuration {i} should have failed")
        except Exception as e:
            print(f"✓ Invalid configuration {i} correctly failed: {type(e).__name__}")


def print_package_info():
    """Print package information."""
    print("=== Package Information ===")

    try:
        from py_superops import get_package_info, get_version

        print(f"Package version: {get_version()}")

        info = get_package_info()
        print(f"Package name: {info['name']}")
        print(f"Description: {info['description']}")
        print(f"Author: {info['author']}")
        print(f"Python requires: {info['python_requires']}")

    except Exception as e:
        print(f"Error getting package info: {e}")


async def main():
    """Run all example tests."""
    print("SuperOps Python Client - Basic Usage Examples")
    print("=" * 50)

    print_package_info()

    # Test configuration validation first
    await test_configuration_validation()

    # Test with environment variables
    await test_with_environment_config()

    # Test with direct configuration
    await test_with_direct_config()

    # Test convenience function
    await test_convenience_function()

    # Test schema introspection
    await test_schema_introspection()

    print("\n=== Example Complete ===")
    print("To run tests with a real API key, set the SUPEROPS_API_KEY environment variable:")
    print("export SUPEROPS_API_KEY='your-api-key-here'")


if __name__ == "__main__":
    asyncio.run(main())
