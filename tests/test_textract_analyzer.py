#!/usr/bin/env python
"""
Unit tests for textract_analyzer.py
====================================
Tests the Textract text extraction functionality using pytest and mocking.
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from textract_analyzer import extract_text_simple, extract_text_from_document


class TestTextractAnalyzer:
    """Test cases for Textract text extraction functionality."""
    
    @patch('textract_analyzer.textract_client')
    def test_extract_text_simple_success(self, mock_textract_client):
        """Test successful text extraction from document."""
        # Setup mock response
        mock_textract_client.detect_document_text.return_value = {
            'Blocks': [
                {'BlockType': 'LINE', 'Text': 'Hello World'},
                {'BlockType': 'LINE', 'Text': 'This is a test document'},
                {'BlockType': 'WORD', 'Text': 'Hello'}  # Should be ignored
            ]
        }
        
        # Test
        result = extract_text_simple(
            bucket_name='test-bucket',
            document_name='test.pdf'
        )
        
        # Assert
        assert result is not None
        assert 'Hello World' in result
        assert 'This is a test document' in result
        assert 'Hello' not in result  # WORD blocks should not be included
        
    @patch('textract_analyzer.textract_client')
    def test_extract_text_simple_empty_document(self, mock_textract_client):
        """Test text extraction from empty document."""
        # Setup mock response with no text
        mock_textract_client.detect_document_text.return_value = {
            'Blocks': []
        }
        
        # Test
        result = extract_text_simple(
            bucket_name='test-bucket',
            document_name='empty.pdf'
        )
        
        # Assert
        assert result == ""
        
    @patch('textract_analyzer.textract_client')
    def test_extract_text_from_document_success(self, mock_textract_client):
        """Test full document analysis with tables and forms."""
        # Setup mock response
        mock_textract_client.analyze_document.return_value = {
            'Blocks': [
                {'BlockType': 'LINE', 'Text': 'Table data'},
                {'BlockType': 'TABLE', 'Text': ''}
            ]
        }
        
        # Test
        result = extract_text_from_document(
            bucket_name='test-bucket',
            document_name='test.pdf',
            feature_types=['TABLES', 'FORMS']
        )
        
        # Assert
        assert result is not None
        assert 'Table data' in str(result)
        
    @patch('textract_analyzer.textract_client')
    def test_extract_text_client_error(self, mock_textract_client):
        """Test handling of AWS client errors."""
        from botocore.exceptions import ClientError
        
        # Setup mock to raise error
        mock_textract_client.detect_document_text.side_effect = ClientError(
            {'Error': {'Code': 'InvalidParameter', 'Message': 'Invalid file type'}},
            'DetectDocumentText'
        )
        
        # Test
        result = extract_text_simple(
            bucket_name='test-bucket',
            document_name='invalid.txt'
        )
        
        # Assert
        assert result is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])