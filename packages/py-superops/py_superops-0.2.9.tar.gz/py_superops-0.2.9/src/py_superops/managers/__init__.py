# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Resource managers for SuperOps API operations.

This package provides high-level, Pythonic interfaces for managing SuperOps resources.
Each manager abstracts the complexity of GraphQL operations and provides intuitive
methods for common business operations.

Example:
    ```python
    import asyncio
    from py_superops import SuperOpsClient, SuperOpsConfig

    async def main():
        # Create client
        config = SuperOpsConfig.from_env()
        client = SuperOpsClient(config)

        # Use managers for high-level operations
        async with client:
            # Client management
            active_clients = await client.clients.get_active_clients()

            # Ticket workflow
            overdue_tickets = await client.tickets.get_overdue_tickets()
            for ticket in overdue_tickets['items']:
                await client.tickets.change_priority(
                    ticket.id,
                    TicketPriority.HIGH
                )

            # Asset tracking
            expiring_warranties = await client.assets.get_warranty_expiring_soon(
                days_threshold=30
            )

    asyncio.run(main())
    ```

Available Managers:
    - AutomationManager: Automation workflow management with job execution and scheduling
    - ClientManager: Client/customer management and workflows
    - TicketManager: Ticket lifecycle and workflow operations
    - TasksManager: Task management with project linking and time tracking
    - AssetManager: Asset tracking and warranty management
    - SiteManager: Site/location management
    - ContactManager: Contact organization and management
    - CommentsManager: Comment management and threaded conversations
    - KnowledgeBaseManager: Knowledge base articles and collections
    - ProjectsManager: Project management and tracking
    - ScriptsManager: Script management, execution, and deployment operations
    - ContractsManager: Contract lifecycle and management operations
    - UsersManager: User management and role assignment operations
    - WebhooksManager: Webhook management and delivery tracking
"""

from .assets import AssetManager
from .attachments import AttachmentsManager
from .automation_manager import AutomationManager
from .base import ResourceManager
from .clients import ClientManager
from .comments import CommentsManager
from .contacts import ContactManager
from .contracts import ContractsManager
from .knowledge_base import (
    KnowledgeBaseArticleManager,
    KnowledgeBaseCollectionManager,
    KnowledgeBaseManager,
)
from .monitoring_manager import MonitoringManager
from .projects import ProjectsManager
from .scripts_manager import ScriptsManager
from .sites import SiteManager
from .tasks import TasksManager
from .tickets import TicketManager
from .time_entries import TimeEntriesManager
from .users import UsersManager
from .webhooks import WebhooksManager

__all__ = [
    # Base manager
    "ResourceManager",
    # Domain-specific managers
    "AutomationManager",
    "ClientManager",
    "MonitoringManager",
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
    "ScriptsManager",
    "TimeEntriesManager",
    "UsersManager",
    "WebhooksManager",
]

# Manager registry for dynamic access
MANAGER_REGISTRY = {
    "automation": AutomationManager,
    "clients": ClientManager,
    "tickets": TicketManager,
    "tasks": TasksManager,
    "assets": AssetManager,
    "attachments": AttachmentsManager,
    "sites": SiteManager,
    "contacts": ContactManager,
    "comments": CommentsManager,
    "contracts": ContractsManager,
    "knowledge_base": KnowledgeBaseManager,
    "projects": ProjectsManager,
    "scripts": ScriptsManager,
    "time_entries": TimeEntriesManager,
    "users": UsersManager,
    "webhooks": WebhooksManager,
}


def get_manager_class(manager_name: str) -> type:
    """Get a manager class by name.

    Args:
        manager_name: Name of the manager ('clients', 'tickets', etc.)

    Returns:
        Manager class

    Raises:
        KeyError: If manager name is not found

    Example:
        ```python
        ClientManagerClass = get_manager_class('clients')
        manager = ClientManagerClass(client)
        ```
    """
    if manager_name not in MANAGER_REGISTRY:
        available = ", ".join(MANAGER_REGISTRY.keys())
        raise KeyError(f"Unknown manager '{manager_name}'. Available: {available}")

    return MANAGER_REGISTRY[manager_name]


def list_available_managers() -> list[str]:
    """Get list of available manager names.

    Returns:
        List of manager names

    Example:
        ```python
        managers = list_available_managers()
        print(f"Available managers: {', '.join(managers)}")
        ```
    """
    return list(MANAGER_REGISTRY.keys())
