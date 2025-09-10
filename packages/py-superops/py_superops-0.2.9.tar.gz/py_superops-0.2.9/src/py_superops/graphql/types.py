# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""GraphQL type definitions and response models for SuperOps API.

This module provides type-safe models for GraphQL queries, mutations, and responses,
enabling better IDE support and runtime validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict


# Base Types
class GraphQLResponse(TypedDict, total=False):
    """Base GraphQL response structure."""

    data: Optional[Dict[str, Any]]
    errors: Optional[List[Dict[str, Any]]]
    extensions: Optional[Dict[str, Any]]


class PaginationInfo(TypedDict):
    """Pagination information for GraphQL queries."""

    page: int
    pageSize: int
    total: int
    hasNextPage: bool
    hasPreviousPage: bool


# Enums
class TicketStatus(str, Enum):
    """Ticket status enumeration."""

    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class TicketPriority(str, Enum):
    """Ticket priority enumeration."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"
    CRITICAL = "CRITICAL"


class AssetStatus(str, Enum):
    """Asset status enumeration."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    RETIRED = "RETIRED"
    UNDER_MAINTENANCE = "UNDER_MAINTENANCE"


class ClientStatus(str, Enum):
    """Client status enumeration."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class ProjectStatus(str, Enum):
    """Project status enumeration."""

    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ON_HOLD = "ON_HOLD"


class TaskStatus(str, Enum):
    """Task status enumeration."""

    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ON_HOLD = "ON_HOLD"
    UNDER_REVIEW = "UNDER_REVIEW"


class ProjectPriority(str, Enum):
    """Project priority enumeration."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"
    CRITICAL = "CRITICAL"


class TaskPriority(str, Enum):
    """Task priority enumeration."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"
    CRITICAL = "CRITICAL"


class TaskRecurrenceType(str, Enum):
    """Task recurrence type enumeration."""

    NONE = "NONE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class CommentType(str, Enum):
    """Comment type enumeration."""

    GENERAL = "GENERAL"
    INTERNAL = "INTERNAL"
    TIME_LOG = "TIME_LOG"
    STATUS_CHANGE = "STATUS_CHANGE"
    SYSTEM = "SYSTEM"


class ContractStatus(str, Enum):
    """Contract status enumeration."""

    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    SUSPENDED = "SUSPENDED"
    RENEWAL_PENDING = "RENEWAL_PENDING"


class ContractType(str, Enum):
    """Contract type enumeration."""

    SERVICE_AGREEMENT = "SERVICE_AGREEMENT"
    MAINTENANCE_CONTRACT = "MAINTENANCE_CONTRACT"
    PROJECT_BASED = "PROJECT_BASED"
    SUPPORT_CONTRACT = "SUPPORT_CONTRACT"
    MSP_CONTRACT = "MSP_CONTRACT"


class BillingCycle(str, Enum):
    """Billing cycle enumeration."""

    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    SEMI_ANNUAL = "SEMI_ANNUAL"
    ANNUAL = "ANNUAL"
    ONE_TIME = "ONE_TIME"


class SLALevel(str, Enum):
    """SLA level enumeration."""

    BASIC = "BASIC"
    STANDARD = "STANDARD"
    PREMIUM = "PREMIUM"
    ENTERPRISE = "ENTERPRISE"
    CUSTOM = "CUSTOM"


class AttachmentType(str, Enum):
    """Attachment type enumeration."""

    DOCUMENT = "DOCUMENT"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    ARCHIVE = "ARCHIVE"
    SPREADSHEET = "SPREADSHEET"
    PRESENTATION = "PRESENTATION"
    CODE = "CODE"
    OTHER = "OTHER"


class EntityType(str, Enum):
    """Entity type enumeration for attachments and comments."""

    TICKET = "TICKET"
    TASK = "TASK"
    PROJECT = "PROJECT"
    CLIENT = "CLIENT"
    ASSET = "ASSET"
    CONTRACT = "CONTRACT"
    SITE = "SITE"
    CONTACT = "CONTACT"
    KB_ARTICLE = "KB_ARTICLE"
    KB_COLLECTION = "KB_COLLECTION"


class UserRole(str, Enum):
    """User role enumeration."""

    ADMIN = "ADMIN"
    TECHNICIAN = "TECHNICIAN"
    USER = "USER"
    MANAGER = "MANAGER"
    READONLY = "READONLY"
    BILLING = "BILLING"
    DISPATCHER = "DISPATCHER"


class UserStatus(str, Enum):
    """User status enumeration."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING = "PENDING"


class WebhookEvent(str, Enum):
    """Webhook event type enumeration."""

    TICKET_CREATED = "TICKET_CREATED"
    TICKET_UPDATED = "TICKET_UPDATED"
    TICKET_DELETED = "TICKET_DELETED"
    TICKET_ASSIGNED = "TICKET_ASSIGNED"
    TICKET_STATUS_CHANGED = "TICKET_STATUS_CHANGED"
    TICKET_COMMENT_ADDED = "TICKET_COMMENT_ADDED"

    CLIENT_CREATED = "CLIENT_CREATED"
    CLIENT_UPDATED = "CLIENT_UPDATED"
    CLIENT_DELETED = "CLIENT_DELETED"
    CLIENT_STATUS_CHANGED = "CLIENT_STATUS_CHANGED"

    ASSET_CREATED = "ASSET_CREATED"
    ASSET_UPDATED = "ASSET_UPDATED"
    ASSET_DELETED = "ASSET_DELETED"
    ASSET_STATUS_CHANGED = "ASSET_STATUS_CHANGED"

    PROJECT_CREATED = "PROJECT_CREATED"
    PROJECT_UPDATED = "PROJECT_UPDATED"
    PROJECT_DELETED = "PROJECT_DELETED"
    PROJECT_STATUS_CHANGED = "PROJECT_STATUS_CHANGED"

    TASK_CREATED = "TASK_CREATED"
    TASK_UPDATED = "TASK_UPDATED"
    TASK_DELETED = "TASK_DELETED"
    TASK_ASSIGNED = "TASK_ASSIGNED"
    TASK_STATUS_CHANGED = "TASK_STATUS_CHANGED"
    TASK_COMPLETED = "TASK_COMPLETED"

    CONTRACT_CREATED = "CONTRACT_CREATED"
    CONTRACT_UPDATED = "CONTRACT_UPDATED"
    CONTRACT_DELETED = "CONTRACT_DELETED"
    CONTRACT_STATUS_CHANGED = "CONTRACT_STATUS_CHANGED"
    CONTRACT_EXPIRING = "CONTRACT_EXPIRING"

    CONTACT_CREATED = "CONTACT_CREATED"
    CONTACT_UPDATED = "CONTACT_UPDATED"
    CONTACT_DELETED = "CONTACT_DELETED"

    SITE_CREATED = "SITE_CREATED"
    SITE_UPDATED = "SITE_UPDATED"
    SITE_DELETED = "SITE_DELETED"


class WebhookStatus(str, Enum):
    """Webhook status enumeration."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DISABLED = "DISABLED"
    ERROR = "ERROR"


class WebhookDeliveryStatus(str, Enum):
    """Webhook delivery status enumeration."""

    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    CANCELLED = "CANCELLED"


class TimeEntryStatus(str, Enum):
    """Time entry status enumeration."""

    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    BILLED = "BILLED"


class TimeEntryType(str, Enum):
    """Time entry type enumeration."""

    WORK = "WORK"
    BREAK = "BREAK"
    MEETING = "MEETING"
    TRAVEL = "TRAVEL"
    TRAINING = "TRAINING"
    MAINTENANCE = "MAINTENANCE"
    SUPPORT = "SUPPORT"


class TimerState(str, Enum):
    """Timer state enumeration."""

    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"


class AutomationTriggerType(str, Enum):
    """Automation trigger type enumeration."""

    SCHEDULED = "SCHEDULED"
    EVENT_BASED = "EVENT_BASED"
    WEBHOOK = "WEBHOOK"
    MANUAL = "MANUAL"
    CONDITION_BASED = "CONDITION_BASED"


class AutomationJobStatus(str, Enum):
    """Automation job status enumeration."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    SKIPPED = "SKIPPED"
    RETRYING = "RETRYING"


