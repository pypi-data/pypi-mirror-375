# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Tests for CommentsManager class."""

from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest

from py_superops.exceptions import (
    SuperOpsAPIError,
    SuperOpsResourceNotFoundError,
    SuperOpsValidationError,
)
from py_superops.graphql.types import Comment, CommentType
from py_superops.managers import CommentsManager


class TestCommentsManager:
    """Test the CommentsManager class."""

    @pytest.fixture
    def mock_client(self) -> AsyncMock:
        """Create a mock SuperOps client."""
        client = AsyncMock()
        client.execute_query = AsyncMock()
        client.execute_mutation = AsyncMock()
        return client

    @pytest.fixture
    def comments_manager(self, mock_client: AsyncMock) -> CommentsManager:
        """Create a CommentsManager instance."""
        return CommentsManager(mock_client)

    @pytest.fixture
    def sample_comment_response(self) -> Dict[str, Any]:
        """Sample comment response data."""
        return {
            "data": {
                "comment": {
                    "id": "comment-123",
                    "entity_type": "ticket",
                    "entity_id": "ticket-456",
                    "author_id": "user-789",
                    "author_name": "John Doe",
                    "content": "This is a test comment",
                    "comment_type": "GENERAL",
                    "is_internal": False,
                    "time_logged": None,
                    "parent_comment_id": None,
                    "reply_count": 0,
                    "attachments": [],
                    "created_at": "2024-01-01T12:00:00Z",
                    "updated_at": "2024-01-01T12:00:00Z",
                }
            }
        }

    @pytest.fixture
    def sample_comments_list_response(self) -> Dict[str, Any]:
        """Sample comment list response data."""
        return {
            "data": {
                "comments": {
                    "items": [
                        {
                            "id": "comment-1",
                            "entity_type": "ticket",
                            "entity_id": "ticket-456",
                            "author_id": "user-789",
                            "author_name": "John Doe",
                            "content": "First comment",
                            "comment_type": "GENERAL",
                            "is_internal": False,
                            "time_logged": None,
                            "parent_comment_id": None,
                            "reply_count": 1,
                            "attachments": [],
                            "created_at": "2024-01-01T12:00:00Z",
                            "updated_at": "2024-01-01T12:00:00Z",
                        },
                        {
                            "id": "comment-2",
                            "entity_type": "ticket",
                            "entity_id": "ticket-456",
                            "author_id": "user-987",
                            "author_name": "Jane Smith",
                            "content": "Second comment",
                            "comment_type": "INTERNAL",
                            "is_internal": True,
                            "time_logged": 1.5,
                            "parent_comment_id": None,
                            "reply_count": 0,
                            "attachments": [],
                            "created_at": "2024-01-02T12:00:00Z",
                            "updated_at": "2024-01-02T12:00:00Z",
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
    def sample_reply_comment_response(self) -> Dict[str, Any]:
        """Sample reply comment response data."""
        return {
            "data": {
                "comment": {
                    "id": "comment-reply-123",
                    "entity_type": "ticket",
                    "entity_id": "ticket-456",
                    "author_id": "user-789",
                    "author_name": "John Doe",
                    "content": "This is a reply to the first comment",
                    "comment_type": "GENERAL",
                    "is_internal": False,
                    "time_logged": None,
                    "parent_comment_id": "comment-1",
                    "reply_count": 0,
                    "attachments": [],
                    "created_at": "2024-01-01T13:00:00Z",
                    "updated_at": "2024-01-01T13:00:00Z",
                }
            }
        }

    # Test initialization
    def test_initialization(self, mock_client, comments_manager) -> None:
        """Test CommentsManager initialization."""
        assert comments_manager.client is mock_client
        assert comments_manager.resource_type is Comment
        assert comments_manager.resource_name == "comment"

    # Test entity-specific comment operations
    @pytest.mark.asyncio
    async def test_get_comments_for_entity_success(
        self, comments_manager, sample_comments_list_response
    ) -> None:
        """Test successful retrieval of comments for an entity."""
        # Mock the list method
        with patch.object(comments_manager, "list", new=AsyncMock()) as mock_list:
            mock_list.return_value = sample_comments_list_response["data"]["comments"]

            result = await comments_manager.get_comments_for_entity(
                entity_type="ticket", entity_id="ticket-456"
            )

            # Verify the call
            mock_list.assert_called_once_with(
                page=1,
                page_size=50,
                filters={
                    "entity_type": "ticket",
                    "entity_id": "ticket-456",
                },
                sort_by="created_at",
                sort_order="desc",
            )

            # Verify result
            assert result["items"][0]["id"] == "comment-1"
            assert result["items"][1]["id"] == "comment-2"

    @pytest.mark.asyncio
    async def test_get_comments_for_entity_validation_errors(self, comments_manager) -> None:
        """Test validation errors in get_comments_for_entity."""
        with pytest.raises(SuperOpsValidationError, match="Entity type must be a non-empty string"):
            await comments_manager.get_comments_for_entity("", "ticket-456")

        with pytest.raises(SuperOpsValidationError, match="Entity type must be a non-empty string"):
            await comments_manager.get_comments_for_entity(None, "ticket-456")

        with pytest.raises(SuperOpsValidationError, match="Entity ID must be a non-empty string"):
            await comments_manager.get_comments_for_entity("ticket", "")

        with pytest.raises(SuperOpsValidationError, match="Entity ID must be a non-empty string"):
            await comments_manager.get_comments_for_entity("ticket", None)

    @pytest.mark.asyncio
    async def test_get_comments_for_entity_filters(self, comments_manager) -> None:
        """Test filtering options in get_comments_for_entity."""
        with patch.object(comments_manager, "list", new=AsyncMock()) as mock_list:
            mock_list.return_value = {"items": [], "pagination": {}}

            # Test exclude replies
            await comments_manager.get_comments_for_entity(
                entity_type="ticket", entity_id="ticket-456", include_replies=False
            )

            mock_list.assert_called_with(
                page=1,
                page_size=50,
                filters={
                    "entity_type": "ticket",
                    "entity_id": "ticket-456",
                    "parent_comment_id__isnull": True,
                },
                sort_by="created_at",
                sort_order="desc",
            )

            # Test exclude internal
            await comments_manager.get_comments_for_entity(
                entity_type="ticket", entity_id="ticket-456", include_internal=False
            )

            mock_list.assert_called_with(
                page=1,
                page_size=50,
                filters={
                    "entity_type": "ticket",
                    "entity_id": "ticket-456",
                    "is_internal": False,
                },
                sort_by="created_at",
                sort_order="desc",
            )

    @pytest.mark.asyncio
    async def test_add_comment_to_entity_success(
        self, comments_manager, sample_comment_response
    ) -> None:
        """Test successful adding of comment to entity."""
        with patch.object(comments_manager, "create", new=AsyncMock()) as mock_create:
            mock_create.return_value = Comment(**sample_comment_response["data"]["comment"])

            result = await comments_manager.add_comment_to_entity(
                entity_type="ticket", entity_id="ticket-456", content="Test comment"
            )

            # Verify the call
            mock_create.assert_called_once_with(
                {
                    "entity_type": "ticket",
                    "entity_id": "ticket-456",
                    "content": "Test comment",
                    "comment_type": "GENERAL",
                    "is_internal": False,
                }
            )

            # Verify result
            assert result.id == "comment-123"
            assert result.content == "This is a test comment"

    @pytest.mark.asyncio
    async def test_add_comment_to_entity_with_time_logged(
        self, comments_manager, sample_comment_response
    ) -> None:
        """Test adding comment with time logged."""
        with patch.object(comments_manager, "create", new=AsyncMock()) as mock_create:
            mock_create.return_value = Comment(**sample_comment_response["data"]["comment"])

            await comments_manager.add_comment_to_entity(
                entity_type="task",
                entity_id="task-123",
                content="Work completed",
                comment_type=CommentType.TIME_LOG,
                is_internal=True,
                time_logged=2.5,
            )

            # Verify the call
            mock_create.assert_called_once_with(
                {
                    "entity_type": "task",
                    "entity_id": "task-123",
                    "content": "Work completed",
                    "comment_type": "TIME_LOG",
                    "is_internal": True,
                    "time_logged": 2.5,
                }
            )

    @pytest.mark.asyncio
    async def test_add_comment_to_entity_validation_errors(self, comments_manager) -> None:
        """Test validation errors in add_comment_to_entity."""
        with pytest.raises(SuperOpsValidationError, match="Entity type must be a non-empty string"):
            await comments_manager.add_comment_to_entity("", "ticket-456", "Test")

        with pytest.raises(SuperOpsValidationError, match="Entity ID must be a non-empty string"):
            await comments_manager.add_comment_to_entity("ticket", "", "Test")

        with pytest.raises(SuperOpsValidationError, match="Content must be a non-empty string"):
            await comments_manager.add_comment_to_entity("ticket", "ticket-456", "")

        with pytest.raises(
            SuperOpsValidationError, match="Time logged must be a non-negative number"
        ):
            await comments_manager.add_comment_to_entity(
                "ticket", "ticket-456", "Test", time_logged=-1
            )

    # Test reply operations
    @pytest.mark.asyncio
    async def test_get_comment_replies_success(
        self, comments_manager, sample_comments_list_response
    ) -> None:
        """Test successful retrieval of comment replies."""
        with patch.object(comments_manager, "list", new=AsyncMock()) as mock_list:
            mock_list.return_value = sample_comments_list_response["data"]["comments"]

            result = await comments_manager.get_comment_replies("comment-1")

            # Verify the call
            mock_list.assert_called_once_with(
                page=1,
                page_size=50,
                filters={"parent_comment_id": "comment-1"},
                sort_by="created_at",
                sort_order="asc",
            )

            # Verify result
            assert len(result["items"]) == 2

    @pytest.mark.asyncio
    async def test_get_comment_replies_validation_error(self, comments_manager) -> None:
        """Test validation error in get_comment_replies."""
        with pytest.raises(
            SuperOpsValidationError, match="Parent comment ID must be a non-empty string"
        ):
            await comments_manager.get_comment_replies("")

    @pytest.mark.asyncio
    async def test_reply_to_comment_success(
        self, comments_manager, sample_comment_response, sample_reply_comment_response
    ) -> None:
        """Test successful reply to comment."""
        with patch.object(comments_manager, "get", new=AsyncMock()) as mock_get, patch.object(
            comments_manager, "create", new=AsyncMock()
        ) as mock_create:
            # Mock getting the parent comment
            parent_comment = Comment(**sample_comment_response["data"]["comment"])
            mock_get.return_value = parent_comment

            # Mock creating the reply
            reply_comment = Comment(**sample_reply_comment_response["data"]["comment"])
            mock_create.return_value = reply_comment

            result = await comments_manager.reply_to_comment(
                parent_comment_id="comment-1", content="This is a reply"
            )

            # Verify calls
            mock_get.assert_called_once_with("comment-1")
            mock_create.assert_called_once_with(
                {
                    "entity_type": "ticket",
                    "entity_id": "ticket-456",
                    "content": "This is a reply",
                    "comment_type": "GENERAL",
                    "is_internal": False,
                    "parent_comment_id": "comment-1",
                }
            )

            # Verify result
            assert result.id == "comment-reply-123"
            assert result.parent_comment_id == "comment-1"

    @pytest.mark.asyncio
    async def test_reply_to_comment_validation_errors(self, comments_manager) -> None:
        """Test validation errors in reply_to_comment."""
        with pytest.raises(
            SuperOpsValidationError, match="Parent comment ID must be a non-empty string"
        ):
            await comments_manager.reply_to_comment("", "Reply content")

        with pytest.raises(SuperOpsValidationError, match="Content must be a non-empty string"):
            await comments_manager.reply_to_comment("comment-1", "")

    @pytest.mark.asyncio
    async def test_reply_to_comment_parent_not_found(self, comments_manager) -> None:
        """Test reply to comment when parent comment not found."""
        with patch.object(comments_manager, "get", new=AsyncMock()) as mock_get:
            mock_get.return_value = None

            with pytest.raises(SuperOpsValidationError, match="Parent comment comment-1 not found"):
                await comments_manager.reply_to_comment("comment-1", "Reply content")

    # Test comment type filtering operations
    @pytest.mark.asyncio
    async def test_get_by_comment_type_success(
        self, comments_manager, sample_comments_list_response
    ) -> None:
        """Test successful filtering by comment type."""
        with patch.object(comments_manager, "list", new=AsyncMock()) as mock_list:
            mock_list.return_value = sample_comments_list_response["data"]["comments"]

            result = await comments_manager.get_by_comment_type(CommentType.INTERNAL)

            # Verify the call
            mock_list.assert_called_once_with(
                page=1,
                page_size=50,
                filters={"comment_type": "INTERNAL"},
                sort_by="created_at",
                sort_order="desc",
            )

            # Verify result
            assert len(result["items"]) == 2

    @pytest.mark.asyncio
    async def test_get_by_comment_type_with_entity_filters(self, comments_manager) -> None:
        """Test filtering by comment type with entity filters."""
        with patch.object(comments_manager, "list", new=AsyncMock()) as mock_list:
            mock_list.return_value = {"items": [], "pagination": {}}

            await comments_manager.get_by_comment_type(
                comment_type=CommentType.TIME_LOG, entity_type="task", entity_id="task-123"
            )

            # Verify the call
            mock_list.assert_called_once_with(
                page=1,
                page_size=50,
                filters={
                    "comment_type": "TIME_LOG",
                    "entity_type": "task",
                    "entity_id": "task-123",
                },
                sort_by="created_at",
                sort_order="desc",
            )

    @pytest.mark.asyncio
    async def test_get_by_comment_type_validation_error(self, comments_manager) -> None:
        """Test validation error in get_by_comment_type."""
        with pytest.raises(
            SuperOpsValidationError, match="Comment type must be a CommentType enum"
        ):
            await comments_manager.get_by_comment_type("INVALID_TYPE")

    @pytest.mark.asyncio
    async def test_get_internal_comments(self, comments_manager) -> None:
        """Test getting internal comments."""
        with patch.object(comments_manager, "list", new=AsyncMock()) as mock_list:
            mock_list.return_value = {"items": [], "pagination": {}}

            await comments_manager.get_internal_comments()

            # Verify the call
            mock_list.assert_called_once_with(
                page=1,
                page_size=50,
                filters={"is_internal": True},
                sort_by="created_at",
                sort_order="desc",
            )

    @pytest.mark.asyncio
    async def test_get_public_comments(self, comments_manager) -> None:
        """Test getting public comments."""
        with patch.object(comments_manager, "list", new=AsyncMock()) as mock_list:
            mock_list.return_value = {"items": [], "pagination": {}}

            await comments_manager.get_public_comments()

            # Verify the call
            mock_list.assert_called_once_with(
                page=1,
                page_size=50,
                filters={"is_internal": False},
                sort_by="created_at",
                sort_order="desc",
            )

    # Test time logging operations
    @pytest.mark.asyncio
    async def test_get_comments_with_time(self, comments_manager) -> None:
        """Test getting comments with time logged."""
        with patch.object(comments_manager, "list", new=AsyncMock()) as mock_list:
            mock_list.return_value = {"items": [], "pagination": {}}

            await comments_manager.get_comments_with_time()

            # Verify the call
            mock_list.assert_called_once_with(
                page=1,
                page_size=50,
                filters={"time_logged__gt": 0},
                sort_by="created_at",
                sort_order="desc",
            )

    # Test search operations
    @pytest.mark.asyncio
    async def test_search_content_success(
        self, comments_manager, sample_comments_list_response
    ) -> None:
        """Test successful content search."""
        with patch.object(comments_manager, "list", new=AsyncMock()) as mock_list:
            mock_list.return_value = sample_comments_list_response["data"]["comments"]

            result = await comments_manager.search_content("test query")

            # Verify the call
            mock_list.assert_called_once_with(
                page=1,
                page_size=50,
                filters={"content__icontains": "test query"},
            )

            # Verify result
            assert len(result["items"]) == 2

    @pytest.mark.asyncio
    async def test_search_content_with_filters(self, comments_manager) -> None:
        """Test content search with additional filters."""
        with patch.object(comments_manager, "list", new=AsyncMock()) as mock_list:
            mock_list.return_value = {"items": [], "pagination": {}}

            await comments_manager.search_content(
                query="search text",
                entity_type="ticket",
                entity_id="ticket-123",
                include_internal=False,
            )

            # Verify the call
            mock_list.assert_called_once_with(
                page=1,
                page_size=50,
                filters={
                    "content__icontains": "search text",
                    "entity_type": "ticket",
                    "entity_id": "ticket-123",
                    "is_internal": False,
                },
            )

    @pytest.mark.asyncio
    async def test_search_content_validation_error(self, comments_manager) -> None:
        """Test validation error in search_content."""
        with pytest.raises(SuperOpsValidationError, match="Query must be a non-empty string"):
            await comments_manager.search_content("")

    @pytest.mark.asyncio
    async def test_get_by_author_success(
        self, comments_manager, sample_comments_list_response
    ) -> None:
        """Test successful retrieval of comments by author."""
        with patch.object(comments_manager, "list", new=AsyncMock()) as mock_list:
            mock_list.return_value = sample_comments_list_response["data"]["comments"]

            result = await comments_manager.get_by_author("user-789")

            # Verify the call
            mock_list.assert_called_once_with(
                page=1,
                page_size=50,
                filters={"author_id": "user-789"},
                sort_by="created_at",
                sort_order="desc",
            )

            # Verify result
            assert len(result["items"]) == 2

    @pytest.mark.asyncio
    async def test_get_by_author_validation_error(self, comments_manager) -> None:
        """Test validation error in get_by_author."""
        with pytest.raises(SuperOpsValidationError, match="Author ID must be a non-empty string"):
            await comments_manager.get_by_author("")

    # Test GraphQL query building methods
    def test_build_get_query(self, comments_manager) -> None:
        """Test building get query."""
        query = comments_manager._build_get_query()
        assert "query GetComment($id: ID!)" in query
        assert "comment(id: $id)" in query

    def test_build_list_query(self, comments_manager) -> None:
        """Test building list query."""
        query = comments_manager._build_list_query()
        assert "query ListComments(" in query
        assert "comments(" in query
        assert "items" in query
        assert "pagination" in query

    def test_build_create_mutation(self, comments_manager) -> None:
        """Test building create mutation."""
        mutation = comments_manager._build_create_mutation()
        assert "mutation CreateComment($input: CommentInput!)" in mutation
        assert "createComment(input: $input)" in mutation

    def test_build_update_mutation(self, comments_manager) -> None:
        """Test building update mutation."""
        mutation = comments_manager._build_update_mutation()
        assert "mutation UpdateComment($id: ID!, $input: CommentInput!)" in mutation
        assert "updateComment(id: $id, input: $input)" in mutation

    def test_build_delete_mutation(self, comments_manager) -> None:
        """Test building delete mutation."""
        mutation = comments_manager._build_delete_mutation()
        assert "mutation DeleteComment($id: ID!)" in mutation
        assert "deleteComment(id: $id)" in mutation

    def test_build_search_query(self, comments_manager) -> None:
        """Test building search query."""
        query = comments_manager._build_search_query()
        assert "query SearchComments(" in query
        assert "searchComments(" in query

    # Test error handling
    @pytest.mark.asyncio
    async def test_api_error_handling(self, comments_manager) -> None:
        """Test API error handling."""
        with patch.object(
            comments_manager, "list", side_effect=SuperOpsAPIError("API Error", 500)
        ), pytest.raises(SuperOpsAPIError):
            await comments_manager.get_comments_for_entity("ticket", "ticket-123")

    @pytest.mark.asyncio
    async def test_resource_not_found_handling(self, comments_manager) -> None:
        """Test resource not found error handling."""
        with patch.object(
            comments_manager, "get", side_effect=SuperOpsResourceNotFoundError("Comment not found")
        ), pytest.raises(SuperOpsResourceNotFoundError):
            await comments_manager.reply_to_comment("nonexistent-comment", "Reply content")
