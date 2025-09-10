# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Integration tests for py-superops client library.

These tests verify end-to-end workflows and integration between components.
They use mocked HTTP responses but test the complete flow from client
to managers to GraphQL utilities.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from py_superops import SuperOpsClient, SuperOpsConfig, create_client
from py_superops.exceptions import (
    SuperOpsAPIError,
    SuperOpsAuthenticationError,
    SuperOpsNetworkError,
    SuperOpsRateLimitError,
    SuperOpsResourceNotFoundError,
    SuperOpsTimeoutError,
    SuperOpsValidationError,
)
from py_superops.graphql.types import AssetStatus, ClientStatus, TicketPriority, TicketStatus


class TestClientIntegration:
    """Integration tests for the main client."""

    @pytest.mark.asyncio
    async def test_complete_client_workflow(self, test_config, mock_httpx_response):
        """Test a complete client workflow from initialization to cleanup."""
        # Setup mock responses for different operations
        responses = [
            # Connection test response
            mock_httpx_response(
                200,
                {
                    "data": {
                        "viewer": {
                            "id": "user-123",
                            "name": "Test User",
                            "email": "test@example.com",
                        }
                    }
                },
            ),
            # Client list response
            mock_httpx_response(
                200,
                {
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
                                }
                            ],
                            "pagination": {
                                "page": 1,
                                "pageSize": 50,
                                "total": 1,
                                "hasNextPage": False,
                                "hasPreviousPage": False,
                            },
                        }
                    }
                },
            ),
            # Client get response
            mock_httpx_response(
                200,
                {
                    "data": {
                        "client": {
                            "id": "client-1",
                            "name": "Client One",
                            "email": "one@example.com",
                            "status": "ACTIVE",
                            "createdAt": datetime.now(timezone.utc).isoformat(),
                            "updatedAt": datetime.now(timezone.utc).isoformat(),
                        }
                    }
                },
            ),
        ]

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.side_effect = responses

            async with SuperOpsClient(test_config) as client:
                # Test connection
                connection_info = await client.test_connection()
                assert connection_info["connected"] is True
                assert connection_info["user"]["name"] == "Test User"

                # List clients
                client_list = await client.clients.list(page_size=50)
                assert len(client_list["items"]) == 1
                assert client_list["items"][0].name == "Client One"

                # Get specific client
                client_obj = await client.clients.get("client-1")
                assert client_obj is not None
                assert client_obj.name == "Client One"
                assert client_obj.status == ClientStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_cross_manager_operations(self, test_config, mock_httpx_response):
        """Test operations across multiple managers."""
        # Mock responses for client, tickets, and assets
        client_response = mock_httpx_response(
            200,
            {
                "data": {
                    "client": {
                        "id": "client-123",
                        "name": "Acme Corp",
                        "email": "admin@acme.com",
                        "status": "ACTIVE",
                        "createdAt": datetime.now(timezone.utc).isoformat(),
                        "updatedAt": datetime.now(timezone.utc).isoformat(),
                    }
                }
            },
        )

        tickets_response = mock_httpx_response(
            200,
            {
                "data": {
                    "tickets": {
                        "items": [
                            {
                                "id": "ticket-1",
                                "clientId": "client-123",
                                "title": "Server Issue",
                                "status": "OPEN",
                                "priority": "HIGH",
                                "createdAt": datetime.now(timezone.utc).isoformat(),
                            }
                        ],
                        "pagination": {
                            "page": 1,
                            "pageSize": 50,
                            "total": 1,
                            "hasNextPage": False,
                            "hasPreviousPage": False,
                        },
                    }
                }
            },
        )

        assets_response = mock_httpx_response(
            200,
            {
                "data": {
                    "assets": {
                        "items": [
                            {
                                "id": "asset-1",
                                "clientId": "client-123",
                                "name": "Production Server",
                                "assetType": "Server",
                                "status": "ACTIVE",
                            }
                        ],
                        "pagination": {
                            "page": 1,
                            "pageSize": 50,
                            "total": 1,
                            "hasNextPage": False,
                            "hasPreviousPage": False,
                        },
                    }
                }
            },
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.side_effect = [client_response, tickets_response, assets_response]

            async with SuperOpsClient(test_config) as client:
                # Get client
                client_obj = await client.clients.get("client-123")
                assert client_obj.name == "Acme Corp"

                # Get tickets for this client
                tickets = await client.tickets.list(filters={"client_id": "client-123"})
                assert len(tickets["items"]) == 1
                assert tickets["items"][0].title == "Server Issue"

                # Get assets for this client
                assets = await client.assets.list(filters={"client_id": "client-123"})
                assert len(assets["items"]) == 1
                assert assets["items"][0].name == "Production Server"

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, test_config, mock_httpx_response):
        """Test concurrent operations across managers."""
        # Setup mock responses for concurrent requests
        client_responses = [
            mock_httpx_response(
                200,
                {
                    "data": {
                        "client": {
                            "id": f"client-{i}",
                            "name": f"Client {i}",
                            "email": f"client{i}@example.com",
                            "status": "ACTIVE",
                            "createdAt": datetime.now(timezone.utc).isoformat(),
                            "updatedAt": datetime.now(timezone.utc).isoformat(),
                        }
                    }
                },
            )
            for i in range(5)
        ]

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.side_effect = client_responses

            async with SuperOpsClient(test_config) as client:
                # Concurrent client requests
                tasks = [client.clients.get(f"client-{i}") for i in range(5)]

                results = await asyncio.gather(*tasks)

                # Verify all requests completed successfully
                assert len(results) == 5
                for i, result in enumerate(results):
                    assert result is not None
                    assert result.name == f"Client {i}"