class AutomationWorkflowStatus(str, Enum):
    """Automation workflow status enumeration."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DRAFT = "DRAFT"
    ARCHIVED = "ARCHIVED"


class ScheduleType(str, Enum):
    """Schedule type enumeration."""

    ONCE = "ONCE"
    RECURRING = "RECURRING"
    CRON = "CRON"
    INTERVAL = "INTERVAL"


class RecurrenceFrequency(str, Enum):
    """Recurrence frequency enumeration."""

    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"
    HOURLY = "HOURLY"


class ActionType(str, Enum):
    """Automation action type enumeration."""

    SEND_EMAIL = "SEND_EMAIL"
    CREATE_TICKET = "CREATE_TICKET"
    UPDATE_TICKET = "UPDATE_TICKET"
    ASSIGN_TICKET = "ASSIGN_TICKET"
    CLOSE_TICKET = "CLOSE_TICKET"
    SEND_NOTIFICATION = "SEND_NOTIFICATION"
    CREATE_TASK = "CREATE_TASK"
    UPDATE_ASSET = "UPDATE_ASSET"
    RUN_SCRIPT = "RUN_SCRIPT"
    WEBHOOK_CALL = "WEBHOOK_CALL"
    CONDITION_CHECK = "CONDITION_CHECK"
    DELAY = "DELAY"
    CUSTOM_ACTION = "CUSTOM_ACTION"


# Base Models
@dataclass
class BaseModel:
    """Base model with common fields."""

    id: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseModel:
        """Create instance from dictionary with field name conversion."""
        # Convert camelCase to snake_case for common fields
        field_mapping = {
            "clientId": "client_id",
            "contractId": "contract_id",
            "contractNumber": "contract_number",
            "contractType": "contract_type",
            "startDate": "start_date",
            "endDate": "end_date",
            "renewalDate": "renewal_date",
            "autoRenew": "auto_renew",
            "billingCycle": "billing_cycle",
            "contractValue": "contract_value",
            "termsAndConditions": "terms_and_conditions",
            "renewalTerms": "renewal_terms",
            "cancellationTerms": "cancellation_terms",
            "signedByClient": "signed_by_client",
            "signedByProvider": "signed_by_provider",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
            "userId": "user_id",
            "userName": "user_name",
            "firstName": "first_name",
            "lastName": "last_name",
            "jobTitle": "job_title",
            "isTechnician": "is_technician",
            "hourlyRate": "hourly_rate",
            "lastLoginTime": "last_login_time",
            "avatarUrl": "avatar_url",
            "isPrimary": "is_primary",
            "notificationPreferences": "notification_preferences",
            "customFields": "custom_fields",
            "ticketId": "ticket_id",
            "projectId": "project_id",
            "taskId": "task_id",
            "assetId": "asset_id",
            "siteId": "site_id",
            "contactId": "contact_id",
            "entityType": "entity_type",
            "entityId": "entity_id",
            "attachmentType": "attachment_type",
            "mimeType": "mime_type",
            "fileSize": "file_size",
            "originalFilename": "original_filename",
            "uploadedBy": "uploaded_by",
            "uploadedByName": "uploaded_by_name",
            "downloadUrl": "download_url",
            "isPublic": "is_public",
            "parentCommentId": "parent_comment_id",
            "commentType": "comment_type",
            "isInternal": "is_internal",
            "timeLogged": "time_logged",
            "replyCount": "reply_count",
            "authorName": "author_name",
            "hasAttachments": "has_attachments",
            "milestoneId": "milestone_id",
            "assignedTo": "assigned_to",
            "startTime": "start_time",
            "endTime": "end_time",
            "completionDate": "completion_date",
            "billableHours": "billable_hours",
            "isBillable": "is_billable",
            "orderIndex": "order_index",
            "signedDate": "signed_date",
            "dueDate": "due_date",
            "progressPercentage": "progress_percentage",
            "estimatedHours": "estimated_hours",
            "actualHours": "actual_hours",
            "billingRate": "billing_rate",
            "managerId": "manager_id",
            "authorId": "author_id",
            "isCompleted": "is_completed",
            "isDeleted": "is_deleted",
            "isActive": "is_active",
            "isArchived": "is_archived",
            "timeSpent": "time_spent",
            "parentId": "parent_id",
            "rootId": "root_id",
            "level": "level",
            "hasChildren": "has_children",
            "publishedAt": "published_at",
            "isPublished": "is_published",
            "viewCount": "view_count",
            "likeCount": "like_count",
            "lastViewed": "last_viewed",
            "isPinned": "is_pinned",
            "expiryDate": "expiry_date",
            "warrantyExpiry": "warranty_expiry",
            "purchaseDate": "purchase_date",
            "serialNumber": "serial_number",
            "modelNumber": "model_number",
            "operatingSystem": "operating_system",
            "ipAddress": "ip_address",
            "macAddress": "mac_address",
            "isOnline": "is_online",
            "lastSeen": "last_seen",
            "billingAddress": "billing_address",
            "phoneNumber": "phone_number",
            "companyName": "company_name",
            "notificationDays": "notification_days",
        }

        # Convert field names
        converted_data = {}
        for key, value in data.items():
            converted_key = field_mapping.get(key, key)
            converted_data[converted_key] = value

        return cls(**converted_data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to dictionary."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, Enum):
                result[key] = value.value
            else:
                result[key] = value
        return result


# Comment Types
@dataclass
class Comment(BaseModel):
    """Generic comment model."""

    entity_type: str  # "ticket", "task", "project", etc.
    entity_id: str
    author_id: str
    author_name: str
    content: str
    comment_type: CommentType = CommentType.GENERAL
    is_internal: bool = False
    time_logged: Optional[float] = None  # hours logged with this comment
    parent_comment_id: Optional[str] = None  # for threaded comments
    reply_count: int = 0
    attachments: List[str] = field(default_factory=list)  # attachment IDs


@dataclass
class CommentAttachment(BaseModel):
    """Comment attachment model."""

    comment_id: str
    filename: str
    file_url: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None


# Client Types
@dataclass
class Client(BaseModel):
    """Client/Customer model."""

    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    status: ClientStatus = ClientStatus.ACTIVE
    billing_address: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Contact(BaseModel):
    """Contact model."""

    client_id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    title: Optional[str] = None
    is_primary: bool = False
    notes: Optional[str] = None


@dataclass
class Site(BaseModel):
    """Site model."""

    client_id: str
    name: str
    address: Optional[str] = None
    description: Optional[str] = None
    timezone: Optional[str] = None
    notes: Optional[str] = None


# Asset Types
@dataclass
class Asset(BaseModel):
    """Asset model."""

    client_id: str
    name: str
    site_id: Optional[str] = None
    asset_type: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    status: AssetStatus = AssetStatus.ACTIVE
    purchase_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    custom_fields: Dict[str, Any] = field(default_factory=dict)


# Ticket Types
@dataclass
class Ticket(BaseModel):
    """Ticket model."""

    client_id: str
    title: str
    site_id: Optional[str] = None
    asset_id: Optional[str] = None
    contact_id: Optional[str] = None
    description: Optional[str] = None
    status: TicketStatus = TicketStatus.OPEN
    priority: TicketPriority = TicketPriority.NORMAL
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    resolution: Optional[str] = None
    time_spent: Optional[int] = None  # minutes
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TicketComment(BaseModel):
    """Ticket comment model."""

    ticket_id: str
    author_id: str
    author_name: str
    content: str
    is_internal: bool = False
    time_spent: Optional[int] = None  # minutes


# Project Types
@dataclass
class Project(BaseModel):
    """Project model."""

    client_id: str
    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.OPEN
    priority: ProjectPriority = ProjectPriority.NORMAL
    contract_id: Optional[str] = None
    site_id: Optional[str] = None
    assigned_to: Optional[str] = None
    manager_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    budget: Optional[float] = None
    billing_rate: Optional[float] = None
    progress_percentage: Optional[int] = None  # 0-100
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None
    notes: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectMilestone(BaseModel):
    """Project milestone model."""

    project_id: str
    name: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    is_completed: bool = False
    progress_percentage: Optional[int] = None  # 0-100
    order_index: int = 0
    notes: Optional[str] = None


@dataclass
class ProjectTask(BaseModel):
    """Project task model."""

    # Required fields first
    project_id: str
    name: str

    # Optional fields with defaults
    milestone_id: Optional[str] = None
    description: Optional[str] = None
    status: TicketStatus = TicketStatus.OPEN
    priority: TicketPriority = TicketPriority.NORMAL
    assigned_to: Optional[str] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None
    progress_percentage: Optional[int] = None  # 0-100
    order_index: int = 0
    notes: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class ProjectTimeEntry(BaseModel):
    """Project time entry model."""

    # Required fields first
    project_id: str
    user_id: str
    user_name: str
    description: str
    hours: float
    start_time: datetime

    # Optional fields with defaults
    task_id: Optional[str] = None
    billable_hours: Optional[float] = None
    rate: Optional[float] = None
    end_time: Optional[datetime] = None
    is_billable: bool = True
    notes: Optional[str] = None


# User Types
@dataclass
class User(BaseModel):
    """User model."""

    # Required fields first (from BaseModel and User-specific)
    email: str
    first_name: str
    last_name: str
    role: UserRole

    # Optional fields with defaults
    status: UserStatus = UserStatus.ACTIVE
    department: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    job_title: Optional[str] = None
    is_technician: bool = False
    hourly_rate: Optional[float] = None
    last_login_time: Optional[datetime] = None
    last_login: Optional[str] = None  # Alternative field name for compatibility
    timezone: Optional[str] = None
    language: Optional[str] = None
    avatar_url: Optional[str] = None
    is_primary: bool = False
    is_active_session: bool = False
    employee_id: Optional[str] = None
    hire_date: Optional[str] = None
    manager_id: Optional[str] = None
    notification_preferences: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)

    @property
    def full_name(self) -> str:
        """Get full name."""
        return f"{self.first_name} {self.last_name}".strip()


# Knowledge Base Types
@dataclass
class KnowledgeBaseCollection(BaseModel):
    """Knowledge base collection model."""

    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    is_public: bool = False
    article_count: int = 0


@dataclass
class KnowledgeBaseArticle(BaseModel):
    """Knowledge base article model."""

    collection_id: str
    title: str
    content: str
    author_id: str
    author_name: str
    summary: Optional[str] = None
    is_published: bool = False
    is_featured: bool = False
    view_count: int = 0
    tags: List[str] = field(default_factory=list)


# Task Types
@dataclass
class Task(BaseModel):
    """Task model."""

    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.NEW
    priority: TaskPriority = TaskPriority.NORMAL

    # Project linking - tasks can be standalone or linked to projects
    project_id: Optional[str] = None

    # Assignment and delegation
    assigned_to: Optional[str] = None
    assigned_to_team: Optional[str] = None
    creator_id: Optional[str] = None

    # Hierarchy support
    parent_task_id: Optional[str] = None
    subtask_count: int = 0

    # Due dates and scheduling
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None

    # Recurring task support
    recurrence_type: TaskRecurrenceType = TaskRecurrenceType.NONE
    recurrence_interval: Optional[int] = None  # e.g., every 2 weeks
    recurrence_end_date: Optional[datetime] = None
    parent_recurring_task_id: Optional[str] = None

    # Time tracking
    time_entries_count: int = 0
    total_time_logged: Optional[float] = None  # hours
    billable_time: Optional[float] = None  # hours

    # Categorization and metadata
    labels: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)

    # Additional metadata
    progress_percentage: Optional[int] = None  # 0-100
    is_milestone: bool = False
    is_template: bool = False
    template_id: Optional[str] = None

    # Attachments and links
    attachment_count: int = 0
    comment_count: int = 0

    # Alert settings
    overdue_alert_sent: bool = False
    reminder_sent: bool = False


@dataclass
class TaskComment(BaseModel):
    """Task comment model."""

    task_id: str
    author_id: str
    author_name: str
    content: str
    is_internal: bool = False
    time_logged: Optional[float] = None  # hours logged with this comment


@dataclass
class TaskTimeEntry(BaseModel):
    """Task time entry model."""

    task_id: str
    user_id: str
    user_name: str
    hours: float
    date_logged: datetime
    description: Optional[str] = None
    is_billable: bool = True
    hourly_rate: Optional[float] = None


# Attachment Types
@dataclass
class Attachment(BaseModel):
    """Attachment model."""

    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    entity_type: EntityType
    entity_id: str
    attachment_type: Optional[AttachmentType] = None
    description: Optional[str] = None
    url: Optional[str] = None
    download_url: Optional[str] = None
    version: int = 1
    uploaded_by: Optional[str] = None
    uploaded_by_name: Optional[str] = None
    is_public: bool = False
    checksum: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskTemplate(BaseModel):
    """Task template model."""

    name: str
    description: Optional[str] = None
    default_priority: TaskPriority = TaskPriority.NORMAL
    estimated_hours: Optional[float] = None
    default_assignee_id: Optional[str] = None
    default_tags: List[str] = field(default_factory=list)
    default_custom_fields: Dict[str, Any] = field(default_factory=dict)
    checklist_items: List[str] = field(default_factory=list)


# Contract Types
@dataclass
class ContractSLA(BaseModel):
    """Contract SLA model."""

    contract_id: str
    level: SLALevel
    response_time_minutes: Optional[int] = None
    resolution_time_hours: Optional[int] = None
    availability_percentage: Optional[float] = None
    description: Optional[str] = None
    penalties: Optional[str] = None


@dataclass
class ContractRate(BaseModel):
    """Contract billing rate model."""

    contract_id: str
    service_type: str
    rate_type: str  # HOURLY, FIXED, TIERED
    rate_amount: float
    currency: str = "USD"
    description: Optional[str] = None
    effective_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@dataclass
class Contract(BaseModel):
    """Contract model."""

    client_id: str
    name: str
    contract_number: str
    contract_type: ContractType
    start_date: datetime
    status: ContractStatus = ContractStatus.DRAFT
    end_date: Optional[datetime] = None
    renewal_date: Optional[datetime] = None
    auto_renew: bool = False
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    contract_value: Optional[float] = None
    currency: str = "USD"
    description: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    renewal_terms: Optional[str] = None
    cancellation_terms: Optional[str] = None
    signed_by_client: Optional[str] = None
    signed_by_provider: Optional[str] = None
    signed_date: Optional[datetime] = None
    notification_days: int = 30
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    # Related data
    slas: List[ContractSLA] = field(default_factory=list)
    rates: List[ContractRate] = field(default_factory=list)


# Webhook Types
@dataclass
class Webhook(BaseModel):
    """Webhook model."""

    name: str
    url: str
    events: List[WebhookEvent]
    status: WebhookStatus = WebhookStatus.ACTIVE
    secret: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    retry_count: int = 3
    timeout_seconds: int = 30
    headers: Dict[str, str] = field(default_factory=dict)
    last_triggered: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    failure_count: int = 0
    success_count: int = 0
    total_deliveries: int = 0
    content_type: str = "application/json"


# Time Entry Types
@dataclass
class TimeEntry(BaseModel):
    """Time entry model."""

    user_id: str
    description: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None  # calculated field
    ticket_id: Optional[str] = None
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    client_id: Optional[str] = None
    status: TimeEntryStatus = TimeEntryStatus.DRAFT
    entry_type: TimeEntryType = TimeEntryType.WORK
    is_billable: bool = True
    hourly_rate: Optional[float] = None
    total_amount: Optional[float] = None  # calculated field
    work_category: Optional[str] = None
    notes: Optional[str] = None
    approval_notes: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Timer(BaseModel):
    """Timer model for active time tracking."""

    # Required fields first
    user_id: str
    description: str
    start_time: datetime

    # Optional fields with defaults
    time_entry_id: Optional[str] = None
    paused_time: Optional[datetime] = None
    total_paused_duration: int = 0  # minutes
    current_duration: Optional[int] = None  # calculated field in minutes
    state: TimerState = TimerState.STOPPED
    ticket_id: Optional[str] = None
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    client_id: Optional[str] = None
    is_billable: bool = True
    entry_type: TimeEntryType = TimeEntryType.WORK
    work_category: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class WebhookDelivery(BaseModel):
    """Webhook delivery model."""

    webhook_id: str
    event_type: WebhookEvent
    status: WebhookDeliveryStatus
    url: str
    payload: Dict[str, Any]
    response_status_code: Optional[int] = None
    response_body: Optional[str] = None
    response_headers: Dict[str, str] = field(default_factory=dict)
    attempt_count: int = 1
    next_retry_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None
    request_headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class WebhookEventRecord(BaseModel):
    """Webhook event record model for event history."""

    webhook_id: str
    event_type: WebhookEvent
    resource_type: str
    resource_id: str
    payload: Dict[str, Any]
    triggered_at: datetime
    delivery_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TimeEntryTemplate(BaseModel):
    """Time entry template for common work types."""

    name: str
    description: str
    user_id: str
    default_duration_minutes: Optional[int] = None
    entry_type: TimeEntryType = TimeEntryType.WORK
    is_billable: bool = True
    work_category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True


# Query Filter Types
@dataclass
class ClientFilter:
    """Client query filter."""

    name: Optional[str] = None
    email: Optional[str] = None
    status: Optional[ClientStatus] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


@dataclass
class TicketFilter:
    """Ticket query filter."""

    client_id: Optional[str] = None
    site_id: Optional[str] = None
    asset_id: Optional[str] = None
    contact_id: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_to: Optional[str] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    due_after: Optional[datetime] = None
    due_before: Optional[datetime] = None


@dataclass
class AssetFilter:
    """Asset query filter."""

    client_id: Optional[str] = None
    site_id: Optional[str] = None
    name: Optional[str] = None
    asset_type: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    status: Optional[AssetStatus] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


@dataclass
class ProjectFilter:
    """Project query filter."""

    client_id: Optional[str] = None
    contract_id: Optional[str] = None
    site_id: Optional[str] = None
    name: Optional[str] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    assigned_to: Optional[str] = None
    manager_id: Optional[str] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    start_after: Optional[datetime] = None
    start_before: Optional[datetime] = None
    due_after: Optional[datetime] = None
    due_before: Optional[datetime] = None


@dataclass
class TaskFilter:
    """Task query filter."""

    # Basic filtering
    title: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None

    # Project and hierarchy
    project_id: Optional[str] = None
    parent_task_id: Optional[str] = None
    is_subtask: Optional[bool] = None  # has parent_task_id
    is_parent: Optional[bool] = None  # has subtasks

    # Assignment
    assigned_to: Optional[str] = None
    assigned_to_team: Optional[str] = None
    creator_id: Optional[str] = None
    unassigned: Optional[bool] = None

    # Date filtering
    due_after: Optional[datetime] = None
    due_before: Optional[datetime] = None
    start_after: Optional[datetime] = None
    start_before: Optional[datetime] = None
    completed_after: Optional[datetime] = None
    completed_before: Optional[datetime] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None

    # Status filtering
    is_overdue: Optional[bool] = None
    is_completed: Optional[bool] = None
    is_active: Optional[bool] = None  # not completed or cancelled

    # Recurring tasks
    recurrence_type: Optional[TaskRecurrenceType] = None
    is_recurring: Optional[bool] = None
    is_recurring_instance: Optional[bool] = None

    # Metadata
    tags: Optional[List[str]] = None
    labels: Optional[List[str]] = None
    is_milestone: Optional[bool] = None
    is_template: Optional[bool] = None
    template_id: Optional[str] = None

    # Time tracking
    has_time_entries: Optional[bool] = None
    estimated_hours_min: Optional[float] = None
    estimated_hours_max: Optional[float] = None
    actual_hours_min: Optional[float] = None
    actual_hours_max: Optional[float] = None


@dataclass
class UserFilter:
    """User query filter."""

    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    department: Optional[str] = None
    job_title: Optional[str] = None
    is_technician: Optional[bool] = None
    is_primary: Optional[bool] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    last_login_after: Optional[datetime] = None
    last_login_before: Optional[datetime] = None


@dataclass
class ContractFilter:
    """Contract query filter."""

    client_id: Optional[str] = None
    name: Optional[str] = None
    contract_number: Optional[str] = None
    contract_type: Optional[ContractType] = None
    status: Optional[ContractStatus] = None
    billing_cycle: Optional[BillingCycle] = None
    auto_renew: Optional[bool] = None
    start_date_after: Optional[datetime] = None
    start_date_before: Optional[datetime] = None
    end_date_after: Optional[datetime] = None
    end_date_before: Optional[datetime] = None
    renewal_date_after: Optional[datetime] = None
    renewal_date_before: Optional[datetime] = None
    value_min: Optional[float] = None
    value_max: Optional[float] = None
    tags: Optional[List[str]] = None


@dataclass
class TimeEntryFilter:
    """Time entry query filter."""

    user_id: Optional[str] = None
    ticket_id: Optional[str] = None
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    client_id: Optional[str] = None
    status: Optional[TimeEntryStatus] = None
    entry_type: Optional[TimeEntryType] = None
    is_billable: Optional[bool] = None
    work_category: Optional[str] = None
    tags: Optional[List[str]] = None
    start_time_after: Optional[datetime] = None
    start_time_before: Optional[datetime] = None
    end_time_after: Optional[datetime] = None
    end_time_before: Optional[datetime] = None
    min_duration_minutes: Optional[int] = None
    max_duration_minutes: Optional[int] = None
    approved_by: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


@dataclass
class CommentFilter:
    """Comment query filter."""

    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    author_id: Optional[str] = None
    comment_type: Optional[CommentType] = None
    is_internal: Optional[bool] = None
    has_time_logged: Optional[bool] = None
    parent_comment_id: Optional[str] = None
    is_reply: Optional[bool] = None  # has parent_comment_id
    has_replies: Optional[bool] = None  # reply_count > 0
    has_attachments: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    content_contains: Optional[str] = None


@dataclass
class AttachmentFilter:
    """Attachment query filter."""

    filename: Optional[str] = None
    mime_type: Optional[str] = None
    attachment_type: Optional[AttachmentType] = None
    entity_type: Optional[EntityType] = None
    entity_id: Optional[str] = None
    uploaded_by: Optional[str] = None
    is_public: Optional[bool] = None
    file_size_min: Optional[int] = None
    file_size_max: Optional[int] = None
    version: Optional[int] = None


@dataclass
class TimerFilter:
    """Timer query filter."""

    user_id: Optional[str] = None
    state: Optional[TimerState] = None
    ticket_id: Optional[str] = None
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    client_id: Optional[str] = None
    is_billable: Optional[bool] = None
    entry_type: Optional[TimeEntryType] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


@dataclass
class WebhookFilter:
    """Webhook query filter."""

    name: Optional[str] = None
    url: Optional[str] = None
    status: Optional[WebhookStatus] = None
    events: Optional[List[WebhookEvent]] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    last_triggered_after: Optional[datetime] = None
    last_triggered_before: Optional[datetime] = None


@dataclass
class WebhookDeliveryFilter:
    """Webhook delivery query filter."""

    webhook_id: Optional[str] = None
    event_type: Optional[WebhookEvent] = None
    status: Optional[WebhookDeliveryStatus] = None
    response_status_code: Optional[int] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    delivered_after: Optional[datetime] = None
    delivered_before: Optional[datetime] = None


# Pagination Types
@dataclass
class PaginationArgs:
    """Pagination arguments."""

    page: int = 1
    pageSize: int = 50

    def __post_init__(self) -> None:
        """Validate pagination arguments."""
        if self.page < 1:
            raise ValueError("Page must be >= 1")
        if self.pageSize < 1 or self.pageSize > 1000:
            raise ValueError("Page size must be between 1 and 1000")


@dataclass
class SortArgs:
    """Sort arguments."""

    field: str
    direction: str = "ASC"  # ASC or DESC

    def __post_init__(self) -> None:
        """Validate sort arguments."""
        if self.direction not in ("ASC", "DESC"):
            raise ValueError("Direction must be ASC or DESC")


# Response Types
@dataclass
class PaginatedResponse:
    """Base paginated response."""

    items: List[Any]
    pagination: PaginationInfo

    @classmethod
    def from_graphql_response(
        cls, data: Dict[str, Any], item_type: type, items_key: str = "items"
    ) -> PaginatedResponse:
        """Create paginated response from GraphQL data."""
        items_data = data.get(items_key, [])
        items = [
            item_type.from_dict(item) if hasattr(item_type, "from_dict") else item
            for item in items_data
        ]

        pagination = data.get("pagination", {})

        return cls(items=items, pagination=pagination)


@dataclass
class ClientsResponse(PaginatedResponse):
    """Clients query response."""

    items: List[Client]


@dataclass
class TicketsResponse(PaginatedResponse):
    """Tickets query response."""

    items: List[Ticket]


@dataclass
class AssetsResponse(PaginatedResponse):
    """Assets query response."""

    items: List[Asset]


@dataclass
class ContactsResponse(PaginatedResponse):
    """Contacts query response."""

    items: List[Contact]


@dataclass
class SitesResponse(PaginatedResponse):
    """Sites query response."""

    items: List[Site]


@dataclass
class KnowledgeBaseCollectionsResponse(PaginatedResponse):
    """Knowledge base collections query response."""

    items: List[KnowledgeBaseCollection]


@dataclass
class KnowledgeBaseArticlesResponse(PaginatedResponse):
    """Knowledge base articles query response."""

    items: List[KnowledgeBaseArticle]


@dataclass
class ProjectsResponse(PaginatedResponse):
    """Projects query response."""

    items: List[Project]


@dataclass
class ProjectMilestonesResponse(PaginatedResponse):
    """Project milestones query response."""

    items: List[ProjectMilestone]


@dataclass
class ProjectTasksResponse(PaginatedResponse):
    """Project tasks query response."""

    items: List[ProjectTask]


@dataclass
class ProjectTimeEntriesResponse(PaginatedResponse):
    """Project time entries query response."""

    items: List[ProjectTimeEntry]


@dataclass
class TasksResponse(PaginatedResponse):
    """Tasks query response."""

    items: List[Task]


@dataclass
class TaskCommentsResponse(PaginatedResponse):
    """Task comments query response."""

    items: List[TaskComment]


@dataclass
class TaskTimeEntriesResponse(PaginatedResponse):
    """Task time entries query response."""

    items: List[TaskTimeEntry]


@dataclass
class TaskTemplatesResponse(PaginatedResponse):
    """Task templates query response."""

    items: List[TaskTemplate]


@dataclass
class ContractsResponse(PaginatedResponse):
    """Contracts query response."""

    items: List[Contract]


@dataclass
class ContractSLAsResponse(PaginatedResponse):
    """Contract SLAs query response."""

    items: List[ContractSLA]


@dataclass
class ContractRatesResponse(PaginatedResponse):
    """Contract rates query response."""

    items: List[ContractRate]


@dataclass
class CommentsResponse(PaginatedResponse):
    """Comments query response."""

    items: List[Comment]


@dataclass
class CommentAttachmentsResponse(PaginatedResponse):
    """Comment attachments query response."""

    items: List[CommentAttachment]


@dataclass
class AttachmentsResponse(PaginatedResponse):
    """Attachments query response."""

    items: List[Attachment]


@dataclass
class WebhooksResponse(PaginatedResponse):
    """Webhooks query response."""

    items: List[Webhook]


@dataclass
class WebhookDeliveriesResponse(PaginatedResponse):
    """Webhook deliveries query response."""

    items: List[WebhookDelivery]


@dataclass
class WebhookEventRecordsResponse(PaginatedResponse):
    """Webhook event records query response."""

    items: List[WebhookEventRecord]


@dataclass
class UsersResponse(PaginatedResponse):
    """Users query response."""

    items: List[User]


@dataclass
class TimeEntriesResponse(PaginatedResponse):
    """Time entries query response."""

    items: List[TimeEntry]


@dataclass
class TimersResponse(PaginatedResponse):
    """Timers query response."""

    items: List[Timer]


@dataclass
class TimeEntryTemplatesResponse(PaginatedResponse):
    """Time entry templates query response."""

    items: List[TimeEntryTemplate]


# Mutation Input Types
@dataclass
class ClientInput:
    """Client creation/update input."""

    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    status: Optional[ClientStatus] = None
    billing_address: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class TicketInput:
    """Ticket creation/update input."""

    client_id: str
    title: str
    site_id: Optional[str] = None
    asset_id: Optional[str] = None
    contact_id: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class AssetInput:
    """Asset creation/update input."""

    client_id: str
    name: str
    site_id: Optional[str] = None
    asset_type: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    status: Optional[AssetStatus] = None
    purchase_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class ContactInput:
    """Contact creation/update input."""

    client_id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    title: Optional[str] = None
    is_primary: Optional[bool] = None
    notes: Optional[str] = None


@dataclass
class SiteInput:
    """Site creation/update input."""

    client_id: str
    name: str
    address: Optional[str] = None
    description: Optional[str] = None
    timezone: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class KnowledgeBaseCollectionInput:
    """Knowledge base collection creation/update input."""

    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    is_public: Optional[bool] = None


@dataclass
class KnowledgeBaseArticleInput:
    """Knowledge base article creation/update input."""

    collection_id: str
    title: str
    content: str
    summary: Optional[str] = None
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None
    tags: Optional[List[str]] = None


@dataclass
class ProjectInput:
    """Project creation/update input."""

    client_id: str
    name: str
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    contract_id: Optional[str] = None
    site_id: Optional[str] = None
    assigned_to: Optional[str] = None
    manager_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    budget: Optional[float] = None
    billing_rate: Optional[float] = None
    progress_percentage: Optional[int] = None
    estimated_hours: Optional[int] = None
    notes: Optional[str] = None


@dataclass
class ContractSLAInput:
    """Contract SLA creation/update input."""

    contract_id: str
    level: SLALevel
    response_time_minutes: Optional[int] = None
    resolution_time_hours: Optional[int] = None
    availability_percentage: Optional[float] = None
    description: Optional[str] = None
    penalties: Optional[str] = None


@dataclass
class ContractRateInput:
    """Contract rate creation/update input."""

    contract_id: str
    service_type: str
    rate_type: str
    rate_amount: float
    currency: Optional[str] = None
    description: Optional[str] = None
    effective_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@dataclass
class ContractInput:
    """Contract creation/update input."""

    client_id: str
    name: str
    contract_type: ContractType
    start_date: datetime
    contract_number: Optional[str] = None
    status: Optional[ContractStatus] = None
    end_date: Optional[datetime] = None
    renewal_date: Optional[datetime] = None
    auto_renew: Optional[bool] = None
    billing_cycle: Optional[BillingCycle] = None
    contract_value: Optional[float] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    renewal_terms: Optional[str] = None
    cancellation_terms: Optional[str] = None
    signed_by_client: Optional[str] = None
    signed_by_provider: Optional[str] = None
    signed_date: Optional[datetime] = None
    notification_days: Optional[int] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class ProjectMilestoneInput:
    """Project milestone creation/update input."""

    project_id: str
    name: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    is_completed: Optional[bool] = None
    progress_percentage: Optional[int] = None
    order_index: Optional[int] = None
    notes: Optional[str] = None


@dataclass
class ProjectTaskInput:
    """Project task creation/update input."""

    # Required fields first
    project_id: str
    name: str

    # Optional fields with defaults
    milestone_id: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_to: Optional[str] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    estimated_hours: Optional[int] = None
    progress_percentage: Optional[int] = None
    order_index: Optional[int] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


@dataclass
class ProjectTimeEntryInput:
    """Project time entry creation/update input."""

    # Required fields first
    project_id: str
    user_id: str
    description: str
    hours: float
    start_time: datetime

    # Optional fields with defaults
    task_id: Optional[str] = None
    billable_hours: Optional[float] = None
    rate: Optional[float] = None
    end_time: Optional[datetime] = None
    is_billable: Optional[bool] = None
    notes: Optional[str] = None


@dataclass
class TaskInput:
    """Task creation/update input."""

    title: str
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None

    # Project linking
    project_id: Optional[str] = None

    # Assignment
    assigned_to: Optional[str] = None
    assigned_to_team: Optional[str] = None

    # Hierarchy
    parent_task_id: Optional[str] = None

    # Scheduling
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None

    # Recurring tasks
    recurrence_type: Optional[TaskRecurrenceType] = None
    recurrence_interval: Optional[int] = None
    recurrence_end_date: Optional[datetime] = None

    # Metadata
    labels: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    progress_percentage: Optional[int] = None
    is_milestone: Optional[bool] = None

    # Template
    template_id: Optional[str] = None


@dataclass
class TaskCommentInput:
    """Task comment creation input."""

    task_id: str
    content: str
    is_internal: Optional[bool] = None
    time_logged: Optional[float] = None


@dataclass
class TaskTimeEntryInput:
    """Task time entry creation input."""

    task_id: str
    hours: float
    description: Optional[str] = None
    date_logged: Optional[datetime] = None
    is_billable: Optional[bool] = None
    hourly_rate: Optional[float] = None


@dataclass
class TaskTemplateInput:
    """Task template creation/update input."""

    name: str
    description: Optional[str] = None
    default_priority: Optional[TaskPriority] = None
    estimated_hours: Optional[float] = None
    default_assignee_id: Optional[str] = None
    default_tags: Optional[List[str]] = None
    default_custom_fields: Optional[Dict[str, Any]] = None
    checklist_items: Optional[List[str]] = None


@dataclass
class TaskStatusUpdateInput:
    """Task status update input for workflow operations."""

    status: TaskStatus
    comment: Optional[str] = None
    time_logged: Optional[float] = None


@dataclass
class TaskAssignmentInput:
    """Task assignment input."""

    assigned_to: Optional[str] = None
    assigned_to_team: Optional[str] = None
    notify_assignee: Optional[bool] = True
    comment: Optional[str] = None


@dataclass
class TaskRecurrenceInput:
    """Task recurrence configuration input."""

    recurrence_type: TaskRecurrenceType
    recurrence_interval: Optional[int] = None
    recurrence_end_date: Optional[datetime] = None
    recurrence_count: Optional[int] = None  # end after N occurrences


@dataclass
class CommentInput:
    """Comment creation/update input."""

    entity_type: str
    entity_id: str
    content: str
    comment_type: Optional[CommentType] = None
    is_internal: Optional[bool] = None
    time_logged: Optional[float] = None
    parent_comment_id: Optional[str] = None
    attachment_ids: Optional[List[str]] = None


@dataclass
class CommentAttachmentInput:
    """Comment attachment creation input."""

    comment_id: str
    filename: str
    file_data: str  # base64 encoded file data
    mime_type: Optional[str] = None


@dataclass
class AttachmentInput:
    """Attachment creation/update input."""

    filename: str
    entity_type: EntityType
    entity_id: str
    description: Optional[str] = None
    attachment_type: Optional[AttachmentType] = None
    is_public: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AttachmentUploadInput:
    """Attachment upload input with file data."""

    filename: str
    original_filename: str
    entity_type: EntityType
    entity_id: str
    file_size: int
    mime_type: str
    description: Optional[str] = None
    attachment_type: Optional[AttachmentType] = None
    is_public: Optional[bool] = None
    checksum: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AttachmentVersionInput:
    """Attachment version creation input."""

    attachment_id: str
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    description: Optional[str] = None
    checksum: Optional[str] = None


@dataclass
class WebhookInput:
    """Webhook creation/update input."""

    name: str
    url: str
    events: List[WebhookEvent]
    status: Optional[WebhookStatus] = None
    secret: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    retry_count: Optional[int] = None
    timeout_seconds: Optional[int] = None
    headers: Optional[Dict[str, str]] = None
    content_type: Optional[str] = None
    tags: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to dictionary."""
        result: Dict[str, Any] = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, Enum):
                result[key] = value.value
            elif isinstance(value, list) and value and isinstance(value[0], Enum):
                result[key] = [item.value for item in value]
            else:
                result[key] = value
        return result


