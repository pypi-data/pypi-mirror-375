# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Tests for TimeEntriesManager."""

from datetime import datetime, timezone
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from py_superops.exceptions import (
    SuperOpsAPIError,
    SuperOpsResourceNotFoundError,
    SuperOpsValidationError,
)
from py_superops.graphql.types import TimeEntryStatus, TimeEntryType, TimerState
from py_superops.managers import TimeEntriesManager


class TestTimeEntriesManager:
    """Test the TimeEntriesManager class."""

    @pytest.fixture
    def manager(self, mock_client):
        """Create a TimeEntriesManager instance for testing."""
        return TimeEntriesManager(mock_client)

    def test_initialization(self, manager):
        """Test TimeEntriesManager initialization."""
        assert manager._resource_name == "timeEntry"
        assert manager._resource_plural == "timeEntries"
        assert manager._graphql_type == "TimeEntry"

    @pytest.mark.asyncio
    async def test_start_timer_success(self, manager, mock_client):
        """Test successful timer start."""
        # Mock response
        mock_response = {
            "data": {
                "startTimer": {
                    "id": "timer-123",
                    "userId": "user-456",
                    "state": "RUNNING",
                    "description": "Working on bug fix",
                    "startTime": "2024-01-01T10:00:00Z",
                    "ticketId": "ticket-789",
                }
            }
        }
        mock_client.execute_mutation.return_value = mock_response

        # Test timer start
        result = await manager.start_timer(
            user_id="user-456",
            description="Working on bug fix",
            ticket_id="ticket-789",
            entry_type=TimeEntryType.WORK,
            is_billable=True,
        )

        # Verify result
        assert result["id"] == "timer-123"
        assert result["state"] == "RUNNING"
        assert result["description"] == "Working on bug fix"

        # Verify GraphQL call
        mock_client.execute_mutation.assert_called_once()
        call_args = mock_client.execute_mutation.call_args
        assert "startTimer" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_stop_timer_success(self, manager, mock_client):
        """Test successful timer stop."""
        # Mock response
        mock_response = {
            "data": {
                "stopTimer": {
                    "id": "entry-123",
                    "userId": "user-456",
                    "description": "Completed bug fix",
                    "startTime": "2024-01-01T10:00:00Z",
                    "endTime": "2024-01-01T12:00:00Z",
                    "durationMinutes": 120,
                    "status": "DRAFT",
                }
            }
        }
        mock_client.execute_mutation.return_value = mock_response

        # Test timer stop
        result = await manager.stop_timer(timer_id="timer-123", description="Completed bug fix")

        # Verify result
        assert result["id"] == "entry-123"
        assert result["durationMinutes"] == 120
        assert result["status"] == "DRAFT"

        # Verify GraphQL call
        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_pause_timer_success(self, manager, mock_client):
        """Test successful timer pause."""
        # Mock response
        mock_response = {
            "data": {
                "pauseTimer": {
                    "id": "timer-123",
                    "state": "PAUSED",
                    "elapsedMinutes": 45,
                    "pausedAt": "2024-01-01T10:45:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = mock_response

        # Test timer pause
        result = await manager.pause_timer("timer-123")

        # Verify result
        assert result["id"] == "timer-123"
        assert result["state"] == "PAUSED"
        assert result["elapsedMinutes"] == 45

    @pytest.mark.asyncio
    async def test_resume_timer_success(self, manager, mock_client):
        """Test successful timer resume."""
        # Mock response
        mock_response = {
            "data": {
                "resumeTimer": {
                    "id": "timer-123",
                    "state": "RUNNING",
                    "resumedAt": "2024-01-01T11:15:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = mock_response

        # Test timer resume
        result = await manager.resume_timer("timer-123")

        # Verify result
        assert result["id"] == "timer-123"
        assert result["state"] == "RUNNING"

    @pytest.mark.asyncio
    async def test_get_active_timers(self, manager, mock_client):
        """Test retrieving active timers."""
        # Mock response
        mock_response = {
            "data": {
                "timers": {
                    "items": [
                        {
                            "id": "timer-123",
                            "userId": "user-456",
                            "state": "RUNNING",
                            "description": "Bug fix work",
                            "startTime": "2024-01-01T10:00:00Z",
                        },
                        {
                            "id": "timer-456",
                            "userId": "user-456",
                            "state": "PAUSED",
                            "description": "Documentation",
                            "startTime": "2024-01-01T09:00:00Z",
                            "pausedAt": "2024-01-01T09:30:00Z",
                        },
                    ],
                    "pagination": {"page": 1, "pageSize": 50, "total": 2, "hasNextPage": False},
                }
            }
        }
        mock_client.execute_query.return_value = mock_response

        # Test get active timers
        result = await manager.get_active_timers("user-456")

        # Verify result
        assert len(result["items"]) == 2
        assert result["items"][0]["state"] == "RUNNING"
        assert result["items"][1]["state"] == "PAUSED"

    @pytest.mark.asyncio
    async def test_submit_for_approval(self, manager, mock_client):
        """Test submitting time entries for approval."""
        # Mock response
        mock_response = {
            "data": {
                "submitTimeEntriesForApproval": [
                    {
                        "id": "entry-123",
                        "status": "SUBMITTED",
                        "submittedAt": "2024-01-01T15:00:00Z",
                    },
                    {
                        "id": "entry-456",
                        "status": "SUBMITTED",
                        "submittedAt": "2024-01-01T15:00:00Z",
                    },
                ]
            }
        }
        mock_client.execute_mutation.return_value = mock_response

        # Test submit for approval
        result = await manager.submit_for_approval(["entry-123", "entry-456"])

        # Verify result
        assert len(result) == 2
        assert result[0]["status"] == "SUBMITTED"
        assert result[1]["status"] == "SUBMITTED"

    @pytest.mark.asyncio
    async def test_approve_entries(self, manager, mock_client):
        """Test approving time entries."""
        # Mock response
        mock_response = {
            "data": {
                "approveTimeEntries": [
                    {
                        "id": "entry-123",
                        "status": "APPROVED",
                        "approvedAt": "2024-01-01T16:00:00Z",
                        "approvedBy": "manager-123",
                    }
                ]
            }
        }
        mock_client.execute_mutation.return_value = mock_response

        # Test approve entries
        result = await manager.approve_entries(
            ["entry-123"], approver_id="manager-123", comments="Good work!"
        )

        # Verify result
        assert len(result) == 1
        assert result[0]["status"] == "APPROVED"
        assert result[0]["approvedBy"] == "manager-123"

    @pytest.mark.asyncio
    async def test_reject_entries(self, manager, mock_client):
        """Test rejecting time entries."""
        # Mock response
        mock_response = {
            "data": {
                "rejectTimeEntries": [
                    {
                        "id": "entry-123",
                        "status": "REJECTED",
                        "rejectedAt": "2024-01-01T16:00:00Z",
                        "rejectedBy": "manager-123",
                        "rejectionReason": "Insufficient details",
                    }
                ]
            }
        }
        mock_client.execute_mutation.return_value = mock_response

        # Test reject entries
        result = await manager.reject_entries(
            ["entry-123"], rejector_id="manager-123", reason="Insufficient details"
        )

        # Verify result
        assert len(result) == 1
        assert result[0]["status"] == "REJECTED"
        assert result[0]["rejectionReason"] == "Insufficient details"

    @pytest.mark.asyncio
    async def test_get_time_summary(self, manager, mock_client):
        """Test getting time summary."""
        # Mock response
        mock_response = {
            "data": {
                "timeEntrySummary": {
                    "totalHours": 40.5,
                    "billableHours": 32.0,
                    "nonBillableHours": 8.5,
                    "entriesCount": 15,
                    "groups": [
                        {
                            "groupKey": "2024-01-01",
                            "totalHours": 8.0,
                            "billableHours": 6.5,
                            "nonBillableHours": 1.5,
                            "entriesCount": 3,
                        },
                        {
                            "groupKey": "2024-01-02",
                            "totalHours": 7.5,
                            "billableHours": 7.5,
                            "nonBillableHours": 0.0,
                            "entriesCount": 2,
                        },
                    ],
                }
            }
        }
        mock_client.execute_query.return_value = mock_response

        # Test get time summary
        result = await manager.get_time_summary(
            start_date="2024-01-01T00:00:00Z",
            end_date="2024-01-07T23:59:59Z",
            user_id="user-456",
            group_by="day",
        )

        # Verify result
        assert result["totalHours"] == 40.5
        assert result["billableHours"] == 32.0
        assert len(result["groups"]) == 2

    @pytest.mark.asyncio
    async def test_get_weekly_timesheet(self, manager, mock_client):
        """Test getting weekly timesheet."""
        # Mock response
        mock_response = {
            "data": {
                "weeklyTimesheet": {
                    "weekStart": "2024-01-01T00:00:00Z",
                    "weekEnd": "2024-01-07T23:59:59Z",
                    "totalHours": 35.5,
                    "entries": [
                        {
                            "id": "entry-123",
                            "date": "2024-01-01",
                            "description": "Bug fix work",
                            "durationMinutes": 240,
                            "ticketId": "ticket-789",
                        }
                    ],
                }
            }
        }
        mock_client.execute_query.return_value = mock_response

        # Test get weekly timesheet
        result = await manager.get_weekly_timesheet(
            user_id="user-456", week_start="2024-01-01T00:00:00Z"
        )

        # Verify result
        assert result["totalHours"] == 35.5
        assert len(result["entries"]) == 1
        assert result["entries"][0]["description"] == "Bug fix work"

    @pytest.mark.asyncio
    async def test_create_template(self, manager, mock_client):
        """Test creating a time entry template."""
        # Mock response
        mock_response = {
            "data": {
                "createTimeEntryTemplate": {
                    "id": "template-123",
                    "name": "Bug Fix Template",
                    "description": "Standard bug fix workflow",
                    "entryType": "WORK",
                    "isBillable": True,
                    "estimatedDurationMinutes": 120,
                }
            }
        }
        mock_client.execute_mutation.return_value = mock_response

        # Test create template
        result = await manager.create_template(
            name="Bug Fix Template",
            description="Standard bug fix workflow",
            entry_type=TimeEntryType.WORK,
            is_billable=True,
            estimated_duration_minutes=120,
            created_by="user-456",
        )

        # Verify result
        assert result["id"] == "template-123"
        assert result["name"] == "Bug Fix Template"
        assert result["entryType"] == "WORK"

    @pytest.mark.asyncio
    async def test_create_from_template(self, manager, mock_client):
        """Test creating time entry from template."""
        # Mock response
        mock_response = {
            "data": {
                "createTimeEntryFromTemplate": {
                    "id": "entry-789",
                    "description": "Standard bug fix workflow",
                    "entryType": "WORK",
                    "isBillable": True,
                    "userId": "user-456",
                    "ticketId": "ticket-123",
                }
            }
        }
        mock_client.execute_mutation.return_value = mock_response

        # Test create from template
        result = await manager.create_from_template(
            template_id="template-123",
            user_id="user-456",
            start_time="2024-01-01T10:00:00Z",
            ticket_id="ticket-123",
        )

        # Verify result
        assert result["id"] == "entry-789"
        assert result["entryType"] == "WORK"
        assert result["userId"] == "user-456"

    @pytest.mark.asyncio
    async def test_bulk_update_status(self, manager, mock_client):
        """Test bulk status update."""
        # Mock response
        mock_response = {
            "data": {
                "bulkUpdateTimeEntryStatus": [
                    {"id": "entry-123", "status": "SUBMITTED"},
                    {"id": "entry-456", "status": "SUBMITTED"},
                ]
            }
        }
        mock_client.execute_mutation.return_value = mock_response

        # Test bulk update
        result = await manager.bulk_update_status(
            ["entry-123", "entry-456"], TimeEntryStatus.SUBMITTED
        )

        # Verify result
        assert len(result) == 2
        assert all(entry["status"] == "SUBMITTED" for entry in result)

    @pytest.mark.asyncio
    async def test_bulk_update_billable(self, manager, mock_client):
        """Test bulk billable update."""
        # Mock response
        mock_response = {
            "data": {
                "bulkUpdateTimeEntryBillable": [
                    {"id": "entry-123", "isBillable": False},
                    {"id": "entry-456", "isBillable": False},
                ]
            }
        }
        mock_client.execute_mutation.return_value = mock_response

        # Test bulk update billable
        result = await manager.bulk_update_billable(["entry-123", "entry-456"], is_billable=False)

        # Verify result
        assert len(result) == 2
        assert all(not entry["isBillable"] for entry in result)

    @pytest.mark.asyncio
    async def test_list_by_user(self, manager, mock_client):
        """Test listing time entries by user."""
        # Mock response
        mock_response = {
            "data": {
                "timeEntries": {
                    "items": [
                        {
                            "id": "entry-123",
                            "userId": "user-456",
                            "description": "Bug fix work",
                            "status": "APPROVED",
                        }
                    ],
                    "pagination": {"page": 1, "pageSize": 25, "total": 1, "hasNextPage": False},
                }
            }
        }
        mock_client.execute_query.return_value = mock_response

        # Test list by user
        result = await manager.list_by_user("user-456", page_size=25)

        # Verify result
        assert len(result["items"]) == 1
        assert result["items"][0]["userId"] == "user-456"

    @pytest.mark.asyncio
    async def test_get_pending_approval(self, manager, mock_client):
        """Test getting entries pending approval."""
        # Mock response
        mock_response = {
            "data": {
                "timeEntries": {
                    "items": [
                        {
                            "id": "entry-123",
                            "status": "SUBMITTED",
                            "submittedAt": "2024-01-01T15:00:00Z",
                        }
                    ],
                    "pagination": {"page": 1, "pageSize": 50, "total": 1, "hasNextPage": False},
                }
            }
        }
        mock_client.execute_query.return_value = mock_response

        # Test get pending approval
        result = await manager.get_pending_approval()

        # Verify result
        assert len(result["items"]) == 1
        assert result["items"][0]["status"] == "SUBMITTED"

    @pytest.mark.asyncio
    async def test_export_time_entries(self, manager, mock_client):
        """Test exporting time entries."""
        # Mock response
        mock_response = {
            "data": {
                "exportTimeEntries": {
                    "format": "json",
                    "entries": [
                        {"id": "entry-123", "description": "Bug fix", "durationMinutes": 120}
                    ],
                    "summary": {"totalEntries": 1, "totalHours": 2.0},
                }
            }
        }
        mock_client.execute_query.return_value = mock_response

        # Test export
        result = await manager.export_time_entries(
            start_date="2024-01-01T00:00:00Z", end_date="2024-01-07T23:59:59Z", format="json"
        )

        # Verify result
        assert result["format"] == "json"
        assert len(result["entries"]) == 1
        assert result["summary"]["totalHours"] == 2.0

    @pytest.mark.asyncio
    async def test_error_handling(self, manager, mock_client):
        """Test error handling in timer operations."""
        # Mock error response
        mock_client.execute_mutation.side_effect = SuperOpsAPIError("Timer not found")

        # Test error handling
        with pytest.raises(SuperOpsAPIError):
            await manager.stop_timer("invalid-timer")

    @pytest.mark.asyncio
    async def test_validation_error(self, manager):
        """Test validation errors."""
        # Test invalid timer operation
        with pytest.raises(SuperOpsValidationError):
            await manager.start_timer(
                user_id="", description="Test"  # Empty user ID should fail validation
            )

    @pytest.mark.asyncio
    async def test_get_billable_hours_summary(self, manager, mock_client):
        """Test getting billable hours summary."""
        # Mock response
        mock_response = {
            "data": {
                "billableHoursSummary": {
                    "billableHours": 30.0,
                    "nonBillableHours": 10.0,
                    "totalHours": 40.0,
                    "billablePercentage": 75.0,
                }
            }
        }
        mock_client.execute_query.return_value = mock_response

        # Test get billable hours summary
        result = await manager.get_billable_hours_summary(
            start_date="2024-01-01T00:00:00Z", end_date="2024-01-07T23:59:59Z", user_id="user-456"
        )

        # Verify result
        assert result["billableHours"] == 30.0
        assert result["nonBillableHours"] == 10.0
        assert result["billablePercentage"] == 75.0

    @pytest.mark.asyncio
    async def test_list_templates(self, manager, mock_client):
        """Test listing time entry templates."""
        # Mock response
        mock_response = {
            "data": {
                "timeEntryTemplates": {
                    "items": [
                        {
                            "id": "template-123",
                            "name": "Bug Fix Template",
                            "description": "Standard workflow",
                            "entryType": "WORK",
                        }
                    ],
                    "pagination": {"page": 1, "pageSize": 25, "total": 1, "hasNextPage": False},
                }
            }
        }
        mock_client.execute_query.return_value = mock_response

        # Test list templates
        result = await manager.list_templates()

        # Verify result
        assert len(result["items"]) == 1
        assert result["items"][0]["name"] == "Bug Fix Template"
