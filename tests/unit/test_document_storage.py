"""
Unit tests for src/services/document_storage.py.
"""

import datetime

import pytest
from botocore.exceptions import ClientError

from services import document_storage
from services.document_storage import (
    _build_metadata,
    _get_content_type,
    store_document,
)


class TestGetContentType:
    """Test cases for content-type mapping."""

    @pytest.mark.parametrize(
        "filename,expected",
        [
            ("document.pdf", "application/pdf"),
            ("image.PNG", "image/png"),
            ("photo.JPG", "image/jpeg"),
            ("scan.tiff", "image/tiff"),
            ("file.JPEG", "image/jpeg"),
        ],
    )
    def test_known_extensions(self, filename, expected):
        assert _get_content_type(filename) == expected

    def test_unknown_extension_defaults_to_octet_stream(self):
        assert _get_content_type("file.unknown") == "application/octet-stream"

    def test_no_extension_defaults_to_octet_stream(self):
        assert _get_content_type("noextension") == "application/octet-stream"

    def test_empty_filename_defaults_to_octet_stream(self):
        assert _get_content_type("") == "application/octet-stream"

    def test_multiple_dots_uses_last_extension(self):
        assert _get_content_type("archive.tar.pdf") == "application/pdf"

    def test_hidden_file_without_extension_defaults_to_octet_stream(self):
        assert _get_content_type(".gitignore") == "application/octet-stream"

    def test_dot_at_end_defaults_to_octet_stream(self):
        assert _get_content_type("weird.") == "application/octet-stream"


class TestBuildMetadata:
    """Test cases for metadata builder."""

    def test_metadata_contains_upload_timestamp(self):
        metadata = _build_metadata("report.pdf")
        assert "upload-timestamp" in metadata
        assert "T" in metadata["upload-timestamp"]

    def test_metadata_timestamp_is_iso_8601_utc(self):
        """Test that the upload timestamp is a valid ISO 8601 UTC string."""
        metadata = _build_metadata("report.pdf")
        timestamp = metadata["upload-timestamp"]
        parsed = datetime.datetime.fromisoformat(timestamp)
        assert parsed.tzinfo == datetime.timezone.utc

    def test_metadata_contains_original_filename(self):
        metadata = _build_metadata("report.pdf")
        assert metadata["original-filename"] == "report.pdf"

    def test_metadata_contains_unicode_filename(self):
        metadata = _build_metadata("résumé_文档.pdf")
        assert metadata["original-filename"] == "résumé_文档.pdf"


class TestStoreDocument:
    """Test cases for the S3 document storage service."""

    def test_store_document_success(self, mock_s3_client):
        """Test successful document upload with metadata and content type."""
        store_document("test-bucket", "test.pdf", b"file content")

        mock_s3_client.put_object.assert_called_once()
        call_kwargs = mock_s3_client.put_object.call_args.kwargs
        assert call_kwargs["Bucket"] == "test-bucket"
        assert call_kwargs["Key"] == "test.pdf"
        assert call_kwargs["Body"] == b"file content"

    def test_store_document_includes_content_type(self, mock_s3_client):
        """Test that the correct ContentType is set on the S3 object."""
        store_document("test-bucket", "report.pdf", b"content")

        call_kwargs = mock_s3_client.put_object.call_args.kwargs
        assert call_kwargs["ContentType"] == "application/pdf"

    def test_store_document_includes_metadata(self, mock_s3_client):
        """Test that upload-timestamp and original-filename metadata are set."""
        store_document(
            "test-bucket",
            "report.pdf",
            b"content",
            original_filename="report.pdf",
        )

        call_kwargs = mock_s3_client.put_object.call_args.kwargs
        metadata = call_kwargs["Metadata"]
        assert "upload-timestamp" in metadata
        assert metadata["original-filename"] == "report.pdf"

    def test_store_document_no_encryption_params(self, mock_s3_client):
        """Test that no per-request encryption parameters are passed."""
        store_document("test-bucket", "test.pdf", b"content")

        call_kwargs = mock_s3_client.put_object.call_args.kwargs
        assert "ServerSideEncryption" not in call_kwargs
        assert "SSEKMSKeyId" not in call_kwargs

    def test_store_document_content_type_for_images(self, mock_s3_client):
        """Test that image files get the correct content type."""
        store_document("test-bucket", "photo.png", b"content")

        call_kwargs = mock_s3_client.put_object.call_args.kwargs
        assert call_kwargs["ContentType"] == "image/png"

    def test_store_document_defaults_original_filename_to_key(self, mock_s3_client):
        """Test that original_filename defaults to the key when not provided."""
        store_document("test-bucket", "scan.tiff", b"content")

        call_kwargs = mock_s3_client.put_object.call_args.kwargs
        assert call_kwargs["Metadata"]["original-filename"] == "scan.tiff"

    def test_store_document_original_filename_differs_from_key(self, mock_s3_client):
        """Test that metadata uses original_filename when it differs from key."""
        store_document(
            "test-bucket",
            "uuid-1234.pdf",
            b"content",
            original_filename="my-document.pdf",
        )

        call_kwargs = mock_s3_client.put_object.call_args.kwargs
        assert call_kwargs["Key"] == "uuid-1234.pdf"
        assert call_kwargs["Metadata"]["original-filename"] == "my-document.pdf"
        assert call_kwargs["ContentType"] == "application/pdf"

    def test_store_document_large_binary_body(self, mock_s3_client):
        """Test storing a large (10MB) binary document body."""
        large_content = b"\x00\x01\x02" * 3_500_000  # ~10.5 MB
        store_document("test-bucket", "large.pdf", large_content)

        call_kwargs = mock_s3_client.put_object.call_args.kwargs
        assert call_kwargs["Body"] == large_content

    def test_store_document_unicode_filename(self, mock_s3_client):
        """Test that unicode filenames are handled correctly."""
        store_document("test-bucket", "résumé.pdf", b"content")

        call_kwargs = mock_s3_client.put_object.call_args.kwargs
        assert call_kwargs["Key"] == "résumé.pdf"
        assert call_kwargs["ContentType"] == "application/pdf"

    def test_store_document_client_error(self, mock_s3_client):
        """Test that ClientError propagates to the caller."""
        mock_s3_client.put_object.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Denied"}},
            "PutObject",
        )

        with pytest.raises(ClientError):
            store_document("test-bucket", "test.pdf", b"content")

    def test_store_document_empty_body(self, mock_s3_client):
        """Test storing an empty document body."""
        store_document("test-bucket", "empty.pdf", b"")

        mock_s3_client.put_object.assert_called_once()
        call_kwargs = mock_s3_client.put_object.call_args.kwargs
        assert call_kwargs["Body"] == b""


class TestS3ClientNotInitialized:
    """Test cases when the boto3 S3 client fails to initialize."""

    def test_store_document_raises_runtime_error(self, monkeypatch):
        """Test that store_document raises RuntimeError when s3_client is None."""
        monkeypatch.setattr(document_storage, "s3_client", None)

        with pytest.raises(RuntimeError, match="S3 client not initialized"):
            store_document("test-bucket", "test.pdf", b"content")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])