@dataclass
class WebhookTestInput:
    """Webhook test input."""

    webhook_id: str
    event_type: WebhookEvent
    test_payload: Optional[Dict[str, Any]] = None


@dataclass
class UserInput:
    """User creation/update input."""

    email: str
    first_name: str
    last_name: str
    role: UserRole
    status: Optional[UserStatus] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    is_technician: Optional[bool] = None
    hourly_rate: Optional[float] = None
    timezone: Optional[str] = None
    is_primary: Optional[bool] = None
    notification_preferences: Optional[Dict[str, Any]] = None
    permissions: Optional[List[str]] = None


@dataclass
class TimeEntryInput:
    """Time entry creation/update input."""

    user_id: str
    description: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    ticket_id: Optional[str] = None
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    client_id: Optional[str] = None
    status: Optional[TimeEntryStatus] = None
    entry_type: Optional[TimeEntryType] = None
    is_billable: Optional[bool] = None
    hourly_rate: Optional[float] = None
    work_category: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class TimerInput:
    """Timer creation/update input."""

    user_id: str
    description: str
    start_time: Optional[datetime] = None
    ticket_id: Optional[str] = None
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    client_id: Optional[str] = None
    is_billable: Optional[bool] = None
    entry_type: Optional[TimeEntryType] = None
    work_category: Optional[str] = None
    tags: Optional[List[str]] = None


