# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Automation manager for SuperOps API operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..exceptions import SuperOpsAPIError, SuperOpsValidationError
from ..graphql.types import (
    AutomationAction,
    AutomationActionInput,
    AutomationExecutionInput,
    AutomationJob,
    AutomationJobStatus,
    AutomationSchedule,
    AutomationScheduleInput,
    AutomationTrigger,
    AutomationTriggerInput,
    AutomationWorkflow,
    AutomationWorkflowStatus,
    ScheduleType,
)

if TYPE_CHECKING:
    from ..client import SuperOpsClient
from .base import ResourceManager


class AutomationManager(ResourceManager[AutomationWorkflow]):
    """Manager for automation workflow operations.

    Provides high-level methods for managing SuperOps automation workflows including
    CRUD operations, job execution, scheduling, template management, and workflow-specific features.
    """

    def __init__(self, client: "SuperOpsClient"):
        """Initialize the automation manager.

        Args:
            client: SuperOps client instance
        """
        super().__init__(client, AutomationWorkflow, "automationWorkflow")

    # Workflow Management

    async def get_by_status(
        self,
        status: AutomationWorkflowStatus,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get workflows filtered by status.

        Args:
            status: Workflow status to filter by
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[AutomationWorkflow]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not isinstance(status, AutomationWorkflowStatus):
            raise SuperOpsValidationError("Status must be an AutomationWorkflowStatus enum")

        self.logger.debug(f"Getting automation workflows with status: {status.value}")

        filters = {"status": status.value}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
        )

    async def get_templates(
        self,
        category: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        """Get automation workflow templates.

        Args:
            category: Optional template category filter
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            Dictionary containing 'items' (List[AutomationWorkflow]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Getting automation workflow templates")

        filters = {"is_template": True}
        if category:
            filters["template_category"] = category

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by="name",
            sort_order="asc",
        )

    async def create_from_template(
        self,
        template_id: str,
        name: str,
        template_variables: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> AutomationWorkflow:
        """Create a workflow from a template.

        Args:
            template_id: The template ID
            name: Name for the new workflow
            template_variables: Template variable values
            **kwargs: Additional workflow properties

        Returns:
            Created workflow instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not template_id or not isinstance(template_id, str):
            raise SuperOpsValidationError("Template ID must be a non-empty string")
        if not name or not isinstance(name, str):
            raise SuperOpsValidationError("Workflow name must be a non-empty string")

        self.logger.debug(f"Creating workflow from template {template_id}")

        data = {
            "name": name,
            "template_id": template_id,
            "template_variables": template_variables or {},
            **kwargs,
        }

        return await self.create(data)

    async def activate_workflow(self, workflow_id: str) -> AutomationWorkflow:
        """Activate a workflow.

        Args:
            workflow_id: The workflow ID

        Returns:
            Updated workflow instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not workflow_id or not isinstance(workflow_id, str):
            raise SuperOpsValidationError("Workflow ID must be a non-empty string")

        self.logger.debug(f"Activating workflow {workflow_id}")

        return await self.update(workflow_id, {"status": AutomationWorkflowStatus.ACTIVE.value})

    async def deactivate_workflow(self, workflow_id: str) -> AutomationWorkflow:
        """Deactivate a workflow.

        Args:
            workflow_id: The workflow ID

        Returns:
            Updated workflow instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not workflow_id or not isinstance(workflow_id, str):
            raise SuperOpsValidationError("Workflow ID must be a non-empty string")

        self.logger.debug(f"Deactivating workflow {workflow_id}")

        return await self.update(workflow_id, {"status": AutomationWorkflowStatus.INACTIVE.value})

    # Action Management

    async def add_action(self, action_input: AutomationActionInput) -> AutomationAction:
        """Add an action to a workflow.

        Args:
            action_input: Action creation data

        Returns:
            Created action instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug(f"Adding action to workflow {action_input.workflow_id}")

        mutation = """
            mutation AddAutomationAction($input: AutomationActionInput!) {
                addAutomationAction(input: $input) {
                    id
                    name
                    actionType
                    config
                    orderIndex
                    isEnabled
                    condition
                    timeoutSeconds
                    retryAttempts
                    retryDelaySeconds
                    createdAt
                    updatedAt
                }
            }
        """

        variables = {"input": self._serialize_action_input(action_input)}

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when adding action", 500, response)

        action_data = response["data"].get("addAutomationAction")
        if not action_data:
            raise SuperOpsAPIError("No action data in response", 500, response)

        return AutomationAction.from_dict(action_data)

    async def update_action(
        self, action_id: str, action_input: AutomationActionInput
    ) -> AutomationAction:
        """Update an automation action.

        Args:
            action_id: The action ID
            action_input: Updated action data

        Returns:
            Updated action instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not action_id or not isinstance(action_id, str):
            raise SuperOpsValidationError("Action ID must be a non-empty string")

        self.logger.debug(f"Updating action {action_id}")

        mutation = """
            mutation UpdateAutomationAction($id: ID!, $input: AutomationActionInput!) {
                updateAutomationAction(id: $id, input: $input) {
                    id
                    name
                    actionType
                    config
                    orderIndex
                    isEnabled
                    condition
                    timeoutSeconds
                    retryAttempts
                    retryDelaySeconds
                    createdAt
                    updatedAt
                }
            }
        """

        variables = {"id": action_id, "input": self._serialize_action_input(action_input)}

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when updating action", 500, response)

        action_data = response["data"].get("updateAutomationAction")
        if not action_data:
            raise SuperOpsAPIError("No action data in response", 500, response)

        return AutomationAction.from_dict(action_data)

    async def remove_action(self, action_id: str) -> bool:
        """Remove an action from a workflow.

        Args:
            action_id: The action ID

        Returns:
            True if removal was successful

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not action_id or not isinstance(action_id, str):
            raise SuperOpsValidationError("Action ID must be a non-empty string")

        self.logger.debug(f"Removing action {action_id}")

        mutation = """
            mutation RemoveAutomationAction($id: ID!) {
                removeAutomationAction(id: $id) {
                    success
                    message
                }
            }
        """

        variables = {"id": action_id}

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when removing action", 500, response)

        result = response["data"].get("removeAutomationAction")
        if not result:
            raise SuperOpsAPIError("No result in response", 500, response)

        return result.get("success", False)

    # Trigger Management

    async def add_trigger(self, trigger_input: AutomationTriggerInput) -> AutomationTrigger:
        """Add a trigger to a workflow.

        Args:
            trigger_input: Trigger creation data

        Returns:
            Created trigger instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug(f"Adding trigger to workflow {trigger_input.workflow_id}")

        mutation = """
            mutation AddAutomationTrigger($input: AutomationTriggerInput!) {
                addAutomationTrigger(input: $input) {
                    id
                    name
                    triggerType
                    config
                    conditions
                    isEnabled
                    workflowId
                    createdAt
                    updatedAt
                }
            }
        """

        variables = {"input": self._serialize_trigger_input(trigger_input)}

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when adding trigger", 500, response)

        trigger_data = response["data"].get("addAutomationTrigger")
        if not trigger_data:
            raise SuperOpsAPIError("No trigger data in response", 500, response)

        return AutomationTrigger.from_dict(trigger_data)

    async def update_trigger(
        self, trigger_id: str, trigger_input: AutomationTriggerInput
    ) -> AutomationTrigger:
        """Update an automation trigger.

        Args:
            trigger_id: The trigger ID
            trigger_input: Updated trigger data

        Returns:
            Updated trigger instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not trigger_id or not isinstance(trigger_id, str):
            raise SuperOpsValidationError("Trigger ID must be a non-empty string")

        self.logger.debug(f"Updating trigger {trigger_id}")

        mutation = """
            mutation UpdateAutomationTrigger($id: ID!, $input: AutomationTriggerInput!) {
                updateAutomationTrigger(id: $id, input: $input) {
                    id
                    name
                    triggerType
                    config
                    conditions
                    isEnabled
                    workflowId
                    createdAt
                    updatedAt
                }
            }
        """

        variables = {"id": trigger_id, "input": self._serialize_trigger_input(trigger_input)}

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when updating trigger", 500, response)

        trigger_data = response["data"].get("updateAutomationTrigger")
        if not trigger_data:
            raise SuperOpsAPIError("No trigger data in response", 500, response)

        return AutomationTrigger.from_dict(trigger_data)

    async def remove_trigger(self, trigger_id: str) -> bool:
        """Remove a trigger from a workflow.

        Args:
            trigger_id: The trigger ID

        Returns:
            True if removal was successful

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not trigger_id or not isinstance(trigger_id, str):
            raise SuperOpsValidationError("Trigger ID must be a non-empty string")

        self.logger.debug(f"Removing trigger {trigger_id}")

        mutation = """
            mutation RemoveAutomationTrigger($id: ID!) {
                removeAutomationTrigger(id: $id) {
                    success
                    message
                }
            }
        """

        variables = {"id": trigger_id}

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when removing trigger", 500, response)

        result = response["data"].get("removeAutomationTrigger")
        if not result:
            raise SuperOpsAPIError("No result in response", 500, response)

        return result.get("success", False)

    # Schedule Management

    async def add_schedule(self, schedule_input: AutomationScheduleInput) -> AutomationSchedule:
        """Add a schedule to a trigger.

        Args:
            schedule_input: Schedule creation data

        Returns:
            Created schedule instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug(f"Adding schedule to trigger {schedule_input.trigger_id}")

        # Validate schedule input
        self._validate_schedule_input(schedule_input)

        mutation = """
            mutation AddAutomationSchedule($input: AutomationScheduleInput!) {
                addAutomationSchedule(input: $input) {
                    id
                    scheduleType
                    cronExpression
                    intervalSeconds
                    recurrenceFrequency
                    recurrenceCount
                    startDate
                    endDate
                    timezone
                    isActive
                    createdAt
                    updatedAt
                }
            }
        """

        variables = {"input": self._serialize_schedule_input(schedule_input)}

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when adding schedule", 500, response)

        schedule_data = response["data"].get("addAutomationSchedule")
        if not schedule_data:
            raise SuperOpsAPIError("No schedule data in response", 500, response)

        return AutomationSchedule.from_dict(schedule_data)

    async def update_schedule(
        self, schedule_id: str, schedule_input: AutomationScheduleInput
    ) -> AutomationSchedule:
        """Update an automation schedule.

        Args:
            schedule_id: The schedule ID
            schedule_input: Updated schedule data

        Returns:
            Updated schedule instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not schedule_id or not isinstance(schedule_id, str):
            raise SuperOpsValidationError("Schedule ID must be a non-empty string")

        self.logger.debug(f"Updating schedule {schedule_id}")

        # Validate schedule input
        self._validate_schedule_input(schedule_input)

        mutation = """
            mutation UpdateAutomationSchedule($id: ID!, $input: AutomationScheduleInput!) {
                updateAutomationSchedule(id: $id, input: $input) {
                    id
                    scheduleType
                    cronExpression
                    intervalSeconds
                    recurrenceFrequency
                    recurrenceCount
                    startDate
                    endDate
                    timezone
                    isActive
                    createdAt
                    updatedAt
                }
            }
        """

        variables = {"id": schedule_id, "input": self._serialize_schedule_input(schedule_input)}

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when updating schedule", 500, response)

        schedule_data = response["data"].get("updateAutomationSchedule")
        if not schedule_data:
            raise SuperOpsAPIError("No schedule data in response", 500, response)

        return AutomationSchedule.from_dict(schedule_data)

    # Job Management

    async def execute_workflow(self, execution_input: AutomationExecutionInput) -> AutomationJob:
        """Execute a workflow.

        Args:
            execution_input: Workflow execution parameters

        Returns:
            Created job instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug(f"Executing workflow {execution_input.workflow_id}")

        mutation = """
            mutation ExecuteAutomationWorkflow($input: AutomationExecutionInput!) {
                executeAutomationWorkflow(input: $input) {
                    id
                    workflowId
                    triggerId
                    status
                    startedAt
                    completedAt
                    failedAt
                    errorMessage
                    executionLog
                    inputData
                    outputData
                    retryCount
                    maxRetries
                    scheduledAt
                    priority
                    createdAt
                    updatedAt
                }
            }
        """

        variables = {"input": self._serialize_execution_input(execution_input)}

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when executing workflow", 500, response)

        job_data = response["data"].get("executeAutomationWorkflow")
        if not job_data:
            raise SuperOpsAPIError("No job data in response", 500, response)

        return AutomationJob.from_dict(job_data)

    async def get_jobs(
        self,
        workflow_id: Optional[str] = None,
        status: Optional[AutomationJobStatus] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get automation jobs with filtering.

        Args:
            workflow_id: Optional workflow ID filter
            status: Optional job status filter
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[AutomationJob]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Getting automation jobs")

        filters = {}
        if workflow_id:
            filters["workflow_id"] = workflow_id
        if status:
            filters["status"] = status.value

        query = """
            query GetAutomationJobs(
                $page: Int!
                $pageSize: Int!
                $filters: AutomationJobFilter
                $sortBy: String
                $sortOrder: SortOrder
            ) {
                automationJobs(
                    page: $page
                    pageSize: $pageSize
                    filters: $filters
                    sortBy: $sortBy
                    sortOrder: $sortOrder
                ) {
                    items {
                        id
                        workflowId
                        triggerId
                        status
                        startedAt
                        completedAt
                        failedAt
                        errorMessage
                        executionLog
                        inputData
                        outputData
                        retryCount
                        maxRetries
                        scheduledAt
                        priority
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

        variables = {
            "page": page,
            "pageSize": page_size,
            "filters": filters,
            "sortBy": sort_by or "created_at",
            "sortOrder": sort_order.upper(),
        }

        response = await self.client.execute_query(query, variables)

        if not response.get("data"):
            return {"items": [], "pagination": self._empty_pagination()}

        jobs_data = response["data"].get("automationJobs")
        if not jobs_data:
            return {"items": [], "pagination": self._empty_pagination()}

        items = [AutomationJob.from_dict(item) for item in jobs_data.get("items", [])]
        pagination = jobs_data.get("pagination", self._empty_pagination())

        return {"items": items, "pagination": pagination}

    async def get_job(self, job_id: str) -> Optional[AutomationJob]:
        """Get a specific automation job.

        Args:
            job_id: The job ID

        Returns:
            Job instance or None if not found

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not job_id or not isinstance(job_id, str):
            raise SuperOpsValidationError("Job ID must be a non-empty string")

        self.logger.debug(f"Getting automation job {job_id}")

        query = """
            query GetAutomationJob($id: ID!) {
                automationJob(id: $id) {
                    id
                    workflowId
                    triggerId
                    status
                    startedAt
                    completedAt
                    failedAt
                    errorMessage
                    executionLog
                    inputData
                    outputData
                    retryCount
                    maxRetries
                    scheduledAt
                    priority
                    createdAt
                    updatedAt
                }
            }
        """

        variables = {"id": job_id}

        response = await self.client.execute_query(query, variables)

        if not response.get("data"):
            return None

        job_data = response["data"].get("automationJob")
        if not job_data:
            return None

        return AutomationJob.from_dict(job_data)

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running automation job.

        Args:
            job_id: The job ID

        Returns:
            True if cancellation was successful

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not job_id or not isinstance(job_id, str):
            raise SuperOpsValidationError("Job ID must be a non-empty string")

        self.logger.debug(f"Cancelling automation job {job_id}")

        mutation = """
            mutation CancelAutomationJob($id: ID!) {
                cancelAutomationJob(id: $id) {
                    success
                    message
                }
            }
        """

        variables = {"id": job_id}

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when cancelling job", 500, response)

        result = response["data"].get("cancelAutomationJob")
        if not result:
            raise SuperOpsAPIError("No result in response", 500, response)

        return result.get("success", False)

    async def retry_job(self, job_id: str) -> AutomationJob:
        """Retry a failed automation job.

        Args:
            job_id: The job ID

        Returns:
            Updated job instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not job_id or not isinstance(job_id, str):
            raise SuperOpsValidationError("Job ID must be a non-empty string")

        self.logger.debug(f"Retrying automation job {job_id}")

        mutation = """
            mutation RetryAutomationJob($id: ID!) {
                retryAutomationJob(id: $id) {
                    id
                    workflowId
                    triggerId
                    status
                    startedAt
                    completedAt
                    failedAt
                    errorMessage
                    executionLog
                    inputData
                    outputData
                    retryCount
                    maxRetries
                    scheduledAt
                    priority
                    createdAt
                    updatedAt
                }
            }
        """

        variables = {"id": job_id}

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when retrying job", 500, response)

        job_data = response["data"].get("retryAutomationJob")
        if not job_data:
            raise SuperOpsAPIError("No job data in response", 500, response)

        return AutomationJob.from_dict(job_data)

    # Bulk Operations

    async def bulk_activate_workflows(self, workflow_ids: List[str]) -> List[AutomationWorkflow]:
        """Activate multiple workflows.

        Args:
            workflow_ids: List of workflow IDs

        Returns:
            List of updated workflow instances

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If any API request fails
        """
        if not workflow_ids:
            raise SuperOpsValidationError("Workflow IDs list cannot be empty")
        if not isinstance(workflow_ids, list):
            raise SuperOpsValidationError("Workflow IDs must be a list")

        self.logger.debug(f"Bulk activating {len(workflow_ids)} workflows")

        updated_workflows = []
        for workflow_id in workflow_ids:
            try:
                workflow = await self.activate_workflow(workflow_id)
                updated_workflows.append(workflow)
            except Exception as e:
                self.logger.error(f"Failed to activate workflow {workflow_id}: {e}")
                # Continue with other workflows

        self.logger.info(
            f"Successfully activated {len(updated_workflows)} out of {len(workflow_ids)} workflows"
        )
        return updated_workflows

    async def bulk_deactivate_workflows(self, workflow_ids: List[str]) -> List[AutomationWorkflow]:
        """Deactivate multiple workflows.

        Args:
            workflow_ids: List of workflow IDs

        Returns:
            List of updated workflow instances

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If any API request fails
        """
        if not workflow_ids:
            raise SuperOpsValidationError("Workflow IDs list cannot be empty")
        if not isinstance(workflow_ids, list):
            raise SuperOpsValidationError("Workflow IDs must be a list")

        self.logger.debug(f"Bulk deactivating {len(workflow_ids)} workflows")

        updated_workflows = []
        for workflow_id in workflow_ids:
            try:
                workflow = await self.deactivate_workflow(workflow_id)
                updated_workflows.append(workflow)
            except Exception as e:
                self.logger.error(f"Failed to deactivate workflow {workflow_id}: {e}")
                # Continue with other workflows

        self.logger.info(
            f"Successfully deactivated {len(updated_workflows)} out of {len(workflow_ids)} workflows"
        )
        return updated_workflows

    # Protected methods for GraphQL query building

    def _build_get_query(self, **kwargs) -> str:
        """Build GraphQL query for getting a single automation workflow."""
        include_actions = kwargs.get("include_actions", False)
        include_triggers = kwargs.get("include_triggers", False)

        fields = [
            "id",
            "name",
            "description",
            "status",
            "version",
            "tags",
            "isTemplate",
            "templateId",
            "maxConcurrentJobs",
            "timeoutSeconds",
            "retryFailedActions",
            "createdBy",
            "lastModifiedBy",
            "lastRunAt",
            "nextRunAt",
            "totalRuns",
            "successfulRuns",
            "failedRuns",
            "templateVariables",
            "templateDescription",
            "templateCategory",
            "createdAt",
            "updatedAt",
        ]

        if include_actions:
            fields.append(
                """
                actions {
                    id
                    name
                    actionType
                    config
                    orderIndex
                    isEnabled
                    condition
                    timeoutSeconds
                    retryAttempts
                    retryDelaySeconds
                }
            """
            )

        if include_triggers:
            fields.append(
                """
                triggers {
                    id
                    name
                    triggerType
                    config
                    conditions
                    isEnabled
                    schedule {
                        id
                        scheduleType
                        cronExpression
                        intervalSeconds
                        recurrenceFrequency
                        recurrenceCount
                        startDate
                        endDate
                        timezone
                        isActive
                    }
                }
            """
            )

        field_str = "\n        ".join(fields)

        return f"""
            query GetAutomationWorkflow($id: ID!) {{
                automationWorkflow(id: $id) {{
                    {field_str}
                }}
            }}
        """

    def _build_list_query(self, **kwargs) -> str:
        """Build GraphQL query for listing automation workflows."""
        return """
            query ListAutomationWorkflows(
                $page: Int!
                $pageSize: Int!
                $filters: AutomationWorkflowFilter
                $sortBy: String
                $sortOrder: SortOrder
            ) {
                automationWorkflows(
                    page: $page
                    pageSize: $pageSize
                    filters: $filters
                    sortBy: $sortBy
                    sortOrder: $sortOrder
                ) {
                    items {
                        id
                        name
                        description
                        status
                        version
                        tags
                        isTemplate
                        templateId
                        maxConcurrentJobs
                        timeoutSeconds
                        retryFailedActions
                        createdBy
                        lastModifiedBy
                        lastRunAt
                        nextRunAt
                        totalRuns
                        successfulRuns
                        failedRuns
                        templateVariables
                        templateDescription
                        templateCategory
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
        """Build GraphQL mutation for creating an automation workflow."""
        return """
            mutation CreateAutomationWorkflow($input: AutomationWorkflowInput!) {
                createAutomationWorkflow(input: $input) {
                    id
                    name
                    description
                    status
                    version
                    tags
                    isTemplate
                    templateId
                    maxConcurrentJobs
                    timeoutSeconds
                    retryFailedActions
                    createdBy
                    lastModifiedBy
                    lastRunAt
                    nextRunAt
                    totalRuns
                    successfulRuns
                    failedRuns
                    templateVariables
                    templateDescription
                    templateCategory
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_update_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for updating an automation workflow."""
        return """
            mutation UpdateAutomationWorkflow($id: ID!, $input: AutomationWorkflowInput!) {
                updateAutomationWorkflow(id: $id, input: $input) {
                    id
                    name
                    description
                    status
                    version
                    tags
                    isTemplate
                    templateId
                    maxConcurrentJobs
                    timeoutSeconds
                    retryFailedActions
                    createdBy
                    lastModifiedBy
                    lastRunAt
                    nextRunAt
                    totalRuns
                    successfulRuns
                    failedRuns
                    templateVariables
                    templateDescription
                    templateCategory
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_delete_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for deleting an automation workflow."""
        return """
            mutation DeleteAutomationWorkflow($id: ID!) {
                deleteAutomationWorkflow(id: $id) {
                    success
                    message
                }
            }
        """

    def _build_search_query(self, **kwargs) -> str:
        """Build GraphQL query for searching automation workflows."""
        return """
            query SearchAutomationWorkflows(
                $query: String!
                $page: Int!
                $pageSize: Int!
            ) {
                searchAutomationWorkflows(
                    query: $query
                    page: $page
                    pageSize: $pageSize
                ) {
                    items {
                        id
                        name
                        description
                        status
                        version
                        tags
                        isTemplate
                        templateId
                        maxConcurrentJobs
                        timeoutSeconds
                        retryFailedActions
                        createdBy
                        lastModifiedBy
                        lastRunAt
                        nextRunAt
                        totalRuns
                        successfulRuns
                        failedRuns
                        templateVariables
                        templateDescription
                        templateCategory
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
        """Validate data for workflow creation."""
        validated = data.copy()

        # Required fields
        if not validated.get("name"):
            raise SuperOpsValidationError("Workflow name is required")

        # Validate status if provided
        status = validated.get("status")
        if status and status not in [s.value for s in AutomationWorkflowStatus]:
            raise SuperOpsValidationError(f"Invalid workflow status: {status}")

        # Validate max_concurrent_jobs if provided
        max_jobs = validated.get("max_concurrent_jobs")
        if max_jobs is not None and (not isinstance(max_jobs, int) or max_jobs < 1):
            raise SuperOpsValidationError("max_concurrent_jobs must be a positive integer")

        # Validate timeout_seconds if provided
        timeout = validated.get("timeout_seconds")
        if timeout is not None and (not isinstance(timeout, int) or timeout < 1):
            raise SuperOpsValidationError("timeout_seconds must be a positive integer")

        return validated

    def _validate_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data for workflow updates."""
        validated = data.copy()

        # Validate status if provided
        status = validated.get("status")
        if status and status not in [s.value for s in AutomationWorkflowStatus]:
            raise SuperOpsValidationError(f"Invalid workflow status: {status}")

        # Validate max_concurrent_jobs if provided
        max_jobs = validated.get("max_concurrent_jobs")
        if max_jobs is not None and (not isinstance(max_jobs, int) or max_jobs < 1):
            raise SuperOpsValidationError("max_concurrent_jobs must be a positive integer")

        # Validate timeout_seconds if provided
        timeout = validated.get("timeout_seconds")
        if timeout is not None and (not isinstance(timeout, int) or timeout < 1):
            raise SuperOpsValidationError("timeout_seconds must be a positive integer")

        return validated

    def _validate_schedule_input(self, schedule_input: AutomationScheduleInput) -> None:
        """Validate schedule input data."""
        schedule_type = schedule_input.schedule_type

        if schedule_type == ScheduleType.CRON:
            if not schedule_input.cron_expression:
                raise SuperOpsValidationError("cron_expression is required for CRON schedule type")

        elif schedule_type == ScheduleType.INTERVAL:
            if not schedule_input.interval_seconds or schedule_input.interval_seconds < 1:
                raise SuperOpsValidationError(
                    "interval_seconds must be positive for INTERVAL schedule type"
                )

        elif schedule_type == ScheduleType.RECURRING and not schedule_input.recurrence_frequency:
            raise SuperOpsValidationError(
                "recurrence_frequency is required for RECURRING schedule type"
            )

        # Validate date range if provided
        if (
            schedule_input.start_date
            and schedule_input.end_date
            and schedule_input.end_date <= schedule_input.start_date
        ):
            raise SuperOpsValidationError("end_date must be after start_date")

    def _serialize_action_input(self, action_input: AutomationActionInput) -> Dict[str, Any]:
        """Serialize action input for GraphQL."""
        result = {
            "name": action_input.name,
            "actionType": action_input.action_type.value,
            "config": action_input.config,
            "workflowId": action_input.workflow_id,
        }

        # Add optional fields if present
        if action_input.order_index is not None:
            result["orderIndex"] = action_input.order_index
        if action_input.is_enabled is not None:
            result["isEnabled"] = action_input.is_enabled
        if action_input.condition is not None:
            result["condition"] = action_input.condition
        if action_input.timeout_seconds is not None:
            result["timeoutSeconds"] = action_input.timeout_seconds
        if action_input.retry_attempts is not None:
            result["retryAttempts"] = action_input.retry_attempts
        if action_input.retry_delay_seconds is not None:
            result["retryDelaySeconds"] = action_input.retry_delay_seconds

        return result

    def _serialize_trigger_input(self, trigger_input: AutomationTriggerInput) -> Dict[str, Any]:
        """Serialize trigger input for GraphQL."""
        result = {
            "name": trigger_input.name,
            "triggerType": trigger_input.trigger_type.value,
            "config": trigger_input.config,
            "workflowId": trigger_input.workflow_id,
        }

        # Add optional fields if present
        if trigger_input.conditions is not None:
            result["conditions"] = trigger_input.conditions
        if trigger_input.is_enabled is not None:
            result["isEnabled"] = trigger_input.is_enabled

        return result

    def _serialize_schedule_input(self, schedule_input: AutomationScheduleInput) -> Dict[str, Any]:
        """Serialize schedule input for GraphQL."""
        result = {
            "scheduleType": schedule_input.schedule_type.value,
            "triggerId": schedule_input.trigger_id,
        }

        # Add optional fields if present
        if schedule_input.cron_expression is not None:
            result["cronExpression"] = schedule_input.cron_expression
        if schedule_input.interval_seconds is not None:
            result["intervalSeconds"] = schedule_input.interval_seconds
        if schedule_input.recurrence_frequency is not None:
            result["recurrenceFrequency"] = schedule_input.recurrence_frequency.value
        if schedule_input.recurrence_count is not None:
            result["recurrenceCount"] = schedule_input.recurrence_count
        if schedule_input.start_date is not None:
            result["startDate"] = schedule_input.start_date.isoformat()
        if schedule_input.end_date is not None:
            result["endDate"] = schedule_input.end_date.isoformat()
        if schedule_input.timezone is not None:
            result["timezone"] = schedule_input.timezone
        if schedule_input.is_active is not None:
            result["isActive"] = schedule_input.is_active

        return result

    def _serialize_execution_input(
        self, execution_input: AutomationExecutionInput
    ) -> Dict[str, Any]:
        """Serialize execution input for GraphQL."""
        result = {
            "workflowId": execution_input.workflow_id,
            "asyncExecution": execution_input.async_execution,
            "waitForCompletion": execution_input.wait_for_completion,
        }

        # Add optional fields if present
        if execution_input.input_data is not None:
            result["inputData"] = execution_input.input_data
        if execution_input.trigger_id is not None:
            result["triggerId"] = execution_input.trigger_id
        if execution_input.priority is not None:
            result["priority"] = execution_input.priority
        if execution_input.timeout_seconds is not None:
            result["timeoutSeconds"] = execution_input.timeout_seconds

        return result
