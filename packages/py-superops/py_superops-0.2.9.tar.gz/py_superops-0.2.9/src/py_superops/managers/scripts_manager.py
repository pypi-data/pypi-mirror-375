# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Script manager for SuperOps API operations."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..exceptions import SuperOpsAPIError, SuperOpsValidationError
from ..graphql.types import (
    DeploymentStatus,
    ExecutionStatus,
    ExecutionTrigger,
    Script,
    ScriptCategory,
    ScriptDeployment,
    ScriptExecution,
    ScriptLibrary,
    ScriptType,
)

if TYPE_CHECKING:
    from ..client import SuperOpsClient
from .base import ResourceManager


class ScriptsManager(ResourceManager[Script]):
    """Manager for script operations.

    Provides high-level methods for managing SuperOps scripts including
    CRUD operations, execution management, deployment, library organization,
    template management, and bulk operations with comprehensive error handling.
    """

    def __init__(self, client: "SuperOpsClient"):
        """Initialize the scripts manager.

        Args:
            client: SuperOps client instance
        """
        super().__init__(client, Script, "script")

    # Basic CRUD operations (inherited from ResourceManager)
    # get, list, create, update, delete, search

    # Script execution operations
    async def execute_script(
        self,
        script_id: str,
        target_assets: Optional[List[str]] = None,
        target_sites: Optional[List[str]] = None,
        target_clients: Optional[List[str]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        timeout_seconds: Optional[int] = None,
        retry_count: Optional[int] = None,
        execution_trigger: ExecutionTrigger = ExecutionTrigger.MANUAL,
    ) -> ScriptExecution:
        """Execute a script on specified targets.

        Args:
            script_id: Script ID to execute
            target_assets: List of asset IDs to execute on
            target_sites: List of site IDs to execute on
            target_clients: List of client IDs to execute on
            parameters: Script parameters as key-value pairs
            timeout_seconds: Execution timeout in seconds
            retry_count: Number of retries on failure
            execution_trigger: How the execution was triggered

        Returns:
            Script execution instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not script_id or not isinstance(script_id, str):
            raise SuperOpsValidationError("Script ID must be a non-empty string")

        if not any([target_assets, target_sites, target_clients]):
            raise SuperOpsValidationError(
                "At least one target (assets, sites, or clients) must be specified"
            )

        self.logger.debug(f"Executing script {script_id}")

        execution_data = {
            "script_id": script_id,
            "execution_trigger": execution_trigger.value,
        }

        if target_assets:
            execution_data["target_assets"] = target_assets
        if target_sites:
            execution_data["target_sites"] = target_sites
        if target_clients:
            execution_data["target_clients"] = target_clients
        if parameters:
            execution_data["parameters"] = parameters
        if timeout_seconds:
            execution_data["timeout_seconds"] = timeout_seconds
        if retry_count is not None:
            execution_data["retry_count"] = retry_count

        mutation = self._build_execute_script_mutation()
        variables = {"input": execution_data}

        response = await self.client.execute_mutation(mutation, variables)
        if not response.get("data") or not response["data"].get("executeScript"):
            raise SuperOpsAPIError("Failed to execute script", 500, response)

        execution = ScriptExecution.from_dict(response["data"]["executeScript"])
        self.logger.info(f"Started script execution: {execution.id}")

        return execution

    async def get_execution_status(self, execution_id: str) -> ScriptExecution:
        """Get script execution status and details.

        Args:
            execution_id: Script execution ID

        Returns:
            Script execution instance with current status

        Raises:
            SuperOpsValidationError: If execution_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not execution_id or not isinstance(execution_id, str):
            raise SuperOpsValidationError("Execution ID must be a non-empty string")

        self.logger.debug(f"Getting execution status: {execution_id}")

        query = self._build_get_execution_query()
        variables = {"id": execution_id}

        response = await self.client.execute_query(query, variables)
        if not response.get("data") or not response["data"].get("scriptExecution"):
            raise SuperOpsAPIError("Execution not found", 404, response)

        return ScriptExecution.from_dict(response["data"]["scriptExecution"])

    async def cancel_execution(self, execution_id: str, reason: Optional[str] = None) -> bool:
        """Cancel a running script execution.

        Args:
            execution_id: Script execution ID to cancel
            reason: Optional cancellation reason

        Returns:
            True if cancellation was successful

        Raises:
            SuperOpsValidationError: If execution_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not execution_id or not isinstance(execution_id, str):
            raise SuperOpsValidationError("Execution ID must be a non-empty string")

        self.logger.debug(f"Cancelling execution: {execution_id}")

        mutation = self._build_cancel_execution_mutation()
        variables = {"id": execution_id}
        if reason:
            variables["reason"] = reason

        response = await self.client.execute_mutation(mutation, variables)
        if not response.get("data"):
            raise SuperOpsAPIError("Failed to cancel execution", 500, response)

        result = response["data"].get("cancelScriptExecution", {})
        success = result.get("success", False)

        if success:
            self.logger.info(f"Cancelled execution: {execution_id}")

        return success

    async def get_execution_history(
        self,
        script_id: Optional[str] = None,
        status: Optional[ExecutionStatus] = None,
        executed_by_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get script execution history with filtering.

        Args:
            script_id: Filter by script ID
            status: Filter by execution status
            executed_by_id: Filter by executor user ID
            start_date: Filter executions started after this date
            end_date: Filter executions started before this date
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: started_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[ScriptExecution]) and 'pagination' info
        """
        self.logger.debug("Getting script execution history")

        filters = {}
        if script_id:
            filters["script_id"] = script_id
        if status:
            filters["status"] = status.value
        if executed_by_id:
            filters["executed_by_id"] = executed_by_id
        if start_date:
            filters["started_after"] = start_date.isoformat()
        if end_date:
            filters["started_before"] = end_date.isoformat()

        query = self._build_list_executions_query()
        variables = {
            "page": page,
            "pageSize": page_size,
            "filters": filters,
            "sortBy": sort_by or "started_at",
            "sortOrder": sort_order.upper(),
        }

        response = await self.client.execute_query(query, variables)
        if not response.get("data") or not response["data"].get("scriptExecutions"):
            return {"items": [], "pagination": self._empty_pagination()}

        executions_data = response["data"]["scriptExecutions"]
        items = [ScriptExecution.from_dict(item) for item in executions_data.get("items", [])]
        pagination = executions_data.get("pagination", self._empty_pagination())

        return {"items": items, "pagination": pagination}

    # Script filtering and search operations
    async def get_by_type(
        self,
        script_type: ScriptType,
        page: int = 1,
        page_size: int = 50,
        deployment_status: Optional[DeploymentStatus] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get scripts filtered by type.

        Args:
            script_type: Script type to filter by
            page: Page number (1-based)
            page_size: Number of items per page
            deployment_status: Optional deployment status filter
            sort_by: Field to sort by (default: updated_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Script]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not isinstance(script_type, ScriptType):
            raise SuperOpsValidationError("Script type must be a ScriptType enum")

        self.logger.debug(f"Getting scripts with type: {script_type.value}")

        filters = {"script_type": script_type.value}
        if deployment_status:
            filters["deployment_status"] = deployment_status.value

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "updated_at",
            sort_order=sort_order,
        )

    async def get_by_category(
        self,
        category: ScriptCategory,
        page: int = 1,
        page_size: int = 50,
        deployment_status: Optional[DeploymentStatus] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get scripts filtered by category.

        Args:
            category: Script category to filter by
            page: Page number (1-based)
            page_size: Number of items per page
            deployment_status: Optional deployment status filter
            sort_by: Field to sort by (default: updated_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Script]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not isinstance(category, ScriptCategory):
            raise SuperOpsValidationError("Category must be a ScriptCategory enum")

        self.logger.debug(f"Getting scripts with category: {category.value}")

        filters = {"category": category.value}
        if deployment_status:
            filters["deployment_status"] = deployment_status.value

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "updated_at",
            sort_order=sort_order,
        )

    async def get_by_author(
        self,
        author_id: str,
        page: int = 1,
        page_size: int = 50,
        include_templates: bool = True,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get scripts authored by a specific user.

        Args:
            author_id: Author user ID
            page: Page number (1-based)
            page_size: Number of items per page
            include_templates: Whether to include template scripts
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Script]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not author_id or not isinstance(author_id, str):
            raise SuperOpsValidationError("Author ID must be a non-empty string")

        self.logger.debug(f"Getting scripts by author: {author_id}")

        filters = {"author_id": author_id}
        if not include_templates:
            filters["is_template"] = False

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
        )

    async def get_templates(
        self,
        script_type: Optional[ScriptType] = None,
        category: Optional[ScriptCategory] = None,
        is_public: bool = True,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get script templates.

        Args:
            script_type: Optional script type filter
            category: Optional category filter
            is_public: Whether to get public templates only
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: usage_count)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Script]) and 'pagination' info
        """
        self.logger.debug("Getting script templates")

        filters = {"is_template": True}
        if script_type:
            filters["script_type"] = script_type.value
        if category:
            filters["category"] = category.value
        if is_public is not None:
            filters["is_public"] = is_public

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "usage_count",
            sort_order=sort_order,
        )

    async def get_by_tags(
        self,
        tags: List[str],
        match_all: bool = False,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get scripts by tags.

        Args:
            tags: List of tags to filter by
            match_all: Whether to match all tags (AND) or any tag (OR)
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: updated_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Script]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not tags or not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
            raise SuperOpsValidationError("Tags must be a non-empty list of strings")

        self.logger.debug(f"Getting scripts by tags: {tags}")

        if match_all:
            filters = {"tags__contains_all": tags}
        else:
            filters = {"tags__contains_any": tags}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "updated_at",
            sort_order=sort_order,
        )

    # Script deployment operations
    async def create_deployment(
        self,
        script_id: str,
        deployment_name: str,
        target_type: str,
        target_ids: Optional[List[str]] = None,
        schedule_expression: Optional[str] = None,
        is_enabled: bool = True,
        configuration: Optional[Dict[str, Any]] = None,
    ) -> ScriptDeployment:
        """Create a script deployment.

        Args:
            script_id: Script ID to deploy
            deployment_name: Name for the deployment
            target_type: Type of targets ('asset', 'site', 'client', 'all')
            target_ids: List of target IDs
            schedule_expression: Cron expression for scheduling
            is_enabled: Whether deployment is enabled
            configuration: Additional deployment configuration

        Returns:
            Created deployment instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not script_id or not isinstance(script_id, str):
            raise SuperOpsValidationError("Script ID must be a non-empty string")
        if not deployment_name or not isinstance(deployment_name, str):
            raise SuperOpsValidationError("Deployment name must be a non-empty string")
        if target_type not in ["asset", "site", "client", "all"]:
            raise SuperOpsValidationError("Target type must be 'asset', 'site', 'client', or 'all'")

        self.logger.debug(f"Creating deployment for script {script_id}: {deployment_name}")

        deployment_data = {
            "script_id": script_id,
            "deployment_name": deployment_name,
            "target_type": target_type,
            "is_enabled": is_enabled,
        }

        if target_ids:
            deployment_data["target_ids"] = target_ids
        if schedule_expression:
            deployment_data["schedule_expression"] = schedule_expression
        if configuration:
            deployment_data["configuration"] = configuration

        mutation = self._build_create_deployment_mutation()
        variables = {"input": deployment_data}

        response = await self.client.execute_mutation(mutation, variables)
        if not response.get("data") or not response["data"].get("createScriptDeployment"):
            raise SuperOpsAPIError("Failed to create deployment", 500, response)

        deployment = ScriptDeployment.from_dict(response["data"]["createScriptDeployment"])
        self.logger.info(f"Created deployment: {deployment.id}")

        return deployment

    async def get_deployments(
        self,
        script_id: Optional[str] = None,
        deployment_status: Optional[DeploymentStatus] = None,
        is_enabled: Optional[bool] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get script deployments with filtering.

        Args:
            script_id: Filter by script ID
            deployment_status: Filter by deployment status
            is_enabled: Filter by enabled status
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: updated_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[ScriptDeployment]) and 'pagination' info
        """
        self.logger.debug("Getting script deployments")

        filters = {}
        if script_id:
            filters["script_id"] = script_id
        if deployment_status:
            filters["deployment_status"] = deployment_status.value
        if is_enabled is not None:
            filters["is_enabled"] = is_enabled

        query = self._build_list_deployments_query()
        variables = {
            "page": page,
            "pageSize": page_size,
            "filters": filters,
            "sortBy": sort_by or "updated_at",
            "sortOrder": sort_order.upper(),
        }

        response = await self.client.execute_query(query, variables)
        if not response.get("data") or not response["data"].get("scriptDeployments"):
            return {"items": [], "pagination": self._empty_pagination()}

        deployments_data = response["data"]["scriptDeployments"]
        items = [ScriptDeployment.from_dict(item) for item in deployments_data.get("items", [])]
        pagination = deployments_data.get("pagination", self._empty_pagination())

        return {"items": items, "pagination": pagination}

    async def update_deployment(
        self,
        deployment_id: str,
        deployment_data: Dict[str, Any],
    ) -> ScriptDeployment:
        """Update a script deployment.

        Args:
            deployment_id: Deployment ID to update
            deployment_data: Updated deployment data

        Returns:
            Updated deployment instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not deployment_id or not isinstance(deployment_id, str):
            raise SuperOpsValidationError("Deployment ID must be a non-empty string")

        self.logger.debug(f"Updating deployment: {deployment_id}")

        mutation = self._build_update_deployment_mutation()
        variables = {"id": deployment_id, "input": deployment_data}

        response = await self.client.execute_mutation(mutation, variables)
        if not response.get("data") or not response["data"].get("updateScriptDeployment"):
            raise SuperOpsAPIError("Failed to update deployment", 500, response)

        deployment = ScriptDeployment.from_dict(response["data"]["updateScriptDeployment"])
        self.logger.info(f"Updated deployment: {deployment_id}")

        return deployment

    async def delete_deployment(self, deployment_id: str) -> bool:
        """Delete a script deployment.

        Args:
            deployment_id: Deployment ID to delete

        Returns:
            True if deletion was successful

        Raises:
            SuperOpsValidationError: If deployment_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not deployment_id or not isinstance(deployment_id, str):
            raise SuperOpsValidationError("Deployment ID must be a non-empty string")

        self.logger.debug(f"Deleting deployment: {deployment_id}")

        mutation = self._build_delete_deployment_mutation()
        variables = {"id": deployment_id}

        response = await self.client.execute_mutation(mutation, variables)
        if not response.get("data"):
            raise SuperOpsAPIError("Failed to delete deployment", 500, response)

        result = response["data"].get("deleteScriptDeployment", {})
        success = result.get("success", False)

        if success:
            self.logger.info(f"Deleted deployment: {deployment_id}")

        return success

    # Script library operations
    async def create_library(
        self,
        name: str,
        description: str,
        is_public: bool = False,
        tags: Optional[List[str]] = None,
        custom_fields: Optional[Dict[str, Any]] = None,
    ) -> ScriptLibrary:
        """Create a script library.

        Args:
            name: Library name
            description: Library description
            is_public: Whether library is public
            tags: Optional tags
            custom_fields: Optional custom fields

        Returns:
            Created library instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not name or not isinstance(name, str):
            raise SuperOpsValidationError("Library name must be a non-empty string")
        if not description or not isinstance(description, str):
            raise SuperOpsValidationError("Library description must be a non-empty string")

        self.logger.debug(f"Creating script library: {name}")

        library_data = {
            "name": name,
            "description": description,
            "is_public": is_public,
        }

        if tags:
            library_data["tags"] = tags
        if custom_fields:
            library_data["custom_fields"] = custom_fields

        mutation = self._build_create_library_mutation()
        variables = {"input": library_data}

        response = await self.client.execute_mutation(mutation, variables)
        if not response.get("data") or not response["data"].get("createScriptLibrary"):
            raise SuperOpsAPIError("Failed to create library", 500, response)

        library = ScriptLibrary.from_dict(response["data"]["createScriptLibrary"])
        self.logger.info(f"Created library: {library.id}")

        return library

    async def get_libraries(
        self,
        is_public: Optional[bool] = None,
        owner_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get script libraries with filtering.

        Args:
            is_public: Filter by public status
            owner_id: Filter by owner ID
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: updated_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[ScriptLibrary]) and 'pagination' info
        """
        self.logger.debug("Getting script libraries")

        filters = {}
        if is_public is not None:
            filters["is_public"] = is_public
        if owner_id:
            filters["owner_id"] = owner_id

        query = self._build_list_libraries_query()
        variables = {
            "page": page,
            "pageSize": page_size,
            "filters": filters,
            "sortBy": sort_by or "updated_at",
            "sortOrder": sort_order.upper(),
        }

        response = await self.client.execute_query(query, variables)
        if not response.get("data") or not response["data"].get("scriptLibraries"):
            return {"items": [], "pagination": self._empty_pagination()}

        libraries_data = response["data"]["scriptLibraries"]
        items = [ScriptLibrary.from_dict(item) for item in libraries_data.get("items", [])]
        pagination = libraries_data.get("pagination", self._empty_pagination())

        return {"items": items, "pagination": pagination}

    async def get_library_scripts(
        self,
        library_id: str,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get scripts in a specific library.

        Args:
            library_id: Library ID
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: name)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Script]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not library_id or not isinstance(library_id, str):
            raise SuperOpsValidationError("Library ID must be a non-empty string")

        self.logger.debug(f"Getting scripts in library: {library_id}")

        filters = {"library_id": library_id}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
        )

    # Template operations
    async def create_from_template(
        self,
        template_id: str,
        script_data: Optional[Dict[str, Any]] = None,
    ) -> Script:
        """Create a script from a template.

        Args:
            template_id: Template ID
            script_data: Optional script data to override template defaults

        Returns:
            Created script instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not template_id or not isinstance(template_id, str):
            raise SuperOpsValidationError("Template ID must be a non-empty string")

        self.logger.debug(f"Creating script from template: {template_id}")

        create_data = {"template_id": template_id}
        if script_data:
            create_data.update(script_data)

        return await self.create(create_data)

    # Bulk operations
    async def bulk_execute(
        self,
        script_ids: List[str],
        target_assets: Optional[List[str]] = None,
        target_sites: Optional[List[str]] = None,
        target_clients: Optional[List[str]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        timeout_seconds: Optional[int] = None,
        execution_trigger: ExecutionTrigger = ExecutionTrigger.MANUAL,
    ) -> List[ScriptExecution]:
        """Execute multiple scripts in bulk.

        Args:
            script_ids: List of script IDs to execute
            target_assets: List of asset IDs to execute on
            target_sites: List of site IDs to execute on
            target_clients: List of client IDs to execute on
            parameters: Common script parameters
            timeout_seconds: Execution timeout in seconds
            execution_trigger: How the execution was triggered

        Returns:
            List of script execution instances

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not script_ids or not isinstance(script_ids, list):
            raise SuperOpsValidationError("Script IDs must be a non-empty list")

        if not any([target_assets, target_sites, target_clients]):
            raise SuperOpsValidationError(
                "At least one target (assets, sites, or clients) must be specified"
            )

        self.logger.debug(f"Bulk executing {len(script_ids)} scripts")

        executions = []
        for script_id in script_ids:
            try:
                execution = await self.execute_script(
                    script_id=script_id,
                    target_assets=target_assets,
                    target_sites=target_sites,
                    target_clients=target_clients,
                    parameters=parameters,
                    timeout_seconds=timeout_seconds,
                    execution_trigger=execution_trigger,
                )
                executions.append(execution)
            except Exception as e:
                self.logger.warning(f"Failed to execute script {script_id}: {e}")
                # Continue with other scripts

        self.logger.info(f"Successfully started {len(executions)} of {len(script_ids)} executions")
        return executions

    async def bulk_update_status(
        self,
        script_ids: List[str],
        deployment_status: DeploymentStatus,
    ) -> List[Script]:
        """Update deployment status for multiple scripts.

        Args:
            script_ids: List of script IDs to update
            deployment_status: New deployment status

        Returns:
            List of updated script instances

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not script_ids or not isinstance(script_ids, list):
            raise SuperOpsValidationError("Script IDs must be a non-empty list")
        if not isinstance(deployment_status, DeploymentStatus):
            raise SuperOpsValidationError("Deployment status must be a DeploymentStatus enum")

        self.logger.debug(f"Bulk updating status for {len(script_ids)} scripts")

        update_data = {"deployment_status": deployment_status.value}
        updated_scripts = []

        for script_id in script_ids:
            try:
                script = await self.update(script_id, update_data)
                updated_scripts.append(script)
            except Exception as e:
                self.logger.warning(f"Failed to update script {script_id}: {e}")
                # Continue with other scripts

        self.logger.info(
            f"Successfully updated {len(updated_scripts)} of {len(script_ids)} scripts"
        )
        return updated_scripts

    # Statistics and analytics
    async def get_execution_statistics(
        self,
        script_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get script execution statistics.

        Args:
            script_id: Optional script ID to get stats for
            start_date: Start date for statistics period
            end_date: End date for statistics period

        Returns:
            Dictionary containing execution statistics

        Raises:
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Getting execution statistics")

        query = self._build_execution_stats_query()
        variables = {}

        if script_id:
            variables["scriptId"] = script_id
        if start_date:
            variables["startDate"] = start_date.isoformat()
        if end_date:
            variables["endDate"] = end_date.isoformat()

        response = await self.client.execute_query(query, variables)
        if not response.get("data"):
            raise SuperOpsAPIError("Failed to get execution statistics", 500, response)

        return response["data"].get("scriptExecutionStatistics", {})

    # Abstract method implementations for ResourceManager
    def _build_get_query(self, **kwargs) -> str:
        """Build GraphQL query for getting a single script."""
        from ..graphql.fragments import create_query_with_fragments, get_script_fields

        detail_level = kwargs.get("detail_level", "full")
        include_executions = kwargs.get("include_executions", False)

        fragment_names = get_script_fields(detail_level, include_executions)

        query = f"""
        query GetScript($id: ID!) {{
            script(id: $id) {{
                ...{list(fragment_names)[0]}
            }}
        }}
        """

        return create_query_with_fragments(query, fragment_names)

    def _build_list_query(self, **kwargs) -> str:
        """Build GraphQL query for listing scripts."""
        from ..graphql.fragments import create_query_with_fragments, get_script_fields

        detail_level = kwargs.get("detail_level", "core")
        include_executions = kwargs.get("include_executions", False)

        fragment_names = get_script_fields(detail_level, include_executions)
        fragment_names.add("PaginationInfo")

        query = f"""
        query ListScripts(
            $page: Int
            $pageSize: Int
            $filters: ScriptFilter
            $sortBy: String
            $sortOrder: SortDirection
        ) {{
            scripts(
                page: $page
                pageSize: $pageSize
                filter: $filters
                sortBy: $sortBy
                sortDirection: $sortOrder
            ) {{
                items {{
                    ...{list(fragment_names)[0]}
                }}
                pagination {{
                    ...PaginationInfo
                }}
            }}
        }}
        """

        return create_query_with_fragments(query, fragment_names)

    def _build_create_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for creating a script."""
        from ..graphql.fragments import create_query_with_fragments, get_script_fields

        detail_level = kwargs.get("detail_level", "full")
        fragment_names = get_script_fields(detail_level)

        mutation = f"""
        mutation CreateScript($input: ScriptInput!) {{
            createScript(input: $input) {{
                ...{list(fragment_names)[0]}
            }}
        }}
        """

        return create_query_with_fragments(mutation, fragment_names)

    def _build_update_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for updating a script."""
        from ..graphql.fragments import create_query_with_fragments, get_script_fields

        detail_level = kwargs.get("detail_level", "full")
        fragment_names = get_script_fields(detail_level)

        mutation = f"""
        mutation UpdateScript($id: ID!, $input: ScriptInput!) {{
            updateScript(id: $id, input: $input) {{
                ...{list(fragment_names)[0]}
            }}
        }}
        """

        return create_query_with_fragments(mutation, fragment_names)

    def _build_delete_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for deleting a script."""
        return """
        mutation DeleteScript($id: ID!) {
            deleteScript(id: $id) {
                success
                message
            }
        }
        """

    def _build_search_query(self, **kwargs) -> str:
        """Build GraphQL query for searching scripts."""
        from ..graphql.fragments import create_query_with_fragments, get_script_fields

        detail_level = kwargs.get("detail_level", "core")
        fragment_names = get_script_fields(detail_level)
        fragment_names.add("PaginationInfo")

        query = f"""
        query SearchScripts(
            $query: String!
            $page: Int
            $pageSize: Int
        ) {{
            searchScripts(
                query: $query
                page: $page
                pageSize: $pageSize
            ) {{
                items {{
                    ...{list(fragment_names)[0]}
                }}
                pagination {{
                    ...PaginationInfo
                }}
            }}
        }}
        """

        return create_query_with_fragments(query, fragment_names)

    # Additional query builders for script-specific operations
    def _build_execute_script_mutation(self) -> str:
        """Build GraphQL mutation for executing a script."""
        from ..graphql.fragments import create_query_with_fragments

        fragment_names = {"ScriptExecutionFields"}

        mutation = """
        mutation ExecuteScript($input: ScriptExecutionInput!) {
            executeScript(input: $input) {
                ...ScriptExecutionFields
            }
        }
        """

        return create_query_with_fragments(mutation, fragment_names)

    def _build_get_execution_query(self) -> str:
        """Build GraphQL query for getting a script execution."""
        from ..graphql.fragments import create_query_with_fragments

        fragment_names = {"ScriptExecutionFullFields"}

        query = """
        query GetScriptExecution($id: ID!) {
            scriptExecution(id: $id) {
                ...ScriptExecutionFullFields
            }
        }
        """

        return create_query_with_fragments(query, fragment_names)

    def _build_cancel_execution_mutation(self) -> str:
        """Build GraphQL mutation for cancelling script execution."""
        return """
        mutation CancelScriptExecution($id: ID!, $reason: String) {
            cancelScriptExecution(id: $id, reason: $reason) {
                success
                message
            }
        }
        """

    def _build_list_executions_query(self) -> str:
        """Build GraphQL query for listing script executions."""
        from ..graphql.fragments import create_query_with_fragments

        fragment_names = {"ScriptExecutionFields", "PaginationInfo"}

        query = """
        query ListScriptExecutions(
            $page: Int
            $pageSize: Int
            $filters: ScriptExecutionFilter
            $sortBy: String
            $sortOrder: SortDirection
        ) {
            scriptExecutions(
                page: $page
                pageSize: $pageSize
                filter: $filters
                sortBy: $sortBy
                sortDirection: $sortOrder
            ) {
                items {
                    ...ScriptExecutionFields
                }
                pagination {
                    ...PaginationInfo
                }
            }
        }
        """

        return create_query_with_fragments(query, fragment_names)

    def _build_create_deployment_mutation(self) -> str:
        """Build GraphQL mutation for creating script deployment."""
        from ..graphql.fragments import create_query_with_fragments

        fragment_names = {"ScriptDeploymentFields"}

        mutation = """
        mutation CreateScriptDeployment($input: ScriptDeploymentInput!) {
            createScriptDeployment(input: $input) {
                ...ScriptDeploymentFields
            }
        }
        """

        return create_query_with_fragments(mutation, fragment_names)

    def _build_update_deployment_mutation(self) -> str:
        """Build GraphQL mutation for updating script deployment."""
        from ..graphql.fragments import create_query_with_fragments

        fragment_names = {"ScriptDeploymentFields"}

        mutation = """
        mutation UpdateScriptDeployment($id: ID!, $input: ScriptDeploymentInput!) {
            updateScriptDeployment(id: $id, input: $input) {
                ...ScriptDeploymentFields
            }
        }
        """

        return create_query_with_fragments(mutation, fragment_names)

    def _build_delete_deployment_mutation(self) -> str:
        """Build GraphQL mutation for deleting script deployment."""
        return """
        mutation DeleteScriptDeployment($id: ID!) {
            deleteScriptDeployment(id: $id) {
                success
                message
            }
        }
        """

    def _build_list_deployments_query(self) -> str:
        """Build GraphQL query for listing script deployments."""
        from ..graphql.fragments import create_query_with_fragments

        fragment_names = {"ScriptDeploymentFields", "PaginationInfo"}

        query = """
        query ListScriptDeployments(
            $page: Int
            $pageSize: Int
            $filters: ScriptDeploymentFilter
            $sortBy: String
            $sortOrder: SortDirection
        ) {
            scriptDeployments(
                page: $page
                pageSize: $pageSize
                filter: $filters
                sortBy: $sortBy
                sortDirection: $sortOrder
            ) {
                items {
                    ...ScriptDeploymentFields
                }
                pagination {
                    ...PaginationInfo
                }
            }
        }
        """

        return create_query_with_fragments(query, fragment_names)

    def _build_create_library_mutation(self) -> str:
        """Build GraphQL mutation for creating script library."""
        from ..graphql.fragments import create_query_with_fragments

        fragment_names = {"ScriptLibraryFields"}

        mutation = """
        mutation CreateScriptLibrary($input: ScriptLibraryInput!) {
            createScriptLibrary(input: $input) {
                ...ScriptLibraryFields
            }
        }
        """

        return create_query_with_fragments(mutation, fragment_names)

    def _build_list_libraries_query(self) -> str:
        """Build GraphQL query for listing script libraries."""
        from ..graphql.fragments import create_query_with_fragments

        fragment_names = {"ScriptLibraryFields", "PaginationInfo"}

        query = """
        query ListScriptLibraries(
            $page: Int
            $pageSize: Int
            $filters: ScriptLibraryFilter
            $sortBy: String
            $sortOrder: SortDirection
        ) {
            scriptLibraries(
                page: $page
                pageSize: $pageSize
                filter: $filters
                sortBy: $sortBy
                sortDirection: $sortOrder
            ) {
                items {
                    ...ScriptLibraryFields
                }
                pagination {
                    ...PaginationInfo
                }
            }
        }
        """

        return create_query_with_fragments(query, fragment_names)

    def _build_execution_stats_query(self) -> str:
        """Build GraphQL query for getting execution statistics."""
        return """
        query GetScriptExecutionStatistics(
            $scriptId: ID
            $startDate: String
            $endDate: String
        ) {
            scriptExecutionStatistics(
                scriptId: $scriptId
                startDate: $startDate
                endDate: $endDate
            ) {
                totalExecutions
                successfulExecutions
                failedExecutions
                averageDuration
                executionsByStatus {
                    status
                    count
                }
                executionsByTrigger {
                    trigger
                    count
                }
                recentExecutions {
                    date
                    count
                    successRate
                }
            }
        }
        """
