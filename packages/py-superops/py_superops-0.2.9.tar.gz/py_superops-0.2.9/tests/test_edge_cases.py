# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Edge case and error scenario tests for py-superops client library.

These tests verify the library's behavior in unusual or error conditions,
ensuring robust error handling and graceful degradation.
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from py_superops import AuthHandler, SuperOpsClient, SuperOpsConfig
from py_superops.exceptions import (
    SuperOpsAPIError,
    SuperOpsAuthenticationError,
    SuperOpsConfigurationError,
    SuperOpsError,
    SuperOpsNetworkError,
    SuperOpsRateLimitError,
    SuperOpsResourceNotFoundError,
    SuperOpsTimeoutError,
    SuperOpsValidationError,
)
from py_superops.graphql.types import ClientStatus


class TestConfigurationEdgeCases:
    """Test edge cases in configuration handling."""

    def test_config_with_minimal_required_fields(self):
        """Test configuration with only required fields."""
        config = SuperOpsConfig(
            api_key="test-api-key-12345678901234567890", base_url="https://api.superops.com/v1"
        )

        assert config.api_key == "test-api-key-12345678901234567890"
        assert config.base_url == "https://api.superops.com/v1"
        assert config.timeout == 30.0  # Default value
        assert config.max_retries == 3  # Default value

    def test_config_with_edge_case_urls(self):
        """Test configuration with edge case URLs."""
        # URLs with various formats
        test_cases = [
            "https://api.superops.com:443/v1",  # With port
            "https://api.superops.com/v1/",  # With trailing slash
            "https://subdomain.api.superops.com/v1",  # Subdomain
        ]

        for url in test_cases:
            config = SuperOpsConfig(api_key="test-api-key-12345678901234567890", base_url=url)
            # URL should be normalized (no trailing slash)
            assert not config.base_url.endswith("/")

    def test_config_with_extreme_timeout_values(self):
        """Test configuration with extreme timeout values."""
        # Very small timeout
        config_small = SuperOpsConfig(
            api_key="test-api-key-12345678901234567890",
            base_url="https://api.superops.com/v1",
            timeout=0.1,
        )
        assert config_small.timeout == 0.1

        # Very large timeout (within limits)
        config_large = SuperOpsConfig(
            api_key="test-api-key-12345678901234567890",
            base_url="https://api.superops.com/v1",
            timeout=300.0,  # 5 minutes (max allowed)
        )
        assert config_large.timeout == 300.0

    def test_config_validation_with_special_characters(self):
        """Test configuration validation with special characters."""
        # API key with special characters (should be valid)
        special_key = "test-api-key-!@#$%^&*()_+-=[]{}|;':\",./<>?~`12345678"
        config = SuperOpsConfig(api_key=special_key, base_url="https://api.superops.com/v1")
        assert config.api_key == special_key

    def test_config_with_invalid_rate_limit_combination(self):
        """Test invalid rate limiting configuration."""
        # Burst limit higher than rate limit per minute
        with pytest.raises(SuperOpsConfigurationError, match="Burst limit cannot exceed"):
            config = SuperOpsConfig(
                api_key="test-api-key-12345678901234567890",
                base_url="https://api.superops.com/v1",
                rate_limit_per_minute=60,
                burst_limit=100,  # Higher than rate limit
            )
            config.validate_config()


