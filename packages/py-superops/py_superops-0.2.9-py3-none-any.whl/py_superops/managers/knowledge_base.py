# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Knowledge base manager for SuperOps API operations."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..exceptions import SuperOpsValidationError
from ..graphql.types import KnowledgeBaseArticle, KnowledgeBaseCollection
from .base import ResourceManager


class KnowledgeBaseCollectionManager(ResourceManager[KnowledgeBaseCollection]):
    """Manager for knowledge base collection operations.

    Provides high-level methods for managing knowledge base collections.
    """

    def __init__(self, client: "SuperOpsClient"):
        """Initialize the collection manager.

        Args:
            client: SuperOps client instance
        """
        super().__init__(client, KnowledgeBaseCollection, "knowledgeBaseCollection")

    async def get_public_collections(
        self,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get public knowledge base collections.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: name)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[KnowledgeBaseCollection]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Getting public knowledge base collections")

        filters = {"is_public": True}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
        )

    async def get_by_parent(
        self,
        parent_id: str,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get child collections of a parent collection.

        Args:
            parent_id: The parent collection ID
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: name)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[KnowledgeBaseCollection]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not parent_id or not isinstance(parent_id, str):
            raise SuperOpsValidationError("Parent ID must be a non-empty string")

        self.logger.debug(f"Getting child collections for parent: {parent_id}")

        filters = {"parent_id": parent_id}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
        )

    async def get_root_collections(
        self,
        page: int = 1,
        page_size: int = 50,
        include_private: bool = False,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get root level collections (no parent).

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            include_private: Whether to include private collections
            sort_by: Field to sort by (default: name)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[KnowledgeBaseCollection]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Getting root knowledge base collections")

        filters = {"parent_id": None}
        if not include_private:
            filters["is_public"] = True

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
        )

    async def make_public(self, collection_id: str) -> KnowledgeBaseCollection:
        """Make a collection public.

        Args:
            collection_id: The collection ID

        Returns:
            Updated collection instance

        Raises:
            SuperOpsValidationError: If collection_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not collection_id or not isinstance(collection_id, str):
            raise SuperOpsValidationError(f"Invalid collection ID: {collection_id}")

        self.logger.debug(f"Making collection public: {collection_id}")

        return await self.update(collection_id, {"is_public": True})

    async def make_private(self, collection_id: str) -> KnowledgeBaseCollection:
        """Make a collection private.

        Args:
            collection_id: The collection ID

        Returns:
            Updated collection instance

        Raises:
            SuperOpsValidationError: If collection_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not collection_id or not isinstance(collection_id, str):
            raise SuperOpsValidationError(f"Invalid collection ID: {collection_id}")

        self.logger.debug(f"Making collection private: {collection_id}")

        return await self.update(collection_id, {"is_public": False})

    async def move_collection(
        self, collection_id: str, new_parent_id: Optional[str]
    ) -> KnowledgeBaseCollection:
        """Move a collection to a different parent.

        Args:
            collection_id: The collection ID to move
            new_parent_id: New parent collection ID (None for root level)

        Returns:
            Updated collection instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not collection_id or not isinstance(collection_id, str):
            raise SuperOpsValidationError(f"Invalid collection ID: {collection_id}")

        self.logger.debug(f"Moving collection {collection_id} to parent {new_parent_id}")

        # Validate that we're not creating a circular reference
        if new_parent_id == collection_id:
            raise SuperOpsValidationError("Cannot make collection a child of itself")

        return await self.update(collection_id, {"parent_id": new_parent_id})

    # GraphQL query building methods

    def _build_get_query(self, **kwargs) -> str:
        """Build GraphQL query for getting a single collection."""
        return """
            query GetKnowledgeBaseCollection($id: ID!) {
                knowledgeBaseCollection(id: $id) {
                    id
                    name
                    description
                    parentId
                    isPublic
                    articleCount
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_list_query(self, **kwargs) -> str:
        """Build GraphQL query for listing collections."""
        return """
            query ListKnowledgeBaseCollections(
                $page: Int!
                $pageSize: Int!
                $filters: KnowledgeBaseCollectionFilter
                $sortBy: String
                $sortOrder: SortOrder
            ) {
                knowledgeBaseCollections(
                    page: $page
                    pageSize: $pageSize
                    filters: $filters
                    sortBy: $sortBy
                    sortOrder: $sortOrder
                ) {
                    items {
                        id
                        name
                        description
                        parentId
                        isPublic
                        articleCount
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
        """Build GraphQL mutation for creating a collection."""
        return """
            mutation CreateKnowledgeBaseCollection($input: CreateKnowledgeBaseCollectionInput!) {
                createKnowledgeBaseCollection(input: $input) {
                    id
                    name
                    description
                    parentId
                    isPublic
                    articleCount
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_update_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for updating a collection."""
        return """
            mutation UpdateKnowledgeBaseCollection($id: ID!, $input: UpdateKnowledgeBaseCollectionInput!) {
                updateKnowledgeBaseCollection(id: $id, input: $input) {
                    id
                    name
                    description
                    parentId
                    isPublic
                    articleCount
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_delete_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for deleting a collection."""
        return """
            mutation DeleteKnowledgeBaseCollection($id: ID!) {
                deleteKnowledgeBaseCollection(id: $id) {
                    success
                    message
                }
            }
        """

    def _build_search_query(self, **kwargs) -> str:
        """Build GraphQL query for searching collections."""
        return """
            query SearchKnowledgeBaseCollections(
                $query: String!
                $page: Int!
                $pageSize: Int!
            ) {
                searchKnowledgeBaseCollections(
                    query: $query
                    page: $page
                    pageSize: $pageSize
                ) {
                    items {
                        id
                        name
                        description
                        parentId
                        isPublic
                        articleCount
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
        """Validate data for collection creation."""
        validated = data.copy()

        # Required fields
        if not validated.get("name"):
            raise SuperOpsValidationError("Collection name is required")

        return validated

    def _validate_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data for collection updates."""
        return data.copy()


class KnowledgeBaseArticleManager(ResourceManager[KnowledgeBaseArticle]):
    """Manager for knowledge base article operations.

    Provides high-level methods for managing knowledge base articles.
    """

    def __init__(self, client: "SuperOpsClient"):
        """Initialize the article manager.

        Args:
            client: SuperOps client instance
        """
        super().__init__(client, KnowledgeBaseArticle, "knowledgeBaseArticle")

    async def get_by_collection(
        self,
        collection_id: str,
        page: int = 1,
        page_size: int = 50,
        published_only: bool = True,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get articles in a specific collection.

        Args:
            collection_id: The collection ID
            page: Page number (1-based)
            page_size: Number of items per page
            published_only: Whether to only return published articles
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[KnowledgeBaseArticle]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not collection_id or not isinstance(collection_id, str):
            raise SuperOpsValidationError("Collection ID must be a non-empty string")

        self.logger.debug(f"Getting articles for collection: {collection_id}")

        filters = {"collection_id": collection_id}
        if published_only:
            filters["is_published"] = True

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
        )

    async def get_published_articles(
        self,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get all published articles.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[KnowledgeBaseArticle]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Getting published articles")

        filters = {"is_published": True}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
        )

    async def get_featured_articles(
        self,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get featured articles.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: view_count)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[KnowledgeBaseArticle]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Getting featured articles")

        filters = {"is_featured": True, "is_published": True}

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "view_count",
            sort_order=sort_order,
        )

    async def get_by_author(
        self,
        author_id: str,
        page: int = 1,
        page_size: int = 50,
        published_only: bool = False,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get articles by a specific author.

        Args:
            author_id: The author ID
            page: Page number (1-based)
            page_size: Number of items per page
            published_only: Whether to only return published articles
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[KnowledgeBaseArticle]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not author_id or not isinstance(author_id, str):
            raise SuperOpsValidationError("Author ID must be a non-empty string")

        self.logger.debug(f"Getting articles by author: {author_id}")

        filters = {"author_id": author_id}
        if published_only:
            filters["is_published"] = True

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
        )

    async def get_most_viewed(
        self, page: int = 1, page_size: int = 50, collection_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get most viewed articles.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            collection_id: Optional collection ID to filter by

        Returns:
            Dictionary containing 'items' (List[KnowledgeBaseArticle]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Getting most viewed articles")

        filters = {"is_published": True}
        if collection_id:
            filters["collection_id"] = collection_id

        return await self.list(
            page=page, page_size=page_size, filters=filters, sort_by="view_count", sort_order="desc"
        )

    async def publish_article(self, article_id: str) -> KnowledgeBaseArticle:
        """Publish an article.

        Args:
            article_id: The article ID

        Returns:
            Updated article instance

        Raises:
            SuperOpsValidationError: If article_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not article_id or not isinstance(article_id, str):
            raise SuperOpsValidationError(f"Invalid article ID: {article_id}")

        self.logger.debug(f"Publishing article: {article_id}")

        return await self.update(article_id, {"is_published": True})

    async def unpublish_article(self, article_id: str) -> KnowledgeBaseArticle:
        """Unpublish an article.

        Args:
            article_id: The article ID

        Returns:
            Updated article instance

        Raises:
            SuperOpsValidationError: If article_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not article_id or not isinstance(article_id, str):
            raise SuperOpsValidationError(f"Invalid article ID: {article_id}")

        self.logger.debug(f"Unpublishing article: {article_id}")

        return await self.update(article_id, {"is_published": False})

    async def feature_article(self, article_id: str) -> KnowledgeBaseArticle:
        """Feature an article.

        Args:
            article_id: The article ID

        Returns:
            Updated article instance

        Raises:
            SuperOpsValidationError: If article_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not article_id or not isinstance(article_id, str):
            raise SuperOpsValidationError(f"Invalid article ID: {article_id}")

        self.logger.debug(f"Featuring article: {article_id}")

        return await self.update(article_id, {"is_featured": True})

    async def unfeature_article(self, article_id: str) -> KnowledgeBaseArticle:
        """Unfeature an article.

        Args:
            article_id: The article ID

        Returns:
            Updated article instance

        Raises:
            SuperOpsValidationError: If article_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not article_id or not isinstance(article_id, str):
            raise SuperOpsValidationError(f"Invalid article ID: {article_id}")

        self.logger.debug(f"Unfeaturing article: {article_id}")

        return await self.update(article_id, {"is_featured": False})

    async def move_to_collection(self, article_id: str, collection_id: str) -> KnowledgeBaseArticle:
        """Move an article to a different collection.

        Args:
            article_id: The article ID
            collection_id: The new collection ID

        Returns:
            Updated article instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not article_id or not isinstance(article_id, str):
            raise SuperOpsValidationError(f"Invalid article ID: {article_id}")
        if not collection_id or not isinstance(collection_id, str):
            raise SuperOpsValidationError("Collection ID must be a non-empty string")

        self.logger.debug(f"Moving article {article_id} to collection {collection_id}")

        return await self.update(article_id, {"collection_id": collection_id})

    async def increment_view_count(self, article_id: str) -> int:
        """Increment the view count for an article.

        Args:
            article_id: The article ID

        Returns:
            New view count

        Raises:
            SuperOpsValidationError: If article_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not article_id or not isinstance(article_id, str):
            raise SuperOpsValidationError(f"Invalid article ID: {article_id}")

        self.logger.debug(f"Incrementing view count for article: {article_id}")

        mutation = """
            mutation IncrementArticleViewCount($articleId: ID!) {
                incrementArticleViewCount(articleId: $articleId) {
                    viewCount
                }
            }
        """

        variables = {"articleId": article_id}

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when incrementing view count", 500, response)

        result = response["data"].get("incrementArticleViewCount")
        if not result:
            raise SuperOpsAPIError("No result data in response", 500, response)

        return result.get("viewCount", 0)

    async def add_tag(self, article_id: str, tag: str) -> KnowledgeBaseArticle:
        """Add a tag to an article.

        Args:
            article_id: The article ID
            tag: Tag to add

        Returns:
            Updated article instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not article_id or not isinstance(article_id, str):
            raise SuperOpsValidationError(f"Invalid article ID: {article_id}")
        if not tag or not isinstance(tag, str):
            raise SuperOpsValidationError("Tag must be a non-empty string")

        self.logger.debug(f"Adding tag '{tag}' to article: {article_id}")

        # Get current article to access existing tags
        article = await self.get(article_id)
        if not article:
            raise SuperOpsValidationError(f"Article not found: {article_id}")

        # Add tag if not already present
        current_tags = article.tags or []
        if tag not in current_tags:
            current_tags.append(tag)
            return await self.update(article_id, {"tags": current_tags})

        return article

    async def remove_tag(self, article_id: str, tag: str) -> KnowledgeBaseArticle:
        """Remove a tag from an article.

        Args:
            article_id: The article ID
            tag: Tag to remove

        Returns:
            Updated article instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not article_id or not isinstance(article_id, str):
            raise SuperOpsValidationError(f"Invalid article ID: {article_id}")
        if not tag or not isinstance(tag, str):
            raise SuperOpsValidationError("Tag must be a non-empty string")

        self.logger.debug(f"Removing tag '{tag}' from article: {article_id}")

        # Get current article to access existing tags
        article = await self.get(article_id)
        if not article:
            raise SuperOpsValidationError(f"Article not found: {article_id}")

        # Remove tag if present
        current_tags = article.tags or []
        if tag in current_tags:
            current_tags.remove(tag)
            return await self.update(article_id, {"tags": current_tags})

        return article

    # GraphQL query building methods

    def _build_get_query(self, **kwargs) -> str:
        """Build GraphQL query for getting a single article."""
        return """
            query GetKnowledgeBaseArticle($id: ID!) {
                knowledgeBaseArticle(id: $id) {
                    id
                    collectionId
                    title
                    content
                    authorId
                    authorName
                    summary
                    isPublished
                    isFeatured
                    viewCount
                    tags
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_list_query(self, **kwargs) -> str:
        """Build GraphQL query for listing articles."""
        return """
            query ListKnowledgeBaseArticles(
                $page: Int!
                $pageSize: Int!
                $filters: KnowledgeBaseArticleFilter
                $sortBy: String
                $sortOrder: SortOrder
            ) {
                knowledgeBaseArticles(
                    page: $page
                    pageSize: $pageSize
                    filters: $filters
                    sortBy: $sortBy
                    sortOrder: $sortOrder
                ) {
                    items {
                        id
                        collectionId
                        title
                        content
                        authorId
                        authorName
                        summary
                        isPublished
                        isFeatured
                        viewCount
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

    def _build_create_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for creating an article."""
        return """
            mutation CreateKnowledgeBaseArticle($input: CreateKnowledgeBaseArticleInput!) {
                createKnowledgeBaseArticle(input: $input) {
                    id
                    collectionId
                    title
                    content
                    authorId
                    authorName
                    summary
                    isPublished
                    isFeatured
                    viewCount
                    tags
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_update_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for updating an article."""
        return """
            mutation UpdateKnowledgeBaseArticle($id: ID!, $input: UpdateKnowledgeBaseArticleInput!) {
                updateKnowledgeBaseArticle(id: $id, input: $input) {
                    id
                    collectionId
                    title
                    content
                    authorId
                    authorName
                    summary
                    isPublished
                    isFeatured
                    viewCount
                    tags
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_delete_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for deleting an article."""
        return """
            mutation DeleteKnowledgeBaseArticle($id: ID!) {
                deleteKnowledgeBaseArticle(id: $id) {
                    success
                    message
                }
            }
        """

    def _build_search_query(self, **kwargs) -> str:
        """Build GraphQL query for searching articles."""
        return """
            query SearchKnowledgeBaseArticles(
                $query: String!
                $page: Int!
                $pageSize: Int!
            ) {
                searchKnowledgeBaseArticles(
                    query: $query
                    page: $page
                    pageSize: $pageSize
                ) {
                    items {
                        id
                        collectionId
                        title
                        content
                        authorId
                        authorName
                        summary
                        isPublished
                        isFeatured
                        viewCount
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
        """Validate data for article creation."""
        validated = data.copy()

        # Required fields
        if not validated.get("title"):
            raise SuperOpsValidationError("Article title is required")
        if not validated.get("content"):
            raise SuperOpsValidationError("Article content is required")
        if not validated.get("collection_id"):
            raise SuperOpsValidationError("Collection ID is required")
        if not validated.get("author_id"):
            raise SuperOpsValidationError("Author ID is required")

        return validated

    def _validate_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data for article updates."""
        return data.copy()


class KnowledgeBaseManager:
    """Combined manager for knowledge base operations.

    Provides access to both collection and article managers.
    """

    def __init__(self, client: "SuperOpsClient"):
        """Initialize the knowledge base manager.

        Args:
            client: SuperOps client instance
        """
        self.client = client
        self.collections = KnowledgeBaseCollectionManager(client)
        self.articles = KnowledgeBaseArticleManager(client)

    async def search_all(
        self, query: str, page: int = 1, page_size: int = 50, published_only: bool = True
    ) -> Dict[str, Any]:
        """Search across both collections and articles.

        Args:
            query: Search query string
            page: Page number (1-based)
            page_size: Number of items per page
            published_only: Whether to only search published content

        Returns:
            Dictionary containing separate results for collections and articles

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not query or not isinstance(query, str):
            raise SuperOpsValidationError("Search query must be a non-empty string")

        # Search collections
        collection_results = await self.collections.search(query, page, page_size // 2)

        # Search articles (filter by published if requested)
        if published_only:
            article_search_query = f"{query} is_published:true"
        else:
            article_search_query = query

        article_results = await self.articles.search(article_search_query, page, page_size // 2)

        return {
            "collections": collection_results,
            "articles": article_results,
            "query": query,
            "published_only": published_only,
        }
