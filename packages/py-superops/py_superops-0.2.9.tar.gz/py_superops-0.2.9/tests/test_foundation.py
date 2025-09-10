# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Tests for the foundational components of py-superops."""

# Import the components we want to test
import sys
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from py_superops import (
    AuthHandler,
    SuperOpsAPIError,
    SuperOpsAuthenticationError,
    SuperOpsClient,
    SuperOpsConfig,
    SuperOpsConfigurationError,
    SuperOpsError,
    SuperOpsValidationError,
    create_client,
    get_version,
)


class TestSuperOpsConfig:
    """Test cases for SuperOpsConfig."""

    def test_config_creation_with_required_fields(self):
        """Test creating config with required fields."""
        config = SuperOpsConfig(
            api_key="test-api-key-12345678", base_url="https://api.superops.com/v1"
        )

        assert config.api_key == "test-api-key-12345678"
        assert config.base_url == "https://api.superops.com/v1"
        assert config.timeout == 30.0
        assert config.max_retries == 3

    def test_config_validation_empty_api_key(self):
        """Test validation with empty API key."""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            SuperOpsConfig(api_key="", base_url="https://api.superops.com/v1")

    def test_config_validation_invalid_base_url(self):
        """Test validation with invalid base URL."""
        with pytest.raises(ValueError, match="Invalid base URL format"):
            SuperOpsConfig(api_key="test-api-key-12345678", base_url="not-a-url")

    def test_config_validation_short_api_key(self):
        """Test validation with short API key."""
        with pytest.raises(ValueError, match="API key appears to be too short"):
            SuperOpsConfig(api_key="short", base_url="https://api.superops.com/v1")

    def test_config_base_url_normalization(self):
        """Test base URL normalization (removing trailing slash)."""
        config = SuperOpsConfig(
            api_key="test-api-key-12345678", base_url="https://api.superops.com/v1/"
        )

        assert config.base_url == "https://api.superops.com/v1"

    def test_config_headers(self):
        """Test header generation."""
        config = SuperOpsConfig(
            api_key="test-api-key-12345678", base_url="https://api.superops.com/v1"
        )

        headers = config.get_headers()

        assert headers["Authorization"] == "Bearer test-api-key-12345678"
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"

    def test_datacenter_detection(self):
        """Test datacenter detection."""
        us_config = SuperOpsConfig(
            api_key="test-api-key-12345678", base_url="https://api.superops.com/v1"
        )

        eu_config = SuperOpsConfig(
            api_key="test-api-key-12345678", base_url="https://eu.superops.com/v1"
        )

        assert us_config.is_us_datacenter() is True
        assert us_config.is_eu_datacenter() is False
        assert eu_config.is_us_datacenter() is False
        assert eu_config.is_eu_datacenter() is True

    def test_config_validation(self):
        """Test comprehensive config validation."""
        config = SuperOpsConfig(
            api_key="test-api-key-12345678", base_url="https://api.superops.com/v1"
        )

        # Should not raise
        config.validate_config()

        # Test invalid configuration
        invalid_config = SuperOpsConfig(
            api_key="test-api-key-12345678",
            base_url="https://api.superops.com/v1",
            burst_limit=100,
            rate_limit_per_minute=50,  # Lower than burst limit
        )

        with pytest.raises(SuperOpsConfigurationError, match="Burst limit cannot exceed"):
            invalid_config.validate_config()


class TestAuthHandler:
    """Test cases for AuthHandler."""

    def test_auth_handler_creation(self):
        """Test creating auth handler."""
        config = SuperOpsConfig(
            api_key="test-api-key-12345678", base_url="https://api.superops.com/v1"
        )

        auth = AuthHandler(config)

        assert auth._config == config
        assert auth._token_validated is False

    def test_token_format_validation(self):
        """Test token format validation."""
        config = SuperOpsConfig(
            api_key="test-api-key-12345678", base_url="https://api.superops.com/v1"
        )

        auth = AuthHandler(config)

        assert auth.is_token_format_valid() is True

        # Test invalid token by creating a mock config with invalid key
        from unittest.mock import Mock

        mock_config = Mock()
        mock_config.api_key = "short"

        invalid_auth = AuthHandler(mock_config)

        # This should return False due to short key
        assert invalid_auth.is_token_format_valid() is False

        # Test placeholder value
        mock_config.api_key = "your-api-key"
        placeholder_auth = AuthHandler(mock_config)
        assert placeholder_auth.is_token_format_valid() is False

    @pytest.mark.asyncio
    async def test_get_headers(self):
        """Test getting authentication headers."""
        config = SuperOpsConfig(
            api_key="test-api-key-12345678", base_url="https://api.superops.com/v1"
        )

        auth = AuthHandler(config)
        headers = await auth.get_headers()

        assert headers["Authorization"] == "Bearer test-api-key-12345678"
        assert headers["Content-Type"] == "application/json"

    def test_invalidate_token(self):
        """Test token invalidation."""
        from datetime import datetime

        config = SuperOpsConfig(
            api_key="test-api-key-12345678", base_url="https://api.superops.com/v1"
        )

        auth = AuthHandler(config)

        # Simulate validated token with recent validation time
        auth._token_validated = True
        auth._validation_time = datetime.now()

        assert auth.is_token_validated is True

        auth.invalidate_token()

        assert auth.is_token_validated is False


