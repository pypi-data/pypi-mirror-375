# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Type-safe GraphQL query and mutation builder classes for SuperOps API.

This module provides builder classes that construct GraphQL operations with type safety,
field selection, filtering, and pagination support.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from .fragments import (
    build_fragments_string,
    get_asset_fields,
    get_client_fields,
    get_comment_fields,
    get_monitoring_agent_fields,
    get_monitoring_alert_fields,
    get_monitoring_check_fields,
    get_monitoring_metric_fields,
    get_project_fields,
    get_task_fields,
    get_ticket_fields,
    get_time_entry_fields,
    get_time_entry_template_fields,
    get_timer_fields,
    get_user_fields,
)
from .types import (
    AssetFilter,
    ClientFilter,
    ClientInput,
    CommentFilter,
    CommentInput,
    MonitoringAgentFilter,
    MonitoringAgentInput,
    MonitoringAlertFilter,
    MonitoringAlertInput,
    MonitoringCheckFilter,
    MonitoringCheckInput,
    MonitoringMetricFilter,
    MonitoringMetricInput,
    PaginationArgs,
    ProjectFilter,
    ProjectInput,
    ProjectMilestoneInput,
    ProjectTaskInput,
    ProjectTimeEntryInput,
    SortArgs,
    TaskFilter,
    TicketFilter,
    TicketInput,
    TimeEntryApprovalInput,
    TimeEntryFilter,
    TimeEntryInput,
    TimeEntryTemplateInput,
    TimerFilter,
    TimerInput,
    UserFilter,
    UserInput,
    serialize_filter_value,
    serialize_input,
)


class QueryBuilder:
    """Base class for building GraphQL queries."""

    def __init__(self):
        """Initialize the query builder."""
        self._operation_name: Optional[str] = None
        self._variables: Dict[str, Any] = {}
        self._variable_definitions: Dict[str, str] = {}
        self._fragments: Set[str] = set()

    def operation_name(self, name: str) -> QueryBuilder:
        """Set the operation name.

        Args:
            name: Operation name

        Returns:
            Self for chaining
        """
        self._operation_name = name
        return self

    def add_variable(self, name: str, type_def: str, value: Any = None) -> QueryBuilder:
        """Add a variable definition.

        Args:
            name: Variable name (without $)
            type_def: GraphQL type definition (e.g., "String!", "[ID!]")
            value: Variable value for query execution

        Returns:
            Self for chaining
        """
        self._variable_definitions[name] = type_def
        if value is not None:
            self._variables[name] = serialize_filter_value(value)
        return self

    def add_fragment(self, fragment_name: str) -> QueryBuilder:
        """Add a fragment to the query.

        Args:
            fragment_name: Name of the fragment

        Returns:
            Self for chaining
        """
        self._fragments.add(fragment_name)
        return self

    def add_fragments(self, fragment_names: Set[str]) -> QueryBuilder:
        """Add multiple fragments to the query.

        Args:
            fragment_names: Set of fragment names

        Returns:
            Self for chaining
        """
        self._fragments.update(fragment_names)
        return self

    def _build_variable_definitions(self) -> str:
        """Build variable definitions string."""
        if not self._variable_definitions:
            return ""

        definitions = []
        for name, type_def in self._variable_definitions.items():
            definitions.append(f"${name}: {type_def}")

        return f"({', '.join(definitions)})"

    def _build_operation_header(self, operation_type: str) -> str:
        """Build operation header with name and variables."""
        header = operation_type

        if self._operation_name:
            header += f" {self._operation_name}"

        var_defs = self._build_variable_definitions()
        if var_defs:
            header += var_defs

        return header

    def get_variables(self) -> Dict[str, Any]:
        """Get variables for query execution."""
        return self._variables.copy()

    def build(self) -> str:
        """Build the complete query string.

        This method must be implemented by subclasses.

        Returns:
            Complete GraphQL query string
        """
        raise NotImplementedError("Subclasses must implement build()")


class SelectionQueryBuilder(QueryBuilder):
    """Builder for queries with field selection."""

    def __init__(self):
        """Initialize the selection query builder."""
        super().__init__()
        self._selections: List[str] = []

    def add_selection(self, selection: str) -> SelectionQueryBuilder:
        """Add a field selection.

        Args:
            selection: Field selection string

        Returns:
            Self for chaining
        """
        self._selections.append(selection.strip())
        return self

    def _build_selections(self) -> str:
        """Build selections string."""
        return "\n".join(f"  {selection}" for selection in self._selections)

    def build_query_body(self, query_field: str, args: str = "") -> str:
        """Build the query body.

        Args:
            query_field: The main query field name
            args: Query arguments string

        Returns:
            Query body string
        """
        selections = self._build_selections()

        if args:
            return f"""{query_field}({args}) {{
{selections}
}}"""
        else:
            return f"""{query_field} {{
{selections}
}}"""

    def build(self, query_field: str, args: str = "") -> str:
        """Build the complete query.

        Args:
            query_field: The main query field name
            args: Query arguments string

        Returns:
            Complete GraphQL query string
        """
        header = self._build_operation_header("query")
        body = self.build_query_body(query_field, args)

        query = f"""{header} {{
{body}
}}"""

        # Add fragments if any
        if self._fragments:
            fragments_str = build_fragments_string(self._fragments)
            query = f"{query}\n\n{fragments_str}"

        return query


class MutationBuilder(QueryBuilder):
    """Builder for GraphQL mutations."""

    def __init__(self):
        """Initialize the mutation builder."""
        super().__init__()
        self._mutation_field: Optional[str] = None
        self._mutation_args: Optional[str] = None
        self._return_fields: List[str] = []

    def mutation_field(self, field: str, args: str = "") -> MutationBuilder:
        """Set the mutation field and arguments.

        Args:
            field: Mutation field name
            args: Mutation arguments string

        Returns:
            Self for chaining
        """
        self._mutation_field = field
        self._mutation_args = args
        return self

    def return_field(self, field: str) -> MutationBuilder:
        """Add a return field.

        Args:
            field: Return field selection

        Returns:
            Self for chaining
        """
        self._return_fields.append(field.strip())
        return self

    def build(self) -> str:
        """Build the complete mutation.

        Returns:
            Complete GraphQL mutation string
        """
        if not self._mutation_field:
            raise ValueError("Mutation field must be set")

        header = self._build_operation_header("mutation")

        # Build mutation body
        args_str = f"({self._mutation_args})" if self._mutation_args else ""
        returns_str = "\n".join(f"  {field}" for field in self._return_fields)

        body = f"""{self._mutation_field}{args_str} {{
{returns_str}
}}"""

        mutation = f"""{header} {{
{body}
}}"""

        # Add fragments if any
        if self._fragments:
            fragments_str = build_fragments_string(self._fragments)
            mutation = f"{mutation}\n\n{fragments_str}"

        return mutation


