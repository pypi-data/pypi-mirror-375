#!/usr/bin/env python3
"""Time Entries Management Workflow Example.

This example demonstrates comprehensive time tracking operations using the py-superops client.
It shows how to use the TimeEntriesManager for:
- Timer functionality (start/stop/pause/resume)
- Time entry CRUD operations
- Approval workflows
- Reporting and analytics
- Template management
- Bulk operations

Example usage:
    python time_entries_workflow.py

Environment variables required:
    SUPEROPS_API_KEY: Your SuperOps API key
    SUPEROPS_BASE_URL: SuperOps API base URL (optional, defaults to production)
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List

from py_superops import SuperOpsClient, SuperOpsConfig
from py_superops.exceptions import SuperOpsError
from py_superops.graphql import TimeEntryStatus, TimeEntryType

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def demonstrate_timer_functionality(
    client: SuperOpsClient, user_id: str, ticket_id: str
) -> dict:
    """Demonstrate timer start/stop/pause/resume functionality."""
    logger.info("=== Timer Functionality Demo ===")

    try:
        # Start a timer for ticket work
        logger.info("Starting timer for ticket work...")
        timer = await client.time_entries.start_timer(
            user_id=user_id,
            description="Working on bug fix implementation",
            ticket_id=ticket_id,
            entry_type=TimeEntryType.WORK,
            is_billable=True,
        )
        logger.info(f"Timer started: {timer['id']}")

        # Simulate some work time
        logger.info("Simulating work... (3 seconds)")
        await asyncio.sleep(3)

        # Pause the timer
        logger.info("Pausing timer...")
        paused_timer = await client.time_entries.pause_timer(timer["id"])
        logger.info(
            f"Timer paused, duration so far: {paused_timer.get('elapsed_minutes', 'N/A')} minutes"
        )

        # Simulate a break
        logger.info("Simulating break... (2 seconds)")
        await asyncio.sleep(2)

        # Resume the timer
        logger.info("Resuming timer...")
        resumed_timer = await client.time_entries.resume_timer(timer["id"])
        logger.info(f"Timer resumed")

        # Simulate more work
        logger.info("Simulating more work... (2 seconds)")
        await asyncio.sleep(2)

        # Stop the timer and create time entry
        logger.info("Stopping timer and creating time entry...")
        time_entry = await client.time_entries.stop_timer(
            timer["id"], description="Completed bug fix implementation and testing"
        )
        logger.info(
            f"Time entry created: {time_entry['id']}, Duration: {time_entry.get('duration_minutes', 'N/A')} minutes"
        )

        return time_entry

    except SuperOpsError as e:
        logger.error(f"Timer operation failed: {e}")
        return None


async def demonstrate_time_entry_crud(client: SuperOpsClient, user_id: str, ticket_id: str) -> dict:
    """Demonstrate time entry CRUD operations."""
    logger.info("=== Time Entry CRUD Demo ===")

    try:
        # Create a manual time entry
        logger.info("Creating manual time entry...")
        start_time = datetime.now() - timedelta(hours=2)
        end_time = datetime.now() - timedelta(hours=1)

        time_entry = await client.time_entries.create(
            user_id=user_id,
            description="Code review and documentation updates",
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            ticket_id=ticket_id,
            entry_type=TimeEntryType.WORK,
            is_billable=True,
            status=TimeEntryStatus.DRAFT,
        )
        logger.info(f"Manual time entry created: {time_entry['id']}")

        # Get the time entry
        logger.info("Retrieving time entry...")
        retrieved_entry = await client.time_entries.get(time_entry["id"])
        logger.info(f"Retrieved: {retrieved_entry['description']}")

        # Update the time entry
        logger.info("Updating time entry description...")
        updated_entry = await client.time_entries.update(
            time_entry["id"],
            description="Code review, documentation updates, and unit tests",
            status=TimeEntryStatus.SUBMITTED,
        )
        logger.info(f"Updated entry status: {updated_entry['status']}")

        # List time entries for the user
        logger.info("Listing user's time entries...")
        user_entries = await client.time_entries.list_by_user(user_id=user_id, page_size=5)
        logger.info(f"Found {len(user_entries['items'])} time entries for user")

        return time_entry

    except SuperOpsError as e:
        logger.error(f"Time entry CRUD operation failed: {e}")
        return None


async def demonstrate_approval_workflow(client: SuperOpsClient, time_entry_ids: List[str]) -> None:
    """Demonstrate time entry approval workflow."""
    logger.info("=== Approval Workflow Demo ===")

    try:
        # Submit entries for approval
        logger.info("Submitting time entries for approval...")
        submitted_entries = await client.time_entries.submit_for_approval(time_entry_ids)
        logger.info(f"Submitted {len(submitted_entries)} entries for approval")

        # Get pending approval entries
        logger.info("Getting entries pending approval...")
        pending_entries = await client.time_entries.get_pending_approval()
        logger.info(f"Found {len(pending_entries['items'])} entries pending approval")

        # Approve entries (simulating manager approval)
        if pending_entries["items"]:
            first_entry_id = pending_entries["items"][0]["id"]
            logger.info(f"Approving entry: {first_entry_id}")

            approved_entries = await client.time_entries.approve_entries(
                [first_entry_id],
                approver_id="manager-user-id",  # Would be actual manager ID
                comments="Good work on the bug fix",
            )
            logger.info(f"Approved {len(approved_entries)} entries")

    except SuperOpsError as e:
        logger.error(f"Approval workflow operation failed: {e}")


async def demonstrate_reporting_analytics(client: SuperOpsClient, user_id: str) -> None:
    """Demonstrate time tracking reporting and analytics."""
    logger.info("=== Reporting & Analytics Demo ===")

    try:
        # Get time summary for current week
        logger.info("Getting weekly time summary...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        weekly_summary = await client.time_entries.get_time_summary(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            user_id=user_id,
            group_by="day",
        )
        logger.info(f"Weekly summary: {weekly_summary['total_hours']} hours total")

        # Get weekly timesheet
        logger.info("Getting weekly timesheet...")
        timesheet = await client.time_entries.get_weekly_timesheet(
            user_id=user_id, week_start=start_date.isoformat()
        )
        logger.info(f"Timesheet contains {len(timesheet.get('entries', []))} entries")

        # Get billable vs non-billable hours
        logger.info("Getting billable hours breakdown...")
        billable_summary = await client.time_entries.get_billable_hours_summary(
            start_date=start_date.isoformat(), end_date=end_date.isoformat(), user_id=user_id
        )
        billable_hours = billable_summary.get("billable_hours", 0)
        non_billable_hours = billable_summary.get("non_billable_hours", 0)
        logger.info(f"Billable: {billable_hours}h, Non-billable: {non_billable_hours}h")

        # Get project time breakdown
        logger.info("Getting project time breakdown...")
        project_summary = await client.time_entries.get_time_summary(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            user_id=user_id,
            group_by="project",
        )
        logger.info(f"Time tracked across {len(project_summary.get('groups', []))} projects")

    except SuperOpsError as e:
        logger.error(f"Reporting operation failed: {e}")


async def demonstrate_template_management(client: SuperOpsClient, user_id: str) -> dict:
    """Demonstrate time entry template functionality."""
    logger.info("=== Template Management Demo ===")

    try:
        # Create a template for common work
        logger.info("Creating time entry template...")
        template = await client.time_entries.create_template(
            name="Bug Fix Template",
            description="Standard bug fix and testing workflow",
            entry_type=TimeEntryType.WORK,
            is_billable=True,
            estimated_duration_minutes=120,
            created_by=user_id,
        )
        logger.info(f"Template created: {template['id']}")

        # List available templates
        logger.info("Listing available templates...")
        templates = await client.time_entries.list_templates()
        logger.info(f"Found {len(templates['items'])} templates available")

        # Use template to create time entry
        logger.info("Using template to create time entry...")
        time_entry_from_template = await client.time_entries.create_from_template(
            template_id=template["id"],
            user_id=user_id,
            start_time=datetime.now().isoformat(),
            ticket_id="ticket-123",  # Would be actual ticket ID
        )
        logger.info(f"Time entry created from template: {time_entry_from_template['id']}")

        return template

    except SuperOpsError as e:
        logger.error(f"Template operation failed: {e}")
        return None


async def demonstrate_bulk_operations(client: SuperOpsClient, time_entry_ids: List[str]) -> None:
    """Demonstrate bulk time entry operations."""
    logger.info("=== Bulk Operations Demo ===")

    try:
        # Bulk update status
        logger.info("Performing bulk status update...")
        updated_entries = await client.time_entries.bulk_update_billable_status(
            time_entry_ids, is_billable=True
        )
        logger.info(f"Bulk updated {len(updated_entries)} entries")

        # Bulk update billable status
        logger.info("Performing bulk billable status update...")
        billable_entries = await client.time_entries.bulk_update_billable_status(
            time_entry_ids, is_billable=False
        )
        logger.info(f"Updated billable status for {len(billable_entries)} entries")

        # Export would be handled through get_time_summary for this demo
        logger.info("Getting comprehensive time data...")
        export_data = await client.time_entries.get_time_summary(
            start_date=(datetime.now() - timedelta(days=30)).isoformat(),
            end_date=datetime.now().isoformat(),
            group_by="day",
        )
        logger.info(f"Retrieved time summary with {len(export_data.get('groups', []))} day groups")

    except SuperOpsError as e:
        logger.error(f"Bulk operation failed: {e}")


async def main() -> None:
    """Main workflow demonstration."""
    logger.info("Starting Time Entries Management Workflow Demo")

    try:
        # Create client from environment variables
        config = SuperOpsConfig.from_env()

        async with SuperOpsClient(config) as client:
            # Test connection
            logger.info("Testing connection to SuperOps API...")
            connection_info = await client.test_connection()
            if not connection_info.get("connected"):
                logger.error("Failed to connect to SuperOps API")
                return

            logger.info("Successfully connected to SuperOps API")

            # Mock IDs for demonstration (in real usage, these would be actual IDs)
            user_id = "demo-user-123"
            ticket_id = "ticket-456"
            time_entry_ids = []

            # Run demonstrations
            logger.info("\n" + "=" * 50)
            logger.info("STARTING TIME ENTRIES WORKFLOW DEMONSTRATION")
            logger.info("=" * 50 + "\n")

            # 1. Timer functionality
            timer_entry = await demonstrate_timer_functionality(client, user_id, ticket_id)
            if timer_entry:
                time_entry_ids.append(timer_entry["id"])

            # 2. CRUD operations
            crud_entry = await demonstrate_time_entry_crud(client, user_id, ticket_id)
            if crud_entry:
                time_entry_ids.append(crud_entry["id"])

            # 3. Template management
            template = await demonstrate_template_management(client, user_id)

            # 4. Bulk operations (if we have entries)
            if time_entry_ids:
                await demonstrate_bulk_operations(client, time_entry_ids)

            # 5. Approval workflow
            if time_entry_ids:
                await demonstrate_approval_workflow(client, time_entry_ids)

            # 6. Reporting and analytics
            await demonstrate_reporting_analytics(client, user_id)

            logger.info("\n" + "=" * 50)
            logger.info("TIME ENTRIES WORKFLOW DEMONSTRATION COMPLETED")
            logger.info("=" * 50)

    except SuperOpsError as e:
        logger.error(f"SuperOps API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    # Run the workflow demonstration
    asyncio.run(main())
