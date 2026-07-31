"""
Unit tests for src/services/document_storage.py.
"""

import pytest
from botocore.exceptions import ClientError

from services.document_storage import store_document


class TestStoreDocument:
    """Test cases for the S3 document storage service."""

    def test_store_document_success(self, mock_s3_client):
        """Test successful document upload."""
        store_document("test-bucket", "test.pdf", b"file content")

        mock_s3_client.put_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="test.pdf",
            Body=b"file content",
        )

    def test_store_document_with_kms(self, mock_s3_client):
        """Test document upload with KMS encryption."""
        kms_key = "arn:aws:kms:us-east-1:123456789012:key/abc123"
        store_document("test-bucket", "test.pdf", b"content", kms_key_id=kms_key)

        mock_s3_client.put_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="test.pdf",
            Body=b"content",
            ServerSideEncryption="aws:kms",
            SSEKMSKeyId=kms_key,
        )

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

        mock_s3_client.put_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="empty.pdf",
            Body=b"",
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])