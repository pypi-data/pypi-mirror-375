# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Tests for UsersManager class."""

from datetime import datetime, timezone
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from py_superops.exceptions import (
    SuperOpsAPIError,
    SuperOpsResourceNotFoundError,
    SuperOpsValidationError,
)
from py_superops.graphql.types import UserRole, UserStatus
from py_superops.managers import UsersManager


class TestUsersManager:
    """Test the UsersManager class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock SuperOps client."""
        client = AsyncMock()
        client.execute_query = AsyncMock()
        client.execute_mutation = AsyncMock()
        return client

    @pytest.fixture
    def users_manager(self, mock_client):
        """Create a UsersManager instance."""
        return UsersManager(mock_client)

    @pytest.fixture
    def sample_user_response(self) -> Dict[str, Any]:
        """Sample user response data."""
        return {
            "data": {
                "user": {
                    "id": "user-123",
                    "email": "john.doe@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "role": "TECHNICIAN",
                    "status": "ACTIVE",
                    "department": "IT Support",
                    "job_title": "Senior Technician",
                    "is_technician": True,
                    "phone": "+1-555-123-4567",
                    "mobile": "+1-555-987-6543",
                    "timezone": "America/New_York",
                    "language": "en-US",
                    "avatar_url": "https://example.com/avatar.jpg",
                    "last_login": "2024-01-15T14:30:00Z",
                    "is_active_session": True,
                    "employee_id": "EMP001",
                    "hire_date": "2023-01-15",
                    "manager_id": "user-456",
                    "created_at": "2023-01-15T08:00:00Z",
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }

    @pytest.fixture
    def sample_user_list_response(self) -> Dict[str, Any]:
        """Sample user list response data."""
        return {
            "data": {
                "users": {
                    "items": [
                        {
                            "id": "user-1",
                            "email": "alice@example.com",
                            "first_name": "Alice",
                            "last_name": "Smith",
                            "role": "ADMIN",
                            "status": "ACTIVE",
                            "department": "Administration",
                            "job_title": "System Administrator",
                            "is_technician": False,
                            "phone": "+1-555-111-1111",
                            "created_at": "2023-01-01T08:00:00Z",
                            "updated_at": "2024-01-01T08:00:00Z",
                        },
                        {
                            "id": "user-2",
                            "email": "bob@example.com",
                            "first_name": "Bob",
                            "last_name": "Johnson",
                            "role": "TECHNICIAN",
                            "status": "ACTIVE",
                            "department": "IT Support",
                            "job_title": "Technician",
                            "is_technician": True,
                            "phone": "+1-555-222-2222",
                            "created_at": "2023-02-01T08:00:00Z",
                            "updated_at": "2024-01-02T08:00:00Z",
                        },
                    ],
                    "pagination": {
                        "page": 1,
                        "pageSize": 50,
                        "total": 2,
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                    },
                }
            }
        }

    @pytest.fixture
    def sample_create_user_data(self) -> Dict[str, Any]:
        """Sample data for creating a user."""
        return {
            "email": "newuser@example.com",
            "first_name": "Jane",
            "last_name": "Wilson",
            "role": UserRole.TECHNICIAN,
            "department": "IT Support",
            "job_title": "Junior Technician",
            "phone": "+1-555-333-3333",
            "timezone": "America/Chicago",
            "language": "en-US",
        }

    @pytest.fixture
    def sample_update_user_data(self) -> Dict[str, Any]:
        """Sample data for updating a user."""
        return {
            "first_name": "John Updated",
            "last_name": "Doe Updated",
            "job_title": "Lead Technician",
            "department": "Advanced Support",
            "phone": "+1-555-999-9999",
            "status": UserStatus.ACTIVE,
        }

    # Test CRUD Operations

    @pytest.mark.asyncio
    async def test_get_user_success(self, users_manager, mock_client, sample_user_response):
        """Test successful user retrieval."""
        mock_client.execute_query.return_value = sample_user_response

        result = await users_manager.get("user-123")

        assert result is not None
        assert result.id == "user-123"
        assert result.email == "john.doe@example.com"
        assert result.first_name == "John"
        assert result.last_name == "Doe"
        assert result.role == UserRole.TECHNICIAN
        assert result.status == UserStatus.ACTIVE

        mock_client.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, users_manager, mock_client):
        """Test user not found scenario."""
        mock_client.execute_query.return_value = {"data": {"user": None}}

        result = await users_manager.get("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_invalid_id(self, users_manager):
        """Test get with invalid user ID."""
        with pytest.raises(SuperOpsValidationError, match="Invalid resource ID"):
            await users_manager.get("")

        with pytest.raises(SuperOpsValidationError, match="Invalid resource ID"):
            await users_manager.get(None)

    @pytest.mark.asyncio
    async def test_list_all_users_success(
        self, users_manager, mock_client, sample_user_list_response
    ):
        """Test successful user listing."""
        mock_client.execute_query.return_value = sample_user_list_response

        result = await users_manager.list()

        assert "items" in result
        assert "pagination" in result
        assert len(result["items"]) == 2
        assert result["items"][0].id == "user-1"
        assert result["items"][1].id == "user-2"

        mock_client.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_all_users_with_filters(
        self, users_manager, mock_client, sample_user_list_response
    ):
        """Test user listing with filters."""
        mock_client.execute_query.return_value = sample_user_list_response

        filters = {
            "role": UserRole.TECHNICIAN,
            "status": UserStatus.ACTIVE,
            "department": "IT Support",
            "is_technician": True,
        }

        result = await users_manager.list(page=2, page_size=25, filters=filters)

        assert len(result["items"]) == 2

        # Verify query parameters were passed correctly
        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["page"] == 2
        assert variables["pageSize"] == 25
        assert variables["filters"]["role"] == UserRole.TECHNICIAN
        assert variables["filters"]["status"] == UserStatus.ACTIVE
        assert variables["filters"]["department"] == "IT Support"
        assert variables["filters"]["is_technician"] is True

    @pytest.mark.asyncio
    async def test_create_user_success(self, users_manager, mock_client, sample_create_user_data):
        """Test successful user creation."""
        created_user = {
            "data": {
                "createUser": {
                    "id": "user-new-123",
                    "email": "newuser@example.com",
                    "first_name": "Jane",
                    "last_name": "Wilson",
                    "role": "TECHNICIAN",
                    "status": "ACTIVE",
                    "department": "IT Support",
                    "job_title": "Junior Technician",
                    "is_technician": True,
                    "phone": "+1-555-333-3333",
                    "timezone": "America/Chicago",
                    "language": "en-US",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = created_user

        result = await users_manager.create(sample_create_user_data)

        assert result.id == "user-new-123"
        assert result.email == "newuser@example.com"
        assert result.role == UserRole.TECHNICIAN

        mock_client.execute_mutation.assert_called_once()
        call_args = mock_client.execute_mutation.call_args
        assert "createUser" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_create_user_validation_error(self, users_manager):
        """Test user creation with invalid data."""
        with pytest.raises(SuperOpsValidationError):
            await users_manager.create(email="", first_name="Test")

        with pytest.raises(SuperOpsValidationError):
            await users_manager.create(email=None, first_name="Test")

        with pytest.raises(SuperOpsValidationError):
            await users_manager.create(email="invalid-email", first_name="Test")

    @pytest.mark.asyncio
    async def test_update_user_success(self, users_manager, mock_client, sample_update_user_data):
        """Test successful user update."""
        updated_user = {
            "data": {
                "updateUser": {
                    "id": "user-123",
                    "first_name": "John Updated",
                    "last_name": "Doe Updated",
                    "job_title": "Lead Technician",
                    "department": "Advanced Support",
                    "phone": "+1-555-999-9999",
                    "status": "ACTIVE",
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = updated_user

        result = await users_manager.update("user-123", **sample_update_user_data)

        assert result.id == "user-123"
        assert result.first_name == "John Updated"
        assert result.job_title == "Lead Technician"

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user_success(self, users_manager, mock_client):
        """Test successful user deletion."""
        delete_response = {
            "data": {"deleteUser": {"success": True, "message": "User deleted successfully"}}
        }
        mock_client.execute_mutation.return_value = delete_response

        result = await users_manager.delete("user-123")

        assert result is True

        mock_client.execute_mutation.assert_called_once()
        call_args = mock_client.execute_mutation.call_args
        assert call_args[0][1]["id"] == "user-123"

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, users_manager, mock_client):
        """Test deleting non-existent user."""
        delete_response = {"data": {"deleteUser": {"success": False, "message": "User not found"}}}
        mock_client.execute_mutation.return_value = delete_response

        result = await users_manager.delete("nonexistent")

        assert result is False

    # Test User-Specific Methods

    @pytest.mark.asyncio
    async def test_get_by_email_success(self, users_manager, mock_client, sample_user_response):
        """Test successful user retrieval by email."""
        mock_client.execute_query.return_value = sample_user_response

        result = await users_manager.get_by_email("john.doe@example.com")

        assert result is not None
        assert result.email == "john.doe@example.com"

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["email"] == "john.doe@example.com"

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, users_manager, mock_client):
        """Test user not found by email."""
        mock_client.execute_query.return_value = {"data": {"users": {"items": []}}}

        result = await users_manager.get_by_email("nonexistent@example.com")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_email_invalid_email(self, users_manager):
        """Test get by email with invalid email."""
        with pytest.raises(SuperOpsValidationError, match="Invalid email format"):
            await users_manager.get_by_email("invalid-email")

        with pytest.raises(SuperOpsValidationError, match="Email cannot be empty"):
            await users_manager.get_by_email("")

    @pytest.mark.asyncio
    async def test_get_users_by_role(self, users_manager, mock_client, sample_user_list_response):
        """Test getting users by role."""
        mock_client.execute_query.return_value = sample_user_list_response

        result = await users_manager.get_users_by_role(UserRole.TECHNICIAN)

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["role"] == UserRole.TECHNICIAN

    @pytest.mark.asyncio
    async def test_get_active_users(self, users_manager, mock_client, sample_user_list_response):
        """Test getting active users."""
        mock_client.execute_query.return_value = sample_user_list_response

        result = await users_manager.get_active_users()

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["status"] == UserStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_get_technicians(self, users_manager, mock_client, sample_user_list_response):
        """Test getting technician users."""
        mock_client.execute_query.return_value = sample_user_list_response

        result = await users_manager.get_technicians()

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["is_technician"] is True

    @pytest.mark.asyncio
    async def test_get_users_by_department(self, users_manager, mock_client, sample_user_list_response):
        """Test getting users by department."""
        mock_client.execute_query.return_value = sample_user_list_response

        result = await users_manager.get_users_by_department("IT Support")

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["department"] == "IT Support"

    @pytest.mark.asyncio
    async def test_get_users_by_department_empty(self, users_manager):
        """Test get users by department with empty department."""
        with pytest.raises(SuperOpsValidationError, match="Department cannot be empty"):
            await users_manager.get_users_by_department("")

    @pytest.mark.asyncio
    async def test_search_users_by_name(self, users_manager, mock_client, sample_user_list_response):
        """Test searching users by name."""
        mock_client.execute_query.return_value = sample_user_list_response

        result = await users_manager.search_users_by_name("John")

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert "search_term" in variables["filters"]

    @pytest.mark.asyncio
    async def test_search_users_by_name_empty(self, users_manager):
        """Test search users by name with empty search term."""
        with pytest.raises(SuperOpsValidationError, match="Search term cannot be empty"):
            await users_manager.search_users_by_name("")

    # Test User Status Management

    @pytest.mark.asyncio
    async def test_change_user_status_success(self, users_manager, mock_client):
        """Test successful user status change."""
        update_response = {
            "data": {
                "updateUser": {
                    "id": "user-123",
                    "status": "INACTIVE",
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = update_response

        result = await users_manager.change_user_status("user-123", UserStatus.INACTIVE)

        assert result.status == UserStatus.INACTIVE

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_activate_user_success(self, users_manager, mock_client):
        """Test successful user activation."""
        update_response = {
            "data": {
                "updateUser": {
                    "id": "user-123",
                    "status": "ACTIVE",
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = update_response

        result = await users_manager.activate_user("user-123")

        assert result.status == UserStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_deactivate_user_success(self, users_manager, mock_client):
        """Test successful user deactivation."""
        update_response = {
            "data": {
                "updateUser": {
                    "id": "user-123",
                    "status": "INACTIVE",
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = update_response

        result = await users_manager.deactivate_user("user-123")

        assert result.status == UserStatus.INACTIVE

    @pytest.mark.asyncio
    async def test_suspend_user_success(self, users_manager, mock_client):
        """Test successful user suspension."""
        update_response = {
            "data": {
                "updateUser": {
                    "id": "user-123",
                    "status": "SUSPENDED",
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = update_response

        result = await users_manager.suspend_user("user-123")

        assert result.status == UserStatus.SUSPENDED

    # Test Role Management

    @pytest.mark.asyncio
    async def test_change_user_role_success(self, users_manager, mock_client):
        """Test successful user role change."""
        update_response = {
            "data": {
                "updateUser": {
                    "id": "user-123",
                    "role": "ADMIN",
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = update_response

        result = await users_manager.change_user_role("user-123", UserRole.ADMIN)

        assert result.role == UserRole.ADMIN

    @pytest.mark.asyncio
    async def test_promote_to_admin_success(self, users_manager, mock_client):
        """Test successful promotion to admin."""
        update_response = {
            "data": {
                "updateUser": {
                    "id": "user-123",
                    "role": "ADMIN",
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = update_response

        result = await users_manager.promote_to_admin("user-123")

        assert result.role == UserRole.ADMIN

    @pytest.mark.asyncio
    async def test_assign_technician_role_success(self, users_manager, mock_client):
        """Test successful technician role assignment."""
        update_response = {
            "data": {
                "updateUser": {
                    "id": "user-123",
                    "role": "TECHNICIAN",
                    "is_technician": True,
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = update_response

        result = await users_manager.assign_technician_role("user-123")

        assert result.role == UserRole.TECHNICIAN
        assert result.is_technician is True

    # Test User Profile Management

    @pytest.mark.asyncio
    async def test_update_user_profile_success(self, users_manager, mock_client):
        """Test successful user profile update."""
        update_response = {
            "data": {
                "updateUser": {
                    "id": "user-123",
                    "first_name": "John",
                    "last_name": "Smith",
                    "job_title": "Senior Developer",
                    "phone": "+1-555-999-8888",
                    "timezone": "America/Los_Angeles",
                    "language": "en-US",
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = update_response

        profile_data = {
            "first_name": "John",
            "last_name": "Smith",
            "job_title": "Senior Developer",
            "phone": "+1-555-999-8888",
            "timezone": "America/Los_Angeles",
            "language": "en-US",
        }

        result = await users_manager.update_user_profile("user-123", **profile_data)

        assert result.first_name == "John"
        assert result.job_title == "Senior Developer"
        assert result.phone == "+1-555-999-8888"

    @pytest.mark.asyncio
    async def test_update_user_avatar_success(self, users_manager, mock_client):
        """Test successful user avatar update."""
        update_response = {
            "data": {
                "updateUser": {
                    "id": "user-123",
                    "avatar_url": "https://example.com/new-avatar.jpg",
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = update_response

        result = await users_manager.update_user_avatar("user-123", "https://example.com/new-avatar.jpg")

        assert result.avatar_url == "https://example.com/new-avatar.jpg"

    @pytest.mark.asyncio
    async def test_update_user_avatar_invalid_url(self, users_manager):
        """Test update user avatar with invalid URL."""
        with pytest.raises(SuperOpsValidationError, match="Invalid avatar URL"):
            await users_manager.update_user_avatar("user-123", "not-a-url")

        with pytest.raises(SuperOpsValidationError, match="Avatar URL cannot be empty"):
            await users_manager.update_user_avatar("user-123", "")

    # Test User Statistics

    @pytest.mark.asyncio
    async def test_get_user_statistics_success(self, users_manager, mock_client):
        """Test getting user statistics."""
        stats_response = {
            "data": {
                "userStatistics": {
                    "total_users": 25,
                    "active_users": 22,
                    "inactive_users": 2,
                    "suspended_users": 1,
                    "users_by_role": {
                        "ADMIN": 2,
                        "TECHNICIAN": 15,
                        "USER": 5,
                        "MANAGER": 2,
                        "READONLY": 1,
                    },
                    "users_by_department": {
                        "IT Support": 18,
                        "Administration": 3,
                        "Management": 2,
                        "Finance": 2,
                    },
                    "technician_count": 15,
                    "recently_active_count": 20,
                }
            }
        }
        mock_client.execute_query.return_value = stats_response

        result = await users_manager.get_user_statistics()

        assert result["total_users"] == 25
        assert result["active_users"] == 22
        assert result["users_by_role"]["TECHNICIAN"] == 15
        assert result["technician_count"] == 15

    @pytest.mark.asyncio
    async def test_get_recently_active_users(self, users_manager, mock_client, sample_user_list_response):
        """Test getting recently active users."""
        mock_client.execute_query.return_value = sample_user_list_response

        result = await users_manager.get_recently_active_users(days=7)

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert "last_login_after" in variables["filters"]

    @pytest.mark.asyncio
    async def test_get_inactive_users(self, users_manager, mock_client, sample_user_list_response):
        """Test getting inactive users."""
        mock_client.execute_query.return_value = sample_user_list_response

        result = await users_manager.get_inactive_users(days=30)

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert "last_login_before" in variables["filters"]

    # Test Batch Operations

    @pytest.mark.asyncio
    async def test_bulk_update_users_success(self, users_manager, mock_client):
        """Test successful bulk user update."""
        bulk_update_response = {
            "data": {
                "bulkUpdateUsers": {
                    "success": True,
                    "updated_count": 3,
                    "message": "3 users updated successfully",
                }
            }
        }
        mock_client.execute_mutation.return_value = bulk_update_response

        user_ids = ["user-1", "user-2", "user-3"]
        updates = {"status": UserStatus.ACTIVE, "department": "IT Support"}

        result = await users_manager.bulk_update_users(user_ids, **updates)

        assert result["success"] is True
        assert result["updated_count"] == 3

    @pytest.mark.asyncio
    async def test_bulk_change_status_success(self, users_manager, mock_client):
        """Test successful bulk status change."""
        bulk_update_response = {
            "data": {
                "bulkUpdateUsers": {
                    "success": True,
                    "updated_count": 2,
                    "message": "2 users updated successfully",
                }
            }
        }
        mock_client.execute_mutation.return_value = bulk_update_response

        user_ids = ["user-1", "user-2"]

        result = await users_manager.bulk_change_status(user_ids, UserStatus.SUSPENDED)

        assert result["success"] is True
        assert result["updated_count"] == 2

    @pytest.mark.asyncio
    async def test_bulk_assign_role_success(self, users_manager, mock_client):
        """Test successful bulk role assignment."""
        bulk_update_response = {
            "data": {
                "bulkUpdateUsers": {
                    "success": True,
                    "updated_count": 4,
                    "message": "4 users updated successfully",
                }
            }
        }
        mock_client.execute_mutation.return_value = bulk_update_response

        user_ids = ["user-1", "user-2", "user-3", "user-4"]

        result = await users_manager.bulk_assign_role(user_ids, UserRole.TECHNICIAN)

        assert result["success"] is True
        assert result["updated_count"] == 4

    # Test Password Management

    @pytest.mark.asyncio
    async def test_reset_user_password_success(self, users_manager, mock_client):
        """Test successful password reset."""
        reset_response = {
            "data": {
                "resetUserPassword": {
                    "success": True,
                    "message": "Password reset email sent",
                    "reset_token_expires": "2024-01-16T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = reset_response

        result = await users_manager.reset_user_password("user-123", notify_user=True)

        assert result["success"] is True
        assert "reset_token_expires" in result

    @pytest.mark.asyncio
    async def test_change_user_password_success(self, users_manager, mock_client):
        """Test successful password change."""
        change_response = {
            "data": {
                "changeUserPassword": {
                    "success": True,
                    "message": "Password changed successfully",
                }
            }
        }
        mock_client.execute_mutation.return_value = change_response

        result = await users_manager.change_user_password("user-123", "new_password123")

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_change_user_password_invalid(self, users_manager):
        """Test change password with invalid data."""
        with pytest.raises(SuperOpsValidationError, match="Password cannot be empty"):
            await users_manager.change_user_password("user-123", "")

        with pytest.raises(SuperOpsValidationError, match="Password must be at least 8 characters"):
            await users_manager.change_user_password("user-123", "short")

    # Test Error Handling

    @pytest.mark.asyncio
    async def test_get_user_api_error(self, users_manager, mock_client):
        """Test API error handling in get_user."""
        mock_client.execute_query.side_effect = SuperOpsAPIError("API Error")

        with pytest.raises(SuperOpsAPIError):
            await users_manager.get("user-123")

    @pytest.mark.asyncio
    async def test_create_user_validation_error_empty_data(self, users_manager):
        """Test validation error for empty user data."""
        with pytest.raises(SuperOpsValidationError):
            await users_manager.create()

    @pytest.mark.asyncio
    async def test_update_user_invalid_id(self, users_manager):
        """Test update user with invalid ID."""
        with pytest.raises(SuperOpsValidationError, match="User ID cannot be empty"):
            await users_manager.update("", first_name="Updated Name")

    @pytest.mark.asyncio
    async def test_change_user_status_invalid_user_id(self, users_manager):
        """Test change status with invalid user ID."""
        with pytest.raises(SuperOpsValidationError, match="User ID cannot be empty"):
            await users_manager.change_user_status("", UserStatus.ACTIVE)

    @pytest.mark.asyncio
    async def test_change_user_role_invalid_user_id(self, users_manager):
        """Test change role with invalid user ID."""
        with pytest.raises(SuperOpsValidationError, match="User ID cannot be empty"):
            await users_manager.change_user_role("", UserRole.ADMIN)

    @pytest.mark.asyncio
    async def test_bulk_operations_empty_user_list(self, users_manager):
        """Test bulk operations with empty user list."""
        with pytest.raises(SuperOpsValidationError, match="User IDs list cannot be empty"):
            await users_manager.bulk_update_users([], status=UserStatus.ACTIVE)

        with pytest.raises(SuperOpsValidationError, match="User IDs list cannot be empty"):
            await users_manager.bulk_change_status([], UserStatus.ACTIVE)

        with pytest.raises(SuperOpsValidationError, match="User IDs list cannot be empty"):
            await users_manager.bulk_assign_role([], UserRole.TECHNICIAN)

    # Test User Session Management

    @pytest.mark.asyncio
    async def test_get_user_sessions_success(self, users_manager, mock_client):
        """Test getting user active sessions."""
        sessions_response = {
            "data": {
                "userSessions": {
                    "items": [
                        {
                            "id": "session-1",
                            "user_id": "user-123",
                            "device_type": "desktop",
                            "browser": "Chrome",
                            "ip_address": "192.168.1.100",
                            "location": "New York, NY",
                            "is_active": True,
                            "last_activity": "2024-01-15T14:30:00Z",
                            "created_at": "2024-01-15T08:00:00Z",
                        },
                        {
                            "id": "session-2",
                            "user_id": "user-123",
                            "device_type": "mobile",
                            "browser": "Safari",
                            "ip_address": "10.0.0.50",
                            "location": "New York, NY",
                            "is_active": True,
                            "last_activity": "2024-01-15T13:45:00Z",
                            "created_at": "2024-01-15T13:00:00Z",
                        },
                    ],
                    "pagination": {
                        "page": 1,
                        "pageSize": 50,
                        "total": 2,
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                    },
                }
            }
        }
        mock_client.execute_query.return_value = sessions_response

        result = await users_manager.get_user_sessions("user-123")

        assert len(result["items"]) == 2
        assert result["items"][0]["device_type"] == "desktop"
        assert result["items"][1]["device_type"] == "mobile"

    @pytest.mark.asyncio
    async def test_terminate_user_sessions_success(self, users_manager, mock_client):
        """Test terminating user sessions."""
        terminate_response = {
            "data": {
                "terminateUserSessions": {
                    "success": True,
                    "terminated_count": 3,
                    "message": "3 sessions terminated successfully",
                }
            }
        }
        mock_client.execute_mutation.return_value = terminate_response

        result = await users_manager.terminate_user_sessions("user-123")

        assert result["success"] is True
        assert result["terminated_count"] == 3

    @pytest.mark.asyncio
    async def test_terminate_user_session_success(self, users_manager, mock_client):
        """Test terminating a specific user session."""
        terminate_response = {
            "data": {
                "terminateUserSession": {
                    "success": True,
                    "message": "Session terminated successfully",
                }
            }
        }
        mock_client.execute_mutation.return_value = terminate_response

        result = await users_manager.terminate_user_session("user-123", "session-456")

        assert result["success"] is True