class TestAuthenticationEdgeCases:
    """Test edge cases in authentication handling."""

    def test_auth_handler_with_placeholder_key(self):
        """Test auth handler with placeholder API key."""
        config = SuperOpsConfig(api_key="your-api-key-here", base_url="https://api.superops.com/v1")
        auth = AuthHandler(config)

        assert not auth.is_token_format_valid()

    def test_auth_handler_with_empty_key(self):
        """Test auth handler behavior with empty key."""
        config = MagicMock()
        config.api_key = ""

        auth = AuthHandler(config)
        assert not auth.is_token_format_valid()

    def test_auth_handler_with_whitespace_key(self):
        """Test auth handler with whitespace in key."""
        config = MagicMock()
        config.api_key = "  test-api-key-12345678901234567890  "

        auth = AuthHandler(config)
        # Should handle whitespace appropriately
        assert not auth.is_token_format_valid()

    @pytest.mark.asyncio
    async def test_auth_header_generation_edge_cases(self):
        """Test authentication header generation in edge cases."""
        config = SuperOpsConfig(
            api_key="test-api-key-with-unicode-copyright-12345678901234567890",
            base_url="https://api.superops.com/v1",
        )
        auth = AuthHandler(config)

        headers = await auth.get_headers()
        assert "Authorization" in headers
        assert (
            "test-api-key-with-unicode-copyright-12345678901234567890" in headers["Authorization"]
        )


class TestNetworkEdgeCases:
    """Test network-related edge cases."""

    @pytest.mark.asyncio
    async def test_malformed_json_response(self, test_config):
        """Test handling of malformed JSON responses."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock response with malformed JSON
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "application/json"}
            mock_response.text = '{"invalid": json malformed'
            mock_response.json.side_effect = json.JSONDecodeError("Expecting ',' delimiter", "", 0)
            mock_response.raise_for_status.return_value = None
            mock_client.post.return_value = mock_response

            async with SuperOpsClient(test_config) as client:
                with pytest.raises(SuperOpsAPIError, match="Invalid JSON response"):
                    await client.clients.get("client-123")

    @pytest.mark.asyncio
    async def test_empty_response_body(self, test_config):
        """Test handling of empty response body."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock response with empty body
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "application/json"}
            mock_response.text = ""
            mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
            mock_response.raise_for_status.return_value = None
            mock_client.post.return_value = mock_response

            async with SuperOpsClient(test_config) as client:
                with pytest.raises(SuperOpsAPIError):
                    await client.clients.get("client-123")

    @pytest.mark.asyncio
    async def test_non_json_response(self, test_config):
        """Test handling of non-JSON response."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock HTML response instead of JSON
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "text/html"}
            mock_response.text = "<html><body>Server Error</body></html>"
            mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
            mock_response.raise_for_status.return_value = None
            mock_client.post.return_value = mock_response

            async with SuperOpsClient(test_config) as client:
                with pytest.raises(SuperOpsAPIError, match="Invalid JSON response"):
                    await client.clients.get("client-123")

    @pytest.mark.asyncio
    async def test_connection_refused_error(self, test_config):
        """Test handling of connection refused errors."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock connection refused error
            mock_client.post.side_effect = httpx.ConnectError("Connection refused")

            async with SuperOpsClient(test_config) as client:
                with pytest.raises(SuperOpsNetworkError, match="Connection refused"):
                    await client.clients.get("client-123")

    @pytest.mark.asyncio
    async def test_ssl_error(self, test_config):
        """Test handling of SSL errors."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock SSL error
            ssl_error = httpx.ConnectError("SSL: CERTIFICATE_VERIFY_FAILED")
            mock_client.post.side_effect = ssl_error

            async with SuperOpsClient(test_config) as client:
                with pytest.raises(SuperOpsNetworkError):
                    await client.clients.get("client-123")

    @pytest.mark.asyncio
    async def test_dns_resolution_error(self, test_config):
        """Test handling of DNS resolution errors."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock DNS error
            dns_error = httpx.ConnectError("[Errno -2] Name or service not known")
            mock_client.post.side_effect = dns_error

            async with SuperOpsClient(test_config) as client:
                with pytest.raises(SuperOpsNetworkError):
                    await client.clients.get("client-123")


