# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Test fixtures and configuration for py-superops tests."""

from datetime import datetime, timezone
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from py_superops import AuthHandler, SuperOpsClient, SuperOpsConfig
from py_superops.graphql.types import (
    AssetStatus,
    ClientStatus,
    TaskPriority,
    TaskRecurrenceType,
    TaskStatus,
    TicketPriority,
    TicketStatus,
    TimeEntryStatus,
    TimeEntryType,
    TimerState,
)

# Test configuration fixtures


@pytest.fixture
def test_config() -> SuperOpsConfig:
    """Create a test configuration."""
    return SuperOpsConfig(
        api_key="test-api-key-12345678901234567890",
        base_url="https://api.superops.com/v1",
        timeout=30.0,
        max_retries=3,
    )


@pytest.fixture
def eu_config() -> SuperOpsConfig:
    """Create a test EU configuration."""
    return SuperOpsConfig(
        api_key="test-api-key-12345678901234567890",
        base_url="https://eu.superops.com/v1",
        timeout=30.0,
        max_retries=3,
    )


@pytest.fixture
def auth_handler(test_config: SuperOpsConfig) -> AuthHandler:
    """Create test auth handler."""
    return AuthHandler(test_config)


@pytest.fixture
def mock_http_client() -> AsyncMock:
    """Create a mock HTTP client."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


@pytest.fixture
def client(test_config: SuperOpsConfig, mock_http_client: AsyncMock) -> SuperOpsClient:
    """Create a test client with mocked HTTP client."""
    return SuperOpsClient(test_config, http_client=mock_http_client)


@pytest.fixture
async def client_context(test_config: SuperOpsConfig) -> SuperOpsClient:
    """Create a client for use in async context manager tests."""
    async with SuperOpsClient(test_config) as client:
        yield client


# Mock response fixtures


@pytest.fixture
def mock_success_response() -> Dict[str, Any]:
    """Create a successful GraphQL response."""
    return {
        "data": {
            "client": {
                "id": "client-123",
                "name": "Test Client",
                "email": "test@example.com",
                "status": "ACTIVE",
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "updatedAt": datetime.now(timezone.utc).isoformat(),
            }
        }
    }


@pytest.fixture
def mock_list_response() -> Dict[str, Any]:
    """Create a successful list response."""
    return {
        "data": {
            "clients": {
                "items": [
                    {
                        "id": "client-1",
                        "name": "Client One",
                        "email": "one@example.com",
                        "status": "ACTIVE",
                        "createdAt": datetime.now(timezone.utc).isoformat(),
                        "updatedAt": datetime.now(timezone.utc).isoformat(),
                    },
                    {
                        "id": "client-2",
                        "name": "Client Two",
                        "email": "two@example.com",
                        "status": "INACTIVE",
                        "createdAt": datetime.now(timezone.utc).isoformat(),
                        "updatedAt": datetime.now(timezone.utc).isoformat(),
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
def mock_error_response() -> Dict[str, Any]:
    """Create a GraphQL error response."""
    return {
        "errors": [{"message": "Resource not found", "extensions": {"code": "RESOURCE_NOT_FOUND"}}]
    }


@pytest.fixture
def mock_authentication_error() -> Dict[str, Any]:
    """Create an authentication error response."""
    return {
        "errors": [{"message": "Authentication failed", "extensions": {"code": "UNAUTHENTICATED"}}]
    }


@pytest.fixture
def mock_validation_error() -> Dict[str, Any]:
    """Create a validation error response."""
    return {
        "errors": [
            {
                "message": "Validation failed",
                "extensions": {
                    "code": "VALIDATION_ERROR",
                    "field": "email",
                    "details": "Invalid email format",
                },
            }
        ]
    }


# Test data fixtures


@pytest.fixture
def sample_client_data() -> Dict[str, Any]:
    """Sample client data for testing."""
    return {
        "name": "Sample Client Corp",
        "email": "contact@sampleclient.com",
        "phone": "+1-555-123-4567",
        "address": "123 Business St",
        "city": "Business City",
        "state": "CA",
        "country": "US",
        "website": "https://www.sampleclient.com",
        "status": ClientStatus.ACTIVE,
        "notes": "Sample client for testing purposes",
    }


@pytest.fixture
def sample_ticket_data() -> Dict[str, Any]:
    """Sample ticket data for testing."""
    return {
        "client_id": "client-123",
        "title": "Sample Ticket",
        "description": "This is a sample ticket for testing",
        "priority": TicketPriority.NORMAL,
        "status": TicketStatus.OPEN,
        "assigned_to": "user-456",
        "category": "General Support",
        "tags": ["test", "sample"],
    }


@pytest.fixture
def sample_asset_data() -> Dict[str, Any]:
    """Sample asset data for testing."""
    return {
        "client_id": "client-123",
        "name": "Sample Server",
        "asset_type": "Server",
        "model": "Dell PowerEdge R730",
        "serial_number": "ABC123XYZ789",
        "status": AssetStatus.ACTIVE,
        "location": "Data Center Rack A1",
        "purchase_date": "2023-01-15",
        "warranty_expiry": "2026-01-15",
        "specifications": {
            "cpu": "Intel Xeon E5-2680 v4",
            "ram": "64GB DDR4",
            "storage": "2TB SSD",
        },
    }


@pytest.fixture
def sample_contact_data() -> Dict[str, Any]:
    """Sample contact data for testing."""
    return {
        "client_id": "client-123",
        "name": "John Doe",
        "email": "john.doe@sampleclient.com",
        "phone": "+1-555-987-6543",
        "role": "IT Manager",
        "is_primary": True,
        "notes": "Primary technical contact",
    }


@pytest.fixture
def sample_site_data() -> Dict[str, Any]:
    """Sample site data for testing."""
    return {
        "client_id": "client-123",
        "name": "Headquarters",
        "address": "456 Corporate Blvd",
        "city": "Corporate City",
        "state": "NY",
        "country": "US",
        "phone": "+1-555-111-2222",
        "is_primary": True,
        "notes": "Main office location",
    }


@pytest.fixture
def sample_kb_collection_data() -> Dict[str, Any]:
    """Sample knowledge base collection data for testing."""
    return {
        "name": "Troubleshooting Guide",
        "description": "Common troubleshooting procedures",
        "is_public": True,
        "category": "Support",
        "tags": ["troubleshooting", "support", "guide"],
    }


@pytest.fixture
def sample_kb_article_data() -> Dict[str, Any]:
    """Sample knowledge base article data for testing."""
    return {
        "collection_id": "collection-123",
        "title": "How to Reset Password",
        "content": "Step-by-step guide to reset your password...",
        "summary": "Password reset instructions",
        "is_published": True,
        "tags": ["password", "reset", "authentication"],
        "author": "support@company.com",
    }


@pytest.fixture
def sample_task_data() -> Dict[str, Any]:
    """Sample task data for testing."""
    return {
        "title": "Sample Task",
        "description": "This is a sample task for testing",
        "project_id": "project-123",
        "assigned_to": "user-456",
        "priority": TaskPriority.NORMAL,
        "status": TaskStatus.NEW,
        "due_date": "2024-12-31",
        "estimated_hours": 8.0,
        "tags": ["test", "sample"],
        "custom_fields": {"environment": "development"},
        "is_billable": True,
    }


@pytest.fixture
def sample_task_template_data() -> Dict[str, Any]:
    """Sample task template data for testing."""
    return {
        "name": "Bug Fix Template",
        "description": "Standard template for bug fix tasks",
        "task_defaults": {
            "priority": TaskPriority.HIGH,
            "estimated_hours": 4.0,
            "tags": ["bug", "fix"],
            "is_billable": True,
        },
        "is_active": True,
    }


@pytest.fixture
def sample_recurring_task_data() -> Dict[str, Any]:
    """Sample recurring task data for testing."""
    return {
        "title": "Weekly Status Report",
        "description": "Generate and send weekly status report",
        "priority": TaskPriority.NORMAL,
        "recurrence_type": TaskRecurrenceType.WEEKLY,
        "recurrence_interval": 1,
        "start_date": "2024-01-01",
        "estimated_hours": 2.0,
        "assigned_to": "user-456",
        "tags": ["reporting", "weekly"],
    }


# HTTP mock helpers


@pytest.fixture
def mock_httpx_response():
    """Create a factory for mock httpx responses."""

    def _create_response(
        status_code: int = 200,
        json_data: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
        text: str = None,
    ) -> httpx.Response:
        """Create a mock httpx Response."""
        response = MagicMock(spec=httpx.Response)
        response.status_code = status_code
        response.headers = headers or {"content-type": "application/json"}

        if json_data is not None:
            response.json.return_value = json_data
            response.text = str(json_data)
        elif text is not None:
            response.text = text
            response.json.side_effect = ValueError("No JSON object could be decoded")
        else:
            response.json.return_value = {}
            response.text = "{}"

        response.raise_for_status.return_value = None
        if status_code >= 400:
            response.raise_for_status.side_effect = httpx.HTTPStatusError(
                f"HTTP {status_code}", request=MagicMock(), response=response
            )

        return response

    return _create_response


# Error simulation fixtures


@pytest.fixture
def network_error():
    """Create a network error for testing."""
    return httpx.NetworkError("Connection failed")


@pytest.fixture
def timeout_error():
    """Create a timeout error for testing."""
    return httpx.TimeoutException("Request timed out")


@pytest.fixture
def rate_limit_response(mock_httpx_response):
    """Create a rate limit error response."""
    return mock_httpx_response(
        status_code=429,
        headers={
            "retry-after": "60",
            "x-ratelimit-limit": "1000",
            "x-ratelimit-remaining": "0",
            "x-ratelimit-reset": str(int(datetime.now().timestamp()) + 3600),
        },
        json_data={
            "errors": [{"message": "Rate limit exceeded", "extensions": {"code": "RATE_LIMITED"}}]
        },
    )


# Test utilities


@pytest.fixture
def assert_valid_graphql_query():
    """Fixture providing GraphQL query validation."""

    def _validate(query: str) -> bool:
        """Basic GraphQL query validation."""
        # Check basic structure
        if not query.strip():
            return False

        # Check for required GraphQL keywords
        has_operation = any(
            keyword in query.lower() for keyword in ["query", "mutation", "subscription"]
        )

        # Check balanced braces
        open_braces = query.count("{")
        close_braces = query.count("}")

        return has_operation and open_braces == close_braces

    return _validate


@pytest.fixture
def assert_valid_variables():
    """Fixture providing GraphQL variables validation."""

    def _validate(variables: Dict[str, Any]) -> bool:
        """Basic GraphQL variables validation."""
        if not isinstance(variables, dict):
            return False

        # Check for common required fields in different operations
        return True  # Basic validation - could be enhanced

    return _validate


# Integration test helpers


@pytest.fixture
def mock_successful_request(mock_http_client, mock_httpx_response, mock_success_response):
    """Configure mock HTTP client for successful requests."""
    response = mock_httpx_response(200, mock_success_response)
    mock_http_client.post.return_value = response
    return mock_http_client


@pytest.fixture
def mock_failed_request(mock_http_client, mock_httpx_response, mock_error_response):
    """Configure mock HTTP client for failed requests."""
    response = mock_httpx_response(400, mock_error_response)
    mock_http_client.post.return_value = response
    return mock_http_client


# Performance testing helpers


@pytest.fixture
def performance_timer():
    """Simple performance timing context manager."""
    import time

    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def __enter__(self):
            self.start_time = time.time()
            return self

        def __exit__(self, *args):
            self.end_time = time.time()

        @property
        def elapsed(self) -> float:
            if self.end_time and self.start_time:
                return self.end_time - self.start_time
            return 0.0

    return Timer
