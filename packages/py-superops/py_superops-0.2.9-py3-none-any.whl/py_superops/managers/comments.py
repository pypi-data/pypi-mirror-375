# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Comment manager for SuperOps API operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

from ..exceptions import SuperOpsValidationError
from ..graphql.types import Comment, CommentType

if TYPE_CHECKING:
    from ..client import SuperOpsClient
from .base import ResourceManager


class CommentsManager(ResourceManager[Comment]):
    """Manager for comment operations.

    Provides high-level methods for managing SuperOps comments including
    CRUD operations, entity-specific comments, threaded conversations,
    time logging, and comment-specific features.
    """

    def __init__(self, client: "SuperOpsClient") -> None:
        """Initialize the comments manager.

        Args:
            client: SuperOps client instance
        """
        super().__init__(client, Comment, "comment")

    # Basic CRUD operations (inherited from ResourceManager)
    # get, list, create, update, delete, search

    # Entity-specific comment operations
    async def get_comments_for_entity(
        self,
        entity_type: str,
        entity_id: str,
        page: int = 1,
        page_size: int = 50,
        include_replies: bool = True,
        include_internal: bool = True,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get comments for a specific entity (ticket, task, project, etc.).

        Args:
            entity_type: Type of entity ('ticket', 'task', 'project', etc.)
            entity_id: ID of the entity
            page: Page number (1-based)
            page_size: Number of items per page
            include_replies: Whether to include reply comments
            include_internal: Whether to include internal comments
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Comment]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not entity_type or not isinstance(entity_type, str):
            raise SuperOpsValidationError("Entity type must be a non-empty string")
        if not entity_id or not isinstance(entity_id, str):
            raise SuperOpsValidationError("Entity ID must be a non-empty string")

        self.logger.debug(f"Getting comments for {entity_type} {entity_id}")

        filters = {
            "entity_type": entity_type,
            "entity_id": entity_id,
        }

        if not include_replies:
            filters["parent_comment_id__isnull"] = True

        if not include_internal:
            filters["is_internal"] = False

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
        )

    async def add_comment_to_entity(
        self,
        entity_type: str,
        entity_id: str,
        content: str,
        comment_type: CommentType = CommentType.GENERAL,
        is_internal: bool = False,
        time_logged: Optional[float] = None,
    ) -> Comment:
        """Add a comment to a specific entity.

        Args:
            entity_type: Type of entity ('ticket', 'task', 'project', etc.)
            entity_id: ID of the entity
            content: Comment content
            comment_type: Type of comment
            is_internal: Whether the comment is internal
            time_logged: Optional time logged with comment (hours)

        Returns:
            Created comment instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not entity_type or not isinstance(entity_type, str):
            raise SuperOpsValidationError("Entity type must be a non-empty string")
        if not entity_id or not isinstance(entity_id, str):
            raise SuperOpsValidationError("Entity ID must be a non-empty string")
        if not content or not isinstance(content, str):
            raise SuperOpsValidationError("Content must be a non-empty string")

        self.logger.debug(f"Adding comment to {entity_type} {entity_id}")

        comment_data = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "content": content,
            "comment_type": (
                comment_type.value if isinstance(comment_type, CommentType) else comment_type
            ),
            "is_internal": is_internal,
        }

        if time_logged is not None:
            if not isinstance(time_logged, (int, float)) or time_logged < 0:
                raise SuperOpsValidationError("Time logged must be a non-negative number")
            comment_data["time_logged"] = float(time_logged)

        return await self.create(comment_data)

    # Reply operations
    async def get_comment_replies(
        self,
        parent_comment_id: str,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get replies to a specific comment.

        Args:
            parent_comment_id: ID of the parent comment
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Comment]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not parent_comment_id or not isinstance(parent_comment_id, str):
            raise SuperOpsValidationError("Parent comment ID must be a non-empty string")

        self.logger.debug(f"Getting replies for comment {parent_comment_id}")

        filters = {"parent_comment_id": parent_comment_id}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
        )

    async def reply_to_comment(
        self,
        parent_comment_id: str,
        content: str,
        is_internal: bool = False,
        time_logged: Optional[float] = None,
    ) -> Comment:
        """Reply to an existing comment.

        Args:
            parent_comment_id: ID of the parent comment
            content: Reply content
            is_internal: Whether the reply is internal
            time_logged: Optional time logged with reply (hours)

        Returns:
            Created reply comment instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not parent_comment_id or not isinstance(parent_comment_id, str):
            raise SuperOpsValidationError("Parent comment ID must be a non-empty string")
        if not content or not isinstance(content, str):
            raise SuperOpsValidationError("Content must be a non-empty string")

        # First get the parent comment to get entity information
        parent_comment = await self.get(parent_comment_id)
        if not parent_comment:
            raise SuperOpsValidationError(f"Parent comment {parent_comment_id} not found")

        self.logger.debug(f"Replying to comment {parent_comment_id}")

        reply_data = {
            "entity_type": parent_comment.entity_type,
            "entity_id": parent_comment.entity_id,
            "content": content,
            "comment_type": CommentType.GENERAL.value,
            "is_internal": is_internal,
            "parent_comment_id": parent_comment_id,
        }

        if time_logged is not None:
            if not isinstance(time_logged, (int, float)) or time_logged < 0:
                raise SuperOpsValidationError("Time logged must be a non-negative number")
            reply_data["time_logged"] = float(time_logged)

        return await self.create(reply_data)

    # Comment type filtering operations
    async def get_by_comment_type(
        self,
        comment_type: CommentType,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get comments filtered by comment type.

        Args:
            comment_type: Comment type to filter by
            entity_type: Optional entity type filter
            entity_id: Optional entity ID filter
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Comment]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not isinstance(comment_type, CommentType):
            raise SuperOpsValidationError("Comment type must be a CommentType enum")

        self.logger.debug(f"Getting comments with type: {comment_type.value}")

        filters = {"comment_type": comment_type.value}

        if entity_type:
            filters["entity_type"] = entity_type
        if entity_id:
            filters["entity_id"] = entity_id

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
        )

    async def get_internal_comments(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get internal comments only.

        Args:
            entity_type: Optional entity type filter
            entity_id: Optional entity ID filter
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Comment]) and 'pagination' info
        """
        self.logger.debug("Getting internal comments")

        filters = {"is_internal": True}

        if entity_type:
            filters["entity_type"] = entity_type
        if entity_id:
            filters["entity_id"] = entity_id

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
        )

    async def get_public_comments(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get public (non-internal) comments only.

        Args:
            entity_type: Optional entity type filter
            entity_id: Optional entity ID filter
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Comment]) and 'pagination' info
        """
        self.logger.debug("Getting public comments")

        filters = {"is_internal": False}

        if entity_type:
            filters["entity_type"] = entity_type
        if entity_id:
            filters["entity_id"] = entity_id

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
        )

    # Time logging operations
    async def get_comments_with_time(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get comments that have time logged.

        Args:
            entity_type: Optional entity type filter
            entity_id: Optional entity ID filter
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Comment]) and 'pagination' info
        """
        self.logger.debug("Getting comments with time logged")

        filters = {"time_logged__gt": 0}

        if entity_type:
            filters["entity_type"] = entity_type
        if entity_id:
            filters["entity_id"] = entity_id

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
        )

    # Search operations
    async def search_content(
        self,
        query: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        include_internal: bool = True,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        """Search comments by content.

        Args:
            query: Search query string
            entity_type: Optional entity type filter
            entity_id: Optional entity ID filter
            include_internal: Whether to include internal comments
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            Dictionary containing 'items' (List[Comment]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not query or not isinstance(query, str):
            raise SuperOpsValidationError("Query must be a non-empty string")

        self.logger.debug(f"Searching comments with query: {query}")

        filters = {"content__icontains": query}

        if entity_type:
            filters["entity_type"] = entity_type
        if entity_id:
            filters["entity_id"] = entity_id
        if not include_internal:
            filters["is_internal"] = False

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
        )

    async def get_by_author(
        self,
        author_id: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get comments by a specific author.

        Args:
            author_id: Author user ID
            entity_type: Optional entity type filter
            entity_id: Optional entity ID filter
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Comment]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not author_id or not isinstance(author_id, str):
            raise SuperOpsValidationError("Author ID must be a non-empty string")

        self.logger.debug(f"Getting comments by author: {author_id}")

        filters = {"author_id": author_id}

        if entity_type:
            filters["entity_type"] = entity_type
        if entity_id:
            filters["entity_id"] = entity_id

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
        )

    # Abstract method implementations for ResourceManager
    def _build_get_query(self, **kwargs) -> str:
        """Build GraphQL query for getting a single comment."""
        from ..graphql.fragments import create_query_with_fragments, get_comment_fields

        detail_level = kwargs.get("detail_level", "full")
        include_attachments = kwargs.get("include_attachments", True)

        fragment_names = get_comment_fields(detail_level, include_attachments)

        query = f"""
        query GetComment($id: ID!) {{
            comment(id: $id) {{
                ...{list(fragment_names)[0]}
            }}
        }}
        """

        return create_query_with_fragments(query, fragment_names)

    def _build_list_query(self, **kwargs) -> str:
        """Build GraphQL query for listing comments."""
        from ..graphql.fragments import create_query_with_fragments, get_comment_fields

        detail_level = kwargs.get("detail_level", "core")
        include_attachments = kwargs.get("include_attachments", False)

        fragment_names = get_comment_fields(detail_level, include_attachments)
        fragment_names.add("PaginationInfo")

        query = f"""
        query ListComments(
            $page: Int
            $pageSize: Int
            $filters: CommentFilter
            $sortBy: String
            $sortOrder: SortDirection
        ) {{
            comments(
                page: $page
                pageSize: $pageSize
                filter: $filters
                sortBy: $sortBy
                sortDirection: $sortOrder
            ) {{
                items {{
                    ...{list(fragment_names)[0]}
                }}
                pagination {{
                    ...PaginationInfo
                }}
            }}
        }}
        """

        return create_query_with_fragments(query, fragment_names)

    def _build_create_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for creating a comment."""
        from ..graphql.fragments import create_query_with_fragments, get_comment_fields

        detail_level = kwargs.get("detail_level", "full")
        fragment_names = get_comment_fields(detail_level)

        mutation = f"""
        mutation CreateComment($input: CommentInput!) {{
            createComment(input: $input) {{
                ...{list(fragment_names)[0]}
            }}
        }}
        """

        return create_query_with_fragments(mutation, fragment_names)

    def _build_update_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for updating a comment."""
        from ..graphql.fragments import create_query_with_fragments, get_comment_fields

        detail_level = kwargs.get("detail_level", "full")
        fragment_names = get_comment_fields(detail_level)

        mutation = f"""
        mutation UpdateComment($id: ID!, $input: CommentInput!) {{
            updateComment(id: $id, input: $input) {{
                ...{list(fragment_names)[0]}
            }}
        }}
        """

        return create_query_with_fragments(mutation, fragment_names)

    def _build_delete_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for deleting a comment."""
        return """
        mutation DeleteComment($id: ID!) {
            deleteComment(id: $id) {
                success
                message
            }
        }
        """

    def _build_search_query(self, **kwargs) -> str:
        """Build GraphQL query for searching comments."""
        from ..graphql.fragments import create_query_with_fragments, get_comment_fields

        detail_level = kwargs.get("detail_level", "core")
        fragment_names = get_comment_fields(detail_level)
        fragment_names.add("PaginationInfo")

        query = f"""
        query SearchComments(
            $query: String!
            $page: Int
            $pageSize: Int
        ) {{
            searchComments(
                query: $query
                page: $page
                pageSize: $pageSize
            ) {{
                items {{
                    ...{list(fragment_names)[0]}
                }}
                pagination {{
                    ...PaginationInfo
                }}
            }}
        }}
        """

        return create_query_with_fragments(query, fragment_names)
