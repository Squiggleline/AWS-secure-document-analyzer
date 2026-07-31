"""
Unit tests for src/services/text_extraction.py.
"""

import pytest
from botocore.exceptions import ClientError

from services.text_extraction import extract_lines, extract_text


class TestExtractText:
    """Test cases for the Textract text extraction service."""

    def test_extract_text_simple(self, mock_textract_client):
        """Test detect_document_text path."""
        mock_textract_client.detect_document_text.return_value = {"Blocks": []}

        result = extract_text("test-bucket", "test.pdf")

        mock_textract_client.detect_document_text.assert_called_once_with(
            Document={"S3Object": {"Bucket": "test-bucket", "Name": "test.pdf"}}
        )
        mock_textract_client.analyze_document.assert_not_called()
        assert result == {"Blocks": []}

    def test_extract_text_with_features(self, mock_textract_client):
        """Test analyze_document path with feature types."""
        mock_textract_client.analyze_document.return_value = {"Blocks": []}

        result = extract_text(
            "test-bucket", "test.pdf", feature_types=["TABLES", "FORMS"]
        )

        mock_textract_client.analyze_document.assert_called_once_with(
            Document={"S3Object": {"Bucket": "test-bucket", "Name": "test.pdf"}},
            FeatureTypes=["TABLES", "FORMS"],
        )
        mock_textract_client.detect_document_text.assert_not_called()
        assert result == {"Blocks": []}

    def test_extract_text_client_error(self, mock_textract_client):
        """Test that ClientError propagates."""
        mock_textract_client.detect_document_text.side_effect = ClientError(
            {"Error": {"Code": "InvalidParameter", "Message": "Bad file"}},
            "DetectDocumentText",
        )

        with pytest.raises(ClientError):
            extract_text("test-bucket", "invalid.txt")


class TestExtractLines:
    """Test cases for the extract_lines helper."""

    def test_extract_lines_returns_joined_line_blocks(self, mock_textract_client):
        """Test that LINE blocks are joined with newlines."""
        mock_textract_client.detect_document_text.return_value = {
            "Blocks": [
                {"BlockType": "LINE", "Text": "Hello World"},
                {"BlockType": "LINE", "Text": "This is a test document"},
                {"BlockType": "WORD", "Text": "ignored"},
            ]
        }

        result = extract_lines("test-bucket", "test.pdf")

        assert result == "Hello World\nThis is a test document"

    def test_extract_lines_empty_document(self, mock_textract_client):
        """Test that empty documents return an empty string."""
        mock_textract_client.detect_document_text.return_value = {"Blocks": []}

        result = extract_lines("test-bucket", "empty.pdf")

        assert result == ""

    def test_extract_lines_skips_blocks_without_text(self, mock_textract_client):
        """Test that LINE blocks missing Text are skipped."""
        mock_textract_client.detect_document_text.return_value = {
            "Blocks": [
                {"BlockType": "LINE", "Text": ""},
                {"BlockType": "LINE", "Text": "Only one line"},
                {"BlockType": "LINE"},
            ]
        }

        result = extract_lines("test-bucket", "test.pdf")

        assert result == "Only one line"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])