class TestSuperOpsClient:
    """Test cases for SuperOpsClient."""

    def test_client_creation(self):
        """Test creating client."""
        config = SuperOpsConfig(
            api_key="test-api-key-12345678", base_url="https://api.superops.com/v1"
        )

        client = SuperOpsClient(config)

        assert client.config == config
        assert isinstance(client.auth_handler, AuthHandler)

    def test_client_with_custom_auth_handler(self):
        """Test creating client with custom auth handler."""
        config = SuperOpsConfig(
            api_key="test-api-key-12345678", base_url="https://api.superops.com/v1"
        )

        custom_auth = AuthHandler(config)
        client = SuperOpsClient(config, auth_handler=custom_auth)

        assert client.auth_handler == custom_auth

    @pytest.mark.asyncio
    async def test_query_validation(self):
        """Test query validation."""
        config = SuperOpsConfig(
            api_key="test-api-key-12345678", base_url="https://api.superops.com/v1"
        )

        client = SuperOpsClient(config)

        # Test empty query
        with pytest.raises(SuperOpsValidationError, match="Query cannot be empty"):
            await client.execute_query("")

        # Test None query
        with pytest.raises(SuperOpsValidationError, match="Query cannot be empty"):
            await client.execute_query(None)

    @pytest.mark.asyncio
    async def test_mutation_validation(self):
        """Test mutation validation."""
        config = SuperOpsConfig(
            api_key="test-api-key-12345678", base_url="https://api.superops.com/v1"
        )

        client = SuperOpsClient(config)

        # Test empty mutation
        with pytest.raises(SuperOpsValidationError, match="Mutation cannot be empty"):
            await client.execute_mutation("")

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        config = SuperOpsConfig(
            api_key="test-api-key-12345678", base_url="https://api.superops.com/v1"
        )

        async with SuperOpsClient(config) as client:
            assert isinstance(client, SuperOpsClient)
            # Client should be set up
            assert client._http_client is not None

        # After exit, client should be cleaned up
        # Note: We don't check _http_client is None because it might still exist
        # but it should be closed


class TestExceptions:
    """Test cases for custom exceptions."""

    def test_superops_error(self):
        """Test base SuperOps error."""
        error = SuperOpsError("Test message", {"key": "value"})

        assert str(error) == "Test message"
        assert error.message == "Test message"
        assert error.details == {"key": "value"}

    def test_superops_api_error(self):
        """Test API error."""
        error = SuperOpsAPIError(
            "API error", status_code=400, response_data={"error": "Bad request"}
        )

        assert error.status_code == 400
        assert error.response_data == {"error": "Bad request"}

    def test_authentication_error(self):
        """Test authentication error."""
        error = SuperOpsAuthenticationError()

        assert "Authentication failed" in str(error)
        assert error.status_code == 401

    def test_configuration_error(self):
        """Test configuration error."""
        error = SuperOpsConfigurationError("Config error", config_field="api_key")

        assert error.config_field == "api_key"


class TestConvenienceFunctions:
    """Test cases for convenience functions."""

    def test_create_client_with_params(self):
        """Test create_client function with parameters."""
        client = create_client(
            api_key="test-api-key-12345678", base_url="https://api.superops.com/v1"
        )

        assert isinstance(client, SuperOpsClient)
        assert client.config.api_key == "test-api-key-12345678"
        assert client.config.base_url == "https://api.superops.com/v1"

    @patch.dict("os.environ", {"SUPEROPS_API_KEY": "env-test-key-123456"})
    def test_create_client_from_env(self):
        """Test create_client function with environment variables."""
        client = create_client()

        assert isinstance(client, SuperOpsClient)
        assert client.config.api_key == "env-test-key-123456"

    def test_get_version(self):
        """Test get_version function."""
        version = get_version()

        assert isinstance(version, str)
        assert len(version) > 0


class TestPackageIntegrity:
    """Test cases for package integrity."""

    def test_all_exports_available(self):
        """Test that all expected exports are available."""
        from py_superops import (
            AuthHandler,
            SuperOpsAPIError,
            SuperOpsAuthenticationError,
            SuperOpsClient,
            SuperOpsConfig,
            SuperOpsConfigurationError,
            SuperOpsError,
            SuperOpsNetworkError,
            SuperOpsRateLimitError,
            SuperOpsResourceNotFoundError,
            SuperOpsTimeoutError,
            SuperOpsValidationError,
            create_client,
            get_default_config,
            get_package_info,
            get_version,
            load_config,
        )

        # If we get here without ImportError, all exports are available
        assert True

    def test_version_format(self):
        """Test version string format."""
        version = get_version()

        # Should be in semantic versioning format
        parts = version.split(".")
        assert len(parts) >= 2  # At least major.minor

        # All parts should be numeric (for basic semver)
        for part in parts:
            # Handle pre-release suffixes like "1.0.0-alpha"
            base_part = part.split("-")[0]
            assert base_part.isdigit(), f"Version part '{base_part}' is not numeric"

    def test_package_info(self):
        """Test package info function."""
        from py_superops import get_package_info

        info = get_package_info()

        assert isinstance(info, dict)
        assert "name" in info
        assert "version" in info
        assert "description" in info
        assert info["name"] == "py-superops"
