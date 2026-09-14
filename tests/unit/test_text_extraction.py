"""
Unit tests for src/services/text_extraction.py (Textract text extraction).
"""

import pytest

from services.text_extraction import (
    extract_lines,
    extract_text,
    parse_text_blocks,
)


class TestExtractText:
    """Test cases for the extract_text function."""

    def test_extract_text_success(self, mock_textract_client):
        """Test successful text extraction with default (detect_document_text)."""
        mock_textract_client.detect_document_text.return_value = {"Blocks": []}

        result = extract_text(b"fake document content")

        assert result == {"Blocks": []}
        mock_textract_client.detect_document_text.assert_called_once_with(
            Document={"Bytes": b"fake document content"}
        )
        mock_textract_client.analyze_document.assert_not_called()

    def test_extract_text_with_feature_types(self, mock_textract_client):
        """Test that feature_types triggers analyze_document."""
        mock_textract_client.analyze_document.return_value = {"Blocks": []}

        result = extract_text(b"fake document content", feature_types=["TABLES"])

        assert result == {"Blocks": []}
        mock_textract_client.analyze_document.assert_called_once_with(
            Document={"Bytes": b"fake document content"},
            FeatureTypes=["TABLES"],
        )
        mock_textract_client.detect_document_text.assert_not_called()

    def test_extract_text_runtime_error(self, monkeypatch):
        """Test that extract_text raises RuntimeError when textract_client is None."""
        from services import text_extraction

        monkeypatch.setattr(text_extraction, "textract_client", None)

        with pytest.raises(RuntimeError, match="Textract client not initialized"):
            extract_text(b"fake document content")


class TestParseTextBlocks:
    """Test cases for the parse_text_blocks helper."""

    def test_parse_text_blocks_returns_lines_with_confidence(self):
        """Test that parse_text_blocks returns structured line data."""
        response = {
            "Blocks": [
                {"BlockType": "LINE", "Text": "Hello World", "Confidence": 99.5},
                {"BlockType": "LINE", "Text": "This is a test document", "Confidence": 98.2},
                {"BlockType": "WORD", "Text": "ignored"},
            ]
        }

        result = parse_text_blocks(response)

        assert result == [
            {"text": "Hello World", "confidence": 99.5},
            {"text": "This is a test document", "confidence": 98.2},
        ]

    def test_parse_text_blocks_empty_response(self):
        """Test that empty responses return an empty list."""
        assert parse_text_blocks({"Blocks": []}) == []

    def test_parse_text_blocks_skips_blocks_without_text(self):
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

        result = extract_lines(b"fake document content")

        assert result == [
            {"text": "Hello World", "confidence": 99.5},
            {"text": "This is a test document", "confidence": 98.2},
        ]

    def test_extract_lines_empty_document(self, mock_textract_client):
        """Test that empty documents return an empty list."""
        mock_textract_client.detect_document_text.return_value = {"Blocks": []}

        result = extract_lines(b"empty content")

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

        result = extract_lines(b"document content")

        assert result == [{"text": "Only one line", "confidence": 95.0}]

    def test_extract_lines_uses_realistic_response(
        self, mock_textract_client, textract_response
    ):
        """Test end-to-end extract_lines with a realistic Textract response."""
        mock_textract_client.detect_document_text.return_value = textract_response

        result = extract_lines(b"fake document content")

        assert result == [
            {"text": "Hello World", "confidence": 99.5},
            {"text": "This is a test document", "confidence": 98.2},
        ]
        mock_textract_client.detect_document_text.assert_called_once_with(
            Document={"Bytes": b"fake document content"}
        )

    def test_extract_lines_passes_document_to_textract(self, mock_textract_client):
        """Test that the correct Document payload (Bytes) is sent to Textract."""
        mock_textract_client.detect_document_text.return_value = {"Blocks": []}

        extract_lines(b"my document content")

        mock_textract_client.detect_document_text.assert_called_once_with(
            Document={"Bytes": b"my document content"}
        )

    def test_extract_lines_runtime_error(self, monkeypatch):
        """Test that extract_lines raises RuntimeError when textract_client is None."""
        from services import text_extraction

        monkeypatch.setattr(text_extraction, "textract_client", None)

        with pytest.raises(RuntimeError, match="Textract client not initialized"):
            extract_lines(b"document content")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