@dataclass
class TimeEntryTemplateInput:
    """Time entry template creation/update input."""

    name: str
    description: str
    user_id: str
    default_duration_minutes: Optional[int] = None
    entry_type: Optional[TimeEntryType] = None
    is_billable: Optional[bool] = None
    work_category: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


@dataclass
class TimeEntryApprovalInput:
    """Time entry approval/rejection input."""

    time_entry_ids: List[str]
    status: TimeEntryStatus
    approval_notes: Optional[str] = None


# Automation Models
@dataclass
class AutomationAction(BaseModel):
    """Automation action model."""

    name: str
    action_type: ActionType
    config: Dict[str, Any]
    order_index: int = 0
    is_enabled: bool = True
    condition: Optional[str] = None
    timeout_seconds: Optional[int] = None
    retry_attempts: Optional[int] = None
    retry_delay_seconds: Optional[int] = None


@dataclass
class AutomationSchedule(BaseModel):
    """Automation schedule model."""

    schedule_type: ScheduleType
    cron_expression: Optional[str] = None
    interval_seconds: Optional[int] = None
    recurrence_frequency: Optional[RecurrenceFrequency] = None
    recurrence_count: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    timezone: Optional[str] = None
    is_active: bool = True


@dataclass
class AutomationTrigger(BaseModel):
    """Automation trigger model."""

    name: str
    trigger_type: AutomationTriggerType
    config: Dict[str, Any]
    conditions: Optional[Dict[str, Any]] = None
    is_enabled: bool = True
    schedule: Optional[AutomationSchedule] = None
    workflow_id: Optional[str] = None


