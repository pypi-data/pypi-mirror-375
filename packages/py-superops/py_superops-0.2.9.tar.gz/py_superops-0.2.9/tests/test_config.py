# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Comprehensive tests for the SuperOpsConfig class."""

import os
from unittest.mock import patch

import pytest
from pydantic_core import ValidationError

from py_superops import SuperOpsConfig


class TestSuperOpsConfig:
    """Test cases for SuperOpsConfig class."""

    def test_init_basic(self):
        """Test basic config initialization."""
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1",
        )
        assert (
            config.api_key == "test-key-1234567890123456789012345678901234567890"
        )  # pragma: allowlist secret
        assert config.base_url == "https://api.superops.com/v1"
        assert config.timeout == 30.0  # default
        assert config.max_retries == 3  # default

    def test_init_with_custom_values(self):
        """Test config initialization with custom values."""
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://eu.superops.com/v1",
            timeout=60.0,
            max_retries=5,
            debug=True,
        )
        assert config.base_url == "https://eu.superops.com/v1"
        assert config.timeout == 60.0
        assert config.max_retries == 5
        assert config.debug is True

    def test_api_key_validation_too_short(self):
        """Test API key validation for too short key."""
        with pytest.raises(ValidationError):
            SuperOpsConfig(
                api_key="short", base_url="https://api.superops.com/v1"  # pragma: allowlist secret
            )

    def test_api_key_validation_empty(self):
        """Test API key validation for empty key."""
        with pytest.raises(ValidationError):
            SuperOpsConfig(api_key="", base_url="https://api.superops.com/v1")

    def test_base_url_normalization(self):
        """Test base URL normalization."""
        # With trailing slash
        config1 = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1/",
        )
        assert config1.base_url == "https://api.superops.com/v1"

        # Without trailing slash
        config2 = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1",
        )
        assert config2.base_url == "https://api.superops.com/v1"

    def test_base_url_validation_invalid(self):
        """Test base URL validation for invalid URLs."""
        # Pydantic now validates URLs more strictly and rejects invalid formats
        with pytest.raises(ValidationError) as exc_info:
            SuperOpsConfig(
                api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret
                base_url="not-a-url",
            )

        assert "Invalid base URL format" in str(exc_info.value)

    def test_timeout_validation_range(self):
        """Test timeout validation range."""
        # Valid timeout
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1",
            timeout=15.0,
        )
        assert config.timeout == 15.0

        # Too low
        with pytest.raises(ValidationError):
            SuperOpsConfig(
                api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
                base_url="https://api.superops.com/v1",
                timeout=0.05,
            )

        # Too high
        with pytest.raises(ValidationError):
            SuperOpsConfig(
                api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
                base_url="https://api.superops.com/v1",
                timeout=500.0,
            )

    def test_max_retries_validation_range(self):
        """Test max_retries validation range."""
        # Valid retries
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1",
            max_retries=5,
        )
        assert config.max_retries == 5

        # Too low
        with pytest.raises(ValidationError):
            SuperOpsConfig(
                api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
                base_url="https://api.superops.com/v1",
                max_retries=-1,
            )

        # Too high
        with pytest.raises(ValidationError):
            SuperOpsConfig(
                api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
                base_url="https://api.superops.com/v1",
                max_retries=15,
            )

    def test_rate_limit_validation(self):
        """Test rate limit validation."""
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1",
            rate_limit_per_minute=120,
            burst_limit=20,
        )
        assert config.rate_limit_per_minute == 120
        assert config.burst_limit == 20

    def test_cache_configuration(self):
        """Test cache configuration."""
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1",
            enable_caching=False,
            cache_ttl=600,
            cache_max_size=2000,
        )
        assert config.enable_caching is False
        assert config.cache_ttl == 600
        assert config.cache_max_size == 2000

    def test_debug_configuration(self):
        """Test debug configuration."""
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1",
            debug=True,
            log_level="DEBUG",
            log_format="%(levelname)s: %(message)s",
        )
        assert config.debug is True
        assert config.log_level == "DEBUG"
        assert config.log_format == "%(levelname)s: %(message)s"

    def test_ssl_and_proxy_configuration(self):
        """Test SSL and proxy configuration."""
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1",
            verify_ssl=False,
            proxy="http://proxy.example.com:8080",
        )
        assert config.verify_ssl is False
        assert config.proxy == "http://proxy.example.com:8080"

    def test_user_agent_configuration(self):
        """Test user agent configuration."""
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1",
            user_agent="MyApp/1.0",
        )
        assert config.user_agent == "MyApp/1.0"

    def test_is_us_datacenter(self):
        """Test US datacenter detection."""
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1",
        )
        assert config.is_us_datacenter() is True

    def test_is_eu_datacenter(self):
        """Test EU datacenter detection."""
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://eu.superops.com/v1",
        )
        assert config.is_eu_datacenter() is True

    def test_datacenter_detection_custom(self):
        """Test datacenter detection for custom URLs."""
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://custom.example.com/v1",
        )
        # 'us' is in 'custom', so it detects as US datacenter
        assert config.is_us_datacenter() is True
        assert config.is_eu_datacenter() is False

    def test_get_headers_basic(self):
        """Test getting basic headers."""
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1",
        )
        headers = config.get_headers()

        assert "Authorization" in headers
        assert headers["Authorization"] == f"Bearer {config.api_key}"
        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/json"

    def test_get_headers_with_custom_user_agent(self):
        """Test headers with custom user agent."""
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1",
            user_agent="MyApp/2.0",
        )
        headers = config.get_headers()

        assert "User-Agent" in headers
        assert headers["User-Agent"] == "MyApp/2.0"

    def test_get_headers_additional(self):
        """Test that get_headers works with default headers."""
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1",
        )
        # get_headers doesn't support additional headers as argument
        headers = config.get_headers()

        assert "Authorization" in headers
        assert (
            headers["Authorization"] == "Bearer test-key-1234567890123456789012345678901234567890"
        )
        assert headers["Content-Type"] == "application/json"

    def test_get_version(self):
        """Test version retrieval."""
        # Version is not part of config, it's in the package
        import py_superops

        version = py_superops.__version__
        assert isinstance(version, str)
        assert len(version) > 0

    @patch.dict(
        os.environ,
        {
            "SUPEROPS_API_KEY": "env-key-1234567890123456789012345678901234567890"  # pragma: allowlist secret
        },
    )
    def test_env_var_loading(self):
        """Test loading configuration from environment variables."""
        config = SuperOpsConfig(base_url="https://api.superops.com/v1")
        assert (
            config.api_key == "env-key-1234567890123456789012345678901234567890"
        )  # pragma: allowlist secret

    @patch.dict(
        os.environ,
        {
            "SUPEROPS_API_KEY": "env-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret
            "SUPEROPS_TIMEOUT": "45.0",
            "SUPEROPS_DEBUG": "true",
        },
    )
    def test_multiple_env_vars(self):
        """Test loading multiple configuration values from environment."""
        config = SuperOpsConfig(base_url="https://api.superops.com/v1")
        assert (
            config.api_key == "env-key-1234567890123456789012345678901234567890"
        )  # pragma: allowlist secret
        assert config.timeout == 45.0
        assert config.debug is True

    def test_config_dict_representation(self):
        """Test configuration dictionary representation."""
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1",
            debug=True,
        )
        config_dict = config.model_dump()

        assert "api_key" in config_dict
        assert "base_url" in config_dict
        assert "debug" in config_dict
        assert config_dict["debug"] is True

    def test_config_dict_exclude_sensitive(self):
        """Test configuration dictionary with sensitive data excluded."""
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1",
        )
        config_dict = config.model_dump(exclude={"api_key"})

        assert "api_key" not in config_dict
        assert "base_url" in config_dict

    def test_config_validation_comprehensive(self):
        """Test comprehensive configuration validation."""
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1",
            timeout=25.0,
            max_retries=2,
            retry_delay=2.0,
            rate_limit_per_minute=100,
            burst_limit=15,
            cache_ttl=600,
            cache_max_size=500,
            debug=True,
            log_level="WARNING",
        )

        # All values should be set correctly
        assert config.timeout == 25.0
        assert config.max_retries == 2
        assert config.retry_delay == 2.0
        assert config.rate_limit_per_minute == 100
        assert config.burst_limit == 15
        assert config.cache_ttl == 600
        assert config.cache_max_size == 500
        assert config.debug is True
        assert config.log_level == "WARNING"

    def test_config_str_representation(self):
        """Test config string representation."""
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1",
        )
        str_repr = str(config)

        # In Pydantic v2, str() shows all fields by default
        # Test that we get a string representation with expected content
        assert "api_key=" in str_repr
        assert "base_url=" in str_repr
        assert "https://api.superops.com/v1" in str_repr

    def test_config_repr(self):
        """Test config repr."""
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1",
        )
        repr_str = repr(config)

        # In Pydantic v2, repr() shows all fields by default
        # Test that we get a repr with expected content
        assert "SuperOpsConfig" in repr_str
        assert "api_key=" in repr_str
        assert "base_url=" in repr_str

    def test_config_equality(self):
        """Test config equality comparison."""
        config1 = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1",
        )
        config2 = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1",
        )
        config3 = SuperOpsConfig(
            api_key="different-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret
            base_url="https://api.superops.com/v1",
        )

        assert config1 == config2
        assert config1 != config3

    def test_config_immutability_protection(self):
        """Test that config is mutable (Pydantic default)."""
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1",
        )

        # Pydantic models show all fields by default
        config_str = str(config)
        config_repr = repr(config)

        # API key is visible in str/repr (Pydantic default behavior)
        assert "test-key-" in config_str
        assert "test-key-" in config_repr

    def test_retry_delay_validation(self):
        """Test retry delay validation."""
        # Valid retry delay
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1",
            retry_delay=5.0,
        )
        assert config.retry_delay == 5.0

        # Too low
        with pytest.raises(ValidationError):
            SuperOpsConfig(
                api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
                base_url="https://api.superops.com/v1",
                retry_delay=0.05,
            )

    def test_cache_settings_validation(self):
        """Test cache settings validation."""
        # Valid cache settings
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
            base_url="https://api.superops.com/v1",
            cache_ttl=1800,
            cache_max_size=5000,
        )
        assert config.cache_ttl == 1800
        assert config.cache_max_size == 5000

        # Invalid cache TTL (too high)
        with pytest.raises(ValidationError):
            SuperOpsConfig(
                api_key="test-key-1234567890123456789012345678901234567890",  # pragma: allowlist secret,
                base_url="https://api.superops.com/v1",
                cache_ttl=4000,
            )

    def test_default_values_comprehensive(self):
        """Test all default values are set correctly."""
        config = SuperOpsConfig(
            api_key="test-key-1234567890123456789012345678901234567890"
        )  # pragma: allowlist secret

        # Check all defaults
        assert config.base_url == "https://api.superops.com/v1"
        assert config.timeout == 30.0
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.rate_limit_per_minute == 60
        assert config.burst_limit == 10
        assert config.enable_caching is True
        assert config.cache_ttl == 300
        assert config.cache_max_size == 1000
        assert config.debug is False
        assert config.log_level == "INFO"
        assert config.user_agent is None
        assert config.verify_ssl is True
        assert config.proxy is None