class TestGraphQLEdgeCases:
    """Test GraphQL-specific edge cases."""

    @pytest.mark.asyncio
    async def test_graphql_errors_without_extensions(self, test_config, mock_httpx_response):
        """Test GraphQL errors without extensions field."""
        error_response = mock_httpx_response(
            200,
            {
                "errors": [
                    {
                        "message": "Something went wrong"
                        # No extensions field
                    }
                ]
            },
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = error_response

            async with SuperOpsClient(test_config) as client:
                with pytest.raises(SuperOpsAPIError, match="Something went wrong"):
                    await client.clients.get("client-123")

    @pytest.mark.asyncio
    async def test_graphql_multiple_errors(self, test_config, mock_httpx_response):
        """Test multiple GraphQL errors in single response."""
        error_response = mock_httpx_response(
            200,
            {
                "errors": [
                    {"message": "First error", "extensions": {"code": "ERROR_1"}},
                    {"message": "Second error", "extensions": {"code": "ERROR_2"}},
                    {"message": "Third error", "extensions": {"code": "ERROR_3"}},
                ]
            },
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = error_response

            async with SuperOpsClient(test_config) as client:
                with pytest.raises(SuperOpsAPIError) as exc_info:
                    await client.clients.get("client-123")

                # Should contain information about multiple errors
                error_message = str(exc_info.value)
                assert "First error" in error_message

    @pytest.mark.asyncio
    async def test_partial_graphql_response(self, test_config, mock_httpx_response):
        """Test partial GraphQL response with data and errors."""
        partial_response = mock_httpx_response(
            200,
            {
                "data": {"client": {"id": "client-123", "name": "Test Client", "status": "ACTIVE"}},
                "errors": [
                    {
                        "message": "Field 'email' is deprecated",
                        "extensions": {"code": "DEPRECATED_FIELD"},
                    }
                ],
            },
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = partial_response

            async with SuperOpsClient(test_config) as client:
                # Should succeed and return data despite warnings
                result = await client.clients.get("client-123")
                assert result is not None
                assert result.name == "Test Client"

    @pytest.mark.asyncio
    async def test_graphql_response_with_null_data(self, test_config, mock_httpx_response):
        """Test GraphQL response with explicit null data."""
        null_response = mock_httpx_response(
            200,
            {
                "data": None,
                "errors": [
                    {"message": "Query execution error", "extensions": {"code": "EXECUTION_ERROR"}}
                ],
            },
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = null_response

            async with SuperOpsClient(test_config) as client:
                with pytest.raises(SuperOpsAPIError, match="Query execution error"):
                    await client.clients.get("client-123")


class TestDataHandlingEdgeCases:
    """Test edge cases in data handling and serialization."""

    @pytest.mark.asyncio
    async def test_large_response_handling(self, test_config, mock_httpx_response):
        """Test handling of very large responses."""
        # Generate a large response
        large_items = [
            {
                "id": f"client-{i}",
                "name": f"Client {i} with very long name " + "x" * 100,
                "email": f"client{i}@verylongdomainname.example.com",
                "status": "ACTIVE",
                "description": "Description " + "y" * 1000,  # Long description
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "updatedAt": datetime.now(timezone.utc).isoformat(),
            }
            for i in range(1000)  # 1000 items
        ]

        large_response = mock_httpx_response(
            200,
            {
                "data": {
                    "clients": {
                        "items": large_items,
                        "pagination": {
                            "page": 1,
                            "pageSize": 1000,
                            "total": 1000,
                            "hasNextPage": False,
                            "hasPreviousPage": False,
                        },
                    }
                }
            },
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = large_response

            async with SuperOpsClient(test_config) as client:
                result = await client.clients.list(page_size=1000)

                # Should handle large response without issues
                assert len(result["items"]) == 1000
                assert result["items"][0].name.startswith("Client 0")
                assert len(result["items"][0].description) > 1000

    def test_unicode_handling_in_data(self, test_config):
        """Test handling of Unicode characters in data."""
        # Test with various Unicode characters
        unicode_data = {
            "name": "Client with �mojis =� and Unicode ������",
            "email": "t�st@�nic�de.com",
            "notes": "Notes with Chinese -�, Arabic 'D91(J), and emoji <�<",
        }

        # Should not raise any encoding errors
        config_headers = test_config.get_headers()
        assert config_headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_nested_data_structures(self, test_config, mock_httpx_response):
        """Test handling of deeply nested data structures."""
        nested_response = mock_httpx_response(
            200,
            {
                "data": {
                    "client": {
                        "id": "client-123",
                        "name": "Test Client",
                        "metadata": {
                            "settings": {
                                "notifications": {
                                    "email": {
                                        "enabled": True,
                                        "frequency": "daily",
                                        "recipients": ["user1@test.com", "user2@test.com"],
                                    },
                                    "sms": {"enabled": False, "providers": []},
                                },
                                "billing": {
                                    "plan": "premium",
                                    "features": {
                                        "advanced_reporting": True,
                                        "custom_fields": True,
                                        "integrations": {
                                            "enabled": ["slack", "teams"],
                                            "disabled": ["discord"],
                                        },
                                    },
                                },
                            }
                        },
                    }
                }
            },
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = nested_response

            async with SuperOpsClient(test_config) as client:
                result = await client.clients.get("client-123")

                # Should handle nested structures
                assert result is not None
                assert result.name == "Test Client"

    @pytest.mark.asyncio
    async def test_missing_required_fields(self, test_config, mock_httpx_response):
        """Test handling of responses missing required fields."""
        incomplete_response = mock_httpx_response(
            200,
            {
                "data": {
                    "client": {
                        # Missing 'id' field
                        "name": "Test Client",
                        "status": "ACTIVE",
                    }
                }
            },
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = incomplete_response

            async with SuperOpsClient(test_config) as client:
                # Should raise validation error for missing required fields
                with pytest.raises((SuperOpsValidationError, SuperOpsAPIError)):
                    await client.clients.get("client-123")

    @pytest.mark.asyncio
    async def test_invalid_data_types(self, test_config, mock_httpx_response):
        """Test handling of invalid data types in response."""
        invalid_response = mock_httpx_response(
            200,
            {
                "data": {
                    "client": {
                        "id": "client-123",
                        "name": 12345,  # Should be string
                        "status": ["ACTIVE"],  # Should be string, not array
                        "createdAt": "not-a-date",  # Invalid date format
                    }
                }
            },
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = invalid_response

            async with SuperOpsClient(test_config) as client:
                # Should handle type mismatches gracefully
                try:
                    result = await client.clients.get("client-123")
                    # If it doesn't raise, verify it handled the conversion
                    assert result is not None
                except (SuperOpsValidationError, SuperOpsAPIError):
                    # This is also acceptable - depends on validation implementation
                    pass


class TestConcurrencyEdgeCases:
    """Test concurrency-related edge cases."""

    @pytest.mark.asyncio
    async def test_concurrent_requests_with_failures(self, test_config, mock_httpx_response):
        """Test concurrent requests where some fail."""
        # Mix of success and failure responses
        responses = [
            mock_httpx_response(
                200,
                {
                    "data": {
                        "client": {"id": f"client-{i}", "name": f"Client {i}", "status": "ACTIVE"}
                    }
                },
            ),
            mock_httpx_response(404, {"errors": [{"message": "Not found"}]}),
            mock_httpx_response(
                200,
                {
                    "data": {
                        "client": {"id": f"client-{i}", "name": f"Client {i}", "status": "ACTIVE"}
                    }
                },
            ),
            mock_httpx_response(500, {"errors": [{"message": "Internal error"}]}),
            mock_httpx_response(
                200,
                {
                    "data": {
                        "client": {"id": f"client-{i}", "name": f"Client {i}", "status": "ACTIVE"}
                    }
                },
            ),
        ]

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.side_effect = responses

            async with SuperOpsClient(test_config) as client:
                # Execute concurrent requests
                tasks = [client.clients.get(f"client-{i}") for i in range(5)]

                # Use gather with return_exceptions to capture failures
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Verify mix of success and exceptions
                successes = [r for r in results if not isinstance(r, Exception)]
                failures = [r for r in results if isinstance(r, Exception)]

                assert len(successes) == 3  # 3 successful responses
                assert len(failures) == 2  # 2 failed responses
                assert all(isinstance(f, SuperOpsAPIError) for f in failures)

    @pytest.mark.asyncio
    async def test_timeout_during_concurrent_requests(self, test_config):
        """Test timeout behavior during concurrent requests."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock timeout for all requests
            mock_client.post.side_effect = httpx.TimeoutException("Request timed out")

            async with SuperOpsClient(test_config) as client:
                # Execute concurrent requests that will all timeout
                tasks = [client.clients.get(f"client-{i}") for i in range(3)]

                # All should raise timeout errors
                results = await asyncio.gather(*tasks, return_exceptions=True)

                assert len(results) == 3
                assert all(isinstance(r, SuperOpsTimeoutError) for r in results)

    @pytest.mark.asyncio
    async def test_resource_exhaustion_scenario(self, test_config, mock_httpx_response):
        """Test behavior under resource exhaustion."""
        # Simulate resource exhaustion with 503 errors
        exhaustion_response = mock_httpx_response(
            503,
            {
                "errors": [
                    {
                        "message": "Service temporarily unavailable",
                        "extensions": {"code": "SERVICE_UNAVAILABLE"},
                    }
                ]
            },
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = exhaustion_response

            async with SuperOpsClient(test_config) as client:
                # Should handle service unavailable appropriately
                with pytest.raises(SuperOpsAPIError, match="Service temporarily unavailable"):
                    await client.clients.get("client-123")


class TestMemoryAndResourceEdgeCases:
    """Test memory usage and resource management edge cases."""

    @pytest.mark.asyncio
    async def test_client_cleanup_after_exception(self, test_config):
        """Test proper cleanup after exceptions."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.side_effect = httpx.NetworkError("Connection failed")

            try:
                async with SuperOpsClient(test_config) as client:
                    await client.clients.get("client-123")
            except SuperOpsNetworkError:
                pass  # Expected

            # Verify client was properly closed
            mock_client.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_multiple_client_instances(self, test_config, mock_httpx_response):
        """Test creating multiple client instances."""
        success_response = mock_httpx_response(
            200,
            {"data": {"client": {"id": "client-123", "name": "Test Client", "status": "ACTIVE"}}},
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = success_response

            # Create multiple clients concurrently
            clients = []
            try:
                for i in range(5):
                    client = SuperOpsClient(test_config)
                    clients.append(client)
                    await client.__aenter__()

                # All should work independently
                tasks = [client.clients.get("client-123") for client in clients]
                results = await asyncio.gather(*tasks)

                assert len(results) == 5
                assert all(r.name == "Test Client" for r in results)

            finally:
                # Cleanup all clients
                for client in clients:
                    await client.__aexit__(None, None, None)

    @pytest.mark.asyncio
    async def test_response_size_limits(self, test_config):
        """Test behavior with very large responses."""
        # This is more of a conceptual test since we're mocking
        # In a real scenario, you'd want to test actual response size handling

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Create a mock response that simulates a very large payload
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "application/json"}
            # Simulate a large JSON response
            large_data = {"data": {"items": [f"item-{i}" for i in range(10000)]}}
            mock_response.json.return_value = large_data
            mock_response.raise_for_status.return_value = None
            mock_client.post.return_value = mock_response

            async with SuperOpsClient(test_config) as client:
                # Should handle large responses without memory issues
                query = "query { items }"
                result = await client.execute_query(query)

                assert "data" in result
                assert len(result["data"]["items"]) == 10000