@dataclass
class AutomationJob(BaseModel):
    """Automation job execution model."""

    workflow_id: str
    trigger_id: Optional[str] = None
    status: AutomationJobStatus = AutomationJobStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    execution_log: List[str] = field(default_factory=list)
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    max_retries: int = 3
    scheduled_at: Optional[datetime] = None
    priority: int = 0


@dataclass
class AutomationWorkflow(BaseModel):
    """Automation workflow model."""

    name: str
    description: Optional[str] = None
    status: AutomationWorkflowStatus = AutomationWorkflowStatus.DRAFT
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    is_template: bool = False
    template_id: Optional[str] = None

    # Workflow execution
    actions: List[AutomationAction] = field(default_factory=list)
    triggers: List[AutomationTrigger] = field(default_factory=list)

    # Configuration
    max_concurrent_jobs: int = 1
    timeout_seconds: Optional[int] = None
    retry_failed_actions: bool = True

    # Metadata
    created_by: Optional[str] = None
    last_modified_by: Optional[str] = None
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0

    # Template-specific fields
    template_variables: Optional[Dict[str, Any]] = None
    template_description: Optional[str] = None
    template_category: Optional[str] = None


# Automation Input Models
@dataclass
class AutomationWorkflowInput:
    """Automation workflow creation/update input."""

    name: str
    description: Optional[str] = None
    status: Optional[AutomationWorkflowStatus] = None
    tags: Optional[List[str]] = None
    is_template: Optional[bool] = None
    template_id: Optional[str] = None

    # Configuration
    max_concurrent_jobs: Optional[int] = None
    timeout_seconds: Optional[int] = None
    retry_failed_actions: Optional[bool] = None

    # Template-specific
    template_variables: Optional[Dict[str, Any]] = None
    template_description: Optional[str] = None
    template_category: Optional[str] = None


