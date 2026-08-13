"""
Unit tests for src/app.py (Lambda handler).
"""

import json
from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError

import app


def _make_event(body: str | None = "SGVsbG8gV29ybGQ=", headers: dict | None = None) -> dict:
    """Build a minimal API Gateway event."""
    event = {}
    if body is not None:
        event["body"] = body
    if headers:
        event["headers"] = headers
    return event


class TestLambdaHandler:
    """Test cases for the Lambda handler."""

    @patch("app.extract_lines")
    @patch("app.store_document")
    def test_success_with_custom_filename(self, mock_store, mock_extract):
        """Test successful processing with a filename header."""
        mock_extract.return_value = [
            {"text": "Hello World", "confidence": 99.5},
            {"text": "This is a test", "confidence": 98.2},
        ]
        event = _make_event(headers={"filename": "report.pdf"})

        result = app.lambda_handler(event, context=None)

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["filename"] == "report.pdf"
        assert body["status"] == "success"
        assert "processingTime" in body
        assert body["text"] == "Hello World\nThis is a test"
        assert body["lines"] == [
            {"text": "Hello World", "confidence": 99.5},
            {"text": "This is a test", "confidence": 98.2},
        ]
        mock_store.assert_called_once_with(
            app.BUCKET_NAME,
            "report.pdf",
            b"Hello World",
            original_filename="report.pdf",
        )
        mock_extract.assert_called_once_with(app.BUCKET_NAME, "report.pdf")

    @patch("app.extract_lines")
    @patch("app.store_document")
    def test_success_with_default_filename(self, mock_store, mock_extract):
        """Test successful processing without a filename header."""
        mock_extract.return_value = [{"text": "Content", "confidence": 95.0}]
        event = _make_event()

        result = app.lambda_handler(event, context=None)

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["filename"] == "uploaded_document.pdf"
        assert body["status"] == "success"
        assert "processingTime" in body
        assert body["text"] == "Content"
        assert body["lines"] == [{"text": "Content", "confidence": 95.0}]
        mock_store.assert_called_once_with(
            app.BUCKET_NAME,
            "uploaded_document.pdf",
            b"Hello World",
            original_filename="uploaded_document.pdf",
        )

    def test_missing_body_returns_400(self):
        """Test that a request with no body returns 400."""
        result = app.lambda_handler({}, context=None)

        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert body["status"] == "error"
        assert "No file provided" in body["message"]

    def test_invalid_base64_returns_400(self):
        """Test that a malformed base64 body returns 400."""
        result = app.lambda_handler(_make_event("!!!not-valid-base64!!!"), context=None)

        assert result["statusCode"] == 400

    @patch("app.store_document")
    @pytest.mark.parametrize(
        "error_code,expected_status",
        [
            ("AccessDenied", 403),
            ("InvalidParameter", 400),
            ("EntityTooLarge", 413),
            ("NoSuchBucket", 404),
            ("Throttling", 429),
            ("ServiceUnavailable", 503),
            ("SomeUnknownCode", 500),
        ],
    )
    def test_client_error_maps_to_http_status(
        self, mock_store, error_code, expected_status
    ):
        """Test that AWS service errors map to meaningful HTTP status codes."""
        mock_store.side_effect = ClientError(
            {"Error": {"Code": error_code, "Message": "Message"}},
            "PutObject",
        )

        result = app.lambda_handler(_make_event(), context=None)

        assert result["statusCode"] == expected_status
        body = json.loads(result["body"])
        assert f"AWS Error: {error_code}" in body["error"]

    @patch("app.store_document")
    def test_client_error_returns_message(self, mock_store):
        """Test that AWS service errors include the service message."""
        mock_store.side_effect = ClientError(
            {"Error": {"Code": "Throttling", "Message": "Rate exceeded"}},
            "PutObject",
        )

        result = app.lambda_handler(_make_event(), context=None)

        assert result["statusCode"] == 429
        body = json.loads(result["body"])
        assert body["message"] == "Rate exceeded"

    @patch("app.extract_lines")
    @patch("app.store_document")
    def test_textract_bad_document_maps_to_422(self, mock_store, mock_extract):
        """Test that a Textract BadDocumentException returns 422."""
        mock_extract.side_effect = ClientError(
            {"Error": {"Code": "BadDocumentException", "Message": "Bad document"}},
            "DetectDocumentText",
        )

        result = app.lambda_handler(_make_event(), context=None)

        assert result["statusCode"] == 422
        body = json.loads(result["body"])
        assert "BadDocumentException" in body["error"]

    @patch("app.extract_lines")
    @patch("app.store_document")
    def test_textract_unsupported_document_maps_to_415(self, mock_store, mock_extract):
        """Test that a Textract UnsupportedDocumentException returns 415."""
        mock_extract.side_effect = ClientError(
            {"Error": {"Code": "UnsupportedDocumentException", "Message": "Unsupported type"}},
            "DetectDocumentText",
        )

        result = app.lambda_handler(_make_event(), context=None)

        assert result["statusCode"] == 415
        body = json.loads(result["body"])
        assert "UnsupportedDocumentException" in body["error"]

    @patch("app.extract_lines")
    @patch("app.store_document")
    def test_unexpected_error_returns_500(self, mock_store, mock_extract):
        """Test that unexpected exceptions return 500."""
        mock_extract.side_effect = RuntimeError("boom")

        result = app.lambda_handler(_make_event(), context=None)

        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert body["error"] == "Internal error"

    def test_response_has_cors_headers(self):
        """Test that responses include CORS headers."""
        result = app.lambda_handler({}, context=None)

        assert result["headers"]["Access-Control-Allow-Origin"] == "*"
        assert result["headers"]["Content-Type"] == "application/json"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
