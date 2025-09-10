# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Site manager for SuperOps API operations."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..exceptions import SuperOpsValidationError
from ..graphql.types import Site
from .base import ResourceManager


class SiteManager(ResourceManager[Site]):
    """Manager for site/location operations.

    Provides high-level methods for managing SuperOps sites including
    CRUD operations, location management, and site-specific workflows.
    """

    def __init__(self, client: "SuperOpsClient"):
        """Initialize the site manager.

        Args:
            client: SuperOps client instance
        """
        super().__init__(client, Site, "site")

    async def get_by_client(
        self,
        client_id: str,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get sites for a specific client.

        Args:
            client_id: The client ID
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: name)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Site]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not client_id or not isinstance(client_id, str):
            raise SuperOpsValidationError("Client ID must be a non-empty string")

        self.logger.debug(f"Getting sites for client: {client_id}")

        filters = {"client_id": client_id}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
        )

    async def get_by_name(self, name: str, client_id: Optional[str] = None) -> Optional[Site]:
        """Get a site by name.

        Args:
            name: Site name to search for
            client_id: Optional client ID to limit search scope

        Returns:
            Site instance or None if not found

        Raises:
            SuperOpsValidationError: If name is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not name or not isinstance(name, str):
            raise SuperOpsValidationError("Site name must be a non-empty string")

        self.logger.debug(f"Getting site by name: {name}")

        # Build search query
        search_query = f'name:"{name}"'
        if client_id:
            search_query += f' client_id:"{client_id}"'

        results = await self.search(search_query, page_size=10)

        # Return first exact match if any
        for site in results["items"]:
            if site.name == name:
                if client_id is None or site.client_id == client_id:
                    return site

        return None

    async def get_by_timezone(
        self,
        timezone: str,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get sites in a specific timezone.

        Args:
            timezone: Timezone to filter by (e.g., 'America/New_York')
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: name)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Site]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not timezone or not isinstance(timezone, str):
            raise SuperOpsValidationError("Timezone must be a non-empty string")

        self.logger.debug(f"Getting sites in timezone: {timezone}")

        filters = {"timezone": timezone}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
        )

    async def get_with_assets(
        self, site_id: str, include_inactive_assets: bool = False
    ) -> Optional[Site]:
        """Get a site with all associated assets loaded.

        Args:
            site_id: The site ID
            include_inactive_assets: Whether to include inactive assets

        Returns:
            Site instance with assets or None if not found

        Raises:
            SuperOpsValidationError: If site_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not site_id or not isinstance(site_id, str):
            raise SuperOpsValidationError(f"Invalid site ID: {site_id}")

        self.logger.debug(f"Getting site with assets: {site_id}")

        return await self.get(
            site_id, include_assets=True, include_inactive_assets=include_inactive_assets
        )

    async def get_with_contacts(self, site_id: str) -> Optional[Site]:
        """Get a site with all associated contacts loaded.

        Args:
            site_id: The site ID

        Returns:
            Site instance with contacts or None if not found

        Raises:
            SuperOpsValidationError: If site_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not site_id or not isinstance(site_id, str):
            raise SuperOpsValidationError(f"Invalid site ID: {site_id}")

        self.logger.debug(f"Getting site with contacts: {site_id}")

        return await self.get(site_id, include_contacts=True)

    async def get_asset_count(self, site_id: str) -> int:
        """Get the number of assets at a site.

        Args:
            site_id: The site ID

        Returns:
            Number of assets at the site

        Raises:
            SuperOpsValidationError: If site_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not site_id or not isinstance(site_id, str):
            raise SuperOpsValidationError(f"Invalid site ID: {site_id}")

        self.logger.debug(f"Getting asset count for site: {site_id}")

        query = """
            query GetSiteAssetCount($siteId: ID!) {
                site(id: $siteId) {
                    assetCount
                }
            }
        """

        variables = {"siteId": site_id}

        response = await self.client.execute_query(query, variables)

        if not response.get("data") or not response["data"].get("site"):
            return 0

        return response["data"]["site"].get("assetCount", 0)

    async def get_ticket_count(self, site_id: str, status_filter: Optional[str] = None) -> int:
        """Get the number of tickets for a site.

        Args:
            site_id: The site ID
            status_filter: Optional status to filter by

        Returns:
            Number of tickets for the site

        Raises:
            SuperOpsValidationError: If site_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not site_id or not isinstance(site_id, str):
            raise SuperOpsValidationError(f"Invalid site ID: {site_id}")

        self.logger.debug(f"Getting ticket count for site: {site_id}")

        query = """
            query GetSiteTicketCount($siteId: ID!, $status: String) {
                site(id: $siteId) {
                    ticketCount(status: $status)
                }
            }
        """

        variables = {"siteId": site_id, "status": status_filter}

        response = await self.client.execute_query(query, variables)

        if not response.get("data") or not response["data"].get("site"):
            return 0

        return response["data"]["site"].get("ticketCount", 0)

    async def set_timezone(self, site_id: str, timezone: str) -> Site:
        """Set the timezone for a site.

        Args:
            site_id: The site ID
            timezone: Timezone string (e.g., 'America/New_York')

        Returns:
            Updated site instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not site_id or not isinstance(site_id, str):
            raise SuperOpsValidationError(f"Invalid site ID: {site_id}")
        if not timezone or not isinstance(timezone, str):
            raise SuperOpsValidationError("Timezone must be a non-empty string")

        self.logger.debug(f"Setting timezone for site {site_id} to {timezone}")

        return await self.update(site_id, {"timezone": timezone})

    async def update_address(
        self, site_id: str, address: str, validate_address: bool = True
    ) -> Site:
        """Update the address for a site.

        Args:
            site_id: The site ID
            address: New address
            validate_address: Whether to validate address format

        Returns:
            Updated site instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not site_id or not isinstance(site_id, str):
            raise SuperOpsValidationError(f"Invalid site ID: {site_id}")
        if not address or not isinstance(address, str):
            raise SuperOpsValidationError("Address must be a non-empty string")

        self.logger.debug(f"Updating address for site {site_id}")

        # Basic address validation if requested
        if validate_address and len(address.strip()) < 10:
            raise SuperOpsValidationError("Address appears to be too short")

        return await self.update(site_id, {"address": address})

    async def bulk_update_timezone(self, site_ids: List[str], timezone: str) -> List[Site]:
        """Update timezone for multiple sites.

        Args:
            site_ids: List of site IDs
            timezone: New timezone for all sites

        Returns:
            List of updated site instances

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If any API request fails
        """
        if not site_ids:
            raise SuperOpsValidationError("Site IDs list cannot be empty")
        if not isinstance(site_ids, list):
            raise SuperOpsValidationError("Site IDs must be a list")
        if not timezone or not isinstance(timezone, str):
            raise SuperOpsValidationError("Timezone must be a non-empty string")

        self.logger.debug(f"Bulk updating timezone for {len(site_ids)} sites to {timezone}")

        updated_sites = []
        for site_id in site_ids:
            try:
                updated_site = await self.set_timezone(site_id, timezone)
                updated_sites.append(updated_site)
            except Exception as e:
                self.logger.error(f"Failed to update site {site_id}: {e}")
                # Continue with other sites

        self.logger.info(f"Successfully updated {len(updated_sites)} out of {len(site_ids)} sites")
        return updated_sites

    async def get_site_statistics(self, site_id: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a site.

        Args:
            site_id: The site ID

        Returns:
            Dictionary containing site statistics

        Raises:
            SuperOpsValidationError: If site_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not site_id or not isinstance(site_id, str):
            raise SuperOpsValidationError(f"Invalid site ID: {site_id}")

        self.logger.debug(f"Getting statistics for site: {site_id}")

        query = """
            query GetSiteStatistics($siteId: ID!) {
                site(id: $siteId) {
                    id
                    name
                    assetCount
                    activeAssetCount
                    inactiveAssetCount
                    ticketCount
                    openTicketCount
                    closedTicketCount
                    contactCount
                    lastActivityAt
                    statistics {
                        totalValue
                        avgTicketResolutionTime
                        criticalAssetsCount
                        overdueTicketsCount
                    }
                }
            }
        """

        variables = {"siteId": site_id}

        response = await self.client.execute_query(query, variables)

        if not response.get("data") or not response["data"].get("site"):
            return {}

        site_data = response["data"]["site"]

        # Structure the statistics nicely
        return {
            "site_id": site_data.get("id"),
            "site_name": site_data.get("name"),
            "assets": {
                "total": site_data.get("assetCount", 0),
                "active": site_data.get("activeAssetCount", 0),
                "inactive": site_data.get("inactiveAssetCount", 0),
                "critical": site_data.get("statistics", {}).get("criticalAssetsCount", 0),
            },
            "tickets": {
                "total": site_data.get("ticketCount", 0),
                "open": site_data.get("openTicketCount", 0),
                "closed": site_data.get("closedTicketCount", 0),
                "overdue": site_data.get("statistics", {}).get("overdueTicketsCount", 0),
            },
            "contacts": {
                "total": site_data.get("contactCount", 0),
            },
            "metrics": {
                "total_value": site_data.get("statistics", {}).get("totalValue", 0),
                "avg_ticket_resolution_time": site_data.get("statistics", {}).get(
                    "avgTicketResolutionTime"
                ),
                "last_activity_at": site_data.get("lastActivityAt"),
            },
        }

    async def get_timezones(self) -> List[str]:
        """Get list of unique timezones used by sites.

        Returns:
            List of timezone strings

        Raises:
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Getting unique site timezones")

        query = """
            query GetSiteTimezones {
                siteTimezones {
                    timezone
                    count
                }
            }
        """

        response = await self.client.execute_query(query, {})

        if not response.get("data"):
            return []

        timezones_data = response["data"].get("siteTimezones", [])
        return [item["timezone"] for item in timezones_data]

    # Protected methods for GraphQL query building

    def _build_get_query(self, **kwargs) -> str:
        """Build GraphQL query for getting a single site."""
        include_assets = kwargs.get("include_assets", False)
        include_inactive_assets = kwargs.get("include_inactive_assets", False)
        include_contacts = kwargs.get("include_contacts", False)

        fields = [
            "id",
            "clientId",
            "name",
            "address",
            "description",
            "timezone",
            "notes",
            "createdAt",
            "updatedAt",
        ]

        if include_assets:
            asset_status_filter = "" if include_inactive_assets else "status: ACTIVE"
            fields.append(
                f"""
                assets({asset_status_filter}) {{
                    id
                    name
                    assetType
                    manufacturer
                    model
                    status
                    location
                    createdAt
                    updatedAt
                }}
            """
            )

        if include_contacts:
            fields.append(
                """
                contacts {
                    id
                    firstName
                    lastName
                    email
                    phone
                    title
                    isPrimary
                    createdAt
                    updatedAt
                }
            """
            )

        field_str = "\n        ".join(fields)

        return f"""
            query GetSite($id: ID!) {{
                site(id: $id) {{
                    {field_str}
                }}
            }}
        """

    def _build_list_query(self, **kwargs) -> str:
        """Build GraphQL query for listing sites."""
        return """
            query ListSites(
                $page: Int!
                $pageSize: Int!
                $filters: SiteFilter
                $sortBy: String
                $sortOrder: SortOrder
            ) {
                sites(
                    page: $page
                    pageSize: $pageSize
                    filters: $filters
                    sortBy: $sortBy
                    sortOrder: $sortOrder
                ) {
                    items {
                        id
                        clientId
                        name
                        address
                        description
                        timezone
                        notes
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
        """Build GraphQL mutation for creating a site."""
        return """
            mutation CreateSite($input: CreateSiteInput!) {
                createSite(input: $input) {
                    id
                    clientId
                    name
                    address
                    description
                    timezone
                    notes
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_update_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for updating a site."""
        return """
            mutation UpdateSite($id: ID!, $input: UpdateSiteInput!) {
                updateSite(id: $id, input: $input) {
                    id
                    clientId
                    name
                    address
                    description
                    timezone
                    notes
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_delete_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for deleting a site."""
        return """
            mutation DeleteSite($id: ID!) {
                deleteSite(id: $id) {
                    success
                    message
                }
            }
        """

    def _build_search_query(self, **kwargs) -> str:
        """Build GraphQL query for searching sites."""
        return """
            query SearchSites(
                $query: String!
                $page: Int!
                $pageSize: Int!
            ) {
                searchSites(
                    query: $query
                    page: $page
                    pageSize: $pageSize
                ) {
                    items {
                        id
                        clientId
                        name
                        address
                        description
                        timezone
                        notes
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
        """Validate data for site creation."""
        validated = data.copy()

        # Required fields
        if not validated.get("name"):
            raise SuperOpsValidationError("Site name is required")
        if not validated.get("client_id"):
            raise SuperOpsValidationError("Client ID is required")

        # Validate timezone format (basic check)
        timezone = validated.get("timezone")
        if timezone and "/" not in timezone:
            raise SuperOpsValidationError(
                "Timezone should be in format 'Region/City' (e.g., 'America/New_York')"
            )

        return validated

    def _validate_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data for site updates."""
        validated = data.copy()

        # Validate timezone format if provided (basic check)
        timezone = validated.get("timezone")
        if timezone and "/" not in timezone:
            raise SuperOpsValidationError(
                "Timezone should be in format 'Region/City' (e.g., 'America/New_York')"
            )

        return validated