class ClientQueryBuilder(SelectionQueryBuilder):
    """Builder for client-related queries."""

    def __init__(self, detail_level: str = "core"):
        """Initialize client query builder.

        Args:
            detail_level: Level of detail (summary, core, full)
        """
        super().__init__()
        self.detail_level = detail_level
        self.add_fragments(get_client_fields(detail_level))

    def list_clients(
        self,
        filter_obj: Optional[ClientFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> ClientQueryBuilder:
        """Build a list clients query.

        Args:
            filter_obj: Client filter
            pagination: Pagination arguments
            sort: Sort arguments

        Returns:
            Self for chaining
        """
        # Build arguments
        args = []

        if filter_obj:
            self.add_variable("filter", "ClientFilter", serialize_input(filter_obj))
            args.append("filter: $filter")

        if pagination:
            self.add_variable("page", "Int", pagination.page)
            self.add_variable("pageSize", "Int", pagination.pageSize)
            args.append("page: $page, pageSize: $pageSize")

        if sort:
            self.add_variable("sortField", "String", sort.field)
            self.add_variable("sortDirection", "SortDirection", sort.direction)
            args.append("sortField: $sortField, sortDirection: $sortDirection")

        # Add selections
        fragment_name = get_client_fields(self.detail_level)
        fragment_spread = f"...{list(fragment_name)[0]}"

        return (
            self.add_selection(
                f"""items {{
  {fragment_spread}
}}"""
            )
            .add_selection(
                """pagination {
  ...PaginationInfo
}"""
            )
            .add_fragment("PaginationInfo")
        )

    def get_client(self, client_id: str) -> ClientQueryBuilder:
        """Build a get client by ID query.

        Args:
            client_id: Client ID

        Returns:
            Self for chaining
        """
        self.add_variable("id", "ID!", client_id)

        fragment_name = get_client_fields(self.detail_level)
        fragment_spread = f"...{list(fragment_name)[0]}"

        return self.add_selection(fragment_spread)

    def build_list(
        self,
        filter_obj: Optional[ClientFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> str:
        """Build complete list clients query.

        Args:
            filter_obj: Client filter
            pagination: Pagination arguments
            sort: Sort arguments

        Returns:
            Complete GraphQL query string
        """
        self.list_clients(filter_obj, pagination, sort)
        args = ", ".join(
            [
                arg
                for arg in [
                    "filter: $filter",
                    "page: $page",
                    "pageSize: $pageSize",
                    "sortField: $sortField",
                    "sortDirection: $sortDirection",
                ]
                if any(var in self._variables for var in arg.split("$")[1:] if "$" in arg)
            ]
        )
        return self.build("clients", args)

    def build_get(self, client_id: str) -> str:
        """Build complete get client query.

        Args:
            client_id: Client ID

        Returns:
            Complete GraphQL query string
        """
        self.get_client(client_id)
        return self.build("client", "id: $id")


class TicketQueryBuilder(SelectionQueryBuilder):
    """Builder for ticket-related queries."""

    def __init__(self, detail_level: str = "core", include_comments: bool = False):
        """Initialize ticket query builder.

        Args:
            detail_level: Level of detail (summary, core, full)
            include_comments: Whether to include comment fields
        """
        super().__init__()
        self.detail_level = detail_level
        self.include_comments = include_comments
        self.add_fragments(get_ticket_fields(detail_level, include_comments))

    def list_tickets(
        self,
        filter_obj: Optional[TicketFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> TicketQueryBuilder:
        """Build a list tickets query.

        Args:
            filter_obj: Ticket filter
            pagination: Pagination arguments
            sort: Sort arguments

        Returns:
            Self for chaining
        """
        # Build arguments
        args = []

        if filter_obj:
            self.add_variable("filter", "TicketFilter", serialize_input(filter_obj))
            args.append("filter: $filter")

        if pagination:
            self.add_variable("page", "Int", pagination.page)
            self.add_variable("pageSize", "Int", pagination.pageSize)
            args.append("page: $page, pageSize: $pageSize")

        if sort:
            self.add_variable("sortField", "String", sort.field)
            self.add_variable("sortDirection", "SortDirection", sort.direction)
            args.append("sortField: $sortField, sortDirection: $sortDirection")

        # Add selections
        fragment_names = get_ticket_fields(self.detail_level, self.include_comments)
        main_fragment = [name for name in fragment_names if "Comment" not in name][0]
        fragment_spread = f"...{main_fragment}"

        selection = f"""items {{
  {fragment_spread}"""

        if self.include_comments:
            selection += """
  comments {
    ...TicketCommentFields
  }"""

        selection += "\n}"

        return (
            self.add_selection(selection)
            .add_selection(
                """pagination {
  ...PaginationInfo
}"""
            )
            .add_fragment("PaginationInfo")
        )

    def get_ticket(self, ticket_id: str) -> TicketQueryBuilder:
        """Build a get ticket by ID query.

        Args:
            ticket_id: Ticket ID

        Returns:
            Self for chaining
        """
        self.add_variable("id", "ID!", ticket_id)

        fragment_names = get_ticket_fields(self.detail_level, self.include_comments)
        main_fragment = [name for name in fragment_names if "Comment" not in name][0]
        fragment_spread = f"...{main_fragment}"

        selection = fragment_spread

        if self.include_comments:
            selection += """
comments {
  ...TicketCommentFields
}"""

        return self.add_selection(selection)

    def build_list(
        self,
        filter_obj: Optional[TicketFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> str:
        """Build complete list tickets query.

        Args:
            filter_obj: Ticket filter
            pagination: Pagination arguments
            sort: Sort arguments

        Returns:
            Complete GraphQL query string
        """
        self.list_tickets(filter_obj, pagination, sort)
        args_list = []

        if "filter" in self._variables:
            args_list.append("filter: $filter")
        if "page" in self._variables:
            args_list.append("page: $page, pageSize: $pageSize")
        if "sortField" in self._variables:
            args_list.append("sortField: $sortField, sortDirection: $sortDirection")

        args = ", ".join(args_list)
        return self.build("tickets", args)

    def build_get(self, ticket_id: str) -> str:
        """Build complete get ticket query.

        Args:
            ticket_id: Ticket ID

        Returns:
            Complete GraphQL query string
        """
        self.get_ticket(ticket_id)
        return self.build("ticket", "id: $id")


class TaskQueryBuilder(SelectionQueryBuilder):
    """Builder for task-related queries."""

    def __init__(
        self,
        detail_level: str = "core",
        include_comments: bool = False,
        include_time_entries: bool = False,
        include_template: bool = False,
    ):
        """Initialize task query builder.

        Args:
            detail_level: Level of detail (summary, core, full)
            include_comments: Whether to include comment fields
            include_time_entries: Whether to include time entry fields
            include_template: Whether to include template fields
        """
        super().__init__()
        self.detail_level = detail_level
        self.include_comments = include_comments
        self.include_time_entries = include_time_entries
        self.include_template = include_template
        self.add_fragments(
            get_task_fields(detail_level, include_comments, include_time_entries, include_template)
        )

    def list_tasks(
        self,
        filter_obj: Optional[TaskFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> "TaskQueryBuilder":
        """Build a list tasks query.

        Args:
            filter_obj: Task filter
            pagination: Pagination arguments
            sort: Sort arguments

        Returns:
            Self for chaining
        """
        # Build arguments
        args = []

        if filter_obj:
            self.add_variable("filter", "TaskFilter", serialize_input(filter_obj))
            args.append("filter: $filter")

        if pagination:
            self.add_variable("page", "Int", pagination.page)
            self.add_variable("pageSize", "Int", pagination.pageSize)
            args.append("page: $page, pageSize: $pageSize")

        if sort:
            self.add_variable("sortField", "String", sort.field)
            self.add_variable("sortDirection", "SortDirection", sort.direction)
            args.append("sortField: $sortField, sortDirection: $sortDirection")

        # Add selections
        fragment_name = get_task_fields(
            self.detail_level,
            self.include_comments,
            self.include_time_entries,
            self.include_template,
        )
        fragment_spread = f"...{list(fragment_name)[0]}"

        return (
            self.add_selection(
                f"""items {{
  {fragment_spread}
}}"""
            )
            .add_selection(
                """pagination {
  ...PaginationInfo
}"""
            )
            .add_fragment("PaginationInfo")
        )

    def get_task(self, task_id: str) -> "TaskQueryBuilder":
        """Build a get task by ID query.

        Args:
            task_id: Task ID

        Returns:
            Self for chaining
        """
        self.add_variable("id", "ID!", task_id)

        fragment_name = get_task_fields(
            self.detail_level,
            self.include_comments,
            self.include_time_entries,
            self.include_template,
        )
        fragment_spread = f"...{list(fragment_name)[0]}"

        return self.add_selection(fragment_spread)

    def build_list(
        self,
        filter_obj: Optional[TaskFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> str:
        """Build complete list tasks query.

        Args:
            filter_obj: Task filter
            pagination: Pagination arguments
            sort: Sort arguments

        Returns:
            Complete GraphQL query string
        """
        self.list_tasks(filter_obj, pagination, sort)
        args = ", ".join(
            [
                arg
                for arg in [
                    "filter: $filter",
                    "page: $page",
                    "pageSize: $pageSize",
                    "sortField: $sortField",
                    "sortDirection: $sortDirection",
                ]
                if any(var in self._variables for var in arg.split("$")[1:] if "$" in arg)
            ]
        )
        return self.build("tasks", args)

    def build_get(self, task_id: str) -> str:
        """Build complete get task query.

        Args:
            task_id: Task ID

        Returns:
            Complete GraphQL query string
        """
        self.get_task(task_id)
        return self.build("task", "id: $id")


class CommentQueryBuilder(SelectionQueryBuilder):
    """Builder for comment-related queries."""

    def __init__(self, detail_level: str = "core", include_attachments: bool = False):
        """Initialize comment query builder.

        Args:
            detail_level: Level of detail (summary, core, full)
            include_attachments: Whether to include attachment fields
        """
        super().__init__()
        self.detail_level = detail_level
        self.include_attachments = include_attachments
        self.add_fragments(get_comment_fields(detail_level, include_attachments))

    def list_comments(
        self,
        filter_obj: Optional[CommentFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> "CommentQueryBuilder":
        """Build a list comments query.

        Args:
            filter_obj: Comment filter
            pagination: Pagination arguments
            sort: Sort arguments

        Returns:
            Self for chaining
        """
        # Build arguments
        args = []

        if filter_obj:
            self.add_variable("filter", "CommentFilter", serialize_input(filter_obj))
            args.append("filter: $filter")

        if pagination:
            self.add_variable("page", "Int", pagination.page)
            self.add_variable("pageSize", "Int", pagination.pageSize)
            args.append("page: $page, pageSize: $pageSize")

        if sort:
            self.add_variable("sortBy", "String", sort.field)
            self.add_variable("sortDirection", "SortDirection", sort.direction)
            args.append("sortBy: $sortBy, sortDirection: $sortDirection")

        # Add selections
        fragment_name = f"Comment{self.detail_level.capitalize()}Fields"
        self.add_selection(
            f"""
        items {{
            ...{fragment_name}
        }}
        """
        )
        self.add_selection("pagination { ...PaginationInfo }")
        self.add_fragment("PaginationInfo")

        args_str = ", ".join(args) if args else ""
        return self.build("comments", args_str)

    def get_comment(self, comment_id: str) -> "CommentQueryBuilder":
        """Build a get comment query.

        Args:
            comment_id: Comment ID

        Returns:
            Self for chaining
        """
        self.add_variable("id", "ID!", comment_id)

        fragment_name = f"Comment{self.detail_level.capitalize()}Fields"
        self.add_selection(f"...{fragment_name}")

        return self.build("comment", "id: $id")

    def get_comments_for_entity(
        self,
        entity_type: str,
        entity_id: str,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
        include_replies: bool = True,
    ) -> "CommentQueryBuilder":
        """Build a query to get comments for a specific entity.

        Args:
            entity_type: Type of entity (e.g., 'ticket', 'task', 'project')
            entity_id: ID of the entity
            pagination: Pagination arguments
            sort: Sort arguments
            include_replies: Whether to include reply comments

        Returns:
            Self for chaining
        """
        # Create filter for entity
        filter_obj = CommentFilter(
            entity_type=entity_type,
            entity_id=entity_id,
        )

        if not include_replies:
            filter_obj.parent_comment_id = None

        return self.list_comments(filter_obj, pagination, sort)

    def get_comment_replies(
        self,
        parent_comment_id: str,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> "CommentQueryBuilder":
        """Build a query to get replies to a specific comment.

        Args:
            parent_comment_id: ID of the parent comment
            pagination: Pagination arguments
            sort: Sort arguments

        Returns:
            Self for chaining
        """
        filter_obj = CommentFilter(parent_comment_id=parent_comment_id)
        return self.list_comments(filter_obj, pagination, sort)

    def search_comments(
        self,
        query: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> "CommentQueryBuilder":
        """Build a search comments query.

        Args:
            query: Search query string
            entity_type: Optional entity type filter
            entity_id: Optional entity ID filter
            pagination: Pagination arguments
            sort: Sort arguments

        Returns:
            Self for chaining
        """
        filter_obj = CommentFilter(
            content_contains=query,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        return self.list_comments(filter_obj, pagination, sort)


class AssetQueryBuilder(SelectionQueryBuilder):
    """Builder for asset-related queries."""

    def __init__(self, detail_level: str = "core"):
        """Initialize asset query builder.

        Args:
            detail_level: Level of detail (summary, core, full)
        """
        super().__init__()
        self.detail_level = detail_level
        self.add_fragments(get_asset_fields(detail_level))

    def list_assets(
        self,
        filter_obj: Optional[AssetFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> AssetQueryBuilder:
        """Build a list assets query.

        Args:
            filter_obj: Asset filter
            pagination: Pagination arguments
            sort: Sort arguments

        Returns:
            Self for chaining
        """
        if filter_obj:
            self.add_variable("filter", "AssetFilter", serialize_input(filter_obj))

        if pagination:
            self.add_variable("page", "Int", pagination.page)
            self.add_variable("pageSize", "Int", pagination.pageSize)

        if sort:
            self.add_variable("sortField", "String", sort.field)
            self.add_variable("sortDirection", "SortDirection", sort.direction)

        # Add selections
        fragment_name = get_asset_fields(self.detail_level)
        fragment_spread = f"...{list(fragment_name)[0]}"

        return (
            self.add_selection(
                f"""items {{
  {fragment_spread}
}}"""
            )
            .add_selection(
                """pagination {
  ...PaginationInfo
}"""
            )
            .add_fragment("PaginationInfo")
        )

    def get_asset(self, asset_id: str) -> AssetQueryBuilder:
        """Build a get asset by ID query.

        Args:
            asset_id: Asset ID

        Returns:
            Self for chaining
        """
        self.add_variable("id", "ID!", asset_id)

        fragment_name = get_asset_fields(self.detail_level)
        fragment_spread = f"...{list(fragment_name)[0]}"

        return self.add_selection(fragment_spread)

    def build_list(
        self,
        filter_obj: Optional[AssetFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> str:
        """Build complete list assets query."""
        self.list_assets(filter_obj, pagination, sort)
        args_list = []

        if "filter" in self._variables:
            args_list.append("filter: $filter")
        if "page" in self._variables:
            args_list.append("page: $page, pageSize: $pageSize")
        if "sortField" in self._variables:
            args_list.append("sortField: $sortField, sortDirection: $sortDirection")

        args = ", ".join(args_list)
        return self.build("assets", args)

    def build_get(self, asset_id: str) -> str:
        """Build complete get asset query."""
        self.get_asset(asset_id)
        return self.build("asset", "id: $id")


class UserQueryBuilder(SelectionQueryBuilder):
    """Builder for user-related queries."""

    def __init__(self, detail_level: str = "core"):
        """Initialize user query builder.

        Args:
            detail_level: Level of detail (summary, core, full)
        """
        super().__init__()
        self.detail_level = detail_level
        self.add_fragments(get_user_fields(detail_level))

    def list_users(
        self,
        filter_obj: Optional[UserFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> "UserQueryBuilder":
        """Build a list users query.

        Args:
            filter_obj: User filter
            pagination: Pagination arguments
            sort: Sort arguments

        Returns:
            Self for chaining
        """
        # Build arguments
        args = []

        if filter_obj:
            self.add_variable("filter", "UserFilter", serialize_input(filter_obj))
            args.append("filter: $filter")

        if pagination:
            self.add_variable("page", "Int", pagination.page)
            self.add_variable("pageSize", "Int", pagination.pageSize)
            args.append("page: $page, pageSize: $pageSize")

        if sort:
            self.add_variable("sortField", "String", sort.field)
            self.add_variable("sortDirection", "SortDirection", sort.direction)
            args.append("sortField: $sortField, sortDirection: $sortDirection")

        # Add selections
        fragment_name = list(get_user_fields(self.detail_level))[0]
        fragment_spread = f"...{fragment_name}"

        return (
            self.add_selection(
                f"""items {{
  {fragment_spread}
}}"""
            )
            .add_selection(
                """pagination {
  ...PaginationInfo
}"""
            )
            .add_fragment("PaginationInfo")
        )

    def get_user(self, user_id: str) -> "UserQueryBuilder":
        """Build a get user by ID query.

        Args:
            user_id: User ID

        Returns:
            Self for chaining
        """
        self.add_variable("id", "ID!", user_id)
        fragment_name = list(get_user_fields(self.detail_level))[0]
        fragment_spread = f"...{fragment_name}"
        return self.add_selection(fragment_spread)

    def build_list(
        self,
        filter_obj: Optional[UserFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> str:
        """Build complete list users query.

        Args:
            filter_obj: User filter
            pagination: Pagination arguments
            sort: Sort arguments

        Returns:
            Complete GraphQL query string
        """
        self.list_users(filter_obj, pagination, sort)

        # Build args list for query
        args_list = []
        if filter_obj:
            args_list.append("filter: $filter")
        if pagination:
            args_list.extend(["page: $page", "pageSize: $pageSize"])
        if sort:
            args_list.extend(["sortField: $sortField", "sortDirection: $sortDirection"])

        args = ", ".join(args_list)
        return self.build("users", args)

    def build_get(self, user_id: str) -> str:
        """Build complete get user query.

        Args:
            user_id: User ID

        Returns:
            Complete GraphQL query string
        """
        self.get_user(user_id)
        return self.build("user", "id: $id")


class ProjectQueryBuilder(SelectionQueryBuilder):
    """Builder for project-related queries."""

    def __init__(
        self,
        detail_level: str = "core",
        include_milestones: bool = False,
        include_tasks: bool = False,
        include_time_entries: bool = False,
        task_detail: str = "core",
    ):
        """Initialize project query builder.

        Args:
            detail_level: Level of detail (summary, core, full)
            include_milestones: Whether to include milestone fields
            include_tasks: Whether to include task fields
            include_time_entries: Whether to include time entry fields
            task_detail: Level of detail for tasks (core, full)
        """
        super().__init__()
        self.detail_level = detail_level
        self.include_milestones = include_milestones
        self.include_tasks = include_tasks
        self.include_time_entries = include_time_entries
        self.task_detail = task_detail

        project_fragments = get_project_fields(
            detail_level=detail_level,
            include_milestones=include_milestones,
            include_tasks=include_tasks,
            include_time_entries=include_time_entries,
            task_detail=task_detail,
        )
        self.add_fragments(project_fragments)

    def list_projects(
        self,
        filter_obj: Optional[ProjectFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> ProjectQueryBuilder:
        """Build a list projects query.

        Args:
            filter_obj: Project filter
            pagination: Pagination arguments
            sort: Sort arguments

        Returns:
            Self for chaining
        """
        # Build arguments
        args = []

        if filter_obj:
            self.add_variable("filter", "ProjectFilter", serialize_input(filter_obj))
            args.append("filter: $filter")

        if pagination:
            self.add_variable("page", "Int", pagination.page)
            self.add_variable("pageSize", "Int", pagination.pageSize)
            args.append("page: $page, pageSize: $pageSize")

        if sort:
            self.add_variable("sortField", "String", sort.field)
            self.add_variable("sortDirection", "SortDirection", sort.direction)
            args.append("sortField: $sortField, sortDirection: $sortDirection")

        # Add selections
        project_fragments = get_project_fields(
            detail_level=self.detail_level,
            include_milestones=self.include_milestones,
            include_tasks=self.include_tasks,
            include_time_entries=self.include_time_entries,
            task_detail=self.task_detail,
        )

        # Get main project fragment
        main_fragment = None
        for fragment in project_fragments:
            if (
                "ProjectSummaryFields" in fragment
                or "ProjectCoreFields" in fragment
                or "ProjectFullFields" in fragment
            ):
                main_fragment = fragment
                break

        if not main_fragment:
            main_fragment = "ProjectCoreFields"

        items_selection = f"""items {{
  ...{main_fragment}"""

        # Add nested selections for milestones, tasks, etc.
        if self.include_milestones:
            items_selection += """
  milestones {
    ...ProjectMilestoneFields
  }"""

        if self.include_tasks:
            task_fragment = (
                "ProjectTaskCoreFields" if self.task_detail == "core" else "ProjectTaskFullFields"
            )
            items_selection += f"""
  tasks {{
    ...{task_fragment}
  }}"""

        if self.include_time_entries:
            items_selection += """
  timeEntries {
    ...ProjectTimeEntryFields
  }"""

        items_selection += "\n}"

        return (
            self.add_selection(items_selection)
            .add_selection(
                """pagination {
  ...PaginationInfo
}"""
            )
            .add_fragment("PaginationInfo")
        )

    def get_project(self, project_id: str) -> ProjectQueryBuilder:
        """Build a get project by ID query.

        Args:
            project_id: Project ID

        Returns:
            Self for chaining
        """
        self.add_variable("id", "ID!", project_id)

        project_fragments = get_project_fields(
            detail_level=self.detail_level,
            include_milestones=self.include_milestones,
            include_tasks=self.include_tasks,
            include_time_entries=self.include_time_entries,
            task_detail=self.task_detail,
        )

        # Get main project fragment
        main_fragment = None
        for fragment in project_fragments:
            if (
                "ProjectSummaryFields" in fragment
                or "ProjectCoreFields" in fragment
                or "ProjectFullFields" in fragment
            ):
                main_fragment = fragment
                break

        if not main_fragment:
            main_fragment = "ProjectCoreFields"

        selection = f"...{main_fragment}"

        # Add nested selections
        if self.include_milestones:
            selection += """
milestones {
  ...ProjectMilestoneFields
}"""

        if self.include_tasks:
            task_fragment = (
                "ProjectTaskCoreFields" if self.task_detail == "core" else "ProjectTaskFullFields"
            )
            selection += f"""
tasks {{
  ...{task_fragment}
}}"""

        if self.include_time_entries:
            selection += """
timeEntries {
  ...ProjectTimeEntryFields
}"""

        return self.add_selection(selection)

    def build_list(
        self,
        filter_obj: Optional[ProjectFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> str:
        """Build list projects query string."""
        self.list_projects(filter_obj, pagination, sort)
        args = ", ".join(
            f"{k}: ${k}" for k in self._variable_definitions.keys() if k in self._variables
        )
        return self.build("projects", args)

    def build_get(self, project_id: str) -> str:
        """Build get project query string."""
        self.get_project(project_id)
        return self.build("project", "id: $id")


class ClientMutationBuilder(MutationBuilder):
    """Builder for client mutations."""

    def __init__(self, detail_level: str = "core"):
        """Initialize client mutation builder.

        Args:
            detail_level: Level of detail for returned fields
        """
        super().__init__()
        self.detail_level = detail_level
        self.add_fragments(get_client_fields(detail_level))

        # Add return fields
        fragment_name = list(get_client_fields(detail_level))[0]
        self.return_field(f"...{fragment_name}")

    def create_client(self, input_data: ClientInput) -> str:
        """Build create client mutation.

        Args:
            input_data: Client input data

        Returns:
            Complete GraphQL mutation string
        """
        self.add_variable("input", "ClientInput!", serialize_input(input_data))
        return self.mutation_field("createClient", "input: $input").build()

    def update_client(self, client_id: str, input_data: ClientInput) -> str:
        """Build update client mutation.

        Args:
            client_id: Client ID
            input_data: Client input data

        Returns:
            Complete GraphQL mutation string
        """
        self.add_variable("id", "ID!", client_id)
        self.add_variable("input", "ClientInput!", serialize_input(input_data))
        return self.mutation_field("updateClient", "id: $id, input: $input").build()

    def delete_client(self, client_id: str) -> str:
        """Build delete client mutation.

        Args:
            client_id: Client ID

        Returns:
            Complete GraphQL mutation string
        """
        self.add_variable("id", "ID!", client_id)
        self._return_fields = ["success", "message"]  # Override return fields
        return self.mutation_field("deleteClient", "id: $id").build()


class TicketMutationBuilder(MutationBuilder):
    """Builder for ticket mutations."""

    def __init__(self, detail_level: str = "core"):
        """Initialize ticket mutation builder.

        Args:
            detail_level: Level of detail for returned fields
        """
        super().__init__()
        self.detail_level = detail_level
        fragment_names = get_ticket_fields(detail_level)
        self.add_fragments(fragment_names)

        # Add return fields
        main_fragment = [name for name in fragment_names if "Comment" not in name][0]
        self.return_field(f"...{main_fragment}")

    def create_ticket(self, input_data: TicketInput) -> str:
        """Build create ticket mutation."""
        self.add_variable("input", "TicketInput!", serialize_input(input_data))
        return self.mutation_field("createTicket", "input: $input").build()

    def update_ticket(self, ticket_id: str, input_data: TicketInput) -> str:
        """Build update ticket mutation."""
        self.add_variable("id", "ID!", ticket_id)
        self.add_variable("input", "TicketInput!", serialize_input(input_data))
        return self.mutation_field("updateTicket", "id: $id, input: $input").build()

    def delete_ticket(self, ticket_id: str) -> str:
        """Build delete ticket mutation."""
        self.add_variable("id", "ID!", ticket_id)
        self._return_fields = ["success", "message"]
        return self.mutation_field("deleteTicket", "id: $id").build()


class ProjectMutationBuilder(MutationBuilder):
    """Builder for project mutations."""

    def __init__(self, detail_level: str = "core"):
        """Initialize project mutation builder.

        Args:
            detail_level: Level of detail for returned fields
        """
        super().__init__()
        self.detail_level = detail_level

        project_fragments = get_project_fields(detail_level)
        self.add_fragments(project_fragments)

        # Set return fields based on fragment
        main_fragment = None
        for fragment in project_fragments:
            if (
                "ProjectSummaryFields" in fragment
                or "ProjectCoreFields" in fragment
                or "ProjectFullFields" in fragment
            ):
                main_fragment = fragment
                break

        if not main_fragment:
            main_fragment = "ProjectCoreFields"

        self._return_fields = [f"...{main_fragment}"]

    def create_project(self, input_data: ProjectInput) -> str:
        """Build create project mutation."""
        self.add_variable("input", "ProjectInput!", serialize_input(input_data))
        return self.mutation_field("createProject", "input: $input").build()

    def update_project(self, project_id: str, input_data: ProjectInput) -> str:
        """Build update project mutation."""
        self.add_variable("id", "ID!", project_id)
        self.add_variable("input", "ProjectInput!", serialize_input(input_data))
        return self.mutation_field("updateProject", "id: $id, input: $input").build()

    def delete_project(self, project_id: str) -> str:
        """Build delete project mutation."""
        self.add_variable("id", "ID!", project_id)
        self._return_fields = ["success", "message"]
        return self.mutation_field("deleteProject", "id: $id").build()

    def create_milestone(self, input_data: ProjectMilestoneInput) -> str:
        """Build create project milestone mutation."""
        self.add_variable("input", "ProjectMilestoneInput!", serialize_input(input_data))
        self._return_fields = ["...ProjectMilestoneFields"]
        self.add_fragment("ProjectMilestoneFields")
        return self.mutation_field("createProjectMilestone", "input: $input").build()

    def update_milestone(self, milestone_id: str, input_data: ProjectMilestoneInput) -> str:
        """Build update project milestone mutation."""
        self.add_variable("id", "ID!", milestone_id)
        self.add_variable("input", "ProjectMilestoneInput!", serialize_input(input_data))
        self._return_fields = ["...ProjectMilestoneFields"]
        self.add_fragment("ProjectMilestoneFields")
        return self.mutation_field("updateProjectMilestone", "id: $id, input: $input").build()

    def delete_milestone(self, milestone_id: str) -> str:
        """Build delete project milestone mutation."""
        self.add_variable("id", "ID!", milestone_id)
        self._return_fields = ["success", "message"]
        return self.mutation_field("deleteProjectMilestone", "id: $id").build()

    def create_task(self, input_data: ProjectTaskInput) -> str:
        """Build create project task mutation."""
        self.add_variable("input", "ProjectTaskInput!", serialize_input(input_data))
        self._return_fields = ["...ProjectTaskFullFields"]
        self.add_fragment("ProjectTaskFullFields")
        return self.mutation_field("createProjectTask", "input: $input").build()

    def update_task(self, task_id: str, input_data: ProjectTaskInput) -> str:
        """Build update project task mutation."""
        self.add_variable("id", "ID!", task_id)
        self.add_variable("input", "ProjectTaskInput!", serialize_input(input_data))
        self._return_fields = ["...ProjectTaskFullFields"]
        self.add_fragment("ProjectTaskFullFields")
        return self.mutation_field("updateProjectTask", "id: $id, input: $input").build()

    def delete_task(self, task_id: str) -> str:
        """Build delete project task mutation."""
        self.add_variable("id", "ID!", task_id)
        self._return_fields = ["success", "message"]
        return self.mutation_field("deleteProjectTask", "id: $id").build()

    def create_time_entry(self, input_data: ProjectTimeEntryInput) -> str:
        """Build create project time entry mutation."""
        self.add_variable("input", "ProjectTimeEntryInput!", serialize_input(input_data))
        self._return_fields = ["...ProjectTimeEntryFields"]
        self.add_fragment("ProjectTimeEntryFields")
        return self.mutation_field("createProjectTimeEntry", "input: $input").build()

    def update_time_entry(self, time_entry_id: str, input_data: ProjectTimeEntryInput) -> str:
        """Build update project time entry mutation."""
        self.add_variable("id", "ID!", time_entry_id)
        self.add_variable("input", "ProjectTimeEntryInput!", serialize_input(input_data))
        self._return_fields = ["...ProjectTimeEntryFields"]
        self.add_fragment("ProjectTimeEntryFields")
        return self.mutation_field("updateProjectTimeEntry", "id: $id, input: $input").build()

    def delete_time_entry(self, time_entry_id: str) -> str:
        """Build delete project time entry mutation."""
        self.add_variable("id", "ID!", time_entry_id)
        self._return_fields = ["success", "message"]
        return self.mutation_field("deleteProjectTimeEntry", "id: $id").build()


class CommentMutationBuilder(MutationBuilder):
    """Builder for comment mutations."""

    def __init__(self, detail_level: str = "core"):
        """Initialize comment mutation builder.

        Args:
            detail_level: Level of detail for returned fields
        """
        super().__init__()
        self.detail_level = detail_level
        self.add_fragments(get_comment_fields(detail_level))

    def create_comment(self, input_data: CommentInput) -> str:
        """Build create comment mutation."""
        self.add_variable("input", "CommentInput!", serialize_input(input_data))

        fragment_name = f"Comment{self.detail_level.capitalize()}Fields"
        self._return_fields = [f"...{fragment_name}"]

        return self.mutation_field("createComment", "input: $input").build()

    def update_comment(self, comment_id: str, input_data: CommentInput) -> str:
        """Build update comment mutation."""
        self.add_variable("id", "ID!", comment_id)
        self.add_variable("input", "CommentInput!", serialize_input(input_data))

        fragment_name = f"Comment{self.detail_level.capitalize()}Fields"
        self._return_fields = [f"...{fragment_name}"]

        return self.mutation_field("updateComment", "id: $id, input: $input").build()

    def delete_comment(self, comment_id: str) -> str:
        """Build delete comment mutation."""
        self.add_variable("id", "ID!", comment_id)
        self._return_fields = ["success", "message"]
        return self.mutation_field("deleteComment", "id: $id").build()

    def add_comment_to_entity(
        self, entity_type: str, entity_id: str, content: str, is_internal: bool = False
    ) -> str:
        """Build mutation to add a comment to an entity.

        Args:
            entity_type: Type of entity (e.g., 'ticket', 'task', 'project')
            entity_id: ID of the entity
            content: Comment content
            is_internal: Whether the comment is internal

        Returns:
            GraphQL mutation string
        """
        input_data = CommentInput(
            entity_type=entity_type,
            entity_id=entity_id,
            content=content,
            is_internal=is_internal,
        )
        return self.create_comment(input_data)

    def reply_to_comment(
        self, parent_comment_id: str, content: str, is_internal: bool = False
    ) -> str:
        """Build mutation to reply to a comment.

        Args:
            parent_comment_id: ID of the parent comment
            content: Reply content
            is_internal: Whether the reply is internal

        Returns:
            GraphQL mutation string
        """
        # Get the parent comment's entity info from context
        # In practice, this would need the entity_type and entity_id from the parent
        # For now, we'll create a basic reply structure
        input_data = CommentInput(
            entity_type="",  # This should be filled from parent context
            entity_id="",  # This should be filled from parent context
            content=content,
            is_internal=is_internal,
            parent_comment_id=parent_comment_id,
        )
        return self.create_comment(input_data)


class UserMutationBuilder(MutationBuilder):
    """Builder for user mutations."""

    def __init__(self, detail_level: str = "core"):
        """Initialize user mutation builder.

        Args:
            detail_level: Level of detail for returned fields
        """
        super().__init__()
        self.detail_level = detail_level
        fragment_names = get_user_fields(detail_level)
        self.add_fragments(fragment_names)

        # Add return fields
        main_fragment = list(fragment_names)[0]
        self.return_field(f"...{main_fragment}")

    def create_user(self, input_data: UserInput) -> str:
        """Build create user mutation.

        Args:
            input_data: User input data

        Returns:
            Complete GraphQL mutation string
        """
        self.add_variable("input", "UserInput!", serialize_input(input_data))
        return self.mutation_field("createUser", "input: $input").build()

    def update_user(self, user_id: str, input_data: UserInput) -> str:
        """Build update user mutation.

        Args:
            user_id: User ID
            input_data: User input data

        Returns:
            Complete GraphQL mutation string
        """
        self.add_variable("id", "ID!", user_id)
        self.add_variable("input", "UserInput!", serialize_input(input_data))
        return self.mutation_field("updateUser", "id: $id, input: $input").build()

    def delete_user(self, user_id: str) -> str:
        """Build delete user mutation.

        Args:
            user_id: User ID

        Returns:
            Complete GraphQL mutation string
        """
        self.add_variable("id", "ID!", user_id)
        self._return_fields = ["success", "message"]  # Override return fields
        return self.mutation_field("deleteUser", "id: $id").build()


# Factory functions for easy builder creation
def create_client_query_builder(detail_level: str = "core") -> ClientQueryBuilder:
    """Create a client query builder.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        ClientQueryBuilder instance
    """
    return ClientQueryBuilder(detail_level)


def create_ticket_query_builder(
    detail_level: str = "core", include_comments: bool = False
) -> TicketQueryBuilder:
    """Create a ticket query builder.

    Args:
        detail_level: Level of detail (summary, core, full)
        include_comments: Whether to include comment fields

    Returns:
        TicketQueryBuilder instance
    """
    return TicketQueryBuilder(detail_level, include_comments)


def create_asset_query_builder(detail_level: str = "core") -> AssetQueryBuilder:
    """Create an asset query builder.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        AssetQueryBuilder instance
    """
    return AssetQueryBuilder(detail_level)


def create_project_query_builder(
    detail_level: str = "core",
    include_milestones: bool = False,
    include_tasks: bool = False,
    include_time_entries: bool = False,
    task_detail: str = "core",
) -> ProjectQueryBuilder:
    """Create a project query builder.

    Args:
        detail_level: Level of detail for projects (summary, core, full)
        include_milestones: Whether to include milestone fields
        include_tasks: Whether to include task fields
        include_time_entries: Whether to include time entry fields
        task_detail: Level of detail for tasks (core, full)

    Returns:
        ProjectQueryBuilder instance
    """
    return ProjectQueryBuilder(
        detail_level=detail_level,
        include_milestones=include_milestones,
        include_tasks=include_tasks,
        include_time_entries=include_time_entries,
        task_detail=task_detail,
    )


def create_client_mutation_builder(detail_level: str = "core") -> ClientMutationBuilder:
    """Create a client mutation builder.

    Args:
        detail_level: Level of detail for returned fields

    Returns:
        ClientMutationBuilder instance
    """
    return ClientMutationBuilder(detail_level)


def create_ticket_mutation_builder(detail_level: str = "core") -> TicketMutationBuilder:
    """Create a ticket mutation builder.

    Args:
        detail_level: Level of detail for returned fields

    Returns:
        TicketMutationBuilder instance
    """
    return TicketMutationBuilder(detail_level)


def create_project_mutation_builder(detail_level: str = "core") -> ProjectMutationBuilder:
    """Create a project mutation builder.

    Args:
        detail_level: Level of detail for returned fields

    Returns:
        ProjectMutationBuilder instance
    """
    return ProjectMutationBuilder(detail_level)


# Time Entry Builders
class TimeEntryQueryBuilder(SelectionQueryBuilder):
    """Builder for time entry-related queries."""

    def __init__(self, detail_level: str = "core"):
        """Initialize time entry query builder.

        Args:
            detail_level: Level of detail (summary, core, full)
        """
        super().__init__()
        self._detail_level = detail_level

        # Add fragments for time entries
        fragments = get_time_entry_fields(detail_level)
        self.add_fragments(fragments)

    def build_get(self, time_entry_id: str) -> str:
        """Build query to get a single time entry.

        Args:
            time_entry_id: Time entry ID

        Returns:
            GraphQL query string
        """
        self.add_variable("id", "ID!", time_entry_id)

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n  ".join(f"...{name}" for name in sorted(self._fragments))

        query = f"""query GetTimeEntry($id: ID!) {{
  timeEntry(id: $id) {{
    {spreads}
  }}
}}

{fragments_str}"""

        return query

    def build_list(
        self,
        filter_obj: Optional[TimeEntryFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> str:
        """Build query to list time entries.

        Args:
            filter_obj: Filter conditions
            pagination: Pagination settings
            sort: Sort settings

        Returns:
            GraphQL query string
        """
        # Add variables
        if filter_obj:
            self.add_variable("filters", "TimeEntryFilter", serialize_input(filter_obj))

        if pagination:
            self.add_variable("page", "Int!", pagination.page)
            self.add_variable("pageSize", "Int!", pagination.pageSize)
        else:
            self.add_variable("page", "Int!", 1)
            self.add_variable("pageSize", "Int!", 50)

        if sort:
            self.add_variable("sortBy", "String", sort.field)
            self.add_variable("sortOrder", "SortOrder", sort.direction)

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n      ".join(f"...{name}" for name in sorted(self._fragments))

        query = f"""query ListTimeEntries($page: Int!, $pageSize: Int!, $filters: TimeEntryFilter, $sortBy: String, $sortOrder: SortOrder) {{
  timeEntries(page: $page, pageSize: $pageSize, filters: $filters, sortBy: $sortBy, sortOrder: $sortOrder) {{
    items {{
      {spreads}
    }}
    pagination {{
      page
      pageSize
      total
      hasNextPage
      hasPreviousPage
    }}
  }}
}}

{fragments_str}"""

        return query

    def build_search(self, search_query: str, pagination: Optional[PaginationArgs] = None) -> str:
        """Build query to search time entries.

        Args:
            search_query: Search query string
            pagination: Pagination settings

        Returns:
            GraphQL query string
        """
        self.add_variable("query", "String!", search_query)

        if pagination:
            self.add_variable("page", "Int!", pagination.page)
            self.add_variable("pageSize", "Int!", pagination.pageSize)
        else:
            self.add_variable("page", "Int!", 1)
            self.add_variable("pageSize", "Int!", 50)

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n      ".join(f"...{name}" for name in sorted(self._fragments))

        query = f"""query SearchTimeEntries($query: String!, $page: Int!, $pageSize: Int!) {{
  searchTimeEntries(query: $query, page: $page, pageSize: $pageSize) {{
    items {{
      {spreads}
    }}
    pagination {{
      page
      pageSize
      total
      hasNextPage
      hasPreviousPage
    }}
  }}
}}

{fragments_str}"""

        return query


class TimerQueryBuilder(SelectionQueryBuilder):
    """Builder for timer-related queries."""

    def __init__(self):
        """Initialize timer query builder."""
        super().__init__()

        # Add fragments for timers
        fragments = get_timer_fields()
        self.add_fragments(fragments)

    def build_get(self, timer_id: str) -> str:
        """Build query to get a single timer.

        Args:
            timer_id: Timer ID

        Returns:
            GraphQL query string
        """
        self.add_variable("id", "ID!", timer_id)

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n  ".join(f"...{name}" for name in sorted(self._fragments))

        query = f"""query GetTimer($id: ID!) {{
  timer(id: $id) {{
    {spreads}
  }}
}}

{fragments_str}"""

        return query

    def build_list(
        self,
        filter_obj: Optional[TimerFilter] = None,
        pagination: Optional[PaginationArgs] = None,
    ) -> str:
        """Build query to list timers.

        Args:
            filter_obj: Filter conditions
            pagination: Pagination settings

        Returns:
            GraphQL query string
        """
        # Add variables
        if filter_obj:
            self.add_variable("filters", "TimerFilter", serialize_input(filter_obj))

        if pagination:
            self.add_variable("page", "Int!", pagination.page)
            self.add_variable("pageSize", "Int!", pagination.pageSize)
        else:
            self.add_variable("page", "Int!", 1)
            self.add_variable("pageSize", "Int!", 50)

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n      ".join(f"...{name}" for name in sorted(self._fragments))

        query = f"""query ListTimers($page: Int!, $pageSize: Int!, $filters: TimerFilter) {{
  timers(page: $page, pageSize: $pageSize, filters: $filters) {{
    items {{
      {spreads}
    }}
    pagination {{
      page
      pageSize
      total
      hasNextPage
      hasPreviousPage
    }}
  }}
}}

{fragments_str}"""

        return query

    def build_active_timer(self, user_id: str) -> str:
        """Build query to get active timer for a user.

        Args:
            user_id: User ID

        Returns:
            GraphQL query string
        """
        self.add_variable("userId", "ID!", user_id)

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n  ".join(f"...{name}" for name in sorted(self._fragments))

        query = f"""query GetActiveTimer($userId: ID!) {{
  activeTimer(userId: $userId) {{
    {spreads}
  }}
}}

{fragments_str}"""

        return query


class TimeEntryMutationBuilder(MutationBuilder):
    """Builder for time entry mutations."""

    def __init__(self, detail_level: str = "core"):
        """Initialize time entry mutation builder.

        Args:
            detail_level: Level of detail for returned fields
        """
        super().__init__()
        self._detail_level = detail_level

        # Add fragments for time entries
        fragments = get_time_entry_fields(detail_level)
        self.add_fragments(fragments)

    def build_create(self, input_data: TimeEntryInput) -> str:
        """Build mutation to create a time entry.

        Args:
            input_data: Time entry input data

        Returns:
            GraphQL mutation string
        """
        self.add_variable("input", "CreateTimeEntryInput!", serialize_input(input_data))

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n  ".join(f"...{name}" for name in sorted(self._fragments))

        mutation = f"""mutation CreateTimeEntry($input: CreateTimeEntryInput!) {{
  createTimeEntry(input: $input) {{
    {spreads}
  }}
}}

{fragments_str}"""

        return mutation

    def build_update(self, time_entry_id: str, input_data: TimeEntryInput) -> str:
        """Build mutation to update a time entry.

        Args:
            time_entry_id: Time entry ID
            input_data: Time entry input data

        Returns:
            GraphQL mutation string
        """
        self.add_variable("id", "ID!", time_entry_id)
        self.add_variable("input", "UpdateTimeEntryInput!", serialize_input(input_data))

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n  ".join(f"...{name}" for name in sorted(self._fragments))

        mutation = f"""mutation UpdateTimeEntry($id: ID!, $input: UpdateTimeEntryInput!) {{
  updateTimeEntry(id: $id, input: $input) {{
    {spreads}
  }}
}}

{fragments_str}"""

        return mutation

    def build_delete(self, time_entry_id: str) -> str:
        """Build mutation to delete a time entry.

        Args:
            time_entry_id: Time entry ID

        Returns:
            GraphQL mutation string
        """
        self.add_variable("id", "ID!", time_entry_id)

        mutation = """mutation DeleteTimeEntry($id: ID!) {
  deleteTimeEntry(id: $id) {
    success
    message
  }
}"""

        return mutation

    def build_bulk_approve(self, approval_input: TimeEntryApprovalInput) -> str:
        """Build mutation to bulk approve/reject time entries.

        Args:
            approval_input: Approval input data

        Returns:
            GraphQL mutation string
        """
        self.add_variable("input", "TimeEntryApprovalInput!", serialize_input(approval_input))

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n      ".join(f"...{name}" for name in sorted(self._fragments))

        mutation = f"""mutation BulkApproveTimeEntries($input: TimeEntryApprovalInput!) {{
  bulkApproveTimeEntries(input: $input) {{
    timeEntries {{
      {spreads}
    }}
    success
    message
  }}
}}

{fragments_str}"""

        return mutation


class TimerMutationBuilder(MutationBuilder):
    """Builder for timer mutations."""

    def __init__(self):
        """Initialize timer mutation builder."""
        super().__init__()

        # Add fragments for timers
        fragments = get_timer_fields()
        self.add_fragments(fragments)

    def build_start(self, input_data: TimerInput) -> str:
        """Build mutation to start a timer.

        Args:
            input_data: Timer input data

        Returns:
            GraphQL mutation string
        """
        self.add_variable("input", "StartTimerInput!", serialize_input(input_data))

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n  ".join(f"...{name}" for name in sorted(self._fragments))

        mutation = f"""mutation StartTimer($input: StartTimerInput!) {{
  startTimer(input: $input) {{
    {spreads}
  }}
}}

{fragments_str}"""

        return mutation

    def build_stop(self, timer_id: str) -> str:
        """Build mutation to stop a timer.

        Args:
            timer_id: Timer ID

        Returns:
            GraphQL mutation string
        """
        self.add_variable("timerId", "ID!", timer_id)

        fragments_str = build_fragments_string(self._fragments)
        time_entry_fragments = get_time_entry_fields("core")
        combined_fragments = self._fragments.union(time_entry_fragments)
        all_fragments_str = build_fragments_string(combined_fragments)

        timer_spreads = "\n    ".join(f"...{name}" for name in sorted(self._fragments))
        time_entry_spreads = "\n    ".join(f"...{name}" for name in sorted(time_entry_fragments))

        mutation = f"""mutation StopTimer($timerId: ID!) {{
  stopTimer(timerId: $timerId) {{
    timer {{
      {timer_spreads}
    }}
    timeEntry {{
      {time_entry_spreads}
    }}
  }}
}}

{all_fragments_str}"""

        return mutation

    def build_pause(self, timer_id: str) -> str:
        """Build mutation to pause a timer.

        Args:
            timer_id: Timer ID

        Returns:
            GraphQL mutation string
        """
        self.add_variable("timerId", "ID!", timer_id)

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n  ".join(f"...{name}" for name in sorted(self._fragments))

        mutation = f"""mutation PauseTimer($timerId: ID!) {{
  pauseTimer(timerId: $timerId) {{
    {spreads}
  }}
}}

{fragments_str}"""

        return mutation

    def build_resume(self, timer_id: str) -> str:
        """Build mutation to resume a timer.

        Args:
            timer_id: Timer ID

        Returns:
            GraphQL mutation string
        """
        self.add_variable("timerId", "ID!", timer_id)

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n  ".join(f"...{name}" for name in sorted(self._fragments))

        mutation = f"""mutation ResumeTimer($timerId: ID!) {{
  resumeTimer(timerId: $timerId) {{
    {spreads}
  }}
}}

{fragments_str}"""

        return mutation


# Factory functions for time entry builders
def create_time_entry_query_builder(detail_level: str = "core") -> TimeEntryQueryBuilder:
    """Create a time entry query builder.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        TimeEntryQueryBuilder instance
    """
    return TimeEntryQueryBuilder(detail_level)


def create_timer_query_builder() -> TimerQueryBuilder:
    """Create a timer query builder.

    Returns:
        TimerQueryBuilder instance
    """
    return TimerQueryBuilder()


def create_time_entry_mutation_builder(detail_level: str = "core") -> TimeEntryMutationBuilder:
    """Create a time entry mutation builder.

    Args:
        detail_level: Level of detail for returned fields

    Returns:
        TimeEntryMutationBuilder instance
    """
    return TimeEntryMutationBuilder(detail_level)


def create_task_query_builder(
    detail_level: str = "core",
    include_comments: bool = False,
    include_time_entries: bool = False,
    include_template: bool = False,
) -> TaskQueryBuilder:
    """Create a task query builder.

    Args:
        detail_level: Level of detail (summary, core, full)
        include_comments: Whether to include comment fields
        include_time_entries: Whether to include time entry fields
        include_template: Whether to include template fields

    Returns:
        TaskQueryBuilder instance
    """
    return TaskQueryBuilder(detail_level, include_comments, include_time_entries, include_template)


def create_comment_query_builder(
    detail_level: str = "core", include_attachments: bool = False
) -> CommentQueryBuilder:
    """Create a comment query builder.

    Args:
        detail_level: Level of detail (summary, core, full)
        include_attachments: Whether to include attachment fields

    Returns:
        CommentQueryBuilder instance
    """
    return CommentQueryBuilder(detail_level, include_attachments)


def create_comment_mutation_builder(detail_level: str = "core") -> CommentMutationBuilder:
    """Create a comment mutation builder.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        CommentMutationBuilder instance
    """
    return CommentMutationBuilder(detail_level)


def create_user_query_builder(detail_level: str = "core") -> UserQueryBuilder:
    """Create a user query builder.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        UserQueryBuilder instance
    """
    return UserQueryBuilder(detail_level)


def create_user_mutation_builder(detail_level: str = "core") -> UserMutationBuilder:
    """Create a user mutation builder.

    Args:
        detail_level: Level of detail for returned fields

    Returns:
        UserMutationBuilder instance
    """
    return UserMutationBuilder(detail_level)


def create_timer_mutation_builder() -> TimerMutationBuilder:
    """Create a timer mutation builder.

    Returns:
        TimerMutationBuilder instance
    """
    return TimerMutationBuilder()


# Monitoring builders
class MonitoringAgentQueryBuilder(QueryBuilder):
    """Query builder for monitoring agents."""

    def __init__(self, detail_level: str = "core"):
        """Initialize the monitoring agent query builder.

        Args:
            detail_level: Level of detail (summary, core, full)
        """
        super().__init__()
        self.detail_level = detail_level
        self._fragments.update(get_monitoring_agent_fields(detail_level))

    def get(self, agent_id: str) -> tuple[str, Dict[str, Any]]:
        """Build query to get a single monitoring agent.

        Args:
            agent_id: Monitoring agent ID

        Returns:
            Tuple of (query_string, variables)
        """
        self.add_variable("id", "ID!", agent_id)

        fields_fragment = list(self._fragments)[0]
        query = f"""
        query GetMonitoringAgent($id: ID!) {{
            monitoringAgent(id: $id) {{
                ...{fields_fragment}
            }}
        }}
        """

        return self._build_query_with_fragments(query)

    def list(
        self,
        filter: Optional[MonitoringAgentFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> tuple[str, Dict[str, Any]]:
        """Build query to list monitoring agents.

        Args:
            filter: Filter criteria
            pagination: Pagination parameters
            sort: Sort parameters

        Returns:
            Tuple of (query_string, variables)
        """
        if filter:
            self.add_variable("filter", "MonitoringAgentFilter", serialize_input(filter))
        if pagination:
            self.add_variable("pagination", "PaginationInput", serialize_input(pagination))
        if sort:
            self.add_variable("sort", "SortInput", serialize_input(sort))

        fields_fragment = list(self._fragments)[0]
        query = f"""
        query ListMonitoringAgents(
            $filter: MonitoringAgentFilter
            $pagination: PaginationInput
            $sort: SortInput
        ) {{
            monitoringAgents(
                filter: $filter
                pagination: $pagination
                sort: $sort
            ) {{
                items {{
                    ...{fields_fragment}
                }}
                pagination {{
                    ...PaginationInfo
                }}
            }}
        }}
        """

        self._fragments.add("PaginationInfo")
        return self._build_query_with_fragments(query)

    def search(self, query: str) -> tuple[str, Dict[str, Any]]:
        """Build query to search monitoring agents.

        Args:
            query: Search query string

        Returns:
            Tuple of (query_string, variables)
        """
        self.add_variable("query", "String!", query)

        fields_fragment = list(self._fragments)[0]
        search_query = f"""
        query SearchMonitoringAgents($query: String!) {{
            searchMonitoringAgents(query: $query) {{
                items {{
                    ...{fields_fragment}
                }}
                pagination {{
                    ...PaginationInfo
                }}
            }}
        }}
        """

        self._fragments.add("PaginationInfo")
        return self._build_query_with_fragments(search_query)


class MonitoringAgentMutationBuilder(MutationBuilder):
    """Mutation builder for monitoring agents."""

    def __init__(self, detail_level: str = "core"):
        """Initialize the monitoring agent mutation builder.

        Args:
            detail_level: Level of detail for returned fields
        """
        super().__init__()
        self.detail_level = detail_level
        self._fragments.update(get_monitoring_agent_fields(detail_level))

    def create(self, agent_input: MonitoringAgentInput) -> tuple[str, Dict[str, Any]]:
        """Build mutation to create a monitoring agent.

        Args:
            agent_input: Agent creation input

        Returns:
            Tuple of (mutation_string, variables)
        """
        self.add_variable("input", "MonitoringAgentInput!", serialize_input(agent_input))

        fields_fragment = list(self._fragments)[0]
        mutation = f"""
        mutation CreateMonitoringAgent($input: MonitoringAgentInput!) {{
            createMonitoringAgent(input: $input) {{
                ...{fields_fragment}
            }}
        }}
        """

        return self._build_query_with_fragments(mutation)

    def update(
        self, agent_id: str, agent_input: MonitoringAgentInput
    ) -> tuple[str, Dict[str, Any]]:
        """Build mutation to update a monitoring agent.

        Args:
            agent_id: Agent ID
            agent_input: Agent update input

        Returns:
            Tuple of (mutation_string, variables)
        """
        self.add_variable("id", "ID!", agent_id)
        self.add_variable("input", "MonitoringAgentInput!", serialize_input(agent_input))

        fields_fragment = list(self._fragments)[0]
        mutation = f"""
        mutation UpdateMonitoringAgent($id: ID!, $input: MonitoringAgentInput!) {{
            updateMonitoringAgent(id: $id, input: $input) {{
                ...{fields_fragment}
            }}
        }}
        """

        return self._build_query_with_fragments(mutation)

    def delete(self, agent_id: str) -> tuple[str, Dict[str, Any]]:
        """Build mutation to delete a monitoring agent.

        Args:
            agent_id: Agent ID

        Returns:
            Tuple of (mutation_string, variables)
        """
        self.add_variable("id", "ID!", agent_id)

        mutation = """
        mutation DeleteMonitoringAgent($id: ID!) {
            deleteMonitoringAgent(id: $id) {
                success
                message
            }
        }
        """

        return mutation, self._variables

    def install(
        self, host_id: str, config: Optional[Dict[str, Any]] = None
    ) -> tuple[str, Dict[str, Any]]:
        """Build mutation to install a monitoring agent.

        Args:
            host_id: Host ID to install agent on
            config: Optional installation configuration

        Returns:
            Tuple of (mutation_string, variables)
        """
        self.add_variable("hostId", "ID!", host_id)
        if config:
            self.add_variable("config", "JSON", config)

        fields_fragment = list(self._fragments)[0]
        mutation = f"""
        mutation InstallMonitoringAgent($hostId: ID!, $config: JSON) {{
            installMonitoringAgent(hostId: $hostId, config: $config) {{
                ...{fields_fragment}
            }}
        }}
        """

        return self._build_query_with_fragments(mutation)


class MonitoringCheckQueryBuilder(QueryBuilder):
    """Query builder for monitoring checks."""

    def __init__(self, detail_level: str = "core"):
        """Initialize the monitoring check query builder.

        Args:
            detail_level: Level of detail (summary, core, full)
        """
        super().__init__()
        self.detail_level = detail_level
        self._fragments.update(get_monitoring_check_fields(detail_level))

    def get(self, check_id: str) -> tuple[str, Dict[str, Any]]:
        """Build query to get a single monitoring check.

        Args:
            check_id: Monitoring check ID

        Returns:
            Tuple of (query_string, variables)
        """
        self.add_variable("id", "ID!", check_id)

        fields_fragment = list(self._fragments)[0]
        query = f"""
        query GetMonitoringCheck($id: ID!) {{
            monitoringCheck(id: $id) {{
                ...{fields_fragment}
            }}
        }}
        """

        return self._build_query_with_fragments(query)

    def list(
        self,
        filter: Optional[MonitoringCheckFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> tuple[str, Dict[str, Any]]:
        """Build query to list monitoring checks.

        Args:
            filter: Filter criteria
            pagination: Pagination parameters
            sort: Sort parameters

        Returns:
            Tuple of (query_string, variables)
        """
        if filter:
            self.add_variable("filter", "MonitoringCheckFilter", serialize_input(filter))
        if pagination:
            self.add_variable("pagination", "PaginationInput", serialize_input(pagination))
        if sort:
            self.add_variable("sort", "SortInput", serialize_input(sort))

        fields_fragment = list(self._fragments)[0]
        query = f"""
        query ListMonitoringChecks(
            $filter: MonitoringCheckFilter
            $pagination: PaginationInput
            $sort: SortInput
        ) {{
            monitoringChecks(
                filter: $filter
                pagination: $pagination
                sort: $sort
            ) {{
                items {{
                    ...{fields_fragment}
                }}
                pagination {{
                    ...PaginationInfo
                }}
            }}
        }}
        """

        self._fragments.add("PaginationInfo")
        return self._build_query_with_fragments(query)


class MonitoringCheckMutationBuilder(MutationBuilder):
    """Mutation builder for monitoring checks."""

    def __init__(self, detail_level: str = "core"):
        """Initialize the monitoring check mutation builder.

        Args:
            detail_level: Level of detail for returned fields
        """
        super().__init__()
        self.detail_level = detail_level
        self._fragments.update(get_monitoring_check_fields(detail_level))

    def create(self, check_input: MonitoringCheckInput) -> tuple[str, Dict[str, Any]]:
        """Build mutation to create a monitoring check.

        Args:
            check_input: Check creation input

        Returns:
            Tuple of (mutation_string, variables)
        """
        self.add_variable("input", "MonitoringCheckInput!", serialize_input(check_input))

        fields_fragment = list(self._fragments)[0]
        mutation = f"""
        mutation CreateMonitoringCheck($input: MonitoringCheckInput!) {{
            createMonitoringCheck(input: $input) {{
                ...{fields_fragment}
            }}
        }}
        """

        return self._build_query_with_fragments(mutation)

    def update(
        self, check_id: str, check_input: MonitoringCheckInput
    ) -> tuple[str, Dict[str, Any]]:
        """Build mutation to update a monitoring check.

        Args:
            check_id: Check ID
            check_input: Check update input

        Returns:
            Tuple of (mutation_string, variables)
        """
        self.add_variable("id", "ID!", check_id)
        self.add_variable("input", "MonitoringCheckInput!", serialize_input(check_input))

        fields_fragment = list(self._fragments)[0]
        mutation = f"""
        mutation UpdateMonitoringCheck($id: ID!, $input: MonitoringCheckInput!) {{
            updateMonitoringCheck(id: $id, input: $input) {{
                ...{fields_fragment}
            }}
        }}
        """

        return self._build_query_with_fragments(mutation)

    def delete(self, check_id: str) -> tuple[str, Dict[str, Any]]:
        """Build mutation to delete a monitoring check.

        Args:
            check_id: Check ID

        Returns:
            Tuple of (mutation_string, variables)
        """
        self.add_variable("id", "ID!", check_id)

        mutation = """
        mutation DeleteMonitoringCheck($id: ID!) {
            deleteMonitoringCheck(id: $id) {
                success
                message
            }
        }
        """

        return mutation, self._variables

    def run_check(self, check_id: str) -> tuple[str, Dict[str, Any]]:
        """Build mutation to manually run a monitoring check.

        Args:
            check_id: Check ID

        Returns:
            Tuple of (mutation_string, variables)
        """
        self.add_variable("id", "ID!", check_id)

        mutation = """
        mutation RunMonitoringCheck($id: ID!) {
            runMonitoringCheck(id: $id) {
                success
                message
                result
            }
        }
        """

        return mutation, self._variables


class MonitoringAlertQueryBuilder(QueryBuilder):
    """Query builder for monitoring alerts."""

    def __init__(self, detail_level: str = "core"):
        """Initialize the monitoring alert query builder.

        Args:
            detail_level: Level of detail (summary, core, full)
        """
        super().__init__()
        self.detail_level = detail_level
        self._fragments.update(get_monitoring_alert_fields(detail_level))

    def get(self, alert_id: str) -> tuple[str, Dict[str, Any]]:
        """Build query to get a single monitoring alert.

        Args:
            alert_id: Monitoring alert ID

        Returns:
            Tuple of (query_string, variables)
        """
        self.add_variable("id", "ID!", alert_id)

        fields_fragment = list(self._fragments)[0]
        query = f"""
        query GetMonitoringAlert($id: ID!) {{
            monitoringAlert(id: $id) {{
                ...{fields_fragment}
            }}
        }}
        """

        return self._build_query_with_fragments(query)

    def list(
        self,
        filter: Optional[MonitoringAlertFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> tuple[str, Dict[str, Any]]:
        """Build query to list monitoring alerts.

        Args:
            filter: Filter criteria
            pagination: Pagination parameters
            sort: Sort parameters

        Returns:
            Tuple of (query_string, variables)
        """
        if filter:
            self.add_variable("filter", "MonitoringAlertFilter", serialize_input(filter))
        if pagination:
            self.add_variable("pagination", "PaginationInput", serialize_input(pagination))
        if sort:
            self.add_variable("sort", "SortInput", serialize_input(sort))

        fields_fragment = list(self._fragments)[0]
        query = f"""
        query ListMonitoringAlerts(
            $filter: MonitoringAlertFilter
            $pagination: PaginationInput
            $sort: SortInput
        ) {{
            monitoringAlerts(
                filter: $filter
                pagination: $pagination
                sort: $sort
            ) {{
                items {{
                    ...{fields_fragment}
                }}
                pagination {{
                    ...PaginationInfo
                }}
            }}
        }}
        """

        self._fragments.add("PaginationInfo")
        return self._build_query_with_fragments(query)


class MonitoringAlertMutationBuilder(MutationBuilder):
    """Mutation builder for monitoring alerts."""

    def __init__(self, detail_level: str = "core"):
        """Initialize the monitoring alert mutation builder.

        Args:
            detail_level: Level of detail for returned fields
        """
        super().__init__()
        self.detail_level = detail_level
        self._fragments.update(get_monitoring_alert_fields(detail_level))

    def create(self, alert_input: MonitoringAlertInput) -> tuple[str, Dict[str, Any]]:
        """Build mutation to create a monitoring alert.

        Args:
            alert_input: Alert creation input

        Returns:
            Tuple of (mutation_string, variables)
        """
        self.add_variable("input", "MonitoringAlertInput!", serialize_input(alert_input))

        fields_fragment = list(self._fragments)[0]
        mutation = f"""
        mutation CreateMonitoringAlert($input: MonitoringAlertInput!) {{
            createMonitoringAlert(input: $input) {{
                ...{fields_fragment}
            }}
        }}
        """

        return self._build_query_with_fragments(mutation)

    def acknowledge(
        self, alert_id: str, comment: Optional[str] = None
    ) -> tuple[str, Dict[str, Any]]:
        """Build mutation to acknowledge a monitoring alert.

        Args:
            alert_id: Alert ID
            comment: Optional acknowledgment comment

        Returns:
            Tuple of (mutation_string, variables)
        """
        self.add_variable("id", "ID!", alert_id)
        if comment:
            self.add_variable("comment", "String", comment)

        fields_fragment = list(self._fragments)[0]
        mutation = f"""
        mutation AcknowledgeMonitoringAlert($id: ID!, $comment: String) {{
            acknowledgeMonitoringAlert(id: $id, comment: $comment) {{
                ...{fields_fragment}
            }}
        }}
        """

        return self._build_query_with_fragments(mutation)

    def resolve(self, alert_id: str, comment: Optional[str] = None) -> tuple[str, Dict[str, Any]]:
        """Build mutation to resolve a monitoring alert.

        Args:
            alert_id: Alert ID
            comment: Optional resolution comment

        Returns:
            Tuple of (mutation_string, variables)
        """
        self.add_variable("id", "ID!", alert_id)
        if comment:
            self.add_variable("comment", "String", comment)

        fields_fragment = list(self._fragments)[0]
        mutation = f"""
        mutation ResolveMonitoringAlert($id: ID!, $comment: String) {{
            resolveMonitoringAlert(id: $id, comment: $comment) {{
                ...{fields_fragment}
            }}
        }}
        """

        return self._build_query_with_fragments(mutation)

    def silence(
        self, alert_id: str, duration_minutes: int, comment: Optional[str] = None
    ) -> tuple[str, Dict[str, Any]]:
        """Build mutation to silence a monitoring alert.

        Args:
            alert_id: Alert ID
            duration_minutes: Duration to silence in minutes
            comment: Optional silence comment

        Returns:
            Tuple of (mutation_string, variables)
        """
        self.add_variable("id", "ID!", alert_id)
        self.add_variable("durationMinutes", "Int!", duration_minutes)
        if comment:
            self.add_variable("comment", "String", comment)

        fields_fragment = list(self._fragments)[0]
        mutation = f"""
        mutation SilenceMonitoringAlert($id: ID!, $durationMinutes: Int!, $comment: String) {{
            silenceMonitoringAlert(id: $id, durationMinutes: $durationMinutes, comment: $comment) {{
                ...{fields_fragment}
            }}
        }}
        """

        return self._build_query_with_fragments(mutation)


class MonitoringMetricQueryBuilder(QueryBuilder):
    """Query builder for monitoring metrics."""

    def __init__(self, detail_level: str = "core"):
        """Initialize the monitoring metric query builder.

        Args:
            detail_level: Level of detail (summary, core, full)
        """
        super().__init__()
        self.detail_level = detail_level
        self._fragments.update(get_monitoring_metric_fields(detail_level))

    def get(self, metric_id: str) -> tuple[str, Dict[str, Any]]:
        """Build query to get a single monitoring metric.

        Args:
            metric_id: Monitoring metric ID

        Returns:
            Tuple of (query_string, variables)
        """
        self.add_variable("id", "ID!", metric_id)

        fields_fragment = list(self._fragments)[0]
        query = f"""
        query GetMonitoringMetric($id: ID!) {{
            monitoringMetric(id: $id) {{
                ...{fields_fragment}
            }}
        }}
        """

        return self._build_query_with_fragments(query)

    def list(
        self,
        filter: Optional[MonitoringMetricFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> tuple[str, Dict[str, Any]]:
        """Build query to list monitoring metrics.

        Args:
            filter: Filter criteria
            pagination: Pagination parameters
            sort: Sort parameters

        Returns:
            Tuple of (query_string, variables)
        """
        if filter:
            self.add_variable("filter", "MonitoringMetricFilter", serialize_input(filter))
        if pagination:
            self.add_variable("pagination", "PaginationInput", serialize_input(pagination))
        if sort:
            self.add_variable("sort", "SortInput", serialize_input(sort))

        fields_fragment = list(self._fragments)[0]
        query = f"""
        query ListMonitoringMetrics(
            $filter: MonitoringMetricFilter
            $pagination: PaginationInput
            $sort: SortInput
        ) {{
            monitoringMetrics(
                filter: $filter
                pagination: $pagination
                sort: $sort
            ) {{
                items {{
                    ...{fields_fragment}
                }}
                pagination {{
                    ...PaginationInfo
                }}
            }}
        }}
        """

        self._fragments.add("PaginationInfo")
        return self._build_query_with_fragments(query)

    def get_dashboard_data(
        self,
        agent_ids: Optional[List[str]] = None,
        check_ids: Optional[List[str]] = None,
        time_range_minutes: int = 60,
    ) -> tuple[str, Dict[str, Any]]:
        """Build query to get monitoring dashboard data.

        Args:
            agent_ids: Optional list of agent IDs to filter by
            check_ids: Optional list of check IDs to filter by
            time_range_minutes: Time range in minutes to look back

        Returns:
            Tuple of (query_string, variables)
        """
        if agent_ids:
            self.add_variable("agentIds", "[ID!]", agent_ids)
        if check_ids:
            self.add_variable("checkIds", "[ID!]", check_ids)
        self.add_variable("timeRangeMinutes", "Int!", time_range_minutes)

        query = """
        query GetMonitoringDashboardData(
            $agentIds: [ID!]
            $checkIds: [ID!]
            $timeRangeMinutes: Int!
        ) {
            monitoringDashboard(
                agentIds: $agentIds
                checkIds: $checkIds
                timeRangeMinutes: $timeRangeMinutes
            ) {
                agentSummary {
                    totalAgents
                    onlineAgents
                    offlineAgents
                    degradedAgents
                }
                checkSummary {
                    totalChecks
                    healthyChecks
                    warningChecks
                    criticalChecks
                }
                alertSummary {
                    activeAlerts
                    acknowledgedAlerts
                    criticalAlerts
                    highPriorityAlerts
                }
                recentMetrics {
                    name
                    value
                    unit
                    timestamp
                    status
                }
            }
        }
        """

        return query, self._variables


class MonitoringMetricMutationBuilder(MutationBuilder):
    """Mutation builder for monitoring metrics."""

    def __init__(self, detail_level: str = "core"):
        """Initialize the monitoring metric mutation builder.

        Args:
            detail_level: Level of detail for returned fields
        """
        super().__init__()
        self.detail_level = detail_level
        self._fragments.update(get_monitoring_metric_fields(detail_level))

    def create(self, metric_input: MonitoringMetricInput) -> tuple[str, Dict[str, Any]]:
        """Build mutation to create a monitoring metric.

        Args:
            metric_input: Metric creation input

        Returns:
            Tuple of (mutation_string, variables)
        """
        self.add_variable("input", "MonitoringMetricInput!", serialize_input(metric_input))

        fields_fragment = list(self._fragments)[0]
        mutation = f"""
        mutation CreateMonitoringMetric($input: MonitoringMetricInput!) {{
            createMonitoringMetric(input: $input) {{
                ...{fields_fragment}
            }}
        }}
        """

        return self._build_query_with_fragments(mutation)

    def record_value(
        self,
        metric_name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        timestamp: Optional[str] = None,
    ) -> tuple[str, Dict[str, Any]]:
        """Build mutation to record a metric value.

        Args:
            metric_name: Name of the metric
            value: Metric value
            labels: Optional labels for the metric
            timestamp: Optional timestamp (ISO format)

        Returns:
            Tuple of (mutation_string, variables)
        """
        self.add_variable("metricName", "String!", metric_name)
        self.add_variable("value", "Float!", value)
        if labels:
            self.add_variable("labels", "JSON", labels)
        if timestamp:
            self.add_variable("timestamp", "String", timestamp)

        mutation = """
        mutation RecordMetricValue(
            $metricName: String!
            $value: Float!
            $labels: JSON
            $timestamp: String
        ) {
            recordMetricValue(
                metricName: $metricName
                value: $value
                labels: $labels
                timestamp: $timestamp
            ) {
                success
                message
            }
        }
        """

        return mutation, self._variables


# Factory functions for monitoring builders
def create_monitoring_agent_query_builder(
    detail_level: str = "core",
) -> MonitoringAgentQueryBuilder:
    """Create a monitoring agent query builder.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        MonitoringAgentQueryBuilder instance
    """
    return MonitoringAgentQueryBuilder(detail_level)


def create_monitoring_agent_mutation_builder(
    detail_level: str = "core",
) -> MonitoringAgentMutationBuilder:
    """Create a monitoring agent mutation builder.

    Args:
        detail_level: Level of detail for returned fields

    Returns:
        MonitoringAgentMutationBuilder instance
    """
    return MonitoringAgentMutationBuilder(detail_level)


def create_monitoring_check_query_builder(
    detail_level: str = "core",
) -> MonitoringCheckQueryBuilder:
    """Create a monitoring check query builder.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        MonitoringCheckQueryBuilder instance
    """
    return MonitoringCheckQueryBuilder(detail_level)


def create_monitoring_check_mutation_builder(
    detail_level: str = "core",
) -> MonitoringCheckMutationBuilder:
    """Create a monitoring check mutation builder.

    Args:
        detail_level: Level of detail for returned fields

    Returns:
        MonitoringCheckMutationBuilder instance
    """
    return MonitoringCheckMutationBuilder(detail_level)


def create_monitoring_alert_query_builder(
    detail_level: str = "core",
) -> MonitoringAlertQueryBuilder:
    """Create a monitoring alert query builder.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        MonitoringAlertQueryBuilder instance
    """
    return MonitoringAlertQueryBuilder(detail_level)


def create_monitoring_alert_mutation_builder(
    detail_level: str = "core",
) -> MonitoringAlertMutationBuilder:
    """Create a monitoring alert mutation builder.

    Args:
        detail_level: Level of detail for returned fields

    Returns:
        MonitoringAlertMutationBuilder instance
    """
    return MonitoringAlertMutationBuilder(detail_level)


def create_monitoring_metric_query_builder(
    detail_level: str = "core",
) -> MonitoringMetricQueryBuilder:
    """Create a monitoring metric query builder.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        MonitoringMetricQueryBuilder instance
    """
    return MonitoringMetricQueryBuilder(detail_level)


def create_monitoring_metric_mutation_builder(
    detail_level: str = "core",
) -> MonitoringMetricMutationBuilder:
    """Create a monitoring metric mutation builder.

    Args:
        detail_level: Level of detail for returned fields

    Returns:
        MonitoringMetricMutationBuilder instance
    """
    return MonitoringMetricMutationBuilder(detail_level)
