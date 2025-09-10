# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Tests for TasksManager class."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from py_superops.exceptions import (
    SuperOpsAPIError,
    SuperOpsResourceNotFoundError,
    SuperOpsValidationError,
)
from py_superops.graphql.types import TaskPriority, TaskRecurrenceType, TaskStatus
from py_superops.managers import TasksManager


class TestTasksManager:
    """Test the TasksManager class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock SuperOps client."""
        client = AsyncMock()
        client.execute_query = AsyncMock()
        client.execute_mutation = AsyncMock()
        return client

    @pytest.fixture
    def tasks_manager(self, mock_client):
        """Create a TasksManager instance."""
        return TasksManager(mock_client)

    @pytest.fixture
    def sample_task_response(self) -> Dict[str, Any]:
        """Sample task response data."""
        return {
            "data": {
                "task": {
                    "id": "task-123",
                    "title": "Sample Task",
                    "description": "This is a sample task for testing",
                    "status": "NEW",
                    "priority": "NORMAL",
                    "project_id": "project-456",
                    "assigned_to": "user-789",
                    "assigned_to_team": "team-321",
                    "creator_id": "user-111",
                    "parent_task_id": None,
                    "subtask_count": 0,
                    "due_date": "2024-12-31T23:59:59Z",
                    "start_date": "2024-01-01T00:00:00Z",
                    "completed_at": None,
                    "estimated_hours": 8.0,
                    "actual_hours": 4.0,
                    "recurrence_type": "NONE",
                    "recurrence_interval": None,
                    "recurrence_end_date": None,
                    "parent_recurring_task_id": None,
                    "time_entries_count": 2,
                    "total_time_logged": 4.0,
                    "billable_time": 4.0,
                    "labels": [],
                    "tags": ["testing", "sample"],
                    "custom_fields": {"environment": "development"},
                    "progress_percentage": 50,
                    "is_milestone": False,
                    "is_template": False,
                    "template_id": None,
                    "attachment_count": 0,
                    "comment_count": 1,
                    "overdue_alert_sent": False,
                    "reminder_sent": False,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }

    @pytest.fixture
    def sample_task_list_response(self) -> Dict[str, Any]:
        """Sample task list response data."""
        return {
            "data": {
                "tasks": {
                    "items": [
                        {
                            "id": "task-1",
                            "title": "Task 1",
                            "description": "First task",
                            "status": "NEW",
                            "priority": "HIGH",
                            "project_id": "project-456",
                            "assigned_to": "user-789",
                            "creator_id": "user-111",
                            "due_date": "2024-12-31T23:59:59Z",
                            "estimated_hours": 8.0,
                            "actual_hours": 0.0,
                            "tags": ["urgent"],
                            "created_at": "2024-01-01T00:00:00Z",
                            "updated_at": "2024-01-01T00:00:00Z",
                        },
                        {
                            "id": "task-2",
                            "title": "Task 2",
                            "description": "Second task",
                            "status": "IN_PROGRESS",
                            "priority": "NORMAL",
                            "project_id": "project-456",
                            "assigned_to": "user-789",
                            "creator_id": "user-111",
                            "due_date": "2024-11-30T23:59:59Z",
                            "estimated_hours": 4.0,
                            "actual_hours": 2.0,
                            "tags": ["development"],
                            "created_at": "2024-01-02T00:00:00Z",
                            "updated_at": "2024-01-02T00:00:00Z",
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
    def sample_create_task_data(self) -> Dict[str, Any]:
        """Sample data for creating a task."""
        return {
            "title": "New Task",
            "description": "A new task for testing",
            "project_id": "project-123",
            "assigned_to": "user-456",
            "priority": TaskPriority.HIGH,
            "due_date": "2024-12-31",
            "estimated_hours": 10.0,
            "tags": ["new", "testing"],
        }

    @pytest.fixture
    def sample_update_task_data(self) -> Dict[str, Any]:
        """Sample data for updating a task."""
        return {
            "title": "Updated Task Title",
            "description": "Updated description",
            "status": TaskStatus.IN_PROGRESS,
            "priority": TaskPriority.LOW,
            "estimated_hours": 12.0,
            "actual_hours": 6.0,
        }

    # Test CRUD Operations

    @pytest.mark.asyncio
    async def test_get_task_success(self, tasks_manager, mock_client, sample_task_response):
        """Test successful task retrieval."""
        mock_client.execute_query.return_value = sample_task_response

        result = await tasks_manager.get("task-123")

        assert result is not None
        assert result.id == "task-123"
        assert result.title == "Sample Task"
        assert result.status == TaskStatus.NEW
        assert result.priority == TaskPriority.NORMAL

        mock_client.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, tasks_manager, mock_client):
        """Test task not found scenario."""
        mock_client.execute_query.return_value = {"data": {"task": None}}

        result = await tasks_manager.get("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_task_invalid_id(self, tasks_manager):
        """Test get with invalid task ID."""
        with pytest.raises(SuperOpsValidationError, match="Invalid resource ID"):
            await tasks_manager.get("")

        with pytest.raises(SuperOpsValidationError, match="Invalid resource ID"):
            await tasks_manager.get(None)

    @pytest.mark.asyncio
    async def test_list_all_tasks_success(
        self, tasks_manager, mock_client, sample_task_list_response
    ):
        """Test successful task listing."""
        mock_client.execute_query.return_value = sample_task_list_response

        result = await tasks_manager.list()

        assert "items" in result
        assert "pagination" in result
        assert len(result["items"]) == 2
        assert result["items"][0].id == "task-1"
        assert result["items"][1].id == "task-2"

        mock_client.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_all_tasks_with_filters(
        self, tasks_manager, mock_client, sample_task_list_response
    ):
        """Test task listing with filters."""
        mock_client.execute_query.return_value = sample_task_list_response

        filters = {
            "status": TaskStatus.IN_PROGRESS,
            "priority": TaskPriority.HIGH,
            "assigned_to": "user-789",
            "project_id": "project-456",
        }

        result = await tasks_manager.list(page=2, page_size=25, filters=filters)

        assert len(result["items"]) == 2

        # Verify query parameters were passed correctly
        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["page"] == 2
        assert variables["pageSize"] == 25
        assert variables["filters"]["status"] == TaskStatus.IN_PROGRESS
        assert variables["filters"]["priority"] == TaskPriority.HIGH
        assert variables["filters"]["assigned_to"] == "user-789"
        assert variables["filters"]["project_id"] == "project-456"

    @pytest.mark.asyncio
    async def test_create_task_success(self, tasks_manager, mock_client, sample_create_task_data):
        """Test successful task creation."""
        created_task = {
            "data": {
                "createTask": {
                    "id": "task-new-123",
                    "title": "New Task",
                    "description": "A new task for testing",
                    "status": "NEW",
                    "priority": "HIGH",
                    "project_id": "project-123",
                    "assigned_to": "user-456",
                    "creator_id": "current-user",
                    "due_date": "2024-12-31T00:00:00Z",
                    "estimated_hours": 10.0,
                    "tags": ["new", "testing"],
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = created_task

        result = await tasks_manager.create(sample_create_task_data)

        assert result.id == "task-new-123"
        assert result.title == "New Task"
        assert result.priority == TaskPriority.HIGH

        mock_client.execute_mutation.assert_called_once()
        call_args = mock_client.execute_mutation.call_args
        assert "createTask" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_create_task_validation_error(self, tasks_manager):
        """Test task creation with invalid data."""
        with pytest.raises(SuperOpsValidationError):
            await tasks_manager.create(title="", description="Test")

        with pytest.raises(SuperOpsValidationError):
            await tasks_manager.create(title=None, description="Test")

    @pytest.mark.asyncio
    async def test_update_task_success(self, tasks_manager, mock_client, sample_update_task_data):
        """Test successful task update."""
        updated_task = {
            "data": {
                "updateTask": {
                    "id": "task-123",
                    "title": "Updated Task Title",
                    "description": "Updated description",
                    "status": "IN_PROGRESS",
                    "priority": "LOW",
                    "estimated_hours": 12.0,
                    "actual_hours": 6.0,
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = updated_task

        result = await tasks_manager.update("task-123", **sample_update_task_data)

        assert result.id == "task-123"
        assert result.title == "Updated Task Title"
        assert result.status == TaskStatus.IN_PROGRESS

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_task_success(self, tasks_manager, mock_client):
        """Test successful task deletion."""
        delete_response = {
            "data": {"deleteTask": {"success": True, "message": "Task deleted successfully"}}
        }
        mock_client.execute_mutation.return_value = delete_response

        result = await tasks_manager.delete("task-123")

        assert result is True

        mock_client.execute_mutation.assert_called_once()
        call_args = mock_client.execute_mutation.call_args
        assert call_args[0][1]["id"] == "task-123"

    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, tasks_manager, mock_client):
        """Test deleting non-existent task."""
        delete_response = {"data": {"deleteTask": {"success": False, "message": "Task not found"}}}
        mock_client.execute_mutation.return_value = delete_response

        result = await tasks_manager.delete("nonexistent")

        assert result is False

    # Test Task Status Management

    @pytest.mark.asyncio
    async def test_change_task_status_success(self, tasks_manager, mock_client):
        """Test successful task status change."""
        update_response = {
            "data": {
                "updateTask": {
                    "id": "task-123",
                    "status": "IN_PROGRESS",
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = update_response

        result = await tasks_manager.change_status("task-123", TaskStatus.IN_PROGRESS)

        assert result.status == TaskStatus.IN_PROGRESS

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_complete_task_success(self, tasks_manager, mock_client):
        """Test successful task completion."""
        update_response = {
            "data": {
                "updateTask": {
                    "id": "task-123",
                    "status": "COMPLETED",
                    "completionPercentage": 100.0,
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = update_response

        result = await tasks_manager.complete_task("task-123")

        assert result.status == TaskStatus.COMPLETED
        assert result["completionPercentage"] == 100.0

    @pytest.mark.asyncio
    async def test_assign_task_success(self, tasks_manager, mock_client):
        """Test successful task assignment."""
        update_response = {
            "data": {
                "updateTask": {
                    "id": "task-123",
                    "assigned_to": "user-456",
                    "status": "ASSIGNED",
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = update_response

        result = await tasks_manager.assign_task("task-123", "user-456")

        assert result.assigned_to == "user-456"
        assert result.status == TaskStatus.ASSIGNED

    # Test Task Filtering Methods

    @pytest.mark.asyncio
    async def test_list_tasks_by_status(
        self, tasks_manager, mock_client, sample_task_list_response
    ):
        """Test listing tasks by status."""
        mock_client.execute_query.return_value = sample_task_list_response

        result = await tasks_manager.list_tasks_by_status(TaskStatus.IN_PROGRESS)

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["status"] == TaskStatus.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_list_tasks_by_project(
        self, tasks_manager, mock_client, sample_task_list_response
    ):
        """Test listing tasks by project."""
        mock_client.execute_query.return_value = sample_task_list_response

        result = await tasks_manager.list_tasks_by_project("project-456")

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["project_id"] == "project-456"

    @pytest.mark.asyncio
    async def test_list_assigned_tasks(self, tasks_manager, mock_client, sample_task_list_response):
        """Test listing tasks assigned to a user."""
        mock_client.execute_query.return_value = sample_task_list_response

        result = await tasks_manager.list_assigned_tasks("user-789")

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["assigned_to"] == "user-789"

    @pytest.mark.asyncio
    async def test_get_overdue_tasks(self, tasks_manager, mock_client, sample_task_list_response):
        """Test getting overdue tasks."""
        mock_client.execute_query.return_value = sample_task_list_response

        result = await tasks_manager.get_overdue_tasks()

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert "dueBefore" in variables["filters"]

    @pytest.mark.asyncio
    async def test_get_due_soon_tasks(self, tasks_manager, mock_client, sample_task_list_response):
        """Test getting tasks due soon."""
        mock_client.execute_query.return_value = sample_task_list_response

        result = await tasks_manager.get_due_soon_tasks(days_ahead=7)

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert "dueAfter" in variables["filters"]
        assert "dueBefore" in variables["filters"]

    # Test Task Hierarchy

    @pytest.mark.asyncio
    async def test_list_subtasks(self, tasks_manager, mock_client, sample_task_list_response):
        """Test listing subtasks."""
        mock_client.execute_query.return_value = sample_task_list_response

        result = await tasks_manager.list_subtasks("parent-task-123")

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["parent_task_id"] == "parent-task-123"

    @pytest.mark.asyncio
    async def test_create_subtask_success(self, tasks_manager, mock_client):
        """Test successful subtask creation."""
        created_task = {
            "data": {
                "createTask": {
                    "id": "subtask-123",
                    "title": "Subtask",
                    "description": "A subtask for testing",
                    "status": "NEW",
                    "priority": "NORMAL",
                    "parent_task_id": "parent-task-123",
                    "creator_id": "current-user",
                    "created_at": "2024-01-01T00:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = created_task

        result = await tasks_manager.create_subtask(
            parent_task_id="parent-task-123", title="Subtask", description="A subtask for testing"
        )

        assert result.id == "subtask-123"
        assert result.parent_task_id == "parent-task-123"

    # Test Recurring Tasks

    @pytest.mark.asyncio
    async def test_create_recurring_task_success(self, tasks_manager, mock_client):
        """Test successful recurring task creation."""
        created_task = {
            "data": {
                "createTask": {
                    "id": "recurring-task-123",
                    "title": "Recurring Task",
                    "description": "A recurring task for testing",
                    "status": "NEW",
                    "priority": "NORMAL",
                    "is_recurring": True,
                    "recurrence_type": "DAILY",
                    "recurrenceInterval": 1,
                    "next_due_date": "2024-01-02T00:00:00Z",
                    "created_at": "2024-01-01T00:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = created_task

        result = await tasks_manager.create_recurring_task(
            title="Recurring Task",
            description="A recurring task for testing",
            recurrence_type=TaskRecurrenceType.DAILY,
            recurrence_interval=1,
            start_date="2024-01-01",
        )

        assert result.id == "recurring-task-123"
        assert result["is_recurring"] is True
        assert result.recurrence_type == TaskRecurrenceType.DAILY

    @pytest.mark.asyncio
    async def test_list_recurring_tasks(
        self, tasks_manager, mock_client, sample_task_list_response
    ):
        """Test listing recurring tasks."""
        mock_client.execute_query.return_value = sample_task_list_response

        result = await tasks_manager.list_recurring_tasks()

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["is_recurring"] is True

    # Test Time Tracking

    @pytest.mark.asyncio
    async def test_log_time_success(self, tasks_manager, mock_client):
        """Test successful time entry logging."""
        time_entry_response = {
            "data": {
                "createTaskTimeEntry": {
                    "id": "time-entry-123",
                    "task_id": "task-123",
                    "user_id": "user-456",
                    "hours": 2.5,
                    "description": "Working on feature implementation",
                    "date": "2024-01-15",
                    "isBillable": True,
                    "created_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = time_entry_response

        result = await tasks_manager.log_time(
            task_id="task-123",
            hours=2.5,
            description="Working on feature implementation",
            is_billable=True,
        )

        assert result.id == "time-entry-123"
        assert result.hours == 2.5
        assert result.is_billable is True

    @pytest.mark.asyncio
    async def test_get_time_entries(self, tasks_manager, mock_client):
        """Test getting task time entries."""
        time_entries_response = {
            "data": {
                "taskTimeEntries": {
                    "items": [
                        {
                            "id": "time-entry-1",
                            "task_id": "task-123",
                            "user_id": "user-456",
                            "hours": 2.0,
                            "description": "Initial work",
                            "date": "2024-01-15",
                            "isBillable": True,
                        },
                        {
                            "id": "time-entry-2",
                            "task_id": "task-123",
                            "user_id": "user-456",
                            "hours": 1.5,
                            "description": "Bug fixes",
                            "date": "2024-01-16",
                            "isBillable": True,
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
        mock_client.execute_query.return_value = time_entries_response

        result = await tasks_manager.get_time_entries("task-123")

        assert len(result["items"]) == 2
        assert result["items"][0].hours == 2.0
        assert result["items"][1].hours == 1.5

    @pytest.mark.asyncio
    async def test_update_time_tracking_success(self, tasks_manager, mock_client):
        """Test successful time tracking update."""
        update_response = {
            "data": {
                "updateTask": {
                    "id": "task-123",
                    "actual_hours": 8.0,
                    "billableHours": 6.0,
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = update_response

        result = await tasks_manager.update_time_tracking(
            task_id="task-123", actual_hours=8.0, billable_hours=6.0
        )

        assert result["actual_hours"] == 8.0
        assert result["billableHours"] == 6.0

    # Test Comments

    @pytest.mark.asyncio
    async def test_add_comment_success(self, tasks_manager, mock_client):
        """Test successful comment addition."""
        comment_response = {
            "data": {
                "createTaskComment": {
                    "id": "comment-123",
                    "task_id": "task-123",
                    "user_id": "user-456",
                    "comment": "This is a test comment",
                    "isInternal": False,
                    "created_at": "2024-01-15T12:00:00Z",
                    "user": {"id": "user-456", "name": "Test User", "email": "test@example.com"},
                }
            }
        }
        mock_client.execute_mutation.return_value = comment_response

        result = await tasks_manager.add_comment(
            task_id="task-123", comment="This is a test comment"
        )

        assert result.id == "comment-123"
        assert result["comment"] == "This is a test comment"

    @pytest.mark.asyncio
    async def test_get_task_comments(self, tasks_manager, mock_client):
        """Test getting task comments."""
        comments_response = {
            "data": {
                "taskComments": {
                    "items": [
                        {
                            "id": "comment-1",
                            "task_id": "task-123",
                            "user_id": "user-456",
                            "comment": "First comment",
                            "isInternal": False,
                            "created_at": "2024-01-15T10:00:00Z",
                        },
                        {
                            "id": "comment-2",
                            "task_id": "task-123",
                            "user_id": "user-789",
                            "comment": "Second comment",
                            "isInternal": True,
                            "created_at": "2024-01-15T11:00:00Z",
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
        mock_client.execute_query.return_value = comments_response

        result = await tasks_manager.get_task_comments("task-123")

        assert len(result["items"]) == 2
        assert result["items"][0].content == "First comment"
        assert result["items"][1].content == "Second comment"

    # Test Search and Batch Operations

    @pytest.mark.asyncio
    async def test_search_tasks_success(
        self, tasks_manager, mock_client, sample_task_list_response
    ):
        """Test successful task search."""
        mock_client.execute_query.return_value = sample_task_list_response

        result = await tasks_manager.search_tasks("bug fix")

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["query"] == "bug fix"

    @pytest.mark.asyncio
    async def test_bulk_update_tasks_success(self, tasks_manager, mock_client):
        """Test successful bulk task update."""
        bulk_update_response = {
            "data": {
                "bulkUpdateTasks": {
                    "success": True,
                    "updatedCount": 3,
                    "message": "3 tasks updated successfully",
                }
            }
        }
        mock_client.execute_mutation.return_value = bulk_update_response

        task_ids = ["task-1", "task-2", "task-3"]
        updates = {"priority": TaskPriority.HIGH, "status": TaskStatus.IN_PROGRESS}

        result = await tasks_manager.bulk_update_tasks(task_ids, **updates)

        assert result["success"] is True
        assert result["updatedCount"] == 3

    @pytest.mark.asyncio
    async def test_bulk_delete_tasks_success(self, tasks_manager, mock_client):
        """Test successful bulk task deletion."""
        bulk_delete_response = {
            "data": {
                "bulkDeleteTasks": {
                    "success": True,
                    "deletedCount": 2,
                    "message": "2 tasks deleted successfully",
                }
            }
        }
        mock_client.execute_mutation.return_value = bulk_delete_response

        task_ids = ["task-1", "task-2"]

        result = await tasks_manager.bulk_delete_tasks(task_ids)

        assert result["success"] is True
        assert result["deletedCount"] == 2

    # Test Templates

    @pytest.mark.asyncio
    async def test_create_task_template_success(self, tasks_manager, mock_client):
        """Test successful task template creation."""
        template_response = {
            "data": {
                "createTaskTemplate": {
                    "id": "template-123",
                    "name": "Bug Fix Template",
                    "description": "Standard template for bug fix tasks",
                    "isActive": True,
                    "taskDefaults": {
                        "priority": "HIGH",
                        "estimated_hours": 4.0,
                        "tags": ["bug", "fix"],
                    },
                    "created_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = template_response

        result = await tasks_manager.create_task_template(
            name="Bug Fix Template",
            description="Standard template for bug fix tasks",
            task_defaults={
                "priority": TaskPriority.HIGH,
                "estimated_hours": 4.0,
                "tags": ["bug", "fix"],
            },
        )

        assert result.id == "template-123"
        assert result["name"] == "Bug Fix Template"

    @pytest.mark.asyncio
    async def test_create_task_from_template_success(self, tasks_manager, mock_client):
        """Test successful task creation from template."""
        created_task = {
            "data": {
                "createTaskFromTemplate": {
                    "id": "task-from-template-123",
                    "title": "Bug Fix: Login Issue",
                    "description": "Fix login authentication problem",
                    "status": "NEW",
                    "priority": "HIGH",
                    "templateId": "template-123",
                    "estimated_hours": 4.0,
                    "tags": ["bug", "fix", "login"],
                    "created_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = created_task

        result = await tasks_manager.create_task_from_template(
            template_id="template-123",
            title="Bug Fix: Login Issue",
            description="Fix login authentication problem",
            assigned_to="user-456",
        )

        assert result.id == "task-from-template-123"
        assert result["templateId"] == "template-123"
        assert result["priority"] == "HIGH"

    # Test Error Handling

    @pytest.mark.asyncio
    async def test_get_task_api_error(self, tasks_manager, mock_client):
        """Test API error handling in get_task."""
        mock_client.execute_query.side_effect = SuperOpsAPIError("API Error")

        with pytest.raises(SuperOpsAPIError):
            await tasks_manager.get_task("task-123")

    @pytest.mark.asyncio
    async def test_create_task_validation_error_empty_data(self, tasks_manager):
        """Test validation error for empty task data."""
        with pytest.raises(SuperOpsValidationError):
            await tasks_manager.create_task()

    @pytest.mark.asyncio
    async def test_update_task_invalid_id(self, tasks_manager):
        """Test update task with invalid ID."""
        with pytest.raises(SuperOpsValidationError, match="Task ID cannot be empty"):
            await tasks_manager.update_task("", title="Updated Title")

    @pytest.mark.asyncio
    async def test_assign_task_invalid_user_id(self, tasks_manager):
        """Test assign task with invalid user ID."""
        with pytest.raises(SuperOpsValidationError, match="User ID cannot be empty"):
            await tasks_manager.assign_task("task-123", "")

    @pytest.mark.asyncio
    async def test_log_time_invalid_hours(self, tasks_manager):
        """Test log time entry with invalid hours."""
        with pytest.raises(SuperOpsValidationError, match="Hours must be positive"):
            await tasks_manager.log_time("task-123", hours=-1.0)

        with pytest.raises(SuperOpsValidationError, match="Hours must be positive"):
            await tasks_manager.log_time("task-123", hours=0.0)

    # Test Priority and Status Workflows

    @pytest.mark.asyncio
    async def test_escalate_task_priority_success(self, tasks_manager, mock_client):
        """Test successful task priority escalation."""
        update_response = {
            "data": {
                "updateTask": {
                    "id": "task-123",
                    "priority": "HIGH",
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = update_response

        result = await tasks_manager.escalate_task_priority("task-123", TaskPriority.HIGH)

        assert result["priority"] == "HIGH"

    @pytest.mark.asyncio
    async def test_get_tasks_by_priority_success(
        self, tasks_manager, mock_client, sample_task_list_response
    ):
        """Test getting tasks by priority."""
        mock_client.execute_query.return_value = sample_task_list_response

        result = await tasks_manager.get_tasks_by_priority(TaskPriority.HIGH)

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["priority"] == TaskPriority.HIGH

    @pytest.mark.asyncio
    async def test_get_task_statistics_success(self, tasks_manager, mock_client):
        """Test getting task statistics."""
        stats_response = {
            "data": {
                "taskStatistics": {
                    "totalTasks": 150,
                    "tasksByStatus": {
                        "NEW": 25,
                        "IN_PROGRESS": 45,
                        "COMPLETED": 70,
                        "CANCELLED": 10,
                    },
                    "tasksByPriority": {"LOW": 30, "NORMAL": 80, "HIGH": 35, "URGENT": 5},
                    "averageCompletionTime": 5.2,
                    "overdueCount": 8,
                }
            }
        }
        mock_client.execute_query.return_value = stats_response

        result = await tasks_manager.get_task_statistics()

        assert result["totalTasks"] == 150
        assert result["tasksByStatus"]["NEW"] == 25
        assert result["tasksByPriority"]["HIGH"] == 35
        assert result["overdueCount"] == 8
