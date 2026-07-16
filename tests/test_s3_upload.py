#!/usr/bin/env python
"""
Unit tests for s3_upload.py
=============================
Tests the S3 upload functionality using pytest and moto for mocking.
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from s3_upload import upload_document


class TestS3Upload:
    """Test cases for S3 upload functionality."""
    
    @patch('s3_upload.s3_client')
    def test_upload_document_success(self, mock_s3_client):
        """Test successful file upload to S3."""
        # Setup mock
        mock_s3_client.upload_file.return_value = None
        
        # Test
        result = upload_document(
            file_path='test_document.pdf',
            bucket_name='test-bucket',
            object_name='test.pdf'
        )
        
        # Assert
        assert result is True
        mock_s3_client.upload_file.assert_called_once()
        
    @patch('s3_upload.s3_client')
    def test_upload_document_with_kms(self, mock_s3_client):
        """Test file upload with KMS encryption."""
        # Setup mock
        mock_s3_client.upload_file.return_value = None
        
        # Test
        result = upload_document(
            file_path='test_document.pdf',
            bucket_name='test-bucket',
            object_name='test.pdf',
            kms_key_id='arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012'
        )
        
        # Assert
        assert result is True
        mock_s3_client.upload_file.assert_called_once()
        
        # Check that KMS encryption was included
        call_args = mock_s3_client.upload_file.call_args
        assert 'ExtraArgs' in call_args[1]
        assert call_args[1]['ExtraArgs']['ServerSideEncryption'] == 'aws:kms'
        
    @patch('s3_upload.s3_client')
    def test_upload_document_file_not_found(self, mock_s3_client):
        """Test handling of missing file."""
        # Test with non-existent file
        result = upload_document(
            file_path='nonexistent.pdf',
            bucket_name='test-bucket'
        )
        
        # Assert
        assert result is False
        
    @patch('s3_upload.s3_client')
    def test_upload_document_client_error(self, mock_s3_client):
        """Test handling of AWS client errors."""
        from botocore.exceptions import ClientError
        
        # Setup mock to raise error
        mock_s3_client.upload_file.side_effect = ClientError(
            {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
            'UploadPart'
        )
        
        # Test
        result = upload_document(
            file_path='test_document.pdf',
            bucket_name='test-bucket'
        )
        
        # Assert
        assert result is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])