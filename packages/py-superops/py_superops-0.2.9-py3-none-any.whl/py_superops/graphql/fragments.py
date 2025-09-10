# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Reusable GraphQL fragments for common fields in SuperOps API.

This module provides GraphQL fragments that can be reused across queries and mutations
to maintain consistency and reduce duplication.
"""

from typing import Optional, Set


class GraphQLFragment:
    """Represents a GraphQL fragment with dependencies."""

    def __init__(
        self, name: str, on_type: str, fields: str, dependencies: Optional[Set[str]] = None
    ):
        """Initialize a GraphQL fragment.

        Args:
            name: Fragment name
            on_type: GraphQL type the fragment applies to
            fields: Fragment field selection
            dependencies: Set of other fragment names this fragment depends on
        """
        self.name = name
        self.on_type = on_type
        self.fields = fields.strip()
        self.dependencies = dependencies or set()

    def __str__(self) -> str:
        """Return the fragment definition."""
        return f"fragment {self.name} on {self.on_type} {{\n{self.fields}\n}}"

    def get_spread(self) -> str:
        """Return the fragment spread syntax."""
        return f"...{self.name}"


# Base fragments
BASE_FIELDS = GraphQLFragment(
    name="BaseFields",
    on_type="BaseModel",
    fields="""
    id
    createdAt
    updatedAt
    """,
)

PAGINATION_INFO = GraphQLFragment(
    name="PaginationInfo",
    on_type="PaginationInfo",
    fields="""
    page
    pageSize
    total
    hasNextPage
    hasPreviousPage
    """,
)

# Client fragments
CLIENT_CORE_FIELDS = GraphQLFragment(
    name="ClientCoreFields",
    on_type="Client",
    fields="""
    ...BaseFields
    name
    email
    phone
    status
    """,
    dependencies={"BaseFields"},
)

CLIENT_FULL_FIELDS = GraphQLFragment(
    name="ClientFullFields",
    on_type="Client",
    fields="""
    ...ClientCoreFields
    address
    billingAddress
    notes
    tags
    customFields
    """,
    dependencies={"ClientCoreFields"},
)

CLIENT_SUMMARY_FIELDS = GraphQLFragment(
    name="ClientSummaryFields",
    on_type="Client",
    fields="""
    id
    name
    email
    status
    """,
)

# Contact fragments
CONTACT_CORE_FIELDS = GraphQLFragment(
    name="ContactCoreFields",
    on_type="Contact",
    fields="""
    ...BaseFields
    clientId
    firstName
    lastName
    email
    phone
    isPrimary
    """,
    dependencies={"BaseFields"},
)

CONTACT_FULL_FIELDS = GraphQLFragment(
    name="ContactFullFields",
    on_type="Contact",
    fields="""
    ...ContactCoreFields
    title
    notes
    """,
    dependencies={"ContactCoreFields"},
)

# Site fragments
SITE_CORE_FIELDS = GraphQLFragment(
    name="SiteCoreFields",
    on_type="Site",
    fields="""
    ...BaseFields
    clientId
    name
    address
    """,
    dependencies={"BaseFields"},
)

SITE_FULL_FIELDS = GraphQLFragment(
    name="SiteFullFields",
    on_type="Site",
    fields="""
    ...SiteCoreFields
    description
    timezone
    notes
    """,
    dependencies={"SiteCoreFields"},
)

# Asset fragments
ASSET_CORE_FIELDS = GraphQLFragment(
    name="AssetCoreFields",
    on_type="Asset",
    fields="""
    ...BaseFields
    clientId
    siteId
    name
    assetType
    status
    """,
    dependencies={"BaseFields"},
)

ASSET_FULL_FIELDS = GraphQLFragment(
    name="AssetFullFields",
    on_type="Asset",
    fields="""
    ...AssetCoreFields
    manufacturer
    model
    serialNumber
    purchaseDate
    warrantyExpiry
    location
    notes
    customFields
    """,
    dependencies={"AssetCoreFields"},
)

ASSET_SUMMARY_FIELDS = GraphQLFragment(
    name="AssetSummaryFields",
    on_type="Asset",
    fields="""
    id
    name
    assetType
    status
    manufacturer
    model
    """,
)

# Ticket fragments
TICKET_CORE_FIELDS = GraphQLFragment(
    name="TicketCoreFields",
    on_type="Ticket",
    fields="""
    ...BaseFields
    clientId
    siteId
    assetId
    contactId
    title
    status
    priority
    assignedTo
    """,
    dependencies={"BaseFields"},
)

TICKET_FULL_FIELDS = GraphQLFragment(
    name="TicketFullFields",
    on_type="Ticket",
    fields="""
    ...TicketCoreFields
    description
    dueDate
    resolution
    timeSpent
    tags
    customFields
    """,
    dependencies={"TicketCoreFields"},
)

TICKET_SUMMARY_FIELDS = GraphQLFragment(
    name="TicketSummaryFields",
    on_type="Ticket",
    fields="""
    id
    title
    status
    priority
    assignedTo
    createdAt
    dueDate
    """,
)

TICKET_COMMENT_FIELDS = GraphQLFragment(
    name="TicketCommentFields",
    on_type="TicketComment",
    fields="""
    ...BaseFields
    ticketId
    authorId
    authorName
    content
    isInternal
    timeSpent
    """,
    dependencies={"BaseFields"},
)

# Task fragments
TASK_CORE_FIELDS = GraphQLFragment(
    name="TaskCoreFields",
    on_type="Task",
    fields="""
    ...BaseFields
    title
    description
    status
    priority
    projectId
    assignedTo
    assignedToTeam
    creatorId
    parentTaskId
    dueDate
    startDate
    """,
    dependencies={"BaseFields"},
)

TASK_FULL_FIELDS = GraphQLFragment(
    name="TaskFullFields",
    on_type="Task",
    fields="""
    ...TaskCoreFields
    subtaskCount
    completedAt
    estimatedHours
    actualHours
    recurrenceType
    recurrenceInterval
    recurrenceEndDate
    parentRecurringTaskId
    timeEntriesCount
    totalTimeLogged
    billableTime
    labels
    tags
    customFields
    progressPercentage
    isMilestone
    isTemplate
    templateId
    attachmentCount
    commentCount
    overdueAlertSent
    reminderSent
    """,
    dependencies={"TaskCoreFields"},
)

TASK_SUMMARY_FIELDS = GraphQLFragment(
    name="TaskSummaryFields",
    on_type="Task",
    fields="""
    id
    title
    status
    priority
    assignedTo
    dueDate
    progressPercentage
    createdAt
    updatedAt
    """,
)

TASK_COMMENT_FIELDS = GraphQLFragment(
    name="TaskCommentFields",
    on_type="TaskComment",
    fields="""
    ...BaseFields
    taskId
    authorId
    authorName
    content
    isInternal
    timeLogged
    """,
    dependencies={"BaseFields"},
)

TASK_TIME_ENTRY_FIELDS = GraphQLFragment(
    name="TaskTimeEntryFields",
    on_type="TaskTimeEntry",
    fields="""
    ...BaseFields
    taskId
    userId
    userName
    hours
    description
    dateLogged
    isBillable
    hourlyRate
    """,
    dependencies={"BaseFields"},
)

TASK_TEMPLATE_FIELDS = GraphQLFragment(
    name="TaskTemplateFields",
    on_type="TaskTemplate",
    fields="""
    ...BaseFields
    name
    description
    defaultPriority
    estimatedHours
    defaultAssigneeId
    defaultTags
    defaultCustomFields
    checklistItems
    """,
    dependencies={"BaseFields"},
)

# Comment fragments
COMMENT_CORE_FIELDS = GraphQLFragment(
    name="CommentCoreFields",
    on_type="Comment",
    fields="""
    ...BaseFields
    entityType
    entityId
    authorId
    authorName
    content
    commentType
    isInternal
    timeLogged
    """,
    dependencies={"BaseFields"},
)

COMMENT_FULL_FIELDS = GraphQLFragment(
    name="CommentFullFields",
    on_type="Comment",
    fields="""
    ...CommentCoreFields
    parentCommentId
    replyCount
    attachments
    """,
    dependencies={"CommentCoreFields"},
)

COMMENT_SUMMARY_FIELDS = GraphQLFragment(
    name="CommentSummaryFields",
    on_type="Comment",
    fields="""
    id
    authorName
    content
    commentType
    isInternal
    createdAt
    replyCount
    """,
)

COMMENT_ATTACHMENT_FIELDS = GraphQLFragment(
    name="CommentAttachmentFields",
    on_type="CommentAttachment",
    fields="""
    ...BaseFields
    commentId
    filename
    fileUrl
    fileSize
    mimeType
    """,
    dependencies={"BaseFields"},
)

# Knowledge Base fragments
KB_COLLECTION_CORE_FIELDS = GraphQLFragment(
    name="KBCollectionCoreFields",
    on_type="KnowledgeBaseCollection",
    fields="""
    ...BaseFields
    name
    description
    parentId
    isPublic
    """,
    dependencies={"BaseFields"},
)

KB_COLLECTION_FULL_FIELDS = GraphQLFragment(
    name="KBCollectionFullFields",
    on_type="KnowledgeBaseCollection",
    fields="""
    ...KBCollectionCoreFields
    articleCount
    """,
    dependencies={"KBCollectionCoreFields"},
)

KB_ARTICLE_CORE_FIELDS = GraphQLFragment(
    name="KBArticleCoreFields",
    on_type="KnowledgeBaseArticle",
    fields="""
    ...BaseFields
    collectionId
    title
    summary
    authorId
    authorName
    isPublished
    isFeatured
    """,
    dependencies={"BaseFields"},
)

KB_ARTICLE_FULL_FIELDS = GraphQLFragment(
    name="KBArticleFullFields",
    on_type="KnowledgeBaseArticle",
    fields="""
    ...KBArticleCoreFields
    content
    viewCount
    tags
    """,
    dependencies={"KBArticleCoreFields"},
)

KB_ARTICLE_SUMMARY_FIELDS = GraphQLFragment(
    name="KBArticleSummaryFields",
    on_type="KnowledgeBaseArticle",
    fields="""
    id
    title
    summary
    authorName
    isPublished
    viewCount
    createdAt
    updatedAt
    """,
)

# Project fragments
PROJECT_CORE_FIELDS = GraphQLFragment(
    name="ProjectCoreFields",
    on_type="Project",
    fields="""
    ...BaseFields
    clientId
    contractId
    name
    status
    priority
    assignedTo
    managerId
    startDate
    endDate
    dueDate
    """,
    dependencies={"BaseFields"},
)

# Contract fragments
CONTRACT_CORE_FIELDS = GraphQLFragment(
    name="ContractCoreFields",
    on_type="Contract",
    fields="""
    ...BaseFields
    clientId
    name
    contractNumber
    contractType
    status
    startDate
    endDate
    billingCycle
    contractValue
    currency
    """,
    dependencies={"BaseFields"},
)

PROJECT_FULL_FIELDS = GraphQLFragment(
    name="ProjectFullFields",
    on_type="Project",
    fields="""
    ...ProjectCoreFields
    description
    siteId
    budget
    billingRate
    progressPercentage
    estimatedHours
    actualHours
    notes
    tags
    customFields
    """,
    dependencies={"ProjectCoreFields"},
)

PROJECT_SUMMARY_FIELDS = GraphQLFragment(
    name="ProjectSummaryFields",
    on_type="Project",
    fields="""
    id
    name
    status
    priority
    assignedTo
    managerId
    startDate
    dueDate
    progressPercentage
    """,
)

PROJECT_MILESTONE_FIELDS = GraphQLFragment(
    name="ProjectMilestoneFields",
    on_type="ProjectMilestone",
    fields="""
    ...BaseFields
    projectId
    name
    description
    dueDate
    completionDate
    isCompleted
    progressPercentage
    orderIndex
    notes
    """,
    dependencies={"BaseFields"},
)

CONTRACT_FULL_FIELDS = GraphQLFragment(
    name="ContractFullFields",
    on_type="Contract",
    fields="""
    ...ContractCoreFields
    renewalDate
    autoRenew
    description
    termsAndConditions
    renewalTerms
    cancellationTerms
    signedByClient
    signedByProvider
    signedDate
    notificationDays
    tags
    customFields
    """,
    dependencies={"ContractCoreFields"},
)

CONTRACT_SUMMARY_FIELDS = GraphQLFragment(
    name="ContractSummaryFields",
    on_type="Contract",
    fields="""
    id
    name
    contractNumber
    contractType
    status
    clientId
    contractValue
    currency
    startDate
    endDate
    """,
)

CONTRACT_SLA_FIELDS = GraphQLFragment(
    name="ContractSLAFields",
    on_type="ContractSLA",
    fields="""
    ...BaseFields
    contractId
    level
    responseTimeMinutes
    resolutionTimeHours
    availabilityPercentage
    description
    penalties
    """,
    dependencies={"BaseFields"},
)

PROJECT_TASK_CORE_FIELDS = GraphQLFragment(
    name="ProjectTaskCoreFields",
    on_type="ProjectTask",
    fields="""
    ...BaseFields
    projectId
    milestoneId
    name
    status
    priority
    assignedTo
    startDate
    dueDate
    completionDate
    """,
    dependencies={"BaseFields"},
)

PROJECT_TASK_FULL_FIELDS = GraphQLFragment(
    name="ProjectTaskFullFields",
    on_type="ProjectTask",
    fields="""
    ...ProjectTaskCoreFields
    description
    estimatedHours
    actualHours
    progressPercentage
    orderIndex
    notes
    tags
    """,
    dependencies={"ProjectTaskCoreFields"},
)

PROJECT_TIME_ENTRY_FIELDS = GraphQLFragment(
    name="ProjectTimeEntryFields",
    on_type="ProjectTimeEntry",
    fields="""
    ...BaseFields
    projectId
    taskId
    userId
    userName
    description
    hours
    billableHours
    rate
    startTime
    endTime
    isBillable
    notes
    """,
    dependencies={"BaseFields"},
)

CONTRACT_RATE_FIELDS = GraphQLFragment(
    name="ContractRateFields",
    on_type="ContractRate",
    fields="""
    ...BaseFields
    contractId
    serviceType
    rateType
    rateAmount
    currency
    description
    effectiveDate
    endDate
    """,
    dependencies={"BaseFields"},
)

# Attachment fragments
ATTACHMENT_CORE_FIELDS = GraphQLFragment(
    name="AttachmentCoreFields",
    on_type="Attachment",
    fields="""
    ...BaseFields
    filename
    originalFilename
    fileSize
    mimeType
    entityType
    entityId
    attachmentType
    version
    uploadedBy
    uploadedByName
    isPublic
    """,
    dependencies={"BaseFields"},
)

# User fragments
USER_CORE_FIELDS = GraphQLFragment(
    name="UserCoreFields",
    on_type="User",
    fields="""
    ...BaseFields
    email
    firstName
    lastName
    role
    status
    department
    jobTitle
    isTechnician
    """,
    dependencies={"BaseFields"},
)

# Webhook fragments
WEBHOOK_CORE_FIELDS = GraphQLFragment(
    name="WebhookCoreFields",
    on_type="Webhook",
    fields="""
    ...BaseFields
    name
    url
    events
    status
    isActive
    """,
    dependencies={"BaseFields"},
)

ATTACHMENT_FULL_FIELDS = GraphQLFragment(
    name="AttachmentFullFields",
    on_type="Attachment",
    fields="""
    ...AttachmentCoreFields
    description
    url
    downloadUrl
    checksum
    metadata
    """,
    dependencies={"AttachmentCoreFields"},
)

ATTACHMENT_SUMMARY_FIELDS = GraphQLFragment(
    name="AttachmentSummaryFields",
    on_type="Attachment",
    fields="""
    id
    filename
    fileSize
    mimeType
    attachmentType
    version
    uploadedByName
    """,
    dependencies={"BaseFields"},
)


# Time Entry fragments
TIME_ENTRY_CORE_FIELDS = GraphQLFragment(
    name="TimeEntryCoreFields",
    on_type="TimeEntry",
    fields="""
    ...BaseFields
    userId
    description
    startTime
    endTime
    durationMinutes
    status
    entryType
    isBillable
    """,
    dependencies={"BaseFields"},
)

TIME_ENTRY_FULL_FIELDS = GraphQLFragment(
    name="TimeEntryFullFields",
    on_type="TimeEntry",
    fields="""
    ...TimeEntryCoreFields
    ticketId
    taskId
    projectId
    clientId
    hourlyRate
    totalAmount
    workCategory
    notes
    approvalNotes
    approvedBy
    approvedAt
    tags
    customFields
    """,
    dependencies={"TimeEntryCoreFields"},
)

TIME_ENTRY_SUMMARY_FIELDS = GraphQLFragment(
    name="TimeEntrySummaryFields",
    on_type="TimeEntry",
    fields="""
    id
    description
    startTime
    endTime
    durationMinutes
    status
    isBillable
    totalAmount
    createdAt
    """,
)

USER_FULL_FIELDS = GraphQLFragment(
    name="UserFullFields",
    on_type="User",
    fields="""
    ...UserCoreFields
    phone
    hourlyRate
    lastLoginTime
    timezone
    avatarUrl
    isPrimary
    notificationPreferences
    permissions
    tags
    customFields
    """,
    dependencies={"UserCoreFields"},
)

USER_SUMMARY_FIELDS = GraphQLFragment(
    name="UserSummaryFields",
    on_type="User",
    fields="""
    id
    email
    firstName
    lastName
    role
    status
    department
    isTechnician
    """,
)

WEBHOOK_FULL_FIELDS = GraphQLFragment(
    name="WebhookFullFields",
    on_type="Webhook",
    fields="""
    ...WebhookCoreFields
    description
    secret
    retryCount
    timeoutSeconds
    headers
    lastTriggered
    lastSuccess
    lastFailure
    failureCount
    successCount
    totalDeliveries
    contentType
    tags
    """,
    dependencies={"WebhookCoreFields"},
)

WEBHOOK_SUMMARY_FIELDS = GraphQLFragment(
    name="WebhookSummaryFields",
    on_type="Webhook",
    fields="""
    id
    name
    url
    status
    isActive
    lastTriggered
    successCount
    failureCount
    """,
)

WEBHOOK_DELIVERY_FIELDS = GraphQLFragment(
    name="WebhookDeliveryFields",
    on_type="WebhookDelivery",
    fields="""
    ...BaseFields
    webhookId
    eventType
    status
    url
    responseStatusCode
    attemptCount
    nextRetryAt
    deliveredAt
    errorMessage
    executionTimeMs
    """,
    dependencies={"BaseFields"},
)

TIMER_FIELDS = GraphQLFragment(
    name="TimerFields",
    on_type="Timer",
    fields="""
    ...BaseFields
    userId
    timeEntryId
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
    """,
    dependencies={"BaseFields"},
)

TIME_ENTRY_TEMPLATE_FIELDS = GraphQLFragment(
    name="TimeEntryTemplateFields",
    on_type="TimeEntryTemplate",
    fields="""
    ...BaseFields
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
    """,
    dependencies={"BaseFields"},
)

WEBHOOK_EVENT_RECORD_FIELDS = GraphQLFragment(
    name="WebhookEventRecordFields",
    on_type="WebhookEventRecord",
    fields="""
    ...BaseFields
    webhookId
    eventType
    resourceType
    resourceId
    triggeredAt
    deliveryId
    userId
    """,
    dependencies={"BaseFields"},
)

# Monitoring fragments (moved here to be available for ALL_FRAGMENTS)
MONITORING_AGENT_CORE_FIELDS = GraphQLFragment(
    name="MonitoringAgentCoreFields",
    on_type="MonitoringAgent",
    fields="""
    ...BaseFields
    name
    description
    status
    version
    hostId
    hostName
    ipAddress
    port
    lastSeen
    """,
    dependencies={"BaseFields"},
)

MONITORING_AGENT_FULL_FIELDS = GraphQLFragment(
    name="MonitoringAgentFullFields",
    on_type="MonitoringAgent",
    fields="""
    ...MonitoringAgentCoreFields
    apiKey
    config
    tags
    installedAt
    createdBy
    metadata
    """,
    dependencies={"MonitoringAgentCoreFields"},
)

MONITORING_AGENT_SUMMARY_FIELDS = GraphQLFragment(
    name="MonitoringAgentSummaryFields",
    on_type="MonitoringAgent",
    fields="""
    id
    name
    status
    hostName
    lastSeen
    """,
)

MONITORING_CHECK_CORE_FIELDS = GraphQLFragment(
    name="MonitoringCheckCoreFields",
    on_type="MonitoringCheck",
    fields="""
    ...BaseFields
    name
    description
    checkType
    target
    status
    enabled
    interval
    timeout
    retryCount
    agentId
    siteId
    assetId
    lastCheck
    nextCheck
    """,
    dependencies={"BaseFields"},
)

MONITORING_CHECK_FULL_FIELDS = GraphQLFragment(
    name="MonitoringCheckFullFields",
    on_type="MonitoringCheck",
    fields="""
    ...MonitoringCheckCoreFields
    config
    thresholds
    tags
    lastResult
    createdBy
    metadata
    """,
    dependencies={"MonitoringCheckCoreFields"},
)

MONITORING_CHECK_SUMMARY_FIELDS = GraphQLFragment(
    name="MonitoringCheckSummaryFields",
    on_type="MonitoringCheck",
    fields="""
    id
    name
    checkType
    status
    target
    lastCheck
    """,
)

MONITORING_ALERT_CORE_FIELDS = GraphQLFragment(
    name="MonitoringAlertCoreFields",
    on_type="MonitoringAlert",
    fields="""
    ...BaseFields
    name
    description
    checkId
    severity
    status
    triggeredAt
    acknowledgedAt
    acknowledgedBy
    resolvedAt
    resolvedBy
    alertCount
    lastAlert
    """,
    dependencies={"BaseFields"},
)

MONITORING_ALERT_FULL_FIELDS = GraphQLFragment(
    name="MonitoringAlertFullFields",
    on_type="MonitoringAlert",
    fields="""
    ...MonitoringAlertCoreFields
    condition
    notificationConfig
    suppressionRules
    escalationRules
    tags
    silencedUntil
    createdBy
    metadata
    """,
    dependencies={"MonitoringAlertCoreFields"},
)

MONITORING_ALERT_SUMMARY_FIELDS = GraphQLFragment(
    name="MonitoringAlertSummaryFields",
    on_type="MonitoringAlert",
    fields="""
    id
    name
    severity
    status
    triggeredAt
    alertCount
    """,
)

MONITORING_METRIC_CORE_FIELDS = GraphQLFragment(
    name="MonitoringMetricCoreFields",
    on_type="MonitoringMetric",
    fields="""
    ...BaseFields
    name
    description
    metricType
    unit
    value
    timestamp
    agentId
    checkId
    assetId
    siteId
    """,
    dependencies={"BaseFields"},
)

MONITORING_METRIC_FULL_FIELDS = GraphQLFragment(
    name="MonitoringMetricFullFields",
    on_type="MonitoringMetric",
    fields="""
    ...MonitoringMetricCoreFields
    labels
    retentionPeriod
    aggregationConfig
    tags
    metadata
    """,
    dependencies={"MonitoringMetricCoreFields"},
)

MONITORING_METRIC_SUMMARY_FIELDS = GraphQLFragment(
    name="MonitoringMetricSummaryFields",
    on_type="MonitoringMetric",
    fields="""
    id
    name
    value
    unit
    timestamp
    """,
)

# Fragment collections for easy access
ALL_FRAGMENTS = {
    fragment.name: fragment
    for fragment in [
        BASE_FIELDS,
        PAGINATION_INFO,
        CLIENT_CORE_FIELDS,
        CLIENT_FULL_FIELDS,
        CLIENT_SUMMARY_FIELDS,
        CONTACT_CORE_FIELDS,
        CONTACT_FULL_FIELDS,
        SITE_CORE_FIELDS,
        SITE_FULL_FIELDS,
        ASSET_CORE_FIELDS,
        ASSET_FULL_FIELDS,
        ASSET_SUMMARY_FIELDS,
        TICKET_CORE_FIELDS,
        TICKET_FULL_FIELDS,
        TICKET_SUMMARY_FIELDS,
        TICKET_COMMENT_FIELDS,
        PROJECT_CORE_FIELDS,
        PROJECT_FULL_FIELDS,
        PROJECT_SUMMARY_FIELDS,
        PROJECT_MILESTONE_FIELDS,
        PROJECT_TASK_CORE_FIELDS,
        PROJECT_TASK_FULL_FIELDS,
        PROJECT_TIME_ENTRY_FIELDS,
        TASK_CORE_FIELDS,
        TASK_FULL_FIELDS,
        TASK_SUMMARY_FIELDS,
        TASK_COMMENT_FIELDS,
        TASK_TIME_ENTRY_FIELDS,
        TASK_TEMPLATE_FIELDS,
        COMMENT_CORE_FIELDS,
        COMMENT_FULL_FIELDS,
        COMMENT_SUMMARY_FIELDS,
        COMMENT_ATTACHMENT_FIELDS,
        KB_COLLECTION_CORE_FIELDS,
        KB_COLLECTION_FULL_FIELDS,
        KB_ARTICLE_CORE_FIELDS,
        KB_ARTICLE_FULL_FIELDS,
        KB_ARTICLE_SUMMARY_FIELDS,
        CONTRACT_CORE_FIELDS,
        CONTRACT_FULL_FIELDS,
        CONTRACT_SUMMARY_FIELDS,
        CONTRACT_SLA_FIELDS,
        CONTRACT_RATE_FIELDS,
        ATTACHMENT_CORE_FIELDS,
        ATTACHMENT_FULL_FIELDS,
        ATTACHMENT_SUMMARY_FIELDS,
        USER_CORE_FIELDS,
        USER_FULL_FIELDS,
        USER_SUMMARY_FIELDS,
        WEBHOOK_CORE_FIELDS,
        WEBHOOK_FULL_FIELDS,
        WEBHOOK_SUMMARY_FIELDS,
        WEBHOOK_DELIVERY_FIELDS,
        WEBHOOK_EVENT_RECORD_FIELDS,
        TIME_ENTRY_CORE_FIELDS,
        TIME_ENTRY_FULL_FIELDS,
        TIME_ENTRY_SUMMARY_FIELDS,
        TIMER_FIELDS,
        TIME_ENTRY_TEMPLATE_FIELDS,
        MONITORING_AGENT_CORE_FIELDS,
        MONITORING_AGENT_FULL_FIELDS,
        MONITORING_AGENT_SUMMARY_FIELDS,
        MONITORING_CHECK_CORE_FIELDS,
        MONITORING_CHECK_FULL_FIELDS,
        MONITORING_CHECK_SUMMARY_FIELDS,
        MONITORING_ALERT_CORE_FIELDS,
        MONITORING_ALERT_FULL_FIELDS,
        MONITORING_ALERT_SUMMARY_FIELDS,
        MONITORING_METRIC_CORE_FIELDS,
        MONITORING_METRIC_FULL_FIELDS,
        MONITORING_METRIC_SUMMARY_FIELDS,
    ]
}

CLIENT_FRAGMENTS = {
    "core": CLIENT_CORE_FIELDS,
    "full": CLIENT_FULL_FIELDS,
    "summary": CLIENT_SUMMARY_FIELDS,
}

CONTACT_FRAGMENTS = {
    "core": CONTACT_CORE_FIELDS,
    "full": CONTACT_FULL_FIELDS,
}

SITE_FRAGMENTS = {
    "core": SITE_CORE_FIELDS,
    "full": SITE_FULL_FIELDS,
}

ASSET_FRAGMENTS = {
    "core": ASSET_CORE_FIELDS,
    "full": ASSET_FULL_FIELDS,
    "summary": ASSET_SUMMARY_FIELDS,
}

TICKET_FRAGMENTS = {
    "core": TICKET_CORE_FIELDS,
    "full": TICKET_FULL_FIELDS,
    "summary": TICKET_SUMMARY_FIELDS,
    "comment": TICKET_COMMENT_FIELDS,
}

PROJECT_FRAGMENTS = {
    "core": PROJECT_CORE_FIELDS,
    "full": PROJECT_FULL_FIELDS,
    "summary": PROJECT_SUMMARY_FIELDS,
    "milestone": PROJECT_MILESTONE_FIELDS,
    "task_core": PROJECT_TASK_CORE_FIELDS,
    "task_full": PROJECT_TASK_FULL_FIELDS,
    "time_entry": PROJECT_TIME_ENTRY_FIELDS,
}

TASK_FRAGMENTS = {
    "core": TASK_CORE_FIELDS,
    "full": TASK_FULL_FIELDS,
    "summary": TASK_SUMMARY_FIELDS,
    "comment": TASK_COMMENT_FIELDS,
    "time_entry": TASK_TIME_ENTRY_FIELDS,
    "template": TASK_TEMPLATE_FIELDS,
}

KB_FRAGMENTS = {
    "collection_core": KB_COLLECTION_CORE_FIELDS,
    "collection_full": KB_COLLECTION_FULL_FIELDS,
    "article_core": KB_ARTICLE_CORE_FIELDS,
    "article_full": KB_ARTICLE_FULL_FIELDS,
    "article_summary": KB_ARTICLE_SUMMARY_FIELDS,
}

CONTRACT_FRAGMENTS = {
    "core": CONTRACT_CORE_FIELDS,
    "full": CONTRACT_FULL_FIELDS,
    "summary": CONTRACT_SUMMARY_FIELDS,
    "sla": CONTRACT_SLA_FIELDS,
    "rate": CONTRACT_RATE_FIELDS,
}

COMMENT_FRAGMENTS = {
    "core": COMMENT_CORE_FIELDS,
    "full": COMMENT_FULL_FIELDS,
    "summary": COMMENT_SUMMARY_FIELDS,
    "attachment": COMMENT_ATTACHMENT_FIELDS,
}

ATTACHMENT_FRAGMENTS = {
    "core": ATTACHMENT_CORE_FIELDS,
    "full": ATTACHMENT_FULL_FIELDS,
    "summary": ATTACHMENT_SUMMARY_FIELDS,
}

USER_FRAGMENTS = {
    "core": USER_CORE_FIELDS,
    "full": USER_FULL_FIELDS,
    "summary": USER_SUMMARY_FIELDS,
}

WEBHOOK_FRAGMENTS = {
    "core": WEBHOOK_CORE_FIELDS,
    "full": WEBHOOK_FULL_FIELDS,
    "summary": WEBHOOK_SUMMARY_FIELDS,
    "delivery": WEBHOOK_DELIVERY_FIELDS,
    "event_record": WEBHOOK_EVENT_RECORD_FIELDS,
}

TIME_ENTRY_FRAGMENTS = {
    "core": TIME_ENTRY_CORE_FIELDS,
    "full": TIME_ENTRY_FULL_FIELDS,
    "summary": TIME_ENTRY_SUMMARY_FIELDS,
}

TIMER_FRAGMENTS = {
    "fields": TIMER_FIELDS,
}

TIME_ENTRY_TEMPLATE_FRAGMENTS = {
    "fields": TIME_ENTRY_TEMPLATE_FIELDS,
}


def resolve_dependencies(fragment_names: Set[str]) -> Set[str]:
    """Resolve fragment dependencies to get all required fragments.

    Args:
        fragment_names: Set of fragment names to resolve

    Returns:
        Set of all fragment names including dependencies
    """
    resolved = set()
    to_resolve = set(fragment_names)

    while to_resolve:
        current = to_resolve.pop()
        if current in resolved:
            continue

        resolved.add(current)

        if current in ALL_FRAGMENTS:
            dependencies = ALL_FRAGMENTS[current].dependencies
            to_resolve.update(dep for dep in dependencies if dep not in resolved)

    return resolved


def build_fragments_string(fragment_names: Set[str]) -> str:
    """Build a string containing all required fragment definitions.

    Args:
        fragment_names: Set of fragment names to include

    Returns:
        String containing all fragment definitions
    """
    resolved_names = resolve_dependencies(fragment_names)

    # Sort to ensure consistent output
    sorted_names = sorted(resolved_names)

    fragments = []
    for name in sorted_names:
        if name in ALL_FRAGMENTS:
            fragments.append(str(ALL_FRAGMENTS[name]))

    return "\n\n".join(fragments)


def get_fragment_spreads(fragment_names: Set[str]) -> str:
    """Get fragment spreads for use in queries.

    Args:
        fragment_names: Set of fragment names

    Returns:
        String containing fragment spreads
    """
    spreads = []
    for name in sorted(fragment_names):
        if name in ALL_FRAGMENTS:
            spreads.append(ALL_FRAGMENTS[name].get_spread())

    return "\n".join(spreads)


def create_query_with_fragments(query: str, fragment_names: Set[str]) -> str:
    """Create a complete GraphQL query with fragments.

    Args:
        query: The main query string
        fragment_names: Set of fragment names to include

    Returns:
        Complete GraphQL query with fragment definitions
    """
    fragments_string = build_fragments_string(fragment_names)

    if fragments_string:
        return f"{query}\n\n{fragments_string}"
    else:
        return query


# Convenience functions for common fragment combinations
def get_client_fields(detail_level: str = "core") -> Set[str]:
    """Get client fragment names for specified detail level.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        Set of fragment names
    """
    mapping = {
        "summary": {"ClientSummaryFields"},
        "core": {"ClientCoreFields"},
        "full": {"ClientFullFields"},
    }
    return mapping.get(detail_level, {"ClientCoreFields"})


def get_ticket_fields(detail_level: str = "core", include_comments: bool = False) -> Set[str]:
    """Get ticket fragment names for specified detail level.

    Args:
        detail_level: Level of detail (summary, core, full)
        include_comments: Whether to include comment fields

    Returns:
        Set of fragment names
    """
    mapping = {
        "summary": {"TicketSummaryFields"},
        "core": {"TicketCoreFields"},
        "full": {"TicketFullFields"},
    }

    fragments = mapping.get(detail_level, {"TicketCoreFields"})

    if include_comments:
        fragments.add("TicketCommentFields")

    return fragments


def get_asset_fields(detail_level: str = "core") -> Set[str]:
    """Get asset fragment names for specified detail level.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        Set of fragment names
    """
    mapping = {
        "summary": {"AssetSummaryFields"},
        "core": {"AssetCoreFields"},
        "full": {"AssetFullFields"},
    }
    return mapping.get(detail_level, {"AssetCoreFields"})


def get_project_fields(
    detail_level: str = "core",
    include_milestones: bool = False,
    include_tasks: bool = False,
    include_time_entries: bool = False,
    task_detail: str = "core",
) -> Set[str]:
    """Get project fragment names for specified detail level.

    Args:
        detail_level: Level of detail for projects (summary, core, full)
        include_milestones: Whether to include milestone fields
        include_tasks: Whether to include task fields
        include_time_entries: Whether to include time entry fields
        task_detail: Level of detail for tasks (core, full)

    Returns:
        Set of fragment names
    """
    project_mapping = {
        "summary": "ProjectSummaryFields",
        "core": "ProjectCoreFields",
        "full": "ProjectFullFields",
    }

    fragments = set()

    if detail_level in project_mapping:
        fragments.add(project_mapping[detail_level])

    if include_milestones:
        fragments.add("ProjectMilestoneFields")

    if include_tasks:
        task_mapping = {
            "core": "ProjectTaskCoreFields",
            "full": "ProjectTaskFullFields",
        }
        if task_detail in task_mapping:
            fragments.add(task_mapping[task_detail])

    if include_time_entries:
        fragments.add("ProjectTimeEntryFields")

    return fragments


def get_task_fields(
    detail_level: str = "core",
    include_comments: bool = False,
    include_time_entries: bool = False,
    include_template: bool = False,
) -> Set[str]:
    """Get task fragment names for specified detail level.

    Args:
        detail_level: Level of detail (summary, core, full)
        include_comments: Whether to include comment fields
        include_time_entries: Whether to include time entry fields
        include_template: Whether to include template fields

    Returns:
        Set of fragment names
    """
    mapping = {
        "summary": {"TaskSummaryFields"},
        "core": {"TaskCoreFields"},
        "full": {"TaskFullFields"},
    }

    fragments = mapping.get(detail_level, {"TaskCoreFields"})

    if include_comments:
        fragments.add("TaskCommentFields")

    if include_time_entries:
        fragments.add("TaskTimeEntryFields")

    if include_template:
        fragments.add("TaskTemplateFields")

    return fragments


def get_kb_fields(collection_detail: str = "core", article_detail: str = "core") -> Set[str]:
    """Get knowledge base fragment names for specified detail levels.

    Args:
        collection_detail: Level of detail for collections (core, full)
        article_detail: Level of detail for articles (summary, core, full)

    Returns:
        Set of fragment names
    """
    collection_mapping = {
        "core": "KBCollectionCoreFields",
        "full": "KBCollectionFullFields",
    }

    article_mapping = {
        "summary": "KBArticleSummaryFields",
        "core": "KBArticleCoreFields",
        "full": "KBArticleFullFields",
    }

    fragments = set()

    if collection_detail in collection_mapping:
        fragments.add(collection_mapping[collection_detail])

    if article_detail in article_mapping:
        fragments.add(article_mapping[article_detail])

    return fragments


def get_contract_fields(
    detail_level: str = "core", include_slas: bool = False, include_rates: bool = False
) -> Set[str]:
    """Get contract fragment names for specified detail level.

    Args:
        detail_level: Level of detail (summary, core, full)
        include_slas: Whether to include SLA fields
        include_rates: Whether to include rate fields

    Returns:
        Set of fragment names
    """
    mapping = {
        "summary": {"ContractSummaryFields"},
        "core": {"ContractCoreFields"},
        "full": {"ContractFullFields"},
    }

    fragments = mapping.get(detail_level, {"ContractCoreFields"})

    if include_slas:
        fragments.add("ContractSLAFields")

    if include_rates:
        fragments.add("ContractRateFields")

    return fragments


def get_comment_fields(detail_level: str = "core", include_attachments: bool = False) -> Set[str]:
    """Get comment fragment names for specified detail level.

    Args:
        detail_level: Level of detail (summary, core, full)
        include_attachments: Whether to include attachment fields

    Returns:
        Set of fragment names
    """
    mapping = {
        "summary": {"CommentSummaryFields"},
        "core": {"CommentCoreFields"},
        "full": {"CommentFullFields"},
    }

    fragments = mapping.get(detail_level, {"CommentCoreFields"})

    if include_attachments:
        fragments.add("CommentAttachmentFields")

    return fragments


def get_attachment_fields(detail_level: str = "core") -> Set[str]:
    """Get attachment fragment names for specified detail level.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        Set of fragment names
    """
    mapping = {
        "summary": {"AttachmentSummaryFields"},
        "core": {"AttachmentCoreFields"},
        "full": {"AttachmentFullFields"},
    }

    return mapping.get(detail_level, {"AttachmentCoreFields"})


def get_time_entry_fields(detail_level: str = "core") -> Set[str]:
    """Get time entry fragment names for specified detail level.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        Set of fragment names
    """
    mapping = {
        "summary": {"TimeEntrySummaryFields"},
        "core": {"TimeEntryCoreFields"},
        "full": {"TimeEntryFullFields"},
    }
    return mapping.get(detail_level, {"TimeEntryCoreFields"})


def get_user_fields(detail_level: str = "core") -> Set[str]:
    """Get user fragment names for specified detail level.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        Set of fragment names
    """
    mapping = {
        "summary": {"UserSummaryFields"},
        "core": {"UserCoreFields"},
        "full": {"UserFullFields"},
    }

    return mapping.get(detail_level, {"UserCoreFields"})


def get_timer_fields() -> Set[str]:
    """Get timer fragment names.

    Returns:
        Set of fragment names
    """
    return {"TimerFields"}


def get_webhook_fields(
    detail_level: str = "core",
    include_deliveries: bool = False,
    include_events: bool = False,
) -> Set[str]:
    """Get webhook fragment names for specified detail level.

    Args:
        detail_level: Level of detail (summary, core, full)
        include_deliveries: Whether to include delivery fields
        include_events: Whether to include event record fields

    Returns:
        Set of fragment names
    """
    mapping = {
        "summary": {"WebhookSummaryFields"},
        "core": {"WebhookCoreFields"},
        "full": {"WebhookFullFields"},
    }

    fragments = mapping.get(detail_level, {"WebhookCoreFields"})

    if include_deliveries:
        fragments.add("WebhookDeliveryFields")

    if include_events:
        fragments.add("WebhookEventRecordFields")

    return fragments


def get_time_entry_template_fields() -> Set[str]:
    """Get time entry template fragment names.

    Returns:
        Set of fragment names
    """
    return {"TimeEntryTemplateFields"}


# Monitoring fragment collections for easy access
MONITORING_FRAGMENTS = {
    # Agent fragments
    "core": MONITORING_AGENT_CORE_FIELDS,
    "full": MONITORING_AGENT_FULL_FIELDS,
    "summary": MONITORING_AGENT_SUMMARY_FIELDS,
    # Check fragments
    "check_core": MONITORING_CHECK_CORE_FIELDS,
    "check_full": MONITORING_CHECK_FULL_FIELDS,
    "check_summary": MONITORING_CHECK_SUMMARY_FIELDS,
    # Alert fragments
    "alert_core": MONITORING_ALERT_CORE_FIELDS,
    "alert_full": MONITORING_ALERT_FULL_FIELDS,
    "alert_summary": MONITORING_ALERT_SUMMARY_FIELDS,
    # Metric fragments
    "metric_core": MONITORING_METRIC_CORE_FIELDS,
    "metric_full": MONITORING_METRIC_FULL_FIELDS,
    "metric_summary": MONITORING_METRIC_SUMMARY_FIELDS,
}


def get_monitoring_agent_fields(detail_level: str = "core") -> Set[str]:
    """Get monitoring agent fragment names for specified detail level.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        Set of fragment names
    """
    mapping = {
        "summary": {"MonitoringAgentSummaryFields"},
        "core": {"MonitoringAgentCoreFields"},
        "full": {"MonitoringAgentFullFields"},
    }

    return mapping.get(detail_level, {"MonitoringAgentCoreFields"})


def get_monitoring_check_fields(detail_level: str = "core") -> Set[str]:
    """Get monitoring check fragment names for specified detail level.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        Set of fragment names
    """
    mapping = {
        "summary": {"MonitoringCheckSummaryFields"},
        "core": {"MonitoringCheckCoreFields"},
        "full": {"MonitoringCheckFullFields"},
    }

    return mapping.get(detail_level, {"MonitoringCheckCoreFields"})


def get_monitoring_alert_fields(detail_level: str = "core") -> Set[str]:
    """Get monitoring alert fragment names for specified detail level.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        Set of fragment names
    """
    mapping = {
        "summary": {"MonitoringAlertSummaryFields"},
        "core": {"MonitoringAlertCoreFields"},
        "full": {"MonitoringAlertFullFields"},
    }

    return mapping.get(detail_level, {"MonitoringAlertCoreFields"})


def get_monitoring_metric_fields(detail_level: str = "core") -> Set[str]:
    """Get monitoring metric fragment names for specified detail level.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        Set of fragment names
    """
    mapping = {
        "summary": {"MonitoringMetricSummaryFields"},
        "core": {"MonitoringMetricCoreFields"},
        "full": {"MonitoringMetricFullFields"},
    }

    return mapping.get(detail_level, {"MonitoringMetricCoreFields"})


# Monitoring fragments (defined again to ensure they're available)
# Note: These fragments are defined here because they weren't being properly included
# when defined earlier in the file due to an unknown issue.

MONITORING_AGENT_CORE_FIELDS_FIXED = GraphQLFragment(
    name="MonitoringAgentCoreFields",
    on_type="MonitoringAgent",
    fields="""
    ...BaseFields
    name
    description
    status
    version
    hostId
    hostName
    ipAddress
    port
    lastSeen
    """,
    dependencies={"BaseFields"},
)

MONITORING_AGENT_FULL_FIELDS_FIXED = GraphQLFragment(
    name="MonitoringAgentFullFields",
    on_type="MonitoringAgent",
    fields="""
    ...MonitoringAgentCoreFields
    apiKey
    config
    tags
    installedAt
    createdBy
    metadata
    """,
    dependencies={"MonitoringAgentCoreFields"},
)

MONITORING_AGENT_SUMMARY_FIELDS_FIXED = GraphQLFragment(
    name="MonitoringAgentSummaryFields",
    on_type="MonitoringAgent",
    fields="""
    id
    name
    status
    hostName
    lastSeen
    """,
)

MONITORING_CHECK_CORE_FIELDS_FIXED = GraphQLFragment(
    name="MonitoringCheckCoreFields",
    on_type="MonitoringCheck",
    fields="""
    ...BaseFields
    name
    description
    checkType
    target
    status
    enabled
    interval
    timeout
    retryCount
    agentId
    siteId
    assetId
    lastCheck
    nextCheck
    """,
    dependencies={"BaseFields"},
)

MONITORING_CHECK_FULL_FIELDS_FIXED = GraphQLFragment(
    name="MonitoringCheckFullFields",
    on_type="MonitoringCheck",
    fields="""
    ...MonitoringCheckCoreFields
    config
    thresholds
    tags
    lastResult
    createdBy
    metadata
    """,
    dependencies={"MonitoringCheckCoreFields"},
)

MONITORING_CHECK_SUMMARY_FIELDS_FIXED = GraphQLFragment(
    name="MonitoringCheckSummaryFields",
    on_type="MonitoringCheck",
    fields="""
    id
    name
    checkType
    status
    target
    lastCheck
    """,
)

MONITORING_ALERT_CORE_FIELDS_FIXED = GraphQLFragment(
    name="MonitoringAlertCoreFields",
    on_type="MonitoringAlert",
    fields="""
    ...BaseFields
    name
    description
    checkId
    severity
    status
    triggeredAt
    acknowledgedAt
    acknowledgedBy
    resolvedAt
    resolvedBy
    alertCount
    lastAlert
    """,
    dependencies={"BaseFields"},
)

MONITORING_ALERT_FULL_FIELDS_FIXED = GraphQLFragment(
    name="MonitoringAlertFullFields",
    on_type="MonitoringAlert",
    fields="""
    ...MonitoringAlertCoreFields
    condition
    notificationConfig
    suppressionRules
    escalationRules
    tags
    silencedUntil
    createdBy
    metadata
    """,
    dependencies={"MonitoringAlertCoreFields"},
)

MONITORING_ALERT_SUMMARY_FIELDS_FIXED = GraphQLFragment(
    name="MonitoringAlertSummaryFields",
    on_type="MonitoringAlert",
    fields="""
    id
    name
    severity
    status
    triggeredAt
    alertCount
    """,
)

MONITORING_METRIC_CORE_FIELDS_FIXED = GraphQLFragment(
    name="MonitoringMetricCoreFields",
    on_type="MonitoringMetric",
    fields="""
    ...BaseFields
    name
    description
    metricType
    unit
    value
    timestamp
    agentId
    checkId
    assetId
    siteId
    """,
    dependencies={"BaseFields"},
)

MONITORING_METRIC_FULL_FIELDS_FIXED = GraphQLFragment(
    name="MonitoringMetricFullFields",
    on_type="MonitoringMetric",
    fields="""
    ...MonitoringMetricCoreFields
    labels
    retentionPeriod
    aggregationConfig
    tags
    metadata
    """,
    dependencies={"MonitoringMetricCoreFields"},
)

MONITORING_METRIC_SUMMARY_FIELDS_FIXED = GraphQLFragment(
    name="MonitoringMetricSummaryFields",
    on_type="MonitoringMetric",
    fields="""
    id
    name
    value
    unit
    timestamp
    """,
)

# Now update ALL_FRAGMENTS to include the monitoring fragments
ALL_FRAGMENTS.update(
    {
        "MonitoringAgentCoreFields": MONITORING_AGENT_CORE_FIELDS_FIXED,
        "MonitoringAgentFullFields": MONITORING_AGENT_FULL_FIELDS_FIXED,
        "MonitoringAgentSummaryFields": MONITORING_AGENT_SUMMARY_FIELDS_FIXED,
        "MonitoringCheckCoreFields": MONITORING_CHECK_CORE_FIELDS_FIXED,
        "MonitoringCheckFullFields": MONITORING_CHECK_FULL_FIELDS_FIXED,
        "MonitoringCheckSummaryFields": MONITORING_CHECK_SUMMARY_FIELDS_FIXED,
        "MonitoringAlertCoreFields": MONITORING_ALERT_CORE_FIELDS_FIXED,
        "MonitoringAlertFullFields": MONITORING_ALERT_FULL_FIELDS_FIXED,
        "MonitoringAlertSummaryFields": MONITORING_ALERT_SUMMARY_FIELDS_FIXED,
        "MonitoringMetricCoreFields": MONITORING_METRIC_CORE_FIELDS_FIXED,
        "MonitoringMetricFullFields": MONITORING_METRIC_FULL_FIELDS_FIXED,
        "MonitoringMetricSummaryFields": MONITORING_METRIC_SUMMARY_FIELDS_FIXED,
    }
)

# Create module-level aliases to match the expected naming
MONITORING_AGENT_CORE_FIELDS = MONITORING_AGENT_CORE_FIELDS_FIXED
MONITORING_AGENT_FULL_FIELDS = MONITORING_AGENT_FULL_FIELDS_FIXED
MONITORING_AGENT_SUMMARY_FIELDS = MONITORING_AGENT_SUMMARY_FIELDS_FIXED
MONITORING_CHECK_CORE_FIELDS = MONITORING_CHECK_CORE_FIELDS_FIXED
MONITORING_CHECK_FULL_FIELDS = MONITORING_CHECK_FULL_FIELDS_FIXED
MONITORING_CHECK_SUMMARY_FIELDS = MONITORING_CHECK_SUMMARY_FIELDS_FIXED
MONITORING_ALERT_CORE_FIELDS = MONITORING_ALERT_CORE_FIELDS_FIXED
MONITORING_ALERT_FULL_FIELDS = MONITORING_ALERT_FULL_FIELDS_FIXED
MONITORING_ALERT_SUMMARY_FIELDS = MONITORING_ALERT_SUMMARY_FIELDS_FIXED
MONITORING_METRIC_CORE_FIELDS = MONITORING_METRIC_CORE_FIELDS_FIXED
MONITORING_METRIC_FULL_FIELDS = MONITORING_METRIC_FULL_FIELDS_FIXED
MONITORING_METRIC_SUMMARY_FIELDS = MONITORING_METRIC_SUMMARY_FIELDS_FIXED
