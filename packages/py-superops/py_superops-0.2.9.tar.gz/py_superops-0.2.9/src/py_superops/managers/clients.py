# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Client/Customer manager for SuperOps API operations."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..exceptions import SuperOpsValidationError
from ..graphql.types import Client, ClientStatus
from .base import ResourceManager


class ClientManager(ResourceManager[Client]):
    """Manager for client/customer operations.

    Provides high-level methods for managing SuperOps clients including
    CRUD operations, business logic, and client-specific workflows.
    """

    def __init__(self, client: "SuperOpsClient"):
        """Initialize the client manager.

        Args:
            client: SuperOps client instance
        """
        super().__init__(client, Client, "client")

    async def get_by_name(self, name: str) -> Optional[Client]:
        """Get a client by name.

        Args:
            name: Client name to search for

        Returns:
            Client instance or None if not found

        Raises:
            SuperOpsValidationError: If name is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not name or not isinstance(name, str):
            raise SuperOpsValidationError("Client name must be a non-empty string")

        self.logger.debug(f"Getting client by name: {name}")

        # Use search with exact name match
        results = await self.search(f'name:"{name}"', page_size=1)

        # Return first exact match if any
        for client in results["items"]:
            if client.name == name:
                return client

        return None

    async def get_by_email(self, email: str) -> Optional[Client]:
        """Get a client by email address.

        Args:
            email: Email address to search for

        Returns:
            Client instance or None if not found

        Raises:
            SuperOpsValidationError: If email is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not email or not isinstance(email, str):
            raise SuperOpsValidationError("Email must be a non-empty string")
        if "@" not in email:
            raise SuperOpsValidationError("Invalid email format")

        self.logger.debug(f"Getting client by email: {email}")

        # Use search with exact email match
        results = await self.search(f'email:"{email}"', page_size=1)

        # Return first exact match if any
        for client in results["items"]:
            if client.email == email:
                return client

        return None

    async def get_with_sites(self, client_id: str) -> Optional[Client]:
        """Get a client with all associated sites loaded.

        Args:
            client_id: The client ID

        Returns:
            Client instance with sites or None if not found

        Raises:
            SuperOpsValidationError: If client_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not client_id or not isinstance(client_id, str):
            raise SuperOpsValidationError(f"Invalid client ID: {client_id}")

        self.logger.debug(f"Getting client with sites: {client_id}")

        return await self.get(client_id, include_sites=True)

    async def get_with_contacts(self, client_id: str) -> Optional[Client]:
        """Get a client with all associated contacts loaded.

        Args:
            client_id: The client ID

        Returns:
            Client instance with contacts or None if not found

        Raises:
            SuperOpsValidationError: If client_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not client_id or not isinstance(client_id, str):
            raise SuperOpsValidationError(f"Invalid client ID: {client_id}")

        self.logger.debug(f"Getting client with contacts: {client_id}")

        return await self.get(client_id, include_contacts=True)

    async def get_active_clients(
        self,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get all active clients.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: name)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Client]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug(f"Getting active clients - page: {page}, size: {page_size}")

        filters = {"status": ClientStatus.ACTIVE.value}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
        )

    async def get_inactive_clients(
        self,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get all inactive clients.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: name)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Client]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug(f"Getting inactive clients - page: {page}, size: {page_size}")

        filters = {"status": ClientStatus.INACTIVE.value}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
        )

    async def activate_client(self, client_id: str) -> Client:
        """Activate a client.

        Args:
            client_id: The client ID

        Returns:
            Updated client instance

        Raises:
            SuperOpsValidationError: If client_id is invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If client doesn't exist
        """
        if not client_id or not isinstance(client_id, str):
            raise SuperOpsValidationError(f"Invalid client ID: {client_id}")

        self.logger.debug(f"Activating client: {client_id}")

        return await self.update(client_id, {"status": ClientStatus.ACTIVE.value})

    async def deactivate_client(self, client_id: str) -> Client:
        """Deactivate a client.

        Args:
            client_id: The client ID

        Returns:
            Updated client instance

        Raises:
            SuperOpsValidationError: If client_id is invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If client doesn't exist
        """
        if not client_id or not isinstance(client_id, str):
            raise SuperOpsValidationError(f"Invalid client ID: {client_id}")

        self.logger.debug(f"Deactivating client: {client_id}")

        return await self.update(client_id, {"status": ClientStatus.INACTIVE.value})

    async def suspend_client(self, client_id: str) -> Client:
        """Suspend a client.

        Args:
            client_id: The client ID

        Returns:
            Updated client instance

        Raises:
            SuperOpsValidationError: If client_id is invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If client doesn't exist
        """
        if not client_id or not isinstance(client_id, str):
            raise SuperOpsValidationError(f"Invalid client ID: {client_id}")

        self.logger.debug(f"Suspending client: {client_id}")

        return await self.update(client_id, {"status": ClientStatus.SUSPENDED.value})

    async def bulk_update_status(self, client_ids: List[str], status: ClientStatus) -> List[Client]:
        """Update status for multiple clients.

        Args:
            client_ids: List of client IDs
            status: New status for all clients

        Returns:
            List of updated client instances

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If any API request fails
        """
        if not client_ids:
            raise SuperOpsValidationError("Client IDs list cannot be empty")
        if not isinstance(client_ids, list):
            raise SuperOpsValidationError("Client IDs must be a list")
        if not isinstance(status, ClientStatus):
            raise SuperOpsValidationError("Status must be a ClientStatus enum")

        self.logger.debug(f"Bulk updating status for {len(client_ids)} clients to {status.value}")

        updated_clients = []
        for client_id in client_ids:
            try:
                updated_client = await self.update(client_id, {"status": status.value})
                updated_clients.append(updated_client)
            except Exception as e:
                self.logger.error(f"Failed to update client {client_id}: {e}")
                # Continue with other clients

        self.logger.info(
            f"Successfully updated {len(updated_clients)} out of {len(client_ids)} clients"
        )
        return updated_clients

    async def add_tag(self, client_id: str, tag: str) -> Client:
        """Add a tag to a client.

        Args:
            client_id: The client ID
            tag: Tag to add

        Returns:
            Updated client instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not client_id or not isinstance(client_id, str):
            raise SuperOpsValidationError(f"Invalid client ID: {client_id}")
        if not tag or not isinstance(tag, str):
            raise SuperOpsValidationError("Tag must be a non-empty string")

        self.logger.debug(f"Adding tag '{tag}' to client: {client_id}")

        # Get current client to access existing tags
        client = await self.get(client_id)
        if not client:
            raise SuperOpsValidationError(f"Client not found: {client_id}")

        # Add tag if not already present
        current_tags = client.tags or []
        if tag not in current_tags:
            current_tags.append(tag)
            return await self.update(client_id, {"tags": current_tags})

        return client

    async def remove_tag(self, client_id: str, tag: str) -> Client:
        """Remove a tag from a client.

        Args:
            client_id: The client ID
            tag: Tag to remove

        Returns:
            Updated client instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not client_id or not isinstance(client_id, str):
            raise SuperOpsValidationError(f"Invalid client ID: {client_id}")
        if not tag or not isinstance(tag, str):
            raise SuperOpsValidationError("Tag must be a non-empty string")

        self.logger.debug(f"Removing tag '{tag}' from client: {client_id}")

        # Get current client to access existing tags
        client = await self.get(client_id)
        if not client:
            raise SuperOpsValidationError(f"Client not found: {client_id}")

        # Remove tag if present
        current_tags = client.tags or []
        if tag in current_tags:
            current_tags.remove(tag)
            return await self.update(client_id, {"tags": current_tags})

        return client

    # Protected methods for GraphQL query building

    def _build_get_query(self, **kwargs) -> str:
        """Build GraphQL query for getting a single client."""
        include_sites = kwargs.get("include_sites", False)
        include_contacts = kwargs.get("include_contacts", False)

        fields = [
            "id",
            "name",
            "email",
            "phone",
            "address",
            "billingAddress",
            "status",
            "notes",
            "tags",
            "customFields",
            "createdAt",
            "updatedAt",
        ]

        if include_sites:
            fields.append(
                """
                sites {
                    id
                    name
                    address
                    description
                    timezone
                    createdAt
                    updatedAt
                }
            """
            )

        if include_contacts:
            fields.append(
                """
                contacts {
                    id
                    firstName
                    lastName
                    email
                    phone
                    title
                    isPrimary
                    createdAt
                    updatedAt
                }
            """
            )

        field_str = "\n        ".join(fields)

        return f"""
            query GetClient($id: ID!) {{
                client(id: $id) {{
                    {field_str}
                }}
            }}
        """

    def _build_list_query(self, **kwargs) -> str:
        """Build GraphQL query for listing clients."""
        return """
            query ListClients(
                $page: Int!
                $pageSize: Int!
                $filters: ClientFilter
                $sortBy: String
                $sortOrder: SortOrder
            ) {
                clients(
                    page: $page
                    pageSize: $pageSize
                    filters: $filters
                    sortBy: $sortBy
                    sortOrder: $sortOrder
                ) {
                    items {
                        id
                        name
                        email
                        phone
                        address
                        billingAddress
                        status
                        notes
                        tags
                        customFields
                        createdAt
                        updatedAt
                    }
                    pagination {
                        page
                        pageSize
                        total
                        hasNextPage
                        hasPreviousPage
                    }
                }
            }
        """

    def _build_create_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for creating a client."""
        return """
            mutation CreateClient($input: CreateClientInput!) {
                createClient(input: $input) {
                    id
                    name
                    email
                    phone
                    address
                    billingAddress
                    status
                    notes
                    tags
                    customFields
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_update_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for updating a client."""
        return """
            mutation UpdateClient($id: ID!, $input: UpdateClientInput!) {
                updateClient(id: $id, input: $input) {
                    id
                    name
                    email
                    phone
                    address
                    billingAddress
                    status
                    notes
                    tags
                    customFields
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_delete_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for deleting a client."""
        return """
            mutation DeleteClient($id: ID!) {
                deleteClient(id: $id) {
                    success
                    message
                }
            }
        """

    def _build_search_query(self, **kwargs) -> str:
        """Build GraphQL query for searching clients."""
        return """
            query SearchClients(
                $query: String!
                $page: Int!
                $pageSize: Int!
            ) {
                searchClients(
                    query: $query
                    page: $page
                    pageSize: $pageSize
                ) {
                    items {
                        id
                        name
                        email
                        phone
                        address
                        billingAddress
                        status
                        notes
                        tags
                        customFields
                        createdAt
                        updatedAt
                    }
                    pagination {
                        page
                        pageSize
                        total
                        hasNextPage
                        hasPreviousPage
                    }
                }
            }
        """

    def _validate_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data for client creation."""
        validated = data.copy()

        # Required fields
        if not validated.get("name"):
            raise SuperOpsValidationError("Client name is required")

        # Validate email format if provided
        email = validated.get("email")
        if email and "@" not in email:
            raise SuperOpsValidationError("Invalid email format")

        # Validate status if provided
        status = validated.get("status")
        if status and status not in [s.value for s in ClientStatus]:
            raise SuperOpsValidationError(f"Invalid client status: {status}")

        return validated

    def _validate_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data for client updates."""
        validated = data.copy()

        # Validate email format if provided
        email = validated.get("email")
        if email and "@" not in email:
            raise SuperOpsValidationError("Invalid email format")

        # Validate status if provided
        status = validated.get("status")
        if status and status not in [s.value for s in ClientStatus]:
            raise SuperOpsValidationError(f"Invalid client status: {status}")

        return validated