@dataclass
class AutomationActionInput:
    """Automation action creation/update input."""

    name: str
    action_type: ActionType
    config: Dict[str, Any]
    workflow_id: str
    order_index: Optional[int] = None
    is_enabled: Optional[bool] = None
    condition: Optional[str] = None
    timeout_seconds: Optional[int] = None
    retry_attempts: Optional[int] = None
    retry_delay_seconds: Optional[int] = None


@dataclass
class AutomationTriggerInput:
    """Automation trigger creation/update input."""

    name: str
    trigger_type: AutomationTriggerType
    config: Dict[str, Any]
    workflow_id: str
    conditions: Optional[Dict[str, Any]] = None
    is_enabled: Optional[bool] = None


@dataclass
class AutomationScheduleInput:
    """Automation schedule creation/update input."""

    schedule_type: ScheduleType
    trigger_id: str
    cron_expression: Optional[str] = None
    interval_seconds: Optional[int] = None
    recurrence_frequency: Optional[RecurrenceFrequency] = None
    recurrence_count: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None


@dataclass
class AutomationJobInput:
    """Automation job creation input."""

    workflow_id: str
    trigger_id: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    max_retries: Optional[int] = None


@dataclass
class AutomationExecutionInput:
    """Automation workflow execution input."""

    workflow_id: str
    input_data: Optional[Dict[str, Any]] = None
    trigger_id: Optional[str] = None
    priority: Optional[int] = None
    async_execution: bool = True
    wait_for_completion: bool = False
    timeout_seconds: Optional[int] = None


# Monitoring Enums
class AlertSeverity(str, Enum):
    """Alert severity enumeration."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CheckType(str, Enum):
    """Monitoring check type enumeration."""

    PING = "PING"
    HTTP = "HTTP"
    HTTPS = "HTTPS"
    TCP = "TCP"
    UDP = "UDP"
    DNS = "DNS"
    SSL_CERT = "SSL_CERT"
    DISK_SPACE = "DISK_SPACE"
    MEMORY = "MEMORY"
    CPU = "CPU"
    PROCESS = "PROCESS"
    SERVICE = "SERVICE"
    DATABASE = "DATABASE"
    CUSTOM_SCRIPT = "CUSTOM_SCRIPT"


class MetricType(str, Enum):
    """Metric type enumeration."""

    COUNTER = "COUNTER"
    GAUGE = "GAUGE"
    HISTOGRAM = "HISTOGRAM"
    SUMMARY = "SUMMARY"


class MonitoringAgentStatus(str, Enum):
    """Monitoring agent status enumeration."""

    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    DEGRADED = "DEGRADED"
    INSTALLING = "INSTALLING"
    UPDATING = "UPDATING"
    ERROR = "ERROR"


class CheckStatus(str, Enum):
    """Monitoring check status enumeration."""

    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"
    DISABLED = "DISABLED"


class AlertStatus(str, Enum):
    """Alert status enumeration."""

    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    SILENCED = "SILENCED"


# Scripts Enums
class ScriptType(str, Enum):
    """Script type enumeration."""

    POWERSHELL = "POWERSHELL"
    BASH = "BASH"
    PYTHON = "PYTHON"
    BATCH = "BATCH"
    JAVASCRIPT = "JAVASCRIPT"
    VBS = "VBS"
    CUSTOM = "CUSTOM"


class ExecutionStatus(str, Enum):
    """Script execution status enumeration."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"


class ScriptCategory(str, Enum):
    """Script category enumeration."""

    MONITORING = "MONITORING"
    MAINTENANCE = "MAINTENANCE"
    DEPLOYMENT = "DEPLOYMENT"
    BACKUP = "BACKUP"
    SECURITY = "SECURITY"
    REPORTING = "REPORTING"
    AUTOMATION = "AUTOMATION"
    DIAGNOSTIC = "DIAGNOSTIC"
    CUSTOM = "CUSTOM"


class DeploymentStatus(str, Enum):
    """Script deployment status enumeration."""

    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"


class ExecutionTrigger(str, Enum):
    """Script execution trigger enumeration."""

    MANUAL = "MANUAL"
    SCHEDULED = "SCHEDULED"
    EVENT_DRIVEN = "EVENT_DRIVEN"
    CONDITION_BASED = "CONDITION_BASED"


# Script Types
@dataclass
class ScriptParameter(BaseModel):
    """Script parameter model."""

    script_id: str
    name: str
    parameter_type: str  # STRING, INTEGER, BOOLEAN, FILE, etc.
    description: Optional[str] = None
    default_value: Optional[str] = None
    is_required: bool = False
    is_sensitive: bool = False  # for passwords, keys, etc.
    validation_regex: Optional[str] = None
    allowed_values: List[str] = field(default_factory=list)
    display_order: int = 0


@dataclass
class ScriptTemplate(BaseModel):
    """Script template model."""

    name: str
    description: str
    script_type: ScriptType
    category: ScriptCategory = ScriptCategory.CUSTOM
    script_content: Optional[str] = None
    parameters: List[ScriptParameter] = field(default_factory=list)
    is_public: bool = False
    author_id: Optional[str] = None
    author_name: Optional[str] = None
    version: str = "1.0.0"
    usage_count: int = 0
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Script(BaseModel):
    """Script model."""

    name: str
    description: Optional[str] = None
    script_type: ScriptType = ScriptType.POWERSHELL
    category: ScriptCategory = ScriptCategory.CUSTOM
    script_content: str = ""

    # Deployment and status
    deployment_status: DeploymentStatus = DeploymentStatus.DRAFT
    is_template: bool = False
    template_id: Optional[str] = None

    # Author and ownership
    author_id: Optional[str] = None
    author_name: Optional[str] = None
    library_id: Optional[str] = None

    # Execution settings
    timeout_seconds: Optional[int] = None
    retry_count: int = 0
    run_as_user: Optional[str] = None
    requires_elevation: bool = False

    # Parameters and configuration
    parameters: List[ScriptParameter] = field(default_factory=list)
    environment_variables: Dict[str, str] = field(default_factory=dict)
    working_directory: Optional[str] = None

    # Metadata and organization
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    is_public: bool = False
    usage_count: int = 0
    last_executed: Optional[datetime] = None
    custom_fields: Dict[str, Any] = field(default_factory=dict)

    # File and checksum information
    file_hash: Optional[str] = None
    file_size: Optional[int] = None


