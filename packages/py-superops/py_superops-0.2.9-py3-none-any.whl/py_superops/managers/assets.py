# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Asset manager for SuperOps API operations."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from ..exceptions import SuperOpsValidationError
from ..graphql.types import Asset, AssetStatus
from .base import ResourceManager


class AssetManager(ResourceManager[Asset]):
    """Manager for asset operations.

    Provides high-level methods for managing SuperOps assets including
    CRUD operations, asset tracking, warranty management, and asset-specific workflows.
    """

    def __init__(self, client: "SuperOpsClient"):
        """Initialize the asset manager.

        Args:
            client: SuperOps client instance
        """
        super().__init__(client, Asset, "asset")

    async def get_by_client(
        self,
        client_id: str,
        page: int = 1,
        page_size: int = 50,
        status_filter: Optional[AssetStatus] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get assets for a specific client.

        Args:
            client_id: The client ID
            page: Page number (1-based)
            page_size: Number of items per page
            status_filter: Optional status filter
            sort_by: Field to sort by (default: name)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Asset]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not client_id or not isinstance(client_id, str):
            raise SuperOpsValidationError("Client ID must be a non-empty string")

        self.logger.debug(f"Getting assets for client: {client_id}")

        filters = {"client_id": client_id}
        if status_filter:
            filters["status"] = status_filter.value

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
        )

    async def get_by_site(
        self,
        site_id: str,
        page: int = 1,
        page_size: int = 50,
        status_filter: Optional[AssetStatus] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get assets for a specific site.

        Args:
            site_id: The site ID
            page: Page number (1-based)
            page_size: Number of items per page
            status_filter: Optional status filter
            sort_by: Field to sort by (default: name)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Asset]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not site_id or not isinstance(site_id, str):
            raise SuperOpsValidationError("Site ID must be a non-empty string")

        self.logger.debug(f"Getting assets for site: {site_id}")

        filters = {"site_id": site_id}
        if status_filter:
            filters["status"] = status_filter.value

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
        )

    async def get_by_type(
        self,
        asset_type: str,
        page: int = 1,
        page_size: int = 50,
        status_filter: Optional[AssetStatus] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get assets by type.

        Args:
            asset_type: Asset type to filter by
            page: Page number (1-based)
            page_size: Number of items per page
            status_filter: Optional status filter
            sort_by: Field to sort by (default: name)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Asset]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not asset_type or not isinstance(asset_type, str):
            raise SuperOpsValidationError("Asset type must be a non-empty string")

        self.logger.debug(f"Getting assets of type: {asset_type}")

        filters = {"asset_type": asset_type}
        if status_filter:
            filters["status"] = status_filter.value

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
        )

    async def get_by_manufacturer(
        self,
        manufacturer: str,
        page: int = 1,
        page_size: int = 50,
        status_filter: Optional[AssetStatus] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get assets by manufacturer.

        Args:
            manufacturer: Manufacturer to filter by
            page: Page number (1-based)
            page_size: Number of items per page
            status_filter: Optional status filter
            sort_by: Field to sort by (default: name)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Asset]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not manufacturer or not isinstance(manufacturer, str):
            raise SuperOpsValidationError("Manufacturer must be a non-empty string")

        self.logger.debug(f"Getting assets by manufacturer: {manufacturer}")

        filters = {"manufacturer": manufacturer}
        if status_filter:
            filters["status"] = status_filter.value

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
        )

    async def get_by_serial_number(self, serial_number: str) -> Optional[Asset]:
        """Get an asset by serial number.

        Args:
            serial_number: Serial number to search for

        Returns:
            Asset instance or None if not found

        Raises:
            SuperOpsValidationError: If serial_number is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not serial_number or not isinstance(serial_number, str):
            raise SuperOpsValidationError("Serial number must be a non-empty string")

        self.logger.debug(f"Getting asset by serial number: {serial_number}")

        # Use search with exact serial number match
        results = await self.search(f'serial_number:"{serial_number}"', page_size=1)

        # Return first exact match if any
        for asset in results["items"]:
            if asset.serial_number == serial_number:
                return asset

        return None

    async def get_active_assets(
        self,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get all active assets.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: name)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Asset]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug(f"Getting active assets - page: {page}, size: {page_size}")

        filters = {"status": AssetStatus.ACTIVE.value}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
        )

    async def get_under_warranty(
        self,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get assets that are currently under warranty.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: warranty_expiry)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Asset]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Getting assets under warranty")

        # Filter by warranty expiry after current date
        today = datetime.utcnow().date()
        filters = {"warranty_expiry__gt": today.isoformat()}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "warranty_expiry",
            sort_order=sort_order,
        )

    async def get_warranty_expiring_soon(
        self,
        days_threshold: int = 30,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get assets with warranties expiring soon.

        Args:
            days_threshold: Number of days threshold for "soon"
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: warranty_expiry)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Asset]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if days_threshold <= 0:
            raise SuperOpsValidationError("Days threshold must be positive")

        self.logger.debug(f"Getting assets with warranty expiring within {days_threshold} days")

        # Calculate date range
        today = datetime.utcnow().date()
        threshold_date = today + timedelta(days=days_threshold)

        filters = {
            "warranty_expiry__gt": today.isoformat(),
            "warranty_expiry__lte": threshold_date.isoformat(),
        }

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "warranty_expiry",
            sort_order=sort_order,
        )

    async def get_expired_warranty(
        self,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get assets with expired warranties.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: warranty_expiry)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Asset]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Getting assets with expired warranties")

        # Filter by warranty expiry before current date
        today = datetime.utcnow().date()
        filters = {"warranty_expiry__lt": today.isoformat()}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "warranty_expiry",
            sort_order=sort_order,
        )

    async def activate_asset(self, asset_id: str) -> Asset:
        """Activate an asset.

        Args:
            asset_id: The asset ID

        Returns:
            Updated asset instance

        Raises:
            SuperOpsValidationError: If asset_id is invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If asset doesn't exist
        """
        if not asset_id or not isinstance(asset_id, str):
            raise SuperOpsValidationError(f"Invalid asset ID: {asset_id}")

        self.logger.debug(f"Activating asset: {asset_id}")

        return await self.update(asset_id, {"status": AssetStatus.ACTIVE.value})

    async def deactivate_asset(self, asset_id: str) -> Asset:
        """Deactivate an asset.

        Args:
            asset_id: The asset ID

        Returns:
            Updated asset instance

        Raises:
            SuperOpsValidationError: If asset_id is invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If asset doesn't exist
        """
        if not asset_id or not isinstance(asset_id, str):
            raise SuperOpsValidationError(f"Invalid asset ID: {asset_id}")

        self.logger.debug(f"Deactivating asset: {asset_id}")

        return await self.update(asset_id, {"status": AssetStatus.INACTIVE.value})

    async def retire_asset(self, asset_id: str) -> Asset:
        """Retire an asset.

        Args:
            asset_id: The asset ID

        Returns:
            Updated asset instance

        Raises:
            SuperOpsValidationError: If asset_id is invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If asset doesn't exist
        """
        if not asset_id or not isinstance(asset_id, str):
            raise SuperOpsValidationError(f"Invalid asset ID: {asset_id}")

        self.logger.debug(f"Retiring asset: {asset_id}")

        return await self.update(asset_id, {"status": AssetStatus.RETIRED.value})

    async def set_maintenance_mode(self, asset_id: str) -> Asset:
        """Set an asset to maintenance mode.

        Args:
            asset_id: The asset ID

        Returns:
            Updated asset instance

        Raises:
            SuperOpsValidationError: If asset_id is invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If asset doesn't exist
        """
        if not asset_id or not isinstance(asset_id, str):
            raise SuperOpsValidationError(f"Invalid asset ID: {asset_id}")

        self.logger.debug(f"Setting asset to maintenance mode: {asset_id}")

        return await self.update(asset_id, {"status": AssetStatus.UNDER_MAINTENANCE.value})

    async def update_warranty_expiry(self, asset_id: str, warranty_expiry: date) -> Asset:
        """Update asset warranty expiry date.

        Args:
            asset_id: The asset ID
            warranty_expiry: New warranty expiry date

        Returns:
            Updated asset instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not asset_id or not isinstance(asset_id, str):
            raise SuperOpsValidationError(f"Invalid asset ID: {asset_id}")
        if not isinstance(warranty_expiry, date):
            raise SuperOpsValidationError("Warranty expiry must be a date object")

        self.logger.debug(f"Updating warranty expiry for asset {asset_id} to {warranty_expiry}")

        return await self.update(asset_id, {"warranty_expiry": warranty_expiry.isoformat()})

    async def move_to_site(
        self, asset_id: str, new_site_id: str, update_location: Optional[str] = None
    ) -> Asset:
        """Move an asset to a different site.

        Args:
            asset_id: The asset ID
            new_site_id: The new site ID
            update_location: Optional new location within the site

        Returns:
            Updated asset instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not asset_id or not isinstance(asset_id, str):
            raise SuperOpsValidationError(f"Invalid asset ID: {asset_id}")
        if not new_site_id or not isinstance(new_site_id, str):
            raise SuperOpsValidationError("New site ID must be a non-empty string")

        self.logger.debug(f"Moving asset {asset_id} to site {new_site_id}")

        update_data = {"site_id": new_site_id}
        if update_location:
            update_data["location"] = update_location

        return await self.update(asset_id, update_data)

    async def bulk_update_status(self, asset_ids: List[str], status: AssetStatus) -> List[Asset]:
        """Update status for multiple assets.

        Args:
            asset_ids: List of asset IDs
            status: New status for all assets

        Returns:
            List of updated asset instances

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If any API request fails
        """
        if not asset_ids:
            raise SuperOpsValidationError("Asset IDs list cannot be empty")
        if not isinstance(asset_ids, list):
            raise SuperOpsValidationError("Asset IDs must be a list")
        if not isinstance(status, AssetStatus):
            raise SuperOpsValidationError("Status must be an AssetStatus enum")

        self.logger.debug(f"Bulk updating status for {len(asset_ids)} assets to {status.value}")

        updated_assets = []
        for asset_id in asset_ids:
            try:
                updated_asset = await self.update(asset_id, {"status": status.value})
                updated_assets.append(updated_asset)
            except Exception as e:
                self.logger.error(f"Failed to update asset {asset_id}: {e}")
                # Continue with other assets

        self.logger.info(
            f"Successfully updated {len(updated_assets)} out of {len(asset_ids)} assets"
        )
        return updated_assets

    async def get_asset_types(self) -> List[str]:
        """Get list of unique asset types.

        Returns:
            List of asset type strings

        Raises:
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Getting unique asset types")

        query = """
            query GetAssetTypes {
                assetTypes {
                    name
                    count
                }
            }
        """

        response = await self.client.execute_query(query, {})

        if not response.get("data"):
            return []

        asset_types_data = response["data"].get("assetTypes", [])
        return [item["name"] for item in asset_types_data]

    async def get_manufacturers(self) -> List[str]:
        """Get list of unique manufacturers.

        Returns:
            List of manufacturer strings

        Raises:
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Getting unique manufacturers")

        query = """
            query GetManufacturers {
                manufacturers {
                    name
                    count
                }
            }
        """

        response = await self.client.execute_query(query, {})

        if not response.get("data"):
            return []

        manufacturers_data = response["data"].get("manufacturers", [])
        return [item["name"] for item in manufacturers_data]

    # Protected methods for GraphQL query building

    def _build_get_query(self, **kwargs) -> str:
        """Build GraphQL query for getting a single asset."""
        return """
            query GetAsset($id: ID!) {
                asset(id: $id) {
                    id
                    clientId
                    name
                    siteId
                    assetType
                    manufacturer
                    model
                    serialNumber
                    status
                    purchaseDate
                    warrantyExpiry
                    location
                    notes
                    customFields
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_list_query(self, **kwargs) -> str:
        """Build GraphQL query for listing assets."""
        return """
            query ListAssets(
                $page: Int!
                $pageSize: Int!
                $filters: AssetFilter
                $sortBy: String
                $sortOrder: SortOrder
            ) {
                assets(
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
                        siteId
                        assetType
                        manufacturer
                        model
                        serialNumber
                        status
                        purchaseDate
                        warrantyExpiry
                        location
                        notes
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
        """Build GraphQL mutation for creating an asset."""
        return """
            mutation CreateAsset($input: CreateAssetInput!) {
                createAsset(input: $input) {
                    id
                    clientId
                    name
                    siteId
                    assetType
                    manufacturer
                    model
                    serialNumber
                    status
                    purchaseDate
                    warrantyExpiry
                    location
                    notes
                    customFields
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_update_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for updating an asset."""
        return """
            mutation UpdateAsset($id: ID!, $input: UpdateAssetInput!) {
                updateAsset(id: $id, input: $input) {
                    id
                    clientId
                    name
                    siteId
                    assetType
                    manufacturer
                    model
                    serialNumber
                    status
                    purchaseDate
                    warrantyExpiry
                    location
                    notes
                    customFields
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_delete_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for deleting an asset."""
        return """
            mutation DeleteAsset($id: ID!) {
                deleteAsset(id: $id) {
                    success
                    message
                }
            }
        """

    def _build_search_query(self, **kwargs) -> str:
        """Build GraphQL query for searching assets."""
        return """
            query SearchAssets(
                $query: String!
                $page: Int!
                $pageSize: Int!
            ) {
                searchAssets(
                    query: $query
                    page: $page
                    pageSize: $pageSize
                ) {
                    items {
                        id
                        clientId
                        name
                        siteId
                        assetType
                        manufacturer
                        model
                        serialNumber
                        status
                        purchaseDate
                        warrantyExpiry
                        location
                        notes
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
        """Validate data for asset creation."""
        validated = data.copy()

        # Required fields
        if not validated.get("name"):
            raise SuperOpsValidationError("Asset name is required")
        if not validated.get("client_id"):
            raise SuperOpsValidationError("Client ID is required")

        # Validate status if provided
        status = validated.get("status")
        if status and status not in [s.value for s in AssetStatus]:
            raise SuperOpsValidationError(f"Invalid asset status: {status}")

        # Validate date formats
        for date_field in ["purchase_date", "warranty_expiry"]:
            date_value = validated.get(date_field)
            if date_value and isinstance(date_value, str):
                try:
                    datetime.fromisoformat(date_value.replace("Z", "+00:00"))
                except ValueError:
                    raise SuperOpsValidationError(f"Invalid {date_field} format. Use ISO format.")

        return validated

    def _validate_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data for asset updates."""
        validated = data.copy()

        # Validate status if provided
        status = validated.get("status")
        if status and status not in [s.value for s in AssetStatus]:
            raise SuperOpsValidationError(f"Invalid asset status: {status}")

        # Validate date formats
        for date_field in ["purchase_date", "warranty_expiry"]:
            date_value = validated.get(date_field)
            if date_value and isinstance(date_value, str):
                try:
                    datetime.fromisoformat(date_value.replace("Z", "+00:00"))
                except ValueError:
                    raise SuperOpsValidationError(f"Invalid {date_field} format. Use ISO format.")

        return validated
