"""
Unit tests for src/services/text_extraction.py.
"""

import pytest
from botocore.exceptions import ClientError

from services.text_extraction import extract_lines, extract_text, parse_text_blocks


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


class TestParseTextBlocks:
    """Test cases for the parse_text_blocks helper."""

    def test_parse_returns_lines_with_confidence(self):
        """Test that LINE blocks are returned with text and confidence."""
        response = {
            "Blocks": [
                {"BlockType": "LINE", "Text": "Hello World", "Confidence": 99.5},
                {"BlockType": "LINE", "Text": "This is a test", "Confidence": 98.2},
                {"BlockType": "WORD", "Text": "ignored"},
            ]
        }

        result = parse_text_blocks(response)

        assert result == [
            {"text": "Hello World", "confidence": 99.5},
            {"text": "This is a test", "confidence": 98.2},
        ]

    def test_parse_empty_blocks_returns_empty_list(self):
        """Test that an empty Blocks list returns an empty list."""
        assert parse_text_blocks({"Blocks": []}) == []

    def test_parse_skips_blocks_without_text(self):
        """Test that LINE blocks missing Text are skipped."""
        response = {
            "Blocks": [
                {"BlockType": "LINE", "Text": "", "Confidence": 90.0},
                {"BlockType": "LINE", "Text": "Only one line", "Confidence": 95.0},
                {"BlockType": "LINE"},
            ]
        }

        result = parse_text_blocks(response)

        assert result == [{"text": "Only one line", "confidence": 95.0}]

    def test_parse_missing_blocks_key_returns_empty_list(self):
        """Test that a response without a Blocks key returns an empty list."""
        assert parse_text_blocks({}) == []

    def test_parse_ignores_non_line_blocks(self):
        """Test that only LINE blocks are extracted."""
        response = {
            "Blocks": [
                {"BlockType": "WORD", "Text": "word1", "Confidence": 90.0},
                {"BlockType": "TABLE", "Text": "table", "Confidence": 80.0},
                {"BlockType": "LINE", "Text": "line1", "Confidence": 99.9},
            ]
        }

        result = parse_text_blocks(response)

        assert result == [{"text": "line1", "confidence": 99.9}]

    def test_parse_rounds_confidence_to_two_decimals(self):
        """Test that confidence is rounded to 2 decimal places."""
        response = {
            "Blocks": [
                {"BlockType": "LINE", "Text": "test", "Confidence": 99.567},
            ]
        }

        result = parse_text_blocks(response)

        assert result[0]["confidence"] == 99.57

    def test_parse_defaults_confidence_to_zero(self):
        """Test that missing Confidence defaults to 0.0."""
        response = {
            "Blocks": [
                {"BlockType": "LINE", "Text": "test"},
            ]
        }

        result = parse_text_blocks(response)

        assert result[0]["confidence"] == 0.0


class TestExtractLines:
    """Test cases for the extract_lines helper."""

    def test_extract_lines_returns_lines_with_confidence(self, mock_textract_client):
        """Test that extract_lines returns structured line data."""
        mock_textract_client.detect_document_text.return_value = {
            "Blocks": [
                {"BlockType": "LINE", "Text": "Hello World", "Confidence": 99.5},
                {"BlockType": "LINE", "Text": "This is a test document", "Confidence": 98.2},
                {"BlockType": "WORD", "Text": "ignored"},
            ]
        }

        result = extract_lines("test-bucket", "test.pdf")

        assert result == [
            {"text": "Hello World", "confidence": 99.5},
            {"text": "This is a test document", "confidence": 98.2},
        ]

    def test_extract_lines_empty_document(self, mock_textract_client):
        """Test that empty documents return an empty list."""
        mock_textract_client.detect_document_text.return_value = {"Blocks": []}

        result = extract_lines("test-bucket", "empty.pdf")

        assert result == []

    def test_extract_lines_skips_blocks_without_text(self, mock_textract_client):
        """Test that LINE blocks missing Text are skipped."""
        mock_textract_client.detect_document_text.return_value = {
            "Blocks": [
                {"BlockType": "LINE", "Text": "", "Confidence": 90.0},
                {"BlockType": "LINE", "Text": "Only one line", "Confidence": 95.0},
                {"BlockType": "LINE"},
            ]
        }

        result = extract_lines("test-bucket", "test.pdf")

        assert result == [{"text": "Only one line", "confidence": 95.0}]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