class TestErrorHandlingIntegration:
    """Integration tests for error handling across components."""

    @pytest.mark.asyncio
    async def test_authentication_error_flow(self, test_config, mock_httpx_response):
        """Test authentication error handling across the stack."""
        auth_error_response = mock_httpx_response(
            401,
            {
                "errors": [
                    {"message": "Authentication failed", "extensions": {"code": "UNAUTHENTICATED"}}
                ]
            },
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = auth_error_response

            async with SuperOpsClient(test_config) as client:
                with pytest.raises(SuperOpsAuthenticationError):
                    await client.clients.get("client-123")

    @pytest.mark.asyncio
    async def test_rate_limiting_integration(self, test_config, rate_limit_response):
        """Test rate limiting error handling."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = rate_limit_response

            async with SuperOpsClient(test_config) as client:
                with pytest.raises(SuperOpsRateLimitError) as exc_info:
                    await client.clients.list()

                # Verify rate limit information is captured
                error = exc_info.value
                assert error.retry_after is not None
                assert error.status_code == 429

    @pytest.mark.asyncio
    async def test_network_error_integration(self, test_config, network_error):
        """Test network error handling integration."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.side_effect = network_error

            async with SuperOpsClient(test_config) as client:
                with pytest.raises(SuperOpsNetworkError):
                    await client.clients.get("client-123")

    @pytest.mark.asyncio
    async def test_timeout_error_integration(self, test_config, timeout_error):
        """Test timeout error handling integration."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.side_effect = timeout_error

            async with SuperOpsClient(test_config) as client:
                with pytest.raises(SuperOpsTimeoutError):
                    await client.tickets.list()

    @pytest.mark.asyncio
    async def test_resource_not_found_integration(self, test_config, mock_httpx_response):
        """Test resource not found error integration."""
        not_found_response = mock_httpx_response(200, {"data": {"client": None}})

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = not_found_response

            async with SuperOpsClient(test_config) as client:
                # Get should return None for not found
                result = await client.clients.get("nonexistent")
                assert result is None

    @pytest.mark.asyncio
    async def test_validation_error_integration(self, test_config):
        """Test validation error integration."""
        async with SuperOpsClient(test_config) as client:
            # Test various validation scenarios
            with pytest.raises(SuperOpsValidationError):
                await client.clients.get("")  # Empty ID

            with pytest.raises(SuperOpsValidationError):
                await client.clients.list(page=0)  # Invalid page

            with pytest.raises(SuperOpsValidationError):
                await client.tickets.create({})  # Empty data


class TestComplexWorkflows:
    """Integration tests for complex, real-world workflows."""

    @pytest.mark.asyncio
    async def test_ticket_management_workflow(self, test_config, mock_httpx_response):
        """Test a complete ticket management workflow."""
        # Mock responses for the workflow
        responses = [
            # Create ticket
            mock_httpx_response(
                200,
                {
                    "data": {
                        "createTicket": {
                            "id": "ticket-new",
                            "clientId": "client-123",
                            "title": "New Issue",
                            "status": "OPEN",
                            "priority": "NORMAL",
                            "createdAt": datetime.now(timezone.utc).isoformat(),
                            "updatedAt": datetime.now(timezone.utc).isoformat(),
                        }
                    }
                },
            ),
            # Update ticket
            mock_httpx_response(
                200,
                {
                    "data": {
                        "updateTicket": {
                            "id": "ticket-new",
                            "clientId": "client-123",
                            "title": "New Issue",
                            "status": "IN_PROGRESS",
                            "priority": "HIGH",
                            "assignedTo": "user-456",
                            "updatedAt": datetime.now(timezone.utc).isoformat(),
                        }
                    }
                },
            ),
            # Get updated ticket
            mock_httpx_response(
                200,
                {
                    "data": {
                        "ticket": {
                            "id": "ticket-new",
                            "clientId": "client-123",
                            "title": "New Issue",
                            "status": "IN_PROGRESS",
                            "priority": "HIGH",
                            "assignedTo": "user-456",
                            "createdAt": datetime.now(timezone.utc).isoformat(),
                            "updatedAt": datetime.now(timezone.utc).isoformat(),
                        }
                    }
                },
            ),
            # Close ticket
            mock_httpx_response(
                200,
                {
                    "data": {
                        "updateTicket": {
                            "id": "ticket-new",
                            "status": "RESOLVED",
                            "resolution": "Issue resolved",
                            "updatedAt": datetime.now(timezone.utc).isoformat(),
                        }
                    }
                },
            ),
        ]

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.side_effect = responses

            async with SuperOpsClient(test_config) as client:
                # Create new ticket
                new_ticket = await client.tickets.create(
                    {
                        "client_id": "client-123",
                        "title": "New Issue",
                        "description": "Description of the issue",
                        "priority": TicketPriority.NORMAL,
                        "status": TicketStatus.OPEN,
                    }
                )
                assert new_ticket.id == "ticket-new"
                assert new_ticket.status == TicketStatus.OPEN

                # Update ticket priority and assign
                updated_ticket = await client.tickets.update(
                    new_ticket.id,
                    {
                        "priority": TicketPriority.HIGH,
                        "status": TicketStatus.IN_PROGRESS,
                        "assigned_to": "user-456",
                    },
                )
                assert updated_ticket.priority == TicketPriority.HIGH
                assert updated_ticket.status == TicketStatus.IN_PROGRESS

                # Get ticket to verify changes
                current_ticket = await client.tickets.get(new_ticket.id)
                assert current_ticket.priority == TicketPriority.HIGH
                assert current_ticket.assigned_to == "user-456"

                # Resolve ticket
                resolved_ticket = await client.tickets.update(
                    new_ticket.id,
                    {
                        "status": TicketStatus.RESOLVED,
                        "resolution": "Issue resolved",
                    },
                )
                assert resolved_ticket.status == TicketStatus.RESOLVED

    @pytest.mark.asyncio
    async def test_client_onboarding_workflow(self, test_config, mock_httpx_response):
        """Test a complete client onboarding workflow."""
        # Mock responses for onboarding workflow
        responses = [
            # Create client
            mock_httpx_response(
                200,
                {
                    "data": {
                        "createClient": {
                            "id": "client-new",
                            "name": "New Client Corp",
                            "email": "admin@newclient.com",
                            "status": "ACTIVE",
                            "createdAt": datetime.now(timezone.utc).isoformat(),
                            "updatedAt": datetime.now(timezone.utc).isoformat(),
                        }
                    }
                },
            ),
            # Create primary site
            mock_httpx_response(
                200,
                {
                    "data": {
                        "createSite": {
                            "id": "site-new",
                            "clientId": "client-new",
                            "name": "Headquarters",
                            "address": "123 Business St",
                            "isPrimary": True,
                        }
                    }
                },
            ),
            # Create contact
            mock_httpx_response(
                200,
                {
                    "data": {
                        "createContact": {
                            "id": "contact-new",
                            "clientId": "client-new",
                            "name": "John Admin",
                            "email": "john@newclient.com",
                            "role": "Administrator",
                            "isPrimary": True,
                        }
                    }
                },
            ),
            # Create first asset
            mock_httpx_response(
                200,
                {
                    "data": {
                        "createAsset": {
                            "id": "asset-new",
                            "clientId": "client-new",
                            "name": "Primary Server",
                            "assetType": "Server",
                            "status": "ACTIVE",
                        }
                    }
                },
            ),
        ]

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.side_effect = responses

            async with SuperOpsClient(test_config) as client:
                # Create new client
                new_client = await client.clients.create(
                    {
                        "name": "New Client Corp",
                        "email": "admin@newclient.com",
                        "phone": "+1-555-123-4567",
                        "status": ClientStatus.ACTIVE,
                    }
                )
                assert new_client.name == "New Client Corp"

                # Create primary site
                site = await client.sites.create(
                    {
                        "client_id": new_client.id,
                        "name": "Headquarters",
                        "address": "123 Business St",
                        "city": "Business City",
                        "state": "CA",
                        "is_primary": True,
                    }
                )
                assert site.name == "Headquarters"
                assert site.is_primary is True

                # Create primary contact
                contact = await client.contacts.create(
                    {
                        "client_id": new_client.id,
                        "name": "John Admin",
                        "email": "john@newclient.com",
                        "role": "Administrator",
                        "is_primary": True,
                    }
                )
                assert contact.name == "John Admin"
                assert contact.is_primary is True

                # Create first asset
                asset = await client.assets.create(
                    {
                        "client_id": new_client.id,
                        "name": "Primary Server",
                        "asset_type": "Server",
                        "status": AssetStatus.ACTIVE,
                    }
                )
                assert asset.name == "Primary Server"
                assert asset.status == AssetStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_search_and_filter_workflow(self, test_config, mock_httpx_response):
        """Test complex search and filtering workflows."""
        # Mock responses for search operations
        responses = [
            # Search clients
            mock_httpx_response(
                200,
                {
                    "data": {
                        "searchClients": {
                            "items": [
                                {
                                    "id": "client-1",
                                    "name": "Acme Corp",
                                    "email": "admin@acme.com",
                                    "status": "ACTIVE",
                                },
                                {
                                    "id": "client-2",
                                    "name": "Acme Industries",
                                    "email": "info@acmeindustries.com",
                                    "status": "ACTIVE",
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
                },
            ),
            # Filter tickets by client
            mock_httpx_response(
                200,
                {
                    "data": {
                        "tickets": {
                            "items": [
                                {
                                    "id": "ticket-1",
                                    "clientId": "client-1",
                                    "title": "Issue 1",
                                    "status": "OPEN",
                                    "priority": "HIGH",
                                },
                                {
                                    "id": "ticket-2",
                                    "clientId": "client-1",
                                    "title": "Issue 2",
                                    "status": "IN_PROGRESS",
                                    "priority": "NORMAL",
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
                },
            ),
            # Filter assets by status
            mock_httpx_response(
                200,
                {
                    "data": {
                        "assets": {
                            "items": [
                                {
                                    "id": "asset-1",
                                    "clientId": "client-1",
                                    "name": "Server 1",
                                    "status": "ACTIVE",
                                    "assetType": "Server",
                                },
                                {
                                    "id": "asset-2",
                                    "clientId": "client-1",
                                    "name": "Workstation 1",
                                    "status": "ACTIVE",
                                    "assetType": "Workstation",
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
                },
            ),
        ]

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.side_effect = responses

            async with SuperOpsClient(test_config) as client:
                # Search for clients containing "Acme"
                search_results = await client.clients.search("Acme")
                assert len(search_results["items"]) == 2
                assert all("Acme" in item.name for item in search_results["items"])

                # Get tickets for a specific client
                client_tickets = await client.tickets.list(filters={"client_id": "client-1"})
                assert len(client_tickets["items"]) == 2
                assert all(ticket.client_id == "client-1" for ticket in client_tickets["items"])

                # Get active assets for the client
                active_assets = await client.assets.list(
                    filters={"client_id": "client-1", "status": AssetStatus.ACTIVE}
                )
                assert len(active_assets["items"]) == 2
                assert all(asset.status == AssetStatus.ACTIVE for asset in active_assets["items"])


class TestConfigurationIntegration:
    """Integration tests for different configuration scenarios."""

    @pytest.mark.asyncio
    async def test_eu_datacenter_integration(self, eu_config, mock_httpx_response):
        """Test integration with EU datacenter configuration."""
        connection_response = mock_httpx_response(
            200,
            {
                "data": {
                    "viewer": {
                        "id": "user-123",
                        "name": "EU User",
                        "email": "user@eu.example.com",
                        "region": "EU",
                    }
                }
            },
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = connection_response

            async with SuperOpsClient(eu_config) as client:
                connection_info = await client.test_connection()
                assert connection_info["connected"] is True
                assert connection_info["user"]["name"] == "EU User"
                assert client.config.is_eu_datacenter() is True

    @pytest.mark.asyncio
    async def test_convenience_function_integration(self, mock_httpx_response):
        """Test integration using convenience functions."""
        connection_response = mock_httpx_response(
            200,
            {
                "data": {
                    "viewer": {"id": "user-123", "name": "Test User", "email": "test@example.com"}
                }
            },
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = connection_response

            # Test create_client convenience function
            async with create_client(
                api_key="test-api-key-12345678901234567890", base_url="https://api.superops.com/v1"
            ) as client:
                connection_info = await client.test_connection()
                assert connection_info["connected"] is True

    @pytest.mark.asyncio
    async def test_custom_timeout_integration(self, mock_httpx_response, timeout_error):
        """Test integration with custom timeout configuration."""
        # Create config with short timeout
        config = SuperOpsConfig(
            api_key="test-api-key-12345678901234567890",
            base_url="https://api.superops.com/v1",
            timeout=0.001,  # Very short timeout
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.side_effect = timeout_error

            async with SuperOpsClient(config) as client:
                with pytest.raises(SuperOpsTimeoutError):
                    await client.clients.list()


class TestPerformanceIntegration:
    """Integration tests for performance characteristics."""

    @pytest.mark.asyncio
    async def test_large_dataset_handling(
        self, test_config, mock_httpx_response, performance_timer
    ):
        """Test handling of large datasets."""
        # Create response with many items
        large_response = mock_httpx_response(
            200,
            {
                "data": {
                    "clients": {
                        "items": [
                            {
                                "id": f"client-{i}",
                                "name": f"Client {i}",
                                "email": f"client{i}@example.com",
                                "status": "ACTIVE",
                                "createdAt": datetime.now(timezone.utc).isoformat(),
                                "updatedAt": datetime.now(timezone.utc).isoformat(),
                            }
                            for i in range(500)
                        ],
                        "pagination": {
                            "page": 1,
                            "pageSize": 500,
                            "total": 500,
                            "hasNextPage": False,
                            "hasPreviousPage": False,
                        },
                    }
                }
            },
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = large_response

            async with SuperOpsClient(test_config) as client:
                with performance_timer() as timer:
                    result = await client.clients.list(page_size=500)

                # Verify data processing performance
                assert len(result["items"]) == 500
                assert result["pagination"]["total"] == 500

                # Should process large dataset quickly
                assert timer.elapsed < 1.0  # Should complete in less than 1 second

    @pytest.mark.asyncio
    async def test_concurrent_different_operations(
        self, test_config, mock_httpx_response, performance_timer
    ):
        """Test concurrent operations of different types."""
        # Setup different response types
        responses = [
            mock_httpx_response(
                200, {"data": {"clients": {"items": [], "pagination": {"total": 0}}}}
            ),
            mock_httpx_response(
                200, {"data": {"tickets": {"items": [], "pagination": {"total": 0}}}}
            ),
            mock_httpx_response(
                200, {"data": {"assets": {"items": [], "pagination": {"total": 0}}}}
            ),
            mock_httpx_response(
                200, {"data": {"sites": {"items": [], "pagination": {"total": 0}}}}
            ),
            mock_httpx_response(
                200, {"data": {"contacts": {"items": [], "pagination": {"total": 0}}}}
            ),
        ]

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.side_effect = responses

            async with SuperOpsClient(test_config) as client:
                with performance_timer() as timer:
                    # Execute different operations concurrently
                    results = await asyncio.gather(
                        client.clients.list(),
                        client.tickets.list(),
                        client.assets.list(),
                        client.sites.list(),
                        client.contacts.list(),
                    )

                # Verify all operations completed
                assert len(results) == 5
                assert all("items" in result for result in results)

                # Should handle concurrent different operations efficiently
                assert timer.elapsed < 2.0  # Should complete in less than 2 seconds
