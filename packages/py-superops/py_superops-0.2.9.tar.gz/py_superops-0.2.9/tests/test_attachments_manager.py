# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Tests for AttachmentsManager."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from py_superops.exceptions import (
    SuperOpsAPIError,
    SuperOpsResourceNotFoundError,
    SuperOpsValidationError,
)
from py_superops.graphql.types import Attachment, AttachmentType, EntityType
from py_superops.managers.attachments import AttachmentsManager


class TestAttachmentsManager:
    """Test AttachmentsManager functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client."""
        client = MagicMock()
        client.execute_query = AsyncMock()
        client.execute_mutation = AsyncMock()
        return client

    @pytest.fixture
    def attachments_manager(self, mock_client):
        """Create AttachmentsManager instance."""
        return AttachmentsManager(mock_client)

    @pytest.fixture
    def sample_attachment_data(self):
        """Sample attachment data for testing."""
        return {
            "id": "attachment_123",
            "filename": "test_document.pdf",
            "original_filename": "test_document.pdf",
            "file_size": 12345,
            "mime_type": "application/pdf",
            "entity_type": "TICKET",
            "entity_id": "ticket_456",
            "attachment_type": "DOCUMENT",
            "description": "Test attachment",
            "url": "https://example.com/files/attachment_123",
            "download_url": "https://example.com/download/attachment_123",
            "version": 1,
            "uploaded_by": "user_789",
            "uploaded_by_name": "John Doe",
            "is_public": False,
            "checksum": "abc123def456",
            "metadata": {},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for testing uploads."""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as f:
            f.write(b"Test file content")
            temp_path = Path(f.name)
        
        yield temp_path
        
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()

    @pytest.mark.asyncio
    async def test_get_attachments_for_entity_success(
        self, attachments_manager, mock_client, sample_attachment_data
    ):
        """Test getting attachments for an entity."""
        mock_client.execute_query.return_value = {
            "data": {
                "attachments": {
                    "items": [sample_attachment_data],
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

        result = await attachments_manager.get_attachments_for_entity(
            EntityType.TICKET, "ticket_456"
        )

        assert len(result["items"]) == 1
        assert result["items"][0].id == "attachment_123"
        assert result["items"][0].filename == "test_document.pdf"
        assert result["pagination"]["total"] == 1

    @pytest.mark.asyncio
    async def test_get_attachments_for_entity_validation_error(self, attachments_manager):
        """Test validation error for invalid entity type."""
        with pytest.raises(SuperOpsValidationError, match="Entity type must be an EntityType enum"):
            await attachments_manager.get_attachments_for_entity("invalid", "entity_123")

        with pytest.raises(SuperOpsValidationError, match="Entity ID must be a non-empty string"):
            await attachments_manager.get_attachments_for_entity(EntityType.TICKET, "")

    @pytest.mark.asyncio
    async def test_upload_file_success(
        self, attachments_manager, mock_client, temp_file, sample_attachment_data
    ):
        """Test successful file upload."""
        # Mock the upload URL response
        mock_client.execute_mutation.side_effect = [
            {
                "data": {
                    "getUploadUrl": {
                        "url": "https://example.com/upload",
                        "token": "upload_token_123",
                        "headers": {"Authorization": "Bearer token"},
                        "fields": {"key": "uploads/file.txt"},
                    }
                }
            },
            {
                "data": {
                    "completeUpload": sample_attachment_data
                }
            }
        ]

        # Mock the HTTP upload method directly
        with patch.object(attachments_manager, '_upload_file_content', new_callable=AsyncMock) as mock_upload:
            result = await attachments_manager.upload_file(
                temp_file,
                EntityType.TICKET,
                "ticket_456",
                description="Test file upload"
            )

            assert result.id == "attachment_123"
            assert result.filename == "test_document.pdf"
            assert mock_client.execute_mutation.call_count == 2
            mock_upload.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_file_not_found(self, attachments_manager):
        """Test upload with non-existent file."""
        with pytest.raises(FileNotFoundError):
            await attachments_manager.upload_file(
                "/non/existent/file.txt",
                EntityType.TICKET,
                "ticket_456"
            )

    @pytest.mark.asyncio
    async def test_upload_content_success(
        self, attachments_manager, mock_client, sample_attachment_data
    ):
        """Test successful content upload."""
        content = b"Test file content"
        filename = "test.txt"

        # Mock the upload URL response
        mock_client.execute_mutation.side_effect = [
            {
                "data": {
                    "getUploadUrl": {
                        "url": "https://example.com/upload",
                        "token": "upload_token_123",
                        "headers": {},
                        "fields": {},
                    }
                }
            },
            {
                "data": {
                    "completeUpload": sample_attachment_data
                }
            }
        ]

        # Mock the HTTP upload method directly
        with patch.object(attachments_manager, '_upload_file_content', new_callable=AsyncMock) as mock_upload:
            result = await attachments_manager.upload_content(
                content,
                filename,
                EntityType.TICKET,
                "ticket_456",
                description="Test content upload"
            )

            assert result.id == "attachment_123"
            assert mock_client.execute_mutation.call_count == 2
            mock_upload.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_content_validation_error(self, attachments_manager):
        """Test upload content validation errors."""
        with pytest.raises(SuperOpsValidationError, match="Content cannot be empty"):
            await attachments_manager.upload_content(
                b"",
                "test.txt",
                EntityType.TICKET,
                "ticket_456"
            )

        with pytest.raises(SuperOpsValidationError, match="Filename must be provided"):
            await attachments_manager.upload_content(
                b"content",
                "",
                EntityType.TICKET,
                "ticket_456"
            )

    @pytest.mark.asyncio
    async def test_download_attachment_success(self, attachments_manager, mock_client):
        """Test successful attachment download."""
        attachment_id = "attachment_123"
        expected_content = b"File content"

        # Mock download URL response
        mock_client.execute_query.return_value = {
            "data": {
                "getDownloadUrl": {
                    "url": "https://example.com/download/file.txt",
                    "expiresAt": "2024-01-01T01:00:00Z"
                }
            }
        }

        # Create a custom context manager for the response
        class MockResponse:
            def __init__(self, content):
                self.status = 200
                self.content = content
                
            async def read(self):
                return self.content
                
            async def __aenter__(self):
                return self
                
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
        
        # Create a custom context manager for the session
        class MockSession:
            def __init__(self, response):
                self.response = response
                
            def get(self, url):
                return self.response
                
            async def __aenter__(self):
                return self
                
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
        
        mock_response = MockResponse(expected_content)
        mock_session = MockSession(mock_response)
        
        with patch("py_superops.managers.attachments.aiohttp.ClientSession", return_value=mock_session):
            result = await attachments_manager.download_attachment(attachment_id)

            assert result == expected_content
            mock_client.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_download_attachment_validation_error(self, attachments_manager):
        """Test download validation error."""
        with pytest.raises(SuperOpsValidationError, match="Attachment ID must be a non-empty string"):
            await attachments_manager.download_attachment("")

    @pytest.mark.asyncio
    async def test_download_attachment_not_found(self, attachments_manager, mock_client):
        """Test download when attachment not found."""
        mock_client.execute_query.return_value = {
            "data": {
                "getDownloadUrl": None
            }
        }

        with pytest.raises(SuperOpsResourceNotFoundError):
            await attachments_manager.download_attachment("nonexistent")

    @pytest.mark.asyncio
    async def test_download_to_file_success(self, attachments_manager, mock_client):
        """Test successful download to file."""
        attachment_id = "attachment_123"
        expected_content = b"File content"

        # Mock download URL response
        mock_client.execute_query.return_value = {
            "data": {
                "getDownloadUrl": {
                    "url": "https://example.com/download/file.txt",
                    "expiresAt": "2024-01-01T01:00:00Z"
                }
            }
        }

        # Create a custom context manager for the response
        class MockResponse:
            def __init__(self, content):
                self.status = 200
                self.content = content
                
            async def read(self):
                return self.content
                
            async def __aenter__(self):
                return self
                
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
        
        # Create a custom context manager for the session
        class MockSession:
            def __init__(self, response):
                self.response = response
                
            def get(self, url):
                return self.response
                
            async def __aenter__(self):
                return self
                
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
        
        mock_response = MockResponse(expected_content)
        mock_session = MockSession(mock_response)
        
        with patch("py_superops.managers.attachments.aiohttp.ClientSession", return_value=mock_session):

            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = Path(temp_dir) / "downloaded.txt"
                result_path = await attachments_manager.download_to_file(attachment_id, file_path)

                assert result_path == file_path
                assert file_path.exists()
                assert file_path.read_bytes() == expected_content

    @pytest.mark.asyncio
    async def test_bulk_upload_success(
        self, attachments_manager, mock_client, sample_attachment_data
    ):
        """Test successful bulk upload."""
        # Create temporary files
        with tempfile.TemporaryDirectory() as temp_dir:
            file1 = Path(temp_dir) / "file1.txt"
            file2 = Path(temp_dir) / "file2.txt"
            file1.write_text("Content 1")
            file2.write_text("Content 2")

            # Mock upload_file method to return expected results
            async def mock_upload_file(path, entity_type, entity_id, description=None):
                from datetime import datetime
                filename = Path(path).name
                attachment_id = "attachment_1" if filename == "file1.txt" else "attachment_2"
                return Attachment(
                    id=attachment_id,
                    created_at=datetime.fromisoformat("2024-01-01T00:00:00+00:00"),
                    updated_at=datetime.fromisoformat("2024-01-01T00:00:00+00:00"),
                    filename=filename,
                    original_filename=filename,
                    file_size=len(Path(path).read_text()),
                    mime_type="text/plain",
                    entity_type=entity_type,
                    entity_id=entity_id,
                    url=f"https://example.com/files/{filename}",
                    description=description,
                    checksum="checksum123",
                    uploaded_by="user_123",
                    version=1
                )
            
            with patch.object(attachments_manager, 'upload_file', new_callable=AsyncMock) as mock_upload_file_method:
                mock_upload_file_method.side_effect = mock_upload_file
                result = await attachments_manager.bulk_upload(
                    [file1, file2],
                    EntityType.TICKET,
                    "ticket_456",
                    descriptions=["First file", "Second file"]
                )

                assert len(result) == 2
                assert result[0].id == "attachment_1"
                assert result[1].id == "attachment_2"
                # Should be called twice (once per file)
                assert mock_upload_file_method.call_count == 2

    @pytest.mark.asyncio
    async def test_bulk_upload_validation_error(self, attachments_manager):
        """Test bulk upload validation errors."""
        with pytest.raises(SuperOpsValidationError, match="File paths list cannot be empty"):
            await attachments_manager.bulk_upload(
                [],
                EntityType.TICKET,
                "ticket_456"
            )

        with pytest.raises(SuperOpsValidationError, match="Descriptions list must have same length"):
            await attachments_manager.bulk_upload(
                ["file1.txt", "file2.txt"],
                EntityType.TICKET,
                "ticket_456",
                descriptions=["Only one description"]
            )

    @pytest.mark.asyncio
    async def test_bulk_delete_success(self, attachments_manager, mock_client):
        """Test successful bulk delete."""
        attachment_ids = ["attachment_1", "attachment_2", "attachment_3"]

        # Mock delete responses - some succeed, one fails
        mock_client.execute_mutation.side_effect = [
            {"data": {"deleteAttachment": {"success": True, "message": "Deleted"}}},
            {"data": {"deleteAttachment": {"success": True, "message": "Deleted"}}},
            SuperOpsAPIError("Not found", 404, {})
        ]

        result = await attachments_manager.bulk_delete(attachment_ids)

        assert result["attachment_1"] is True
        assert result["attachment_2"] is True
        assert result["attachment_3"] is False

    @pytest.mark.asyncio
    async def test_get_attachment_history_success(self, attachments_manager, mock_client):
        """Test getting attachment history."""
        attachment_id = "attachment_123"
        history_data = [
            {
                "version": 1,
                "filename": "document_v1.pdf",
                "fileSize": 12345,
                "mimeType": "application/pdf",
                "description": "Initial version",
                "checksum": "abc123",
                "uploadedBy": "user_789",
                "uploadedByName": "John Doe",
                "createdAt": "2024-01-01T00:00:00Z"
            },
            {
                "version": 2,
                "filename": "document_v2.pdf",
                "fileSize": 15678,
                "mimeType": "application/pdf",
                "description": "Updated version",
                "checksum": "def456",
                "uploadedBy": "user_789",
                "uploadedByName": "John Doe",
                "createdAt": "2024-01-02T00:00:00Z"
            }
        ]

        mock_client.execute_query.return_value = {
            "data": {
                "attachmentHistory": history_data
            }
        }

        result = await attachments_manager.get_attachment_history(attachment_id)

        assert len(result) == 2
        assert result[0]["version"] == 1
        assert result[1]["version"] == 2
        mock_client.execute_query.assert_called_once()

    def test_detect_attachment_type(self, attachments_manager):
        """Test attachment type detection from MIME types."""
        assert attachments_manager._detect_attachment_type("image/jpeg") == AttachmentType.IMAGE
        assert attachments_manager._detect_attachment_type("video/mp4") == AttachmentType.VIDEO
        assert attachments_manager._detect_attachment_type("audio/mp3") == AttachmentType.AUDIO
        assert attachments_manager._detect_attachment_type("application/pdf") == AttachmentType.DOCUMENT
        assert attachments_manager._detect_attachment_type("application/vnd.ms-excel") == AttachmentType.SPREADSHEET
        assert attachments_manager._detect_attachment_type("application/vnd.ms-powerpoint") == AttachmentType.PRESENTATION
        assert attachments_manager._detect_attachment_type("application/zip") == AttachmentType.ARCHIVE
        assert attachments_manager._detect_attachment_type("text/x-python") == AttachmentType.CODE
        assert attachments_manager._detect_attachment_type("application/unknown") == AttachmentType.OTHER

    @pytest.mark.asyncio
    async def test_calculate_file_checksum(self, attachments_manager, temp_file):
        """Test file checksum calculation."""
        checksum = await attachments_manager._calculate_file_checksum(temp_file)
        assert isinstance(checksum, str)
        assert len(checksum) == 32  # MD5 hash length

    def test_build_queries(self, attachments_manager):
        """Test GraphQL query building methods."""
        # Test get query
        get_query = attachments_manager._build_get_query()
        assert "attachment(id: $id)" in get_query
        assert "AttachmentCoreFields" in get_query or "AttachmentFullFields" in get_query

        # Test list query
        list_query = attachments_manager._build_list_query()
        assert "attachments(" in list_query
        assert "pagination" in list_query

        # Test create mutation
        create_mutation = attachments_manager._build_create_mutation()
        assert "createAttachment" in create_mutation

        # Test update mutation
        update_mutation = attachments_manager._build_update_mutation()
        assert "updateAttachment" in update_mutation

        # Test delete mutation
        delete_mutation = attachments_manager._build_delete_mutation()
        assert "deleteAttachment" in delete_mutation

        # Test search query
        search_query = attachments_manager._build_search_query()
        assert "searchAttachments" in search_query

    def test_validation_methods(self, attachments_manager):
        """Test data validation methods."""
        # Test create data validation
        valid_create_data = {
            "filename": "test.pdf",
            "entity_type": "TICKET",
            "entity_id": "ticket_123"
        }
        result = attachments_manager._validate_create_data(valid_create_data)
        assert result["filename"] == "test.pdf"

        # Test validation errors
        with pytest.raises(SuperOpsValidationError, match="Filename is required"):
            attachments_manager._validate_create_data({})

        with pytest.raises(SuperOpsValidationError, match="Invalid entity type"):
            attachments_manager._validate_create_data({
                "filename": "test.pdf",
                "entity_type": "INVALID",
                "entity_id": "123"
            })

        # Test update data validation
        update_data = {"attachment_type": "DOCUMENT"}
        result = attachments_manager._validate_update_data(update_data)
        assert result["attachment_type"] == "DOCUMENT"

        with pytest.raises(SuperOpsValidationError, match="Invalid attachment type"):
            attachments_manager._validate_update_data({"attachment_type": "INVALID"})