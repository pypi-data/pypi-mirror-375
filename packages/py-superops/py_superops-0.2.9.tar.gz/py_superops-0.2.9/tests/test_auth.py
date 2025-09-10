# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Comprehensive tests for the authentication module."""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from py_superops import SuperOpsConfig
from py_superops.auth import AuthHandler
from py_superops.exceptions import (
    SuperOpsAuthenticationError,
    SuperOpsNetworkError,
    SuperOpsTimeoutError,
)


class TestAuthHandler:
    """Test cases for AuthHandler class."""

    def test_init(self, test_config: SuperOpsConfig):
        """Test AuthHandler initialization."""
        auth = AuthHandler(test_config)
        assert auth._config == test_config
        assert auth._token_validated is False
        assert auth._validation_time is None
        assert not auth.is_token_validated

    def test_is_token_validated_fresh(self, test_config: SuperOpsConfig):
        """Test token validation freshness check."""
        auth = AuthHandler(test_config)

        # Initially not validated
        assert not auth.is_token_validated

        # Set validated with fresh timestamp
        auth._token_validated = True
        auth._validation_time = datetime.now()
        assert auth.is_token_validated

        # Set validated with stale timestamp (over 5 minutes)
        auth._validation_time = datetime.now() - timedelta(minutes=6)
        assert not auth.is_token_validated

    def test_is_validation_fresh_no_validation_time(self, test_config: SuperOpsConfig):
        """Test validation freshness when no validation time is set."""
        auth = AuthHandler(test_config)
        auth._token_validated = True
        # _validation_time is None
        assert not auth._is_validation_fresh()

    @pytest.mark.asyncio
    async def test_get_headers_basic(self, test_config: SuperOpsConfig):
        """Test getting basic authentication headers."""
        auth = AuthHandler(test_config)
        headers = await auth.get_headers()

        # Headers should contain authorization and be from config
        assert "Authorization" in headers
        assert "Content-Type" in headers
        # Note: User-Agent may not be included depending on config implementation
        assert headers["Authorization"] == f"Bearer {test_config.api_key}"

    @pytest.mark.asyncio
    async def test_get_headers_debug_mode(self, test_config: SuperOpsConfig):
        """Test that debug headers are added when debug mode is enabled."""
        test_config.debug = True
        auth = AuthHandler(test_config)
        headers = await auth.get_headers()

        assert "X-Debug" in headers
        assert headers["X-Debug"] == "true"

    def test_invalidate_token(self, test_config: SuperOpsConfig):
        """Test token invalidation."""
        auth = AuthHandler(test_config)

        # Set up validated token
        auth._token_validated = True
        auth._validation_time = datetime.now()
        assert auth.is_token_validated

        # Invalidate
        auth.invalidate_token()
        assert not auth._token_validated
        assert auth._validation_time is None
        assert not auth.is_token_validated

    def test_is_token_format_valid(self, test_config: SuperOpsConfig):
        """Test token format validation."""
        auth = AuthHandler(test_config)

        # Valid token (test_config has valid token)
        assert auth.is_token_format_valid() is True

    @pytest.mark.asyncio
    async def test_authenticate_success(self, test_config: SuperOpsConfig):
        """Test successful authentication."""
        auth = AuthHandler(test_config)

        # Mock successful HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"__schema": {"queryType": {"name": "Query"}}}}
        mock_response.content = b'{"data": {"__schema": {"queryType": {"name": "Query"}}}}'

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response

            result = await auth.authenticate()

            assert result == test_config.api_key
            assert auth._token_validated is True
            assert auth._validation_time is not None

    @pytest.mark.asyncio
    async def test_authenticate_already_valid(self, test_config: SuperOpsConfig):
        """Test that authentication returns cached token when valid."""
        auth = AuthHandler(test_config)

        # Set up validated token
        auth._token_validated = True
        auth._validation_time = datetime.now()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await auth.authenticate()

            assert result == test_config.api_key
            # Should not have made HTTP request
            mock_client.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_authenticate_401_error(self, test_config: SuperOpsConfig):
        """Test authentication with 401 error."""
        auth = AuthHandler(test_config)

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {}
        mock_response.content = b"{}"

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response

            with pytest.raises(SuperOpsAuthenticationError, match="Invalid API key"):
                await auth.authenticate()

    @pytest.mark.asyncio
    async def test_authenticate_403_error(self, test_config: SuperOpsConfig):
        """Test authentication with 403 error."""
        auth = AuthHandler(test_config)

        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {}
        mock_response.content = b"{}"

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response

            with pytest.raises(SuperOpsAuthenticationError, match="Insufficient permissions"):
                await auth.authenticate()

    @pytest.mark.asyncio
    async def test_authenticate_graphql_auth_error(self, test_config: SuperOpsConfig):
        """Test authentication with GraphQL authentication error."""
        auth = AuthHandler(test_config)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"errors": [{"message": "Unauthenticated request"}]}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response

            with pytest.raises(SuperOpsAuthenticationError, match="GraphQL authentication error"):
                await auth.authenticate()

    @pytest.mark.asyncio
    async def test_authenticate_network_error(self, test_config: SuperOpsConfig):
        """Test authentication with network error."""
        auth = AuthHandler(test_config)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.side_effect = httpx.NetworkError("Connection failed")

            with pytest.raises(SuperOpsNetworkError, match="Network error during token validation"):
                await auth.authenticate()

    @pytest.mark.asyncio
    async def test_authenticate_timeout_error(self, test_config: SuperOpsConfig):
        """Test authentication with timeout error."""
        auth = AuthHandler(test_config)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.side_effect = httpx.TimeoutException("Request timed out")

            with pytest.raises(SuperOpsTimeoutError, match="Token validation timed out"):
                await auth.authenticate()

    @pytest.mark.asyncio
    async def test_refresh_token(self, test_config: SuperOpsConfig):
        """Test token refresh."""
        auth = AuthHandler(test_config)

        # Set up validated token
        auth._token_validated = True
        auth._validation_time = datetime.now()

        # Mock successful HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"__schema": {"queryType": {"name": "Query"}}}}
        mock_response.content = b'{"data": {"__schema": {"queryType": {"name": "Query"}}}}'

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response

            result = await auth.refresh_token()

            assert result == test_config.api_key
            assert auth._token_validated is True
            # Should have made HTTP request even though token was valid
            mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_test_connection_success(self, test_config: SuperOpsConfig):
        """Test successful connection test."""
        auth = AuthHandler(test_config)

        # Mock successful HTTP responses for both validate and test
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "__schema": {
                    "queryType": {"name": "Query"},
                    "mutationType": {"name": "Mutation"},
                    "subscriptionType": None,
                }
            }
        }
        mock_response.content = b'{"data": {"__schema": {"queryType": {"name": "Query"}}}}'
        mock_response.raise_for_status.return_value = None

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response

            result = await auth.test_connection()

            assert result["connected"] is True
            assert "response_time_seconds" in result
            assert result["api_version"] == "v1"
            assert result["authenticated"] is True
            assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_test_connection_http_error(self, test_config: SuperOpsConfig):
        """Test connection test with HTTP error."""
        auth = AuthHandler(test_config)

        # Mock HTTP error
        http_error = httpx.HTTPStatusError(
            "401 Unauthorized", request=MagicMock(), response=MagicMock(status_code=401)
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.side_effect = http_error

            with pytest.raises(SuperOpsAuthenticationError):
                await auth.test_connection()

    @pytest.mark.asyncio
    async def test_concurrent_authentication(self, test_config: SuperOpsConfig):
        """Test that concurrent authentication calls are handled properly."""
        auth = AuthHandler(test_config)

        # Mock successful HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"__schema": {"queryType": {"name": "Query"}}}}
        mock_response.content = b'{"data": {"__schema": {"queryType": {"name": "Query"}}}}'

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response

            # Start multiple authentication tasks concurrently
            tasks = [auth.authenticate() for _ in range(3)]
            results = await asyncio.gather(*tasks)

            # All should succeed and return the same token
            assert all(result == test_config.api_key for result in results)
            assert auth._token_validated is True

            # Should have made only one HTTP request due to locking
            assert mock_client.post.call_count == 1
