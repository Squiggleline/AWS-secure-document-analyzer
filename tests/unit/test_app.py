"""
Unit tests for src/app.py (Lambda handler).
"""

import base64
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
        mock_extract.return_value = "Hello World\nThis is a test"
        event = _make_event(headers={"filename": "report.pdf"})

        result = app.lambda_handler(event, context=None)

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["filename"] == "report.pdf"
        assert body["extracted_text"] == "Hello World\nThis is a test"
        mock_store.assert_called_once_with(
            app.BUCKET_NAME, "report.pdf", b"Hello World"
        )
        mock_extract.assert_called_once_with(app.BUCKET_NAME, "report.pdf")

    @patch("app.extract_lines")
    @patch("app.store_document")
    def test_success_with_default_filename(self, mock_store, mock_extract):
        """Test successful processing without a filename header."""
        mock_extract.return_value = "Content"
        event = _make_event()

        result = app.lambda_handler(event, context=None)

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["filename"] == "uploaded_document.pdf"
        mock_store.assert_called_once_with(
            app.BUCKET_NAME, "uploaded_document.pdf", b"Hello World"
        )

    def test_missing_body_returns_400(self):
        """Test that a request with no body returns 400."""
        result = app.lambda_handler({}, context=None)

        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert "No file provided" in body["message"]

    def test_invalid_base64_returns_400(self):
        """Test that a malformed base64 body returns 400."""
        result = app.lambda_handler(_make_event("!!!not-valid-base64!!!"), context=None)

        assert result["statusCode"] == 400

    @patch("app.store_document")
    def test_client_error_returns_500(self, mock_store):
        """Test that AWS service errors return 500 with error details."""
        mock_store.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
            "PutObject",
        )

        result = app.lambda_handler(_make_event(), context=None)

        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert "AWS Error: AccessDenied" in body["error"]

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