# # Copyright (c) {{ year }} {{ author }}
# # Licensed under the MIT License.
# # See LICENSE file in the project root for full license information.

# # Copyright (c) 2025 Aaron Sachs
# # Licensed under the MIT License.
# # See LICENSE file in the project root for full license information.

# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Main SuperOps client class for interacting with the SuperOps GraphQL API."""

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

import httpx

from .auth import AuthHandler
from .config import SuperOpsConfig
from .exceptions import (
    SuperOpsAPIError,
    SuperOpsAuthenticationError,
    SuperOpsNetworkError,
    SuperOpsRateLimitError,
    SuperOpsTimeoutError,
    SuperOpsValidationError,
)

if TYPE_CHECKING:
    from .managers import (
        AssetManager,
        ClientManager,
        CommentsManager,
        ContactManager,
        ContractsManager,
        KnowledgeBaseManager,
        ProjectsManager,
        ScriptsManager,
        SiteManager,
        TasksManager,
        TicketManager,
        TimeEntriesManager,
        UsersManager,
        WebhooksManager,
    )

logger = logging.getLogger(__name__)


class SuperOpsClient:
    """Main client class for interacting with the SuperOps GraphQL API.

    This client provides a high-level interface for making GraphQL requests to
    the SuperOps API with built-in authentication, error handling, and retry logic.

    Example:
        ```python
        from py_superops import SuperOpsClient, SuperOpsConfig

        # Create configuration
        config = SuperOpsConfig(
            api_key="your-api-key",  # pragma: allowlist secret
            base_url="https://api.superops.com/v1"
        )

        # Create client
        client = SuperOpsClient(config)

        # Test connection
        connection_info = await client.test_connection()
        print(f"Connected: {connection_info['connected']}")
        ```
    """

    def __init__(
        self,
        config: SuperOpsConfig,
        auth_handler: Optional[AuthHandler] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        """Initialize the SuperOps client.

        Args:
            config: SuperOps configuration instance
            auth_handler: Optional custom authentication handler
            http_client: Optional custom HTTP client
        """
        self._config = config
        self._auth_handler = auth_handler or AuthHandler(config)
        self._http_client = http_client
        self._client_provided = http_client is not None

        # Initialize resource managers (lazy loading)
        self._clients_manager = None
        self._tickets_manager = None
        self._tasks_manager = None
        self._assets_manager = None
        self._sites_manager = None
        self._contacts_manager = None
        self._contracts_manager = None
        self._knowledge_base_manager = None
        self._projects_manager = None
        self._time_entries_manager = None

        # Setup logging
        logging.basicConfig(level=getattr(logging, config.log_level), format=config.log_format)

        logger.debug(f"SuperOpsClient initialized with base URL: {config.base_url}")

    @property
    def config(self) -> SuperOpsConfig:
        """Get the client configuration."""
        return self._config

    @property
    def auth_handler(self) -> AuthHandler:
        """Get the authentication handler."""
        return self._auth_handler

    @property
    def clients(self) -> "ClientManager":
        """Get the client manager for client operations."""
        if self._clients_manager is None:
            from .managers import ClientManager

            self._clients_manager = ClientManager(self)
        return self._clients_manager

    @property
    def tickets(self) -> "TicketManager":
        """Get the ticket manager for ticket operations."""
        if self._tickets_manager is None:
            from .managers import TicketManager

            self._tickets_manager = TicketManager(self)
        return self._tickets_manager

    @property
    def tasks(self) -> "TasksManager":
        """Get the tasks manager for task operations."""
        if self._tasks_manager is None:
            from .managers import TasksManager

            self._tasks_manager = TasksManager(self)
        return self._tasks_manager

    @property
    def assets(self) -> "AssetManager":
        """Get the asset manager for asset operations."""
        if self._assets_manager is None:
            from .managers import AssetManager

            self._assets_manager = AssetManager(self)
        return self._assets_manager

    @property
    def sites(self) -> "SiteManager":
        """Get the site manager for site operations."""
        if self._sites_manager is None:
            from .managers import SiteManager

            self._sites_manager = SiteManager(self)
        return self._sites_manager

    @property
    def contacts(self) -> "ContactManager":
        """Get the contact manager for contact operations."""
        if self._contacts_manager is None:
            from .managers import ContactManager

            self._contacts_manager = ContactManager(self)
        return self._contacts_manager

    @property
    def contracts(self) -> "ContractsManager":
        """Get the contracts manager for contract operations."""
        if self._contracts_manager is None:
            from .managers import ContractsManager

            self._contracts_manager = ContractsManager(self)
        return self._contracts_manager

    @property
    def knowledge_base(self) -> "KnowledgeBaseManager":
        """Get the knowledge base manager for articles and collections."""
        if self._knowledge_base_manager is None:
            from .managers import KnowledgeBaseManager

            self._knowledge_base_manager = KnowledgeBaseManager(self)
        return self._knowledge_base_manager

    @property
    def projects(self) -> "ProjectsManager":
        """Get the projects manager for project operations."""
        if self._projects_manager is None:
            from .managers import ProjectsManager

            self._projects_manager = ProjectsManager(self)
        return self._projects_manager

    @property
    def time_entries(self) -> "TimeEntriesManager":
        """Get the time entries manager for time tracking operations."""
        if self._time_entries_manager is None:
            from .managers import TimeEntriesManager

            self._time_entries_manager = TimeEntriesManager(self)
        return self._time_entries_manager

    @property
    def comments(self) -> "CommentsManager":
        """Get the comments manager for comment operations."""
        if not hasattr(self, "_comments_manager") or self._comments_manager is None:
            from .managers import CommentsManager

            self._comments_manager = CommentsManager(self)
        return self._comments_manager

    @property
    def scripts(self) -> "ScriptsManager":
        """Get the scripts manager for script operations."""
        if not hasattr(self, "_scripts_manager") or self._scripts_manager is None:
            from .managers import ScriptsManager

            self._scripts_manager = ScriptsManager(self)
        return self._scripts_manager

    @property
    def users(self) -> "UsersManager":
        """Get the users manager for user operations."""
        if not hasattr(self, "_users_manager") or self._users_manager is None:
            from .managers import UsersManager

            self._users_manager = UsersManager(self)
        return self._users_manager

    @property
    def webhooks(self) -> "WebhooksManager":
        """Get the webhooks manager for webhook operations."""
        if not hasattr(self, "_webhooks_manager") or self._webhooks_manager is None:
            from .managers import WebhooksManager

            self._webhooks_manager = WebhooksManager(self)
        return self._webhooks_manager

    async def __aenter__(self) -> "SuperOpsClient":
        """Async context manager entry."""
        if not self._client_provided and not self._http_client:
            client_kwargs = {
                "timeout": httpx.Timeout(self._config.timeout),
                "verify": self._config.verify_ssl,
                "limits": httpx.Limits(
                    max_keepalive_connections=5,
                    max_connections=10,
                ),
            }

            if self._config.proxy:
                client_kwargs["proxies"] = self._config.proxy

            self._http_client = httpx.AsyncClient(**client_kwargs)
            logger.debug("HTTP client created")

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if not self._client_provided and self._http_client:
            await self._http_client.aclose()
            self._http_client = None
            logger.debug("HTTP client closed")

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client instance."""
        if not self._http_client:
            client_kwargs = {
                "timeout": httpx.Timeout(self._config.timeout),
                "verify": self._config.verify_ssl,
                "limits": httpx.Limits(
                    max_keepalive_connections=5,
                    max_connections=10,
                ),
            }

            if self._config.proxy:
                client_kwargs["proxies"] = self._config.proxy

            self._http_client = httpx.AsyncClient(**client_kwargs)

        return self._http_client

    async def execute_query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a GraphQL query.

        Args:
            query: GraphQL query string
            variables: Optional query variables
            operation_name: Optional operation name for the query

        Returns:
            GraphQL response data

        Raises:
            SuperOpsAuthenticationError: If authentication fails
            SuperOpsAPIError: If API returns an error
            SuperOpsNetworkError: If network error occurs
            SuperOpsValidationError: If request validation fails
        """
        if not query or not query.strip():
            raise SuperOpsValidationError("Query cannot be empty")

        # Validate variables type
        if variables is not None and not isinstance(variables, dict):
            raise SuperOpsValidationError("Variables must be a dictionary")

        # Prepare the GraphQL request
        request_data = {"query": query.strip()}

        if variables:
            request_data["variables"] = variables

        if operation_name:
            request_data["operationName"] = operation_name

        logger.debug(f"Executing GraphQL query: {operation_name or 'unnamed'}")

        return await self._make_request(request_data)

    async def execute_mutation(
        self,
        mutation: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a GraphQL mutation.

        Args:
            mutation: GraphQL mutation string
            variables: Optional mutation variables
            operation_name: Optional operation name for the mutation

        Returns:
            GraphQL response data

        Raises:
            SuperOpsAuthenticationError: If authentication fails
            SuperOpsAPIError: If API returns an error
            SuperOpsNetworkError: If network error occurs
            SuperOpsValidationError: If request validation fails
        """
        if not mutation or not mutation.strip():
            raise SuperOpsValidationError("Mutation cannot be empty")

        # Validate variables type
        if variables is not None and not isinstance(variables, dict):
            raise SuperOpsValidationError("Variables must be a dictionary")

        # Prepare the GraphQL request
        request_data = {"query": mutation.strip()}

        if variables:
            request_data["variables"] = variables

        if operation_name:
            request_data["operationName"] = operation_name

        logger.debug(f"Executing GraphQL mutation: {operation_name or 'unnamed'}")

        return await self._make_request(request_data)

    async def _make_request(
        self,
        request_data: Dict[str, Any],
        retry_count: int = 0,
    ) -> Dict[str, Any]:
        """Make an HTTP request to the GraphQL endpoint with retry logic.

        Args:
            request_data: GraphQL request payload
            retry_count: Current retry attempt count

        Returns:
            GraphQL response data

        Raises:
            SuperOpsAuthenticationError: If authentication fails
            SuperOpsAPIError: If API returns an error
            SuperOpsNetworkError: If network error occurs
            SuperOpsRateLimitError: If rate limit is exceeded
        """
        # Get authentication headers
        headers = await self._auth_handler.get_headers()

        # Get HTTP client
        http_client = await self._get_http_client()

        try:
            response = await http_client.post(
                f"{self._config.base_url}/graphql",
                json=request_data,
                headers=headers,
            )

            return await self._handle_response(response, request_data, retry_count)

        except httpx.TimeoutException:
            if retry_count < self._config.max_retries:
                logger.warning(
                    f"Request timeout, retrying ({retry_count + 1}/{self._config.max_retries})"
                )
                await asyncio.sleep(self._config.retry_delay * (2**retry_count))
                return await self._make_request(request_data, retry_count + 1)

            raise SuperOpsTimeoutError(
                f"Request timed out after {self._config.max_retries} retries",
                timeout_duration=self._config.timeout,
            )

        except httpx.NetworkError as e:
            if retry_count < self._config.max_retries:
                logger.warning(
                    f"Network error, retrying ({retry_count + 1}/{self._config.max_retries}): {e}"
                )
                await asyncio.sleep(self._config.retry_delay * (2**retry_count))
                return await self._make_request(request_data, retry_count + 1)

            raise SuperOpsNetworkError(
                f"Network error after {self._config.max_retries} retries: {e}",
                original_exception=e,
            )

    async def _handle_response(
        self,
        response: httpx.Response,
        request_data: Dict[str, Any],
        retry_count: int,
    ) -> Dict[str, Any]:
        """Handle and parse GraphQL response.

        Args:
            response: HTTP response object
            request_data: Original request data for retries
            retry_count: Current retry count

        Returns:
            Parsed GraphQL response data

        Raises:
            SuperOpsAuthenticationError: If authentication fails
            SuperOpsAPIError: If API returns an error
            SuperOpsRateLimitError: If rate limit is exceeded
        """
        # Handle rate limiting
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", "60"))

            if retry_count < self._config.max_retries:
                logger.warning(f"Rate limit hit, retrying after {retry_after} seconds")
                await asyncio.sleep(retry_after)
                return await self._make_request(request_data, retry_count + 1)

            raise SuperOpsRateLimitError(
                "Rate limit exceeded",
                retry_after=retry_after,
                status_code=response.status_code,
                response_data=response.json() if response.content else {},
            )

        # Handle authentication errors
        if response.status_code in (401, 403):
            # Invalidate cached token and try once more
            if retry_count == 0:
                logger.warning("Authentication error, invalidating token and retrying")
                self._auth_handler.invalidate_token()
                return await self._make_request(request_data, retry_count + 1)

            error_data = response.json() if response.content else {}
            raise SuperOpsAuthenticationError(
                f"Authentication failed: {response.status_code}",
                status_code=response.status_code,
                response_data=error_data,
            )

        # Handle server errors with retry
        if response.status_code >= 500:
            error_data = response.json() if response.content else {}

            # Retry on 5xx errors if we haven't exceeded retry limit
            if retry_count < self._config.max_retries:
                retry_delay = self._config.retry_delay * (2**retry_count)  # Exponential backoff
                logger.warning(
                    f"Server error {response.status_code}, retrying after {retry_delay}s "
                    f"(attempt {retry_count + 1}/{self._config.max_retries})"
                )
                await asyncio.sleep(retry_delay)
                return await self._make_request(request_data, retry_count + 1)

            raise SuperOpsAPIError(
                f"API request failed with status {response.status_code}",
                status_code=response.status_code,
                response_data=error_data,
            )

        # Handle other client errors (4xx) without retry
        if response.status_code >= 400:
            error_data = response.json() if response.content else {}
            raise SuperOpsAPIError(
                f"API request failed with status {response.status_code}",
                status_code=response.status_code,
                response_data=error_data,
            )

        # Parse JSON response
        try:
            response_data = response.json()
        except Exception as e:
            raise SuperOpsAPIError(
                f"Failed to parse JSON response: {e}",
                status_code=response.status_code,
                response_data={"raw_content": str(response.content[:1000])},
            )

        # Handle GraphQL errors
        if "errors" in response_data:
            errors = response_data["errors"]
            error_messages = [error.get("message", "Unknown error") for error in errors]

            # Check for authentication-related GraphQL errors
            auth_keywords = ["unauthorized", "unauthenticated", "invalid token", "authentication"]
            if any(
                keyword in message.lower()
                for message in error_messages
                for keyword in auth_keywords
            ):
                raise SuperOpsAuthenticationError(
                    f"GraphQL authentication error: {'; '.join(error_messages)}",
                    response_data=response_data,
                )

            raise SuperOpsAPIError(
                f"GraphQL errors: {'; '.join(error_messages)}",
                status_code=response.status_code,
                response_data=response_data,
            )

        # Log successful response
        if self._config.debug:
            logger.debug(f"GraphQL request successful: {response.status_code}")

        return response_data

    async def test_connection(self) -> Dict[str, Any]:
        """Test the connection to the SuperOps API.

        Returns:
            Dictionary with connection test results

        Raises:
            SuperOpsAuthenticationError: If authentication fails
            SuperOpsNetworkError: If connection fails
        """
        return await self._auth_handler.test_connection()

    async def get_schema(self) -> Dict[str, Any]:
        """Get the GraphQL schema from the API.

        Returns:
            GraphQL schema information

        Raises:
            SuperOpsAPIError: If schema retrieval fails
        """
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                queryType { name }
                mutationType { name }
                subscriptionType { name }
                types {
                    ...FullType
                }
                directives {
                    name
                    description
                    locations
                    args {
                        ...InputValue
                    }
                }
            }
        }

        fragment FullType on __Type {
            kind
            name
            description
            fields(includeDeprecated: true) {
                name
                description
                args {
                    ...InputValue
                }
                type {
                    ...TypeRef
                }
                isDeprecated
                deprecationReason
            }
            inputFields {
                ...InputValue
            }
            interfaces {
                ...TypeRef
            }
            enumValues(includeDeprecated: true) {
                name
                description
                isDeprecated
                deprecationReason
            }
            possibleTypes {
                ...TypeRef
            }
        }

        fragment InputValue on __InputValue {
            name
            description
            type { ...TypeRef }
            defaultValue
        }

        fragment TypeRef on __Type {
            kind
            name
            ofType {
                kind
                name
                ofType {
                    kind
                    name
                    ofType {
                        kind
                        name
                        ofType {
                            kind
                            name
                            ofType {
                                kind
                                name
                                ofType {
                                    kind
                                    name
                                    ofType {
                                        kind
                                        name
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """

        response = await self.execute_query(
            introspection_query, operation_name="IntrospectionQuery"
        )
        return response.get("data", {}).get("__schema", {})

    async def close(self) -> None:
        """Close the HTTP client and clean up resources."""
        if not self._client_provided and self._http_client:
            await self._http_client.aclose()
            self._http_client = None
            logger.debug("HTTP client closed")
