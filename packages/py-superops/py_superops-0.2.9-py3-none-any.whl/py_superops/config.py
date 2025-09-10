# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Configuration management for the SuperOps Python client library."""

from pathlib import Path
from typing import Any, Dict, Optional, Union
from urllib.parse import urlparse

from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings

from .exceptions import SuperOpsConfigurationError


class SuperOpsConfig(BaseSettings):
    """Configuration settings for the SuperOps client.

    This class uses Pydantic settings to manage configuration from multiple sources:
    - Environment variables (prefixed with SUPEROPS_)
    - Configuration files (YAML/JSON)
    - Direct instantiation

    Configuration hierarchy (highest to lowest priority):
    1. Direct instantiation parameters
    2. Environment variables
    3. Configuration file
    4. Default values
    """

    # API Configuration
    api_key: str = Field(..., description="SuperOps API key")
    base_url: str = Field(
        default="https://api.superops.com/v1", description="Base URL for the SuperOps API"
    )

    # Request Configuration
    timeout: float = Field(default=30.0, ge=0.1, le=300.0, description="Request timeout in seconds")
    max_retries: int = Field(
        default=3, ge=0, le=10, description="Maximum number of request retries"
    )
    retry_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=60.0,
        description="Initial retry delay in seconds (exponential backoff)",
    )

    # Rate Limiting
    rate_limit_per_minute: int = Field(
        default=60, ge=1, le=1000, description="Maximum requests per minute"
    )
    burst_limit: int = Field(default=10, ge=1, le=100, description="Maximum burst requests")

    # Caching
    enable_caching: bool = Field(default=True, description="Enable response caching")
    cache_ttl: int = Field(default=300, ge=0, le=3600, description="Cache TTL in seconds")
    cache_max_size: int = Field(
        default=1000, ge=10, le=10000, description="Maximum number of cached responses"
    )

    # Debugging and Logging
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format",
    )

    # Advanced Configuration
    user_agent: Optional[str] = Field(default=None, description="Custom User-Agent header")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    proxy: Optional[str] = Field(default=None, description="HTTP proxy URL")

    model_config = ConfigDict(
        env_prefix="SUPEROPS_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_assignment=True,
    )

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate the base URL format."""
        if not v:
            raise ValueError("Base URL cannot be empty")

        try:
            parsed = urlparse(v)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Base URL must include scheme and domain")

            if parsed.scheme not in ("http", "https"):
                raise ValueError("Base URL scheme must be http or https")

            # Remove trailing slash for consistency
            return v.rstrip("/")

        except Exception as e:
            raise ValueError(f"Invalid base URL format: {e}")

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate the API key format."""
        if not v or not v.strip():
            raise ValueError("API key cannot be empty")

        # Basic API key format validation
        api_key = v.strip()
        if len(api_key) < 10:
            raise ValueError("API key appears to be too short")

        return api_key

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate the log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        level = v.upper()
        if level not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return level

    @field_validator("proxy")
    @classmethod
    def validate_proxy(cls, v: Optional[str]) -> Optional[str]:
        """Validate proxy URL format if provided."""
        if v is None:
            return v

        try:
            parsed = urlparse(v)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Proxy URL must include scheme and host")
            return v
        except Exception as e:
            raise ValueError(f"Invalid proxy URL format: {e}")

    def get_headers(self) -> Dict[str, str]:
        """Get default HTTP headers for requests."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if self.user_agent:
            headers["User-Agent"] = self.user_agent

        return headers

    def is_us_datacenter(self) -> bool:
        """Check if using US datacenter."""
        return "us" in self.base_url.lower() or "api.superops.com" in self.base_url.lower()

    def is_eu_datacenter(self) -> bool:
        """Check if using EU datacenter."""
        return "eu" in self.base_url.lower()

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "SuperOpsConfig":
        """Load configuration from a file.

        Args:
            file_path: Path to the configuration file (JSON or YAML)

        Returns:
            SuperOpsConfig instance

        Raises:
            SuperOpsConfigurationError: If file cannot be loaded or parsed
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise SuperOpsConfigurationError(f"Configuration file not found: {file_path}")

            content = path.read_text(encoding="utf-8")

            if path.suffix.lower() in (".yml", ".yaml"):
                try:
                    import yaml

                    data = yaml.safe_load(content)
                except ImportError:
                    raise SuperOpsConfigurationError(
                        "PyYAML is required to load YAML configuration files. "
                        "Install with: pip install PyYAML"
                    )
            elif path.suffix.lower() == ".json":
                import json

                data = json.loads(content)
            else:
                raise SuperOpsConfigurationError(
                    f"Unsupported configuration file format: {path.suffix}. "
                    "Supported formats: .json, .yml, .yaml"
                )

            return cls(**data)

        except Exception as e:
            if isinstance(e, SuperOpsConfigurationError):
                raise
            raise SuperOpsConfigurationError(f"Failed to load configuration from {file_path}: {e}")

    @classmethod
    def from_env(cls) -> "SuperOpsConfig":
        """Load configuration from environment variables.

        Returns:
            SuperOpsConfig instance

        Raises:
            SuperOpsConfigurationError: If required environment variables are missing
        """
        try:
            return cls()
        except Exception as e:
            raise SuperOpsConfigurationError(f"Failed to load configuration from environment: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding sensitive data)."""
        data = self.dict()
        # Mask the API key for security
        if "api_key" in data:
            data["api_key"] = f"{data['api_key'][:8]}{'*' * (len(data['api_key']) - 8)}"
        return data

    def validate_config(self) -> None:
        """Validate the current configuration.

        Raises:
            SuperOpsConfigurationError: If configuration is invalid
        """
        errors = []

        # Check required fields
        if not self.api_key:
            errors.append("API key is required")

        if not self.base_url:
            errors.append("Base URL is required")

        # Check rate limiting configuration
        if self.burst_limit > self.rate_limit_per_minute:
            errors.append("Burst limit cannot exceed rate limit per minute")

        # Check cache configuration
        if self.enable_caching and self.cache_ttl <= 0:
            errors.append("Cache TTL must be positive when caching is enabled")

        if errors:
            raise SuperOpsConfigurationError(
                f"Configuration validation failed: {'; '.join(errors)}"
            )


def get_default_config() -> SuperOpsConfig:
    """Get default configuration from environment variables.

    Returns:
        SuperOpsConfig instance with default settings

    Raises:
        SuperOpsConfigurationError: If required configuration is missing
    """
    return SuperOpsConfig.from_env()


def load_config(config_file: Optional[Union[str, Path]] = None, **overrides: Any) -> SuperOpsConfig:
    """Load configuration with optional file and overrides.

    Args:
        config_file: Optional path to configuration file
        **overrides: Configuration overrides

    Returns:
        SuperOpsConfig instance

    Raises:
        SuperOpsConfigurationError: If configuration cannot be loaded
    """
    if config_file:
        config = SuperOpsConfig.from_file(config_file)
        if overrides:
            # Apply overrides by creating a new instance
            config_data = config.dict()
            config_data.update(overrides)
            config = SuperOpsConfig(**config_data)
    else:
        config = SuperOpsConfig(**overrides) if overrides else SuperOpsConfig.from_env()

    config.validate_config()
    return config
