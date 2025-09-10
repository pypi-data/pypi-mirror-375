# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Monitoring manager for SuperOps API operations."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..exceptions import SuperOpsAPIError, SuperOpsValidationError
from ..graphql.types import (
    AlertSeverity,
    AlertStatus,
    CheckStatus,
    CheckType,
    MetricType,
    MonitoringAgent,
    MonitoringAgentFilter,
    MonitoringAgentInput,
    MonitoringAgentStatus,
    MonitoringAlert,
    MonitoringAlertFilter,
    MonitoringAlertInput,
    MonitoringCheck,
    MonitoringCheckFilter,
    MonitoringCheckInput,
    MonitoringMetric,
    MonitoringMetricFilter,
    MonitoringMetricInput,
)
from .base import ResourceManager

if TYPE_CHECKING:
    from ..config import SuperOpsConfig


class MonitoringManager(ResourceManager[MonitoringAgent]):
    """Manager for monitoring operations.

    Provides comprehensive monitoring functionality including agent management,
    check creation and management, alert handling, and metric collection.
    """

    def __init__(self, config: "SuperOpsConfig"):
        """Initialize the monitoring manager.

        Args:
            config: SuperOps configuration instance
        """
        # For now, we'll need to create a client from config or get it another way
        # This is a pattern change the user requested
        from ..client import SuperOpsClient

        client = SuperOpsClient(config)
        super().__init__(client, MonitoringAgent, "monitoringAgent")

    # Agent Management (using base ResourceManager methods)
    async def get_agent(
        self, agent_id: str, detail_level: str = "full"
    ) -> Optional[MonitoringAgent]:
        """Get a monitoring agent by ID.

        Args:
            agent_id: Agent ID
            detail_level: Level of detail (summary, core, full)

        Returns:
            MonitoringAgent instance or None if not found

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        return await self.get(agent_id, detail_level=detail_level)

    async def list_agents(
        self,
        filter: Optional[MonitoringAgentFilter] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        detail_level: str = "core",
    ) -> Dict[str, Any]:
        """List monitoring agents.

        Args:
            filter: Filter criteria
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            detail_level: Level of detail (summary, core, full)

        Returns:
            Dictionary containing 'items' (List[MonitoringAgent]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        filters = filter.__dict__ if filter else None
        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
            detail_level=detail_level,
        )

    async def create_agent(
        self,
        name: str,
        host_name: Optional[str] = None,
        ip_address: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        detail_level: str = "full",
    ) -> MonitoringAgent:
        """Create a new monitoring agent.

        Args:
            name: Agent name
            host_name: Host name
            ip_address: IP address
            description: Agent description
            config: Agent configuration
            tags: Agent tags
            detail_level: Level of detail for returned fields

        Returns:
            Created MonitoringAgent instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        data = {
            "name": name,
            "description": description,
            "host_name": host_name,
            "ip_address": ip_address,
            "config": config,
            "tags": tags,
        }

        return await self.create(data, detail_level=detail_level)

    async def update_agent(
        self,
        agent_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        detail_level: str = "full",
    ) -> MonitoringAgent:
        """Update a monitoring agent.

        Args:
            agent_id: Agent ID
            name: New agent name
            description: New description
            config: New configuration
            tags: New tags
            detail_level: Level of detail for returned fields

        Returns:
            Updated MonitoringAgent instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if config is not None:
            data["config"] = config
        if tags is not None:
            data["tags"] = tags

        return await self.update(agent_id, data, detail_level=detail_level)

    async def delete_agent(self, agent_id: str) -> bool:
        """Delete a monitoring agent.

        Args:
            agent_id: Agent ID

        Returns:
            True if deletion was successful

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        return await self.delete(agent_id)

    async def install_agent(
        self,
        host_id: str,
        config: Optional[Dict[str, Any]] = None,
        detail_level: str = "full",
    ) -> MonitoringAgent:
        """Install a monitoring agent on a host.

        Args:
            host_id: Host ID to install agent on
            config: Installation configuration
            detail_level: Level of detail for returned fields

        Returns:
            Installed MonitoringAgent instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not host_id or not isinstance(host_id, str):
            raise SuperOpsValidationError("Host ID must be a non-empty string")

        self.logger.debug(f"Installing monitoring agent on host: {host_id}")

        from ..graphql.builder import create_monitoring_agent_mutation_builder

        builder = create_monitoring_agent_mutation_builder(detail_level)
        mutation, variables = builder.install(host_id, config)

        response = await self.client.execute_mutation(mutation, variables)
        if not response.get("data") or not response["data"].get("installMonitoringAgent"):
            raise SuperOpsAPIError("Failed to install monitoring agent", 500, response)

        return MonitoringAgent.from_dict(response["data"]["installMonitoringAgent"])

    async def get_agents_by_status(
        self,
        status: MonitoringAgentStatus,
        page: int = 1,
        page_size: int = 50,
        detail_level: str = "core",
    ) -> Dict[str, Any]:
        """Get agents filtered by status.

        Args:
            status: Agent status to filter by
            page: Page number (1-based)
            page_size: Number of items per page
            detail_level: Level of detail

        Returns:
            Dictionary containing 'items' (List[MonitoringAgent]) and 'pagination' info
        """
        agent_filter = MonitoringAgentFilter(status=status)
        return await self.list_agents(
            filter=agent_filter, page=page, page_size=page_size, detail_level=detail_level
        )

    async def get_offline_agents(
        self, page: int = 1, page_size: int = 50, detail_level: str = "core"
    ) -> Dict[str, Any]:
        """Get offline agents.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            detail_level: Level of detail

        Returns:
            Dictionary containing 'items' (List[MonitoringAgent]) and 'pagination' info
        """
        return await self.get_agents_by_status(
            MonitoringAgentStatus.OFFLINE, page, page_size, detail_level
        )

    # Check Management
    async def get_check(self, check_id: str, detail_level: str = "full") -> MonitoringCheck:
        """Get a monitoring check by ID.

        Args:
            check_id: Check ID
            detail_level: Level of detail (summary, core, full)

        Returns:
            MonitoringCheck instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not check_id or not isinstance(check_id, str):
            raise SuperOpsValidationError("Check ID must be a non-empty string")

        self.logger.debug(f"Getting monitoring check: {check_id}")

        from ..graphql.builder import create_monitoring_check_query_builder

        builder = create_monitoring_check_query_builder(detail_level)
        query, variables = builder.get(check_id)

        response = await self.client.execute_query(query, variables)
        if not response.get("data") or not response["data"].get("monitoringCheck"):
            raise SuperOpsAPIError(f"Check {check_id} not found", 404, response)

        return MonitoringCheck.from_dict(response["data"]["monitoringCheck"])

    async def list_checks(
        self,
        filter: Optional[MonitoringCheckFilter] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        detail_level: str = "core",
    ) -> Dict[str, Any]:
        """List monitoring checks.

        Args:
            filter: Filter criteria
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            detail_level: Level of detail (summary, core, full)

        Returns:
            Dictionary containing 'items' (List[MonitoringCheck]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Listing monitoring checks")

        from ..graphql.builder import create_monitoring_check_query_builder
        from ..graphql.types import PaginationArgs, SortArgs

        builder = create_monitoring_check_query_builder(detail_level)

        pagination = PaginationArgs(page=page, page_size=page_size) if page or page_size else None
        sort = SortArgs(sort_by=sort_by or "created_at", sort_order=sort_order) if sort_by else None

        query, variables = builder.list(filter=filter, pagination=pagination, sort=sort)

        response = await self.client.execute_query(query, variables)
        if not response.get("data") or not response["data"].get("monitoringChecks"):
            return {"items": [], "pagination": self._empty_pagination()}

        checks_data = response["data"]["monitoringChecks"]
        items = [MonitoringCheck.from_dict(item) for item in checks_data.get("items", [])]
        pagination_info = checks_data.get("pagination", self._empty_pagination())

        return {"items": items, "pagination": pagination_info}

    async def create_check(
        self,
        name: str,
        check_type: CheckType,
        target: Optional[str] = None,
        agent_id: Optional[str] = None,
        description: Optional[str] = None,
        interval: int = 300,
        timeout: int = 30,
        retry_count: int = 3,
        config: Optional[Dict[str, Any]] = None,
        thresholds: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        detail_level: str = "full",
    ) -> MonitoringCheck:
        """Create a new monitoring check.

        Args:
            name: Check name
            check_type: Type of check
            target: Check target (URL, IP, etc.)
            agent_id: Agent to run the check
            description: Check description
            interval: Check interval in seconds
            timeout: Check timeout in seconds
            retry_count: Number of retries on failure
            config: Check-specific configuration
            thresholds: Alert thresholds
            tags: Check tags
            detail_level: Level of detail for returned fields

        Returns:
            Created MonitoringCheck instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not name or not isinstance(name, str):
            raise SuperOpsValidationError("Check name must be a non-empty string")
        if not isinstance(check_type, CheckType):
            raise SuperOpsValidationError("Check type must be a CheckType enum")

        self.logger.debug(f"Creating monitoring check: {name}")

        from ..graphql.builder import create_monitoring_check_mutation_builder

        check_input = MonitoringCheckInput(
            name=name,
            description=description,
            check_type=check_type,
            target=target,
            agent_id=agent_id,
            interval=interval,
            timeout=timeout,
            retry_count=retry_count,
            config=config,
            thresholds=thresholds,
            tags=tags,
        )

        builder = create_monitoring_check_mutation_builder(detail_level)
        mutation, variables = builder.create(check_input)

        response = await self.client.execute_mutation(mutation, variables)
        if not response.get("data") or not response["data"].get("createMonitoringCheck"):
            raise SuperOpsAPIError("Failed to create monitoring check", 500, response)

        return MonitoringCheck.from_dict(response["data"]["createMonitoringCheck"])

    async def update_check(
        self,
        check_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        enabled: Optional[bool] = None,
        interval: Optional[int] = None,
        timeout: Optional[int] = None,
        config: Optional[Dict[str, Any]] = None,
        thresholds: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        detail_level: str = "full",
    ) -> MonitoringCheck:
        """Update a monitoring check.

        Args:
            check_id: Check ID
            name: New check name
            description: New description
            enabled: Whether check is enabled
            interval: New interval in seconds
            timeout: New timeout in seconds
            config: New configuration
            thresholds: New thresholds
            tags: New tags
            detail_level: Level of detail for returned fields

        Returns:
            Updated MonitoringCheck instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not check_id or not isinstance(check_id, str):
            raise SuperOpsValidationError("Check ID must be a non-empty string")

        self.logger.debug(f"Updating monitoring check: {check_id}")

        from ..graphql.builder import create_monitoring_check_mutation_builder

        check_input = MonitoringCheckInput(
            name=name or "",  # Required field
            description=description,
            enabled=enabled,
            interval=interval,
            timeout=timeout,
            config=config,
            thresholds=thresholds,
            tags=tags,
        )

        builder = create_monitoring_check_mutation_builder(detail_level)
        mutation, variables = builder.update(check_id, check_input)

        response = await self.client.execute_mutation(mutation, variables)
        if not response.get("data") or not response["data"].get("updateMonitoringCheck"):
            raise SuperOpsAPIError("Failed to update monitoring check", 500, response)

        return MonitoringCheck.from_dict(response["data"]["updateMonitoringCheck"])

    async def delete_check(self, check_id: str) -> Dict[str, Any]:
        """Delete a monitoring check.

        Args:
            check_id: Check ID

        Returns:
            Dictionary with success status and message

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not check_id or not isinstance(check_id, str):
            raise SuperOpsValidationError("Check ID must be a non-empty string")

        self.logger.debug(f"Deleting monitoring check: {check_id}")

        from ..graphql.builder import create_monitoring_check_mutation_builder

        builder = create_monitoring_check_mutation_builder()
        mutation, variables = builder.delete(check_id)

        response = await self.client.execute_mutation(mutation, variables)
        if not response.get("data") or not response["data"].get("deleteMonitoringCheck"):
            raise SuperOpsAPIError("Failed to delete monitoring check", 500, response)

        return response["data"]["deleteMonitoringCheck"]

    async def run_check(self, check_id: str) -> Dict[str, Any]:
        """Manually run a monitoring check.

        Args:
            check_id: Check ID

        Returns:
            Dictionary with execution results

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not check_id or not isinstance(check_id, str):
            raise SuperOpsValidationError("Check ID must be a non-empty string")

        self.logger.debug(f"Running monitoring check: {check_id}")

        from ..graphql.builder import create_monitoring_check_mutation_builder

        builder = create_monitoring_check_mutation_builder()
        mutation, variables = builder.run_check(check_id)

        response = await self.client.execute_mutation(mutation, variables)
        if not response.get("data") or not response["data"].get("runMonitoringCheck"):
            raise SuperOpsAPIError("Failed to run monitoring check", 500, response)

        return response["data"]["runMonitoringCheck"]

    async def get_checks_by_status(
        self,
        status: CheckStatus,
        page: int = 1,
        page_size: int = 50,
        detail_level: str = "core",
    ) -> Dict[str, Any]:
        """Get checks filtered by status.

        Args:
            status: Check status to filter by
            page: Page number (1-based)
            page_size: Number of items per page
            detail_level: Level of detail

        Returns:
            Dictionary containing 'items' (List[MonitoringCheck]) and 'pagination' info
        """
        check_filter = MonitoringCheckFilter(status=status)
        return await self.list_checks(
            filter=check_filter, page=page, page_size=page_size, detail_level=detail_level
        )

    async def get_failing_checks(
        self, page: int = 1, page_size: int = 50, detail_level: str = "core"
    ) -> Dict[str, Any]:
        """Get checks that are in warning or critical state.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            detail_level: Level of detail

        Returns:
            Dictionary containing 'items' (List[MonitoringCheck]) and 'pagination' info
        """
        from ..graphql.types import PaginationArgs, SortArgs

        builder_class = await self._get_check_query_builder()
        builder = builder_class(detail_level)

        pagination = PaginationArgs(page=page, page_size=page_size)
        sort = SortArgs(sort_by="last_check", sort_order="desc")

        # Build custom query for failing checks
        query = """
        query GetFailingChecks($pagination: PaginationInput, $sort: SortInput) {
            monitoringChecks(
                filter: {
                    status_in: ["WARNING", "CRITICAL"]
                    enabled: true
                }
                pagination: $pagination
                sort: $sort
            ) {
                items {
                    id
                    name
                    status
                    checkType
                    target
                    lastCheck
                    lastResult
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

        response = await self.client.execute_query(
            query, {"pagination": pagination.__dict__, "sort": sort.__dict__}
        )

        if not response.get("data") or not response["data"].get("monitoringChecks"):
            return {"items": [], "pagination": self._empty_pagination()}

        checks_data = response["data"]["monitoringChecks"]
        items = [MonitoringCheck.from_dict(item) for item in checks_data.get("items", [])]
        pagination_info = checks_data.get("pagination", self._empty_pagination())

        return {"items": items, "pagination": pagination_info}

    # Alert Management
    async def get_alert(self, alert_id: str, detail_level: str = "full") -> MonitoringAlert:
        """Get a monitoring alert by ID.

        Args:
            alert_id: Alert ID
            detail_level: Level of detail (summary, core, full)

        Returns:
            MonitoringAlert instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not alert_id or not isinstance(alert_id, str):
            raise SuperOpsValidationError("Alert ID must be a non-empty string")

        self.logger.debug(f"Getting monitoring alert: {alert_id}")

        from ..graphql.builder import create_monitoring_alert_query_builder

        builder = create_monitoring_alert_query_builder(detail_level)
        query, variables = builder.get(alert_id)

        response = await self.client.execute_query(query, variables)
        if not response.get("data") or not response["data"].get("monitoringAlert"):
            raise SuperOpsAPIError(f"Alert {alert_id} not found", 404, response)

        return MonitoringAlert.from_dict(response["data"]["monitoringAlert"])

    async def list_alerts(
        self,
        filter: Optional[MonitoringAlertFilter] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        detail_level: str = "core",
    ) -> Dict[str, Any]:
        """List monitoring alerts.

        Args:
            filter: Filter criteria
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            detail_level: Level of detail (summary, core, full)

        Returns:
            Dictionary containing 'items' (List[MonitoringAlert]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Listing monitoring alerts")

        from ..graphql.builder import create_monitoring_alert_query_builder
        from ..graphql.types import PaginationArgs, SortArgs

        builder = create_monitoring_alert_query_builder(detail_level)

        pagination = PaginationArgs(page=page, page_size=page_size) if page or page_size else None
        sort = (
            SortArgs(sort_by=sort_by or "triggered_at", sort_order=sort_order) if sort_by else None
        )

        query, variables = builder.list(filter=filter, pagination=pagination, sort=sort)

        response = await self.client.execute_query(query, variables)
        if not response.get("data") or not response["data"].get("monitoringAlerts"):
            return {"items": [], "pagination": self._empty_pagination()}

        alerts_data = response["data"]["monitoringAlerts"]
        items = [MonitoringAlert.from_dict(item) for item in alerts_data.get("items", [])]
        pagination_info = alerts_data.get("pagination", self._empty_pagination())

        return {"items": items, "pagination": pagination_info}

    async def create_alert(
        self,
        name: str,
        check_id: str,
        severity: AlertSeverity = AlertSeverity.MEDIUM,
        condition: Optional[Dict[str, Any]] = None,
        notification_config: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        detail_level: str = "full",
    ) -> MonitoringAlert:
        """Create a new monitoring alert.

        Args:
            name: Alert name
            check_id: Associated check ID
            severity: Alert severity
            condition: Alert condition rules
            notification_config: Notification configuration
            description: Alert description
            tags: Alert tags
            detail_level: Level of detail for returned fields

        Returns:
            Created MonitoringAlert instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not name or not isinstance(name, str):
            raise SuperOpsValidationError("Alert name must be a non-empty string")
        if not check_id or not isinstance(check_id, str):
            raise SuperOpsValidationError("Check ID must be a non-empty string")

        self.logger.debug(f"Creating monitoring alert: {name}")

        from ..graphql.builder import create_monitoring_alert_mutation_builder

        alert_input = MonitoringAlertInput(
            name=name,
            description=description,
            check_id=check_id,
            severity=severity,
            condition=condition,
            notification_config=notification_config,
            tags=tags,
        )

        builder = create_monitoring_alert_mutation_builder(detail_level)
        mutation, variables = builder.create(alert_input)

        response = await self.client.execute_mutation(mutation, variables)
        if not response.get("data") or not response["data"].get("createMonitoringAlert"):
            raise SuperOpsAPIError("Failed to create monitoring alert", 500, response)

        return MonitoringAlert.from_dict(response["data"]["createMonitoringAlert"])

    async def acknowledge_alert(
        self,
        alert_id: str,
        comment: Optional[str] = None,
        detail_level: str = "full",
    ) -> MonitoringAlert:
        """Acknowledge a monitoring alert.

        Args:
            alert_id: Alert ID
            comment: Optional acknowledgment comment
            detail_level: Level of detail for returned fields

        Returns:
            Updated MonitoringAlert instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not alert_id or not isinstance(alert_id, str):
            raise SuperOpsValidationError("Alert ID must be a non-empty string")

        self.logger.debug(f"Acknowledging monitoring alert: {alert_id}")

        from ..graphql.builder import create_monitoring_alert_mutation_builder

        builder = create_monitoring_alert_mutation_builder(detail_level)
        mutation, variables = builder.acknowledge(alert_id, comment)

        response = await self.client.execute_mutation(mutation, variables)
        if not response.get("data") or not response["data"].get("acknowledgeMonitoringAlert"):
            raise SuperOpsAPIError("Failed to acknowledge monitoring alert", 500, response)

        return MonitoringAlert.from_dict(response["data"]["acknowledgeMonitoringAlert"])

    async def resolve_alert(
        self,
        alert_id: str,
        comment: Optional[str] = None,
        detail_level: str = "full",
    ) -> MonitoringAlert:
        """Resolve a monitoring alert.

        Args:
            alert_id: Alert ID
            comment: Optional resolution comment
            detail_level: Level of detail for returned fields

        Returns:
            Updated MonitoringAlert instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not alert_id or not isinstance(alert_id, str):
            raise SuperOpsValidationError("Alert ID must be a non-empty string")

        self.logger.debug(f"Resolving monitoring alert: {alert_id}")

        from ..graphql.builder import create_monitoring_alert_mutation_builder

        builder = create_monitoring_alert_mutation_builder(detail_level)
        mutation, variables = builder.resolve(alert_id, comment)

        response = await self.client.execute_mutation(mutation, variables)
        if not response.get("data") or not response["data"].get("resolveMonitoringAlert"):
            raise SuperOpsAPIError("Failed to resolve monitoring alert", 500, response)

        return MonitoringAlert.from_dict(response["data"]["resolveMonitoringAlert"])

    async def silence_alert(
        self,
        alert_id: str,
        duration_minutes: int,
        comment: Optional[str] = None,
        detail_level: str = "full",
    ) -> MonitoringAlert:
        """Silence a monitoring alert for a specified duration.

        Args:
            alert_id: Alert ID
            duration_minutes: Duration to silence in minutes
            comment: Optional silence comment
            detail_level: Level of detail for returned fields

        Returns:
            Updated MonitoringAlert instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not alert_id or not isinstance(alert_id, str):
            raise SuperOpsValidationError("Alert ID must be a non-empty string")
        if not isinstance(duration_minutes, int) or duration_minutes <= 0:
            raise SuperOpsValidationError("Duration must be a positive integer")

        self.logger.debug(f"Silencing monitoring alert: {alert_id} for {duration_minutes} minutes")

        from ..graphql.builder import create_monitoring_alert_mutation_builder

        builder = create_monitoring_alert_mutation_builder(detail_level)
        mutation, variables = builder.silence(alert_id, duration_minutes, comment)

        response = await self.client.execute_mutation(mutation, variables)
        if not response.get("data") or not response["data"].get("silenceMonitoringAlert"):
            raise SuperOpsAPIError("Failed to silence monitoring alert", 500, response)

        return MonitoringAlert.from_dict(response["data"]["silenceMonitoringAlert"])

    async def get_active_alerts(
        self, page: int = 1, page_size: int = 50, detail_level: str = "core"
    ) -> Dict[str, Any]:
        """Get active alerts.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            detail_level: Level of detail

        Returns:
            Dictionary containing 'items' (List[MonitoringAlert]) and 'pagination' info
        """
        alert_filter = MonitoringAlertFilter(status=AlertStatus.ACTIVE)
        return await self.list_alerts(
            filter=alert_filter, page=page, page_size=page_size, detail_level=detail_level
        )

    async def get_critical_alerts(
        self, page: int = 1, page_size: int = 50, detail_level: str = "core"
    ) -> Dict[str, Any]:
        """Get critical alerts.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            detail_level: Level of detail

        Returns:
            Dictionary containing 'items' (List[MonitoringAlert]) and 'pagination' info
        """
        alert_filter = MonitoringAlertFilter(
            severity=AlertSeverity.CRITICAL, status=AlertStatus.ACTIVE
        )
        return await self.list_alerts(
            filter=alert_filter, page=page, page_size=page_size, detail_level=detail_level
        )

    # Metric Management
    async def get_metric(self, metric_id: str, detail_level: str = "full") -> MonitoringMetric:
        """Get a monitoring metric by ID.

        Args:
            metric_id: Metric ID
            detail_level: Level of detail (summary, core, full)

        Returns:
            MonitoringMetric instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not metric_id or not isinstance(metric_id, str):
            raise SuperOpsValidationError("Metric ID must be a non-empty string")

        self.logger.debug(f"Getting monitoring metric: {metric_id}")

        from ..graphql.builder import create_monitoring_metric_query_builder

        builder = create_monitoring_metric_query_builder(detail_level)
        query, variables = builder.get(metric_id)

        response = await self.client.execute_query(query, variables)
        if not response.get("data") or not response["data"].get("monitoringMetric"):
            raise SuperOpsAPIError(f"Metric {metric_id} not found", 404, response)

        return MonitoringMetric.from_dict(response["data"]["monitoringMetric"])

    async def list_metrics(
        self,
        filter: Optional[MonitoringMetricFilter] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        detail_level: str = "core",
    ) -> Dict[str, Any]:
        """List monitoring metrics.

        Args:
            filter: Filter criteria
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            detail_level: Level of detail (summary, core, full)

        Returns:
            Dictionary containing 'items' (List[MonitoringMetric]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Listing monitoring metrics")

        from ..graphql.builder import create_monitoring_metric_query_builder
        from ..graphql.types import PaginationArgs, SortArgs

        builder = create_monitoring_metric_query_builder(detail_level)

        pagination = PaginationArgs(page=page, page_size=page_size) if page or page_size else None
        sort = SortArgs(sort_by=sort_by or "timestamp", sort_order=sort_order) if sort_by else None

        query, variables = builder.list(filter=filter, pagination=pagination, sort=sort)

        response = await self.client.execute_query(query, variables)
        if not response.get("data") or not response["data"].get("monitoringMetrics"):
            return {"items": [], "pagination": self._empty_pagination()}

        metrics_data = response["data"]["monitoringMetrics"]
        items = [MonitoringMetric.from_dict(item) for item in metrics_data.get("items", [])]
        pagination_info = metrics_data.get("pagination", self._empty_pagination())

        return {"items": items, "pagination": pagination_info}

    async def create_metric(
        self,
        name: str,
        metric_type: MetricType = MetricType.GAUGE,
        unit: Optional[str] = None,
        description: Optional[str] = None,
        agent_id: Optional[str] = None,
        retention_period: Optional[int] = None,
        tags: Optional[List[str]] = None,
        detail_level: str = "full",
    ) -> MonitoringMetric:
        """Create a new monitoring metric.

        Args:
            name: Metric name
            metric_type: Type of metric
            unit: Metric unit
            description: Metric description
            agent_id: Associated agent ID
            retention_period: Data retention period in days
            tags: Metric tags
            detail_level: Level of detail for returned fields

        Returns:
            Created MonitoringMetric instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not name or not isinstance(name, str):
            raise SuperOpsValidationError("Metric name must be a non-empty string")

        self.logger.debug(f"Creating monitoring metric: {name}")

        from ..graphql.builder import create_monitoring_metric_mutation_builder

        metric_input = MonitoringMetricInput(
            name=name,
            description=description,
            metric_type=metric_type,
            unit=unit,
            agent_id=agent_id,
            retention_period=retention_period,
            tags=tags,
        )

        builder = create_monitoring_metric_mutation_builder(detail_level)
        mutation, variables = builder.create(metric_input)

        response = await self.client.execute_mutation(mutation, variables)
        if not response.get("data") or not response["data"].get("createMonitoringMetric"):
            raise SuperOpsAPIError("Failed to create monitoring metric", 500, response)

        return MonitoringMetric.from_dict(response["data"]["createMonitoringMetric"])

    async def record_metric_value(
        self,
        metric_name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        timestamp: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Record a value for a metric.

        Args:
            metric_name: Name of the metric
            value: Metric value
            labels: Optional metric labels
            timestamp: Optional timestamp (defaults to now)

        Returns:
            Dictionary with success status and message

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not metric_name or not isinstance(metric_name, str):
            raise SuperOpsValidationError("Metric name must be a non-empty string")
        if not isinstance(value, (int, float)):
            raise SuperOpsValidationError("Value must be a number")

        self.logger.debug(f"Recording metric value: {metric_name} = {value}")

        from ..graphql.builder import create_monitoring_metric_mutation_builder

        timestamp_str = timestamp.isoformat() if timestamp else None

        builder = create_monitoring_metric_mutation_builder()
        mutation, variables = builder.record_value(metric_name, value, labels, timestamp_str)

        response = await self.client.execute_mutation(mutation, variables)
        if not response.get("data") or not response["data"].get("recordMetricValue"):
            raise SuperOpsAPIError("Failed to record metric value", 500, response)

        return response["data"]["recordMetricValue"]

    async def get_dashboard_data(
        self,
        agent_ids: Optional[List[str]] = None,
        check_ids: Optional[List[str]] = None,
        time_range_minutes: int = 60,
    ) -> Dict[str, Any]:
        """Get monitoring dashboard data.

        Args:
            agent_ids: Optional list of agent IDs to filter by
            check_ids: Optional list of check IDs to filter by
            time_range_minutes: Time range in minutes to look back

        Returns:
            Dictionary with dashboard summary data

        Raises:
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug(
            f"Getting dashboard data for {time_range_minutes} minutes"
            f" (agents: {len(agent_ids) if agent_ids else 0}, checks: {len(check_ids) if check_ids else 0})"
        )

        from ..graphql.builder import create_monitoring_metric_query_builder

        builder = create_monitoring_metric_query_builder()
        query, variables = builder.get_dashboard_data(agent_ids, check_ids, time_range_minutes)

        response = await self.client.execute_query(query, variables)
        if not response.get("data") or not response["data"].get("monitoringDashboard"):
            raise SuperOpsAPIError("Failed to get dashboard data", 500, response)

        return response["data"]["monitoringDashboard"]

    # Maintenance Window Support
    async def create_maintenance_window(
        self,
        name: str,
        start_time: datetime,
        end_time: datetime,
        agent_ids: Optional[List[str]] = None,
        check_ids: Optional[List[str]] = None,
        description: Optional[str] = None,
        suppress_alerts: bool = True,
    ) -> Dict[str, Any]:
        """Create a maintenance window to suppress alerts.

        Args:
            name: Maintenance window name
            start_time: Start time
            end_time: End time
            agent_ids: Optional list of agent IDs to include
            check_ids: Optional list of check IDs to include
            description: Optional description
            suppress_alerts: Whether to suppress alerts during window

        Returns:
            Dictionary with maintenance window details

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not name or not isinstance(name, str):
            raise SuperOpsValidationError("Maintenance window name must be a non-empty string")
        if not isinstance(start_time, datetime) or not isinstance(end_time, datetime):
            raise SuperOpsValidationError("Start and end times must be datetime objects")
        if start_time >= end_time:
            raise SuperOpsValidationError("Start time must be before end time")

        self.logger.debug(f"Creating maintenance window: {name}")

        mutation = """
        mutation CreateMaintenanceWindow(
            $name: String!
            $description: String
            $startTime: String!
            $endTime: String!
            $agentIds: [ID!]
            $checkIds: [ID!]
            $suppressAlerts: Boolean!
        ) {
            createMaintenanceWindow(
                name: $name
                description: $description
                startTime: $startTime
                endTime: $endTime
                agentIds: $agentIds
                checkIds: $checkIds
                suppressAlerts: $suppressAlerts
            ) {
                id
                name
                description
                startTime
                endTime
                suppressAlerts
                agentIds
                checkIds
                createdAt
            }
        }
        """

        variables = {
            "name": name,
            "description": description,
            "startTime": start_time.isoformat(),
            "endTime": end_time.isoformat(),
            "agentIds": agent_ids,
            "checkIds": check_ids,
            "suppressAlerts": suppress_alerts,
        }

        response = await self.client.execute_mutation(mutation, variables)
        if not response.get("data") or not response["data"].get("createMaintenanceWindow"):
            raise SuperOpsAPIError("Failed to create maintenance window", 500, response)

        return response["data"]["createMaintenanceWindow"]

    # Threshold Management
    async def set_check_thresholds(
        self,
        check_id: str,
        warning_threshold: Optional[Dict[str, Any]] = None,
        critical_threshold: Optional[Dict[str, Any]] = None,
    ) -> MonitoringCheck:
        """Set warning and critical thresholds for a check.

        Args:
            check_id: Check ID
            warning_threshold: Warning threshold configuration
            critical_threshold: Critical threshold configuration

        Returns:
            Updated MonitoringCheck instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not check_id or not isinstance(check_id, str):
            raise SuperOpsValidationError("Check ID must be a non-empty string")

        thresholds = {}
        if warning_threshold:
            thresholds["warning"] = warning_threshold
        if critical_threshold:
            thresholds["critical"] = critical_threshold

        return await self.update_check(check_id, thresholds=thresholds)

    # Utility methods
    def _empty_pagination(self) -> Dict[str, Any]:
        """Return empty pagination info."""
        return {
            "page": 1,
            "pageSize": 0,
            "total": 0,
            "hasNextPage": False,
            "hasPreviousPage": False,
        }

    async def _get_check_query_builder(self):
        """Get the check query builder class."""
        from ..graphql.builder import MonitoringCheckQueryBuilder

        return MonitoringCheckQueryBuilder

    # Abstract method implementations required by ResourceManager

    def _build_get_query(self, **kwargs) -> str:
        """Build GraphQL query for getting a single monitoring agent."""
        detail_level = kwargs.get("detail_level", "full")

        base_fields = [
            "id",
            "name",
            "description",
            "hostName",
            "ipAddress",
            "status",
            "version",
            "lastSeen",
            "config",
            "tags",
            "createdAt",
            "updatedAt",
        ]

        if detail_level == "full":
            base_fields.extend(
                [
                    "installedAt",
                    "uninstalledAt",
                    "isActive",
                    "metrics",
                    "checks {id name status}",
                ]
            )
        elif detail_level == "core":
            base_fields.extend(
                [
                    "isActive",
                    "lastCheckIn",
                ]
            )

        fields_str = "\n        ".join(base_fields)

        return f"""
            query GetMonitoringAgent($id: ID!) {{
                monitoringAgent(id: $id) {{
                    {fields_str}
                }}
            }}
        """

    def _build_list_query(self, **kwargs) -> str:
        """Build GraphQL query for listing monitoring agents."""
        detail_level = kwargs.get("detail_level", "core")

        base_fields = [
            "id",
            "name",
            "description",
            "hostName",
            "ipAddress",
            "status",
            "version",
            "lastSeen",
            "tags",
            "createdAt",
            "updatedAt",
        ]

        if detail_level == "full":
            base_fields.extend(
                [
                    "installedAt",
                    "uninstalledAt",
                    "isActive",
                    "config",
                    "metrics",
                ]
            )
        elif detail_level == "core":
            base_fields.extend(
                [
                    "isActive",
                    "lastCheckIn",
                ]
            )

        fields_str = "\n            ".join(base_fields)

        return f"""
            query ListMonitoringAgents(
                $page: Int!
                $pageSize: Int!
                $filters: MonitoringAgentFilter
                $sortBy: String
                $sortOrder: SortOrder
            ) {{
                monitoringAgents(
                    page: $page
                    pageSize: $pageSize
                    filters: $filters
                    sortBy: $sortBy
                    sortOrder: $sortOrder
                ) {{
                    items {{
                        {fields_str}
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
        """

    def _build_create_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for creating a monitoring agent."""
        detail_level = kwargs.get("detail_level", "full")

        fields = [
            "id",
            "name",
            "description",
            "hostName",
            "ipAddress",
            "status",
            "version",
            "config",
            "tags",
            "createdAt",
            "updatedAt",
        ]

        if detail_level == "full":
            fields.extend(
                [
                    "installedAt",
                    "isActive",
                    "lastSeen",
                ]
            )

        fields_str = "\n            ".join(fields)

        return f"""
            mutation CreateMonitoringAgent($input: MonitoringAgentInput!) {{
                createMonitoringAgent(input: $input) {{
                    {fields_str}
                }}
            }}
        """

    def _build_update_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for updating a monitoring agent."""
        detail_level = kwargs.get("detail_level", "full")

        fields = [
            "id",
            "name",
            "description",
            "hostName",
            "ipAddress",
            "status",
            "version",
            "config",
            "tags",
            "createdAt",
            "updatedAt",
        ]

        if detail_level == "full":
            fields.extend(
                [
                    "installedAt",
                    "isActive",
                    "lastSeen",
                ]
            )

        fields_str = "\n            ".join(fields)

        return f"""
            mutation UpdateMonitoringAgent($id: ID!, $input: MonitoringAgentInput!) {{
                updateMonitoringAgent(id: $id, input: $input) {{
                    {fields_str}
                }}
            }}
        """

    def _build_delete_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for deleting a monitoring agent."""
        return """
            mutation DeleteMonitoringAgent($id: ID!) {
                deleteMonitoringAgent(id: $id) {
                    success
                    message
                }
            }
        """

    def _build_search_query(self, **kwargs) -> str:
        """Build GraphQL query for searching monitoring agents."""
        detail_level = kwargs.get("detail_level", "core")

        fields = [
            "id",
            "name",
            "description",
            "hostName",
            "ipAddress",
            "status",
            "version",
            "lastSeen",
            "tags",
            "createdAt",
            "updatedAt",
        ]

        if detail_level == "full":
            fields.extend(
                [
                    "installedAt",
                    "isActive",
                    "config",
                ]
            )
        elif detail_level == "core":
            fields.extend(
                [
                    "isActive",
                    "lastCheckIn",
                ]
            )

        fields_str = "\n            ".join(fields)

        return f"""
            query SearchMonitoringAgents(
                $query: String!
                $page: Int!
                $pageSize: Int!
            ) {{
                searchMonitoringAgents(
                    query: $query
                    page: $page
                    pageSize: $pageSize
                ) {{
                    items {{
                        {fields_str}
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
        """

    def _validate_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data for monitoring agent creation."""
        validated = data.copy()

        # Required fields
        if not validated.get("name"):
            raise SuperOpsValidationError("Agent name is required")

        # Validate IP address format if provided
        ip_address = validated.get("ip_address")
        if ip_address:
            import ipaddress

            try:
                ipaddress.ip_address(ip_address)
            except ValueError:
                raise SuperOpsValidationError(f"Invalid IP address format: {ip_address}")

        # Validate tags format if provided
        tags = validated.get("tags")
        if tags is not None:
            if not isinstance(tags, list):
                raise SuperOpsValidationError("Tags must be a list")
            for tag in tags:
                if not isinstance(tag, str):
                    raise SuperOpsValidationError("All tags must be strings")

        return validated

    def _validate_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data for monitoring agent updates."""
        validated = data.copy()

        # Validate IP address format if provided
        ip_address = validated.get("ip_address")
        if ip_address:
            import ipaddress

            try:
                ipaddress.ip_address(ip_address)
            except ValueError:
                raise SuperOpsValidationError(f"Invalid IP address format: {ip_address}")

        # Validate tags format if provided
        tags = validated.get("tags")
        if tags is not None:
            if not isinstance(tags, list):
                raise SuperOpsValidationError("Tags must be a list")
            for tag in tags:
                if not isinstance(tag, str):
                    raise SuperOpsValidationError("All tags must be strings")

        return validated
