# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""GraphQL utilities for the py-superops client library.

This package provides type-safe GraphQL query building, common queries,
and response handling for the SuperOps API.

Key Components:
    - Types: GraphQL type definitions and response models
    - Fragments: Reusable GraphQL fragments for common fields
    - Builder: Type-safe query and mutation builder classes
    - Queries: Pre-built common queries for SuperOps resources

Example Usage:
    ```python
    from py_superops.graphql import (
        CommonQueries,
        ClientQueryBuilder,
        ClientFilter,
        PaginationArgs,
        ClientStatus
    )

    # Using pre-built queries
    query, variables = CommonQueries.list_active_clients(page=1, page_size=25)

    # Using builders for custom queries
    builder = ClientQueryBuilder(detail_level="full")
    filter_obj = ClientFilter(status=ClientStatus.ACTIVE)
    pagination = PaginationArgs(page=1, pageSize=25)

    query = builder.build_list(filter_obj=filter_obj, pagination=pagination)
    variables = builder.get_variables()

    # Execute with SuperOpsClient
    async with SuperOpsClient(config) as client:
        response = await client.execute_query(query, variables)
        data = response['data']['clients']
    ```
"""

# Query and mutation builders
from .builder import (  # Base builders; Specific builders; Factory functions
    AssetQueryBuilder,
    ClientMutationBuilder,
    ClientQueryBuilder,
    CommentMutationBuilder,
    CommentQueryBuilder,
    MutationBuilder,
    ProjectMutationBuilder,
    ProjectQueryBuilder,
    QueryBuilder,
    SelectionQueryBuilder,
    TicketMutationBuilder,
    TicketQueryBuilder,
    UserMutationBuilder,
    UserQueryBuilder,
    TimeEntryMutationBuilder,
    TimeEntryQueryBuilder,
    TimerMutationBuilder,
    TimerQueryBuilder,
    create_asset_query_builder,
    create_client_mutation_builder,
    create_client_query_builder,
    create_comment_mutation_builder,
    create_comment_query_builder,
    create_project_mutation_builder,
    create_project_query_builder,
    create_ticket_mutation_builder,
    create_ticket_query_builder,
    create_user_mutation_builder,
    create_user_query_builder,
    create_time_entry_mutation_builder,
    create_time_entry_query_builder,
    create_timer_mutation_builder,
    create_timer_query_builder,
)

# GraphQL fragments
from .fragments import (
    ALL_FRAGMENTS,
    ASSET_CORE_FIELDS,
    ASSET_FRAGMENTS,
    ASSET_FULL_FIELDS,
    ASSET_SUMMARY_FIELDS,
    BASE_FIELDS,
    CLIENT_CORE_FIELDS,
    CLIENT_FRAGMENTS,
    CLIENT_FULL_FIELDS,
    CLIENT_SUMMARY_FIELDS,
    COMMENT_CORE_FIELDS,
    COMMENT_FRAGMENTS,
    COMMENT_FULL_FIELDS,
    COMMENT_SUMMARY_FIELDS,
    CONTACT_CORE_FIELDS,
    CONTACT_FRAGMENTS,
    CONTACT_FULL_FIELDS,
    CONTRACT_CORE_FIELDS,
    CONTRACT_FRAGMENTS,
    CONTRACT_FULL_FIELDS,
    CONTRACT_RATE_FIELDS,
    CONTRACT_SLA_FIELDS,
    CONTRACT_SUMMARY_FIELDS,
    KB_ARTICLE_CORE_FIELDS,
    KB_ARTICLE_FULL_FIELDS,
    KB_ARTICLE_SUMMARY_FIELDS,
    KB_COLLECTION_CORE_FIELDS,
    KB_COLLECTION_FULL_FIELDS,
    KB_FRAGMENTS,
    PAGINATION_INFO,
    PROJECT_CORE_FIELDS,
    PROJECT_FRAGMENTS,
    PROJECT_FULL_FIELDS,
    PROJECT_MILESTONE_FIELDS,
    PROJECT_SUMMARY_FIELDS,
    PROJECT_TASK_CORE_FIELDS,
    PROJECT_TASK_FULL_FIELDS,
    PROJECT_TIME_ENTRY_FIELDS,
    SITE_CORE_FIELDS,
    SITE_FRAGMENTS,
    SITE_FULL_FIELDS,
    TICKET_COMMENT_FIELDS,
    TICKET_CORE_FIELDS,
    TICKET_FRAGMENTS,
    TICKET_FULL_FIELDS,
    TICKET_SUMMARY_FIELDS,
    USER_CORE_FIELDS,
    USER_FRAGMENTS,
    USER_FULL_FIELDS,
    USER_SUMMARY_FIELDS,
    WEBHOOK_CORE_FIELDS,
    WEBHOOK_DELIVERY_FIELDS,
    WEBHOOK_EVENT_RECORD_FIELDS,
    WEBHOOK_FRAGMENTS,
    WEBHOOK_FULL_FIELDS,
    WEBHOOK_SUMMARY_FIELDS,
    TIME_ENTRY_CORE_FIELDS,
    TIME_ENTRY_FRAGMENTS,
    TIME_ENTRY_FULL_FIELDS,
    TIME_ENTRY_SUMMARY_FIELDS,
    TIME_ENTRY_TEMPLATE_FIELDS,
    TIMER_FIELDS,
    build_fragments_string,
    create_query_with_fragments,
    get_asset_fields,
    get_client_fields,
    get_comment_fields,
    get_contract_fields,
    get_fragment_spreads,
    get_kb_fields,
    get_project_fields,
    get_ticket_fields,
    get_user_fields,
    get_webhook_fields,
    get_time_entry_fields,
    resolve_dependencies,
)

# Pre-built queries
from .queries import CommonQueries, SuperOpsQueries

# Type definitions and models
from .types import (  # Base types; Enums; Models; Filters; Input types for mutations; Response types; Utility functions
    Asset,
    AssetFilter,
    AssetInput,
    AssetsResponse,
    AssetStatus,
    AttachmentType,
    BaseModel,
    BillingCycle,
    Client,
    ClientFilter,
    ClientInput,
    ClientsResponse,
    ClientStatus,
    Comment,
    CommentAttachment,
    CommentType,
    Contact,
    ContactInput,
    ContactsResponse,
    Contract,
    ContractFilter,
    ContractInput,
    ContractRate,
    ContractRateInput,
    ContractRatesResponse,
    ContractSLA,
    ContractSLAInput,
    ContractSLAsResponse,
    ContractsResponse,
    ContractStatus,
    ContractType,
    EntityType,
    GraphQLResponse,
    KnowledgeBaseArticle,
    KnowledgeBaseArticleInput,
    KnowledgeBaseArticlesResponse,
    KnowledgeBaseCollection,
    KnowledgeBaseCollectionInput,
    KnowledgeBaseCollectionsResponse,
    PaginatedResponse,
    PaginationArgs,
    PaginationInfo,
    Project,
    ProjectFilter,
    ProjectInput,
    ProjectMilestone,
    ProjectPriority,
    ProjectsResponse,
    ProjectStatus,
    ProjectTask,
    ProjectTimeEntry,
    Site,
    SiteInput,
    SitesResponse,
    SLALevel,
    SortArgs,
    Ticket,
    TicketComment,
    TicketFilter,
    TicketInput,
    TicketPriority,
    TicketsResponse,
    TicketStatus,
    User,
    UserFilter,
    UserInput,
    UserRole,
    UsersResponse,
    UserStatus,
    Webhook,
    WebhookDeliveriesResponse,
    WebhookDelivery,
    WebhookDeliveryFilter,
    WebhookEvent,
    WebhookEventRecord,
    WebhookEventRecordsResponse,
    WebhookFilter,
    WebhookInput,
    WebhooksResponse,
    WebhookStatus,
    WebhookTestInput,
    TimeEntriesResponse,
    TimeEntry,
    TimeEntryFilter,
    TimeEntryInput,
    TimeEntryStatus,
    TimeEntryTemplate,
    TimeEntryTemplateInput,
    TimeEntryType,
    Timer,
    TimerFilter,
    TimerInput,
    TimersResponse,
    TimerState,
    convert_datetime_to_iso,
    convert_iso_to_datetime,
    serialize_filter_value,
    serialize_input,
)

# Version information
__version__ = "0.1.0"
__all__ = [
    # Types and models
    "GraphQLResponse",
    "PaginationInfo",
    "BaseModel",
    "PaginationArgs",
    "SortArgs",
    "TicketStatus",
    "TicketPriority",
    "AssetStatus",
    "ClientStatus",
    "BillingCycle",
    "ContractStatus",
    "ContractType",
    "SLALevel",
    "ProjectStatus",
    "ProjectPriority",
    "WebhookEvent",
    "WebhookStatus",
    "TimeEntryStatus",
    "TimeEntryType",
    "TimerState",
    "Client",
    "Comment",
    "CommentAttachment",
    "CommentType",
    "Contact",
    "Site",
    "Asset",
    "Ticket",
    "TicketComment",
    "Contract",
    "ContractSLA",
    "ContractRate",
    "Project",
    "ProjectMilestone",
    "ProjectTask",
    "ProjectTimeEntry",
    "TimeEntry",
    "Timer",
    "TimeEntryTemplate",
    "KnowledgeBaseCollection",
    "KnowledgeBaseArticle",
    "User",
    "Webhook",
    "WebhookDelivery",
    "WebhookEventRecord",
    "ClientFilter",
    "TicketFilter",
    "AssetFilter",
    "ContractFilter",
    "ProjectFilter",
    "UserFilter",
    "WebhookFilter",
    "WebhookDeliveryFilter",
    "ClientInput",
    "TicketInput",
    "AssetInput",
    "ProjectInput",
    "TimeEntryFilter",
    "TimerFilter",
    "ClientInput",
    "TicketInput",
    "AssetInput",
    "TimeEntryInput",
    "TimerInput",
    "TimeEntryTemplateInput",
    "ContactInput",
    "SiteInput",
    "ContractInput",
    "ContractSLAInput",
    "ContractRateInput",
    "KnowledgeBaseCollectionInput",
    "KnowledgeBaseArticleInput",
    "UserInput",
    "PaginatedResponse",
    "ClientsResponse",
    "TicketsResponse",
    "AssetsResponse",
    "ProjectsResponse",
    "TimeEntriesResponse",
    "TimersResponse",
    "ContactsResponse",
    "SitesResponse",
    "ContractsResponse",
    "ContractSLAsResponse",
    "ContractRatesResponse",
    "KnowledgeBaseCollectionsResponse",
    "KnowledgeBaseArticlesResponse",
    "UsersResponse",
    "WebhooksResponse",
    "WebhookDeliveriesResponse",
    "WebhookEventRecordsResponse",
    "serialize_input",
    "serialize_filter_value",
    "convert_datetime_to_iso",
    "convert_iso_to_datetime",
    # Fragments
    "BASE_FIELDS",
    "PAGINATION_INFO",
    "CLIENT_CORE_FIELDS",
    "CLIENT_FULL_FIELDS",
    "CLIENT_SUMMARY_FIELDS",
    "COMMENT_CORE_FIELDS",
    "COMMENT_FULL_FIELDS",
    "COMMENT_SUMMARY_FIELDS",
    "CONTACT_CORE_FIELDS",
    "CONTACT_FULL_FIELDS",
    "SITE_CORE_FIELDS",
    "SITE_FULL_FIELDS",
    "ASSET_CORE_FIELDS",
    "ASSET_FULL_FIELDS",
    "ASSET_SUMMARY_FIELDS",
    "TICKET_CORE_FIELDS",
    "TICKET_FULL_FIELDS",
    "TICKET_SUMMARY_FIELDS",
    "TICKET_COMMENT_FIELDS",
    "TIME_ENTRY_CORE_FIELDS",
    "TIME_ENTRY_FULL_FIELDS",
    "TIME_ENTRY_SUMMARY_FIELDS",
    "TIME_ENTRY_TEMPLATE_FIELDS",
    "TIMER_FIELDS",
    "KB_COLLECTION_CORE_FIELDS",
    "KB_COLLECTION_FULL_FIELDS",
    "KB_ARTICLE_CORE_FIELDS",
    "KB_ARTICLE_FULL_FIELDS",
    "KB_ARTICLE_SUMMARY_FIELDS",
    "PROJECT_CORE_FIELDS",
    "PROJECT_FULL_FIELDS",
    "PROJECT_SUMMARY_FIELDS",
    "PROJECT_MILESTONE_FIELDS",
    "PROJECT_TASK_CORE_FIELDS",
    "PROJECT_TASK_FULL_FIELDS",
    "PROJECT_TIME_ENTRY_FIELDS",
    "ALL_FRAGMENTS",
    "CLIENT_FRAGMENTS",
    "COMMENT_FRAGMENTS",
    "CONTACT_FRAGMENTS",
    "SITE_FRAGMENTS",
    "ASSET_FRAGMENTS",
    "TICKET_FRAGMENTS",
    "TIME_ENTRY_FRAGMENTS",
    "KB_FRAGMENTS",
    "PROJECT_FRAGMENTS",
    "CONTRACT_CORE_FIELDS",
    "CONTRACT_FULL_FIELDS",
    "CONTRACT_SUMMARY_FIELDS",
    "CONTRACT_SLA_FIELDS",
    "CONTRACT_RATE_FIELDS",
    "CONTRACT_FRAGMENTS",
    "USER_CORE_FIELDS",
    "USER_FULL_FIELDS",
    "USER_SUMMARY_FIELDS",
    "USER_FRAGMENTS",
    "WEBHOOK_CORE_FIELDS",
    "WEBHOOK_FULL_FIELDS",
    "WEBHOOK_SUMMARY_FIELDS",
    "WEBHOOK_DELIVERY_FIELDS",
    "WEBHOOK_EVENT_RECORD_FIELDS",
    "WEBHOOK_FRAGMENTS",
    "resolve_dependencies",
    "build_fragments_string",
    "get_fragment_spreads",
    "create_query_with_fragments",
    "get_client_fields",
    "get_comment_fields",
    "get_ticket_fields",
    "get_asset_fields",
    "get_time_entry_fields",
    "get_kb_fields",
    "get_contract_fields",
    "get_project_fields",
    "get_user_fields",
    "get_webhook_fields",
    # Builders
    "QueryBuilder",
    "SelectionQueryBuilder",
    "MutationBuilder",
    "ClientQueryBuilder",
    "CommentQueryBuilder",
    "CommentMutationBuilder",
    "TicketQueryBuilder",
    "AssetQueryBuilder",
    "ProjectQueryBuilder",
    "UserQueryBuilder",
    "ClientMutationBuilder",
    "TicketMutationBuilder",
    "ProjectMutationBuilder",
    "UserMutationBuilder",
    "TimeEntryQueryBuilder",
    "TimerQueryBuilder",
    "ClientMutationBuilder",
    "TicketMutationBuilder",
    "TimeEntryMutationBuilder",
    "TimerMutationBuilder",
    "create_client_query_builder",
    "create_comment_query_builder",
    "create_comment_mutation_builder",
    "create_ticket_query_builder",
    "create_asset_query_builder",
    "create_project_query_builder",
    "create_client_mutation_builder",
    "create_ticket_mutation_builder",
    "create_project_mutation_builder",
    "create_user_query_builder",
    "create_user_mutation_builder",
    "create_time_entry_query_builder",
    "create_timer_query_builder",
    "create_client_mutation_builder",
    "create_ticket_mutation_builder",
    "create_time_entry_mutation_builder",
    "create_timer_mutation_builder",
    # Queries
    "CommonQueries",
    "SuperOpsQueries",
]


# Convenience functions for easy access
def build_client_list_query(
    status: ClientStatus = None,
    name_search: str = None,
    page: int = 1,
    page_size: int = 50,
    detail_level: str = "core",
) -> tuple[str, dict]:
    """Build a client list query with common filters.

    Args:
        status: Client status filter
        name_search: Name search filter
        page: Page number
        page_size: Items per page
        detail_level: Level of detail (summary, core, full)

    Returns:
        Tuple of (query string, variables dict)
    """
    if name_search:
        return CommonQueries.search_clients_by_name(name_search, page, page_size, detail_level)
    elif status:
        builder = create_client_query_builder(detail_level)
        client_filter = ClientFilter(status=status)
        pagination = PaginationArgs(page=page, pageSize=page_size)

        query = builder.build_list(filter_obj=client_filter, pagination=pagination)
        variables = builder.get_variables()

        return query, variables
    else:
        return CommonQueries.list_all_clients(page, page_size, detail_level=detail_level)


def build_ticket_list_query(
    client_id: str = None,
    status: TicketStatus = None,
    priority: TicketPriority = None,
    assigned_to: str = None,
    page: int = 1,
    page_size: int = 50,
    detail_level: str = "core",
    include_comments: bool = False,
) -> tuple[str, dict]:
    """Build a ticket list query with common filters.

    Args:
        client_id: Client ID filter
        status: Ticket status filter
        priority: Ticket priority filter
        assigned_to: Assigned to filter
        page: Page number
        page_size: Items per page
        detail_level: Level of detail (summary, core, full)
        include_comments: Whether to include comments

    Returns:
        Tuple of (query string, variables dict)
    """
    builder = create_ticket_query_builder(detail_level, include_comments)

    # Build filter
    filter_kwargs = {}
    if client_id:
        filter_kwargs["client_id"] = client_id
    if status:
        filter_kwargs["status"] = status
    if priority:
        filter_kwargs["priority"] = priority
    if assigned_to:
        filter_kwargs["assigned_to"] = assigned_to

    ticket_filter = TicketFilter(**filter_kwargs) if filter_kwargs else None
    pagination = PaginationArgs(page=page, pageSize=page_size)
    sort_args = SortArgs(field="createdAt", direction="DESC")

    query = builder.build_list(filter_obj=ticket_filter, pagination=pagination, sort=sort_args)
    variables = builder.get_variables()

    return query, variables


def build_asset_list_query(
    client_id: str = None,
    asset_type: str = None,
    status: AssetStatus = None,
    page: int = 1,
    page_size: int = 50,
    detail_level: str = "core",
) -> tuple[str, dict]:
    """Build an asset list query with common filters.

    Args:
        client_id: Client ID filter
        asset_type: Asset type filter
        status: Asset status filter
        page: Page number
        page_size: Items per page
        detail_level: Level of detail (summary, core, full)

    Returns:
        Tuple of (query string, variables dict)
    """
    builder = create_asset_query_builder(detail_level)

    # Build filter
    filter_kwargs = {}
    if client_id:
        filter_kwargs["client_id"] = client_id
    if asset_type:
        filter_kwargs["asset_type"] = asset_type
    if status:
        filter_kwargs["status"] = status

    asset_filter = AssetFilter(**filter_kwargs) if filter_kwargs else None
    pagination = PaginationArgs(page=page, pageSize=page_size)
    sort_args = SortArgs(field="name", direction="ASC")

    query = builder.build_list(filter_obj=asset_filter, pagination=pagination, sort=sort_args)
    variables = builder.get_variables()

    return query, variables


def build_project_list_query(
    client_id: str = None,
    status: ProjectStatus = None,
    priority: ProjectPriority = None,
    assigned_to: str = None,
    page: int = 1,
    page_size: int = 50,
    detail_level: str = "core",
    include_milestones: bool = False,
    include_tasks: bool = False,
) -> tuple[str, dict]:
    """Build a project list query with common filters.

    Args:
        client_id: Client ID filter
        status: Project status filter
        priority: Project priority filter
        assigned_to: Assigned to filter
        page: Page number
        page_size: Items per page
        detail_level: Level of detail (summary, core, full)
        include_milestones: Whether to include milestones
        include_tasks: Whether to include tasks

    Returns:
        Tuple of (query string, variables dict)
    """
    builder = create_project_query_builder(detail_level, include_milestones, include_tasks)

    # Build filter
    filter_kwargs = {}
    if client_id:
        filter_kwargs["client_id"] = client_id
    if status:
        filter_kwargs["status"] = status
    if priority:
        filter_kwargs["priority"] = priority
    if assigned_to:
        filter_kwargs["assigned_to"] = assigned_to

    project_filter = ProjectFilter(**filter_kwargs) if filter_kwargs else None
    pagination = PaginationArgs(page=page, pageSize=page_size)
    sort_args = SortArgs(field="createdAt", direction="DESC")

    query = builder.build_list(filter_obj=project_filter, pagination=pagination, sort=sort_args)
    variables = builder.get_variables()

    return query, variables


def build_time_entry_list_query(
    user_id: str = None,
    ticket_id: str = None,
    project_id: str = None,
    client_id: str = None,
    status: "TimeEntryStatus" = None,
    entry_type: "TimeEntryType" = None,
    is_billable: bool = None,
    start_date: str = None,
    end_date: str = None,
    page: int = 1,
    page_size: int = 50,
    detail_level: str = "core",
) -> tuple[str, dict]:
    """Build a time entry list query with common filters.

    Args:
        user_id: User ID filter
        ticket_id: Ticket ID filter
        project_id: Project ID filter
        client_id: Client ID filter
        status: Time entry status filter
        entry_type: Time entry type filter
        is_billable: Billable filter
        start_date: Start date filter (ISO format)
        end_date: End date filter (ISO format)
        page: Page number
        page_size: Items per page
        detail_level: Level of detail (summary, core, full)

    Returns:
        Tuple of (query string, variables dict)
    """
    builder = create_time_entry_query_builder(detail_level)

    # Build filter
    filter_kwargs = {}
    if user_id:
        filter_kwargs["user_id"] = user_id
    if ticket_id:
        filter_kwargs["ticket_id"] = ticket_id
    if project_id:
        filter_kwargs["project_id"] = project_id
    if client_id:
        filter_kwargs["client_id"] = client_id
    if status:
        filter_kwargs["status"] = status
    if entry_type:
        filter_kwargs["entry_type"] = entry_type
    if is_billable is not None:
        filter_kwargs["is_billable"] = is_billable
    if start_date:
        filter_kwargs["start_date"] = start_date
    if end_date:
        filter_kwargs["end_date"] = end_date

    time_entry_filter = TimeEntryFilter(**filter_kwargs) if filter_kwargs else None
    pagination = PaginationArgs(page=page, pageSize=page_size)
    sort_args = SortArgs(field="startTime", direction="DESC")

    query = builder.build_list(filter_obj=time_entry_filter, pagination=pagination, sort=sort_args)
    variables = builder.get_variables()

    return query, variables


def build_contract_list_query(
    client_id: str = None,
    contract_type: ContractType = None,
    status: ContractStatus = None,
    page: int = 1,
    page_size: int = 50,
    detail_level: str = "core",
    include_slas: bool = False,
    include_rates: bool = False,
) -> tuple[str, dict]:
    """Build a contract list query with common filters.

    Args:
        client_id: Client ID filter
        contract_type: Contract type filter
        status: Contract status filter
        page: Page number
        page_size: Items per page
        detail_level: Level of detail (summary, core, full)
        include_slas: Whether to include SLA fields
        include_rates: Whether to include rate fields

    Returns:
        Tuple of (query string, variables dict)
    """
    from .builder import QueryBuilder
    from .fragments import get_contract_fields

    # Get contract fragments
    fragment_names = get_contract_fields(detail_level, include_slas, include_rates)

    # Build filter
    filter_kwargs = {}
    if client_id:
        filter_kwargs["client_id"] = client_id
    if contract_type:
        filter_kwargs["contract_type"] = contract_type
    if status:
        filter_kwargs["status"] = status

    contract_filter = ContractFilter(**filter_kwargs) if filter_kwargs else None
    pagination = PaginationArgs(page=page, pageSize=page_size)
    sort_args = SortArgs(field="createdAt", direction="DESC")

    # Build the query manually since we don't have ContractQueryBuilder yet
    fragments_string = ""
    if fragment_names:
        from .fragments import build_fragments_string

        fragments_string = build_fragments_string(fragment_names)

    # Get fragment spreads
    fragment_spreads = ""
    if fragment_names:
        from .fragments import get_fragment_spreads

        fragment_spreads = get_fragment_spreads(fragment_names)

    query = f"""
    query ListContracts($filter: ContractFilter, $pagination: PaginationArgs, $sort: SortArgs) {{
        contracts(filter: $filter, pagination: $pagination, sort: $sort) {{
            items {{
                {fragment_spreads}
            }}
            pagination {{
                ...PaginationInfo
            }}
        }}
    }}

    {fragments_string}
    """

    variables = {}
    if contract_filter:
        variables["filter"] = serialize_input(contract_filter)
    if pagination:
        variables["pagination"] = serialize_input(pagination)
    if sort_args:
        variables["sort"] = serialize_input(sort_args)

    return query.strip(), variables


def build_user_list_query(
    role: UserRole = None,
    status: UserStatus = None,
    department: str = None,
    page: int = 1,
    page_size: int = 50,
    detail_level: str = "core",
) -> tuple[str, dict]:
    """Build a user list query with common filters.

    Args:
        role: User role filter
        status: User status filter
        department: Department filter
        page: Page number
        page_size: Items per page
        detail_level: Level of detail (summary, core, full)

    Returns:
        Tuple of (query string, variables dict)
    """
    builder = create_user_query_builder(detail_level)

    # Build filter
    filter_kwargs = {}
    if role:
        filter_kwargs["role"] = role
    if status:
        filter_kwargs["status"] = status
    if department:
        filter_kwargs["department"] = department

    user_filter = UserFilter(**filter_kwargs) if filter_kwargs else None
    pagination = PaginationArgs(page=page, pageSize=page_size)
    sort_args = SortArgs(field="last_name", direction="ASC")

    query = builder.build_list(filter_obj=user_filter, pagination=pagination, sort=sort_args)
    if entry_type:
        filter_kwargs["entry_type"] = entry_type
    if is_billable is not None:
        filter_kwargs["is_billable"] = is_billable
    if start_date:
        filter_kwargs["start_date"] = start_date
    if end_date:
        filter_kwargs["end_date"] = end_date

    time_entry_filter = TimeEntryFilter(**filter_kwargs) if filter_kwargs else None
    pagination = PaginationArgs(page=page, pageSize=page_size)
    sort_args = SortArgs(field="startTime", direction="DESC")

    query = builder.build_list(filter_obj=time_entry_filter, pagination=pagination, sort=sort_args)
    variables = builder.get_variables()

    return query, variables


# Package information
def get_package_info():
    """Get GraphQL utilities package information."""
    return {
        "name": "py-superops.graphql",
        "version": __version__,
        "description": "GraphQL utilities for SuperOps API client",
        "components": [
            "Type-safe query builders",
            "GraphQL fragments and field selection",
            "Pre-built common queries",
            "Response parsing and validation",
            "Pagination and filtering support",
            "Mutation builders for CRUD operations",
        ],
        "supported_resources": [
            "Clients/Customers",
            "Contacts",
            "Sites",
            "Assets",
            "Tickets",
            "Projects",
            "Time Entries",
            "Timers",
            "Knowledge Base Collections",
            "Knowledge Base Articles",
        ],
    }
