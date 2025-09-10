# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Webhooks manager for SuperOps API operations."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..exceptions import SuperOpsValidationError, SuperOpsAPIError
from ..graphql.types import Webhook, WebhookEvent, WebhookStatus, WebhookDelivery, WebhookEventRecord
from .base import ResourceManager


class WebhooksManager(ResourceManager[Webhook]):
    """Manager for webhook operations.

    Provides high-level methods for managing SuperOps webhooks including
    CRUD operations, webhook testing, delivery tracking, and event monitoring.
    """

    def __init__(self, client: "SuperOpsClient"):
        """Initialize the webhooks manager.

        Args:
            client: SuperOps client instance
        """
        super().__init__(client, Webhook, "webhook")

    async def get_by_name(self, name: str) -> Optional[Webhook]:
        """Get a webhook by name.

        Args:
            name: Webhook name to search for

        Returns:
            Webhook instance or None if not found

        Raises:
            SuperOpsValidationError: If name is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not name or not isinstance(name, str):
            raise SuperOpsValidationError("Webhook name must be a non-empty string")

        self.logger.debug(f"Getting webhook by name: {name}")

        # Use search with exact name match
        results = await self.search(f'name:"{name}"', page_size=1)

        # Return first exact match if any
        for webhook in results["items"]:
            if webhook.name == name:
                return webhook

        return None

    async def get_by_url(self, url: str) -> Optional[Webhook]:
        """Get a webhook by URL.

        Args:
            url: Webhook URL to search for

        Returns:
            Webhook instance or None if not found

        Raises:
            SuperOpsValidationError: If URL is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not url or not isinstance(url, str):
            raise SuperOpsValidationError("Webhook URL must be a non-empty string")

        self.logger.debug(f"Getting webhook by URL: {url}")

        # Use search with exact URL match
        results = await self.search(f'url:"{url}"', page_size=1)

        # Return first exact match if any
        for webhook in results["items"]:
            if webhook.url == url:
                return webhook

        return None

    async def get_active_webhooks(
        self, page: int = 1, page_size: int = 50
    ) -> Dict[str, Any]:
        """Get all active webhooks.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            Dictionary containing 'items' and 'pagination'

        Raises:
            SuperOpsAPIError: If the API request fails
        """
        return await self.list(
            page=page, 
            page_size=page_size, 
            filters={"status": WebhookStatus.ACTIVE, "is_active": True}
        )

    async def get_webhooks_by_event(
        self, event_type: WebhookEvent, page: int = 1, page_size: int = 50
    ) -> Dict[str, Any]:
        """Get webhooks that listen to a specific event type.

        Args:
            event_type: Event type to filter by
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            Dictionary containing 'items' and 'pagination'

        Raises:
            SuperOpsValidationError: If event_type is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not isinstance(event_type, WebhookEvent):
            raise SuperOpsValidationError("event_type must be a WebhookEvent")

        return await self.list(
            page=page, 
            page_size=page_size, 
            filters={"events": [event_type]}
        )

    async def test_webhook(self, webhook_id: str, event_type: WebhookEvent, 
                          test_payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Test a webhook by sending a test payload.

        Args:
            webhook_id: The webhook ID to test
            event_type: Event type to simulate
            test_payload: Optional test payload data

        Returns:
            Test result with delivery status

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not webhook_id or not isinstance(webhook_id, str):
            raise SuperOpsValidationError("Webhook ID must be a non-empty string")
        if not event_type or not isinstance(event_type, WebhookEvent):
            raise SuperOpsValidationError("Event type must be provided")

        self.logger.debug(f"Testing webhook {webhook_id} with event {event_type}")

        mutation = """
        mutation TestWebhook($webhookId: ID!, $eventType: WebhookEvent!, $testPayload: JSON) {
            testWebhook(webhookId: $webhookId, eventType: $eventType, testPayload: $testPayload) {
                success
                deliveryId
                responseStatusCode
                responseBody
                errorMessage
                executionTimeMs
            }
        }
        """

        variables = {
            "webhookId": webhook_id,
            "eventType": event_type.value,
            "testPayload": test_payload or {}
        }

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when testing webhook", 500, response)

        return response["data"].get("testWebhook", {})

    async def enable_webhook(self, webhook_id: str) -> Webhook:
        """Enable a webhook.

        Args:
            webhook_id: The webhook ID

        Returns:
            Updated webhook instance

        Raises:
            SuperOpsValidationError: If webhook_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not webhook_id or not isinstance(webhook_id, str):
            raise SuperOpsValidationError("Webhook ID must be a non-empty string")
            
        return await self.update(webhook_id, {
            "status": WebhookStatus.ACTIVE,
            "is_active": True
        })

    async def disable_webhook(self, webhook_id: str) -> Webhook:
        """Disable a webhook.

        Args:
            webhook_id: The webhook ID

        Returns:
            Updated webhook instance

        Raises:
            SuperOpsValidationError: If webhook_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not webhook_id or not isinstance(webhook_id, str):
            raise SuperOpsValidationError("Webhook ID must be a non-empty string")
            
        return await self.update(webhook_id, {
            "status": WebhookStatus.INACTIVE,
            "is_active": False
        })

    async def get_webhook_deliveries(
        self, webhook_id: str, page: int = 1, page_size: int = 50,
        delivery_filter: Optional["WebhookDeliveryFilter"] = None
    ) -> Dict[str, Any]:
        """Get delivery history for a webhook.

        Args:
            webhook_id: The webhook ID
            page: Page number (1-based)
            page_size: Number of items per page
            delivery_filter: Optional filter for delivery status and event type

        Returns:
            Dictionary containing webhook deliveries

        Raises:
            SuperOpsValidationError: If webhook_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not webhook_id or not isinstance(webhook_id, str):
            raise SuperOpsValidationError("Webhook ID must be a non-empty string")

        self.logger.debug(f"Getting deliveries for webhook: {webhook_id}")

        query = """
        query GetWebhookDeliveries(
            $webhookId: ID!,
            $page: Int!,
            $pageSize: Int!,
            $deliveryFilter: WebhookDeliveryFilter
        ) {
            webhookDeliveries(
                webhookId: $webhookId,
                filters: $deliveryFilter,
                pagination: { page: $page, pageSize: $pageSize },
                sort: { field: "createdAt", direction: DESC }
            ) {
                items {
                    id
                    webhookId
                    eventType
                    status
                    url
                    responseStatusCode
                    responseBody
                    attemptCount
                    deliveredAt
                    errorMessage
                    executionTimeMs
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
            "webhookId": webhook_id,
            "page": page,
            "pageSize": page_size
        }
        
        if delivery_filter:
            variables["filters"] = delivery_filter.to_dict()

        response = await self.client.execute_query(query, variables)

        if not response.get("data"):
            return {"items": [], "pagination": self._empty_pagination()}

        deliveries_data = response["data"].get("webhookDeliveries")
        if not deliveries_data:
            return {"items": [], "pagination": self._empty_pagination()}

        # Convert to WebhookDelivery instances
        items = [WebhookDelivery.from_dict(item) for item in deliveries_data.get("items", [])]
        pagination = deliveries_data.get("pagination", self._empty_pagination())

        return {"items": items, "pagination": pagination}

    async def retry_failed_delivery(self, delivery_id: str) -> Dict[str, Any]:
        """Retry a failed webhook delivery.

        Args:
            delivery_id: The delivery ID to retry

        Returns:
            Retry result

        Raises:
            SuperOpsValidationError: If delivery_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not delivery_id or not isinstance(delivery_id, str):
            raise SuperOpsValidationError("Delivery ID must be a non-empty string")

        self.logger.debug(f"Retrying webhook delivery: {delivery_id}")

        mutation = """
        mutation RetryWebhookDelivery($deliveryId: ID!) {
            retryWebhookDelivery(deliveryId: $deliveryId) {
                success
                newDeliveryId
                status
                errorMessage
            }
        }
        """

        variables = {"deliveryId": delivery_id}

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when retrying delivery", 500, response)

        return response["data"].get("retryWebhookDelivery", {})

    async def get_webhook_events(
        self,
        webhook_id: str,
        page: int = 1,
        page_size: int = 50,
        event_type: Optional[WebhookEvent] = None,
    ) -> Dict[str, Any]:
        """Get event records for a webhook.

        Args:
            webhook_id: The webhook ID
            page: Page number (1-based)
            page_size: Number of items per page  
            event_type: Optional event type filter

        Returns:
            Dictionary containing webhook event records

        Raises:
            SuperOpsValidationError: If webhook_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not webhook_id or not isinstance(webhook_id, str):
            raise SuperOpsValidationError("Webhook ID must be a non-empty string")
        if page < 1:
            raise SuperOpsValidationError("Page number must be >= 1")
        if page_size < 1 or page_size > 1000:
            raise SuperOpsValidationError("Page size must be between 1 and 1000")

        self.logger.debug(f"Getting events for webhook: {webhook_id}")

        query = """
        query WebhookEventRecords(
            $webhookId: ID!,
            $page: Int!,
            $pageSize: Int!,
            $eventType: WebhookEvent
        ) {
            webhookEventRecords(
                webhookId: $webhookId,
                page: $page,
                pageSize: $pageSize,
                eventType: $eventType
            ) {
                items {
                    id
                    webhookId
                    eventType
                    resourceId
                    resourceType
                    timestamp
                    payload
                    deliveryStatus
                    attemptCount
                    lastAttempt
                    errorMessage
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
            "webhookId": webhook_id,
            "page": page,
            "pageSize": page_size,
        }
        
        if event_type:
            variables["eventType"] = event_type.value

        response = await self.client.execute_query(query, variables)

        if not response.get("data"):
            return {"items": [], "pagination": self._empty_pagination()}

        events_data = response["data"].get("webhookEventRecords")
        if not events_data:
            return {"items": [], "pagination": self._empty_pagination()}

        # Convert items to WebhookEventRecord instances
        from ..graphql.types import WebhookEventRecord
        items = [
            WebhookEventRecord.from_dict(item) 
            for item in events_data.get("items", [])
        ]

        pagination = events_data.get("pagination", self._empty_pagination())

        return {"items": items, "pagination": pagination}

    # Protected methods for GraphQL query building

    def _build_get_query(self, **kwargs) -> str:
        """Build GraphQL query for getting a single webhook."""
        include_deliveries = kwargs.get("include_deliveries", False)
        include_events = kwargs.get("include_events", False)

        fields = [
            "id",
            "name", 
            "url",
            "events",
            "status",
            "secret",
            "description",
            "isActive",
            "retryCount",
            "timeoutSeconds",
            "headers",
            "lastTriggered",
            "lastSuccess",
            "lastFailure",
            "failureCount",
            "successCount",
            "totalDeliveries",
            "contentType",
            "tags",
            "createdAt",
            "updatedAt"
        ]

        if include_deliveries:
            fields.append("""
                deliveries {
                    id
                    eventType
                    status
                    responseStatusCode
                    attemptCount
                    deliveredAt
                    errorMessage
                    createdAt
                }
            """)

        if include_events:
            fields.append("""
                events {
                    id
                    eventType
                    resourceType
                    resourceId
                    triggeredAt
                    createdAt
                }
            """)

        field_selection = "\n".join(fields)

        return f"""
        query GetWebhook($id: ID!) {{
            webhook(id: $id) {{
                {field_selection}
            }}
        }}
        """

    def _build_list_query(self, **kwargs) -> str:
        """Build GraphQL query for listing webhooks."""
        return """
        query ListWebhooks(
            $page: Int!,
            $pageSize: Int!,
            $filters: WebhookFilter,
            $sortBy: String,
            $sortOrder: String
        ) {
            webhooks(
                pagination: { page: $page, pageSize: $pageSize }
                filters: $filters
                sort: { field: $sortBy, direction: $sortOrder }
            ) {
                items {
                    id
                    name
                    url
                    events
                    status
                    isActive
                    lastTriggered
                    successCount
                    failureCount
                    totalDeliveries
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
        """Build GraphQL mutation for creating a webhook."""
        return """
        mutation CreateWebhook($input: WebhookInput!) {
            createWebhook(input: $input) {
                id
                name
                url
                events
                status
                description
                isActive
                retryCount
                timeoutSeconds
                headers
                contentType
                tags
                createdAt
                updatedAt
            }
        }
        """

    def _build_update_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for updating a webhook."""
        return """
        mutation UpdateWebhook($id: ID!, $input: WebhookInput!) {
            updateWebhook(id: $id, input: $input) {
                id
                name
                url
                events
                status
                description
                isActive
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
                createdAt
                updatedAt
            }
        }
        """

    def _build_delete_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for deleting a webhook."""
        return """
        mutation DeleteWebhook($id: ID!) {
            deleteWebhook(id: $id) {
                success
                message
            }
        }
        """

    def _build_search_query(self, **kwargs) -> str:
        """Build GraphQL query for searching webhooks."""
        return """
        query SearchWebhooks(
            $query: String!,
            $page: Int!,
            $pageSize: Int!
        ) {
            searchWebhooks(
                query: $query
                pagination: { page: $page, pageSize: $pageSize }
            ) {
                items {
                    id
                    name
                    url
                    events
                    status
                    isActive
                    description
                    lastTriggered
                    successCount
                    failureCount
                    tags
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
        """Validate data for webhook creation."""
        validated_data = super()._validate_create_data(data)

        # Ensure required fields are present
        if "name" not in validated_data:
            raise SuperOpsValidationError("Name is required")
        if "url" not in validated_data:
            raise SuperOpsValidationError("URL is required")
        if "events" not in validated_data:
            raise SuperOpsValidationError("Events are required")

        # Validate URL format
        url = validated_data.get("url", "")
        if not url.startswith(("http://", "https://")):
            raise SuperOpsValidationError("Webhook URL must be a valid HTTP/HTTPS URL")

        # Validate events
        events = validated_data.get("events", [])
        if not events:
            raise SuperOpsValidationError("At least one event must be specified")

        # Convert string events to WebhookEvent enums for validation
        valid_events = []
        for event in events:
            if isinstance(event, str):
                try:
                    valid_events.append(WebhookEvent(event))
                except ValueError:
                    raise SuperOpsValidationError(f"Invalid webhook event: {event}")
            elif isinstance(event, WebhookEvent):
                valid_events.append(event)
            else:
                raise SuperOpsValidationError(f"Invalid webhook event type: {type(event)}")

        validated_data["events"] = [event.value for event in valid_events]

        # Set defaults
        if "status" not in validated_data:
            validated_data["status"] = WebhookStatus.ACTIVE.value
        if "is_active" not in validated_data:
            validated_data["is_active"] = True
        if "retry_count" not in validated_data:
            validated_data["retry_count"] = 3
        if "timeout_seconds" not in validated_data:
            validated_data["timeout_seconds"] = 30
        if "content_type" not in validated_data:
            validated_data["content_type"] = "application/json"

        return validated_data

    def _validate_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data for webhook updates."""
        validated_data = super()._validate_update_data(data)

        # Validate URL if provided
        if "url" in validated_data:
            url = validated_data["url"]
            if url and not url.startswith(("http://", "https://")):
                raise SuperOpsValidationError("Webhook URL must be a valid HTTP/HTTPS URL")

        # Validate events if provided
        if "events" in validated_data:
            events = validated_data["events"]
            if events is not None:
                if not events:
                    raise SuperOpsValidationError("At least one webhook event must be specified")

                # Convert string events to WebhookEvent enums for validation
                valid_events = []
                for event in events:
                    if isinstance(event, str):
                        try:
                            valid_events.append(WebhookEvent(event))
                        except ValueError:
                            raise SuperOpsValidationError(f"Invalid webhook event: {event}")
                    elif isinstance(event, WebhookEvent):
                        valid_events.append(event)
                    else:
                        raise SuperOpsValidationError(f"Invalid webhook event type: {type(event)}")

                validated_data["events"] = [event.value for event in valid_events]

        return validated_data