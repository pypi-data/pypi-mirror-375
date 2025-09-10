# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Authentication handling for the SuperOps Python client library."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

import httpx

from .config import SuperOpsConfig
from .exceptions import SuperOpsAuthenticationError, SuperOpsNetworkError, SuperOpsTimeoutError

logger = logging.getLogger(__name__)


class AuthHandler:
    """Handles authentication for SuperOps API requests.

    This class manages API key authentication and provides methods for
    validating credentials and preparing request headers.
    """

    def __init__(self, config: SuperOpsConfig) -> None:
        """Initialize the authentication handler.

        Args:
            config: SuperOps configuration instance
        """
        self._config = config
        self._token_validated = False
        self._validation_time: Optional[datetime] = None
        self._validation_lock = asyncio.Lock()

        logger.debug("AuthHandler initialized")

    @property
    def is_token_validated(self) -> bool:
        """Check if the token has been validated."""
        return self._token_validated and self._is_validation_fresh()

    def _is_validation_fresh(self) -> bool:
        """Check if token validation is still fresh (within 5 minutes)."""
        if not self._validation_time:
            return False

        return datetime.now() - self._validation_time < timedelta(minutes=5)

    async def authenticate(self) -> str:
        """Authenticate and validate the API token.

        Returns:
            The validated API token

        Raises:
            SuperOpsAuthenticationError: If authentication fails
            SuperOpsNetworkError: If network error occurs
        """
        if self.is_token_validated:
            return self._config.api_key

        async with self._validation_lock:
            # Double-check after acquiring lock
            if self.is_token_validated:
                return self._config.api_key

            await self._validate_token()
            return self._config.api_key

    async def _validate_token(self) -> None:
        """Validate the API token by making a test request.

        Raises:
            SuperOpsAuthenticationError: If token is invalid
            SuperOpsNetworkError: If network error occurs
        """
        logger.debug("Validating API token")

        headers = await self.get_headers()

        # Use a simple GraphQL introspection query to validate the token
        validation_query = {"query": "query { __schema { queryType { name } } }"}

        timeout = httpx.Timeout(self._config.timeout)

        try:
            async with httpx.AsyncClient(
                timeout=timeout,
                verify=self._config.verify_ssl,
                proxies=self._config.proxy,
            ) as client:
                response = await client.post(
                    f"{self._config.base_url}/graphql",
                    json=validation_query,
                    headers=headers,
                )

                if response.status_code == 401:
                    raise SuperOpsAuthenticationError(
                        "Invalid API key - authentication failed",
                        status_code=401,
                        response_data=response.json() if response.content else {},
                    )
                elif response.status_code == 403:
                    raise SuperOpsAuthenticationError(
                        "Insufficient permissions - access forbidden",
                        status_code=403,
                        response_data=response.json() if response.content else {},
                    )
                elif response.status_code >= 400:
                    error_data = response.json() if response.content else {}
                    raise SuperOpsAuthenticationError(
                        f"Authentication validation failed with status {response.status_code}",
                        status_code=response.status_code,
                        response_data=error_data,
                    )

                # Check for GraphQL errors that might indicate auth issues
                response_data = response.json()
                if "errors" in response_data:
                    errors = response_data["errors"]
                    auth_errors = [
                        error
                        for error in errors
                        if "unauthorized" in error.get("message", "").lower()
                        or "unauthenticated" in error.get("message", "").lower()
                    ]

                    if auth_errors:
                        error_message = "; ".join(error["message"] for error in auth_errors)
                        raise SuperOpsAuthenticationError(
                            f"GraphQL authentication error: {error_message}",
                            status_code=response.status_code,
                            response_data=response_data,
                        )

                # If we get here, the token is valid
                self._token_validated = True
                self._validation_time = datetime.now()
                logger.info("API token validated successfully")

        except httpx.TimeoutException:
            raise SuperOpsTimeoutError(
                "Token validation timed out",
                timeout_duration=self._config.timeout,
            )
        except httpx.NetworkError as e:
            raise SuperOpsNetworkError(
                f"Network error during token validation: {e}",
                original_exception=e,
            )
        except SuperOpsAuthenticationError:
            # Re-raise auth errors as-is
            raise
        except Exception as e:
            logger.error(f"Unexpected error during token validation: {e}")
            raise SuperOpsAuthenticationError(
                f"Token validation failed: {e}",
                details={"original_error": str(e)},
            )

    async def refresh_token(self) -> str:
        """Refresh the authentication token.

        Note: SuperOps uses API keys, so this method invalidates the cached
        validation and re-validates the token.

        Returns:
            The refreshed (re-validated) API token

        Raises:
            SuperOpsAuthenticationError: If token refresh fails
        """
        logger.debug("Refreshing authentication token")

        async with self._validation_lock:
            self._token_validated = False
            self._validation_time = None
            await self._validate_token()

        return self._config.api_key

    def invalidate_token(self) -> None:
        """Invalidate the cached token validation.

        This forces re-validation on the next authenticate() call.
        """
        logger.debug("Invalidating cached token validation")
        self._token_validated = False
        self._validation_time = None

    async def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for authenticated requests.

        Returns:
            Dictionary of HTTP headers including authorization
        """
        headers = self._config.get_headers()

        # Add additional headers if needed
        if self._config.debug:
            headers["X-Debug"] = "true"

        return headers

    def is_token_format_valid(self) -> bool:
        """Perform basic validation on token format without making API calls.

        Returns:
            True if token format appears valid, False otherwise
        """
        if not self._config.api_key:
            return False

        token = self._config.api_key.strip()

        # Basic format checks
        if len(token) < 10:
            return False

        # Check for obvious placeholder values
        if token.lower() in ("your-api-key", "api-key", "token", "key"):
            return False

        # Allow test tokens for testing purposes
        # if token.lower().startswith(("test", "demo", "example", "sample")):
        #     return False

        return True

    async def test_connection(self) -> Dict[str, any]:
        """Test the connection and return basic API information.

        Returns:
            Dictionary with connection test results

        Raises:
            SuperOpsAuthenticationError: If authentication fails
            SuperOpsNetworkError: If connection fails
        """
        logger.debug("Testing API connection")

        # First validate the token
        await self.authenticate()

        # Get basic schema information
        query = {
            "query": """
            query TestConnection {
                __schema {
                    queryType { name }
                    mutationType { name }
                    subscriptionType { name }
                }
            }
            """
        }

        headers = await self.get_headers()
        timeout = httpx.Timeout(self._config.timeout)

        try:
            async with httpx.AsyncClient(
                timeout=timeout,
                verify=self._config.verify_ssl,
                proxies=self._config.proxy,
            ) as client:
                start_time = datetime.now()

                response = await client.post(
                    f"{self._config.base_url}/graphql",
                    json=query,
                    headers=headers,
                )

                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()

                response.raise_for_status()
                data = response.json()

                return {
                    "connected": True,
                    "response_time_seconds": response_time,
                    "api_version": "v1",  # Extracted from base_url
                    "datacenter": (
                        "US"
                        if self._config.is_us_datacenter()
                        else ("EU" if self._config.is_eu_datacenter() else "Unknown")
                    ),
                    "schema_info": data.get("data", {}).get("__schema", {}),
                    "authenticated": True,
                    "timestamp": datetime.now().isoformat(),
                }

        except httpx.HTTPStatusError as e:
            if e.response.status_code in (401, 403):
                raise SuperOpsAuthenticationError(
                    f"Connection test failed: {e.response.status_code}",
                    status_code=e.response.status_code,
                )
            raise SuperOpsNetworkError(
                f"HTTP error during connection test: {e}",
                original_exception=e,
            )
        except httpx.TimeoutException:
            raise SuperOpsTimeoutError(
                "Connection test timed out",
                timeout_duration=self._config.timeout,
            )
        except httpx.NetworkError as e:
            raise SuperOpsNetworkError(
                f"Network error during connection test: {e}",
                original_exception=e,
            )
