# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Custom exception classes for the SuperOps Python client library."""

from typing import Any, Dict, Optional


class SuperOpsError(Exception):
    """Base exception for all SuperOps errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the SuperOps error.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class SuperOpsAPIError(SuperOpsError):
    """API-specific errors from SuperOps GraphQL endpoint."""

    def __init__(
        self,
        message: str,
        status_code: int,
        response_data: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the API error.

        Args:
            message: Error message
            status_code: HTTP status code from the response
            response_data: Raw response data from the API
            details: Additional error details
        """
        super().__init__(message, details)
        self.status_code = status_code
        self.response_data = response_data or {}


class SuperOpsAuthenticationError(SuperOpsAPIError):
    """Authentication and authorization errors."""

    def __init__(
        self,
        message: str = "Authentication failed",
        status_code: int = 401,
        response_data: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the authentication error.

        Args:
            message: Error message
            status_code: HTTP status code (typically 401 or 403)
            response_data: Raw response data from the API
            details: Additional error details
        """
        super().__init__(message, status_code, response_data, details)


class SuperOpsRateLimitError(SuperOpsAPIError):
    """Rate limiting errors with retry information."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int = 60,
        status_code: int = 429,
        response_data: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the rate limit error.

        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
            status_code: HTTP status code (typically 429)
            response_data: Raw response data from the API
            details: Additional error details
        """
        super().__init__(message, status_code, response_data, details)
        self.retry_after = retry_after


class SuperOpsNetworkError(SuperOpsError):
    """Network connectivity and timeout errors."""

    def __init__(
        self,
        message: str = "Network error occurred",
        original_exception: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the network error.

        Args:
            message: Error message
            original_exception: The underlying network exception
            details: Additional error details
        """
        super().__init__(message, details)
        self.original_exception = original_exception


class SuperOpsValidationError(SuperOpsError):
    """Data validation and parsing errors."""

    def __init__(
        self,
        message: str = "Validation failed",
        field_errors: Optional[Dict[str, str]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the validation error.

        Args:
            message: Error message
            field_errors: Field-specific validation errors
            details: Additional error details
        """
        super().__init__(message, details)
        self.field_errors = field_errors or {}


class SuperOpsConfigurationError(SuperOpsError):
    """Configuration and setup errors."""

    def __init__(
        self,
        message: str = "Configuration error",
        config_field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the configuration error.

        Args:
            message: Error message
            config_field: The configuration field that caused the error
            details: Additional error details
        """
        super().__init__(message, details)
        self.config_field = config_field


class SuperOpsTimeoutError(SuperOpsNetworkError):
    """Request timeout errors."""

    def __init__(
        self,
        message: str = "Request timed out",
        timeout_duration: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the timeout error.

        Args:
            message: Error message
            timeout_duration: The timeout duration that was exceeded
            details: Additional error details
        """
        super().__init__(message, None, details)
        self.timeout_duration = timeout_duration


class SuperOpsResourceNotFoundError(SuperOpsAPIError):
    """Resource not found errors."""

    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        status_code: int = 404,
        response_data: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the resource not found error.

        Args:
            message: Error message
            resource_type: Type of resource that was not found
            resource_id: ID of the resource that was not found
            status_code: HTTP status code (typically 404)
            response_data: Raw response data from the API
            details: Additional error details
        """
        super().__init__(message, status_code, response_data, details)
        self.resource_type = resource_type
        self.resource_id = resource_id