@dataclass
class ScriptExecution(BaseModel):
    """Script execution model."""

    script_id: str
    script_name: Optional[str] = None
    status: ExecutionStatus = ExecutionStatus.PENDING
    execution_trigger: ExecutionTrigger = ExecutionTrigger.MANUAL

    # Execution metadata
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    executed_by: Optional[str] = None
    executed_by_name: Optional[str] = None

    # Target information
    target_assets: List[str] = field(default_factory=list)
    target_sites: List[str] = field(default_factory=list)
    target_clients: List[str] = field(default_factory=list)

    # Execution parameters and results
    parameters: Dict[str, Any] = field(default_factory=dict)
    environment_variables: Dict[str, str] = field(default_factory=dict)
    exit_code: Optional[int] = None
    output: Optional[str] = None
    error_output: Optional[str] = None

    # Progress and statistics
    total_targets: int = 0
    successful_targets: int = 0
    failed_targets: int = 0
    progress_percentage: Optional[int] = None

    # Execution settings
    timeout_seconds: Optional[int] = None
    retry_count: int = 0
    current_retry: int = 0

    # Scheduling information
    scheduled_at: Optional[datetime] = None
    deployment_id: Optional[str] = None

    # Error and failure information
    failure_reason: Optional[str] = None
    cancellation_reason: Optional[str] = None

    # Logs and output details
    execution_log: List[str] = field(default_factory=list)
    target_results: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ScriptDeployment(BaseModel):
    """Script deployment model."""

    script_id: str
    deployment_name: str
    script_name: Optional[str] = None
    deployment_status: DeploymentStatus = DeploymentStatus.DRAFT

    # Target configuration
    target_type: str = "all"  # 'asset', 'site', 'client', 'all'
    target_ids: List[str] = field(default_factory=list)
    target_criteria: Optional[Dict[str, Any]] = None

    # Scheduling
    schedule_expression: Optional[str] = None  # cron expression
    next_run_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    is_enabled: bool = True

    # Execution configuration
    timeout_seconds: Optional[int] = None
    retry_count: int = 0
    run_as_user: Optional[str] = None
    requires_elevation: bool = False

    # Parameters and environment
    parameters: Dict[str, Any] = field(default_factory=dict)
    environment_variables: Dict[str, str] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)

    # Deployment metadata
    created_by: Optional[str] = None
    created_by_name: Optional[str] = None
    last_modified_by: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    # Statistics and monitoring
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_execution_time: Optional[float] = None
    last_execution_status: Optional[ExecutionStatus] = None

    # Notification settings
    notify_on_success: bool = False
    notify_on_failure: bool = True
    notification_recipients: List[str] = field(default_factory=list)


@dataclass
class ScriptLibrary(BaseModel):
    """Script library model."""

    name: str
    description: str
    owner_id: Optional[str] = None
    owner_name: Optional[str] = None
    is_public: bool = False

    # Organization and metadata
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None

    # Statistics
    script_count: int = 0
    template_count: int = 0
    subscriber_count: int = 0
    usage_count: int = 0

    # Access control
    shared_with_users: List[str] = field(default_factory=list)
    shared_with_teams: List[str] = field(default_factory=list)
    permissions: Dict[str, Any] = field(default_factory=dict)

    # Content organization
    featured_scripts: List[str] = field(default_factory=list)
    recent_scripts: List[str] = field(default_factory=list)

    # Metadata
    last_updated_by: Optional[str] = None
    version: str = "1.0.0"
    custom_fields: Dict[str, Any] = field(default_factory=dict)


# Monitoring Data Classes
@dataclass
class MonitoringAgent:
    """Monitoring agent data class."""

    id: str
    name: str
    description: Optional[str] = None
    status: MonitoringAgentStatus = MonitoringAgentStatus.OFFLINE
    version: Optional[str] = None
    host_id: Optional[str] = None
    host_name: Optional[str] = None
    ip_address: Optional[str] = None
    port: Optional[int] = None
    api_key: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    tags: List[str] = field(default_factory=list)
    last_seen: Optional[datetime] = None
    installed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MonitoringAgent":
        """Create MonitoringAgent from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            status=MonitoringAgentStatus(data.get("status", "OFFLINE")),
            version=data.get("version"),
            host_id=data.get("host_id"),
            host_name=data.get("host_name"),
            ip_address=data.get("ip_address"),
            port=data.get("port"),
            api_key=data.get("api_key"),
            config=data.get("config"),
            tags=data.get("tags", []),
            last_seen=convert_iso_to_datetime(data.get("last_seen")),
            installed_at=convert_iso_to_datetime(data.get("installed_at")),
            updated_at=convert_iso_to_datetime(data.get("updated_at")),
            created_at=convert_iso_to_datetime(data.get("created_at")),
            created_by=data.get("created_by"),
            metadata=data.get("metadata"),
        )


@dataclass
class MonitoringCheck:
    """Monitoring check data class."""

    id: str
    name: str
    description: Optional[str] = None
    check_type: CheckType = CheckType.PING
    target: Optional[str] = None
    status: CheckStatus = CheckStatus.UNKNOWN
    enabled: bool = True
    interval: int = 300  # seconds
    timeout: int = 30  # seconds
    retry_count: int = 3
    config: Optional[Dict[str, Any]] = None
    thresholds: Optional[Dict[str, Any]] = None
    agent_id: Optional[str] = None
    site_id: Optional[str] = None
    asset_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    last_check: Optional[datetime] = None
    next_check: Optional[datetime] = None
    last_result: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MonitoringCheck":
        """Create MonitoringCheck from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            check_type=CheckType(data.get("check_type", "PING")),
            target=data.get("target"),
            status=CheckStatus(data.get("status", "UNKNOWN")),
            enabled=data.get("enabled", True),
            interval=data.get("interval", 300),
            timeout=data.get("timeout", 30),
            retry_count=data.get("retry_count", 3),
            config=data.get("config"),
            thresholds=data.get("thresholds"),
            agent_id=data.get("agent_id"),
            site_id=data.get("site_id"),
            asset_id=data.get("asset_id"),
            tags=data.get("tags", []),
            last_check=convert_iso_to_datetime(data.get("last_check")),
            next_check=convert_iso_to_datetime(data.get("next_check")),
            last_result=data.get("last_result"),
            created_at=convert_iso_to_datetime(data.get("created_at")),
            updated_at=convert_iso_to_datetime(data.get("updated_at")),
            created_by=data.get("created_by"),
            metadata=data.get("metadata"),
        )


@dataclass
class MonitoringAlert:
    """Monitoring alert data class."""

    id: str
    name: str
    description: Optional[str] = None
    check_id: Optional[str] = None
    severity: AlertSeverity = AlertSeverity.MEDIUM
    status: AlertStatus = AlertStatus.ACTIVE
    condition: Optional[Dict[str, Any]] = None
    notification_config: Optional[Dict[str, Any]] = None
    suppression_rules: Optional[Dict[str, Any]] = None
    escalation_rules: Optional[Dict[str, Any]] = None
    tags: List[str] = field(default_factory=list)
    triggered_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    silenced_until: Optional[datetime] = None
    alert_count: int = 0
    last_alert: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MonitoringAlert":
        """Create MonitoringAlert from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            check_id=data.get("check_id"),
            severity=AlertSeverity(data.get("severity", "MEDIUM")),
            status=AlertStatus(data.get("status", "ACTIVE")),
            condition=data.get("condition"),
            notification_config=data.get("notification_config"),
            suppression_rules=data.get("suppression_rules"),
            escalation_rules=data.get("escalation_rules"),
            tags=data.get("tags", []),
            triggered_at=convert_iso_to_datetime(data.get("triggered_at")),
            acknowledged_at=convert_iso_to_datetime(data.get("acknowledged_at")),
            acknowledged_by=data.get("acknowledged_by"),
            resolved_at=convert_iso_to_datetime(data.get("resolved_at")),
            resolved_by=data.get("resolved_by"),
            silenced_until=convert_iso_to_datetime(data.get("silenced_until")),
            alert_count=data.get("alert_count", 0),
            last_alert=convert_iso_to_datetime(data.get("last_alert")),
            created_at=convert_iso_to_datetime(data.get("created_at")),
            updated_at=convert_iso_to_datetime(data.get("updated_at")),
            created_by=data.get("created_by"),
            metadata=data.get("metadata"),
        )


@dataclass
class MonitoringMetric:
    """Monitoring metric data class."""

    id: str
    name: str
    description: Optional[str] = None
    metric_type: MetricType = MetricType.GAUGE
    unit: Optional[str] = None
    value: Optional[float] = None
    labels: Optional[Dict[str, str]] = None
    agent_id: Optional[str] = None
    check_id: Optional[str] = None
    asset_id: Optional[str] = None
    site_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    retention_period: Optional[int] = None  # days
    aggregation_config: Optional[Dict[str, Any]] = None
    tags: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MonitoringMetric":
        """Create MonitoringMetric from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            metric_type=MetricType(data.get("metric_type", "GAUGE")),
            unit=data.get("unit"),
            value=data.get("value"),
            labels=data.get("labels"),
            agent_id=data.get("agent_id"),
            check_id=data.get("check_id"),
            asset_id=data.get("asset_id"),
            site_id=data.get("site_id"),
            timestamp=convert_iso_to_datetime(data.get("timestamp")),
            retention_period=data.get("retention_period"),
            aggregation_config=data.get("aggregation_config"),
            tags=data.get("tags", []),
            created_at=convert_iso_to_datetime(data.get("created_at")),
            updated_at=convert_iso_to_datetime(data.get("updated_at")),
            metadata=data.get("metadata"),
        )


