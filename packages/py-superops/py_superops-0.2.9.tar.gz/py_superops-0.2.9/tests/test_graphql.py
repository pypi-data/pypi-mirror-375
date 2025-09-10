# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Tests for GraphQL utilities.

This module tests the GraphQL query builders, fragments, types,
and common queries to ensure they work correctly.
"""

from datetime import datetime
from typing import Any, Dict

import pytest

from py_superops.graphql import (  # Types; Fragments; Builders; Queries
    BASE_FIELDS,
    CLIENT_CORE_FIELDS,
    TICKET_FULL_FIELDS,
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
    build_fragments_string,
    build_ticket_list_query,
    create_asset_query_builder,
    create_client_mutation_builder,
    create_client_query_builder,
    create_ticket_mutation_builder,
    create_ticket_query_builder,
    get_asset_fields,
    get_client_fields,
    get_ticket_fields,
    resolve_dependencies,
    serialize_filter_value,
    serialize_input,
)


class TestTypes:
    """Test GraphQL types and utilities."""

    def test_pagination_args_validation(self):
        """Test pagination arguments validation."""
        # Valid pagination
        pagination = PaginationArgs(page=1, pageSize=50)
        assert pagination.page == 1
        assert pagination.pageSize == 50

        # Invalid page
        with pytest.raises(ValueError, match="Page must be >= 1"):
            PaginationArgs(page=0, pageSize=50)

        # Invalid page size
        with pytest.raises(ValueError, match="Page size must be between 1 and 1000"):
            PaginationArgs(page=1, pageSize=0)

        with pytest.raises(ValueError, match="Page size must be between 1 and 1000"):
            PaginationArgs(page=1, pageSize=1001)

    def test_sort_args_validation(self):
        """Test sort arguments validation."""
        # Valid sort
        sort = SortArgs(field="name", direction="ASC")
        assert sort.field == "name"
        assert sort.direction == "ASC"

        # Invalid direction
        with pytest.raises(ValueError, match="Direction must be ASC or DESC"):
            SortArgs(field="name", direction="INVALID")

    def test_serialize_filter_value(self):
        """Test filter value serialization."""
        # DateTime
        dt = datetime(2023, 1, 1, 12, 0, 0)
        assert serialize_filter_value(dt) == dt.isoformat()

        # Enum
        assert serialize_filter_value(ClientStatus.ACTIVE) == "ACTIVE"

        # List
        assert serialize_filter_value([1, 2, 3]) == [1, 2, 3]

        # Dict
        assert serialize_filter_value({"key": "value"}) == {"key": "value"}

        # Regular value
        assert serialize_filter_value("test") == "test"

    def test_serialize_input(self):
        """Test input serialization."""
        input_data = ClientInput(
            name="Test Client", email="test@example.com", status=ClientStatus.ACTIVE
        )

        serialized = serialize_input(input_data)

        assert serialized["name"] == "Test Client"
        assert serialized["email"] == "test@example.com"
        assert serialized["status"] == "ACTIVE"
        assert "phone" not in serialized  # None values should be omitted


class TestFragments:
    """Test GraphQL fragments."""

    def test_fragment_string_generation(self):
        """Test fragment string generation."""
        fragment_str = str(CLIENT_CORE_FIELDS)

        assert "fragment ClientCoreFields on Client" in fragment_str
        assert "...BaseFields" in fragment_str
        assert "name" in fragment_str
        assert "email" in fragment_str
        assert "status" in fragment_str

    def test_dependency_resolution(self):
        """Test fragment dependency resolution."""
        # CLIENT_CORE_FIELDS depends on BASE_FIELDS
        resolved = resolve_dependencies({"ClientCoreFields"})

        assert "ClientCoreFields" in resolved
        assert "BaseFields" in resolved
        assert len(resolved) == 2

    def test_build_fragments_string(self):
        """Test building complete fragment string."""
        fragment_names = {"ClientCoreFields"}
        fragments_str = build_fragments_string(fragment_names)

        # Should include both BaseFields and ClientCoreFields
        assert "fragment BaseFields" in fragments_str
        assert "fragment ClientCoreFields" in fragments_str

    def test_get_field_helpers(self):
        """Test field helper functions."""
        # Client fields
        client_fields = get_client_fields("core")
        assert "ClientCoreFields" in client_fields

        client_fields_full = get_client_fields("full")
        assert "ClientFullFields" in client_fields_full

        # Ticket fields
        ticket_fields = get_ticket_fields("core")
        assert "TicketCoreFields" in ticket_fields

        ticket_fields_with_comments = get_ticket_fields("core", include_comments=True)
        assert "TicketCoreFields" in ticket_fields_with_comments
        assert "TicketCommentFields" in ticket_fields_with_comments

        # Asset fields
        asset_fields = get_asset_fields("summary")
        assert "AssetSummaryFields" in asset_fields


class TestBuilders:
    """Test GraphQL query and mutation builders."""

    def test_client_query_builder_list(self):
        """Test client query builder for list queries."""
        builder = create_client_query_builder("core")

        # Create filter and pagination
        client_filter = ClientFilter(status=ClientStatus.ACTIVE)
        pagination = PaginationArgs(page=1, pageSize=25)

        # Build query
        query = builder.build_list(filter_obj=client_filter, pagination=pagination)

        # Verify query structure
        assert "query" in query
        assert "clients(" in query
        assert "filter: $filter" in query
        assert "page: $page" in query
        assert "pageSize: $pageSize" in query
        assert "...ClientCoreFields" in query
        assert "fragment ClientCoreFields" in query
        assert "fragment BaseFields" in query

        # Verify variables
        variables = builder.get_variables()
        assert variables["filter"]["status"] == "ACTIVE"
        assert variables["page"] == 1
        assert variables["pageSize"] == 25

    def test_client_query_builder_get(self):
        """Test client query builder for single item queries."""
        builder = create_client_query_builder("full")
        client_id = "client-123"

        query = builder.build_get(client_id)

        assert "query" in query
        assert "client(" in query
        assert "id: $id" in query
        assert "...ClientFullFields" in query

        variables = builder.get_variables()
        assert variables["id"] == client_id

    def test_ticket_query_builder_with_comments(self):
        """Test ticket query builder with comments."""
        builder = create_ticket_query_builder("full", include_comments=True)

        ticket_filter = TicketFilter(status=TicketStatus.OPEN, priority=TicketPriority.HIGH)
        pagination = PaginationArgs(page=1, pageSize=10)

        query = builder.build_list(filter_obj=ticket_filter, pagination=pagination)

        assert "...TicketFullFields" in query
        assert "comments {" in query
        assert "...TicketCommentFields" in query
        assert "fragment TicketCommentFields" in query

        variables = builder.get_variables()
        assert variables["filter"]["status"] == "OPEN"
        assert variables["filter"]["priority"] == "HIGH"

    def test_asset_query_builder(self):
        """Test asset query builder."""
        builder = create_asset_query_builder("summary")

        asset_filter = AssetFilter(
            client_id="client-123", status=AssetStatus.ACTIVE, asset_type="Server"
        )

        query = builder.build_list(filter_obj=asset_filter)

        assert "assets(" in query
        assert "...AssetSummaryFields" in query

        variables = builder.get_variables()
        assert variables["filter"]["clientId"] == "client-123"
        assert variables["filter"]["status"] == "ACTIVE"
        assert variables["filter"]["assetType"] == "Server"

    def test_client_mutation_builder_create(self):
        """Test client mutation builder for create operations."""
        builder = create_client_mutation_builder("core")

        client_input = ClientInput(
            name="New Client", email="new@example.com", status=ClientStatus.ACTIVE
        )

        mutation = builder.create_client(client_input)

        assert "mutation" in mutation
        assert "createClient(" in mutation
        assert "input: $input" in mutation
        assert "...ClientCoreFields" in mutation

        variables = builder.get_variables()
        assert variables["input"]["name"] == "New Client"
        assert variables["input"]["email"] == "new@example.com"
        assert variables["input"]["status"] == "ACTIVE"

    def test_client_mutation_builder_update(self):
        """Test client mutation builder for update operations."""
        builder = create_client_mutation_builder("full")

        client_id = "client-123"
        client_input = ClientInput(name="Updated Client", email="updated@example.com")

        mutation = builder.update_client(client_id, client_input)

        assert "updateClient(" in mutation
        assert "id: $id" in mutation
        assert "input: $input" in mutation

        variables = builder.get_variables()
        assert variables["id"] == client_id
        assert variables["input"]["name"] == "Updated Client"

    def test_client_mutation_builder_delete(self):
        """Test client mutation builder for delete operations."""
        builder = create_client_mutation_builder()
        client_id = "client-123"

        mutation = builder.delete_client(client_id)

        assert "deleteClient(" in mutation
        assert "id: $id" in mutation
        assert "success" in mutation
        assert "message" in mutation

        variables = builder.get_variables()
        assert variables["id"] == client_id


class TestCommonQueries:
    """Test pre-built common queries."""

    def test_list_all_clients(self):
        """Test list all clients query."""
        query, variables = CommonQueries.list_all_clients(
            page=2, page_size=30, sort_field="email", sort_direction="DESC"
        )

        assert "clients(" in query
        assert "page: $page" in query
        assert "pageSize: $pageSize" in query
        assert "sortField: $sortField" in query
        assert "sortDirection: $sortDirection" in query

        assert variables["page"] == 2
        assert variables["pageSize"] == 30
        assert variables["sortField"] == "email"
        assert variables["sortDirection"] == "DESC"

    def test_list_active_clients(self):
        """Test list active clients query."""
        query, variables = CommonQueries.list_active_clients(page=1, page_size=25)

        assert "filter: $filter" in query
        assert variables["filter"]["status"] == "ACTIVE"
        assert variables["page"] == 1
        assert variables["pageSize"] == 25

    def test_search_clients_by_name(self):
        """Test search clients by name query."""
        query, variables = CommonQueries.search_clients_by_name("Test Corp")

        assert "filter: $filter" in query
        assert variables["filter"]["name"] == "Test Corp"

    def test_get_client_by_id(self):
        """Test get client by ID query."""
        client_id = "client-123"
        query, variables = CommonQueries.get_client_by_id(client_id, "full")

        assert "client(" in query
        assert "id: $id" in query
        assert "...ClientFullFields" in query
        assert variables["id"] == client_id

    def test_list_open_tickets(self):
        """Test list open tickets query."""
        query, variables = CommonQueries.list_open_tickets(
            page=1, page_size=20, include_comments=True
        )

        assert "tickets(" in query
        assert "filter: $filter" in query
        assert "comments {" in query
        assert variables["filter"]["status"] == "OPEN"

    def test_list_tickets_by_client(self):
        """Test list tickets by client query."""
        client_id = "client-123"
        query, variables = CommonQueries.list_tickets_by_client(
            client_id, status=TicketStatus.IN_PROGRESS
        )

        assert variables["filter"]["clientId"] == client_id
        assert variables["filter"]["status"] == "IN_PROGRESS"

    def test_list_urgent_tickets(self):
        """Test list urgent tickets query."""
        query, variables = CommonQueries.list_urgent_tickets()

        assert variables["filter"]["priority"] == "URGENT"

    def test_list_assets_by_client(self):
        """Test list assets by client query."""
        client_id = "client-123"
        query, variables = CommonQueries.list_assets_by_client(client_id, status=AssetStatus.ACTIVE)

        assert variables["filter"]["clientId"] == client_id
        assert variables["filter"]["status"] == "ACTIVE"

    def test_search_assets_by_type(self):
        """Test search assets by type query."""
        query, variables = CommonQueries.search_assets_by_type("Server")

        assert variables["filter"]["assetType"] == "Server"

    def test_list_kb_collections(self):
        """Test list knowledge base collections query."""
        query, variables = CommonQueries.list_kb_collections(page=1, page_size=20, is_public=True)

        assert "knowledgeBaseCollections(" in query
        assert "isPublic: $isPublic" in query
        assert variables["isPublic"] is True

    def test_list_kb_articles_by_collection(self):
        """Test list knowledge base articles by collection query."""
        collection_id = "collection-123"
        query, variables = CommonQueries.list_kb_articles_by_collection(
            collection_id, is_published=True
        )

        assert "knowledgeBaseArticles(" in query
        assert "collectionId: $collectionId" in query
        assert variables["collectionId"] == collection_id
        assert variables["isPublished"] is True

    def test_search_kb_articles(self):
        """Test search knowledge base articles query."""
        query, variables = CommonQueries.search_kb_articles("troubleshooting")

        assert "searchKnowledgeBaseArticles(" in query
        assert variables["searchTerm"] == "troubleshooting"

    def test_get_client_overview(self):
        """Test get client overview query."""
        client_id = "client-123"
        query, variables = SuperOpsQueries.get_client_overview(client_id)

        assert "client(" in query
        assert "tickets(" in query
        assert "assets(" in query
        assert "sites {" in query
        assert "contacts {" in query
        assert variables["clientId"] == client_id

    def test_get_dashboard_summary(self):
        """Test get dashboard summary query."""
        query, variables = SuperOpsQueries.get_dashboard_summary()

        assert "ticketsSummary:" in query
        assert "openTickets:" in query
        assert "urgentTickets:" in query
        assert "clientsSummary:" in query
        assert "activeClients:" in query
        assert "assetsSummary:" in query
        assert variables == {}

    def test_get_recent_activity(self):
        """Test get recent activity query."""
        query, variables = SuperOpsQueries.get_recent_activity(limit=10)

        assert "recentTickets:" in query
        assert "recentAssets:" in query
        assert 'sortField: "updatedAt"' in query
        assert "sortDirection: DESC" in query
        assert variables["limit"] == 10


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_build_client_list_query_with_status(self):
        """Test client list query builder with status filter."""
        query, variables = build_client_list_query(status=ClientStatus.ACTIVE, page=2, page_size=25)

        assert "filter: $filter" in query
        assert variables["filter"]["status"] == "ACTIVE"
        assert variables["page"] == 2
        assert variables["pageSize"] == 25

    def test_build_client_list_query_with_name_search(self):
        """Test client list query builder with name search."""
        query, variables = build_client_list_query(name_search="Acme Corp")

        assert variables["filter"]["name"] == "Acme Corp"

    def test_build_ticket_list_query_with_filters(self):
        """Test ticket list query builder with multiple filters."""
        query, variables = build_ticket_list_query(
            client_id="client-123",
            status=TicketStatus.OPEN,
            priority=TicketPriority.HIGH,
            assigned_to="user-456",
            include_comments=True,
        )

        assert "comments {" in query
        assert variables["filter"]["clientId"] == "client-123"
        assert variables["filter"]["status"] == "OPEN"
        assert variables["filter"]["priority"] == "HIGH"
        assert variables["filter"]["assignedTo"] == "user-456"

    def test_build_asset_list_query_with_filters(self):
        """Test asset list query builder with filters."""
        query, variables = build_asset_list_query(
            client_id="client-123", asset_type="Server", status=AssetStatus.ACTIVE
        )

        assert variables["filter"]["clientId"] == "client-123"
        assert variables["filter"]["assetType"] == "Server"
        assert variables["filter"]["status"] == "ACTIVE"

    def test_build_asset_list_query_no_filters(self):
        """Test asset list query builder with no filters."""
        query, variables = build_asset_list_query()

        # Should not have filter in query when no filters provided
        assert "filter" not in variables


class TestIntegration:
    """Integration tests for GraphQL utilities."""

    def test_complete_query_workflow(self):
        """Test a complete query building workflow."""
        # Create a complex filter
        ticket_filter = TicketFilter(
            client_id="client-123",
            status=TicketStatus.OPEN,
            priority=TicketPriority.HIGH,
            created_after=datetime(2023, 1, 1),
        )

        # Create pagination and sorting
        pagination = PaginationArgs(page=2, pageSize=15)
        sort_args = SortArgs(field="createdAt", direction="DESC")

        # Build query
        builder = create_ticket_query_builder("full", include_comments=True)
        query = builder.build_list(filter_obj=ticket_filter, pagination=pagination, sort=sort_args)
        variables = builder.get_variables()

        # Verify complete query structure
        assert "query" in query
        assert "tickets(" in query
        assert "filter: $filter" in query
        assert "page: $page" in query
        assert "pageSize: $pageSize" in query
        assert "sortField: $sortField" in query
        assert "sortDirection: $sortDirection" in query
        assert "...TicketFullFields" in query
        assert "comments {" in query
        assert "...TicketCommentFields" in query
        assert "fragment TicketFullFields" in query
        assert "fragment TicketCommentFields" in query
        assert "fragment BaseFields" in query

        # Verify variables are correctly serialized
        assert variables["filter"]["clientId"] == "client-123"
        assert variables["filter"]["status"] == "OPEN"
        assert variables["filter"]["priority"] == "HIGH"
        assert isinstance(variables["filter"]["createdAfter"], str)
        assert variables["page"] == 2
        assert variables["pageSize"] == 15
        assert variables["sortField"] == "createdAt"
        assert variables["sortDirection"] == "DESC"

    def test_mutation_workflow(self):
        """Test a complete mutation workflow."""
        # Create input data
        ticket_input = TicketInput(
            client_id="client-123",
            title="Test Ticket",
            description="Test description",
            priority=TicketPriority.NORMAL,
            status=TicketStatus.OPEN,
            tags=["test", "api"],
        )

        # Build mutation
        builder = create_ticket_mutation_builder("full")
        mutation = builder.create_ticket(ticket_input)
        variables = builder.get_variables()

        # Verify mutation structure
        assert "mutation" in mutation
        assert "createTicket(" in mutation
        assert "input: $input" in mutation
        assert "...TicketFullFields" in mutation
        assert "fragment TicketFullFields" in mutation

        # Verify variables
        input_vars = variables["input"]
        assert input_vars["clientId"] == "client-123"
        assert input_vars["title"] == "Test Ticket"
        assert input_vars["description"] == "Test description"
        assert input_vars["priority"] == "NORMAL"
        assert input_vars["status"] == "OPEN"
        assert input_vars["tags"] == ["test", "api"]


if __name__ == "__main__":
    pytest.main([__file__])
