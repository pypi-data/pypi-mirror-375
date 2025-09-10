# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Task manager for SuperOps API operations."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..exceptions import SuperOpsAPIError, SuperOpsValidationError
from ..graphql.types import (
    Task,
    TaskComment,
    TaskPriority,
    TaskRecurrenceType,
    TaskStatus,
    TaskTemplate,
    TaskTimeEntry,
)
from .base import ResourceManager


class TasksManager(ResourceManager[Task]):
    """Manager for task operations.

    Provides high-level methods for managing SuperOps tasks including
    CRUD operations, workflow management, project linking, assignment,
    recurring tasks, time tracking, and task-specific features.
    """

    def __init__(self, client: "SuperOpsClient"):
        """Initialize the tasks manager.

        Args:
            client: SuperOps client instance
        """
        super().__init__(client, Task, "task")

    # Basic CRUD operations (inherited from ResourceManager)
    # get, list, create, update, delete, search

    # Status and workflow operations
    async def get_by_status(
        self,
        status: TaskStatus,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get tasks filtered by status.

        Args:
            status: Task status to filter by
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Task]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not isinstance(status, TaskStatus):
            raise SuperOpsValidationError("Status must be a TaskStatus enum")

        self.logger.debug(f"Getting tasks with status: {status.value}")

        filters = {"status": status.value}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
        )

    async def change_status(
        self,
        task_id: str,
        new_status: TaskStatus,
        comment: Optional[str] = None,
        time_logged: Optional[float] = None,
    ) -> Task:
        """Change task status with optional comment and time logging.

        Args:
            task_id: Task ID
            new_status: New status to set
            comment: Optional status change comment
            time_logged: Optional time logged with status change (hours)

        Returns:
            Updated task instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not task_id or not isinstance(task_id, str):
            raise SuperOpsValidationError("Task ID must be a non-empty string")
        if not isinstance(new_status, TaskStatus):
            raise SuperOpsValidationError("Status must be a TaskStatus enum")

        self.logger.debug(f"Changing task {task_id} status to: {new_status.value}")

        update_data = {"status": new_status.value}

        # Add completion timestamp for completed status
        if new_status == TaskStatus.COMPLETED:
            update_data["completed_at"] = datetime.utcnow().isoformat()

        return await self.update(task_id, update_data, comment=comment, time_logged=time_logged)

    async def get_active_tasks(
        self,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get active tasks (not completed or cancelled).

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: updated_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Task]) and 'pagination' info
        """
        self.logger.debug("Getting active tasks")

        filters = {"status__not_in": [TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value]}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "updated_at",
            sort_order=sort_order,
        )

    # Assignment operations
    async def get_by_assignee(
        self,
        assignee_id: str,
        page: int = 1,
        page_size: int = 50,
        include_completed: bool = False,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get tasks assigned to a specific user.

        Args:
            assignee_id: The assignee user ID
            page: Page number (1-based)
            page_size: Number of items per page
            include_completed: Whether to include completed tasks
            sort_by: Field to sort by (default: due_date)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Task]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not assignee_id or not isinstance(assignee_id, str):
            raise SuperOpsValidationError("Assignee ID must be a non-empty string")

        self.logger.debug(f"Getting tasks assigned to: {assignee_id}")

        filters = {"assigned_to": assignee_id}
        if not include_completed:
            filters["status__not_in"] = [TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value]

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "due_date",
            sort_order=sort_order,
        )

    async def assign_task(
        self,
        task_id: str,
        assigned_to: Optional[str] = None,
        assigned_to_team: Optional[str] = None,
        notify_assignee: bool = True,
        comment: Optional[str] = None,
    ) -> Task:
        """Assign task to user or team.

        Args:
            task_id: Task ID
            assigned_to: User ID to assign to (optional)
            assigned_to_team: Team ID to assign to (optional)
            notify_assignee: Whether to notify the assignee
            comment: Optional assignment comment

        Returns:
            Updated task instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not task_id or not isinstance(task_id, str):
            raise SuperOpsValidationError("Task ID must be a non-empty string")
        if not assigned_to and not assigned_to_team:
            raise SuperOpsValidationError("Must specify either assigned_to or assigned_to_team")

        self.logger.debug(f"Assigning task {task_id}")

        update_data = {}
        if assigned_to:
            update_data["assigned_to"] = assigned_to
        if assigned_to_team:
            update_data["assigned_to_team"] = assigned_to_team

        return await self.update(
            task_id, update_data, comment=comment, notify_assignee=notify_assignee
        )

    async def unassign_task(
        self,
        task_id: str,
        comment: Optional[str] = None,
    ) -> Task:
        """Unassign task (remove assignment).

        Args:
            task_id: Task ID
            comment: Optional unassignment comment

        Returns:
            Updated task instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not task_id or not isinstance(task_id, str):
            raise SuperOpsValidationError("Task ID must be a non-empty string")

        self.logger.debug(f"Unassigning task {task_id}")

        update_data = {
            "assigned_to": None,
            "assigned_to_team": None,
        }

        return await self.update(task_id, update_data, comment=comment)

    async def get_unassigned_tasks(
        self,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get unassigned tasks.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Task]) and 'pagination' info
        """
        self.logger.debug("Getting unassigned tasks")

        filters = {
            "assigned_to__isnull": True,
            "assigned_to_team__isnull": True,
            "status__not_in": [TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value],
        }

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
        )

    # Project operations
    async def get_by_project(
        self,
        project_id: str,
        page: int = 1,
        page_size: int = 50,
        include_completed: bool = False,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get tasks for a specific project.

        Args:
            project_id: The project ID
            page: Page number (1-based)
            page_size: Number of items per page
            include_completed: Whether to include completed tasks
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Task]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not project_id or not isinstance(project_id, str):
            raise SuperOpsValidationError("Project ID must be a non-empty string")

        self.logger.debug(f"Getting tasks for project: {project_id}")

        filters = {"project_id": project_id}
        if not include_completed:
            filters["status__not_in"] = [TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value]

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
        )

    async def link_to_project(
        self,
        task_id: str,
        project_id: str,
        comment: Optional[str] = None,
    ) -> Task:
        """Link task to a project.

        Args:
            task_id: Task ID
            project_id: Project ID to link to
            comment: Optional linking comment

        Returns:
            Updated task instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not task_id or not isinstance(task_id, str):
            raise SuperOpsValidationError("Task ID must be a non-empty string")
        if not project_id or not isinstance(project_id, str):
            raise SuperOpsValidationError("Project ID must be a non-empty string")

        self.logger.debug(f"Linking task {task_id} to project {project_id}")

        update_data = {"project_id": project_id}
        return await self.update(task_id, update_data, comment=comment)

    async def unlink_from_project(
        self,
        task_id: str,
        comment: Optional[str] = None,
    ) -> Task:
        """Unlink task from project (make it standalone).

        Args:
            task_id: Task ID
            comment: Optional unlinking comment

        Returns:
            Updated task instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not task_id or not isinstance(task_id, str):
            raise SuperOpsValidationError("Task ID must be a non-empty string")

        self.logger.debug(f"Unlinking task {task_id} from project")

        update_data = {"project_id": None}
        return await self.update(task_id, update_data, comment=comment)

    async def get_standalone_tasks(
        self,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get standalone tasks (not linked to any project).

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Task]) and 'pagination' info
        """
        self.logger.debug("Getting standalone tasks")

        filters = {"project_id__isnull": True}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
        )

    # Priority operations
    async def get_by_priority(
        self,
        priority: TaskPriority,
        page: int = 1,
        page_size: int = 50,
        include_completed: bool = False,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get tasks filtered by priority.

        Args:
            priority: Task priority to filter by
            page: Page number (1-based)
            page_size: Number of items per page
            include_completed: Whether to include completed tasks
            sort_by: Field to sort by (default: due_date)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Task]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not isinstance(priority, TaskPriority):
            raise SuperOpsValidationError("Priority must be a TaskPriority enum")

        self.logger.debug(f"Getting tasks with priority: {priority.value}")

        filters = {"priority": priority.value}
        if not include_completed:
            filters["status__not_in"] = [TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value]

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "due_date",
            sort_order=sort_order,
        )

    async def get_high_priority_tasks(
        self,
        page: int = 1,
        page_size: int = 50,
        include_urgent: bool = True,
        include_critical: bool = True,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get high priority tasks.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            include_urgent: Whether to include urgent priority tasks
            include_critical: Whether to include critical priority tasks
            sort_by: Field to sort by (default: due_date)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Task]) and 'pagination' info
        """
        self.logger.debug("Getting high priority tasks")

        priorities = [TaskPriority.HIGH.value]
        if include_urgent:
            priorities.append(TaskPriority.URGENT.value)
        if include_critical:
            priorities.append(TaskPriority.CRITICAL.value)

        filters = {
            "priority__in": priorities,
            "status__not_in": [TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value],
        }

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "due_date",
            sort_order=sort_order,
        )

    async def change_priority(
        self,
        task_id: str,
        new_priority: TaskPriority,
        comment: Optional[str] = None,
    ) -> Task:
        """Change task priority.

        Args:
            task_id: Task ID
            new_priority: New priority to set
            comment: Optional priority change comment

        Returns:
            Updated task instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not task_id or not isinstance(task_id, str):
            raise SuperOpsValidationError("Task ID must be a non-empty string")
        if not isinstance(new_priority, TaskPriority):
            raise SuperOpsValidationError("Priority must be a TaskPriority enum")

        self.logger.debug(f"Changing task {task_id} priority to: {new_priority.value}")

        update_data = {"priority": new_priority.value}
        return await self.update(task_id, update_data, comment=comment)

    # Due date and scheduling operations
    async def get_overdue_tasks(
        self,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get all overdue tasks.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: due_date)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Task]) and 'pagination' info
        """
        self.logger.debug("Getting overdue tasks")

        now = datetime.utcnow()
        filters = {
            "due_date__lt": now.isoformat(),
            "status__not_in": [TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value],
        }

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "due_date",
            sort_order=sort_order,
        )

    async def get_due_soon(
        self,
        days_ahead: int = 7,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get tasks due within a specified number of days.

        Args:
            days_ahead: Number of days ahead to check
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: due_date)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Task]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
        """
        if days_ahead < 1:
            raise SuperOpsValidationError("Days ahead must be >= 1")

        self.logger.debug(f"Getting tasks due within {days_ahead} days")

        now = datetime.utcnow()
        future_date = now + timedelta(days=days_ahead)

        filters = {
            "due_date__gte": now.isoformat(),
            "due_date__lte": future_date.isoformat(),
            "status__not_in": [TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value],
        }

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "due_date",
            sort_order=sort_order,
        )

    async def set_due_date(
        self,
        task_id: str,
        due_date: datetime,
        comment: Optional[str] = None,
    ) -> Task:
        """Set task due date.

        Args:
            task_id: Task ID
            due_date: Due date to set
            comment: Optional due date change comment

        Returns:
            Updated task instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not task_id or not isinstance(task_id, str):
            raise SuperOpsValidationError("Task ID must be a non-empty string")
        if not isinstance(due_date, datetime):
            raise SuperOpsValidationError("Due date must be a datetime object")

        self.logger.debug(f"Setting task {task_id} due date to: {due_date}")

        update_data = {"due_date": due_date.isoformat()}
        return await self.update(task_id, update_data, comment=comment)

    async def clear_due_date(
        self,
        task_id: str,
        comment: Optional[str] = None,
    ) -> Task:
        """Clear task due date.

        Args:
            task_id: Task ID
            comment: Optional due date clear comment

        Returns:
            Updated task instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not task_id or not isinstance(task_id, str):
            raise SuperOpsValidationError("Task ID must be a non-empty string")

        self.logger.debug(f"Clearing task {task_id} due date")

        update_data = {"due_date": None}
        return await self.update(task_id, update_data, comment=comment)

    # Task hierarchy operations
    async def get_subtasks(
        self,
        parent_task_id: str,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get subtasks for a specific parent task.

        Args:
            parent_task_id: Parent task ID
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Task]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not parent_task_id or not isinstance(parent_task_id, str):
            raise SuperOpsValidationError("Parent task ID must be a non-empty string")

        self.logger.debug(f"Getting subtasks for task: {parent_task_id}")

        filters = {"parent_task_id": parent_task_id}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
        )

    async def get_parent_tasks(
        self,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get parent tasks (tasks that have subtasks).

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: updated_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Task]) and 'pagination' info
        """
        self.logger.debug("Getting parent tasks")

        filters = {"subtask_count__gt": 0}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "updated_at",
            sort_order=sort_order,
        )

    async def create_subtask(
        self,
        parent_task_id: str,
        subtask_data: Dict[str, Any],
    ) -> Task:
        """Create a subtask under a parent task.

        Args:
            parent_task_id: Parent task ID
            subtask_data: Subtask data (must include 'title')

        Returns:
            Created subtask instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not parent_task_id or not isinstance(parent_task_id, str):
            raise SuperOpsValidationError("Parent task ID must be a non-empty string")
        if not subtask_data or not isinstance(subtask_data, dict):
            raise SuperOpsValidationError("Subtask data must be a non-empty dictionary")
        if not subtask_data.get("title"):
            raise SuperOpsValidationError("Subtask data must include 'title'")

        self.logger.debug(f"Creating subtask for task: {parent_task_id}")

        # Add parent task ID to subtask data
        subtask_data["parent_task_id"] = parent_task_id

        return await self.create(subtask_data)

    # Recurring task operations
    async def get_recurring_tasks(
        self,
        page: int = 1,
        page_size: int = 50,
        recurrence_type: Optional[TaskRecurrenceType] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get recurring tasks.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            recurrence_type: Optional recurrence type filter
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Task]) and 'pagination' info
        """
        self.logger.debug("Getting recurring tasks")

        filters = {"recurrence_type__ne": TaskRecurrenceType.NONE.value}
        if recurrence_type and recurrence_type != TaskRecurrenceType.NONE:
            filters["recurrence_type"] = recurrence_type.value

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
        )

    async def setup_recurrence(
        self,
        task_id: str,
        recurrence_type: TaskRecurrenceType,
        recurrence_interval: int = 1,
        recurrence_end_date: Optional[datetime] = None,
        comment: Optional[str] = None,
    ) -> Task:
        """Set up task recurrence.

        Args:
            task_id: Task ID
            recurrence_type: Type of recurrence
            recurrence_interval: Recurrence interval (e.g., every 2 weeks)
            recurrence_end_date: Optional end date for recurrence
            comment: Optional recurrence setup comment

        Returns:
            Updated task instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not task_id or not isinstance(task_id, str):
            raise SuperOpsValidationError("Task ID must be a non-empty string")
        if not isinstance(recurrence_type, TaskRecurrenceType):
            raise SuperOpsValidationError("Recurrence type must be a TaskRecurrenceType enum")
        if recurrence_type == TaskRecurrenceType.NONE:
            raise SuperOpsValidationError("Cannot setup recurrence with NONE type")
        if recurrence_interval < 1:
            raise SuperOpsValidationError("Recurrence interval must be >= 1")

        self.logger.debug(f"Setting up recurrence for task {task_id}: {recurrence_type.value}")

        update_data = {
            "recurrence_type": recurrence_type.value,
            "recurrence_interval": recurrence_interval,
        }
        if recurrence_end_date:
            update_data["recurrence_end_date"] = recurrence_end_date.isoformat()

        return await self.update(task_id, update_data, comment=comment)

    async def disable_recurrence(
        self,
        task_id: str,
        comment: Optional[str] = None,
    ) -> Task:
        """Disable task recurrence.

        Args:
            task_id: Task ID
            comment: Optional recurrence disable comment

        Returns:
            Updated task instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not task_id or not isinstance(task_id, str):
            raise SuperOpsValidationError("Task ID must be a non-empty string")

        self.logger.debug(f"Disabling recurrence for task {task_id}")

        update_data = {
            "recurrence_type": TaskRecurrenceType.NONE.value,
            "recurrence_interval": None,
            "recurrence_end_date": None,
        }

        return await self.update(task_id, update_data, comment=comment)

    # Time tracking operations
    async def log_time(
        self,
        task_id: str,
        hours: float,
        description: Optional[str] = None,
        date_logged: Optional[datetime] = None,
        is_billable: bool = True,
        hourly_rate: Optional[float] = None,
    ) -> TaskTimeEntry:
        """Log time entry for a task.

        Args:
            task_id: Task ID
            hours: Hours to log
            description: Optional description of work done
            date_logged: Date/time when work was done (default: now)
            is_billable: Whether time is billable
            hourly_rate: Optional hourly rate for billing

        Returns:
            Created time entry instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not task_id or not isinstance(task_id, str):
            raise SuperOpsValidationError("Task ID must be a non-empty string")
        if not isinstance(hours, (int, float)) or hours <= 0:
            raise SuperOpsValidationError("Hours must be a positive number")

        self.logger.debug(f"Logging {hours} hours for task {task_id}")

        time_entry_data = {
            "task_id": task_id,
            "hours": hours,
            "is_billable": is_billable,
        }
        if description:
            time_entry_data["description"] = description
        if date_logged:
            time_entry_data["date_logged"] = date_logged.isoformat()
        else:
            time_entry_data["date_logged"] = datetime.utcnow().isoformat()
        if hourly_rate is not None:
            time_entry_data["hourly_rate"] = hourly_rate

        # This would need to be implemented as a separate mutation
        # For now, we'll use a generic mutation approach
        mutation = self._build_create_time_entry_mutation()
        variables = {"input": time_entry_data}

        response = await self.client.execute_mutation(mutation, variables)
        if not response.get("data") or not response["data"].get("createTaskTimeEntry"):
            raise SuperOpsAPIError("Failed to create time entry", 500, response)

        return TaskTimeEntry.from_dict(response["data"]["createTaskTimeEntry"])

    async def get_time_entries(
        self,
        task_id: str,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get time entries for a task.

        Args:
            task_id: Task ID
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: date_logged)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[TaskTimeEntry]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not task_id or not isinstance(task_id, str):
            raise SuperOpsValidationError("Task ID must be a non-empty string")

        self.logger.debug(f"Getting time entries for task: {task_id}")

        # This would need to be implemented as a separate query
        # For now, we'll use a generic approach
        query = self._build_time_entries_query()
        variables = {
            "taskId": task_id,
            "page": page,
            "pageSize": page_size,
            "sortBy": sort_by or "date_logged",
            "sortOrder": sort_order.upper(),
        }

        response = await self.client.execute_query(query, variables)
        if not response.get("data") or not response["data"].get("taskTimeEntries"):
            return {"items": [], "pagination": self._empty_pagination()}

        time_entries_data = response["data"]["taskTimeEntries"]
        items = [TaskTimeEntry.from_dict(item) for item in time_entries_data.get("items", [])]
        pagination = time_entries_data.get("pagination", self._empty_pagination())

        return {"items": items, "pagination": pagination}

    # Template operations
    async def create_from_template(
        self,
        template_id: str,
        task_data: Optional[Dict[str, Any]] = None,
    ) -> Task:
        """Create a task from a template.

        Args:
            template_id: Template ID
            task_data: Optional task data to override template defaults

        Returns:
            Created task instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not template_id or not isinstance(template_id, str):
            raise SuperOpsValidationError("Template ID must be a non-empty string")

        self.logger.debug(f"Creating task from template: {template_id}")

        create_data = {"template_id": template_id}
        if task_data:
            create_data.update(task_data)

        return await self.create(create_data)

    # Search and filtering
    async def search_by_title(
        self,
        query: str,
        page: int = 1,
        page_size: int = 50,
        include_completed: bool = False,
    ) -> Dict[str, Any]:
        """Search tasks by title.

        Args:
            query: Search query
            page: Page number (1-based)
            page_size: Number of items per page
            include_completed: Whether to include completed tasks

        Returns:
            Dictionary containing 'items' (List[Task]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not query or not isinstance(query, str):
            raise SuperOpsValidationError("Query must be a non-empty string")

        self.logger.debug(f"Searching tasks by title: {query}")

        filters = {"title__icontains": query}
        if not include_completed:
            filters["status__not_in"] = [TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value]

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
        )

    async def get_by_tags(
        self,
        tags: List[str],
        match_all: bool = False,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        """Get tasks by tags.

        Args:
            tags: List of tags to filter by
            match_all: Whether to match all tags (AND) or any tag (OR)
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            Dictionary containing 'items' (List[Task]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not tags or not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
            raise SuperOpsValidationError("Tags must be a non-empty list of strings")

        self.logger.debug(f"Getting tasks by tags: {tags}")

        if match_all:
            filters = {"tags__contains_all": tags}
        else:
            filters = {"tags__contains_any": tags}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
        )

    # Milestone operations
    async def get_milestones(
        self,
        page: int = 1,
        page_size: int = 50,
        include_completed: bool = True,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get milestone tasks.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            include_completed: Whether to include completed milestones
            sort_by: Field to sort by (default: due_date)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Task]) and 'pagination' info
        """
        self.logger.debug("Getting milestone tasks")

        filters = {"is_milestone": True}
        if not include_completed:
            filters["status__not_in"] = [TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value]

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "due_date",
            sort_order=sort_order,
        )

    async def mark_as_milestone(
        self,
        task_id: str,
        comment: Optional[str] = None,
    ) -> Task:
        """Mark task as milestone.

        Args:
            task_id: Task ID
            comment: Optional milestone marking comment

        Returns:
            Updated task instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not task_id or not isinstance(task_id, str):
            raise SuperOpsValidationError("Task ID must be a non-empty string")

        self.logger.debug(f"Marking task {task_id} as milestone")

        update_data = {"is_milestone": True}
        return await self.update(task_id, update_data, comment=comment)

    # Abstract method implementations for ResourceManager
    def _build_get_query(self, **kwargs) -> str:
        """Build GraphQL query for getting a single task."""
        from ..graphql.fragments import create_query_with_fragments, get_task_fields

        detail_level = kwargs.get("detail_level", "full")
        include_comments = kwargs.get("include_comments", True)
        include_time_entries = kwargs.get("include_time_entries", True)

        fragment_names = get_task_fields(detail_level, include_comments, include_time_entries)

        query = f"""
        query GetTask($id: ID!) {{
            task(id: $id) {{
                ...{list(fragment_names)[0]}
            }}
        }}
        """

        return create_query_with_fragments(query, fragment_names)

    def _build_list_query(self, **kwargs) -> str:
        """Build GraphQL query for listing tasks."""
        from ..graphql.fragments import create_query_with_fragments, get_task_fields

        detail_level = kwargs.get("detail_level", "core")
        include_comments = kwargs.get("include_comments", False)
        include_time_entries = kwargs.get("include_time_entries", False)

        fragment_names = get_task_fields(detail_level, include_comments, include_time_entries)
        fragment_names.add("PaginationInfo")

        query = f"""
        query ListTasks(
            $page: Int
            $pageSize: Int
            $filters: TaskFilter
            $sortBy: String
            $sortOrder: SortDirection
        ) {{
            tasks(
                page: $page
                pageSize: $pageSize
                filter: $filters
                sortBy: $sortBy
                sortDirection: $sortOrder
            ) {{
                items {{
                    ...{list(fragment_names)[0]}
                }}
                pagination {{
                    ...PaginationInfo
                }}
            }}
        }}
        """

        return create_query_with_fragments(query, fragment_names)

    def _build_create_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for creating a task."""
        from ..graphql.fragments import create_query_with_fragments, get_task_fields

        detail_level = kwargs.get("detail_level", "full")
        fragment_names = get_task_fields(detail_level)

        mutation = f"""
        mutation CreateTask($input: TaskInput!) {{
            createTask(input: $input) {{
                ...{list(fragment_names)[0]}
            }}
        }}
        """

        return create_query_with_fragments(mutation, fragment_names)

    def _build_update_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for updating a task."""
        from ..graphql.fragments import create_query_with_fragments, get_task_fields

        detail_level = kwargs.get("detail_level", "full")
        fragment_names = get_task_fields(detail_level)

        mutation = f"""
        mutation UpdateTask($id: ID!, $input: TaskInput!) {{
            updateTask(id: $id, input: $input) {{
                ...{list(fragment_names)[0]}
            }}
        }}
        """

        return create_query_with_fragments(mutation, fragment_names)

    def _build_delete_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for deleting a task."""
        return """
        mutation DeleteTask($id: ID!) {
            deleteTask(id: $id) {
                success
                message
            }
        }
        """

    def _build_search_query(self, **kwargs) -> str:
        """Build GraphQL query for searching tasks."""
        from ..graphql.fragments import create_query_with_fragments, get_task_fields

        detail_level = kwargs.get("detail_level", "core")
        fragment_names = get_task_fields(detail_level)
        fragment_names.add("PaginationInfo")

        query = f"""
        query SearchTasks(
            $query: String!
            $page: Int
            $pageSize: Int
        ) {{
            searchTasks(
                query: $query
                page: $page
                pageSize: $pageSize
            ) {{
                items {{
                    ...{list(fragment_names)[0]}
                }}
                pagination {{
                    ...PaginationInfo
                }}
            }}
        }}
        """

        return create_query_with_fragments(query, fragment_names)

    def _build_create_time_entry_mutation(self) -> str:
        """Build GraphQL mutation for creating a time entry."""
        from ..graphql.fragments import create_query_with_fragments

        fragment_names = {"TaskTimeEntryFields"}

        mutation = """
        mutation CreateTaskTimeEntry($input: TaskTimeEntryInput!) {
            createTaskTimeEntry(input: $input) {
                ...TaskTimeEntryFields
            }
        }
        """

        return create_query_with_fragments(mutation, fragment_names)

    def _build_time_entries_query(self) -> str:
        """Build GraphQL query for getting time entries."""
        from ..graphql.fragments import create_query_with_fragments

        fragment_names = {"TaskTimeEntryFields", "PaginationInfo"}

        query = """
        query GetTaskTimeEntries(
            $taskId: ID!
            $page: Int
            $pageSize: Int
            $sortBy: String
            $sortOrder: SortDirection
        ) {
            taskTimeEntries(
                taskId: $taskId
                page: $page
                pageSize: $pageSize
                sortBy: $sortBy
                sortDirection: $sortOrder
            ) {
                items {
                    ...TaskTimeEntryFields
                }
                pagination {
                    ...PaginationInfo
                }
            }
        }
        """

        return create_query_with_fragments(query, fragment_names)
