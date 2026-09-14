"""
Unit tests for src/app.py (Lambda handler).
"""

import json
from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError

import app


class TestLambdaHandler:
    """Test cases for the Lambda handler."""

    @patch("app.extract_lines")
    @patch("app.store_document")
    def test_success_with_custom_filename(
        self, mock_store, mock_extract, api_gateway_event
    ):
        """Test successful processing with a filename header."""
        mock_extract.return_value = [
            {"text": "Hello World", "confidence": 99.5},
            {"text": "This is a test", "confidence": 98.2},
        ]
        event = api_gateway_event(filename="report.pdf")

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
    def test_success_with_default_filename(self, mock_store, mock_extract, api_gateway_event):
        """Test successful processing without a filename header."""
        mock_extract.return_value = [{"text": "Content", "confidence": 95.0}]
        event = api_gateway_event(filename=None)

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

    @patch("app.extract_lines")
    @patch("app.store_document")
    def test_full_event_structure_processed(
        self, mock_store, mock_extract, api_gateway_event
    ):
        """Test that a fully populated API Gateway event is handled."""
        mock_extract.return_value = [{"text": "scanned text", "confidence": 97.0}]
        event = api_gateway_event(
            body=b"Sample document content",
            filename="scan.pdf",
            http_method="POST",
            path="/document",
            request_id="custom-request-id-42",
        )

        result = app.lambda_handler(event, context=None)

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["filename"] == "scan.pdf"
        assert body["status"] == "success"
        assert body["text"] == "scanned text"
        mock_store.assert_called_once_with(
            app.BUCKET_NAME,
            "scan.pdf",
            b"Sample document content",
            original_filename="scan.pdf",
        )
        mock_extract.assert_called_once_with(app.BUCKET_NAME, "scan.pdf")

    def test_missing_body_returns_400(self, api_gateway_event):
        """Test that a request with no body returns 400."""
        event = api_gateway_event(body=None)
        result = app.lambda_handler(event, context=None)

        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert body["status"] == "error"
        assert body["error"] == "InvalidRequest"
        assert "No file provided" in body["message"]
        assert "processingTime" in body
        assert body["filename"] is None

    def test_invalid_base64_returns_400(self, api_gateway_event):
        """Test that a malformed base64 body returns 400."""
        event = api_gateway_event(body=b"!!!not-valid-base64!!!")
        event["body"] = "!!!not-valid-base64!!!"  # override with raw invalid base64
        result = app.lambda_handler(event, context=None)

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
        self, mock_store, api_gateway_event, error_code, expected_status
    ):
        """Test that AWS service errors map to meaningful HTTP status codes."""
        mock_store.side_effect = ClientError(
            {"Error": {"Code": error_code, "Message": "Message"}},
            "PutObject",
        )

        result = app.lambda_handler(api_gateway_event(), context=None)

        assert result["statusCode"] == expected_status
        body = json.loads(result["body"])
        assert body["error"] == error_code
        assert body["status"] == "error"
        assert "processingTime" in body
        assert body["filename"] is None

    @patch("app.store_document")
    def test_client_error_returns_message(self, mock_store, api_gateway_event):
        """Test that AWS service errors include the service message."""
        mock_store.side_effect = ClientError(
            {"Error": {"Code": "Throttling", "Message": "Rate exceeded"}},
            "PutObject",
        )

        result = app.lambda_handler(api_gateway_event(), context=None)

        assert result["statusCode"] == 429
        body = json.loads(result["body"])
        assert body["message"] == "Rate exceeded"

    @patch("app.extract_lines")
    @patch("app.store_document")
    def test_textract_bad_document_maps_to_422(
        self, mock_store, mock_extract, api_gateway_event
    ):
        """Test that a Textract BadDocumentException returns 422."""
        mock_extract.side_effect = ClientError(
            {"Error": {"Code": "BadDocumentException", "Message": "Bad document"}},
            "DetectDocumentText",
        )

        result = app.lambda_handler(api_gateway_event(), context=None)

        assert result["statusCode"] == 422
        body = json.loads(result["body"])
        assert body["error"] == "BadDocumentException"
        assert body["status"] == "error"

    @patch("app.extract_lines")
    @patch("app.store_document")
    def test_textract_unsupported_document_maps_to_415(
        self, mock_store, mock_extract, api_gateway_event
    ):
        """Test that a Textract UnsupportedDocumentException returns 415."""
        mock_extract.side_effect = ClientError(
            {"Error": {"Code": "UnsupportedDocumentException", "Message": "Unsupported type"}},
            "DetectDocumentText",
        )

        result = app.lambda_handler(api_gateway_event(), context=None)

        assert result["statusCode"] == 415
        body = json.loads(result["body"])
        assert body["error"] == "UnsupportedDocumentException"
        assert body["status"] == "error"

    @patch("app.extract_lines")
    @patch("app.store_document")
    def test_unexpected_error_returns_500(
        self, mock_store, mock_extract, api_gateway_event
    ):
        """Test that unexpected exceptions return 500."""
        mock_extract.side_effect = RuntimeError("boom")

        result = app.lambda_handler(api_gateway_event(), context=None)

        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert body["error"] == "InternalError"
        assert body["status"] == "error"
        assert "processingTime" in body

    def test_response_has_cors_headers(self, api_gateway_event):
        """Test that responses include proper CORS headers."""
        result = app.lambda_handler(api_gateway_event(), context=None)

        assert result["headers"]["Access-Control-Allow-Origin"] == "*"
        assert result["headers"]["Content-Type"] == "application/json"
        assert result["headers"]["Access-Control-Allow-Methods"] == "POST,OPTIONS"
        assert "filename" in result["headers"]["Access-Control-Allow-Headers"]
        assert result["headers"]["Access-Control-Max-Age"] == "86400"
        assert result["headers"]["Vary"] == "Origin"

    def test_request_context_preserved_in_logging(self, api_gateway_event, caplog):
        """Test that request context fields are present in the event."""
        event = api_gateway_event(request_id="trace-123")
        assert event["requestContext"]["requestId"] == "trace-123"
        assert event["requestContext"]["stage"] == "prod"
        assert event["requestContext"]["httpMethod"] == "POST"
        assert event["isBase64Encoded"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])