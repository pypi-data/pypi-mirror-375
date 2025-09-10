#!/usr/bin/env python3
"""GraphQL utilities usage examples for the py-superops client library.

This example demonstrates how to use the GraphQL utilities for type-safe
query building and common operations.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the src directory to Python path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from py_superops import SuperOpsClient, SuperOpsConfig, create_client

# GraphQL utilities
from py_superops.graphql import (  # Pre-built queries; Type-safe builders; Types and filters; Enums; Input types for mutations; Convenience functions
    AssetFilter,
    AssetInput,
    AssetStatus,
    ClientFilter,
    ClientInput,
    ClientStatus,
    CommonQueries,
    PaginationArgs,
    SortArgs,
    SuperOpsQueries,
    TicketFilter,
    TicketInput,
    TicketPriority,
    TicketStatus,
    build_asset_list_query,
    build_client_list_query,
    build_ticket_list_query,
    create_asset_query_builder,
    create_client_mutation_builder,
    create_client_query_builder,
    create_ticket_mutation_builder,
    create_ticket_query_builder,
)


async def demo_pre_built_queries():
    """Demonstrate using pre-built queries."""
    print("=== Pre-built Query Examples ===")

    # Example 1: List all active clients
    query, variables = CommonQueries.list_active_clients(page=1, page_size=10)
    print(f"Active clients query:\n{query}\n")
    print(f"Variables: {variables}\n")

    # Example 2: Search clients by name
    query, variables = CommonQueries.search_clients_by_name("Acme", page=1, page_size=5)
    print(f"Search clients query (first 100 chars):\n{query[:100]}...\n")
    print(f"Variables: {variables}\n")

    # Example 3: List open tickets with comments
    query, variables = CommonQueries.list_open_tickets(page=1, page_size=20, include_comments=True)
    print(f"Open tickets with comments (first 150 chars):\n{query[:150]}...\n")
    print(f"Variables: {variables}\n")

    # Example 4: Get client overview
    client_id = "client-123"
    query, variables = SuperOpsQueries.get_client_overview(client_id)
    print(f"Client overview query (first 200 chars):\n{query[:200]}...\n")
    print(f"Variables: {variables}\n")


async def demo_query_builders():
    """Demonstrate using type-safe query builders."""
    print("=== Query Builder Examples ===")

    # Example 1: Custom client query with filtering and pagination
    builder = create_client_query_builder("full")

    client_filter = ClientFilter(status=ClientStatus.ACTIVE, name="Tech")  # Partial name match

    pagination = PaginationArgs(page=2, pageSize=25)
    sort_args = SortArgs(field="name", direction="ASC")

    query = builder.build_list(filter_obj=client_filter, pagination=pagination, sort=sort_args)
    variables = builder.get_variables()

    print(f"Custom client query (first 200 chars):\n{query[:200]}...\n")
    print(f"Variables: {variables}\n")

    # Example 2: Ticket query with complex filtering
    builder = create_ticket_query_builder("full", include_comments=True)

    # Create a filter for high-priority tickets from last week
    last_week = datetime.now() - timedelta(days=7)
    ticket_filter = TicketFilter(
        status=TicketStatus.OPEN, priority=TicketPriority.HIGH, created_after=last_week
    )

    query = builder.build_list(
        filter_obj=ticket_filter,
        pagination=PaginationArgs(page=1, pageSize=15),
        sort=SortArgs(field="createdAt", direction="DESC"),
    )
    variables = builder.get_variables()

    print(f"Complex ticket query (first 200 chars):\n{query[:200]}...\n")
    print(f"Variables: {variables}\n")

    # Example 3: Asset query by type
    builder = create_asset_query_builder("summary")

    asset_filter = AssetFilter(asset_type="Server", status=AssetStatus.ACTIVE)

    query = builder.build_list(filter_obj=asset_filter)
    variables = builder.get_variables()

    print(f"Asset query (first 150 chars):\n{query[:150]}...\n")
    print(f"Variables: {variables}\n")


async def demo_mutations():
    """Demonstrate using mutation builders."""
    print("=== Mutation Examples ===")

    # Example 1: Create client mutation
    builder = create_client_mutation_builder("full")

    client_input = ClientInput(
        name="New Tech Corp",
        email="contact@newtech.com",
        phone="+1-555-0123",
        status=ClientStatus.ACTIVE,
        notes="New client onboarding",
    )

    mutation = builder.create_client(client_input)
    variables = builder.get_variables()

    print(f"Create client mutation (first 200 chars):\n{mutation[:200]}...\n")
    print(f"Variables: {variables}\n")

    # Example 2: Create ticket mutation
    builder = create_ticket_mutation_builder("full")

    ticket_input = TicketInput(
        client_id="client-123",
        title="Server maintenance required",
        description="Regular maintenance on production server",
        priority=TicketPriority.NORMAL,
        status=TicketStatus.OPEN,
        tags=["maintenance", "server", "production"],
    )

    mutation = builder.create_ticket(ticket_input)
    variables = builder.get_variables()

    print(f"Create ticket mutation (first 200 chars):\n{mutation[:200]}...\n")
    print(f"Variables: {variables}\n")

    # Example 3: Update client mutation
    builder = create_client_mutation_builder("core")
    client_id = "client-123"

    update_input = ClientInput(
        name="Updated Tech Corp",
        email="newemail@updatedtech.com",
        notes="Updated contact information",
    )

    mutation = builder.update_client(client_id, update_input)
    variables = builder.get_variables()

    print(f"Update client mutation (first 200 chars):\n{mutation[:200]}...\n")
    print(f"Variables: {variables}\n")


async def demo_convenience_functions():
    """Demonstrate convenience functions for common patterns."""
    print("=== Convenience Function Examples ===")

    # Example 1: Build client list query with status filter
    query, variables = build_client_list_query(
        status=ClientStatus.ACTIVE, page=1, page_size=20, detail_level="full"
    )

    print(f"Convenience client query (first 150 chars):\n{query[:150]}...\n")
    print(f"Variables: {variables}\n")

    # Example 2: Build ticket list query with multiple filters
    query, variables = build_ticket_list_query(
        client_id="client-123",
        status=TicketStatus.OPEN,
        priority=TicketPriority.HIGH,
        assigned_to="user-456",
        page=1,
        page_size=15,
        include_comments=True,
    )

    print(f"Convenience ticket query (first 150 chars):\n{query[:150]}...\n")
    print(f"Variables: {variables}\n")

    # Example 3: Build asset list query
    query, variables = build_asset_list_query(
        client_id="client-123",
        asset_type="Server",
        status=AssetStatus.ACTIVE,
        detail_level="summary",
    )

    print(f"Convenience asset query (first 150 chars):\n{query[:150]}...\n")
    print(f"Variables: {variables}\n")


async def demo_with_real_client():
    """Demonstrate using GraphQL utilities with a real client (if API key available)."""
    print("=== Real Client Integration Example ===")

    api_key = os.getenv("SUPEROPS_API_KEY")

    if not api_key:
        print("No API key found. Set SUPEROPS_API_KEY to test with real API.\n")
        print("Example usage:")
        print("```python")
        print("# Create client")
        print("client = create_client(api_key='your-api-key')")
        print("")
        print("async with client:")
        print("    # Use pre-built query")
        print("    query, variables = CommonQueries.list_active_clients(page=1, page_size=10)")
        print("    response = await client.execute_query(query, variables)")
        print("    clients = response['data']['clients']['items']")
        print("")
        print("    # Use custom builder")
        print("    builder = create_ticket_query_builder('summary')")
        print("    filter_obj = TicketFilter(status=TicketStatus.OPEN)")
        print("    query = builder.build_list(filter_obj=filter_obj)")
        print("    variables = builder.get_variables()")
        print("    response = await client.execute_query(query, variables)")
        print("```")
        return

    try:
        client = create_client(api_key=api_key)

        async with client:
            # Test connection
            connection_info = await client.test_connection()
            print(f"Connected: {connection_info['connected']}")

            # Example 1: Use pre-built query
            query, variables = CommonQueries.list_active_clients(page=1, page_size=5)
            response = await client.execute_query(query, variables)

            if "data" in response and "clients" in response["data"]:
                clients_data = response["data"]["clients"]
                print(f"Found {len(clients_data['items'])} active clients")

                for client_info in clients_data["items"]:
                    print(f"  - {client_info['name']} ({client_info.get('email', 'No email')})")

            # Example 2: Use custom builder
            builder = create_ticket_query_builder("summary")
            ticket_filter = TicketFilter(status=TicketStatus.OPEN)
            pagination = PaginationArgs(page=1, pageSize=3)

            query = builder.build_list(filter_obj=ticket_filter, pagination=pagination)
            variables = builder.get_variables()

            response = await client.execute_query(query, variables)

            if "data" in response and "tickets" in response["data"]:
                tickets_data = response["data"]["tickets"]
                print(f"Found {len(tickets_data['items'])} open tickets")

                for ticket in tickets_data["items"]:
                    print(f"  - #{ticket['id']}: {ticket['title']} ({ticket['status']})")

    except Exception as e:
        print(f"Error testing with real API: {e}")
        print("This could be due to network issues or API key problems.")


async def demo_schema_introspection():
    """Demonstrate schema introspection capabilities."""
    print("=== Schema Introspection Example ===")

    api_key = os.getenv("SUPEROPS_API_KEY")

    if not api_key:
        print("No API key found. Schema introspection requires API access.")
        print("Set SUPEROPS_API_KEY to test schema introspection.")
        return

    try:
        client = create_client(api_key=api_key)

        async with client:
            schema = await client.get_schema()

            print(f"Schema loaded successfully!")
            print(f"Query type: {schema.get('queryType', {}).get('name', 'Unknown')}")
            print(f"Mutation type: {schema.get('mutationType', {}).get('name', 'Unknown')}")

            # Count types
            types = schema.get("types", [])
            print(f"Total types in schema: {len(types)}")

            # Show some type names
            type_names = [t.get("name", "Unknown") for t in types[:10] if t.get("name")]
            print(f"First 10 types: {', '.join(type_names)}")

    except Exception as e:
        print(f"Error with schema introspection: {e}")


async def main():
    """Run all GraphQL utility demonstrations."""
    print("SuperOps GraphQL Utilities - Usage Examples")
    print("=" * 50)

    # Demo pre-built queries
    await demo_pre_built_queries()

    # Demo query builders
    await demo_query_builders()

    # Demo mutations
    await demo_mutations()

    # Demo convenience functions
    await demo_convenience_functions()

    # Demo with real client (if API key available)
    await demo_with_real_client()

    # Demo schema introspection
    await demo_schema_introspection()

    print("=" * 50)
    print("GraphQL utilities demo complete!")
    print("")
    print("Key Benefits:")
    print("- Type-safe query building with IDE support")
    print("- Pre-built queries for common operations")
    print("- Reusable GraphQL fragments")
    print("- Automatic field selection and pagination")
    print("- Built-in response parsing and validation")
    print("- Seamless integration with SuperOpsClient")


if __name__ == "__main__":
    asyncio.run(main())
