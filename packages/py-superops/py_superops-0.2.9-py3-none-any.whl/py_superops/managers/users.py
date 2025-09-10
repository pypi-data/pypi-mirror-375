# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""User manager for SuperOps API operations."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..exceptions import SuperOpsAPIError, SuperOpsResourceNotFoundError, SuperOpsValidationError
from ..graphql.types import User, UserRole, UserStatus
from .base import ResourceManager

if TYPE_CHECKING:
    from ..client import SuperOpsClient


class UsersManager(ResourceManager[User]):
    """Manager for user operations.

    Provides high-level methods for managing SuperOps users including
    CRUD operations, role management, status updates, and user-specific
    filtering and search capabilities.
    """

    def __init__(self, client: SuperOpsClient):
        """Initialize the users manager.

        Args:
            client: SuperOps client instance
        """
        super().__init__(client, User, "user")

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email address.

        Args:
            email: Email address to search for

        Returns:
            User instance or None if not found

        Raises:
            SuperOpsValidationError: If email is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not email or not isinstance(email, str):
            raise SuperOpsValidationError("Email must be a non-empty string")

        if "@" not in email:
            raise SuperOpsValidationError("Invalid email format")

        self.logger.debug(f"Getting user by email: {email}")

        # Use search with exact email match
        search_query = f'email:"{email}"'
        results = await self.search(search_query, page_size=1)

        # Return first exact match if any
        for user in results["items"]:
            if user.email.lower() == email.lower():
                return user

        return None

    async def get_users_by_role(
        self,
        role: UserRole,
        status: Optional[UserStatus] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get users filtered by role.

        Args:
            role: User role to filter by
            status: Optional user status filter
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: lastName, firstName)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[User]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If role is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not isinstance(role, UserRole):
            raise SuperOpsValidationError("Role must be a UserRole enum")

        self.logger.debug(f"Getting users with role: {role.value}")

        filters = {"role": role.value}
        if status:
            if not isinstance(status, UserStatus):
                raise SuperOpsValidationError("Status must be a UserStatus enum")
            filters["status"] = status.value

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "lastName",
            sort_order=sort_order,
        )

    async def get_active_users(
        self,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get all active users.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: lastName, firstName)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[User]) and 'pagination' info

        Raises:
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Getting active users")

        filters = {"status": UserStatus.ACTIVE.value}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "lastName",
            sort_order=sort_order,
        )

    async def get_technicians(
        self,
        status: Optional[UserStatus] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get users who are technicians.

        Args:
            status: Optional user status filter
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: lastName, firstName)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[User]) and 'pagination' info

        Raises:
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Getting technician users")

        filters = {"is_technician": True}
        if status:
            if not isinstance(status, UserStatus):
                raise SuperOpsValidationError("Status must be a UserStatus enum")
            filters["status"] = status.value

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "lastName",
            sort_order=sort_order,
        )

    async def get_users_by_department(
        self,
        department: str,
        status: Optional[UserStatus] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get users filtered by department.

        Args:
            department: Department name to filter by
            status: Optional user status filter
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: lastName, firstName)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[User]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If department is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not department or not isinstance(department, str):
            raise SuperOpsValidationError("Department must be a non-empty string")

        self.logger.debug(f"Getting users in department: {department}")

        filters = {"department": department}
        if status:
            if not isinstance(status, UserStatus):
                raise SuperOpsValidationError("Status must be a UserStatus enum")
            filters["status"] = status.value

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "lastName",
            sort_order=sort_order,
        )

    async def change_user_status(self, user_id: str, new_status: UserStatus) -> User:
        """Change a user's status.

        Args:
            user_id: User ID
            new_status: New status to set

        Returns:
            Updated user instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsResourceNotFoundError: If user is not found
            SuperOpsAPIError: If the API request fails
        """
        if not user_id or not isinstance(user_id, str):
            raise SuperOpsValidationError(f"Invalid user ID: {user_id}")

        if not isinstance(new_status, UserStatus):
            raise SuperOpsValidationError("Status must be a UserStatus enum")

        self.logger.debug(f"Changing user {user_id} status to: {new_status.value}")

        # Get current user to preserve other fields
        current_user = await self.get(user_id)
        if not current_user:
            raise SuperOpsResourceNotFoundError(f"User {user_id} not found")

        # Update only the status
        update_data = {
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "role": current_user.role,
            "status": new_status,
        }

        return await self.update(user_id, update_data)

    async def assign_role(self, user_id: str, new_role: UserRole) -> User:
        """Assign a new role to a user.

        Args:
            user_id: User ID
            new_role: New role to assign

        Returns:
            Updated user instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsResourceNotFoundError: If user is not found
            SuperOpsAPIError: If the API request fails
        """
        if not user_id or not isinstance(user_id, str):
            raise SuperOpsValidationError(f"Invalid user ID: {user_id}")

        if not isinstance(new_role, UserRole):
            raise SuperOpsValidationError("Role must be a UserRole enum")

        self.logger.debug(f"Assigning role {new_role.value} to user {user_id}")

        # Get current user to preserve other fields
        current_user = await self.get(user_id)
        if not current_user:
            raise SuperOpsResourceNotFoundError(f"User {user_id} not found")

        # Update only the role
        update_data = {
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "role": new_role,
            "status": current_user.status,
        }

        return await self.update(user_id, update_data)

    async def search_users(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Search users with advanced filtering.

        Args:
            query: Search query (searches name, email)
            filters: Optional additional filters
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: lastName, firstName)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[User]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not query or not isinstance(query, str):
            raise SuperOpsValidationError("Query must be a non-empty string")

        self.logger.debug(f"Searching users with query: {query}")

        # Build search query for name and email
        search_query = f'(firstName:"{query}" OR lastName:"{query}" OR email:"{query}")'

        # Add additional filters if provided
        if filters:
            for key, value in filters.items():
                if value is not None:
                    if isinstance(value, (UserRole, UserStatus)):
                        search_query += f' {key}:"{value.value}"'
                    else:
                        search_query += f' {key}:"{value}"'

        return await self.search(
            search_query,
            page=page,
            page_size=page_size,
            sort_by=sort_by or "lastName",
            sort_order=sort_order,
        )

    async def get_recently_logged_in_users(
        self,
        days: int = 7,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        """Get users who have logged in recently.

        Args:
            days: Number of days to look back (default: 7)
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            Dictionary containing 'items' (List[User]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If days is invalid
            SuperOpsAPIError: If the API request fails
        """
        if days <= 0:
            raise SuperOpsValidationError("Days must be a positive integer")

        self.logger.debug(f"Getting users who logged in within {days} days")

        # Calculate date threshold
        cutoff_date = datetime.now() - timedelta(days=days)
        
        filters = {
            "last_login_after": cutoff_date,
            "status": UserStatus.ACTIVE.value,
        }

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by="lastLoginTime",
            sort_order="desc",
        )

    async def bulk_update_status(
        self, user_ids: List[str], new_status: UserStatus
    ) -> List[User]:
        """Update status for multiple users.

        Args:
            user_ids: List of user IDs to update
            new_status: New status to set for all users

        Returns:
            List of updated user instances

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not user_ids or not isinstance(user_ids, list):
            raise SuperOpsValidationError("user_ids must be a non-empty list")

        if not isinstance(new_status, UserStatus):
            raise SuperOpsValidationError("Status must be a UserStatus enum")

        self.logger.debug(f"Bulk updating status for {len(user_ids)} users to {new_status.value}")

        updated_users = []
        for user_id in user_ids:
            try:
                updated_user = await self.change_user_status(user_id, new_status)
                updated_users.append(updated_user)
            except Exception as e:
                self.logger.warning(f"Failed to update user {user_id}: {e}")
                # Continue with other users instead of failing completely

        return updated_users

    # Abstract method implementations

    def _build_get_query(self, **kwargs) -> str:
        """Build GraphQL query for getting a single user."""
        return """
            query GetUser($id: ID!) {
                user(id: $id) {
                    ...UserFullFields
                }
            }
            
            fragment UserFullFields on User {
                id
                email
                firstName
                lastName
                role
                status
                department
                phone
                mobile
                jobTitle
                isTechnician
                hourlyRate
                lastLoginTime
                lastLogin
                timezone
                language
                avatarUrl
                isPrimary
                isActiveSession
                employeeId
                hireDate
                managerId
                notificationPreferences
                permissions
                tags
                customFields
                createdAt
                updatedAt
            }
        """

    def _build_list_query(self, **kwargs) -> str:
        """Build GraphQL query for listing users."""
        return """
            query ListUsers($page: Int, $pageSize: Int, $filters: UserFilter, $sortBy: String, $sortOrder: SortDirection) {
                users(page: $page, pageSize: $pageSize, filters: $filters, sortBy: $sortBy, sortOrder: $sortOrder) {
                    items {
                        ...UserCoreFields
                    }
                    pagination {
                        ...PaginationInfo
                    }
                }
            }
            
            fragment UserCoreFields on User {
                id
                email
                firstName
                lastName
                role
                status
                department
                jobTitle
                isTechnician
                avatarUrl
                createdAt
                updatedAt
            }
            
            fragment PaginationInfo on PaginationInfo {
                page
                pageSize
                total
                hasNextPage
                hasPreviousPage
            }
        """

    def _build_create_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for creating a user."""
        return """
            mutation CreateUser($input: UserInput!) {
                createUser(input: $input) {
                    ...UserFullFields
                }
            }
            
            fragment UserFullFields on User {
                id
                email
                firstName
                lastName
                role
                status
                department
                phone
                mobile
                jobTitle
                isTechnician
                hourlyRate
                lastLoginTime
                lastLogin
                timezone
                language
                avatarUrl
                isPrimary
                isActiveSession
                employeeId
                hireDate
                managerId
                notificationPreferences
                permissions
                tags
                customFields
                createdAt
                updatedAt
            }
        """

    def _build_update_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for updating a user."""
        return """
            mutation UpdateUser($id: ID!, $input: UserInput!) {
                updateUser(id: $id, input: $input) {
                    ...UserFullFields
                }
            }
            
            fragment UserFullFields on User {
                id
                email
                firstName
                lastName
                role
                status
                department
                phone
                mobile
                jobTitle
                isTechnician
                hourlyRate
                lastLoginTime
                lastLogin
                timezone
                language
                avatarUrl
                isPrimary
                isActiveSession
                employeeId
                hireDate
                managerId
                notificationPreferences
                permissions
                tags
                customFields
                createdAt
                updatedAt
            }
        """

    def _build_delete_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for deleting a user."""
        return """
            mutation DeleteUser($id: ID!) {
                deleteUser(id: $id) {
                    success
                    message
                }
            }
        """

    def _build_search_query(self, **kwargs) -> str:
        """Build GraphQL query for searching users."""
        return """
            query SearchUsers($query: String!, $page: Int, $pageSize: Int) {
                searchUsers(query: $query, page: $page, pageSize: $pageSize) {
                    items {
                        ...UserCoreFields
                    }
                    pagination {
                        ...PaginationInfo
                    }
                }
            }
            
            fragment UserCoreFields on User {
                id
                email
                firstName
                lastName
                role
                status
                department
                jobTitle
                isTechnician
                avatarUrl
                createdAt
                updatedAt
            }
            
            fragment PaginationInfo on PaginationInfo {
                page
                pageSize
                total
                hasNextPage
                hasPreviousPage
            }
        """