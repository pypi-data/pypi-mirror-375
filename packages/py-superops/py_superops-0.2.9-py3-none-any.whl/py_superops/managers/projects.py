# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Project manager for SuperOps API operations."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..exceptions import SuperOpsValidationError
from ..graphql.types import Project, ProjectPriority, ProjectStatus
from .base import ResourceManager

if TYPE_CHECKING:
    from ..client import SuperOpsClient


class ProjectsManager(ResourceManager[Project]):
    """Manager for project operations.

    Provides high-level methods for managing SuperOps projects including
    CRUD operations, project-specific workflows, milestone tracking,
    task management, and time tracking.
    """

    def __init__(self, client: SuperOpsClient):
        """Initialize the projects manager.

        Args:
            client: SuperOps client instance
        """
        super().__init__(client, Project, "project")

    async def get_by_name(self, name: str, client_id: Optional[str] = None) -> Optional[Project]:
        """Get a project by name.

        Args:
            name: Project name to search for
            client_id: Optional client ID to limit search scope

        Returns:
            Project instance or None if not found

        Raises:
            SuperOpsValidationError: If name is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not name or not isinstance(name, str):
            raise SuperOpsValidationError("Project name must be a non-empty string")

        self.logger.debug(f"Getting project by name: {name}")

        # Build search query
        search_query = f'name:"{name}"'
        if client_id:
            search_query += f' client_id:"{client_id}"'

        # Use search with exact name match
        results = await self.search(search_query, page_size=1)

        # Return first exact match if any
        for project in results["items"]:
            if project.name == name and (not client_id or project.client_id == client_id):
                return project

        return None

    async def get_by_client(
        self,
        client_id: str,
        status: Optional[ProjectStatus] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get projects for a specific client.

        Args:
            client_id: Client ID
            status: Optional project status filter
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: name)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Project]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If client_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not client_id or not isinstance(client_id, str):
            raise SuperOpsValidationError(f"Invalid client ID: {client_id}")

        self.logger.debug(f"Getting projects for client: {client_id}")

        filters = {"client_id": client_id}
        if status:
            filters["status"] = status.value

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
        )

    async def get_active_projects(
        self,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get all active (in-progress) projects.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: name)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Project]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug(f"Getting active projects - page: {page}, size: {page_size}")

        filters = {"status": ProjectStatus.IN_PROGRESS.value}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
        )

    async def get_overdue_projects(
        self,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get all overdue projects.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: due_date)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Project]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug(f"Getting overdue projects - page: {page}, size: {page_size}")

        current_date = datetime.now()
        filters = {"due_before": current_date}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "due_date",
            sort_order=sort_order,
        )

    async def get_high_priority_projects(
        self,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get high priority projects.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: priority)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Project]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug(f"Getting high priority projects - page: {page}, size: {page_size}")

        filters = {"priority": ProjectPriority.HIGH.value}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "priority",
            sort_order=sort_order,
        )

    async def link_to_client(self, project_id: str, client_id: str) -> Project:
        """Link a project to a client.

        Args:
            project_id: The project ID
            client_id: The client ID to link to

        Returns:
            Updated project instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If project doesn't exist
        """
        if not project_id or not isinstance(project_id, str):
            raise SuperOpsValidationError(f"Invalid project ID: {project_id}")
        if not client_id or not isinstance(client_id, str):
            raise SuperOpsValidationError(f"Invalid client ID: {client_id}")

        self.logger.debug(f"Linking project {project_id} to client {client_id}")

        return await self.update(project_id, {"client_id": client_id})

    async def link_to_contract(self, project_id: str, contract_id: str) -> Project:
        """Link a project to a contract.

        Args:
            project_id: The project ID
            contract_id: The contract ID to link to

        Returns:
            Updated project instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If project doesn't exist
        """
        if not project_id or not isinstance(project_id, str):
            raise SuperOpsValidationError(f"Invalid project ID: {project_id}")
        if not contract_id or not isinstance(contract_id, str):
            raise SuperOpsValidationError(f"Invalid contract ID: {contract_id}")

        self.logger.debug(f"Linking project {project_id} to contract {contract_id}")

        return await self.update(project_id, {"contract_id": contract_id})

    async def unlink_from_contract(self, project_id: str) -> Project:
        """Unlink a project from its contract.

        Args:
            project_id: The project ID

        Returns:
            Updated project instance

        Raises:
            SuperOpsValidationError: If project_id is invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If project doesn't exist
        """
        if not project_id or not isinstance(project_id, str):
            raise SuperOpsValidationError(f"Invalid project ID: {project_id}")

        self.logger.debug(f"Unlinking project {project_id} from contract")

        return await self.update(project_id, {"contract_id": None})

    async def assign_to_user(self, project_id: str, user_id: str) -> Project:
        """Assign a project to a user.

        Args:
            project_id: The project ID
            user_id: The user ID to assign to

        Returns:
            Updated project instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If project doesn't exist
        """
        if not project_id or not isinstance(project_id, str):
            raise SuperOpsValidationError(f"Invalid project ID: {project_id}")
        if not user_id or not isinstance(user_id, str):
            raise SuperOpsValidationError(f"Invalid user ID: {user_id}")

        self.logger.debug(f"Assigning project {project_id} to user {user_id}")

        return await self.update(project_id, {"assigned_to": user_id})

    async def set_manager(self, project_id: str, manager_id: str) -> Project:
        """Set the project manager.

        Args:
            project_id: The project ID
            manager_id: The manager user ID

        Returns:
            Updated project instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If project doesn't exist
        """
        if not project_id or not isinstance(project_id, str):
            raise SuperOpsValidationError(f"Invalid project ID: {project_id}")
        if not manager_id or not isinstance(manager_id, str):
            raise SuperOpsValidationError(f"Invalid manager ID: {manager_id}")

        self.logger.debug(f"Setting project {project_id} manager to {manager_id}")

        return await self.update(project_id, {"manager_id": manager_id})

    async def update_status(self, project_id: str, status: ProjectStatus) -> Project:
        """Update project status.

        Args:
            project_id: The project ID
            status: New project status

        Returns:
            Updated project instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If project doesn't exist
        """
        if not project_id or not isinstance(project_id, str):
            raise SuperOpsValidationError(f"Invalid project ID: {project_id}")
        if not isinstance(status, ProjectStatus):
            raise SuperOpsValidationError("Status must be a ProjectStatus enum")

        self.logger.debug(f"Updating project {project_id} status to {status.value}")

        return await self.update(project_id, {"status": status.value})

    async def update_priority(self, project_id: str, priority: ProjectPriority) -> Project:
        """Update project priority.

        Args:
            project_id: The project ID
            priority: New project priority

        Returns:
            Updated project instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If project doesn't exist
        """
        if not project_id or not isinstance(project_id, str):
            raise SuperOpsValidationError(f"Invalid project ID: {project_id}")
        if not isinstance(priority, ProjectPriority):
            raise SuperOpsValidationError("Priority must be a ProjectPriority enum")

        self.logger.debug(f"Updating project {project_id} priority to {priority.value}")

        return await self.update(project_id, {"priority": priority.value})

    async def update_progress(self, project_id: str, progress_percentage: int) -> Project:
        """Update project progress percentage.

        Args:
            project_id: The project ID
            progress_percentage: Progress percentage (0-100)

        Returns:
            Updated project instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If project doesn't exist
        """
        if not project_id or not isinstance(project_id, str):
            raise SuperOpsValidationError(f"Invalid project ID: {project_id}")
        if (
            not isinstance(progress_percentage, int)
            or progress_percentage < 0
            or progress_percentage > 100
        ):
            raise SuperOpsValidationError(
                "Progress percentage must be an integer between 0 and 100"
            )

        self.logger.debug(f"Updating project {project_id} progress to {progress_percentage}%")

        return await self.update(project_id, {"progress_percentage": progress_percentage})

    async def update_budget(self, project_id: str, budget: float) -> Project:
        """Update project budget.

        Args:
            project_id: The project ID
            budget: New budget amount

        Returns:
            Updated project instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If project doesn't exist
        """
        if not project_id or not isinstance(project_id, str):
            raise SuperOpsValidationError(f"Invalid project ID: {project_id}")
        if not isinstance(budget, (int, float)) or budget < 0:
            raise SuperOpsValidationError("Budget must be a positive number")

        self.logger.debug(f"Updating project {project_id} budget to {budget}")

        return await self.update(project_id, {"budget": float(budget)})

    async def set_dates(
        self,
        project_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        due_date: Optional[datetime] = None,
    ) -> Project:
        """Set project dates.

        Args:
            project_id: The project ID
            start_date: Project start date
            end_date: Project end date
            due_date: Project due date

        Returns:
            Updated project instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If project doesn't exist
        """
        if not project_id or not isinstance(project_id, str):
            raise SuperOpsValidationError(f"Invalid project ID: {project_id}")

        self.logger.debug(f"Setting project {project_id} dates")

        update_data = {}
        if start_date is not None:
            update_data["start_date"] = start_date
        if end_date is not None:
            update_data["end_date"] = end_date
        if due_date is not None:
            update_data["due_date"] = due_date

        if not update_data:
            raise SuperOpsValidationError("At least one date must be provided")

        return await self.update(project_id, update_data)

    async def add_tag(self, project_id: str, tag: str) -> Project:
        """Add a tag to a project.

        Args:
            project_id: The project ID
            tag: Tag to add

        Returns:
            Updated project instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not project_id or not isinstance(project_id, str):
            raise SuperOpsValidationError(f"Invalid project ID: {project_id}")
        if not tag or not isinstance(tag, str):
            raise SuperOpsValidationError("Tag must be a non-empty string")

        self.logger.debug(f"Adding tag '{tag}' to project: {project_id}")

        # Get current project to access existing tags
        project = await self.get(project_id)
        if not project:
            raise SuperOpsValidationError(f"Project not found: {project_id}")

        # Add tag if not already present
        current_tags = project.tags or []
        if tag not in current_tags:
            current_tags.append(tag)
            return await self.update(project_id, {"tags": current_tags})

        return project

    async def remove_tag(self, project_id: str, tag: str) -> Project:
        """Remove a tag from a project.

        Args:
            project_id: The project ID
            tag: Tag to remove

        Returns:
            Updated project instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not project_id or not isinstance(project_id, str):
            raise SuperOpsValidationError(f"Invalid project ID: {project_id}")
        if not tag or not isinstance(tag, str):
            raise SuperOpsValidationError("Tag must be a non-empty string")

        self.logger.debug(f"Removing tag '{tag}' from project: {project_id}")

        # Get current project to access existing tags
        project = await self.get(project_id)
        if not project:
            raise SuperOpsValidationError(f"Project not found: {project_id}")

        # Remove tag if present
        current_tags = project.tags or []
        if tag in current_tags:
            current_tags.remove(tag)
            return await self.update(project_id, {"tags": current_tags})

        return project

    async def bulk_update_status(
        self, project_ids: List[str], status: ProjectStatus
    ) -> List[Project]:
        """Update status for multiple projects.

        Args:
            project_ids: List of project IDs
            status: New status for all projects

        Returns:
            List of updated project instances

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If any API request fails
        """
        if not project_ids:
            raise SuperOpsValidationError("Project IDs list cannot be empty")
        if not isinstance(project_ids, list):
            raise SuperOpsValidationError("Project IDs must be a list")
        if not isinstance(status, ProjectStatus):
            raise SuperOpsValidationError("Status must be a ProjectStatus enum")

        self.logger.debug(f"Bulk updating status for {len(project_ids)} projects to {status.value}")

        updated_projects = []
        for project_id in project_ids:
            try:
                updated_project = await self.update(project_id, {"status": status.value})
                updated_projects.append(updated_project)
            except Exception as e:
                self.logger.error(f"Failed to update project {project_id}: {e}")
                # Continue with other projects

        self.logger.info(
            f"Successfully updated {len(updated_projects)} out of {len(project_ids)} projects"
        )
        return updated_projects

    # Timeline and reporting methods

    async def get_project_timeline(self, project_id: str) -> Dict[str, Any]:
        """Get project timeline with milestones and tasks.

        Args:
            project_id: The project ID

        Returns:
            Dictionary containing project timeline data

        Raises:
            SuperOpsValidationError: If project_id is invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If project doesn't exist
        """
        if not project_id or not isinstance(project_id, str):
            raise SuperOpsValidationError(f"Invalid project ID: {project_id}")

        self.logger.debug(f"Getting timeline for project: {project_id}")

        # Get project with milestones and tasks
        project = await self.get(project_id, include_milestones=True, include_tasks=True)
        if not project:
            raise SuperOpsValidationError(f"Project not found: {project_id}")

        # Build timeline data
        timeline = {
            "project": project,
            "milestones": getattr(project, "milestones", []),
            "tasks": getattr(project, "tasks", []),
            "duration_days": None,
            "progress_summary": {
                "overall_progress": project.progress_percentage or 0,
                "completed_milestones": 0,
                "total_milestones": 0,
                "completed_tasks": 0,
                "total_tasks": 0,
            },
        }

        # Calculate duration
        if project.start_date and project.end_date:
            timeline["duration_days"] = (project.end_date - project.start_date).days

        # Calculate progress summary
        milestones = timeline["milestones"]
        if milestones:
            timeline["progress_summary"]["total_milestones"] = len(milestones)
            timeline["progress_summary"]["completed_milestones"] = sum(
                1 for m in milestones if getattr(m, "is_completed", False)
            )

        tasks = timeline["tasks"]
        if tasks:
            timeline["progress_summary"]["total_tasks"] = len(tasks)
            timeline["progress_summary"]["completed_tasks"] = sum(
                1 for t in tasks if getattr(t, "status", None) == TicketStatus.CLOSED
            )

        return timeline

    async def get_project_analytics(self, project_id: str) -> Dict[str, Any]:
        """Get project analytics and metrics.

        Args:
            project_id: The project ID

        Returns:
            Dictionary containing project analytics data

        Raises:
            SuperOpsValidationError: If project_id is invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If project doesn't exist
        """
        if not project_id or not isinstance(project_id, str):
            raise SuperOpsValidationError(f"Invalid project ID: {project_id}")

        self.logger.debug(f"Getting analytics for project: {project_id}")

        # Get project with all related data
        project = await self.get(
            project_id, include_milestones=True, include_tasks=True, include_time_entries=True
        )
        if not project:
            raise SuperOpsValidationError(f"Project not found: {project_id}")

        # Build analytics data
        analytics = {
            "project_id": project_id,
            "project_name": project.name,
            "status": project.status,
            "priority": project.priority,
            "progress_percentage": project.progress_percentage or 0,
            "budget": {
                "allocated": project.budget or 0,
                "spent": 0,
                "remaining": 0,
            },
            "time": {
                "estimated_hours": project.estimated_hours or 0,
                "actual_hours": project.actual_hours or 0,
                "billable_hours": 0,
                "efficiency_ratio": 0,
            },
            "milestones": {
                "total": 0,
                "completed": 0,
                "overdue": 0,
                "completion_rate": 0,
            },
            "tasks": {
                "total": 0,
                "completed": 0,
                "in_progress": 0,
                "overdue": 0,
                "completion_rate": 0,
            },
            "dates": {
                "start_date": project.start_date,
                "end_date": project.end_date,
                "due_date": project.due_date,
                "days_elapsed": None,
                "days_remaining": None,
                "is_overdue": False,
            },
        }

        # Calculate date metrics
        now = datetime.now()
        if project.start_date:
            analytics["dates"]["days_elapsed"] = (now - project.start_date).days

        if project.due_date:
            days_remaining = (project.due_date - now).days
            analytics["dates"]["days_remaining"] = days_remaining
            analytics["dates"]["is_overdue"] = days_remaining < 0

        # Calculate milestone metrics
        milestones = project.milestones if hasattr(project, "milestones") else []
        self._calculate_milestone_analytics(analytics, milestones, now)

        # Calculate task metrics
        tasks = project.tasks if hasattr(project, "tasks") else []
        self._calculate_task_analytics(analytics, tasks, now)

        # Calculate time and budget metrics
        time_entries = project.time_entries if hasattr(project, "time_entries") else []
        if time_entries:
            total_billable_hours = sum(
                (t.billable_hours or 0) if hasattr(t, "billable_hours") else 0
                for t in time_entries
                if not hasattr(t, "is_billable") or t.is_billable
            )
            analytics["time"]["billable_hours"] = total_billable_hours

            # Calculate budget spent based on billable hours and rates
            total_spent = sum(
                (
                    ((t.billable_hours or 0) * (t.rate or 0))
                    if hasattr(t, "billable_hours") and hasattr(t, "rate")
                    else 0
                )
                for t in time_entries
                if not hasattr(t, "is_billable") or t.is_billable
            )
            analytics["budget"]["spent"] = total_spent
            analytics["budget"]["remaining"] = max(
                0, analytics["budget"]["allocated"] - total_spent
            )

        # Calculate efficiency ratio
        if analytics["time"]["estimated_hours"] > 0:
            analytics["time"]["efficiency_ratio"] = (
                (analytics["time"]["estimated_hours"] / analytics["time"]["actual_hours"])
                if analytics["time"]["actual_hours"] > 0
                else 0
            )

        return analytics

    # Protected methods for GraphQL query building

    def _build_get_query(self, **kwargs) -> str:
        """Build GraphQL query for getting a single project."""
        include_milestones = kwargs.get("include_milestones", False)
        include_tasks = kwargs.get("include_tasks", False)
        include_time_entries = kwargs.get("include_time_entries", False)

        fields = [
            "id",
            "clientId",
            "contractId",
            "name",
            "description",
            "status",
            "priority",
            "siteId",
            "assignedTo",
            "managerId",
            "startDate",
            "endDate",
            "dueDate",
            "budget",
            "billingRate",
            "progressPercentage",
            "estimatedHours",
            "actualHours",
            "notes",
            "tags",
            "customFields",
            "createdAt",
            "updatedAt",
        ]

        if include_milestones:
            fields.append(
                """
                milestones {
                    id
                    projectId
                    name
                    description
                    dueDate
                    completionDate
                    isCompleted
                    progressPercentage
                    orderIndex
                    notes
                    createdAt
                    updatedAt
                }
            """
            )

        if include_tasks:
            fields.append(
                """
                tasks {
                    id
                    projectId
                    milestoneId
                    name
                    description
                    status
                    priority
                    assignedTo
                    startDate
                    dueDate
                    completionDate
                    estimatedHours
                    actualHours
                    progressPercentage
                    orderIndex
                    notes
                    tags
                    createdAt
                    updatedAt
                }
            """
            )

        if include_time_entries:
            fields.append(
                """
                timeEntries {
                    id
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
                    createdAt
                    updatedAt
                }
            """
            )

        field_str = "\n        ".join(fields)

        return f"""
            query GetProject($id: ID!) {{
                project(id: $id) {{
                    {field_str}
                }}
            }}
        """

    def _build_list_query(self, **kwargs) -> str:
        """Build GraphQL query for listing projects."""
        return """
            query ListProjects(
                $page: Int!
                $pageSize: Int!
                $filters: ProjectFilter
                $sortBy: String
                $sortOrder: SortOrder
            ) {
                projects(
                    page: $page
                    pageSize: $pageSize
                    filters: $filters
                    sortBy: $sortBy
                    sortOrder: $sortOrder
                ) {
                    items {
                        id
                        clientId
                        contractId
                        name
                        description
                        status
                        priority
                        siteId
                        assignedTo
                        managerId
                        startDate
                        endDate
                        dueDate
                        budget
                        billingRate
                        progressPercentage
                        estimatedHours
                        actualHours
                        notes
                        tags
                        customFields
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
        """Build GraphQL mutation for creating a project."""
        return """
            mutation CreateProject($input: CreateProjectInput!) {
                createProject(input: $input) {
                    id
                    clientId
                    contractId
                    name
                    description
                    status
                    priority
                    siteId
                    assignedTo
                    managerId
                    startDate
                    endDate
                    dueDate
                    budget
                    billingRate
                    progressPercentage
                    estimatedHours
                    actualHours
                    notes
                    tags
                    customFields
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_update_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for updating a project."""
        return """
            mutation UpdateProject($id: ID!, $input: UpdateProjectInput!) {
                updateProject(id: $id, input: $input) {
                    id
                    clientId
                    contractId
                    name
                    description
                    status
                    priority
                    siteId
                    assignedTo
                    managerId
                    startDate
                    endDate
                    dueDate
                    budget
                    billingRate
                    progressPercentage
                    estimatedHours
                    actualHours
                    notes
                    tags
                    customFields
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_delete_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for deleting a project."""
        return """
            mutation DeleteProject($id: ID!) {
                deleteProject(id: $id) {
                    success
                    message
                }
            }
        """

    def _build_search_query(self, **kwargs) -> str:
        """Build GraphQL query for searching projects."""
        return """
            query SearchProjects(
                $query: String!
                $page: Int!
                $pageSize: Int!
            ) {
                searchProjects(
                    query: $query
                    page: $page
                    pageSize: $pageSize
                ) {
                    items {
                        id
                        clientId
                        contractId
                        name
                        description
                        status
                        priority
                        siteId
                        assignedTo
                        managerId
                        startDate
                        endDate
                        dueDate
                        budget
                        billingRate
                        progressPercentage
                        estimatedHours
                        actualHours
                        notes
                        tags
                        customFields
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
        """Validate data for project creation."""
        validated = data.copy()

        # Required fields
        if not validated.get("name"):
            raise SuperOpsValidationError("Project name is required")
        if not validated.get("client_id"):
            raise SuperOpsValidationError("Client ID is required")

        # Validate status if provided
        status = validated.get("status")
        if status and status not in [s.value for s in ProjectStatus]:
            raise SuperOpsValidationError(f"Invalid project status: {status}")

        # Validate priority if provided
        priority = validated.get("priority")
        if priority and priority not in [p.value for p in ProjectPriority]:
            raise SuperOpsValidationError(f"Invalid project priority: {priority}")

        # Validate progress percentage if provided
        progress = validated.get("progress_percentage")
        if progress is not None and (
            not isinstance(progress, int) or progress < 0 or progress > 100
        ):
            raise SuperOpsValidationError(
                "Progress percentage must be an integer between 0 and 100"
            )

        # Validate budget if provided
        budget = validated.get("budget")
        if budget is not None and (not isinstance(budget, (int, float)) or budget < 0):
            raise SuperOpsValidationError("Budget must be a positive number")

        return validated

    def _calculate_milestone_analytics(
        self, analytics: Dict[str, Any], milestones: List, now: datetime
    ) -> None:
        """Calculate milestone analytics metrics."""
        if not milestones:
            return

        analytics["milestones"]["total"] = len(milestones)
        completed = sum(1 for m in milestones if hasattr(m, "is_completed") and m.is_completed)
        analytics["milestones"]["completed"] = completed

        # Count overdue milestones
        overdue = sum(
            1
            for m in milestones
            if (
                hasattr(m, "due_date")
                and m.due_date
                and m.due_date < now
                and (not hasattr(m, "is_completed") or not m.is_completed)
            )
        )
        analytics["milestones"]["overdue"] = overdue

        if analytics["milestones"]["total"] > 0:
            analytics["milestones"]["completion_rate"] = (
                completed / analytics["milestones"]["total"]
            ) * 100

    def _calculate_task_analytics(
        self, analytics: Dict[str, Any], tasks: List, now: datetime
    ) -> None:
        """Calculate task analytics metrics."""
        if not tasks:
            return

        analytics["tasks"]["total"] = len(tasks)
        # Simplified status checking without TicketStatus dependency
        completed = sum(
            1 for t in tasks if hasattr(t, "status") and t.status in ["CLOSED", "COMPLETED"]
        )
        in_progress = sum(1 for t in tasks if hasattr(t, "status") and t.status == "IN_PROGRESS")

        overdue = sum(
            1
            for t in tasks
            if (
                hasattr(t, "due_date")
                and t.due_date
                and t.due_date < now
                and hasattr(t, "status")
                and t.status not in ["CLOSED", "COMPLETED", "RESOLVED"]
            )
        )

        analytics["tasks"]["completed"] = completed
        analytics["tasks"]["in_progress"] = in_progress
        analytics["tasks"]["overdue"] = overdue

        if analytics["tasks"]["total"] > 0:
            analytics["tasks"]["completion_rate"] = (completed / analytics["tasks"]["total"]) * 100

    def _validate_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data for project updates."""
        validated = data.copy()

        # Validate status if provided
        status = validated.get("status")
        if status and status not in [s.value for s in ProjectStatus]:
            raise SuperOpsValidationError(f"Invalid project status: {status}")

        # Validate priority if provided
        priority = validated.get("priority")
        if priority and priority not in [p.value for p in ProjectPriority]:
            raise SuperOpsValidationError(f"Invalid project priority: {priority}")

        # Validate progress percentage if provided
        progress = validated.get("progress_percentage")
        if progress is not None and (
            not isinstance(progress, int) or progress < 0 or progress > 100
        ):
            raise SuperOpsValidationError(
                "Progress percentage must be an integer between 0 and 100"
            )

        # Validate budget if provided
        budget = validated.get("budget")
        if budget is not None and (not isinstance(budget, (int, float)) or budget < 0):
            raise SuperOpsValidationError("Budget must be a positive number")

        return validated
