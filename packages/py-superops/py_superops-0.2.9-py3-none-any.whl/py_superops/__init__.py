# # Copyright (c) {{ year }} {{ author }}
# # Licensed under the MIT License.
# # See LICENSE file in the project root for full license information.

# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Python client library for the SuperOps GraphQL API.

This package provides a comprehensive Python SDK for interacting with the SuperOps
GraphQL API, featuring async/await support, comprehensive error handling, rate limiting,
and type safety.

Example:
    ```python
    import asyncio
    from py_superops import SuperOpsClient, SuperOpsConfig
    from py_superops.graphql import TicketStatus, TicketPriority

    async def main():
        # Create configuration from environment variables
        config = SuperOpsConfig.from_env()

        # Create and use the client
        async with SuperOpsClient(config) as client:
            # Test connection
            connection_info = await client.test_connection()
            print(f"Connected: {connection_info['connected']}")

            # Use high-level managers for intuitive operations
            # Client management
            active_clients = await client.clients.get_active_clients(page_size=10)
            for client_data in active_clients['items']:
                print(f"Client: {client_data.name} ({client_data.email})")

            # Ticket workflow management
            overdue_tickets = await client.tickets.get_overdue_tickets()
            for ticket in overdue_tickets['items']:
                print(f"Overdue ticket: {ticket.title}")
                # Escalate overdue tickets
                await client.tickets.change_priority(
                    ticket.id,
                    TicketPriority.HIGH
                )

            # Asset tracking
            expiring_warranties = await client.assets.get_warranty_expiring_soon(
                days_threshold=30
            )
            print(f"Found {len(expiring_warranties['items'])} assets with expiring warranties")

            # Knowledge base search
            search_results = await client.knowledge_base.search_all(
                "password reset",
                published_only=True
            )
            print(f"Found {len(search_results['articles']['items'])} relevant articles")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

Key Features:
    - Async/await support for high-performance applications
    - Type-safe GraphQL query builders with fragments and field selection
    - Pre-built common queries for all SuperOps resources
    - Comprehensive error handling with custom exception hierarchy
    - Built-in rate limiting and retry logic
    - Type safety with full type hint support
    - Configuration management with environment variable support
    - Authentication handling with token validation
    - Response caching for improved performance
    - Connection pooling and resource management
    - GraphQL schema introspection and validation
"""

from typing import Any, Optional

__version__ = "0.2.9"
__author__ = "SuperOps Team"
__email__ = "support@superops.com"
__license__ = "MIT"

from .auth import AuthHandler

# Core components
from .client import SuperOpsClient
from .config import SuperOpsConfig, get_default_config, load_config

# Exceptions
from .exceptions import (
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

# Resource managers (optional import to avoid circular dependencies)
try:
    from .managers import (  # Base manager; Domain-specific managers
        AssetManager,
        AttachmentsManager,
        ClientManager,
        CommentsManager,
        ContactManager,
        ContractsManager,
        KnowledgeBaseArticleManager,
        KnowledgeBaseCollectionManager,
        KnowledgeBaseManager,
        ProjectsManager,
        ResourceManager,
        SiteManager,
        TasksManager,
        TicketManager,
        TimeEntriesManager,
        UsersManager,
        WebhooksManager,
    )

    _MANAGERS_AVAILABLE = True
except ImportError:
    _MANAGERS_AVAILABLE = False

# GraphQL utilities (optional import to avoid circular dependencies)
try:
    from .graphql import (  # Common types and enums; Pre-built queries; Convenience functions
        AssetStatus,
        AttachmentType,
        BillingCycle,
        ClientStatus,
        Comment,
        CommentType,
        CommonQueries,
        ContractStatus,
        ContractType,
        EntityType,
        PaginationArgs,
        ProjectPriority,
        ProjectStatus,
        SLALevel,
        SortArgs,
        SuperOpsQueries,
        TicketPriority,
        TicketStatus,
        TimeEntry,
        TimeEntryStatus,
        TimeEntryTemplate,
        TimeEntryType,
        Timer,
        TimerState,
        UserRole,
        UserStatus,
        build_asset_list_query,
        build_client_list_query,
        build_contract_list_query,
        build_project_list_query,
        build_ticket_list_query,
        build_time_entry_list_query,
        build_user_list_query,
    )

    _GRAPHQL_AVAILABLE = True
except ImportError:
    _GRAPHQL_AVAILABLE = False

# Version information
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    # Core classes
    "SuperOpsClient",
    "SuperOpsConfig",
    "AuthHandler",
    # Configuration helpers
    "get_default_config",
    "load_config",
    # Exceptions
    "SuperOpsError",
    "SuperOpsAPIError",
    "SuperOpsAuthenticationError",
    "SuperOpsConfigurationError",
    "SuperOpsNetworkError",
    "SuperOpsRateLimitError",
    "SuperOpsResourceNotFoundError",
    "SuperOpsTimeoutError",
    "SuperOpsValidationError",
    # Resource managers (if available)
    *(
        [
            "ResourceManager",
            "ClientManager",
            "TicketManager",
            "TasksManager",
            "AssetManager",
            "AttachmentsManager",
            "SiteManager",
            "ContactManager",
            "CommentsManager",
            "ContractsManager",
            "KnowledgeBaseManager",
            "KnowledgeBaseArticleManager",
            "KnowledgeBaseCollectionManager",
            "ProjectsManager",
            "TimeEntriesManager",
            "UsersManager",
            "WebhooksManager",
        ]
        if _MANAGERS_AVAILABLE
        else []
    ),
    # GraphQL utilities (if available)
    *(
        [
            "ClientStatus",
            "TicketStatus",
            "TicketPriority",
            "AssetStatus",
            "AttachmentType",
            "Comment",
            "CommentType",
            "EntityType",
            "ContractStatus",
            "ContractType",
            "BillingCycle",
            "SLALevel",
            "ProjectStatus",
            "ProjectPriority",
            "TimeEntry",
            "TimeEntryStatus",
            "TimeEntryType",
            "TimerState",
            "Timer",
            "TimeEntryTemplate",
            "UserRole",
            "UserStatus",
            "PaginationArgs",
            "SortArgs",
            "CommonQueries",
            "SuperOpsQueries",
            "build_client_list_query",
            "build_ticket_list_query",
            "build_asset_list_query",
            "build_contract_list_query",
            "build_project_list_query",
            "build_time_entry_list_query",
            "build_user_list_query",
        ]
        if _GRAPHQL_AVAILABLE
        else []
    ),
]

# Package metadata for introspection
__package_info__ = {
    "name": "py-superops",
    "version": __version__,
    "description": "Python client library for the SuperOps GraphQL API with type-safe query builders",
    "author": __author__,
    "author_email": __email__,
    "license": __license__,
    "url": "https://github.com/superops/py-superops",
    "python_requires": ">=3.8",
    "features": [
        "Async GraphQL client with connection pooling",
        "Type-safe query and mutation builders",
        "Pre-built common queries for all resources",
        "GraphQL fragments for field selection",
        "High-level resource managers with Pythonic interfaces",
        "Domain-specific business logic and workflows",
        "Comprehensive error handling and retry logic",
        "Built-in authentication and rate limiting",
        "Schema introspection and validation",
    ]
    + (
        ["Resource managers available"]
        if _MANAGERS_AVAILABLE
        else ["Resource managers not available"]
    )
    + (
        ["GraphQL utilities available"]
        if _GRAPHQL_AVAILABLE
        else ["GraphQL utilities not available"]
    ),
}


def get_version() -> str:
    """Get the package version.

    Returns:
        Version string in semantic versioning format
    """
    return __version__


def get_package_info() -> dict:
    """Get package metadata information.

    Returns:
        Dictionary containing package metadata
    """
    return __package_info__.copy()


# Convenience function for quick client creation
def create_client(
    api_key: Optional[str] = None, base_url: Optional[str] = None, **config_kwargs: Any
) -> SuperOpsClient:
    """Create a SuperOps client with minimal configuration.

    Args:
        api_key: SuperOps API key (if not provided, loaded from environment)
        base_url: API base URL (if not provided, uses default)
        **config_kwargs: Additional configuration options

    Returns:
        Configured SuperOpsClient instance

    Example:
        ```python
        # Create client with API key
        client = create_client(api_key="your-api-key")

        # Create client with environment variables
        client = create_client()

        # Create client with custom configuration
        client = create_client(
            api_key="your-api-key",  # pragma: allowlist secret
            timeout=60.0,
            debug=True
        )
        ```
    """
    config_data = {}

    if api_key:
        config_data["api_key"] = api_key

    if base_url:
        config_data["base_url"] = base_url

    config_data.update(config_kwargs)

    if config_data:
        config = SuperOpsConfig(**config_data)
    else:
        config = SuperOpsConfig.from_env()

    return SuperOpsClient(config)
