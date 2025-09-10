# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Base manager class providing common functionality for all resource managers."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from ..exceptions import SuperOpsAPIError, SuperOpsResourceNotFoundError, SuperOpsValidationError
from ..graphql.types import BaseModel, GraphQLResponse, PaginationInfo

# Type variable for resource types
T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)


class ResourceManager(Generic[T], ABC):
    """Base class for all SuperOps resource managers.

    Provides common CRUD operations, error handling, and utilities
    for managing SuperOps API resources.

    Args:
        client: SuperOps client instance
        resource_type: The model class this manager handles
        resource_name: GraphQL resource name (e.g., 'client', 'ticket')
    """

    def __init__(
        self,
        client: "SuperOpsClient",  # Forward reference to avoid circular imports
        resource_type: Type[T],
        resource_name: str,
    ):
        """Initialize the resource manager.

        Args:
            client: SuperOps client instance
            resource_type: The model class this manager handles
            resource_name: GraphQL resource name
        """
        self.client = client
        self.resource_type = resource_type
        self.resource_name = resource_name
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def get(self, resource_id: str, **kwargs) -> Optional[T]:
        """Get a single resource by ID.

        Args:
            resource_id: The resource ID
            **kwargs: Additional query parameters

        Returns:
            The resource instance or None if not found

        Raises:
            SuperOpsAPIError: If the API request fails
            SuperOpsValidationError: If the resource_id is invalid
        """
        if not resource_id or not isinstance(resource_id, str):
            raise SuperOpsValidationError(f"Invalid resource ID: {resource_id}")

        self.logger.debug(f"Getting {self.resource_name} with ID: {resource_id}")

        try:
            query = self._build_get_query(**kwargs)
            variables = {"id": resource_id, **self._build_get_variables(**kwargs)}

            response = await self.client.execute_query(query, variables)

            if not response.get("data"):
                return None

            resource_data = response["data"].get(self.resource_name)
            if not resource_data:
                return None

            return self._create_instance(resource_data)

        except SuperOpsAPIError:
            raise
        except Exception as e:
            self.logger.error(f"Error getting {self.resource_name} {resource_id}: {e}")
            raise SuperOpsAPIError(f"Failed to get {self.resource_name}", 0, {}) from e

    async def list(
        self,
        page: int = 1,
        page_size: int = 50,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        **kwargs,
    ) -> Dict[str, Union[List[T], PaginationInfo]]:
        """List resources with pagination and filtering.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            filters: Filter conditions
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            **kwargs: Additional query parameters

        Returns:
            Dictionary containing 'items' (List[T]) and 'pagination' (PaginationInfo)

        Raises:
            SuperOpsAPIError: If the API request fails
            SuperOpsValidationError: If parameters are invalid
        """
        if page < 1:
            raise SuperOpsValidationError("Page number must be >= 1")
        if page_size < 1 or page_size > 1000:
            raise SuperOpsValidationError("Page size must be between 1 and 1000")
        if sort_order not in ("asc", "desc"):
            raise SuperOpsValidationError("Sort order must be 'asc' or 'desc'")

        self.logger.debug(f"Listing {self.resource_name}s - page: {page}, size: {page_size}")

        try:
            query = self._build_list_query(**kwargs)
            variables = {
                "page": page,
                "pageSize": page_size,
                "filters": filters or {},
                "sortBy": sort_by,
                "sortOrder": sort_order.upper(),
                **self._build_list_variables(**kwargs),
            }

            response = await self.client.execute_query(query, variables)

            if not response.get("data"):
                return {"items": [], "pagination": self._empty_pagination()}

            resource_data = response["data"].get(f"{self.resource_name}s")
            if not resource_data:
                return {"items": [], "pagination": self._empty_pagination()}

            items = [self._create_instance(item) for item in resource_data.get("items", [])]

            pagination = resource_data.get("pagination", self._empty_pagination())

            return {"items": items, "pagination": pagination}

        except SuperOpsAPIError:
            raise
        except Exception as e:
            self.logger.error(f"Error listing {self.resource_name}s: {e}")
            raise SuperOpsAPIError(f"Failed to list {self.resource_name}s", 0, {}) from e

    async def create(self, data: Dict[str, Any], **kwargs) -> T:
        """Create a new resource.

        Args:
            data: Resource data
            **kwargs: Additional parameters

        Returns:
            The created resource instance

        Raises:
            SuperOpsAPIError: If the API request fails
            SuperOpsValidationError: If the data is invalid
        """
        if not data:
            raise SuperOpsValidationError("Resource data cannot be empty")

        self.logger.debug(f"Creating new {self.resource_name}")

        try:
            # Validate data before sending
            validated_data = self._validate_create_data(data)

            mutation = self._build_create_mutation(**kwargs)
            variables = {"input": validated_data, **self._build_create_variables(**kwargs)}

            response = await self.client.execute_mutation(mutation, variables)

            if not response.get("data"):
                raise SuperOpsAPIError(
                    f"No data returned when creating {self.resource_name}", 500, response
                )

            resource_data = response["data"].get(f"create{self.resource_name.title()}")
            if not resource_data:
                raise SuperOpsAPIError(
                    f"No {self.resource_name} data in create response", 500, response
                )

            created_resource = self._create_instance(resource_data)
            self.logger.info(f"Created {self.resource_name} with ID: {created_resource.id}")

            return created_resource

        except SuperOpsAPIError:
            raise
        except Exception as e:
            self.logger.error(f"Error creating {self.resource_name}: {e}")
            raise SuperOpsAPIError(f"Failed to create {self.resource_name}", 0, {}) from e

    async def update(self, resource_id: str, data: Dict[str, Any], **kwargs) -> T:
        """Update an existing resource.

        Args:
            resource_id: The resource ID
            data: Updated data
            **kwargs: Additional parameters

        Returns:
            The updated resource instance

        Raises:
            SuperOpsAPIError: If the API request fails
            SuperOpsValidationError: If parameters are invalid
            SuperOpsResourceNotFoundError: If the resource doesn't exist
        """
        if not resource_id or not isinstance(resource_id, str):
            raise SuperOpsValidationError(f"Invalid resource ID: {resource_id}")
        if not data:
            raise SuperOpsValidationError("Update data cannot be empty")

        self.logger.debug(f"Updating {self.resource_name} with ID: {resource_id}")

        try:
            # Validate data before sending
            validated_data = self._validate_update_data(data)

            mutation = self._build_update_mutation(**kwargs)
            variables = {
                "id": resource_id,
                "input": validated_data,
                **self._build_update_variables(**kwargs),
            }

            response = await self.client.execute_mutation(mutation, variables)

            if not response.get("data"):
                raise SuperOpsAPIError(
                    f"No data returned when updating {self.resource_name}", 500, response
                )

            resource_data = response["data"].get(f"update{self.resource_name.title()}")
            if not resource_data:
                raise SuperOpsResourceNotFoundError(
                    f"{self.resource_name} not found: {resource_id}"
                )

            updated_resource = self._create_instance(resource_data)
            self.logger.info(f"Updated {self.resource_name} with ID: {resource_id}")

            return updated_resource

        except (SuperOpsAPIError, SuperOpsResourceNotFoundError):
            raise
        except Exception as e:
            self.logger.error(f"Error updating {self.resource_name} {resource_id}: {e}")
            raise SuperOpsAPIError(f"Failed to update {self.resource_name}", 0, {}) from e

    async def delete(self, resource_id: str, **kwargs) -> bool:
        """Delete a resource.

        Args:
            resource_id: The resource ID
            **kwargs: Additional parameters

        Returns:
            True if deletion was successful

        Raises:
            SuperOpsAPIError: If the API request fails
            SuperOpsValidationError: If the resource_id is invalid
            SuperOpsResourceNotFoundError: If the resource doesn't exist
        """
        if not resource_id or not isinstance(resource_id, str):
            raise SuperOpsValidationError(f"Invalid resource ID: {resource_id}")

        self.logger.debug(f"Deleting {self.resource_name} with ID: {resource_id}")

        try:
            mutation = self._build_delete_mutation(**kwargs)
            variables = {"id": resource_id, **self._build_delete_variables(**kwargs)}

            response = await self.client.execute_mutation(mutation, variables)

            if not response.get("data"):
                raise SuperOpsAPIError(
                    f"No data returned when deleting {self.resource_name}", 500, response
                )

            result = response["data"].get(f"delete{self.resource_name.title()}")
            if not result:
                raise SuperOpsResourceNotFoundError(
                    f"{self.resource_name} not found: {resource_id}"
                )

            success = result.get("success", False)
            if success:
                self.logger.info(f"Deleted {self.resource_name} with ID: {resource_id}")

            return success

        except (SuperOpsAPIError, SuperOpsResourceNotFoundError):
            raise
        except Exception as e:
            self.logger.error(f"Error deleting {self.resource_name} {resource_id}: {e}")
            raise SuperOpsAPIError(f"Failed to delete {self.resource_name}", 0, {}) from e

    async def search(
        self, query: str, page: int = 1, page_size: int = 50, **kwargs
    ) -> Dict[str, Union[List[T], PaginationInfo]]:
        """Search for resources using text query.

        Args:
            query: Search query string
            page: Page number (1-based)
            page_size: Number of items per page
            **kwargs: Additional search parameters

        Returns:
            Dictionary containing 'items' (List[T]) and 'pagination' (PaginationInfo)

        Raises:
            SuperOpsAPIError: If the API request fails
            SuperOpsValidationError: If parameters are invalid
        """
        if not query or not isinstance(query, str):
            raise SuperOpsValidationError("Search query must be a non-empty string")
        if page < 1:
            raise SuperOpsValidationError("Page number must be >= 1")
        if page_size < 1 or page_size > 1000:
            raise SuperOpsValidationError("Page size must be between 1 and 1000")

        self.logger.debug(f"Searching {self.resource_name}s with query: {query}")

        try:
            search_query = self._build_search_query(**kwargs)
            variables = {
                "query": query,
                "page": page,
                "pageSize": page_size,
                **self._build_search_variables(**kwargs),
            }

            response = await self.client.execute_query(search_query, variables)

            if not response.get("data"):
                return {"items": [], "pagination": self._empty_pagination()}

            search_data = response["data"].get(f"search{self.resource_name.title()}s")
            if not search_data:
                return {"items": [], "pagination": self._empty_pagination()}

            items = [self._create_instance(item) for item in search_data.get("items", [])]

            pagination = search_data.get("pagination", self._empty_pagination())

            return {"items": items, "pagination": pagination}

        except SuperOpsAPIError:
            raise
        except Exception as e:
            self.logger.error(f"Error searching {self.resource_name}s: {e}")
            raise SuperOpsAPIError(f"Failed to search {self.resource_name}s", 0, {}) from e

    # Protected helper methods

    def _create_instance(self, data: Dict[str, Any]) -> T:
        """Create a resource instance from API data.

        Args:
            data: Raw API data

        Returns:
            Resource instance
        """
        try:
            return self.resource_type.from_dict(data)
        except Exception as e:
            self.logger.error(f"Error creating {self.resource_type.__name__} instance: {e}")
            raise SuperOpsValidationError(f"Invalid {self.resource_name} data") from e

    def _empty_pagination(self) -> PaginationInfo:
        """Create empty pagination info."""
        return {
            "page": 1,
            "pageSize": 0,
            "total": 0,
            "hasNextPage": False,
            "hasPreviousPage": False,
        }

    def _validate_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data for create operations.

        Override in subclasses for specific validation.

        Args:
            data: Data to validate

        Returns:
            Validated data

        Raises:
            SuperOpsValidationError: If data is invalid
        """
        return data.copy()

    def _validate_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data for update operations.

        Override in subclasses for specific validation.

        Args:
            data: Data to validate

        Returns:
            Validated data

        Raises:
            SuperOpsValidationError: If data is invalid
        """
        return data.copy()

    # Abstract methods - must be implemented by subclasses

    @abstractmethod
    def _build_get_query(self, **kwargs) -> str:
        """Build GraphQL query for getting a single resource."""
        pass

    @abstractmethod
    def _build_list_query(self, **kwargs) -> str:
        """Build GraphQL query for listing resources."""
        pass

    @abstractmethod
    def _build_create_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for creating a resource."""
        pass

    @abstractmethod
    def _build_update_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for updating a resource."""
        pass

    @abstractmethod
    def _build_delete_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for deleting a resource."""
        pass

    @abstractmethod
    def _build_search_query(self, **kwargs) -> str:
        """Build GraphQL query for searching resources."""
        pass

    def _build_get_variables(self, **kwargs) -> Dict[str, Any]:
        """Build variables for get query. Override if needed."""
        return {}

    def _build_list_variables(self, **kwargs) -> Dict[str, Any]:
        """Build variables for list query. Override if needed."""
        return {}

    def _build_create_variables(self, **kwargs) -> Dict[str, Any]:
        """Build variables for create mutation. Override if needed."""
        return {}

    def _build_update_variables(self, **kwargs) -> Dict[str, Any]:
        """Build variables for update mutation. Override if needed."""
        return {}

    def _build_delete_variables(self, **kwargs) -> Dict[str, Any]:
        """Build variables for delete mutation. Override if needed."""
        return {}

    def _build_search_variables(self, **kwargs) -> Dict[str, Any]:
        """Build variables for search query. Override if needed."""
        return {}
