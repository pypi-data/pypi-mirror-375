#!/usr/bin/env python3
"""Complete workflow example showing how to use the py-superops API client."""
import asyncio
import os

from py_superops import SuperOpsClient, SuperOpsConfig
from py_superops.graphql import (
    ClientStatus,
    TaskPriority,
    TaskRecurrenceType,
    TaskStatus,
    TicketPriority,
    TicketStatus,
)


async def msp_workflow_example() -> None:
    """Demonstrate a complete MSP workflow using the SuperOps API client."""
    # Configuration - can be from environment variables or direct setup
    config = SuperOpsConfig(
        api_key=os.getenv("SUPEROPS_API_KEY", "your-api-key-here"),
        customer_subdomain=os.getenv("SUPEROPS_SUBDOMAIN", "your-subdomain"),
        # Automatically detects US/EU datacenter from subdomain
        timeout=30.0,
        rate_limit_per_minute=600,  # Conservative rate limiting
    )

    async with SuperOpsClient(config) as client:
        print("🚀 Starting MSP Workflow Example")
        print(f"Connected to SuperOps at: {config.base_url}")

        # 1. CLIENT MANAGEMENT
        print("\n📋 1. Client Management")

        # List active clients
        active_clients = await client.clients.list(
            filter_obj={"status": ClientStatus.ACTIVE}, page=1, page_size=10
        )
        print(f"Found {len(active_clients.get('items', []))} active clients")

        # Search for specific client
        if active_clients.get("items"):
            client_name = active_clients["items"][0].get("name", "Unknown")
            search_results = await client.clients.search(query=client_name[:3])
            print(
                f"Search results for '{client_name[:3]}': {len(search_results.get('items', []))} found"
            )

        # 2. TICKET MANAGEMENT
        print("\n🎫 2. Ticket Management")

        # Find overdue tickets
        overdue_tickets = await client.tickets.get_overdue_tickets()
        print(f"Found {len(overdue_tickets.get('items', []))} overdue tickets")

        # Find high priority tickets
        urgent_tickets = await client.tickets.list(
            filter_obj={"priority": TicketPriority.HIGH, "status": TicketStatus.OPEN}
        )
        print(f"Found {len(urgent_tickets.get('items', []))} urgent open tickets")

        # Escalate overdue tickets (demo)
        if overdue_tickets.get("items"):
            ticket = overdue_tickets["items"][0]
            print(f"Escalating ticket #{ticket.get('number', 'Unknown')}")

            # Change priority and add comment
            await client.tickets.change_priority(
                ticket_id=ticket["id"],
                priority=TicketPriority.HIGH,
                add_comment=True,
                comment="Auto-escalated due to overdue status",
            )
            print("✅ Ticket escalated successfully")

        # 3. ASSET MANAGEMENT
        print("\n💻 3. Asset Management")

        # Find assets with expiring warranties
        expiring_assets = await client.assets.get_warranty_expiring_soon(days=30)
        print(
            f"Found {len(expiring_assets.get('items', []))} assets with warranties expiring in 30 days"
        )

        # List assets by type
        server_assets = await client.assets.list(filter_obj={"asset_type": "Server"})
        print(f"Found {len(server_assets.get('items', []))} server assets")

        # 4. SITE MANAGEMENT
        print("\n🏢 4. Site Management")

        # List all sites
        all_sites = await client.sites.list()
        print(f"Total sites managed: {len(all_sites.get('items', []))}")

        # Get site statistics
        if all_sites.get("items"):
            site = all_sites["items"][0]
            site_stats = await client.sites.get_site_statistics(site["id"])
            print(
                f"Site '{site.get('name', 'Unknown')}' has {site_stats.get('asset_count', 0)} assets"
            )

        # 5. KNOWLEDGE BASE OPERATIONS
        print("\n📚 5. Knowledge Base Operations")

        # List knowledge base collections
        kb_collections = await client.knowledge_base.list_collections()
        print(f"Found {len(kb_collections.get('items', []))} knowledge base collections")

        # Search articles
        search_results = await client.knowledge_base.search_articles(
            query="password reset", limit=5
        )
        print(f"Found {len(search_results.get('items', []))} articles for 'password reset'")

        # 6. CROSS-RESOURCE OPERATIONS
        print("\n🔄 6. Cross-Resource Operations")

        if active_clients.get("items"):
            client_id = active_clients["items"][0]["id"]

            # Get all tickets for a client
            client_tickets = await client.tickets.list(filter_obj={"client_id": client_id})

            # Get all assets for a client
            client_assets = await client.assets.list(filter_obj={"client_id": client_id})

            # Get all sites for a client
            client_sites = await client.sites.list(filter_obj={"client_id": client_id})

            client_name = active_clients["items"][0].get("name", "Unknown")
            print(f"Client '{client_name}' summary:")
            print(f"  - Tickets: {len(client_tickets.get('items', []))}")
            print(f"  - Assets: {len(client_assets.get('items', []))}")
            print(f"  - Sites: {len(client_sites.get('items', []))}")

        # 7. BULK OPERATIONS
        print("\n📊 7. Bulk Operations")

        # Example: Update multiple tickets at once
        open_tickets = await client.tickets.list(
            filter_obj={"status": TicketStatus.OPEN}, page_size=5
        )

        if open_tickets.get("items"):
            ticket_ids = [ticket["id"] for ticket in open_tickets["items"]]
            print(f"Found {len(ticket_ids)} open tickets for bulk operations")

            # In production, you might want to:
            # - Assign tickets to specific technicians
            # - Update priorities based on SLA
            # - Add bulk comments for policy updates
            print("✅ Bulk operations ready (demo mode)")

        # 6. TASK MANAGEMENT
        print("\n✅ 6. Task Management")

        # Create a project task
        project_task = await client.tasks.create(
            title="Client Onboarding Project",
            description="Complete onboarding process for new enterprise client",
            priority=TaskPriority.HIGH,
            project_id="onboarding-2024",
            assigned_to="project-manager",
            estimated_hours=40.0,
            tags=["onboarding", "enterprise", "high-priority"],
        )
        print(f"Created project task: {project_task.title}")

        # Create subtasks for structured workflow
        subtasks = []
        subtask_data = [
            {
                "title": "Setup client account and access",
                "description": "Create client account with proper permissions and access controls",
                "estimated_hours": 4.0,
                "assigned_to": "admin-team",
            },
            {
                "title": "Configure monitoring and alerts",
                "description": "Setup automated monitoring for all client systems",
                "estimated_hours": 8.0,
                "assigned_to": "monitoring-team",
            },
            {
                "title": "Deploy security baseline",
                "description": "Implement security policies and baseline configurations",
                "estimated_hours": 12.0,
                "assigned_to": "security-team",
            },
        ]

        for subtask_info in subtask_data:
            subtask = await client.tasks.create_subtask(
                parent_task_id=project_task.id, **subtask_info
            )
            subtasks.append(subtask)

        print(f"Created {len(subtasks)} subtasks for structured workflow")

        # Demonstrate task status management
        first_subtask = subtasks[0]
        await client.tasks.change_status(first_subtask.id, TaskStatus.IN_PROGRESS)

        # Log time entry
        await client.tasks.log_time_entry(
            task_id=first_subtask.id,
            hours=2.5,
            description="Initial account setup and permissions configuration",
            is_billable=True,
        )
        print(f"Started work on: {first_subtask.title} and logged 2.5 hours")

        # Create a recurring maintenance task
        recurring_task = await client.tasks.create_recurring_task(
            title="Weekly Client Health Check",
            description="Perform weekly health checks on all client systems",
            recurrence_type=TaskRecurrenceType.WEEKLY,
            recurrence_interval=1,
            assigned_to="monitoring-team",
            priority=TaskPriority.NORMAL,
            estimated_hours=4.0,
            tags=["maintenance", "health-check", "recurring"],
        )
        print(f"Setup recurring task: {recurring_task.title}")

        # Find and manage overdue tasks
        overdue_tasks = await client.tasks.get_overdue_tasks()
        if overdue_tasks.get("items"):
            print(f"Found {len(overdue_tasks['items'])} overdue tasks - escalating priority")
            for task in overdue_tasks["items"][:3]:  # Limit for demo
                await client.tasks.change_priority(task["id"], TaskPriority.URGENT)

        # Search for specific tasks
        security_tasks = await client.tasks.search("security")
        print(f"Found {len(security_tasks.get('items', []))} security-related tasks")

        # Get task statistics
        try:
            stats = await client.tasks.get_task_statistics()
            print(f"Task Overview: {stats['totalTasks']} total, {stats['overdueCount']} overdue")
        except Exception:
            print("Task statistics not available in demo mode")

        print("✅ Task Management Workflow Completed")

        print("\n✨ MSP Workflow Example Complete!")
        print("\nThis example demonstrated:")
        print("  ✅ Client management and search")
        print("  ✅ Ticket prioritization and escalation")
        print("  ✅ Asset warranty tracking")
        print("  ✅ Site management and statistics")
        print("  ✅ Knowledge base search and organization")
        print("  ✅ Task management with hierarchies and time tracking")
        print("  ✅ Recurring task automation")
        print("  ✅ Cross-resource data correlation")
        print("  ✅ Bulk operation capabilities")


def main() -> None:
    """Run the MSP workflow example."""
    try:
        asyncio.run(msp_workflow_example())
    except KeyboardInterrupt:
        print("\n⚠️  Workflow interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during workflow: {e}")
        print("Please check your configuration and API connectivity")


if __name__ == "__main__":
    main()
