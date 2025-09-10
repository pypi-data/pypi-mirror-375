# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Contact manager for SuperOps API operations."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..exceptions import SuperOpsValidationError
from ..graphql.types import Contact
from .base import ResourceManager


class ContactManager(ResourceManager[Contact]):
    """Manager for contact operations.

    Provides high-level methods for managing SuperOps contacts including
    CRUD operations, contact organization, and contact-specific workflows.
    """

    def __init__(self, client: "SuperOpsClient"):
        """Initialize the contact manager.

        Args:
            client: SuperOps client instance
        """
        super().__init__(client, Contact, "contact")

    async def get_by_client(
        self,
        client_id: str,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get contacts for a specific client.

        Args:
            client_id: The client ID
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: last_name)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Contact]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not client_id or not isinstance(client_id, str):
            raise SuperOpsValidationError("Client ID must be a non-empty string")

        self.logger.debug(f"Getting contacts for client: {client_id}")

        filters = {"client_id": client_id}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "last_name",
            sort_order=sort_order,
        )

    async def get_by_email(self, email: str) -> Optional[Contact]:
        """Get a contact by email address.

        Args:
            email: Email address to search for

        Returns:
            Contact instance or None if not found

        Raises:
            SuperOpsValidationError: If email is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not email or not isinstance(email, str):
            raise SuperOpsValidationError("Email must be a non-empty string")
        if "@" not in email:
            raise SuperOpsValidationError("Invalid email format")

        self.logger.debug(f"Getting contact by email: {email}")

        # Use search with exact email match
        results = await self.search(f'email:"{email}"', page_size=1)

        # Return first exact match if any
        for contact in results["items"]:
            if contact.email == email:
                return contact

        return None

    async def get_by_name(
        self, first_name: str, last_name: str, client_id: Optional[str] = None
    ) -> List[Contact]:
        """Get contacts by name.

        Args:
            first_name: First name to search for
            last_name: Last name to search for
            client_id: Optional client ID to limit search scope

        Returns:
            List of matching contacts

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not first_name or not isinstance(first_name, str):
            raise SuperOpsValidationError("First name must be a non-empty string")
        if not last_name or not isinstance(last_name, str):
            raise SuperOpsValidationError("Last name must be a non-empty string")

        self.logger.debug(f"Getting contacts by name: {first_name} {last_name}")

        # Build search query
        search_query = f'first_name:"{first_name}" last_name:"{last_name}"'
        if client_id:
            search_query += f' client_id:"{client_id}"'

        results = await self.search(search_query, page_size=50)

        # Filter for exact matches
        exact_matches = []
        for contact in results["items"]:
            if (
                contact.first_name.lower() == first_name.lower()
                and contact.last_name.lower() == last_name.lower()
            ):
                if client_id is None or contact.client_id == client_id:
                    exact_matches.append(contact)

        return exact_matches

    async def get_primary_contacts(
        self,
        page: int = 1,
        page_size: int = 50,
        client_id: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get primary contacts.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            client_id: Optional client ID to filter by
            sort_by: Field to sort by (default: last_name)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Contact]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Getting primary contacts")

        filters = {"is_primary": True}
        if client_id:
            filters["client_id"] = client_id

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "last_name",
            sort_order=sort_order,
        )

    async def get_by_title(
        self,
        title: str,
        page: int = 1,
        page_size: int = 50,
        client_id: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get contacts by job title.

        Args:
            title: Job title to filter by
            page: Page number (1-based)
            page_size: Number of items per page
            client_id: Optional client ID to filter by
            sort_by: Field to sort by (default: last_name)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Contact]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not title or not isinstance(title, str):
            raise SuperOpsValidationError("Title must be a non-empty string")

        self.logger.debug(f"Getting contacts with title: {title}")

        filters = {"title": title}
        if client_id:
            filters["client_id"] = client_id

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "last_name",
            sort_order=sort_order,
        )

    async def set_primary_contact(
        self, contact_id: str, client_id: Optional[str] = None
    ) -> Contact:
        """Set a contact as the primary contact for their client.

        This will unset any existing primary contact for the client.

        Args:
            contact_id: The contact ID to set as primary
            client_id: Optional client ID for validation

        Returns:
            Updated contact instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not contact_id or not isinstance(contact_id, str):
            raise SuperOpsValidationError(f"Invalid contact ID: {contact_id}")

        self.logger.debug(f"Setting primary contact: {contact_id}")

        # Get the contact first to validate it exists and get client_id
        contact = await self.get(contact_id)
        if not contact:
            raise SuperOpsValidationError(f"Contact not found: {contact_id}")

        # If client_id provided, validate it matches
        if client_id and contact.client_id != client_id:
            raise SuperOpsValidationError("Contact does not belong to specified client")

        # Use the mutation that handles primary contact switching
        mutation = """
            mutation SetPrimaryContact($contactId: ID!) {
                setPrimaryContact(contactId: $contactId) {
                    id
                    clientId
                    firstName
                    lastName
                    email
                    phone
                    title
                    isPrimary
                    notes
                    createdAt
                    updatedAt
                }
            }
        """

        variables = {"contactId": contact_id}

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when setting primary contact", 500, response)

        contact_data = response["data"].get("setPrimaryContact")
        if not contact_data:
            raise SuperOpsAPIError("No contact data in response", 500, response)

        return Contact.from_dict(contact_data)

    async def unset_primary_contact(self, contact_id: str) -> Contact:
        """Unset a contact as primary contact.

        Args:
            contact_id: The contact ID

        Returns:
            Updated contact instance

        Raises:
            SuperOpsValidationError: If contact_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not contact_id or not isinstance(contact_id, str):
            raise SuperOpsValidationError(f"Invalid contact ID: {contact_id}")

        self.logger.debug(f"Unsetting primary contact: {contact_id}")

        return await self.update(contact_id, {"is_primary": False})

    async def update_contact_info(
        self,
        contact_id: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Contact:
        """Update contact information.

        Args:
            contact_id: The contact ID
            email: New email address
            phone: New phone number
            title: New job title

        Returns:
            Updated contact instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not contact_id or not isinstance(contact_id, str):
            raise SuperOpsValidationError(f"Invalid contact ID: {contact_id}")

        self.logger.debug(f"Updating contact info: {contact_id}")

        update_data = {}

        if email is not None:
            if "@" not in email:
                raise SuperOpsValidationError("Invalid email format")
            update_data["email"] = email

        if phone is not None:
            update_data["phone"] = phone

        if title is not None:
            update_data["title"] = title

        if not update_data:
            raise SuperOpsValidationError("No update data provided")

        return await self.update(contact_id, update_data)

    async def bulk_update_title(self, contact_ids: List[str], new_title: str) -> List[Contact]:
        """Update job title for multiple contacts.

        Args:
            contact_ids: List of contact IDs
            new_title: New title for all contacts

        Returns:
            List of updated contact instances

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If any API request fails
        """
        if not contact_ids:
            raise SuperOpsValidationError("Contact IDs list cannot be empty")
        if not isinstance(contact_ids, list):
            raise SuperOpsValidationError("Contact IDs must be a list")
        if not new_title or not isinstance(new_title, str):
            raise SuperOpsValidationError("New title must be a non-empty string")

        self.logger.debug(f"Bulk updating title for {len(contact_ids)} contacts to '{new_title}'")

        updated_contacts = []
        for contact_id in contact_ids:
            try:
                updated_contact = await self.update(contact_id, {"title": new_title})
                updated_contacts.append(updated_contact)
            except Exception as e:
                self.logger.error(f"Failed to update contact {contact_id}: {e}")
                # Continue with other contacts

        self.logger.info(
            f"Successfully updated {len(updated_contacts)} out of {len(contact_ids)} contacts"
        )
        return updated_contacts

    async def get_contact_statistics_for_client(self, client_id: str) -> Dict[str, Any]:
        """Get contact statistics for a client.

        Args:
            client_id: The client ID

        Returns:
            Dictionary containing contact statistics

        Raises:
            SuperOpsValidationError: If client_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not client_id or not isinstance(client_id, str):
            raise SuperOpsValidationError("Client ID must be a non-empty string")

        self.logger.debug(f"Getting contact statistics for client: {client_id}")

        query = """
            query GetClientContactStatistics($clientId: ID!) {
                client(id: $clientId) {
                    id
                    name
                    contactStatistics {
                        totalContacts
                        primaryContacts
                        contactsWithEmail
                        contactsWithPhone
                        uniqueTitles
                        topTitles {
                            title
                            count
                        }
                    }
                }
            }
        """

        variables = {"clientId": client_id}

        response = await self.client.execute_query(query, variables)

        if not response.get("data") or not response["data"].get("client"):
            return {}

        client_data = response["data"]["client"]
        stats = client_data.get("contactStatistics", {})

        return {
            "client_id": client_data.get("id"),
            "client_name": client_data.get("name"),
            "total_contacts": stats.get("totalContacts", 0),
            "primary_contacts": stats.get("primaryContacts", 0),
            "contacts_with_email": stats.get("contactsWithEmail", 0),
            "contacts_with_phone": stats.get("contactsWithPhone", 0),
            "unique_titles": stats.get("uniqueTitles", 0),
            "top_titles": stats.get("topTitles", []),
        }

    async def get_job_titles(self, client_id: Optional[str] = None) -> List[str]:
        """Get list of unique job titles.

        Args:
            client_id: Optional client ID to filter by

        Returns:
            List of job title strings

        Raises:
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Getting unique job titles")

        query = """
            query GetContactTitles($clientId: ID) {
                contactTitles(clientId: $clientId) {
                    title
                    count
                }
            }
        """

        variables = {"clientId": client_id} if client_id else {}

        response = await self.client.execute_query(query, variables)

        if not response.get("data"):
            return []

        titles_data = response["data"].get("contactTitles", [])
        return [item["title"] for item in titles_data]

    # Protected methods for GraphQL query building

    def _build_get_query(self, **kwargs) -> str:
        """Build GraphQL query for getting a single contact."""
        return """
            query GetContact($id: ID!) {
                contact(id: $id) {
                    id
                    clientId
                    firstName
                    lastName
                    email
                    phone
                    title
                    isPrimary
                    notes
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_list_query(self, **kwargs) -> str:
        """Build GraphQL query for listing contacts."""
        return """
            query ListContacts(
                $page: Int!
                $pageSize: Int!
                $filters: ContactFilter
                $sortBy: String
                $sortOrder: SortOrder
            ) {
                contacts(
                    page: $page
                    pageSize: $pageSize
                    filters: $filters
                    sortBy: $sortBy
                    sortOrder: $sortOrder
                ) {
                    items {
                        id
                        clientId
                        firstName
                        lastName
                        email
                        phone
                        title
                        isPrimary
                        notes
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
        """Build GraphQL mutation for creating a contact."""
        return """
            mutation CreateContact($input: CreateContactInput!) {
                createContact(input: $input) {
                    id
                    clientId
                    firstName
                    lastName
                    email
                    phone
                    title
                    isPrimary
                    notes
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_update_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for updating a contact."""
        return """
            mutation UpdateContact($id: ID!, $input: UpdateContactInput!) {
                updateContact(id: $id, input: $input) {
                    id
                    clientId
                    firstName
                    lastName
                    email
                    phone
                    title
                    isPrimary
                    notes
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_delete_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for deleting a contact."""
        return """
            mutation DeleteContact($id: ID!) {
                deleteContact(id: $id) {
                    success
                    message
                }
            }
        """

    def _build_search_query(self, **kwargs) -> str:
        """Build GraphQL query for searching contacts."""
        return """
            query SearchContacts(
                $query: String!
                $page: Int!
                $pageSize: Int!
            ) {
                searchContacts(
                    query: $query
                    page: $page
                    pageSize: $pageSize
                ) {
                    items {
                        id
                        clientId
                        firstName
                        lastName
                        email
                        phone
                        title
                        isPrimary
                        notes
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
        """Validate data for contact creation."""
        validated = data.copy()

        # Required fields
        if not validated.get("first_name"):
            raise SuperOpsValidationError("First name is required")
        if not validated.get("last_name"):
            raise SuperOpsValidationError("Last name is required")
        if not validated.get("email"):
            raise SuperOpsValidationError("Email is required")
        if not validated.get("client_id"):
            raise SuperOpsValidationError("Client ID is required")

        # Validate email format
        email = validated.get("email")
        if "@" not in email:
            raise SuperOpsValidationError("Invalid email format")

        return validated

    def _validate_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data for contact updates."""
        validated = data.copy()

        # Validate email format if provided
        email = validated.get("email")
        if email and "@" not in email:
            raise SuperOpsValidationError("Invalid email format")

        return validated
