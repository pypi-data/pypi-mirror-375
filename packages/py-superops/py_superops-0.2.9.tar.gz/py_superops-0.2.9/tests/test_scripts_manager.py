# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Tests for ScriptsManager class."""

from typing import Any, Dict
from unittest.mock import AsyncMock

import pytest

from py_superops.exceptions import SuperOpsAPIError, SuperOpsValidationError
from py_superops.graphql.types import DeploymentStatus, ExecutionStatus, ScriptCategory, ScriptType
from py_superops.managers import ScriptsManager


class TestScriptsManager:
    """Test the ScriptsManager class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock SuperOps client."""
        client = AsyncMock()
        client.execute_query = AsyncMock()
        client.execute_mutation = AsyncMock()
        return client

    @pytest.fixture
    def scripts_manager(self, mock_client):
        """Create a ScriptsManager instance."""
        return ScriptsManager(mock_client)

    @pytest.fixture
    def sample_script_response(self) -> Dict[str, Any]:
        """Sample script response data."""
        return {
            "data": {
                "script": {
                    "id": "script-123",
                    "name": "Test PowerShell Script",
                    "description": "A test PowerShell script for automation",
                    "script_type": "POWERSHELL",
                    "category": "AUTOMATION",
                    "content": "Write-Host 'Hello World'",
                    "version": "1.0.0",
                    "author": "test-user",
                    "organization_id": "org-456",
                    "is_template": False,
                    "is_active": True,
                    "tags": ["automation", "test"],
                    "parameters": [
                        {
                            "name": "message",
                            "type": "string",
                            "required": True,
                            "default_value": "Hello World",
                            "description": "Message to display",
                        }
                    ],
                    "timeout_seconds": 300,
                    "requires_elevation": False,
                    "supported_platforms": ["WINDOWS"],
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }

    @pytest.fixture
    def sample_script_list_response(self) -> Dict[str, Any]:
        """Sample script list response data."""
        return {
            "data": {
                "scripts": {
                    "items": [
                        {
                            "id": "script-1",
                            "name": "PowerShell Script 1",
                            "description": "First PowerShell script",
                            "script_type": "POWERSHELL",
                            "category": "AUTOMATION",
                            "version": "1.0.0",
                            "author": "user-1",
                            "is_template": False,
                            "is_active": True,
                            "tags": ["automation"],
                            "created_at": "2024-01-01T00:00:00Z",
                        },
                        {
                            "id": "script-2",
                            "name": "Bash Script 2",
                            "description": "Second Bash script",
                            "script_type": "BASH",
                            "category": "MONITORING",
                            "version": "1.1.0",
                            "author": "user-2",
                            "is_template": True,
                            "is_active": True,
                            "tags": ["monitoring"],
                            "created_at": "2024-01-02T00:00:00Z",
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

    @pytest.fixture
    def sample_execution_response(self) -> Dict[str, Any]:
        """Sample script execution response data."""
        return {
            "data": {
                "scriptExecution": {
                    "id": "exec-123",
                    "script_id": "script-123",
                    "script_name": "Test PowerShell Script",
                    "status": "COMPLETED",
                    "trigger": "MANUAL",
                    "executor_user_id": "user-456",
                    "target_device_id": "device-789",
                    "target_agent_id": "agent-321",
                    "parameters": {"message": "Hello Test"},
                    "output": "Hello Test",
                    "error_message": None,
                    "exit_code": 0,
                    "started_at": "2024-01-15T10:00:00Z",
                    "completed_at": "2024-01-15T10:01:30Z",
                    "duration_seconds": 90,
                    "created_at": "2024-01-15T10:00:00Z",
                }
            }
        }

    @pytest.fixture
    def sample_library_response(self) -> Dict[str, Any]:
        """Sample script library response data."""
        return {
            "data": {
                "scriptLibrary": {
                    "id": "lib-123",
                    "name": "Automation Scripts",
                    "description": "Collection of automation scripts",
                    "organization_id": "org-456",
                    "is_public": False,
                    "script_count": 5,
                    "tags": ["automation", "collection"],
                    "created_by": "user-456",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }

    @pytest.fixture
    def sample_create_script_data(self) -> Dict[str, Any]:
        """Sample data for creating a script."""
        return {
            "name": "New Test Script",
            "description": "A new script for testing",
            "script_type": ScriptType.POWERSHELL,
            "category": ScriptCategory.AUTOMATION,
            "content": "Write-Host 'Hello New World'",
            "version": "1.0.0",
            "tags": ["new", "testing"],
            "timeout_seconds": 300,
        }

    @pytest.fixture
    def sample_update_script_data(self) -> Dict[str, Any]:
        """Sample data for updating a script."""
        return {
            "name": "Updated Script Name",
            "description": "Updated description",
            "content": "Write-Host 'Updated Hello World'",
            "version": "1.1.0",
            "tags": ["updated", "testing"],
            "timeout_seconds": 600,
        }

    # Test CRUD Operations

    @pytest.mark.asyncio
    async def test_get_script_success(self, scripts_manager, mock_client, sample_script_response):
        """Test successful script retrieval."""
        mock_client.execute_query.return_value = sample_script_response

        result = await scripts_manager.get("script-123")

        assert result is not None
        assert result.id == "script-123"
        assert result.name == "Test PowerShell Script"
        assert result.script_type == ScriptType.POWERSHELL
        assert result.category == ScriptCategory.AUTOMATION

        mock_client.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_script_not_found(self, scripts_manager, mock_client):
        """Test script not found scenario."""
        mock_client.execute_query.return_value = {"data": {"script": None}}

        result = await scripts_manager.get("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_script_invalid_id(self, scripts_manager):
        """Test get with invalid script ID."""
        with pytest.raises(SuperOpsValidationError, match="Invalid resource ID"):
            await scripts_manager.get("")

        with pytest.raises(SuperOpsValidationError, match="Invalid resource ID"):
            await scripts_manager.get(None)

    @pytest.mark.asyncio
    async def test_list_all_scripts_success(
        self, scripts_manager, mock_client, sample_script_list_response
    ):
        """Test successful script listing."""
        mock_client.execute_query.return_value = sample_script_list_response

        result = await scripts_manager.list()

        assert "items" in result
        assert "pagination" in result
        assert len(result["items"]) == 2
        assert result["items"][0].id == "script-1"
        assert result["items"][1].id == "script-2"

        mock_client.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_scripts_with_filters(
        self, scripts_manager, mock_client, sample_script_list_response
    ):
        """Test script listing with filters."""
        mock_client.execute_query.return_value = sample_script_list_response

        filters = {
            "script_type": ScriptType.POWERSHELL,
            "category": ScriptCategory.AUTOMATION,
            "author": "user-1",
            "is_template": False,
        }

        result = await scripts_manager.list(page=2, page_size=25, filters=filters)

        assert len(result["items"]) == 2

        # Verify query parameters were passed correctly
        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["page"] == 2
        assert variables["pageSize"] == 25
        assert variables["filters"]["script_type"] == ScriptType.POWERSHELL
        assert variables["filters"]["category"] == ScriptCategory.AUTOMATION

    @pytest.mark.asyncio
    async def test_create_script_success(
        self, scripts_manager, mock_client, sample_create_script_data
    ):
        """Test successful script creation."""
        created_script = {
            "data": {
                "createScript": {
                    "id": "script-new-123",
                    "name": "New Test Script",
                    "description": "A new script for testing",
                    "script_type": "POWERSHELL",
                    "category": "AUTOMATION",
                    "content": "Write-Host 'Hello New World'",
                    "version": "1.0.0",
                    "author": "current-user",
                    "is_template": False,
                    "is_active": True,
                    "tags": ["new", "testing"],
                    "timeout_seconds": 300,
                    "created_at": "2024-01-01T00:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = created_script

        result = await scripts_manager.create(sample_create_script_data)

        assert result.id == "script-new-123"
        assert result.name == "New Test Script"
        assert result.script_type == ScriptType.POWERSHELL

        mock_client.execute_mutation.assert_called_once()
        call_args = mock_client.execute_mutation.call_args
        assert "createScript" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_create_script_validation_error(self, scripts_manager):
        """Test script creation with invalid data."""
        with pytest.raises(SuperOpsValidationError):
            await scripts_manager.create(name="", content="test")

        with pytest.raises(SuperOpsValidationError):
            await scripts_manager.create(name=None, content="test")

    @pytest.mark.asyncio
    async def test_update_script_success(
        self, scripts_manager, mock_client, sample_update_script_data
    ):
        """Test successful script update."""
        updated_script = {
            "data": {
                "updateScript": {
                    "id": "script-123",
                    "name": "Updated Script Name",
                    "description": "Updated description",
                    "content": "Write-Host 'Updated Hello World'",
                    "version": "1.1.0",
                    "tags": ["updated", "testing"],
                    "timeout_seconds": 600,
                    "updated_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = updated_script

        result = await scripts_manager.update("script-123", **sample_update_script_data)

        assert result.id == "script-123"
        assert result.name == "Updated Script Name"
        assert result.version == "1.1.0"

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_script_success(self, scripts_manager, mock_client):
        """Test successful script deletion."""
        delete_response = {
            "data": {"deleteScript": {"success": True, "message": "Script deleted successfully"}}
        }
        mock_client.execute_mutation.return_value = delete_response

        result = await scripts_manager.delete("script-123")

        assert result is True

        mock_client.execute_mutation.assert_called_once()
        call_args = mock_client.execute_mutation.call_args
        assert call_args[0][1]["id"] == "script-123"

    @pytest.mark.asyncio
    async def test_delete_script_not_found(self, scripts_manager, mock_client):
        """Test deleting non-existent script."""
        delete_response = {
            "data": {"deleteScript": {"success": False, "message": "Script not found"}}
        }
        mock_client.execute_mutation.return_value = delete_response

        result = await scripts_manager.delete("nonexistent")

        assert result is False

    # Test Script Execution

    @pytest.mark.asyncio
    async def test_execute_script_success(
        self, scripts_manager, mock_client, sample_execution_response
    ):
        """Test successful script execution."""
        execution_response = {
            "data": {
                "executeScript": {
                    "id": "exec-123",
                    "script_id": "script-123",
                    "status": "RUNNING",
                    "trigger": "MANUAL",
                    "executor_user_id": "user-456",
                    "target_device_id": "device-789",
                    "parameters": {"message": "Hello Test"},
                    "started_at": "2024-01-15T10:00:00Z",
                    "created_at": "2024-01-15T10:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = execution_response

        result = await scripts_manager.execute_script(
            script_id="script-123",
            target_device_id="device-789",
            parameters={"message": "Hello Test"},
        )

        assert result.id == "exec-123"
        assert result.status == ExecutionStatus.RUNNING
        assert result.parameters == {"message": "Hello Test"}

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_execution_status_success(
        self, scripts_manager, mock_client, sample_execution_response
    ):
        """Test getting execution status."""
        mock_client.execute_query.return_value = sample_execution_response

        result = await scripts_manager.get_execution_status("exec-123")

        assert result.id == "exec-123"
        assert result.status == ExecutionStatus.COMPLETED
        assert result.exit_code == 0

        mock_client.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_execution_success(self, scripts_manager, mock_client):
        """Test successful execution cancellation."""
        cancel_response = {
            "data": {
                "cancelScriptExecution": {
                    "id": "exec-123",
                    "status": "CANCELLED",
                    "cancelled_at": "2024-01-15T10:05:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = cancel_response

        result = await scripts_manager.cancel_execution("exec-123")

        assert result["status"] == "CANCELLED"

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_execution_history_success(self, scripts_manager, mock_client):
        """Test getting execution history."""
        history_response = {
            "data": {
                "scriptExecutions": {
                    "items": [
                        {
                            "id": "exec-1",
                            "script_id": "script-123",
                            "status": "COMPLETED",
                            "started_at": "2024-01-15T10:00:00Z",
                            "completed_at": "2024-01-15T10:01:30Z",
                            "exit_code": 0,
                        },
                        {
                            "id": "exec-2",
                            "script_id": "script-123",
                            "status": "FAILED",
                            "started_at": "2024-01-14T15:30:00Z",
                            "completed_at": "2024-01-14T15:31:00Z",
                            "exit_code": 1,
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
        mock_client.execute_query.return_value = history_response

        result = await scripts_manager.get_execution_history("script-123")

        assert len(result["items"]) == 2
        assert result["items"][0].status == ExecutionStatus.COMPLETED
        assert result["items"][1].status == ExecutionStatus.FAILED

        mock_client.execute_query.assert_called_once()

    # Test Filtering Methods

    @pytest.mark.asyncio
    async def test_get_by_type_success(
        self, scripts_manager, mock_client, sample_script_list_response
    ):
        """Test getting scripts by type."""
        mock_client.execute_query.return_value = sample_script_list_response

        result = await scripts_manager.get_by_type(ScriptType.POWERSHELL)

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["script_type"] == ScriptType.POWERSHELL

    @pytest.mark.asyncio
    async def test_get_by_category_success(
        self, scripts_manager, mock_client, sample_script_list_response
    ):
        """Test getting scripts by category."""
        mock_client.execute_query.return_value = sample_script_list_response

        result = await scripts_manager.get_by_category(ScriptCategory.AUTOMATION)

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["category"] == ScriptCategory.AUTOMATION

    @pytest.mark.asyncio
    async def test_get_by_author_success(
        self, scripts_manager, mock_client, sample_script_list_response
    ):
        """Test getting scripts by author."""
        mock_client.execute_query.return_value = sample_script_list_response

        result = await scripts_manager.get_by_author("user-1")

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["author"] == "user-1"

    @pytest.mark.asyncio
    async def test_get_templates_success(
        self, scripts_manager, mock_client, sample_script_list_response
    ):
        """Test getting script templates."""
        mock_client.execute_query.return_value = sample_script_list_response

        result = await scripts_manager.get_templates()

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["is_template"] is True

    @pytest.mark.asyncio
    async def test_get_by_tags_success(
        self, scripts_manager, mock_client, sample_script_list_response
    ):
        """Test getting scripts by tags."""
        mock_client.execute_query.return_value = sample_script_list_response

        result = await scripts_manager.get_by_tags(["automation", "test"])

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["tags"] == ["automation", "test"]

    # Test Deployment Operations

    @pytest.mark.asyncio
    async def test_create_deployment_success(self, scripts_manager, mock_client):
        """Test successful deployment creation."""
        deployment_response = {
            "data": {
                "createScriptDeployment": {
                    "id": "deploy-123",
                    "script_id": "script-123",
                    "target_type": "DEVICE",
                    "target_ids": ["device-1", "device-2"],
                    "status": "PENDING",
                    "schedule_type": "IMMEDIATE",
                    "parameters": {"param1": "value1"},
                    "created_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = deployment_response

        result = await scripts_manager.create_deployment(
            script_id="script-123",
            target_type="DEVICE",
            target_ids=["device-1", "device-2"],
            parameters={"param1": "value1"},
        )

        assert result.id == "deploy-123"
        assert result.status == DeploymentStatus.PENDING

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_deployments_success(self, scripts_manager, mock_client):
        """Test getting deployments."""
        deployments_response = {
            "data": {
                "scriptDeployments": {
                    "items": [
                        {
                            "id": "deploy-1",
                            "script_id": "script-123",
                            "status": "COMPLETED",
                            "created_at": "2024-01-15T10:00:00Z",
                        },
                        {
                            "id": "deploy-2",
                            "script_id": "script-123",
                            "status": "RUNNING",
                            "created_at": "2024-01-15T11:00:00Z",
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
        mock_client.execute_query.return_value = deployments_response

        result = await scripts_manager.get_deployments("script-123")

        assert len(result["items"]) == 2
        assert result["items"][0].status == DeploymentStatus.COMPLETED

        mock_client.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_deployment_success(self, scripts_manager, mock_client):
        """Test successful deployment update."""
        update_response = {
            "data": {
                "updateScriptDeployment": {
                    "id": "deploy-123",
                    "status": "CANCELLED",
                    "updated_at": "2024-01-15T12:30:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = update_response

        result = await scripts_manager.update_deployment(
            deployment_id="deploy-123", status=DeploymentStatus.INACTIVE
        )

        assert result["status"] == "CANCELLED"

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_deployment_success(self, scripts_manager, mock_client):
        """Test successful deployment deletion."""
        delete_response = {
            "data": {"deleteScriptDeployment": {"success": True, "message": "Deployment deleted"}}
        }
        mock_client.execute_mutation.return_value = delete_response

        result = await scripts_manager.delete_deployment("deploy-123")

        assert result is True

        mock_client.execute_mutation.assert_called_once()

    # Test Library Operations

    @pytest.mark.asyncio
    async def test_create_library_success(
        self, scripts_manager, mock_client, sample_library_response
    ):
        """Test successful library creation."""
        create_response = {
            "data": {
                "createScriptLibrary": {
                    "id": "lib-new-123",
                    "name": "New Library",
                    "description": "A new script library",
                    "organization_id": "org-456",
                    "is_public": False,
                    "script_count": 0,
                    "tags": ["new"],
                    "created_by": "user-456",
                    "created_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = create_response

        result = await scripts_manager.create_library(
            name="New Library",
            description="A new script library",
            is_public=False,
            tags=["new"],
        )

        assert result.id == "lib-new-123"
        assert result.name == "New Library"

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_libraries_success(self, scripts_manager, mock_client):
        """Test getting libraries."""
        libraries_response = {
            "data": {
                "scriptLibraries": {
                    "items": [
                        {
                            "id": "lib-1",
                            "name": "Library 1",
                            "description": "First library",
                            "script_count": 5,
                            "is_public": True,
                        },
                        {
                            "id": "lib-2",
                            "name": "Library 2",
                            "description": "Second library",
                            "script_count": 3,
                            "is_public": False,
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
        mock_client.execute_query.return_value = libraries_response

        result = await scripts_manager.get_libraries()

        assert len(result["items"]) == 2
        assert result["items"][0].script_count == 5

        mock_client.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_library_scripts_success(
        self, scripts_manager, mock_client, sample_script_list_response
    ):
        """Test getting scripts in a library."""
        mock_client.execute_query.return_value = sample_script_list_response

        result = await scripts_manager.get_library_scripts("lib-123")

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["library_id"] == "lib-123"

    # Test Bulk Operations

    @pytest.mark.asyncio
    async def test_bulk_execute_success(self, scripts_manager, mock_client):
        """Test successful bulk execution."""
        bulk_response = {
            "data": {
                "bulkExecuteScripts": {
                    "success": True,
                    "execution_count": 3,
                    "executions": [
                        {"id": "exec-1", "script_id": "script-1", "status": "RUNNING"},
                        {"id": "exec-2", "script_id": "script-2", "status": "RUNNING"},
                        {"id": "exec-3", "script_id": "script-3", "status": "RUNNING"},
                    ],
                }
            }
        }
        mock_client.execute_mutation.return_value = bulk_response

        script_ids = ["script-1", "script-2", "script-3"]
        target_device_ids = ["device-1", "device-2"]

        result = await scripts_manager.bulk_execute(script_ids, target_device_ids)

        assert result["success"] is True
        assert result["execution_count"] == 3
        assert len(result["executions"]) == 3

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_bulk_update_status_success(self, scripts_manager, mock_client):
        """Test successful bulk status update."""
        bulk_response = {
            "data": {
                "bulkUpdateScripts": {
                    "success": True,
                    "updated_count": 2,
                    "message": "2 scripts updated successfully",
                }
            }
        }
        mock_client.execute_mutation.return_value = bulk_response

        script_ids = ["script-1", "script-2"]

        result = await scripts_manager.bulk_update_status(script_ids, is_active=False)

        assert result["success"] is True
        assert result["updated_count"] == 2

        mock_client.execute_mutation.assert_called_once()

    # Test Statistics

    @pytest.mark.asyncio
    async def test_get_execution_statistics_success(self, scripts_manager, mock_client):
        """Test getting execution statistics."""
        stats_response = {
            "data": {
                "scriptExecutionStatistics": {
                    "total_executions": 150,
                    "executions_by_status": {
                        "COMPLETED": 120,
                        "FAILED": 20,
                        "RUNNING": 5,
                        "CANCELLED": 5,
                    },
                    "executions_by_script_type": {
                        "POWERSHELL": 80,
                        "BASH": 50,
                        "PYTHON": 20,
                    },
                    "average_execution_time": 45.5,
                    "success_rate": 80.0,
                }
            }
        }
        mock_client.execute_query.return_value = stats_response

        result = await scripts_manager.get_execution_statistics()

        assert result["total_executions"] == 150
        assert result["executions_by_status"]["COMPLETED"] == 120
        assert result["success_rate"] == 80.0

        mock_client.execute_query.assert_called_once()

    # Test Error Handling

    @pytest.mark.asyncio
    async def test_get_script_api_error(self, scripts_manager, mock_client):
        """Test API error handling in get_script."""
        mock_client.execute_query.side_effect = SuperOpsAPIError("API Error", 500)

        with pytest.raises(SuperOpsAPIError):
            await scripts_manager.get("script-123")

    @pytest.mark.asyncio
    async def test_create_script_validation_error_empty_data(self, scripts_manager):
        """Test validation error for empty script data."""
        with pytest.raises(SuperOpsValidationError):
            await scripts_manager.create()

    @pytest.mark.asyncio
    async def test_execute_script_invalid_id(self, scripts_manager):
        """Test execute script with invalid ID."""
        with pytest.raises(SuperOpsValidationError, match="Script ID cannot be empty"):
            await scripts_manager.execute_script("", target_device_id="device-123")

    @pytest.mark.asyncio
    async def test_execute_script_invalid_target(self, scripts_manager):
        """Test execute script without target."""
        with pytest.raises(SuperOpsValidationError, match="Target device ID or agent ID required"):
            await scripts_manager.execute_script("script-123")

    @pytest.mark.asyncio
    async def test_create_deployment_validation_error(self, scripts_manager):
        """Test deployment creation with invalid data."""
        with pytest.raises(SuperOpsValidationError, match="Script ID cannot be empty"):
            await scripts_manager.create_deployment(
                "", target_type="DEVICE", target_ids=["device-1"]
            )

        with pytest.raises(SuperOpsValidationError, match="Target IDs cannot be empty"):
            await scripts_manager.create_deployment(
                "script-123", target_type="DEVICE", target_ids=[]
            )

    @pytest.mark.asyncio
    async def test_bulk_execute_validation_error(self, scripts_manager):
        """Test bulk execute with invalid data."""
        with pytest.raises(SuperOpsValidationError, match="Script IDs cannot be empty"):
            await scripts_manager.bulk_execute([], ["device-1"])

        with pytest.raises(SuperOpsValidationError, match="Target device IDs cannot be empty"):
            await scripts_manager.bulk_execute(["script-1"], [])

    # Test Search and Advanced Operations

    @pytest.mark.asyncio
    async def test_search_scripts_success(
        self, scripts_manager, mock_client, sample_script_list_response
    ):
        """Test successful script search."""
        mock_client.execute_query.return_value = sample_script_list_response

        result = await scripts_manager.search_scripts("automation")

        assert len(result["items"]) == 2

        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["query"] == "automation"

    @pytest.mark.asyncio
    async def test_get_script_versions_success(self, scripts_manager, mock_client):
        """Test getting script versions."""
        versions_response = {
            "data": {
                "scriptVersions": [
                    {
                        "version": "1.0.0",
                        "created_at": "2024-01-01T00:00:00Z",
                        "is_current": False,
                    },
                    {
                        "version": "1.1.0",
                        "created_at": "2024-01-15T00:00:00Z",
                        "is_current": True,
                    },
                ]
            }
        }
        mock_client.execute_query.return_value = versions_response

        result = await scripts_manager.get_script_versions("script-123")

        assert len(result) == 2
        assert result[1]["is_current"] is True

        mock_client.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_clone_script_success(self, scripts_manager, mock_client):
        """Test successful script cloning."""
        clone_response = {
            "data": {
                "cloneScript": {
                    "id": "script-cloned-123",
                    "name": "Cloned Script",
                    "description": "Cloned from original script",
                    "script_type": "POWERSHELL",
                    "version": "1.0.0",
                    "is_active": True,
                    "created_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = clone_response

        result = await scripts_manager.clone_script(
            script_id="script-123", new_name="Cloned Script"
        )

        assert result.id == "script-cloned-123"
        assert result.name == "Cloned Script"

        mock_client.execute_mutation.assert_called_once()

    @pytest.mark.asyncio
    async def test_schedule_script_success(self, scripts_manager, mock_client):
        """Test successful script scheduling."""
        schedule_response = {
            "data": {
                "scheduleScript": {
                    "id": "schedule-123",
                    "script_id": "script-123",
                    "schedule_expression": "0 0 * * *",
                    "is_active": True,
                    "next_run": "2024-01-16T00:00:00Z",
                    "created_at": "2024-01-15T12:00:00Z",
                }
            }
        }
        mock_client.execute_mutation.return_value = schedule_response

        result = await scripts_manager.schedule_script(
            script_id="script-123",
            cron_expression="0 0 * * *",
            target_device_ids=["device-1"],
        )

        assert result.id == "schedule-123"
        assert result.is_active is True

        mock_client.execute_mutation.assert_called_once()
