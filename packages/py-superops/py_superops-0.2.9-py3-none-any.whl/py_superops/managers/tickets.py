# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Ticket manager for SuperOps API operations."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..exceptions import SuperOpsValidationError
from ..graphql.types import Ticket, TicketComment, TicketPriority, TicketStatus
from .base import ResourceManager


class TicketManager(ResourceManager[Ticket]):
    """Manager for ticket operations.

    Provides high-level methods for managing SuperOps tickets including
    CRUD operations, lifecycle management, workflow operations, and ticket-specific features.
    """

    def __init__(self, client: "SuperOpsClient"):
        """Initialize the ticket manager.

        Args:
            client: SuperOps client instance
        """
        super().__init__(client, Ticket, "ticket")

    async def get_by_status(
        self,
        status: TicketStatus,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get tickets filtered by status.

        Args:
            status: Ticket status to filter by
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Ticket]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not isinstance(status, TicketStatus):
            raise SuperOpsValidationError("Status must be a TicketStatus enum")

        self.logger.debug(f"Getting tickets with status: {status.value}")

        filters = {"status": status.value}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
        )

    async def get_by_assignee(
        self,
        assignee_id: str,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get tickets assigned to a specific user.

        Args:
            assignee_id: The assignee user ID
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Ticket]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not assignee_id or not isinstance(assignee_id, str):
            raise SuperOpsValidationError("Assignee ID must be a non-empty string")

        self.logger.debug(f"Getting tickets assigned to: {assignee_id}")

        filters = {"assigned_to": assignee_id}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
        )

    async def get_by_client(
        self,
        client_id: str,
        page: int = 1,
        page_size: int = 50,
        status_filter: Optional[TicketStatus] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get tickets for a specific client.

        Args:
            client_id: The client ID
            page: Page number (1-based)
            page_size: Number of items per page
            status_filter: Optional status filter
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Ticket]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not client_id or not isinstance(client_id, str):
            raise SuperOpsValidationError("Client ID must be a non-empty string")

        self.logger.debug(f"Getting tickets for client: {client_id}")

        filters = {"client_id": client_id}
        if status_filter:
            filters["status"] = status_filter.value

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
        )

    async def get_overdue_tickets(
        self,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get all overdue tickets.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: due_date)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Ticket]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Getting overdue tickets")

        # Filter by due date before current time and not closed/resolved
        now = datetime.utcnow()
        filters = {
            "due_before": now.isoformat(),
            "status__not_in": [TicketStatus.CLOSED.value, TicketStatus.RESOLVED.value],
        }

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "due_date",
            sort_order=sort_order,
        )

    async def get_high_priority_tickets(
        self,
        page: int = 1,
        page_size: int = 50,
        include_urgent: bool = True,
        include_critical: bool = True,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get high priority tickets.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            include_urgent: Include urgent priority tickets
            include_critical: Include critical priority tickets
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Ticket]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Getting high priority tickets")

        priority_values = [TicketPriority.HIGH.value]
        if include_urgent:
            priority_values.append(TicketPriority.URGENT.value)
        if include_critical:
            priority_values.append(TicketPriority.CRITICAL.value)

        filters = {"priority__in": priority_values}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
        )

    async def assign_ticket(
        self,
        ticket_id: str,
        assignee_id: str,
        add_comment: bool = True,
        comment_text: Optional[str] = None,
    ) -> Ticket:
        """Assign a ticket to a user.

        Args:
            ticket_id: The ticket ID
            assignee_id: The assignee user ID
            add_comment: Whether to add an assignment comment
            comment_text: Optional custom comment text

        Returns:
            Updated ticket instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not ticket_id or not isinstance(ticket_id, str):
            raise SuperOpsValidationError("Ticket ID must be a non-empty string")
        if not assignee_id or not isinstance(assignee_id, str):
            raise SuperOpsValidationError("Assignee ID must be a non-empty string")

        self.logger.debug(f"Assigning ticket {ticket_id} to {assignee_id}")

        # Update ticket assignment
        ticket = await self.update(ticket_id, {"assigned_to": assignee_id})

        # Add assignment comment if requested
        if add_comment:
            comment = comment_text or f"Ticket assigned to {assignee_id}"
            await self.add_comment(ticket_id, comment, is_internal=True)

        return ticket

    async def change_status(
        self,
        ticket_id: str,
        new_status: TicketStatus,
        add_comment: bool = True,
        comment_text: Optional[str] = None,
        resolution_notes: Optional[str] = None,
    ) -> Ticket:
        """Change ticket status.

        Args:
            ticket_id: The ticket ID
            new_status: New ticket status
            add_comment: Whether to add a status change comment
            comment_text: Optional custom comment text
            resolution_notes: Resolution notes (for resolved/closed tickets)

        Returns:
            Updated ticket instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not ticket_id or not isinstance(ticket_id, str):
            raise SuperOpsValidationError("Ticket ID must be a non-empty string")
        if not isinstance(new_status, TicketStatus):
            raise SuperOpsValidationError("Status must be a TicketStatus enum")

        self.logger.debug(f"Changing ticket {ticket_id} status to {new_status.value}")

        update_data = {"status": new_status.value}

        # Add resolution notes for closed/resolved tickets
        if new_status in (TicketStatus.RESOLVED, TicketStatus.CLOSED) and resolution_notes:
            update_data["resolution"] = resolution_notes

        # Update ticket status
        ticket = await self.update(ticket_id, update_data)

        # Add status change comment if requested
        if add_comment:
            comment = comment_text or f"Ticket status changed to {new_status.value}"
            await self.add_comment(ticket_id, comment, is_internal=True)

        return ticket

    async def change_priority(
        self,
        ticket_id: str,
        new_priority: TicketPriority,
        add_comment: bool = True,
        comment_text: Optional[str] = None,
    ) -> Ticket:
        """Change ticket priority.

        Args:
            ticket_id: The ticket ID
            new_priority: New ticket priority
            add_comment: Whether to add a priority change comment
            comment_text: Optional custom comment text

        Returns:
            Updated ticket instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not ticket_id or not isinstance(ticket_id, str):
            raise SuperOpsValidationError("Ticket ID must be a non-empty string")
        if not isinstance(new_priority, TicketPriority):
            raise SuperOpsValidationError("Priority must be a TicketPriority enum")

        self.logger.debug(f"Changing ticket {ticket_id} priority to {new_priority.value}")

        # Update ticket priority
        ticket = await self.update(ticket_id, {"priority": new_priority.value})

        # Add priority change comment if requested
        if add_comment:
            comment = comment_text or f"Ticket priority changed to {new_priority.value}"
            await self.add_comment(ticket_id, comment, is_internal=True)

        return ticket

    async def set_due_date(
        self,
        ticket_id: str,
        due_date: datetime,
        add_comment: bool = True,
        comment_text: Optional[str] = None,
    ) -> Ticket:
        """Set or update ticket due date.

        Args:
            ticket_id: The ticket ID
            due_date: Due date for the ticket
            add_comment: Whether to add a due date comment
            comment_text: Optional custom comment text

        Returns:
            Updated ticket instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not ticket_id or not isinstance(ticket_id, str):
            raise SuperOpsValidationError("Ticket ID must be a non-empty string")
        if not isinstance(due_date, datetime):
            raise SuperOpsValidationError("Due date must be a datetime object")

        self.logger.debug(f"Setting due date for ticket {ticket_id} to {due_date}")

        # Update ticket due date
        ticket = await self.update(ticket_id, {"due_date": due_date.isoformat()})

        # Add due date comment if requested
        if add_comment:
            comment = comment_text or f"Due date set to {due_date.strftime('%Y-%m-%d %H:%M')}"
            await self.add_comment(ticket_id, comment, is_internal=True)

        return ticket

    async def add_comment(
        self,
        ticket_id: str,
        content: str,
        is_internal: bool = False,
        time_spent: Optional[int] = None,
    ) -> TicketComment:
        """Add a comment to a ticket.

        Args:
            ticket_id: The ticket ID
            content: Comment content
            is_internal: Whether this is an internal comment
            time_spent: Time spent in minutes

        Returns:
            Created comment instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not ticket_id or not isinstance(ticket_id, str):
            raise SuperOpsValidationError("Ticket ID must be a non-empty string")
        if not content or not isinstance(content, str):
            raise SuperOpsValidationError("Comment content must be a non-empty string")
        if time_spent is not None and (not isinstance(time_spent, int) or time_spent < 0):
            raise SuperOpsValidationError("Time spent must be a non-negative integer")

        self.logger.debug(f"Adding comment to ticket {ticket_id}")

        mutation = """
            mutation AddTicketComment($input: AddTicketCommentInput!) {
                addTicketComment(input: $input) {
                    id
                    ticketId
                    authorId
                    authorName
                    content
                    isInternal
                    timeSpent
                    createdAt
                    updatedAt
                }
            }
        """

        variables = {
            "input": {
                "ticket_id": ticket_id,
                "content": content,
                "is_internal": is_internal,
                "time_spent": time_spent,
            }
        }

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when adding comment", 500, response)

        comment_data = response["data"].get("addTicketComment")
        if not comment_data:
            raise SuperOpsAPIError("No comment data in response", 500, response)

        return TicketComment.from_dict(comment_data)

    async def get_comments(
        self, ticket_id: str, include_internal: bool = True, page: int = 1, page_size: int = 50
    ) -> List[TicketComment]:
        """Get comments for a ticket.

        Args:
            ticket_id: The ticket ID
            include_internal: Whether to include internal comments
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            List of ticket comments

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not ticket_id or not isinstance(ticket_id, str):
            raise SuperOpsValidationError("Ticket ID must be a non-empty string")

        self.logger.debug(f"Getting comments for ticket {ticket_id}")

        query = """
            query GetTicketComments(
                $ticketId: ID!
                $includeInternal: Boolean!
                $page: Int!
                $pageSize: Int!
            ) {
                ticketComments(
                    ticketId: $ticketId
                    includeInternal: $includeInternal
                    page: $page
                    pageSize: $pageSize
                ) {
                    items {
                        id
                        ticketId
                        authorId
                        authorName
                        content
                        isInternal
                        timeSpent
                        createdAt
                        updatedAt
                    }
                }
            }
        """

        variables = {
            "ticketId": ticket_id,
            "includeInternal": include_internal,
            "page": page,
            "pageSize": page_size,
        }

        response = await self.client.execute_query(query, variables)

        if not response.get("data"):
            return []

        comments_data = response["data"].get("ticketComments", {}).get("items", [])
        return [TicketComment.from_dict(comment) for comment in comments_data]

    async def bulk_update_status(
        self, ticket_ids: List[str], new_status: TicketStatus, add_comments: bool = True
    ) -> List[Ticket]:
        """Update status for multiple tickets.

        Args:
            ticket_ids: List of ticket IDs
            new_status: New status for all tickets
            add_comments: Whether to add status change comments

        Returns:
            List of updated ticket instances

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If any API request fails
        """
        if not ticket_ids:
            raise SuperOpsValidationError("Ticket IDs list cannot be empty")
        if not isinstance(ticket_ids, list):
            raise SuperOpsValidationError("Ticket IDs must be a list")
        if not isinstance(new_status, TicketStatus):
            raise SuperOpsValidationError("Status must be a TicketStatus enum")

        self.logger.debug(
            f"Bulk updating status for {len(ticket_ids)} tickets to {new_status.value}"
        )

        updated_tickets = []
        for ticket_id in ticket_ids:
            try:
                ticket = await self.change_status(ticket_id, new_status, add_comment=add_comments)
                updated_tickets.append(ticket)
            except Exception as e:
                self.logger.error(f"Failed to update ticket {ticket_id}: {e}")
                # Continue with other tickets

        self.logger.info(
            f"Successfully updated {len(updated_tickets)} out of {len(ticket_ids)} tickets"
        )
        return updated_tickets

    async def bulk_assign(
        self, ticket_ids: List[str], assignee_id: str, add_comments: bool = True
    ) -> List[Ticket]:
        """Assign multiple tickets to a user.

        Args:
            ticket_ids: List of ticket IDs
            assignee_id: The assignee user ID
            add_comments: Whether to add assignment comments

        Returns:
            List of updated ticket instances

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If any API request fails
        """
        if not ticket_ids:
            raise SuperOpsValidationError("Ticket IDs list cannot be empty")
        if not isinstance(ticket_ids, list):
            raise SuperOpsValidationError("Ticket IDs must be a list")
        if not assignee_id or not isinstance(assignee_id, str):
            raise SuperOpsValidationError("Assignee ID must be a non-empty string")

        self.logger.debug(f"Bulk assigning {len(ticket_ids)} tickets to {assignee_id}")

        updated_tickets = []
        for ticket_id in ticket_ids:
            try:
                ticket = await self.assign_ticket(ticket_id, assignee_id, add_comment=add_comments)
                updated_tickets.append(ticket)
            except Exception as e:
                self.logger.error(f"Failed to assign ticket {ticket_id}: {e}")
                # Continue with other tickets

        self.logger.info(
            f"Successfully assigned {len(updated_tickets)} out of {len(ticket_ids)} tickets"
        )
        return updated_tickets

    # Protected methods for GraphQL query building

    def _build_get_query(self, **kwargs) -> str:
        """Build GraphQL query for getting a single ticket."""
        include_comments = kwargs.get("include_comments", False)

        fields = [
            "id",
            "clientId",
            "title",
            "description",
            "siteId",
            "assetId",
            "contactId",
            "status",
            "priority",
            "assignedTo",
            "dueDate",
            "resolution",
            "timeSpent",
            "tags",
            "customFields",
            "createdAt",
            "updatedAt",
        ]

        if include_comments:
            fields.append(
                """
                comments {
                    id
                    authorId
                    authorName
                    content
                    isInternal
                    timeSpent
                    createdAt
                }
            """
            )

        field_str = "\n        ".join(fields)

        return f"""
            query GetTicket($id: ID!) {{
                ticket(id: $id) {{
                    {field_str}
                }}
            }}
        """

    def _build_list_query(self, **kwargs) -> str:
        """Build GraphQL query for listing tickets."""
        return """
            query ListTickets(
                $page: Int!
                $pageSize: Int!
                $filters: TicketFilter
                $sortBy: String
                $sortOrder: SortOrder
            ) {
                tickets(
                    page: $page
                    pageSize: $pageSize
                    filters: $filters
                    sortBy: $sortBy
                    sortOrder: $sortOrder
                ) {
                    items {
                        id
                        clientId
                        title
                        description
                        siteId
                        assetId
                        contactId
                        status
                        priority
                        assignedTo
                        dueDate
                        resolution
                        timeSpent
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
        """Build GraphQL mutation for creating a ticket."""
        return """
            mutation CreateTicket($input: CreateTicketInput!) {
                createTicket(input: $input) {
                    id
                    clientId
                    title
                    description
                    siteId
                    assetId
                    contactId
                    status
                    priority
                    assignedTo
                    dueDate
                    resolution
                    timeSpent
                    tags
                    customFields
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_update_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for updating a ticket."""
        return """
            mutation UpdateTicket($id: ID!, $input: UpdateTicketInput!) {
                updateTicket(id: $id, input: $input) {
                    id
                    clientId
                    title
                    description
                    siteId
                    assetId
                    contactId
                    status
                    priority
                    assignedTo
                    dueDate
                    resolution
                    timeSpent
                    tags
                    customFields
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_delete_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for deleting a ticket."""
        return """
            mutation DeleteTicket($id: ID!) {
                deleteTicket(id: $id) {
                    success
                    message
                }
            }
        """

    def _build_search_query(self, **kwargs) -> str:
        """Build GraphQL query for searching tickets."""
        return """
            query SearchTickets(
                $query: String!
                $page: Int!
                $pageSize: Int!
            ) {
                searchTickets(
                    query: $query
                    page: $page
                    pageSize: $pageSize
                ) {
                    items {
                        id
                        clientId
                        title
                        description
                        siteId
                        assetId
                        contactId
                        status
                        priority
                        assignedTo
                        dueDate
                        resolution
                        timeSpent
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
        """Validate data for ticket creation."""
        validated = data.copy()

        # Required fields
        if not validated.get("title"):
            raise SuperOpsValidationError("Ticket title is required")
        if not validated.get("client_id"):
            raise SuperOpsValidationError("Client ID is required")

        # Validate status if provided
        status = validated.get("status")
        if status and status not in [s.value for s in TicketStatus]:
            raise SuperOpsValidationError(f"Invalid ticket status: {status}")

        # Validate priority if provided
        priority = validated.get("priority")
        if priority and priority not in [p.value for p in TicketPriority]:
            raise SuperOpsValidationError(f"Invalid ticket priority: {priority}")

        # Validate due_date format if provided
        due_date = validated.get("due_date")
        if due_date and isinstance(due_date, str):
            try:
                datetime.fromisoformat(due_date.replace("Z", "+00:00"))
            except ValueError:
                raise SuperOpsValidationError("Invalid due_date format. Use ISO format.")

        return validated

    def _validate_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data for ticket updates."""
        validated = data.copy()

        # Validate status if provided
        status = validated.get("status")
        if status and status not in [s.value for s in TicketStatus]:
            raise SuperOpsValidationError(f"Invalid ticket status: {status}")

        # Validate priority if provided
        priority = validated.get("priority")
        if priority and priority not in [p.value for p in TicketPriority]:
            raise SuperOpsValidationError(f"Invalid ticket priority: {priority}")

        # Validate due_date format if provided
        due_date = validated.get("due_date")
        if due_date and isinstance(due_date, str):
            try:
                datetime.fromisoformat(due_date.replace("Z", "+00:00"))
            except ValueError:
                raise SuperOpsValidationError("Invalid due_date format. Use ISO format.")

        return validated
