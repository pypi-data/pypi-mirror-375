# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Tests for MonitoringManager class."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from py_superops.exceptions import (
    SuperOpsAPIError,
    SuperOpsResourceNotFoundError,
    SuperOpsValidationError,
)
from py_superops.graphql.types import (
    AlertSeverity,
    AlertStatus,
    CheckStatus,
    CheckType,
    MetricType,
    MonitoringAgentStatus,
)
from py_superops.managers import MonitoringManager


class TestMonitoringManager:
    """Test the MonitoringManager class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock SuperOps client."""
        client = AsyncMock()
        client.execute_query = AsyncMock()
        client.execute_mutation = AsyncMock()
        return client

    @pytest.fixture
    def monitoring_manager(self, mock_client):
        """Create a MonitoringManager instance."""
        return MonitoringManager(mock_client)

    @pytest.fixture
    def sample_agent_response(self) -> Dict[str, Any]:
        """Sample monitoring agent response data."""
        return {
            "data": {
                "monitoringAgent": {
                    "id": "agent-123",
                    "name": "Web Server Monitor",
                    "hostname": "webserver-01.example.com",
                    "ip_address": "192.168.1.100",
                    "status": "ACTIVE",
                    "version": "2.1.0",
                    "last_heartbeat": "2024-01-15T12:00:00Z",
                    "installed_at": "2024-01-01T00:00:00Z",
                    "configuration": {
                        "check_interval": 60,
                        "timeout": 30,
                        "max_retries": 3,
                    },
                    "tags": ["production", "webserver"],
                    "check_count": 5,
                    "alert_count": 2,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }

    @pytest.fixture
    def sample_check_response(self) -> Dict[str, Any]:
        """Sample monitoring check response data."""
        return {
            "data": {
                "monitoringCheck": {
                    "id": "check-456",
                    "name": "HTTP Health Check",
                    "check_type": "HTTP",
                    "agent_id": "agent-123",
                    "status": "ENABLED",
                    "configuration": {
                        "url": "https://example.com/health",
                        "method": "GET",
                        "expected_status": 200,
                        "timeout": 30,
                    },
                    "check_interval": 300,
                    "retry_interval": 60,
                    "max_retries": 3,
                    "is_critical": True,
                    "tags": ["health", "api"],
                    "last_check": "2024-01-15T11:55:00Z",
                    "next_check": "2024-01-15T12:00:00Z",
                    "alert_count": 1,
                    "success_count": 98,
                    "failure_count": 2,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-15T11:55:00Z",
                }
            }
        }

    @pytest.fixture
    def sample_alert_response(self) -> Dict[str, Any]:
        """Sample monitoring alert response data."""
        return {
            "data": {
                "monitoringAlert": {
                    "id": "alert-789",
                    "check_id": "check-456",
                    "severity": "HIGH",
                    "status": "TRIGGERED",
                    "message": "HTTP check failed with status 500",
                    "details": {
                        "response_time": 5000,
                        "status_code": 500,
                        "error": "Internal Server Error",
                    },
                    "triggered_at": "2024-01-15T11:55:00Z",
                    "acknowledged_at": None,
                    "resolved_at": None,
                    "escalated_at": None,
                    "silenced_until": None,
                    "notification_sent": True,
                    "notification_count": 1,
                    "created_at": "2024-01-15T11:55:00Z",
                    "updated_at": "2024-01-15T11:55:00Z",
                }
            }
        }

    @pytest.fixture
    def sample_metric_response(self) -> Dict[str, Any]:
        """Sample monitoring metric response data."""
        return {
            "data": {
                "monitoringMetric": {
                    "id": "metric-321",
                    "name": "cpu_usage",
                    "metric_type": "GAUGE",
                    "agent_id": "agent-123",
                    "value": 75.5,
                    "unit": "percent",
                    "tags": {"host": "webserver-01", "environment": "production"},
                    "timestamp": "2024-01-15T12:00:00Z",
                    "check_id": None,
                    "threshold_config": {
                        "warning_threshold": 80.0,
                        "critical_threshold": 90.0,
                    },
                    "created_at": "2024-01-15T12:00:00Z",
                }
            }
        }

    @pytest.fixture
    def sample_agent_list_response(self) -> Dict[str, Any]:
        """Sample agent list response data."""
        return {
            "data": {
                "monitoringAgents": {
                    "items": [
                        {
                            "id": "agent-1",
                            "name": "Agent 1",
                            "hostname": "server-01",
                            "status": "ACTIVE",
                            "last_heartbeat": "2024-01-15T12:00:00Z",
                            "check_count": 3,
                            "alert_count": 0,
                        },
                        {
                            "id": "agent-2",
                            "name": "Agent 2",
                            "hostname": "server-02",
                            "status": "INACTIVE",
                            "last_heartbeat": "2024-01-15T10:00:00Z",
                            "check_count": 5,
                            "alert_count": 2,
                        },
                    ],
                    "pagination": {
                        "page": 1,
                        "pageSize": 50,
                        "total": 2,
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                    },
                }
            }
        }

    # Test Agent CRUD Operations

    @pytest.mark.asyncio
    async def test_get_agent_success(self, monitoring_manager, mock_client, sample_agent_response):
        """Test successful agent retrieval."""
        mock_client.execute_query.return_value = sample_agent_response

        result = await monitoring_manager.get_agent("agent-123")

        assert result is not None
        assert result.id == "agent-123"
        assert result.name == "Web Server Monitor"
        assert result.status == MonitoringAgentStatus.ACTIVE
        assert result.hostname == "webserver-01.example.com"

        mock_client.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_agent_not_found(self, monitoring_manager, mock_client):
        """Test agent not found scenario."""
        mock_client.execute_query.return_value = {"data": {"monitoringAgent": None}}

        result = await monitoring_manager.get_agent("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_agent_invalid_id(self, monitoring_manager):
        """Test get agent with invalid ID."""
        with pytest.raises(SuperOpsValidationError, match="Agent ID must be a non-empty string"):
            await monitoring_manager.get_agent("")

        with pytest.raises(SuperOpsValidationError, match="Agent ID must be a non-empty string"):
            await monitoring_manager.get_agent(None)

    @pytest.mark.asyncio
    async def test_list_agents_success(
        self, monitoring_manager, mock_client, sample_agent_list_response
    ):
        """Test successful agent listing."""
        mock_client.execute_query.return_value = sample_agent_list_response

        result = await monitoring_manager.list_agents()

        assert "items" in result
        assert "pagination" in result
        assert len(result["items"]) == 2
        assert result["items"][0].id == "agent-1"
        assert result["items"][1].id == "agent-2"

        mock_client.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_agents_with_filters(
        self, monitoring_manager, mock_client, sample_agent_list_response
    ):
        """Test agent listing with filters."""
        mock_client.execute_query.return_value = sample_agent_list_response

        filters = {
            "status": MonitoringAgentStatus.ACTIVE,
            "hostname": "webserver-01",
        }

        result = await monitoring_manager.list_agents(filters=filters)

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["status"] == MonitoringAgentStatus.ACTIVE
        assert variables["filters"]["hostname"] == "webserver-01"

    @pytest.mark.asyncio
    async def test_install_agent_success(self, monitoring_manager, mock_client):
        """Test successful agent installation."""
        install_response = {
            "data": {
                "installMonitoringAgent": {
                    "id": "agent-new-123",
                    "name": "New Agent",
                    "hostname": "newserver.example.com",
                    "ip_address": "192.168.1.200",
                    "status": "INSTALLING",
                    "version": "2.1.0",
                    "configuration": {"check_interval": 60},
                    "created_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = install_response

        result = await monitoring_manager.install_agent(
            name="New Agent",
            hostname="newserver.example.com",
            ip_address="192.168.1.200",
        )

        assert result.id == "agent-new-123"
        assert result.name == "New Agent"
        assert result.status == MonitoringAgentStatus.INSTALLING

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_install_agent_validation_error(self, monitoring_manager):
        """Test agent installation with invalid data."""
        with pytest.raises(SuperOpsValidationError, match="Name must be a non-empty string"):
            await monitoring_manager.install_agent(name="", hostname="test.com")

        with pytest.raises(SuperOpsValidationError, match="Hostname must be a non-empty string"):
            await monitoring_manager.install_agent(name="Test", hostname="")

    @pytest.mark.asyncio
    async def test_update_agent_success(self, monitoring_manager, mock_client):
        """Test successful agent update."""
        update_response = {
            "data": {
                "updateMonitoringAgent": {
                    "id": "agent-123",
                    "name": "Updated Agent",
                    "configuration": {"check_interval": 120, "timeout": 45},
                    "tags": ["updated", "production"],
                    "updated_at": "2024-01-15T12:30:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = update_response

        result = await monitoring_manager.update_agent(
            "agent-123",
            name="Updated Agent",
            configuration={"check_interval": 120, "timeout": 45},
            tags=["updated", "production"],
        )

        assert result.id == "agent-123"
        assert result.name == "Updated Agent"

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_uninstall_agent_success(self, monitoring_manager, mock_client):
        """Test successful agent uninstallation."""
        uninstall_response = {
            "data": {
                "uninstallMonitoringAgent": {
                    "success": True,
                    "message": "Agent uninstalled successfully",
                }
            }
        }
        mock_client.execute_mutation.return_value = uninstall_response

        result = await monitoring_manager.uninstall_agent("agent-123")

        assert result is True

        mock_client.execute_mutation.assert_called_once()

    # Test Check CRUD Operations

    @pytest.mark.asyncio
    async def test_get_check_success(self, monitoring_manager, mock_client, sample_check_response):
        """Test successful check retrieval."""
        mock_client.execute_query.return_value = sample_check_response

        result = await monitoring_manager.get_check("check-456")

        assert result is not None
        assert result.id == "check-456"
        assert result.name == "HTTP Health Check"
        assert result.check_type == CheckType.HTTP
        assert result.status == CheckStatus.ENABLED

        mock_client.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_check_success(self, monitoring_manager, mock_client):
        """Test successful check creation."""
        create_response = {
            "data": {
                "createMonitoringCheck": {
                    "id": "check-new-456",
                    "name": "New HTTP Check",
                    "check_type": "HTTP",
                    "agent_id": "agent-123",
                    "status": "ENABLED",
                    "configuration": {
                        "url": "https://example.com/api",
                        "method": "GET",
                        "expected_status": 200,
                    },
                    "check_interval": 300,
                    "is_critical": False,
                    "created_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = create_response

        result = await monitoring_manager.create_check(
            name="New HTTP Check",
            check_type=CheckType.HTTP,
            agent_id="agent-123",
            configuration={
                "url": "https://example.com/api",
                "method": "GET",
                "expected_status": 200,
            },
            check_interval=300,
        )

        assert result.id == "check-new-456"
        assert result.name == "New HTTP Check"
        assert result.check_type == CheckType.HTTP

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_check_validation_error(self, monitoring_manager):
        """Test check creation with invalid data."""
        with pytest.raises(SuperOpsValidationError, match="Name must be a non-empty string"):
            await monitoring_manager.create_check(
                name="",
                check_type=CheckType.HTTP,
                agent_id="agent-123",
                configuration={},
            )

        with pytest.raises(SuperOpsValidationError, match="Agent ID must be a non-empty string"):
            await monitoring_manager.create_check(
                name="Test Check",
                check_type=CheckType.HTTP,
                agent_id="",
                configuration={},
            )

    @pytest.mark.asyncio
    async def test_update_check_success(self, monitoring_manager, mock_client):
        """Test successful check update."""
        update_response = {
            "data": {
                "updateMonitoringCheck": {
                    "id": "check-456",
                    "name": "Updated HTTP Check",
                    "check_interval": 600,
                    "is_critical": True,
                    "updated_at": "2024-01-15T12:30:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = update_response

        result = await monitoring_manager.update_check(
            "check-456",
            name="Updated HTTP Check",
            check_interval=600,
            is_critical=True,
        )

        assert result.id == "check-456"
        assert result.name == "Updated HTTP Check"

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_check_success(self, monitoring_manager, mock_client):
        """Test successful check deletion."""
        delete_response = {
            "data": {
                "deleteMonitoringCheck": {
                    "success": True,
                    "message": "Check deleted successfully",
                }
            }
        }
        mock_client.execute_mutation.return_value = delete_response

        result = await monitoring_manager.delete_check("check-456")

        assert result is True

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_check_success(self, monitoring_manager, mock_client):
        """Test successful manual check run."""
        run_response = {
            "data": {
                "runMonitoringCheck": {
                    "success": True,
                    "message": "Check executed successfully",
                    "result": {
                        "status": "PASS",
                        "response_time": 150,
                        "details": {"status_code": 200},
                    },
                }
            }
        }
        mock_client.execute_mutation.return_value = run_response

        result = await monitoring_manager.run_check("check-456")

        assert result["success"] is True
        assert result["result"]["status"] == "PASS"

        mock_client.execute_mutation.assert_called_once()

    # Test Alert Operations

    @pytest.mark.asyncio
    async def test_get_alert_success(self, monitoring_manager, mock_client, sample_alert_response):
        """Test successful alert retrieval."""
        mock_client.execute_query.return_value = sample_alert_response

        result = await monitoring_manager.get_alert("alert-789")

        assert result is not None
        assert result.id == "alert-789"
        assert result.severity == AlertSeverity.HIGH
        assert result.status == AlertStatus.TRIGGERED

        mock_client.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_acknowledge_alert_success(self, monitoring_manager, mock_client):
        """Test successful alert acknowledgment."""
        ack_response = {
            "data": {
                "acknowledgeMonitoringAlert": {
                    "id": "alert-789",
                    "status": "ACKNOWLEDGED",
                    "acknowledged_at": "2024-01-15T12:00:00Z",
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = ack_response

        result = await monitoring_manager.acknowledge_alert("alert-789", "Investigating the issue")

        assert result.id == "alert-789"
        assert result.status == AlertStatus.ACKNOWLEDGED

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_resolve_alert_success(self, monitoring_manager, mock_client):
        """Test successful alert resolution."""
        resolve_response = {
            "data": {
                "resolveMonitoringAlert": {
                    "id": "alert-789",
                    "status": "RESOLVED",
                    "resolved_at": "2024-01-15T12:30:00Z",
                    "updated_at": "2024-01-15T12:30:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = resolve_response

        result = await monitoring_manager.resolve_alert(
            "alert-789", "Issue fixed by restarting service"
        )

        assert result.id == "alert-789"
        assert result.status == AlertStatus.RESOLVED

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_silence_alert_success(self, monitoring_manager, mock_client):
        """Test successful alert silencing."""
        silence_response = {
            "data": {
                "silenceMonitoringAlert": {
                    "id": "alert-789",
                    "status": "SILENCED",
                    "silenced_until": "2024-01-15T14:00:00Z",
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = silence_response

        result = await monitoring_manager.silence_alert("alert-789", duration_minutes=120)

        assert result.id == "alert-789"
        assert result.status == AlertStatus.SILENCED

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_escalate_alert_success(self, monitoring_manager, mock_client):
        """Test successful alert escalation."""
        escalate_response = {
            "data": {
                "escalateMonitoringAlert": {
                    "id": "alert-789",
                    "severity": "CRITICAL",
                    "escalated_at": "2024-01-15T12:00:00Z",
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = escalate_response

        result = await monitoring_manager.escalate_alert("alert-789", AlertSeverity.CRITICAL)

        assert result.id == "alert-789"
        assert result.severity == AlertSeverity.CRITICAL

        mock_client.execute_mutation.assert_called_once()

    # Test Metric Operations

    @pytest.mark.asyncio
    async def test_get_metric_success(
        self, monitoring_manager, mock_client, sample_metric_response
    ):
        """Test successful metric retrieval."""
        mock_client.execute_query.return_value = sample_metric_response

        result = await monitoring_manager.get_metric("metric-321")

        assert result is not None
        assert result.id == "metric-321"
        assert result.name == "cpu_usage"
        assert result.metric_type == MetricType.GAUGE
        assert result.value == 75.5

        mock_client.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_record_metric_value_success(self, monitoring_manager, mock_client):
        """Test successful metric value recording."""
        record_response = {
            "data": {
                "recordMonitoringMetric": {
                    "id": "metric-new-321",
                    "name": "memory_usage",
                    "metric_type": "GAUGE",
                    "agent_id": "agent-123",
                    "value": 65.0,
                    "unit": "percent",
                    "timestamp": "2024-01-15T12:00:00Z",
                    "created_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = record_response

        result = await monitoring_manager.record_metric_value(
            name="memory_usage",
            metric_type=MetricType.GAUGE,
            agent_id="agent-123",
            value=65.0,
            unit="percent",
        )

        assert result.id == "metric-new-321"
        assert result.name == "memory_usage"
        assert result.value == 65.0

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_metric_history_success(self, monitoring_manager, mock_client):
        """Test successful metric history retrieval."""
        history_response = {
            "data": {
                "monitoringMetricHistory": {
                    "items": [
                        {
                            "timestamp": "2024-01-15T11:00:00Z",
                            "value": 70.0,
                            "tags": {"host": "webserver-01"},
                        },
                        {
                            "timestamp": "2024-01-15T12:00:00Z",
                            "value": 75.5,
                            "tags": {"host": "webserver-01"},
                        },
                    ],
                    "pagination": {"total": 2},
                }
            }
        }
        mock_client.execute_query.return_value = history_response

        result = await monitoring_manager.get_metric_history(
            agent_id="agent-123",
            metric_name="cpu_usage",
            start_time="2024-01-15T10:00:00Z",
            end_time="2024-01-15T13:00:00Z",
        )

        assert len(result["items"]) == 2
        assert result["items"][0]["value"] == 70.0
        assert result["items"][1]["value"] == 75.5

        mock_client.execute_query.assert_called_once()

    # Test Dashboard Operations

    @pytest.mark.asyncio
    async def test_get_dashboard_data_success(self, monitoring_manager, mock_client):
        """Test successful dashboard data retrieval."""
        dashboard_response = {
            "data": {
                "monitoringDashboard": {
                    "summary": {
                        "total_agents": 10,
                        "active_agents": 8,
                        "total_checks": 50,
                        "passing_checks": 45,
                        "failing_checks": 3,
                        "disabled_checks": 2,
                        "active_alerts": 5,
                        "critical_alerts": 1,
                    },
                    "recent_alerts": [
                        {
                            "id": "alert-1",
                            "severity": "HIGH",
                            "message": "HTTP check failed",
                            "triggered_at": "2024-01-15T11:55:00Z",
                        }
                    ],
                    "top_metrics": [
                        {
                            "name": "cpu_usage",
                            "current_value": 75.5,
                            "threshold_status": "WARNING",
                        }
                    ],
                }
            }
        }
        mock_client.execute_query.return_value = dashboard_response

        result = await monitoring_manager.get_dashboard_data()

        assert result["summary"]["total_agents"] == 10
        assert result["summary"]["active_alerts"] == 5
        assert len(result["recent_alerts"]) == 1
        assert len(result["top_metrics"]) == 1

        mock_client.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_agent_status_summary_success(self, monitoring_manager, mock_client):
        """Test successful agent status summary retrieval."""
        status_response = {
            "data": {
                "monitoringAgentStatusSummary": {
                    "total": 10,
                    "by_status": {
                        "ACTIVE": 8,
                        "INACTIVE": 1,
                        "ERROR": 1,
                    },
                    "recent_heartbeats": 8,
                    "overdue_heartbeats": 2,
                }
            }
        }
        mock_client.execute_query.return_value = status_response

        result = await monitoring_manager.get_agent_status_summary()

        assert result["total"] == 10
        assert result["by_status"]["ACTIVE"] == 8
        assert result["overdue_heartbeats"] == 2

        mock_client.execute_query.assert_called_once()

    # Test Threshold Management

    @pytest.mark.asyncio
    async def test_set_metric_threshold_success(self, monitoring_manager, mock_client):
        """Test successful metric threshold setting."""
        threshold_response = {
            "data": {
                "setMetricThreshold": {
                    "id": "threshold-123",
                    "metric_name": "cpu_usage",
                    "agent_id": "agent-123",
                    "warning_threshold": 80.0,
                    "critical_threshold": 90.0,
                    "operator": "GREATER_THAN",
                    "created_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = threshold_response

        result = await monitoring_manager.set_metric_threshold(
            metric_name="cpu_usage",
            agent_id="agent-123",
            warning_threshold=80.0,
            critical_threshold=90.0,
        )

        assert result.id == "threshold-123"
        assert result["warning_threshold"] == 80.0
        assert result["critical_threshold"] == 90.0

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_metric_threshold_success(self, monitoring_manager, mock_client):
        """Test successful metric threshold removal."""
        remove_response = {
            "data": {
                "removeMetricThreshold": {
                    "success": True,
                    "message": "Threshold removed successfully",
                }
            }
        }
        mock_client.execute_mutation.return_value = remove_response

        result = await monitoring_manager.remove_metric_threshold("threshold-123")

        assert result is True

        mock_client.execute_mutation.assert_called_once()

    # Test Maintenance Window Operations

    @pytest.mark.asyncio
    async def test_create_maintenance_window_success(self, monitoring_manager, mock_client):
        """Test successful maintenance window creation."""
        maintenance_response = {
            "data": {
                "createMaintenanceWindow": {
                    "id": "maintenance-123",
                    "name": "Server Maintenance",
                    "description": "Scheduled server maintenance",
                    "start_time": "2024-01-20T02:00:00Z",
                    "end_time": "2024-01-20T04:00:00Z",
                    "affected_agents": ["agent-123", "agent-456"],
                    "suppress_alerts": True,
                    "created_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = maintenance_response

        result = await monitoring_manager.create_maintenance_window(
            name="Server Maintenance",
            description="Scheduled server maintenance",
            start_time="2024-01-20T02:00:00Z",
            end_time="2024-01-20T04:00:00Z",
            affected_agents=["agent-123", "agent-456"],
            suppress_alerts=True,
        )

        assert result.id == "maintenance-123"
        assert result["name"] == "Server Maintenance"
        assert result["suppress_alerts"] is True

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_active_maintenance_windows_success(self, monitoring_manager, mock_client):
        """Test successful active maintenance windows retrieval."""
        windows_response = {
            "data": {
                "activeMaintenanceWindows": {
                    "items": [
                        {
                            "id": "maintenance-1",
                            "name": "Network Upgrade",
                            "start_time": "2024-01-15T10:00:00Z",
                            "end_time": "2024-01-15T14:00:00Z",
                            "affected_agents": ["agent-123"],
                        }
                    ],
                    "pagination": {"total": 1},
                }
            }
        }
        mock_client.execute_query.return_value = windows_response

        result = await monitoring_manager.get_active_maintenance_windows()

        assert len(result["items"]) == 1
        assert result["items"][0]["name"] == "Network Upgrade"

        mock_client.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_end_maintenance_window_success(self, monitoring_manager, mock_client):
        """Test successful maintenance window ending."""
        end_response = {
            "data": {
                "endMaintenanceWindow": {
                    "id": "maintenance-123",
                    "status": "ENDED",
                    "ended_at": "2024-01-15T12:00:00Z",
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = end_response

        result = await monitoring_manager.end_maintenance_window("maintenance-123")

        assert result.id == "maintenance-123"
        assert result["status"] == "ENDED"

        mock_client.execute_mutation.assert_called_once()

    # Test Filtering Methods

    @pytest.mark.asyncio
    async def test_list_active_alerts_success(self, monitoring_manager, mock_client):
        """Test listing active alerts."""
        alerts_response = {
            "data": {
                "monitoringAlerts": {
                    "items": [
                        {
                            "id": "alert-1",
                            "severity": "HIGH",
                            "status": "TRIGGERED",
                            "message": "Check failed",
                        },
                        {
                            "id": "alert-2",
                            "severity": "MEDIUM",
                            "status": "ACKNOWLEDGED",
                            "message": "Performance degraded",
                        },
                    ],
                    "pagination": {"total": 2},
                }
            }
        }
        mock_client.execute_query.return_value = alerts_response

        result = await monitoring_manager.list_active_alerts()

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["status_not"] == [AlertStatus.RESOLVED]

    @pytest.mark.asyncio
    async def test_list_checks_by_agent_success(self, monitoring_manager, mock_client):
        """Test listing checks by agent."""
        checks_response = {
            "data": {
                "monitoringChecks": {
                    "items": [
                        {
                            "id": "check-1",
                            "name": "HTTP Check",
                            "check_type": "HTTP",
                            "agent_id": "agent-123",
                            "status": "ENABLED",
                        }
                    ],
                    "pagination": {"total": 1},
                }
            }
        }
        mock_client.execute_query.return_value = checks_response

        result = await monitoring_manager.list_checks_by_agent("agent-123")

        assert len(result["items"]) == 1

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["agent_id"] == "agent-123"

    @pytest.mark.asyncio
    async def test_get_failing_checks_success(self, monitoring_manager, mock_client):
        """Test getting failing checks."""
        checks_response = {
            "data": {
                "monitoringChecks": {
                    "items": [
                        {
                            "id": "check-1",
                            "name": "HTTP Check",
                            "last_status": "FAIL",
                            "failure_count": 3,
                        }
                    ],
                    "pagination": {"total": 1},
                }
            }
        }
        mock_client.execute_query.return_value = checks_response

        result = await monitoring_manager.get_failing_checks()

        assert len(result["items"]) == 1

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert "last_status" in variables["filters"]

    # Test Error Handling

    @pytest.mark.asyncio
    async def test_get_agent_api_error(self, monitoring_manager, mock_client):
        """Test API error handling in get_agent."""
        mock_client.execute_query.side_effect = SuperOpsAPIError("API Error")

        with pytest.raises(SuperOpsAPIError):
            await monitoring_manager.get_agent("agent-123")

    @pytest.mark.asyncio
    async def test_install_agent_validation_error_missing_name(self, monitoring_manager):
        """Test validation error for missing agent name."""
        with pytest.raises(SuperOpsValidationError, match="Name must be a non-empty string"):
            await monitoring_manager.install_agent(hostname="test.com")

    @pytest.mark.asyncio
    async def test_create_check_invalid_interval(self, monitoring_manager):
        """Test check creation with invalid interval."""
        with pytest.raises(SuperOpsValidationError, match="Check interval must be positive"):
            await monitoring_manager.create_check(
                name="Test Check",
                check_type=CheckType.HTTP,
                agent_id="agent-123",
                configuration={},
                check_interval=0,
            )

    @pytest.mark.asyncio
    async def test_silence_alert_invalid_duration(self, monitoring_manager):
        """Test alert silencing with invalid duration."""
        with pytest.raises(SuperOpsValidationError, match="Duration must be positive"):
            await monitoring_manager.silence_alert("alert-123", duration_minutes=0)

    @pytest.mark.asyncio
    async def test_record_metric_value_validation_error(self, monitoring_manager):
        """Test metric value recording with invalid data."""
        with pytest.raises(SuperOpsValidationError, match="Name must be a non-empty string"):
            await monitoring_manager.record_metric_value(
                name="",
                metric_type=MetricType.GAUGE,
                agent_id="agent-123",
                value=50.0,
            )

    @pytest.mark.asyncio
    async def test_set_metric_threshold_invalid_values(self, monitoring_manager):
        """Test metric threshold setting with invalid values."""
        with pytest.raises(
            SuperOpsValidationError,
            match="Critical threshold must be greater than warning threshold",
        ):
            await monitoring_manager.set_metric_threshold(
                metric_name="cpu_usage",
                agent_id="agent-123",
                warning_threshold=90.0,
                critical_threshold=80.0,  # Invalid: critical < warning
            )

    @pytest.mark.asyncio
    async def test_create_maintenance_window_validation_error(self, monitoring_manager):
        """Test maintenance window creation with invalid time range."""
        with pytest.raises(SuperOpsValidationError, match="End time must be after start time"):
            await monitoring_manager.create_maintenance_window(
                name="Invalid Window",
                start_time="2024-01-20T04:00:00Z",
                end_time="2024-01-20T02:00:00Z",  # Invalid: end < start
                affected_agents=["agent-123"],
            )

    # Test Bulk Operations

    @pytest.mark.asyncio
    async def test_bulk_acknowledge_alerts_success(self, monitoring_manager, mock_client):
        """Test successful bulk alert acknowledgment."""
        bulk_response = {
            "data": {
                "bulkAcknowledgeAlerts": {
                    "success": True,
                    "acknowledged_count": 3,
                    "message": "3 alerts acknowledged successfully",
                }
            }
        }
        mock_client.execute_mutation.return_value = bulk_response

        alert_ids = ["alert-1", "alert-2", "alert-3"]
        result = await monitoring_manager.bulk_acknowledge_alerts(alert_ids, "Bulk acknowledgment")

        assert result["success"] is True
        assert result["acknowledged_count"] == 3

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_bulk_enable_checks_success(self, monitoring_manager, mock_client):
        """Test successful bulk check enablement."""
        bulk_response = {
            "data": {
                "bulkUpdateChecks": {
                    "success": True,
                    "updated_count": 2,
                    "message": "2 checks updated successfully",
                }
            }
        }
        mock_client.execute_mutation.return_value = bulk_response

        check_ids = ["check-1", "check-2"]
        result = await monitoring_manager.bulk_enable_checks(check_ids)

        assert result["success"] is True
        assert result["updated_count"] == 2

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_bulk_disable_checks_success(self, monitoring_manager, mock_client):
        """Test successful bulk check disablement."""
        bulk_response = {
            "data": {
                "bulkUpdateChecks": {
                    "success": True,
                    "updated_count": 2,
                    "message": "2 checks updated successfully",
                }
            }
        }
        mock_client.execute_mutation.return_value = bulk_response

        check_ids = ["check-1", "check-2"]
        result = await monitoring_manager.bulk_disable_checks(check_ids)

        assert result["success"] is True
        assert result["updated_count"] == 2

        mock_client.execute_mutation.assert_called_once()
