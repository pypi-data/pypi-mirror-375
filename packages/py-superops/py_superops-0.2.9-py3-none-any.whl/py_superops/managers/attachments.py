# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Attachment manager for SuperOps API operations."""

from __future__ import annotations

import asyncio
import os
import mimetypes
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Union
from urllib.parse import urlparse
from hashlib import md5

import aiohttp
import aiofiles

from ..exceptions import (
    SuperOpsAPIError,
    SuperOpsResourceNotFoundError,
    SuperOpsValidationError,
)
from ..graphql.types import (
    Attachment,
    AttachmentFilter,
    AttachmentType,
    EntityType,
)
from ..graphql.fragments import ATTACHMENT_FRAGMENTS, get_attachment_fields
from .base import ResourceManager


class AttachmentsManager(ResourceManager[Attachment]):
    """Manager for attachment operations.

    Provides high-level methods for managing SuperOps attachments including
    file uploads, downloads, metadata management, versioning, and bulk operations.
    Handles both GraphQL metadata operations and REST file operations.
    """

    def __init__(self, client: "SuperOpsClient"):
        """Initialize the attachments manager.

        Args:
            client: SuperOps client instance
        """
        super().__init__(client, Attachment, "attachment")

    async def get_attachments_for_entity(
        self,
        entity_type: EntityType,
        entity_id: str,
        page: int = 1,
        page_size: int = 50,
        filters: Optional[AttachmentFilter] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get all attachments for a specific entity.

        Args:
            entity_type: Type of entity (TICKET, TASK, etc.)
            entity_id: ID of the entity
            page: Page number (1-based)
            page_size: Number of items per page
            filters: Additional attachment filters
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Attachment]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not isinstance(entity_type, EntityType):
            raise SuperOpsValidationError("Entity type must be an EntityType enum")
        if not entity_id or not isinstance(entity_id, str):
            raise SuperOpsValidationError("Entity ID must be a non-empty string")

        self.logger.debug(f"Getting attachments for {entity_type.value}:{entity_id}")

        # Build filters including entity filter
        combined_filters = {"entity_type": entity_type.value, "entity_id": entity_id}
        if filters:
            combined_filters.update(filters.__dict__)

        return await self.list(
            page=page,
            page_size=page_size,
            filters=combined_filters,
            sort_by=sort_by or "created_at",
            sort_order=sort_order,
        )

    async def upload_file(
        self,
        file_path: Union[str, Path],
        entity_type: EntityType,
        entity_id: str,
        description: Optional[str] = None,
        attachment_type: Optional[AttachmentType] = None,
        is_public: bool = False,
    ) -> Attachment:
        """Upload a file and attach it to an entity.

        Args:
            file_path: Path to the file to upload
            entity_type: Type of entity to attach to
            entity_id: ID of the entity to attach to
            description: Optional description for the attachment
            attachment_type: Optional attachment type
            is_public: Whether the attachment is public

        Returns:
            Created attachment instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the upload fails
            FileNotFoundError: If the file doesn't exist
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise SuperOpsValidationError(f"Path is not a file: {file_path}")

        self.logger.debug(f"Uploading file {file_path.name} for {entity_type.value}:{entity_id}")

        # Get file metadata
        file_size = file_path.stat().st_size
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            mime_type = "application/octet-stream"

        # Detect attachment type if not provided
        if not attachment_type:
            attachment_type = self._detect_attachment_type(mime_type)

        # Calculate file checksum
        checksum = await self._calculate_file_checksum(file_path)

        # Step 1: Get upload URL from GraphQL
        upload_data = await self._get_upload_url(
            file_path.name, file_size, mime_type, entity_type, entity_id
        )

        # Step 2: Upload file to REST endpoint
        try:
            async with aiofiles.open(file_path, "rb") as f:
                file_content = await f.read()
                await self._upload_file_content(upload_data, file_content, file_path.name, mime_type)

        except Exception as e:
            self.logger.error(f"File upload failed: {e}")
            raise SuperOpsAPIError(f"File upload failed: {str(e)}", 500, {}) from e

        # Step 3: Complete upload via GraphQL
        attachment = await self._complete_upload(
            upload_data["token"],
            file_path.name,
            file_path.name,
            file_size,
            mime_type,
            entity_type,
            entity_id,
            description,
            attachment_type,
            is_public,
            checksum,
        )

        self.logger.info(f"Successfully uploaded {file_path.name} as attachment {attachment.id}")
        return attachment

    async def upload_content(
        self,
        content: bytes,
        filename: str,
        entity_type: EntityType,
        entity_id: str,
        mime_type: Optional[str] = None,
        description: Optional[str] = None,
        attachment_type: Optional[AttachmentType] = None,
        is_public: bool = False,
    ) -> Attachment:
        """Upload file content directly and attach it to an entity.

        Args:
            content: File content as bytes
            filename: Name for the file
            entity_type: Type of entity to attach to
            entity_id: ID of the entity to attach to
            mime_type: MIME type of the content
            description: Optional description for the attachment
            attachment_type: Optional attachment type
            is_public: Whether the attachment is public

        Returns:
            Created attachment instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the upload fails
        """
        if not content:
            raise SuperOpsValidationError("Content cannot be empty")
        if not filename:
            raise SuperOpsValidationError("Filename must be provided")

        self.logger.debug(f"Uploading content as {filename} for {entity_type.value}:{entity_id}")

        # Determine MIME type
        if not mime_type:
            mime_type, _ = mimetypes.guess_type(filename)
            if not mime_type:
                mime_type = "application/octet-stream"

        # Detect attachment type if not provided
        if not attachment_type:
            attachment_type = self._detect_attachment_type(mime_type)

        file_size = len(content)
        checksum = md5(content).hexdigest()

        # Step 1: Get upload URL
        upload_data = await self._get_upload_url(filename, file_size, mime_type, entity_type, entity_id)

        # Step 2: Upload content
        try:
            await self._upload_file_content(upload_data, content, filename, mime_type)
        except Exception as e:
            self.logger.error(f"Content upload failed: {e}")
            raise SuperOpsAPIError(f"Content upload failed: {str(e)}", 500, {}) from e

        # Step 3: Complete upload
        attachment = await self._complete_upload(
            upload_data["token"],
            filename,
            filename,
            file_size,
            mime_type,
            entity_type,
            entity_id,
            description,
            attachment_type,
            is_public,
            checksum,
        )

        self.logger.info(f"Successfully uploaded content as attachment {attachment.id}")
        return attachment

    async def download_attachment(self, attachment_id: str) -> bytes:
        """Download attachment content.

        Args:
            attachment_id: ID of the attachment to download

        Returns:
            File content as bytes

        Raises:
            SuperOpsValidationError: If attachment_id is invalid
            SuperOpsResourceNotFoundError: If attachment doesn't exist
            SuperOpsAPIError: If the download fails
        """
        if not attachment_id or not isinstance(attachment_id, str):
            raise SuperOpsValidationError("Attachment ID must be a non-empty string")

        self.logger.debug(f"Downloading attachment {attachment_id}")

        # Get download URL from GraphQL
        download_url = await self._get_download_url(attachment_id)

        # Download file content
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(download_url) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise SuperOpsAPIError(f"Download failed: {error_text}", response.status, {})

                    content = await response.read()
                    self.logger.info(f"Successfully downloaded attachment {attachment_id}")
                    return content

        except aiohttp.ClientError as e:
            self.logger.error(f"Download request failed: {e}")
            raise SuperOpsAPIError(f"Download request failed: {str(e)}", 500, {}) from e

    async def download_to_file(self, attachment_id: str, file_path: Union[str, Path]) -> Path:
        """Download attachment and save to file.

        Args:
            attachment_id: ID of the attachment to download
            file_path: Path where to save the downloaded file

        Returns:
            Path to the downloaded file

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the download fails
        """
        content = await self.download_attachment(attachment_id)
        
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        self.logger.info(f"Downloaded attachment {attachment_id} to {file_path}")
        return file_path

    async def create_version(
        self,
        attachment_id: str,
        file_path: Union[str, Path],
        description: Optional[str] = None,
    ) -> Attachment:
        """Create a new version of an existing attachment.

        Args:
            attachment_id: ID of the existing attachment
            file_path: Path to the new version file
            description: Optional description for the new version

        Returns:
            Updated attachment with new version

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsResourceNotFoundError: If attachment doesn't exist
            SuperOpsAPIError: If the operation fails
        """
        if not attachment_id or not isinstance(attachment_id, str):
            raise SuperOpsValidationError("Attachment ID must be a non-empty string")

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        self.logger.debug(f"Creating new version for attachment {attachment_id}")

        # Get existing attachment metadata
        existing_attachment = await self.get(attachment_id)
        if not existing_attachment:
            raise SuperOpsResourceNotFoundError(f"Attachment not found: {attachment_id}")

        # Get file metadata
        file_size = file_path.stat().st_size
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            mime_type = existing_attachment.mime_type

        checksum = await self._calculate_file_checksum(file_path)

        # Create new version mutation
        mutation = self._build_create_version_mutation()
        variables = {
            "input": {
                "attachment_id": attachment_id,
                "filename": file_path.name,
                "original_filename": file_path.name,
                "file_size": file_size,
                "mime_type": mime_type,
                "description": description,
                "checksum": checksum,
            }
        }

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when creating version", 500, response)

        version_data = response["data"].get("createAttachmentVersion")
        if not version_data:
            raise SuperOpsAPIError("No version data in response", 500, response)

        # Upload new version content
        upload_data = version_data.get("uploadData")
        if upload_data:
            async with aiofiles.open(file_path, "rb") as f:
                content = await f.read()
                await self._upload_file_content(upload_data, content, file_path.name, mime_type)

        # Return updated attachment
        return Attachment.from_dict(version_data.get("attachment", version_data))

    async def bulk_upload(
        self,
        file_paths: List[Union[str, Path]],
        entity_type: EntityType,
        entity_id: str,
        descriptions: Optional[List[str]] = None,
        max_concurrent: int = 3,
    ) -> List[Attachment]:
        """Upload multiple files concurrently.

        Args:
            file_paths: List of file paths to upload
            entity_type: Type of entity to attach to
            entity_id: ID of the entity to attach to
            descriptions: Optional list of descriptions (must match file_paths length)
            max_concurrent: Maximum number of concurrent uploads

        Returns:
            List of created attachments

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If any upload fails
        """
        if not file_paths:
            raise SuperOpsValidationError("File paths list cannot be empty")

        if descriptions and len(descriptions) != len(file_paths):
            raise SuperOpsValidationError(
                "Descriptions list must have same length as file_paths"
            )

        self.logger.debug(f"Bulk uploading {len(file_paths)} files")

        # Create semaphore to limit concurrent uploads
        semaphore = asyncio.Semaphore(max_concurrent)

        async def upload_single(index: int, path: Union[str, Path]) -> Attachment:
            async with semaphore:
                description = descriptions[index] if descriptions else None
                return await self.upload_file(path, entity_type, entity_id, description)

        # Execute uploads concurrently
        tasks = [upload_single(i, path) for i, path in enumerate(file_paths)]
        attachments = await asyncio.gather(*tasks)

        self.logger.info(f"Successfully uploaded {len(attachments)} files")
        return attachments

    async def bulk_download(
        self,
        attachment_ids: List[str],
        target_dir: Union[str, Path],
        max_concurrent: int = 3,
    ) -> List[Path]:
        """Download multiple attachments concurrently.

        Args:
            attachment_ids: List of attachment IDs to download
            target_dir: Directory where to save downloaded files
            max_concurrent: Maximum number of concurrent downloads

        Returns:
            List of paths to downloaded files

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If any download fails
        """
        if not attachment_ids:
            raise SuperOpsValidationError("Attachment IDs list cannot be empty")

        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        self.logger.debug(f"Bulk downloading {len(attachment_ids)} attachments")

        # Create semaphore to limit concurrent downloads
        semaphore = asyncio.Semaphore(max_concurrent)

        async def download_single(attachment_id: str) -> Path:
            async with semaphore:
                # Get attachment metadata for filename
                attachment = await self.get(attachment_id)
                if not attachment:
                    raise SuperOpsResourceNotFoundError(f"Attachment not found: {attachment_id}")

                file_path = target_dir / attachment.filename
                return await self.download_to_file(attachment_id, file_path)

        # Execute downloads concurrently
        tasks = [download_single(attachment_id) for attachment_id in attachment_ids]
        file_paths = await asyncio.gather(*tasks)

        self.logger.info(f"Successfully downloaded {len(file_paths)} attachments")
        return file_paths

    async def bulk_delete(self, attachment_ids: List[str]) -> Dict[str, bool]:
        """Delete multiple attachments.

        Args:
            attachment_ids: List of attachment IDs to delete

        Returns:
            Dictionary mapping attachment IDs to success status

        Raises:
            SuperOpsValidationError: If parameters are invalid
        """
        if not attachment_ids:
            raise SuperOpsValidationError("Attachment IDs list cannot be empty")

        self.logger.debug(f"Bulk deleting {len(attachment_ids)} attachments")

        results = {}
        for attachment_id in attachment_ids:
            try:
                success = await self.delete(attachment_id)
                results[attachment_id] = success
            except Exception as e:
                self.logger.error(f"Failed to delete attachment {attachment_id}: {e}")
                results[attachment_id] = False

        successful_count = sum(1 for success in results.values() if success)
        self.logger.info(f"Successfully deleted {successful_count} out of {len(attachment_ids)} attachments")

        return results

    async def get_attachment_history(self, attachment_id: str) -> List[Dict[str, Any]]:
        """Get version history for an attachment.

        Args:
            attachment_id: ID of the attachment

        Returns:
            List of version history records

        Raises:
            SuperOpsValidationError: If attachment_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not attachment_id or not isinstance(attachment_id, str):
            raise SuperOpsValidationError("Attachment ID must be a non-empty string")

        self.logger.debug(f"Getting history for attachment {attachment_id}")

        query = """
            query GetAttachmentHistory($id: ID!) {
                attachmentHistory(id: $id) {
                    version
                    filename
                    fileSize
                    mimeType
                    description
                    checksum
                    uploadedBy
                    uploadedByName
                    createdAt
                }
            }
        """

        variables = {"id": attachment_id}

        response = await self.client.execute_query(query, variables)

        if not response.get("data"):
            return []

        history = response["data"].get("attachmentHistory", [])
        return history

    # Helper methods

    def _detect_attachment_type(self, mime_type: str) -> AttachmentType:
        """Detect attachment type from MIME type."""
        mime_type = mime_type.lower()

        if mime_type.startswith("image/"):
            return AttachmentType.IMAGE
        elif mime_type.startswith("video/"):
            return AttachmentType.VIDEO
        elif mime_type.startswith("audio/"):
            return AttachmentType.AUDIO
        elif mime_type in ["application/pdf", "text/plain", "application/rtf"]:
            return AttachmentType.DOCUMENT
        elif mime_type in [
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/csv",
        ]:
            return AttachmentType.SPREADSHEET
        elif mime_type in [
            "application/vnd.ms-powerpoint",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ]:
            return AttachmentType.PRESENTATION
        elif mime_type in ["application/zip", "application/x-rar-compressed", "application/x-7z-compressed"]:
            return AttachmentType.ARCHIVE
        elif mime_type in ["text/x-python", "text/x-java-source", "text/javascript", "text/html"]:
            return AttachmentType.CODE
        else:
            return AttachmentType.OTHER

    async def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of a file."""
        hash_md5 = md5()
        async with aiofiles.open(file_path, "rb") as f:
            async for chunk in self._file_chunks(f):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    async def _file_chunks(self, file_obj, chunk_size: int = 8192):
        """Async generator for file chunks."""
        while True:
            chunk = await file_obj.read(chunk_size)
            if not chunk:
                break
            yield chunk

    async def _get_upload_url(
        self,
        filename: str,
        file_size: int,
        mime_type: str,
        entity_type: EntityType,
        entity_id: str,
    ) -> Dict[str, Any]:
        """Get upload URL from GraphQL."""
        mutation = """
            mutation GetUploadUrl($input: GetUploadUrlInput!) {
                getUploadUrl(input: $input) {
                    url
                    token
                    headers
                    fields
                }
            }
        """

        variables = {
            "input": {
                "filename": filename,
                "file_size": file_size,
                "mime_type": mime_type,
                "entity_type": entity_type.value,
                "entity_id": entity_id,
            }
        }

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when getting upload URL", 500, response)

        upload_data = response["data"].get("getUploadUrl")
        if not upload_data:
            raise SuperOpsAPIError("No upload URL in response", 500, response)

        return upload_data

    async def _upload_file_content(
        self, upload_data: Dict[str, Any], content: bytes, filename: str, mime_type: str
    ) -> None:
        """Upload file content to REST endpoint."""
        url = upload_data["url"]
        headers = upload_data.get("headers", {})
        fields = upload_data.get("fields", {})

        async with aiohttp.ClientSession() as session:
            # Prepare form data
            form_data = aiohttp.FormData()

            # Add any required fields from the upload data
            for key, value in fields.items():
                form_data.add_field(key, value)

            # Add the file
            form_data.add_field(
                "file",
                content,
                filename=filename,
                content_type=mime_type,
            )

            async with session.post(url, data=form_data, headers=headers) as response:
                if response.status not in (200, 201, 204):
                    error_text = await response.text()
                    raise SuperOpsAPIError(
                        f"File upload failed with status {response.status}: {error_text}",
                        response.status,
                        {},
                    )

    async def _complete_upload(
        self,
        token: str,
        filename: str,
        original_filename: str,
        file_size: int,
        mime_type: str,
        entity_type: EntityType,
        entity_id: str,
        description: Optional[str] = None,
        attachment_type: Optional[AttachmentType] = None,
        is_public: bool = False,
        checksum: Optional[str] = None,
    ) -> Attachment:
        """Complete upload process via GraphQL."""
        mutation = """
            mutation CompleteUpload($input: CompleteUploadInput!) {
                completeUpload(input: $input) {
                    id
                    filename
                    originalFilename
                    fileSize
                    mimeType
                    entityType
                    entityId
                    attachmentType
                    description
                    url
                    downloadUrl
                    version
                    uploadedBy
                    uploadedByName
                    isPublic
                    checksum
                    metadata
                    createdAt
                    updatedAt
                }
            }
        """

        variables = {
            "input": {
                "token": token,
                "filename": filename,
                "original_filename": original_filename,
                "file_size": file_size,
                "mime_type": mime_type,
                "entity_type": entity_type.value,
                "entity_id": entity_id,
                "description": description,
                "attachment_type": attachment_type.value if attachment_type else None,
                "is_public": is_public,
                "checksum": checksum,
            }
        }

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when completing upload", 500, response)

        attachment_data = response["data"].get("completeUpload")
        if not attachment_data:
            raise SuperOpsAPIError("No attachment data in response", 500, response)

        return Attachment.from_dict(attachment_data)

    async def _get_download_url(self, attachment_id: str) -> str:
        """Get download URL from GraphQL."""
        query = """
            query GetDownloadUrl($id: ID!) {
                getDownloadUrl(id: $id) {
                    url
                    expiresAt
                }
            }
        """

        variables = {"id": attachment_id}

        response = await self.client.execute_query(query, variables)

        if not response.get("data"):
            raise SuperOpsAPIError("No data returned when getting download URL", 500, response)

        download_data = response["data"].get("getDownloadUrl")
        if not download_data:
            raise SuperOpsResourceNotFoundError(f"Attachment not found: {attachment_id}")

        return download_data["url"]

    # Protected methods for GraphQL query building (required by base class)

    def _build_get_query(self, **kwargs) -> str:
        """Build GraphQL query for getting a single attachment."""
        detail_level = kwargs.get("detail_level", "full")
        fragment_names = get_attachment_fields(detail_level)

        return f"""
            query GetAttachment($id: ID!) {{
                attachment(id: $id) {{
                    ...{list(fragment_names)[0]}
                }}
            }}

            {self._build_fragments_string(fragment_names)}
        """

    def _build_list_query(self, **kwargs) -> str:
        """Build GraphQL query for listing attachments."""
        detail_level = kwargs.get("detail_level", "core")
        fragment_names = get_attachment_fields(detail_level)

        return f"""
            query ListAttachments(
                $page: Int!
                $pageSize: Int!
                $filters: AttachmentFilter
                $sortBy: String
                $sortOrder: SortOrder
            ) {{
                attachments(
                    page: $page
                    pageSize: $pageSize
                    filters: $filters
                    sortBy: $sortBy
                    sortOrder: $sortOrder
                ) {{
                    items {{
                        ...{list(fragment_names)[0]}
                    }}
                    pagination {{
                        page
                        pageSize
                        total
                        hasNextPage
                        hasPreviousPage
                    }}
                }}
            }}

            {self._build_fragments_string(fragment_names)}
        """

    def _build_create_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for creating an attachment."""
        return """
            mutation CreateAttachment($input: CreateAttachmentInput!) {
                createAttachment(input: $input) {
                    id
                    filename
                    originalFilename
                    fileSize
                    mimeType
                    entityType
                    entityId
                    attachmentType
                    description
                    url
                    downloadUrl
                    version
                    uploadedBy
                    uploadedByName
                    isPublic
                    checksum
                    metadata
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_update_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for updating an attachment."""
        return """
            mutation UpdateAttachment($id: ID!, $input: UpdateAttachmentInput!) {
                updateAttachment(id: $id, input: $input) {
                    id
                    filename
                    originalFilename
                    fileSize
                    mimeType
                    entityType
                    entityId
                    attachmentType
                    description
                    url
                    downloadUrl
                    version
                    uploadedBy
                    uploadedByName
                    isPublic
                    checksum
                    metadata
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_delete_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for deleting an attachment."""
        return """
            mutation DeleteAttachment($id: ID!) {
                deleteAttachment(id: $id) {
                    success
                    message
                }
            }
        """

    def _build_search_query(self, **kwargs) -> str:
        """Build GraphQL query for searching attachments."""
        detail_level = kwargs.get("detail_level", "core")
        fragment_names = get_attachment_fields(detail_level)

        return f"""
            query SearchAttachments(
                $query: String!
                $page: Int!
                $pageSize: Int!
            ) {{
                searchAttachments(
                    query: $query
                    page: $page
                    pageSize: $pageSize
                ) {{
                    items {{
                        ...{list(fragment_names)[0]}
                    }}
                    pagination {{
                        page
                        pageSize
                        total
                        hasNextPage
                        hasPreviousPage
                    }}
                }}
            }}

            {self._build_fragments_string(fragment_names)}
        """

    def _build_create_version_mutation(self) -> str:
        """Build GraphQL mutation for creating attachment version."""
        return """
            mutation CreateAttachmentVersion($input: CreateAttachmentVersionInput!) {
                createAttachmentVersion(input: $input) {
                    attachment {
                        id
                        filename
                        originalFilename
                        fileSize
                        mimeType
                        entityType
                        entityId
                        attachmentType
                        description
                        url
                        downloadUrl
                        version
                        uploadedBy
                        uploadedByName
                        isPublic
                        checksum
                        metadata
                        createdAt
                        updatedAt
                    }
                    uploadData {
                        url
                        headers
                        fields
                    }
                }
            }
        """

    def _build_fragments_string(self, fragment_names: set) -> str:
        """Build fragments string for queries."""
        from ..graphql.fragments import build_fragments_string
        return build_fragments_string(fragment_names)

    def _validate_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data for attachment creation."""
        validated = data.copy()

        # Required fields
        if not validated.get("filename"):
            raise SuperOpsValidationError("Filename is required")
        if not validated.get("entity_type"):
            raise SuperOpsValidationError("Entity type is required")
        if not validated.get("entity_id"):
            raise SuperOpsValidationError("Entity ID is required")

        # Validate entity type
        entity_type = validated.get("entity_type")
        if entity_type and entity_type not in [t.value for t in EntityType]:
            raise SuperOpsValidationError(f"Invalid entity type: {entity_type}")

        # Validate attachment type if provided
        attachment_type = validated.get("attachment_type")
        if attachment_type and attachment_type not in [t.value for t in AttachmentType]:
            raise SuperOpsValidationError(f"Invalid attachment type: {attachment_type}")

        return validated

    def _validate_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data for attachment updates."""
        validated = data.copy()

        # Validate attachment type if provided
        attachment_type = validated.get("attachment_type")
        if attachment_type and attachment_type not in [t.value for t in AttachmentType]:
            raise SuperOpsValidationError(f"Invalid attachment type: {attachment_type}")

        return validated