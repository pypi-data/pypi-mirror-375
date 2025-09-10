# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

# # Copyright (c) 2025 Aaron Sachs
# # Licensed under the MIT License.
# # See LICENSE file in the project root for full license information.

"""Tests for the WebhooksManager class."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock
from typing import Any, Dict, List

import pytest

from py_superops.exceptions import SuperOpsValidationError, SuperOpsAPIError
from py_superops.graphql.types import (
    Webhook,
    WebhookEvent,
    WebhookStatus,
    WebhookDelivery,
    WebhookDeliveryStatus,
    WebhookEventRecord,
    WebhookFilter,
    WebhookDeliveryFilter,
    WebhookInput,
    WebhookTestInput,
)
from py_superops.managers.webhooks import WebhooksManager


class TestWebhooksManager:
    """Test cases for WebhooksManager."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock SuperOps client."""
        client = Mock()
        client.execute_query = AsyncMock()
        client.execute_mutation = AsyncMock()
        return client

    @pytest.fixture
    def webhooks_manager(self, mock_client):
        """Create a WebhooksManager instance with mocked client."""
        return WebhooksManager(mock_client)

    @pytest.fixture
    def sample_webhook_data(self):
        """Sample webhook data for tests."""
        return {
            "id": "webhook_123",
            "name": "Test Webhook",
            "url": "https://example.com/webhook",
            "events": ["TICKET_CREATED", "TICKET_UPDATED", "CLIENT_CREATED"],
            "status": "ACTIVE",
            "is_active": True,
            "secret": "webhook_secret_key",
            "description": "Test webhook for integration testing",
            "headers": {
                "Authorization": "Bearer token123",
                "X-Custom-Header": "CustomValue"
            },
            "timeout_seconds": 30,
            "retry_count": 3,
            "tags": ["integration", "test"],
            "custom_fields": {"environment": "test"},
            "last_triggered": "2024-01-15T10:30:00Z",
            "delivery_count": 25,
            "failure_count": 2,
            "created_at": "2024-01-01T09:00:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
        }

    @pytest.fixture
    def sample_webhook_delivery_data(self):
        """Sample webhook delivery data for tests."""
        return {
            "id": "delivery_456",
            "webhook_id": "webhook_123",
            "event_type": "TICKET_CREATED",
            "status": "DELIVERED",
            "status_code": 200,
            "response_body": "OK",
            "request_payload": {
                "event": "ticket.created",
                "data": {"ticketId": "ticket_789", "title": "Test Ticket"}
            },
            "attempts": 1,
            "last_attempt_at": "2024-01-15T10:30:00Z",
            "next_retry_at": None,
            "error": None,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
        }

    @pytest.fixture
    def sample_webhook_event_record_data(self):
        """Sample webhook event record data for tests."""
        return {
            "id": "event_789",
            "webhook_id": "webhook_123",
            "event_type": "TICKET_CREATED",
            "resource_id": "ticket_101",
            "resource_type": "Ticket",
            "payload": {
                "id": "ticket_101",
                "title": "New Support Ticket",
                "status": "OPEN",
                "priority": "MEDIUM"
            },
            "processed_at": "2024-01-15T10:30:00Z",
            "delivery_id": "delivery_456",
            "created_at": "2024-01-15T10:29:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
        }

    @pytest.fixture
    def sample_webhook_input(self):
        """Sample webhook input data for tests."""
        return WebhookInput(
            name="New Webhook",
            url="https://api.example.com/webhooks",
            events=[WebhookEvent.TICKET_CREATED, WebhookEvent.CLIENT_UPDATED],
            secret="new_webhook_secret",
            description="New integration webhook",
            headers={"Content-Type": "application/json"},
            timeout_seconds=45,
            retry_count=5,
            tags=["production", "crm"]
        )

    # Test basic CRUD operations

    async def test_get_by_name_success(
        self, webhooks_manager, mock_client, sample_webhook_data
    ):
        """Test successful webhook retrieval by name."""
        # Mock the search response
        mock_client.execute_query.return_value = {
            "data": {
                "searchWebhooks": {
                    "items": [sample_webhook_data],
                    "pagination": {
                        "page": 1,
                        "pageSize": 1,
                        "total": 1,
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                    },
                }
            }
        }

        result = await webhooks_manager.get_by_name("Test Webhook")

        assert result is not None
        assert result.name == "Test Webhook"
        assert result.url == "https://example.com/webhook"
        assert WebhookEvent.TICKET_CREATED in result.events
        mock_client.execute_query.assert_called_once()

    async def test_get_by_name_not_found(self, webhooks_manager, mock_client):
        """Test webhook not found by name."""
        # Mock empty search response
        mock_client.execute_query.return_value = {
            "data": {
                "searchWebhooks": {
                    "items": [],
                    "pagination": {
                        "page": 1,
                        "pageSize": 1,
                        "total": 0,
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                    },
                }
            }
        }

        result = await webhooks_manager.get_by_name("Nonexistent Webhook")

        assert result is None
        mock_client.execute_query.assert_called_once()

    async def test_get_by_name_invalid_input(self, webhooks_manager):
        """Test webhook retrieval with invalid name."""
        with pytest.raises(
            SuperOpsValidationError, match="Webhook name must be a non-empty string"
        ):
            await webhooks_manager.get_by_name("")

        with pytest.raises(
            SuperOpsValidationError, match="Webhook name must be a non-empty string"
        ):
            await webhooks_manager.get_by_name(None)

    async def test_get_by_url_success(
        self, webhooks_manager, mock_client, sample_webhook_data
    ):
        """Test successful webhook retrieval by URL."""
        mock_client.execute_query.return_value = {
            "data": {
                "searchWebhooks": {
                    "items": [sample_webhook_data],
                    "pagination": {
                        "page": 1,
                        "pageSize": 1,
                        "total": 1,
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                    },
                }
            }
        }

        result = await webhooks_manager.get_by_url("https://example.com/webhook")

        assert result is not None
        assert result.url == "https://example.com/webhook"
        assert result.name == "Test Webhook"
        mock_client.execute_query.assert_called_once()

    async def test_get_by_url_invalid_input(self, webhooks_manager):
        """Test webhook retrieval with invalid URL."""
        with pytest.raises(
            SuperOpsValidationError, match="Webhook URL must be a non-empty string"
        ):
            await webhooks_manager.get_by_url("")

        with pytest.raises(
            SuperOpsValidationError, match="Webhook URL must be a non-empty string"
        ):
            await webhooks_manager.get_by_url(None)

    async def test_get_active_webhooks(self, webhooks_manager, mock_client, sample_webhook_data):
        """Test retrieving active webhooks."""
        mock_client.execute_query.return_value = {
            "data": {
                "webhooks": {
                    "items": [sample_webhook_data],
                    "pagination": {
                        "page": 1,
                        "pageSize": 50,
                        "total": 1,
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                    },
                }
            }
        }

        result = await webhooks_manager.get_active_webhooks()

        assert len(result["items"]) == 1
        assert result["items"][0].status == WebhookStatus.ACTIVE
        mock_client.execute_query.assert_called_once()

        # Check that the filter was applied correctly
        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["status"] == "ACTIVE"

    async def test_get_webhooks_by_event(
        self, webhooks_manager, mock_client, sample_webhook_data
    ):
        """Test retrieving webhooks by event type."""
        mock_client.execute_query.return_value = {
            "data": {
                "webhooks": {
                    "items": [sample_webhook_data],
                    "pagination": {
                        "page": 1,
                        "pageSize": 50,
                        "total": 1,
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                    },
                }
            }
        }

        result = await webhooks_manager.get_webhooks_by_event(WebhookEvent.TICKET_CREATED)

        assert len(result["items"]) == 1
        assert WebhookEvent.TICKET_CREATED in result["items"][0].events
        mock_client.execute_query.assert_called_once()

        # Check that the filter was applied correctly
        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert WebhookEvent.TICKET_CREATED.value in variables["filters"]["events"]

    # Test webhook testing functionality

    async def test_test_webhook_success(self, webhooks_manager, mock_client):
        """Test successful webhook testing."""
        mock_client.execute_mutation.return_value = {
            "data": {
                "testWebhook": {
                    "success": True,
                    "statusCode": 200,
                    "responseBody": "OK",
                    "responseTime": 250,
                    "error": None
                }
            }
        }

        result = await webhooks_manager.test_webhook(
            "webhook_123",
            WebhookEvent.TICKET_CREATED,
            {"test": "payload"}
        )

        assert result["success"] is True
        assert result["statusCode"] == 200
        assert result["responseBody"] == "OK"
        assert result["responseTime"] == 250
        mock_client.execute_mutation.assert_called_once()

    async def test_test_webhook_failure(self, webhooks_manager, mock_client):
        """Test webhook testing with failure response."""
        mock_client.execute_mutation.return_value = {
            "data": {
                "testWebhook": {
                    "success": False,
                    "statusCode": 500,
                    "responseBody": "Internal Server Error",
                    "responseTime": 5000,
                    "error": "Connection timeout"
                }
            }
        }

        result = await webhooks_manager.test_webhook(
            "webhook_123",
            WebhookEvent.TICKET_CREATED
        )

        assert result["success"] is False
        assert result["statusCode"] == 500
        assert result["error"] == "Connection timeout"
        mock_client.execute_mutation.assert_called_once()

    async def test_test_webhook_invalid_input(self, webhooks_manager):
        """Test webhook testing with invalid input."""
        with pytest.raises(
            SuperOpsValidationError, match="Webhook ID must be a non-empty string"
        ):
            await webhooks_manager.test_webhook("", WebhookEvent.TICKET_CREATED)

        with pytest.raises(
            SuperOpsValidationError, match="Event type must be provided"
        ):
            await webhooks_manager.test_webhook("webhook_123", None)

    # Test enable/disable functionality

    async def test_enable_webhook_success(self, webhooks_manager, mock_client, sample_webhook_data):
        """Test successfully enabling a webhook."""
        updated_data = sample_webhook_data.copy()
        updated_data["status"] = "ACTIVE"
        updated_data["isActive"] = True

        mock_client.execute_mutation.return_value = {
            "data": {
                "updateWebhook": updated_data
            }
        }

        result = await webhooks_manager.enable_webhook("webhook_123")

        assert result.status == WebhookStatus.ACTIVE
        assert result.is_active is True
        mock_client.execute_mutation.assert_called_once()

    async def test_disable_webhook_success(self, webhooks_manager, mock_client, sample_webhook_data):
        """Test successfully disabling a webhook."""
        updated_data = sample_webhook_data.copy()
        updated_data["status"] = "INACTIVE"
        updated_data["isActive"] = False

        mock_client.execute_mutation.return_value = {
            "data": {
                "updateWebhook": updated_data
            }
        }

        result = await webhooks_manager.disable_webhook("webhook_123")

        assert result.status == WebhookStatus.INACTIVE
        assert result.is_active is False
        mock_client.execute_mutation.assert_called_once()

    async def test_enable_webhook_invalid_input(self, webhooks_manager):
        """Test enabling webhook with invalid input."""
        with pytest.raises(
            SuperOpsValidationError, match="Webhook ID must be a non-empty string"
        ):
            await webhooks_manager.enable_webhook("")

    async def test_disable_webhook_invalid_input(self, webhooks_manager):
        """Test disabling webhook with invalid input."""
        with pytest.raises(
            SuperOpsValidationError, match="Webhook ID must be a non-empty string"
        ):
            await webhooks_manager.disable_webhook(None)

    # Test webhook delivery functionality

    async def test_get_webhook_deliveries_success(
        self, webhooks_manager, mock_client, sample_webhook_delivery_data
    ):
        """Test retrieving webhook deliveries."""
        mock_client.execute_query.return_value = {
            "data": {
                "webhookDeliveries": {
                    "items": [sample_webhook_delivery_data],
                    "pagination": {
                        "page": 1,
                        "pageSize": 50,
                        "total": 1,
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                    },
                }
            }
        }

        result = await webhooks_manager.get_webhook_deliveries("webhook_123")

        assert len(result["items"]) == 1
        assert result["items"][0].webhook_id == "webhook_123"
        assert result["items"][0].event_type == WebhookEvent.TICKET_CREATED
        assert result["items"][0].status == WebhookDeliveryStatus.DELIVERED
        mock_client.execute_query.assert_called_once()

    async def test_get_webhook_deliveries_with_filters(
        self, webhooks_manager, mock_client, sample_webhook_delivery_data
    ):
        """Test retrieving webhook deliveries with filters."""
        mock_client.execute_query.return_value = {
            "data": {
                "webhookDeliveries": {
                    "items": [sample_webhook_delivery_data],
                    "pagination": {
                        "page": 1,
                        "pageSize": 20,
                        "total": 1,
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                    },
                }
            }
        }

        delivery_filter = WebhookDeliveryFilter(
            status=WebhookDeliveryStatus.DELIVERED,
            event_type=WebhookEvent.TICKET_CREATED
        )

        result = await webhooks_manager.get_webhook_deliveries(
            "webhook_123",
            page=1,
            page_size=20,
            delivery_filter=delivery_filter
        )

        assert len(result["items"]) == 1
        mock_client.execute_query.assert_called_once()

        # Check that filters were applied
        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["status"] == "DELIVERED"
        assert variables["filters"]["eventType"] == "TICKET_CREATED"

    async def test_get_webhook_deliveries_invalid_input(self, webhooks_manager):
        """Test retrieving webhook deliveries with invalid input."""
        with pytest.raises(
            SuperOpsValidationError, match="Webhook ID must be a non-empty string"
        ):
            await webhooks_manager.get_webhook_deliveries("")

    async def test_retry_failed_delivery_success(self, webhooks_manager, mock_client):
        """Test successfully retrying a failed delivery."""
        mock_client.execute_mutation.return_value = {
            "data": {
                "retryWebhookDelivery": {
                    "success": True,
                    "deliveryId": "delivery_456",
                    "newAttemptId": "attempt_789"
                }
            }
        }

        result = await webhooks_manager.retry_failed_delivery("delivery_456")

        assert result["success"] is True
        assert result["deliveryId"] == "delivery_456"
        assert result["newAttemptId"] == "attempt_789"
        mock_client.execute_mutation.assert_called_once()

    async def test_retry_failed_delivery_invalid_input(self, webhooks_manager):
        """Test retrying failed delivery with invalid input."""
        with pytest.raises(
            SuperOpsValidationError, match="Delivery ID must be a non-empty string"
        ):
            await webhooks_manager.retry_failed_delivery("")

        with pytest.raises(
            SuperOpsValidationError, match="Delivery ID must be a non-empty string"
        ):
            await webhooks_manager.retry_failed_delivery(None)

    # Test webhook event records

    async def test_get_webhook_events_success(
        self, webhooks_manager, mock_client, sample_webhook_event_record_data
    ):
        """Test retrieving webhook event records."""
        mock_client.execute_query.return_value = {
            "data": {
                "webhookEventRecords": {
                    "items": [sample_webhook_event_record_data],
                    "pagination": {
                        "page": 1,
                        "pageSize": 50,
                        "total": 1,
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                    },
                }
            }
        }

        result = await webhooks_manager.get_webhook_events("webhook_123")

        assert len(result["items"]) == 1
        assert result["items"][0].webhook_id == "webhook_123"
        assert result["items"][0].event_type == WebhookEvent.TICKET_CREATED
        assert result["items"][0].resource_id == "ticket_101"
        mock_client.execute_query.assert_called_once()

    # Test validation methods

    async def test_validate_create_data_valid_input(self, webhooks_manager, sample_webhook_input):
        """Test validation of valid create data."""
        # Should not raise any exceptions
        webhooks_manager._validate_create_data(sample_webhook_input.to_dict())

    async def test_validate_create_data_missing_required_fields(self, webhooks_manager):
        """Test validation with missing required fields."""
        invalid_data = {"name": "Test", "url": "https://example.com"}  # Missing events

        with pytest.raises(SuperOpsValidationError, match="Events are required"):
            webhooks_manager._validate_create_data(invalid_data)

        invalid_data = {"url": "https://example.com", "events": ["TICKET_CREATED"]}  # Missing name

        with pytest.raises(SuperOpsValidationError, match="Name is required"):
            webhooks_manager._validate_create_data(invalid_data)

    async def test_validate_create_data_invalid_url(self, webhooks_manager):
        """Test validation with invalid URL."""
        invalid_data = {
            "name": "Test Webhook",
            "url": "not-a-valid-url",
            "events": ["TICKET_CREATED"]
        }

        with pytest.raises(SuperOpsValidationError, match="URL must be a valid HTTP/HTTPS URL"):
            webhooks_manager._validate_create_data(invalid_data)

    async def test_validate_create_data_invalid_events(self, webhooks_manager):
        """Test validation with invalid events."""
        invalid_data = {
            "name": "Test Webhook",
            "url": "https://example.com/webhook",
            "events": []  # Empty events list
        }

        with pytest.raises(SuperOpsValidationError, match="At least one event must be specified"):
            webhooks_manager._validate_create_data(invalid_data)

    async def test_validate_update_data_valid_input(self, webhooks_manager):
        """Test validation of valid update data."""
        valid_data = {
            "name": "Updated Webhook",
            "description": "Updated description",
            "timeout": 60
        }

        # Should not raise any exceptions
        webhooks_manager._validate_update_data(valid_data)

    async def test_validate_update_data_invalid_url(self, webhooks_manager):
        """Test validation of update data with invalid URL."""
        invalid_data = {"url": "not-a-valid-url"}

        with pytest.raises(SuperOpsValidationError, match="URL must be a valid HTTP/HTTPS URL"):
            webhooks_manager._validate_update_data(invalid_data)

    # Test query building methods

    async def test_build_get_query(self, webhooks_manager):
        """Test building GET query."""
        query = webhooks_manager._build_get_query()

        assert "query GetWebhook" in query
        assert "webhook(id: $id)" in query
        assert "$id: ID!" in query

    async def test_build_list_query(self, webhooks_manager):
        """Test building LIST query."""
        query = webhooks_manager._build_list_query()

        assert "query ListWebhooks" in query
        assert "webhooks(" in query

    async def test_build_create_mutation(self, webhooks_manager):
        """Test building CREATE mutation."""
        mutation = webhooks_manager._build_create_mutation()

        assert "mutation CreateWebhook" in mutation
        assert "createWebhook(input: $input)" in mutation
        assert "$input: WebhookInput!" in mutation

    async def test_build_update_mutation(self, webhooks_manager):
        """Test building UPDATE mutation."""
        mutation = webhooks_manager._build_update_mutation()

        assert "mutation UpdateWebhook" in mutation
        assert "updateWebhook(id: $id, input: $input)" in mutation
        assert "$id: ID!" in mutation
        assert "$input: WebhookInput!" in mutation

    async def test_build_delete_mutation(self, webhooks_manager):
        """Test building DELETE mutation."""
        mutation = webhooks_manager._build_delete_mutation()

        assert "mutation DeleteWebhook" in mutation
        assert "deleteWebhook(id: $id)" in mutation
        assert "$id: ID!" in mutation

    # Test error handling

    async def test_api_error_handling(self, webhooks_manager, mock_client):
        """Test handling of API errors."""
        mock_client.execute_query.side_effect = SuperOpsAPIError("API Error", 500)

        with pytest.raises(SuperOpsAPIError, match="API Error"):
            await webhooks_manager.get_by_name("Test Webhook")

    async def test_network_error_handling(self, webhooks_manager, mock_client):
        """Test handling of network errors."""
        mock_client.execute_mutation.side_effect = Exception("Network error")

        with pytest.raises(Exception, match="Network error"):
            await webhooks_manager.test_webhook("webhook_123", WebhookEvent.TICKET_CREATED)

    # Test edge cases

    async def test_empty_response_handling(self, webhooks_manager, mock_client):
        """Test handling of empty API responses."""
        mock_client.execute_query.return_value = {"data": None}

        result = await webhooks_manager.get_by_name("Test Webhook")
        assert result is None

    async def test_malformed_response_handling(self, webhooks_manager, mock_client):
        """Test handling of malformed API responses."""
        mock_client.execute_query.return_value = {"data": {"webhooks": None}}

        result = await webhooks_manager.get_active_webhooks()
        assert result["items"] == []

    async def test_pagination_edge_cases(self, webhooks_manager, mock_client):
        """Test edge cases in pagination."""
        mock_client.execute_query.return_value = {
            "data": {
                "webhooks": {
                    "items": [],
                    "pagination": {
                        "page": 1,
                        "pageSize": 50,
                        "total": 0,
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                    },
                }
            }
        }

        result = await webhooks_manager.list(page=999, page_size=1)
        assert len(result["items"]) == 0
        assert result["pagination"]["total"] == 0