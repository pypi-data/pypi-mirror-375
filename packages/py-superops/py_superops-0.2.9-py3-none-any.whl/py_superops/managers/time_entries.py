# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Time entries manager for SuperOps API operations."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..exceptions import SuperOpsAPIError, SuperOpsValidationError
from ..graphql.types import (
    TimeEntry,
    TimeEntryFilter,
    TimeEntryStatus,
    TimeEntryTemplate,
    TimeEntryType,
    Timer,
    TimerFilter,
    TimerState,
)
from .base import ResourceManager


class TimeEntriesManager(ResourceManager[TimeEntry]):
    """Manager for time entry operations.

    Provides high-level methods for managing SuperOps time entries including
    CRUD operations, time tracking, timer functionality, approval workflows,
    and time-based reporting and analytics.
    """

    def __init__(self, client: "SuperOpsClient"):
        """Initialize the time entries manager.

        Args:
            client: SuperOps client instance
        """
        super().__init__(client, TimeEntry, "timeEntry")

    # Basic CRUD Operations

    async def get_by_user(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 50,
        status_filter: Optional[TimeEntryStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get time entries for a specific user.

        Args:
            user_id: The user ID
            page: Page number (1-based)
            page_size: Number of items per page
            status_filter: Optional status filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            sort_by: Field to sort by (default: start_time)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[TimeEntry]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not user_id or not isinstance(user_id, str):
            raise SuperOpsValidationError("User ID must be a non-empty string")

        self.logger.debug(f"Getting time entries for user: {user_id}")

        filters = {"user_id": user_id}

        if status_filter:
            filters["status"] = status_filter.value
        if start_date:
            filters["start_time_after"] = start_date.isoformat()
        if end_date:
            filters["end_time_before"] = end_date.isoformat()

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "start_time",
            sort_order=sort_order,
        )

    async def get_by_project(
        self,
        project_id: str,
        page: int = 1,
        page_size: int = 50,
        status_filter: Optional[TimeEntryStatus] = None,
        is_billable: Optional[bool] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get time entries for a specific project.

        Args:
            project_id: The project ID
            page: Page number (1-based)
            page_size: Number of items per page
            status_filter: Optional status filter
            is_billable: Optional billable filter
            sort_by: Field to sort by (default: start_time)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[TimeEntry]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not project_id or not isinstance(project_id, str):
            raise SuperOpsValidationError("Project ID must be a non-empty string")

        self.logger.debug(f"Getting time entries for project: {project_id}")

        filters = {"project_id": project_id}

        if status_filter:
            filters["status"] = status_filter.value
        if is_billable is not None:
            filters["is_billable"] = is_billable

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "start_time",
            sort_order=sort_order,
        )

    async def get_by_ticket(
        self,
        ticket_id: str,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get time entries for a specific ticket.

        Args:
            ticket_id: The ticket ID
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: start_time)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[TimeEntry]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not ticket_id or not isinstance(ticket_id, str):
            raise SuperOpsValidationError("Ticket ID must be a non-empty string")

        self.logger.debug(f"Getting time entries for ticket: {ticket_id}")

        filters = {"ticket_id": ticket_id}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "start_time",
            sort_order=sort_order,
        )

    # Time Tracking Methods

    async def start_timer(
        self,
        user_id: str,
        description: str,
        ticket_id: Optional[str] = None,
        task_id: Optional[str] = None,
        project_id: Optional[str] = None,
        client_id: Optional[str] = None,
        entry_type: TimeEntryType = TimeEntryType.WORK,
        is_billable: bool = True,
        work_category: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Timer:
        """Start a new timer.

        Args:
            user_id: User starting the timer
            description: Description of work being performed
            ticket_id: Optional ticket ID
            task_id: Optional task ID
            project_id: Optional project ID
            client_id: Optional client ID
            entry_type: Type of time entry
            is_billable: Whether time is billable
            work_category: Optional work category
            tags: Optional tags

        Returns:
            Started timer instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not user_id or not isinstance(user_id, str):
            raise SuperOpsValidationError("User ID must be a non-empty string")
        if not description or not isinstance(description, str):
            raise SuperOpsValidationError("Description must be a non-empty string")

        # Check if user has an active timer
        active_timer = await self.get_active_timer(user_id)
        if active_timer:
            raise SuperOpsValidationError(f"User {user_id} already has an active timer")

        self.logger.debug(f"Starting timer for user {user_id}")

        mutation = """
            mutation StartTimer($input: StartTimerInput!) {
                startTimer(input: $input) {
                    id
                    userId
                    description
                    startTime
                    state
                    ticketId
                    taskId
                    projectId
                    clientId
                    isBillable
                    entryType
                    workCategory
                    tags
                    createdAt
                    updatedAt
                }
            }
        """

        variables = {
            "input": {
                "user_id": user_id,
                "description": description,
                "start_time": datetime.utcnow().isoformat(),
                "ticket_id": ticket_id,
                "task_id": task_id,
                "project_id": project_id,
                "client_id": client_id,
                "entry_type": entry_type.value,
                "is_billable": is_billable,
                "work_category": work_category,
                "tags": tags or [],
            }
        }

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when starting timer", 500, response)

        timer_data = response["data"].get("startTimer")
        if not timer_data:
            raise SuperOpsAPIError("No timer data in start response", 500, response)

        return Timer.from_dict(timer_data)

    async def stop_timer(self, timer_id: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """Stop an active timer and create a time entry.

        Args:
            timer_id: Timer ID to stop
            notes: Optional notes for the time entry

        Returns:
            Dictionary with timer and created time entry

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not timer_id or not isinstance(timer_id, str):
            raise SuperOpsValidationError("Timer ID must be a non-empty string")

        self.logger.debug(f"Stopping timer {timer_id}")

        mutation = """
            mutation StopTimer($timerId: ID!, $notes: String) {
                stopTimer(timerId: $timerId, notes: $notes) {
                    timer {
                        id
                        state
                        updatedAt
                    }
                    timeEntry {
                        id
                        userId
                        description
                        startTime
                        endTime
                        durationMinutes
                        status
                        entryType
                        isBillable
                        notes
                        createdAt
                        updatedAt
                    }
                }
            }
        """

        variables = {"timerId": timer_id, "notes": notes}

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when stopping timer", 500, response)

        stop_data = response["data"].get("stopTimer")
        if not stop_data:
            raise SuperOpsAPIError("No stop timer data in response", 500, response)

        result = {
            "timer": Timer.from_dict(stop_data["timer"]) if stop_data.get("timer") else None,
            "time_entry": (
                TimeEntry.from_dict(stop_data["timeEntry"]) if stop_data.get("timeEntry") else None
            ),
        }

        self.logger.info(
            f"Stopped timer {timer_id}, created time entry {result['time_entry'].id if result['time_entry'] else 'N/A'}"
        )

        return result

    async def pause_timer(self, timer_id: str) -> Timer:
        """Pause an active timer.

        Args:
            timer_id: Timer ID to pause

        Returns:
            Updated timer instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not timer_id or not isinstance(timer_id, str):
            raise SuperOpsValidationError("Timer ID must be a non-empty string")

        self.logger.debug(f"Pausing timer {timer_id}")

        mutation = """
            mutation PauseTimer($timerId: ID!) {
                pauseTimer(timerId: $timerId) {
                    id
                    state
                    pausedTime
                    totalPausedDuration
                    updatedAt
                }
            }
        """

        variables = {"timerId": timer_id}

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when pausing timer", 500, response)

        timer_data = response["data"].get("pauseTimer")
        if not timer_data:
            raise SuperOpsAPIError("No timer data in pause response", 500, response)

        return Timer.from_dict(timer_data)

    async def resume_timer(self, timer_id: str) -> Timer:
        """Resume a paused timer.

        Args:
            timer_id: Timer ID to resume

        Returns:
            Updated timer instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not timer_id or not isinstance(timer_id, str):
            raise SuperOpsValidationError("Timer ID must be a non-empty string")

        self.logger.debug(f"Resuming timer {timer_id}")

        mutation = """
            mutation ResumeTimer($timerId: ID!) {
                resumeTimer(timerId: $timerId) {
                    id
                    state
                    pausedTime
                    totalPausedDuration
                    updatedAt
                }
            }
        """

        variables = {"timerId": timer_id}

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when resuming timer", 500, response)

        timer_data = response["data"].get("resumeTimer")
        if not timer_data:
            raise SuperOpsAPIError("No timer data in resume response", 500, response)

        return Timer.from_dict(timer_data)

    async def get_active_timer(self, user_id: str) -> Optional[Timer]:
        """Get the active timer for a user.

        Args:
            user_id: User ID

        Returns:
            Active timer instance or None if no active timer

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not user_id or not isinstance(user_id, str):
            raise SuperOpsValidationError("User ID must be a non-empty string")

        self.logger.debug(f"Getting active timer for user {user_id}")

        query = """
            query GetActiveTimer($userId: ID!) {
                activeTimer(userId: $userId) {
                    id
                    userId
                    description
                    startTime
                    pausedTime
                    totalPausedDuration
                    currentDuration
                    state
                    ticketId
                    taskId
                    projectId
                    clientId
                    isBillable
                    entryType
                    workCategory
                    tags
                    createdAt
                    updatedAt
                }
            }
        """

        variables = {"userId": user_id}

        response = await self.client.execute_query(query, variables)

        if not response.get("data"):
            return None

        timer_data = response["data"].get("activeTimer")
        if not timer_data:
            return None

        return Timer.from_dict(timer_data)

    # Billable vs Non-billable Categorization

    async def get_billable_entries(
        self,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        client_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        """Get billable time entries with optional filtering.

        Args:
            user_id: Optional user ID filter
            project_id: Optional project ID filter
            client_id: Optional client ID filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            Dictionary containing 'items' (List[TimeEntry]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Getting billable time entries")

        filters = {"is_billable": True}

        if user_id:
            filters["user_id"] = user_id
        if project_id:
            filters["project_id"] = project_id
        if client_id:
            filters["client_id"] = client_id
        if start_date:
            filters["start_time_after"] = start_date.isoformat()
        if end_date:
            filters["end_time_before"] = end_date.isoformat()

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by="start_time",
            sort_order="desc",
        )

    async def get_non_billable_entries(
        self,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        client_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        """Get non-billable time entries with optional filtering.

        Args:
            user_id: Optional user ID filter
            project_id: Optional project ID filter
            client_id: Optional client ID filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            Dictionary containing 'items' (List[TimeEntry]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Getting non-billable time entries")

        filters = {"is_billable": False}

        if user_id:
            filters["user_id"] = user_id
        if project_id:
            filters["project_id"] = project_id
        if client_id:
            filters["client_id"] = client_id
        if start_date:
            filters["start_time_after"] = start_date.isoformat()
        if end_date:
            filters["end_time_before"] = end_date.isoformat()

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by="start_time",
            sort_order="desc",
        )

    async def mark_as_billable(
        self,
        time_entry_ids: List[str],
        hourly_rate: Optional[float] = None,
    ) -> List[TimeEntry]:
        """Mark time entries as billable.

        Args:
            time_entry_ids: List of time entry IDs to mark as billable
            hourly_rate: Optional hourly rate to set

        Returns:
            List of updated time entries

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not time_entry_ids:
            raise SuperOpsValidationError("Time entry IDs list cannot be empty")
        if not isinstance(time_entry_ids, list):
            raise SuperOpsValidationError("Time entry IDs must be a list")

        self.logger.debug(f"Marking {len(time_entry_ids)} time entries as billable")

        updated_entries = []
        for entry_id in time_entry_ids:
            try:
                update_data = {"is_billable": True}
                if hourly_rate is not None:
                    update_data["hourly_rate"] = hourly_rate

                entry = await self.update(entry_id, update_data)
                updated_entries.append(entry)
            except Exception as e:
                self.logger.error(f"Failed to mark time entry {entry_id} as billable: {e}")

        self.logger.info(
            f"Successfully marked {len(updated_entries)} out of {len(time_entry_ids)} entries as billable"
        )
        return updated_entries

    async def mark_as_non_billable(self, time_entry_ids: List[str]) -> List[TimeEntry]:
        """Mark time entries as non-billable.

        Args:
            time_entry_ids: List of time entry IDs to mark as non-billable

        Returns:
            List of updated time entries

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not time_entry_ids:
            raise SuperOpsValidationError("Time entry IDs list cannot be empty")
        if not isinstance(time_entry_ids, list):
            raise SuperOpsValidationError("Time entry IDs must be a list")

        self.logger.debug(f"Marking {len(time_entry_ids)} time entries as non-billable")

        updated_entries = []
        for entry_id in time_entry_ids:
            try:
                update_data = {"is_billable": False, "hourly_rate": None, "total_amount": None}
                entry = await self.update(entry_id, update_data)
                updated_entries.append(entry)
            except Exception as e:
                self.logger.error(f"Failed to mark time entry {entry_id} as non-billable: {e}")

        self.logger.info(
            f"Successfully marked {len(updated_entries)} out of {len(time_entry_ids)} entries as non-billable"
        )
        return updated_entries

    # Approval Workflow Methods

    async def submit_for_approval(
        self,
        time_entry_ids: List[str],
        notes: Optional[str] = None,
    ) -> List[TimeEntry]:
        """Submit time entries for approval.

        Args:
            time_entry_ids: List of time entry IDs to submit
            notes: Optional submission notes

        Returns:
            List of updated time entries

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not time_entry_ids:
            raise SuperOpsValidationError("Time entry IDs list cannot be empty")

        return await self._bulk_update_status(
            time_entry_ids, TimeEntryStatus.SUBMITTED, {"notes": notes} if notes else {}
        )

    async def approve_entries(
        self,
        time_entry_ids: List[str],
        approval_notes: Optional[str] = None,
    ) -> List[TimeEntry]:
        """Approve time entries.

        Args:
            time_entry_ids: List of time entry IDs to approve
            approval_notes: Optional approval notes

        Returns:
            List of approved time entries

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not time_entry_ids:
            raise SuperOpsValidationError("Time entry IDs list cannot be empty")

        return await self._bulk_approve_entries(
            time_entry_ids, TimeEntryStatus.APPROVED, approval_notes
        )

    async def reject_entries(
        self,
        time_entry_ids: List[str],
        rejection_notes: str,
    ) -> List[TimeEntry]:
        """Reject time entries.

        Args:
            time_entry_ids: List of time entry IDs to reject
            rejection_notes: Required rejection notes

        Returns:
            List of rejected time entries

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not time_entry_ids:
            raise SuperOpsValidationError("Time entry IDs list cannot be empty")
        if not rejection_notes:
            raise SuperOpsValidationError("Rejection notes are required")

        return await self._bulk_approve_entries(
            time_entry_ids, TimeEntryStatus.REJECTED, rejection_notes
        )

    async def get_pending_approval(
        self,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        client_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        """Get time entries pending approval.

        Args:
            user_id: Optional user ID filter
            project_id: Optional project ID filter
            client_id: Optional client ID filter
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            Dictionary containing 'items' (List[TimeEntry]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Getting time entries pending approval")

        filters = {"status": TimeEntryStatus.SUBMITTED.value}

        if user_id:
            filters["user_id"] = user_id
        if project_id:
            filters["project_id"] = project_id
        if client_id:
            filters["client_id"] = client_id

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by="created_at",
            sort_order="asc",
        )

    # Helper Methods

    async def _bulk_update_status(
        self,
        time_entry_ids: List[str],
        new_status: TimeEntryStatus,
        additional_data: Optional[Dict[str, Any]] = None,
    ) -> List[TimeEntry]:
        """Bulk update status for multiple time entries.

        Args:
            time_entry_ids: List of time entry IDs
            new_status: New status for all entries
            additional_data: Optional additional data to update

        Returns:
            List of updated time entries

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If any API request fails
        """
        if not time_entry_ids:
            raise SuperOpsValidationError("Time entry IDs list cannot be empty")

        self.logger.debug(
            f"Bulk updating status for {len(time_entry_ids)} time entries to {new_status.value}"
        )

        updated_entries = []
        for entry_id in time_entry_ids:
            try:
                update_data = {"status": new_status.value}
                if additional_data:
                    update_data.update(additional_data)

                entry = await self.update(entry_id, update_data)
                updated_entries.append(entry)
            except Exception as e:
                self.logger.error(f"Failed to update time entry {entry_id}: {e}")

        self.logger.info(
            f"Successfully updated {len(updated_entries)} out of {len(time_entry_ids)} entries"
        )
        return updated_entries

    # Bulk Operations

    async def bulk_update_billable_status(
        self,
        time_entry_ids: List[str],
        is_billable: bool,
        hourly_rate: Optional[float] = None,
    ) -> List[TimeEntry]:
        """Bulk update billable status for time entries.

        Args:
            time_entry_ids: List of time entry IDs
            is_billable: Whether entries should be billable
            hourly_rate: Optional hourly rate for billable entries

        Returns:
            List of updated time entries

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If any API request fails
        """
        if is_billable:
            return await self.mark_as_billable(time_entry_ids, hourly_rate)
        else:
            return await self.mark_as_non_billable(time_entry_ids)

    async def bulk_update_category(
        self,
        time_entry_ids: List[str],
        work_category: str,
        entry_type: Optional[TimeEntryType] = None,
    ) -> List[TimeEntry]:
        """Bulk update work category for time entries.

        Args:
            time_entry_ids: List of time entry IDs
            work_category: New work category
            entry_type: Optional entry type

        Returns:
            List of updated time entries

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If any API request fails
        """
        if not time_entry_ids:
            raise SuperOpsValidationError("Time entry IDs list cannot be empty")
        if not work_category:
            raise SuperOpsValidationError("Work category must be provided")

        self.logger.debug(f"Bulk updating category for {len(time_entry_ids)} time entries")

        update_data = {"work_category": work_category}
        if entry_type:
            update_data["entry_type"] = entry_type.value

        updated_entries = []
        for entry_id in time_entry_ids:
            try:
                entry = await self.update(entry_id, update_data)
                updated_entries.append(entry)
            except Exception as e:
                self.logger.error(f"Failed to update time entry {entry_id}: {e}")

        self.logger.info(
            f"Successfully updated {len(updated_entries)} out of {len(time_entry_ids)} entries"
        )
        return updated_entries

    async def bulk_add_tags(
        self,
        time_entry_ids: List[str],
        tags: List[str],
    ) -> List[TimeEntry]:
        """Bulk add tags to time entries.

        Args:
            time_entry_ids: List of time entry IDs
            tags: Tags to add

        Returns:
            List of updated time entries

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If any API request fails
        """
        if not time_entry_ids:
            raise SuperOpsValidationError("Time entry IDs list cannot be empty")
        if not tags:
            raise SuperOpsValidationError("Tags list cannot be empty")

        self.logger.debug(f"Bulk adding tags to {len(time_entry_ids)} time entries")

        updated_entries = []
        for entry_id in time_entry_ids:
            try:
                # First get the existing entry to merge tags
                existing_entry = await self.get(entry_id)
                if existing_entry:
                    existing_tags = set(existing_entry.tags or [])
                    new_tags = existing_tags.union(set(tags))

                    entry = await self.update(entry_id, {"tags": list(new_tags)})
                    updated_entries.append(entry)
            except Exception as e:
                self.logger.error(f"Failed to add tags to time entry {entry_id}: {e}")

        self.logger.info(
            f"Successfully added tags to {len(updated_entries)} out of {len(time_entry_ids)} entries"
        )
        return updated_entries

    # Reporting and Analytics

    async def get_time_summary(
        self,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        client_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: str = "day",  # day, week, month, project, user
    ) -> Dict[str, Any]:
        """Get time summary report with aggregated data.

        Args:
            user_id: Optional user ID filter
            project_id: Optional project ID filter
            client_id: Optional client ID filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            group_by: Grouping method (day, week, month, project, user)

        Returns:
            Dictionary with summary data

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if group_by not in ["day", "week", "month", "project", "user", "category"]:
            raise SuperOpsValidationError(
                "group_by must be one of: day, week, month, project, user, category"
            )

        self.logger.debug(f"Getting time summary grouped by {group_by}")

        query = """
            query GetTimeSummary(
                $userId: ID
                $projectId: ID
                $clientId: ID
                $startDate: DateTime
                $endDate: DateTime
                $groupBy: String!
            ) {
                timeSummary(
                    userId: $userId
                    projectId: $projectId
                    clientId: $clientId
                    startDate: $startDate
                    endDate: $endDate
                    groupBy: $groupBy
                ) {
                    totalMinutes
                    billableMinutes
                    nonBillableMinutes
                    totalAmount
                    entryCount
                    groups {
                        key
                        label
                        totalMinutes
                        billableMinutes
                        nonBillableMinutes
                        totalAmount
                        entryCount
                    }
                }
            }
        """

        variables = {
            "groupBy": group_by,
        }

        if user_id:
            variables["userId"] = user_id
        if project_id:
            variables["projectId"] = project_id
        if client_id:
            variables["clientId"] = client_id
        if start_date:
            variables["startDate"] = start_date.isoformat()
        if end_date:
            variables["endDate"] = end_date.isoformat()

        response = await self.client.execute_query(query, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned for time summary", 500, response)

        summary_data = response["data"].get("timeSummary")
        if not summary_data:
            return {
                "total_minutes": 0,
                "billable_minutes": 0,
                "non_billable_minutes": 0,
                "total_amount": 0.0,
                "entry_count": 0,
                "groups": [],
            }

        return {
            "total_minutes": summary_data.get("totalMinutes", 0),
            "billable_minutes": summary_data.get("billableMinutes", 0),
            "non_billable_minutes": summary_data.get("nonBillableMinutes", 0),
            "total_amount": summary_data.get("totalAmount", 0.0),
            "entry_count": summary_data.get("entryCount", 0),
            "groups": summary_data.get("groups", []),
        }

    async def get_user_time_report(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        include_details: bool = False,
    ) -> Dict[str, Any]:
        """Get detailed time report for a specific user.

        Args:
            user_id: User ID
            start_date: Report start date
            end_date: Report end date
            include_details: Whether to include individual time entries

        Returns:
            Dictionary with user time report

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not user_id:
            raise SuperOpsValidationError("User ID is required")
        if start_date >= end_date:
            raise SuperOpsValidationError("Start date must be before end date")

        self.logger.debug(f"Getting time report for user {user_id} from {start_date} to {end_date}")

        # Get summary data
        summary = await self.get_time_summary(
            user_id=user_id, start_date=start_date, end_date=end_date, group_by="day"
        )

        report = {
            "user_id": user_id,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "summary": summary,
        }

        if include_details:
            # Get detailed time entries
            entries_result = await self.get_by_user(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                page_size=1000,  # Large page size to get all entries
            )
            report["entries"] = entries_result["items"]

        return report

    async def get_project_time_report(
        self,
        project_id: str,
        start_date: datetime,
        end_date: datetime,
        include_user_breakdown: bool = True,
    ) -> Dict[str, Any]:
        """Get detailed time report for a specific project.

        Args:
            project_id: Project ID
            start_date: Report start date
            end_date: Report end date
            include_user_breakdown: Whether to include breakdown by user

        Returns:
            Dictionary with project time report

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not project_id:
            raise SuperOpsValidationError("Project ID is required")
        if start_date >= end_date:
            raise SuperOpsValidationError("Start date must be before end date")

        self.logger.debug(
            f"Getting time report for project {project_id} from {start_date} to {end_date}"
        )

        # Get summary data
        summary = await self.get_time_summary(
            project_id=project_id, start_date=start_date, end_date=end_date, group_by="day"
        )

        report = {
            "project_id": project_id,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "summary": summary,
        }

        if include_user_breakdown:
            # Get breakdown by user
            user_breakdown = await self.get_time_summary(
                project_id=project_id, start_date=start_date, end_date=end_date, group_by="user"
            )
            report["user_breakdown"] = user_breakdown["groups"]

        return report

    async def get_weekly_timesheet(
        self,
        user_id: str,
        week_start: datetime,
    ) -> Dict[str, Any]:
        """Get weekly timesheet for a user.

        Args:
            user_id: User ID
            week_start: Start of the week (Monday)

        Returns:
            Dictionary with weekly timesheet data

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not user_id:
            raise SuperOpsValidationError("User ID is required")

        # Calculate week end (Sunday)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)

        self.logger.debug(
            f"Getting weekly timesheet for user {user_id} for week starting {week_start}"
        )

        # Get time entries for the week
        entries_result = await self.get_by_user(
            user_id=user_id,
            start_date=week_start,
            end_date=week_end,
            page_size=1000,  # Large page size to get all entries
            sort_by="start_time",
            sort_order="asc",
        )

        # Group entries by day
        daily_entries = {}
        total_minutes = 0
        billable_minutes = 0

        for entry in entries_result["items"]:
            entry_date = entry.start_time.date()
            day_name = entry_date.strftime("%A")

            if day_name not in daily_entries:
                daily_entries[day_name] = {
                    "date": entry_date.isoformat(),
                    "entries": [],
                    "total_minutes": 0,
                    "billable_minutes": 0,
                }

            daily_entries[day_name]["entries"].append(entry)
            entry_minutes = entry.duration_minutes or 0
            daily_entries[day_name]["total_minutes"] += entry_minutes
            total_minutes += entry_minutes

            if entry.is_billable:
                daily_entries[day_name]["billable_minutes"] += entry_minutes
                billable_minutes += entry_minutes

        return {
            "user_id": user_id,
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "total_minutes": total_minutes,
            "billable_minutes": billable_minutes,
            "non_billable_minutes": total_minutes - billable_minutes,
            "daily_breakdown": daily_entries,
        }

    # Time Entry Templates

    async def create_template(
        self,
        name: str,
        description: str,
        user_id: str,
        default_duration_minutes: Optional[int] = None,
        entry_type: TimeEntryType = TimeEntryType.WORK,
        is_billable: bool = True,
        work_category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        custom_fields: Optional[Dict[str, Any]] = None,
    ) -> TimeEntryTemplate:
        """Create a time entry template.

        Args:
            name: Template name
            description: Template description
            user_id: User ID who owns the template
            default_duration_minutes: Default duration in minutes
            entry_type: Default entry type
            is_billable: Default billable status
            work_category: Default work category
            tags: Default tags
            custom_fields: Default custom fields

        Returns:
            Created template instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not name or not isinstance(name, str):
            raise SuperOpsValidationError("Template name must be a non-empty string")
        if not description or not isinstance(description, str):
            raise SuperOpsValidationError("Template description must be a non-empty string")
        if not user_id or not isinstance(user_id, str):
            raise SuperOpsValidationError("User ID must be a non-empty string")

        self.logger.debug(f"Creating time entry template: {name}")

        mutation = """
            mutation CreateTimeEntryTemplate($input: CreateTimeEntryTemplateInput!) {
                createTimeEntryTemplate(input: $input) {
                    id
                    name
                    description
                    userId
                    defaultDurationMinutes
                    entryType
                    isBillable
                    workCategory
                    tags
                    customFields
                    isActive
                    createdAt
                    updatedAt
                }
            }
        """

        variables = {
            "input": {
                "name": name,
                "description": description,
                "user_id": user_id,
                "default_duration_minutes": default_duration_minutes,
                "entry_type": entry_type.value,
                "is_billable": is_billable,
                "work_category": work_category,
                "tags": tags or [],
                "custom_fields": custom_fields or {},
            }
        }

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when creating template", 500, response)

        template_data = response["data"].get("createTimeEntryTemplate")
        if not template_data:
            raise SuperOpsAPIError("No template data in response", 500, response)

        return TimeEntryTemplate.from_dict(template_data)

    async def create_from_template(
        self,
        template_id: str,
        user_id: str,
        start_time: datetime,
        override_data: Optional[Dict[str, Any]] = None,
    ) -> TimeEntry:
        """Create a time entry from a template.

        Args:
            template_id: Template ID
            user_id: User ID for the new time entry
            start_time: Start time for the new time entry
            override_data: Optional data to override template defaults

        Returns:
            Created time entry instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not template_id or not isinstance(template_id, str):
            raise SuperOpsValidationError("Template ID must be a non-empty string")
        if not user_id or not isinstance(user_id, str):
            raise SuperOpsValidationError("User ID must be a non-empty string")

        self.logger.debug(f"Creating time entry from template {template_id}")

        # Get template details
        template_query = """
            query GetTimeEntryTemplate($id: ID!) {
                timeEntryTemplate(id: $id) {
                    id
                    name
                    description
                    defaultDurationMinutes
                    entryType
                    isBillable
                    workCategory
                    tags
                    customFields
                }
            }
        """

        template_response = await self.client.execute_query(template_query, {"id": template_id})

        if not template_response.get("data") or not template_response["data"].get(
            "timeEntryTemplate"
        ):
            raise SuperOpsAPIError(f"Template {template_id} not found", 404, {})

        template = template_response["data"]["timeEntryTemplate"]

        # Build time entry data from template
        entry_data = {
            "user_id": user_id,
            "description": template["description"],
            "start_time": start_time,
            "entry_type": template["entryType"],
            "is_billable": template["isBillable"],
            "work_category": template.get("workCategory"),
            "tags": template.get("tags", []),
            "custom_fields": template.get("customFields", {}),
        }

        # Add end time if default duration is specified
        if template.get("defaultDurationMinutes"):
            end_time = start_time + timedelta(minutes=template["defaultDurationMinutes"])
            entry_data["end_time"] = end_time
            entry_data["duration_minutes"] = template["defaultDurationMinutes"]

        # Apply any overrides
        if override_data:
            entry_data.update(override_data)

        return await self.create(entry_data)

    async def _bulk_approve_entries(
        self,
        time_entry_ids: List[str],
        status: TimeEntryStatus,
        approval_notes: Optional[str] = None,
    ) -> List[TimeEntry]:
        """Bulk approve or reject time entries using specialized mutation.

        Args:
            time_entry_ids: List of time entry IDs
            status: Approval status (APPROVED or REJECTED)
            approval_notes: Optional approval/rejection notes

        Returns:
            List of updated time entries

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if status not in (TimeEntryStatus.APPROVED, TimeEntryStatus.REJECTED):
            raise SuperOpsValidationError("Status must be APPROVED or REJECTED")

        self.logger.debug(f"Bulk {status.value.lower()}ing {len(time_entry_ids)} time entries")

        mutation = """
            mutation BulkApproveTimeEntries($input: TimeEntryApprovalInput!) {
                bulkApproveTimeEntries(input: $input) {
                    timeEntries {
                        id
                        status
                        approvalNotes
                        approvedBy
                        approvedAt
                        updatedAt
                    }
                    success
                    message
                }
            }
        """

        variables = {
            "input": {
                "time_entry_ids": time_entry_ids,
                "status": status.value,
                "approval_notes": approval_notes,
            }
        }

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when bulk approving entries", 500, response)

        approval_data = response["data"].get("bulkApproveTimeEntries")
        if not approval_data:
            raise SuperOpsAPIError("No approval data in response", 500, response)

        if not approval_data.get("success"):
            error_msg = approval_data.get("message", "Bulk approval failed")
            raise SuperOpsAPIError(error_msg, 400, response)

        entries_data = approval_data.get("timeEntries", [])
        updated_entries = [TimeEntry.from_dict(entry) for entry in entries_data]

        self.logger.info(
            f"Successfully {status.value.lower()}ed {len(updated_entries)} time entries"
        )
        return updated_entries

    # Protected methods for GraphQL query building

    def _build_get_query(self, **kwargs) -> str:
        """Build GraphQL query for getting a single time entry."""
        return """
            query GetTimeEntry($id: ID!) {
                timeEntry(id: $id) {
                    id
                    userId
                    description
                    startTime
                    endTime
                    durationMinutes
                    ticketId
                    taskId
                    projectId
                    clientId
                    status
                    entryType
                    isBillable
                    hourlyRate
                    totalAmount
                    workCategory
                    notes
                    approvalNotes
                    approvedBy
                    approvedAt
                    tags
                    customFields
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_list_query(self, **kwargs) -> str:
        """Build GraphQL query for listing time entries."""
        return """
            query ListTimeEntries(
                $page: Int!
                $pageSize: Int!
                $filters: TimeEntryFilter
                $sortBy: String
                $sortOrder: SortOrder
            ) {
                timeEntries(
                    page: $page
                    pageSize: $pageSize
                    filters: $filters
                    sortBy: $sortBy
                    sortOrder: $sortOrder
                ) {
                    items {
                        id
                        userId
                        description
                        startTime
                        endTime
                        durationMinutes
                        ticketId
                        taskId
                        projectId
                        clientId
                        status
                        entryType
                        isBillable
                        hourlyRate
                        totalAmount
                        workCategory
                        notes
                        approvalNotes
                        approvedBy
                        approvedAt
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
        """Build GraphQL mutation for creating a time entry."""
        return """
            mutation CreateTimeEntry($input: CreateTimeEntryInput!) {
                createTimeEntry(input: $input) {
                    id
                    userId
                    description
                    startTime
                    endTime
                    durationMinutes
                    ticketId
                    taskId
                    projectId
                    clientId
                    status
                    entryType
                    isBillable
                    hourlyRate
                    totalAmount
                    workCategory
                    notes
                    tags
                    customFields
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_update_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for updating a time entry."""
        return """
            mutation UpdateTimeEntry($id: ID!, $input: UpdateTimeEntryInput!) {
                updateTimeEntry(id: $id, input: $input) {
                    id
                    userId
                    description
                    startTime
                    endTime
                    durationMinutes
                    ticketId
                    taskId
                    projectId
                    clientId
                    status
                    entryType
                    isBillable
                    hourlyRate
                    totalAmount
                    workCategory
                    notes
                    approvalNotes
                    approvedBy
                    approvedAt
                    tags
                    customFields
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_delete_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for deleting a time entry."""
        return """
            mutation DeleteTimeEntry($id: ID!) {
                deleteTimeEntry(id: $id) {
                    success
                    message
                }
            }
        """

    def _build_search_query(self, **kwargs) -> str:
        """Build GraphQL query for searching time entries."""
        return """
            query SearchTimeEntries(
                $query: String!
                $page: Int!
                $pageSize: Int!
            ) {
                searchTimeEntries(
                    query: $query
                    page: $page
                    pageSize: $pageSize
                ) {
                    items {
                        id
                        userId
                        description
                        startTime
                        endTime
                        durationMinutes
                        ticketId
                        taskId
                        projectId
                        clientId
                        status
                        entryType
                        isBillable
                        hourlyRate
                        totalAmount
                        workCategory
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
        """Validate data for time entry creation."""
        validated = data.copy()

        # Required fields
        if not validated.get("user_id"):
            raise SuperOpsValidationError("User ID is required")
        if not validated.get("description"):
            raise SuperOpsValidationError("Description is required")
        if not validated.get("start_time"):
            raise SuperOpsValidationError("Start time is required")

        # Validate status if provided
        status = validated.get("status")
        if status and status not in [s.value for s in TimeEntryStatus]:
            raise SuperOpsValidationError(f"Invalid time entry status: {status}")

        # Validate entry type if provided
        entry_type = validated.get("entry_type")
        if entry_type and entry_type not in [t.value for t in TimeEntryType]:
            raise SuperOpsValidationError(f"Invalid time entry type: {entry_type}")

        # Validate time fields
        start_time = validated.get("start_time")
        end_time = validated.get("end_time")

        if isinstance(start_time, str):
            try:
                datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            except ValueError:
                raise SuperOpsValidationError("Invalid start_time format. Use ISO format.")

        if end_time and isinstance(end_time, str):
            try:
                datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            except ValueError:
                raise SuperOpsValidationError("Invalid end_time format. Use ISO format.")

        return validated

    def _validate_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data for time entry updates."""
        validated = data.copy()

        # Validate status if provided
        status = validated.get("status")
        if status and status not in [s.value for s in TimeEntryStatus]:
            raise SuperOpsValidationError(f"Invalid time entry status: {status}")

        # Validate entry type if provided
        entry_type = validated.get("entry_type")
        if entry_type and entry_type not in [t.value for t in TimeEntryType]:
            raise SuperOpsValidationError(f"Invalid time entry type: {entry_type}")

        # Validate time fields
        start_time = validated.get("start_time")
        end_time = validated.get("end_time")

        if start_time and isinstance(start_time, str):
            try:
                datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            except ValueError:
                raise SuperOpsValidationError("Invalid start_time format. Use ISO format.")

        if end_time and isinstance(end_time, str):
            try:
                datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            except ValueError:
                raise SuperOpsValidationError("Invalid end_time format. Use ISO format.")

        return validated
