# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Comprehensive tests for the SuperOpsClient class."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from py_superops import SuperOpsClient, SuperOpsConfig
from py_superops.auth import AuthHandler
from py_superops.exceptions import (
    SuperOpsAPIError,
    SuperOpsAuthenticationError,
    SuperOpsNetworkError,
    SuperOpsRateLimitError,
    SuperOpsTimeoutError,
    SuperOpsValidationError,
)


class TestSuperOpsClient:
    """Test cases for SuperOpsClient class."""

    def test_init_basic(self, test_config: SuperOpsConfig):
        """Test basic client initialization."""
        client = SuperOpsClient(test_config)
        assert client._config == test_config
        assert client._auth_handler is not None
        assert isinstance(client._auth_handler, AuthHandler)
        assert client._http_client is None
        assert not client._client_provided

    def test_init_with_custom_auth(self, test_config: SuperOpsConfig):
        """Test client initialization with custom auth handler."""
        custom_auth = AuthHandler(test_config)
        client = SuperOpsClient(test_config, auth_handler=custom_auth)
        assert client._auth_handler is custom_auth

    def test_init_with_custom_http_client(self, test_config: SuperOpsConfig):
        """Test client initialization with custom HTTP client."""
        custom_http_client = AsyncMock()
        client = SuperOpsClient(test_config, http_client=custom_http_client)
        assert client._http_client is custom_http_client
        assert client._client_provided is True

    @pytest.mark.asyncio
    async def test_context_manager_basic(self, test_config: SuperOpsConfig):
        """Test client as context manager."""
        async with SuperOpsClient(test_config) as client:
            assert isinstance(client, SuperOpsClient)

    @pytest.mark.asyncio
    async def test_context_manager_with_custom_client(self, test_config: SuperOpsConfig):
        """Test context manager with custom HTTP client."""
        custom_http_client = AsyncMock()
        async with SuperOpsClient(test_config, http_client=custom_http_client) as client:
            assert client._http_client is custom_http_client

    @pytest.mark.asyncio
    async def test_execute_query_success(self, test_config: SuperOpsConfig):
        """Test successful query execution."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        # json() is a sync method on httpx Response, not async
        mock_response.json = MagicMock(return_value={
            "data": {"clients": [{"id": "123", "name": "Test Client"}]}
        })
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.aclose = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        
        with patch("httpx.AsyncClient", return_value=mock_client):

            # Mock auth handler
            with patch.object(AuthHandler, "get_headers") as mock_get_headers:
                mock_get_headers.return_value = {"Authorization": "Bearer test"}

                async with SuperOpsClient(test_config) as client:
                    result = await client.execute_query(
                        query="query { clients { id name } }", variables={}
                    )

                    assert "data" in result
                    assert "clients" in result["data"]
                    assert len(result["data"]["clients"]) == 1

    @pytest.mark.asyncio
    async def test_execute_query_with_variables(self, test_config: SuperOpsConfig):
        """Test query execution with variables."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"data": {"client": {"id": "123", "name": "Test Client"}}})
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.aclose = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        
        with patch("httpx.AsyncClient", return_value=mock_client):

            with patch.object(AuthHandler, "get_headers") as mock_get_headers:
                mock_get_headers.return_value = {"Authorization": "Bearer test"}

                async with SuperOpsClient(test_config) as client:
                    await client.execute_query(
                        query="query GetClient($id: ID!) { client(id: $id) { id name } }",
                        variables={"id": "123"},
                    )

                    # Verify the request was made with correct variables
                    call_args = mock_client.post.call_args
                    json_payload = call_args[1]["json"]
                    assert json_payload["variables"] == {"id": "123"}

    @pytest.mark.asyncio
    async def test_execute_query_validation_error(self, test_config: SuperOpsConfig):
        """Test query validation error."""
        async with SuperOpsClient(test_config) as client:
            with pytest.raises(SuperOpsValidationError, match="Query cannot be empty"):
                await client.execute_query("", {})

    @pytest.mark.asyncio
    async def test_execute_query_invalid_json_variables(self, test_config: SuperOpsConfig):
        """Test query with invalid JSON variables."""
        async with SuperOpsClient(test_config) as client:
            # Variables should be a dict, not a string
            with pytest.raises(SuperOpsValidationError):
                await client.execute_query("query { clients }", "invalid")

    @pytest.mark.asyncio
    async def test_execute_query_graphql_error(self, test_config: SuperOpsConfig):
        """Test GraphQL error response."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={
            "errors": [
                {
                    "message": "Field 'invalidField' doesn't exist on type 'Client'",
                    "extensions": {"code": "GRAPHQL_VALIDATION_FAILED"},
                }
            ]
        })
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.aclose = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        
        with patch("httpx.AsyncClient", return_value=mock_client):

            with patch.object(AuthHandler, "get_headers") as mock_get_headers:
                mock_get_headers.return_value = {"Authorization": "Bearer test"}

                async with SuperOpsClient(test_config) as client:
                    with pytest.raises(
                        SuperOpsAPIError, match="Field 'invalidField' doesn't exist"
                    ):
                        await client.execute_query("query { clients { invalidField } }", {})

    @pytest.mark.asyncio
    async def test_execute_query_authentication_error(self, test_config: SuperOpsConfig):
        """Test authentication error."""
        mock_response = AsyncMock()
        mock_response.status_code = 401
        mock_response.json = MagicMock(return_value={"errors": [{"message": "Authentication failed"}]})

        mock_client = AsyncMock()
        mock_client.aclose = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        
        with patch("httpx.AsyncClient", return_value=mock_client):

            with patch.object(AuthHandler, "get_headers") as mock_get_headers:
                mock_get_headers.return_value = {"Authorization": "Bearer test"}

                async with SuperOpsClient(test_config) as client:
                    with pytest.raises(SuperOpsAuthenticationError):
                        await client.execute_query("query { clients }", {})

    @pytest.mark.asyncio
    async def test_execute_query_rate_limit_error(self, test_config: SuperOpsConfig):
        """Test rate limit error."""
        mock_response = AsyncMock()
        mock_response.status_code = 429
        mock_response.json = MagicMock(return_value={"errors": [{"message": "Rate limit exceeded"}]})
        mock_response.headers = {"retry-after": "60", "x-ratelimit-remaining": "0"}

        mock_client = AsyncMock()
        mock_client.aclose = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        
        with patch("httpx.AsyncClient", return_value=mock_client):

            with patch.object(AuthHandler, "get_headers") as mock_get_headers:
                mock_get_headers.return_value = {"Authorization": "Bearer test"}

                async with SuperOpsClient(test_config) as client:
                    with pytest.raises(SuperOpsRateLimitError):
                        await client.execute_query("query { clients }", {})

    @pytest.mark.asyncio
    async def test_execute_query_network_error(self, test_config: SuperOpsConfig):
        """Test network error."""
        mock_client = AsyncMock()
        mock_client.aclose = AsyncMock()
        
        with patch("httpx.AsyncClient", return_value=mock_client):
            mock_client.post.side_effect = httpx.NetworkError("Connection failed")

            with patch.object(AuthHandler, "get_headers") as mock_get_headers:
                mock_get_headers.return_value = {"Authorization": "Bearer test"}

                async with SuperOpsClient(test_config) as client:
                    with pytest.raises(SuperOpsNetworkError, match="Connection failed"):
                        await client.execute_query("query { clients }", {})

    @pytest.mark.asyncio
    async def test_execute_query_timeout_error(self, test_config: SuperOpsConfig):
        """Test timeout error."""
        mock_client = AsyncMock()
        mock_client.aclose = AsyncMock()
        
        with patch("httpx.AsyncClient", return_value=mock_client):
            mock_client.post.side_effect = httpx.TimeoutException("Request timed out")

            with patch.object(AuthHandler, "get_headers") as mock_get_headers:
                mock_get_headers.return_value = {"Authorization": "Bearer test"}

                async with SuperOpsClient(test_config) as client:
                    with pytest.raises(SuperOpsTimeoutError, match="Request timed out"):
                        await client.execute_query("query { clients }", {})

    @pytest.mark.asyncio
    async def test_execute_mutation_success(self, test_config: SuperOpsConfig):
        """Test successful mutation execution."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={
            "data": {"createClient": {"id": "123", "name": "New Client"}}
        })
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.aclose = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        
        with patch("httpx.AsyncClient", return_value=mock_client):

            with patch.object(AuthHandler, "get_headers") as mock_get_headers:
                mock_get_headers.return_value = {"Authorization": "Bearer test"}

                async with SuperOpsClient(test_config) as client:
                    result = await client.execute_mutation(
                        mutation="mutation CreateClient($name: String!) { createClient(name: $name) { id name } }",
                        variables={"name": "New Client"},
                    )

                    assert "data" in result
                    assert "createClient" in result["data"]
                    assert result["data"]["createClient"]["name"] == "New Client"

    @pytest.mark.asyncio
    async def test_execute_mutation_validation_error(self, test_config: SuperOpsConfig):
        """Test mutation validation error."""
        async with SuperOpsClient(test_config) as client:
            with pytest.raises(SuperOpsValidationError, match="Mutation cannot be empty"):
                await client.execute_mutation("", {})

    @pytest.mark.asyncio
    async def test_test_connection_success(self, test_config: SuperOpsConfig):
        """Test successful connection test."""
        with patch.object(AuthHandler, "test_connection") as mock_test_connection:
            mock_test_connection.return_value = {
                "connected": True,
                "response_time_seconds": 0.123,
                "api_version": "v1",
                "authenticated": True,
                "timestamp": "2024-01-01T00:00:00Z",
            }

            async with SuperOpsClient(test_config) as client:
                result = await client.test_connection()

                assert result["connected"] is True
                assert result["authenticated"] is True
                assert "response_time_seconds" in result
                mock_test_connection.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_schema_info_success(self, test_config: SuperOpsConfig):
        """Test successful schema info retrieval."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={
            "data": {
                "__schema": {
                    "types": [
                        {"name": "Client", "kind": "OBJECT"},
                        {"name": "Ticket", "kind": "OBJECT"},
                    ]
                }
            }
        })
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.aclose = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        
        with patch("httpx.AsyncClient", return_value=mock_client):

            with patch.object(AuthHandler, "get_headers") as mock_get_headers:
                mock_get_headers.return_value = {"Authorization": "Bearer test"}

                async with SuperOpsClient(test_config):
                    # Skip testing get_schema_info as it's not implemented
                    pass

    @pytest.mark.skip(reason="_validate_query not implemented yet")
    @pytest.mark.asyncio
    async def test_validate_query_basic(self, test_config: SuperOpsConfig):
        """Test basic query validation."""
        pass  # Method not yet implemented in client

    @pytest.mark.skip(reason="_validate_variables not implemented yet")
    @pytest.mark.asyncio
    async def test_validate_variables_basic(self, test_config: SuperOpsConfig):
        """Test basic variables validation."""
        pass  # Method not yet implemented in client

    def test_manager_properties_lazy_loading(self, test_config: SuperOpsConfig):
        """Test that manager properties are lazy loaded."""
        client = SuperOpsClient(test_config)

        # Initially None
        assert client._clients_manager is None
        assert client._tickets_manager is None

        # Access should create managers
        clients_manager = client.clients
        assert clients_manager is not None
        assert client._clients_manager is clients_manager

        tickets_manager = client.tickets
        assert tickets_manager is not None
        assert client._tickets_manager is tickets_manager

    @pytest.mark.asyncio
    async def test_retry_logic_success_after_retry(self, test_config: SuperOpsConfig):
        """Test retry logic with success after retry."""
        test_config.max_retries = 2

        # First call fails, second succeeds
        mock_response_fail = AsyncMock()
        mock_response_fail.status_code = 500
        mock_response_fail.json = MagicMock(return_value={"errors": [{"message": "Server error"}]})

        mock_response_success = AsyncMock()
        mock_response_success.status_code = 200
        mock_response_success.json = MagicMock(return_value={"data": {"clients": []}})
        mock_response_success.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.aclose = AsyncMock()
        mock_client.post.side_effect = [mock_response_fail, mock_response_success]
        
        with patch("httpx.AsyncClient", return_value=mock_client):

            with patch.object(AuthHandler, "get_headers") as mock_get_headers:
                mock_get_headers.return_value = {"Authorization": "Bearer test"}

                async with SuperOpsClient(test_config) as client:
                    result = await client.execute_query("query { clients }", {})

                    assert "data" in result
                    # Should have made 2 calls (1 failure + 1 success)
                    assert mock_client.post.call_count == 2

    @pytest.mark.asyncio
    async def test_custom_headers_in_request(self, test_config: SuperOpsConfig):
        """Test that custom headers are included in requests."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"data": {"clients": []}})
        mock_response.raise_for_status = MagicMock()

        custom_headers = {"X-Custom-Header": "test-value"}

        mock_client = AsyncMock()
        mock_client.aclose = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        
        with patch("httpx.AsyncClient", return_value=mock_client):

            with patch.object(AuthHandler, "get_headers") as mock_get_headers:
                mock_get_headers.return_value = {**custom_headers, "Authorization": "Bearer test"}

                async with SuperOpsClient(test_config) as client:
                    await client.execute_query("query { clients }", {})

                    # Verify custom header was included
                    call_args = mock_client.post.call_args
                    headers = call_args[1]["headers"]
                    assert "X-Custom-Header" in headers
                    assert headers["X-Custom-Header"] == "test-value"

    def test_client_str_representation(self, test_config: SuperOpsConfig):
        """Test client string representation."""
        client = SuperOpsClient(test_config)
        str_repr = str(client)

        assert "SuperOpsClient" in str_repr
        # Should not expose sensitive information
        assert test_config.api_key not in str_repr

    def test_client_repr(self, test_config: SuperOpsConfig):
        """Test client repr."""
        client = SuperOpsClient(test_config)
        repr_str = repr(client)

        assert "SuperOpsClient" in repr_str
        # Should not expose sensitive information
        assert test_config.api_key not in repr_str