# Monitoring Input Types
@dataclass
class MonitoringAgentInput:
    """Input for creating/updating monitoring agents."""

    name: str
    description: Optional[str] = None
    host_id: Optional[str] = None
    host_name: Optional[str] = None
    ip_address: Optional[str] = None
    port: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MonitoringCheckInput:
    """Input for creating/updating monitoring checks."""

    name: str
    description: Optional[str] = None
    check_type: Optional[CheckType] = None
    target: Optional[str] = None
    enabled: Optional[bool] = None
    interval: Optional[int] = None
    timeout: Optional[int] = None
    retry_count: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    thresholds: Optional[Dict[str, Any]] = None
    agent_id: Optional[str] = None
    site_id: Optional[str] = None
    asset_id: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MonitoringAlertInput:
    """Input for creating/updating monitoring alerts."""

    name: str
    description: Optional[str] = None
    check_id: Optional[str] = None
    severity: Optional[AlertSeverity] = None
    condition: Optional[Dict[str, Any]] = None
    notification_config: Optional[Dict[str, Any]] = None
    suppression_rules: Optional[Dict[str, Any]] = None
    escalation_rules: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MonitoringMetricInput:
    """Input for creating/updating monitoring metrics."""

    name: str
    description: Optional[str] = None
    metric_type: Optional[MetricType] = None
    unit: Optional[str] = None
    value: Optional[float] = None
    labels: Optional[Dict[str, str]] = None
    agent_id: Optional[str] = None
    check_id: Optional[str] = None
    asset_id: Optional[str] = None
    site_id: Optional[str] = None
    retention_period: Optional[int] = None
    aggregation_config: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


# Script Input Types
@dataclass
class ScriptInput:
    """Script creation/update input."""

    name: str
    description: Optional[str] = None
    script_type: Optional[ScriptType] = None
    category: Optional[ScriptCategory] = None
    script_content: Optional[str] = None
    deployment_status: Optional[DeploymentStatus] = None
    is_template: Optional[bool] = None
    template_id: Optional[str] = None
    library_id: Optional[str] = None
    timeout_seconds: Optional[int] = None
    retry_count: Optional[int] = None
    run_as_user: Optional[str] = None
    requires_elevation: Optional[bool] = None
    environment_variables: Optional[Dict[str, str]] = None
    working_directory: Optional[str] = None
    version: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class ScriptExecutionInput:
    """Script execution input."""

    script_id: str
    execution_trigger: Optional[ExecutionTrigger] = None
    target_assets: Optional[List[str]] = None
    target_sites: Optional[List[str]] = None
    target_clients: Optional[List[str]] = None
    parameters: Optional[Dict[str, Any]] = None
    environment_variables: Optional[Dict[str, str]] = None
    timeout_seconds: Optional[int] = None
    retry_count: Optional[int] = None
    scheduled_at: Optional[datetime] = None


@dataclass
class ScriptDeploymentInput:
    """Script deployment creation/update input."""

    script_id: str
    deployment_name: str
    target_type: str
    deployment_status: Optional[DeploymentStatus] = None
    target_ids: Optional[List[str]] = None
    target_criteria: Optional[Dict[str, Any]] = None
    schedule_expression: Optional[str] = None
    is_enabled: Optional[bool] = None
    timeout_seconds: Optional[int] = None
    retry_count: Optional[int] = None
    run_as_user: Optional[str] = None
    requires_elevation: Optional[bool] = None
    parameters: Optional[Dict[str, Any]] = None
    environment_variables: Optional[Dict[str, str]] = None
    configuration: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    notify_on_success: Optional[bool] = None
    notify_on_failure: Optional[bool] = None
    notification_recipients: Optional[List[str]] = None


@dataclass
class ScriptLibraryInput:
    """Script library creation/update input."""

    name: str
    description: str
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class ScriptParameterInput:
    """Script parameter creation/update input."""

    script_id: str
    name: str
    parameter_type: str
    description: Optional[str] = None
    default_value: Optional[str] = None
    is_required: Optional[bool] = None
    is_sensitive: Optional[bool] = None
    validation_regex: Optional[str] = None
    allowed_values: Optional[List[str]] = None
    display_order: Optional[int] = None


@dataclass
class ScriptTemplateInput:
    """Script template creation/update input."""

    name: str
    description: str
    script_type: ScriptType
    category: Optional[ScriptCategory] = None
    script_content: Optional[str] = None
    is_public: Optional[bool] = None
    version: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class MonitoringAgentFilter:
    """Filter for monitoring agent queries."""

    id: Optional[str] = None
    name: Optional[str] = None
    status: Optional[MonitoringAgentStatus] = None
    host_id: Optional[str] = None
    host_name: Optional[str] = None
    ip_address: Optional[str] = None
    tags: Optional[List[str]] = None
    last_seen_after: Optional[datetime] = None
    last_seen_before: Optional[datetime] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


@dataclass
class MonitoringCheckFilter:
    """Filter for monitoring check queries."""

    id: Optional[str] = None
    name: Optional[str] = None
    check_type: Optional[CheckType] = None
    status: Optional[CheckStatus] = None
    enabled: Optional[bool] = None
    agent_id: Optional[str] = None
    site_id: Optional[str] = None
    asset_id: Optional[str] = None
    target: Optional[str] = None
    tags: Optional[List[str]] = None
    last_check_after: Optional[datetime] = None
    last_check_before: Optional[datetime] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


@dataclass
class MonitoringAlertFilter:
    """Filter for monitoring alert queries."""

    id: Optional[str] = None
    name: Optional[str] = None
    check_id: Optional[str] = None
    severity: Optional[AlertSeverity] = None
    status: Optional[AlertStatus] = None
    tags: Optional[List[str]] = None
    triggered_after: Optional[datetime] = None
    triggered_before: Optional[datetime] = None
    acknowledged: Optional[bool] = None
    resolved: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


# Script Filter Types
@dataclass
class ScriptFilter:
    """Script query filter."""

    name: Optional[str] = None
    script_type: Optional[ScriptType] = None
    category: Optional[ScriptCategory] = None
    deployment_status: Optional[DeploymentStatus] = None
    author_id: Optional[str] = None
    library_id: Optional[str] = None
    is_template: Optional[bool] = None
    template_id: Optional[str] = None
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    last_executed_after: Optional[datetime] = None
    last_executed_before: Optional[datetime] = None


@dataclass
class ScriptExecutionFilter:
    """Script execution query filter."""

    script_id: Optional[str] = None
    status: Optional[ExecutionStatus] = None
    execution_trigger: Optional[ExecutionTrigger] = None
    executed_by: Optional[str] = None
    deployment_id: Optional[str] = None
    started_after: Optional[datetime] = None
    started_before: Optional[datetime] = None
    completed_after: Optional[datetime] = None
    completed_before: Optional[datetime] = None
    duration_min: Optional[int] = None
    duration_max: Optional[int] = None
    has_failures: Optional[bool] = None
    target_assets: Optional[List[str]] = None
    target_sites: Optional[List[str]] = None
    target_clients: Optional[List[str]] = None


@dataclass
class ScriptDeploymentFilter:
    """Script deployment query filter."""

    script_id: Optional[str] = None
    deployment_name: Optional[str] = None
    deployment_status: Optional[DeploymentStatus] = None
    target_type: Optional[str] = None
    is_enabled: Optional[bool] = None
    created_by: Optional[str] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    next_run_after: Optional[datetime] = None
    next_run_before: Optional[datetime] = None
    last_run_after: Optional[datetime] = None
    last_run_before: Optional[datetime] = None


@dataclass
class ScriptLibraryFilter:
    """Script library query filter."""

    name: Optional[str] = None
    owner_id: Optional[str] = None
    is_public: Optional[bool] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    script_count_min: Optional[int] = None
    script_count_max: Optional[int] = None


@dataclass
class MonitoringMetricFilter:
    """Filter for monitoring metric queries."""

    id: Optional[str] = None
    name: Optional[str] = None
    metric_type: Optional[MetricType] = None
    unit: Optional[str] = None
    agent_id: Optional[str] = None
    check_id: Optional[str] = None
    asset_id: Optional[str] = None
    site_id: Optional[str] = None
    timestamp_after: Optional[datetime] = None
    timestamp_before: Optional[datetime] = None
    tags: Optional[List[str]] = None


# Utility Functions
def convert_datetime_to_iso(dt: Optional[datetime]) -> Optional[str]:
    """Convert datetime to ISO string."""
    return dt.isoformat() if dt else None


def convert_iso_to_datetime(iso_string: Optional[str]) -> Optional[datetime]:
    """Convert ISO string to datetime."""
    if not iso_string:
        return None
    try:
        return datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
    except ValueError:
        return None


def serialize_filter_value(value: Any) -> Any:
    """Serialize filter value for GraphQL variables."""
    if isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, Enum):
        return value.value
    elif isinstance(value, list):
        return [serialize_filter_value(item) for item in value]
    elif isinstance(value, dict):
        return {k: serialize_filter_value(v) for k, v in value.items()}
    else:
        return value


def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case to camelCase."""
    components = snake_str.split("_")
    return components[0] + "".join(word.capitalize() for word in components[1:])


def serialize_input(input_obj: Any) -> Dict[str, Any]:
    """Serialize input object for GraphQL variables."""
    if hasattr(input_obj, "__dict__"):
        result = {}
        for key, value in input_obj.__dict__.items():
            if value is not None:
                # Convert snake_case to camelCase for GraphQL
                camel_key = snake_to_camel(key)
                result[camel_key] = serialize_filter_value(value)
        return result
    else:
        # Cast to maintain type safety for mypy
        return serialize_filter_value(input_obj)  # type: ignore[no-any-return]
