"""
Shared test fixtures and path configuration.

Adds the Lambda source directory (``src/``) to ``sys.path`` so tests can
import ``services`` and ``utils`` packages directly, matching how the
deployed Lambda resolves imports.
"""

import os
import sys

import pytest

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Provide deterministic environment variables for tests. The Lambda code
# requires BUCKET_NAME (no hardcoded fallback); SAM sets it in production.
os.environ.setdefault("BUCKET_NAME", "test-bucket")
os.environ.setdefault("CORS_ALLOWED_ORIGIN", "*")


@pytest.fixture
def mock_s3_client():
    """Patch the S3 client used by services.document_storage."""
    from unittest.mock import patch

    with patch("services.document_storage.s3_client") as mock:
        yield mock


@pytest.fixture
def mock_textract_client():
    """Patch the Textract client used by services.text_extraction."""
    from unittest.mock import patch

    with patch("services.text_extraction.textract_client") as mock:
        yield mock


@pytest.fixture
def textract_response():
    """
    Build a realistic Textract DetectDocumentText response.

    Simulates the block structure Textract returns for a scanned document:
    one PAGE block, two LINE blocks, and three WORD blocks (one of which
    is a child of the first LINE and two of which are children of the
    second LINE).
    """
    return {
        "DocumentMetadata": {"Pages": 1},
        "Blocks": [
            {"BlockType": "PAGE", "Page": 1},
            {
                "BlockType": "LINE",
                "Id": "line-1",
                "Page": 1,
                "Text": "Hello World",
                "Confidence": 99.5,
                "Geometry": {"BoundingBox": {"Left": 0.1, "Top": 0.1}},
            },
            {
                "BlockType": "LINE",
                "Id": "line-2",
                "Page": 1,
                "Text": "This is a test document",
                "Confidence": 98.2,
                "Geometry": {"BoundingBox": {"Left": 0.1, "Top": 0.2}},
            },
            {"BlockType": "WORD", "Id": "word-1", "Page": 1, "Text": "Hello", "Confidence": 99.8},
            {"BlockType": "WORD", "Id": "word-2", "Page": 1, "Text": "World", "Confidence": 99.2},
            {"BlockType": "WORD", "Id": "word-3", "Page": 1, "Text": "test", "Confidence": 97.9},
        ],
    }


@pytest.fixture
def api_gateway_event():
    """
    Build a realistic API Gateway proxy event.

    Simulates the full event structure that API Gateway sends to the
    Lambda handler, including requestContext, multiValueHeaders,
    queryStringParameters, pathParameters, stageVariables, and
    isBase64Encoded.
    """
    import base64

    def _build(
        body: bytes | None = b"Hello World",
        filename: str | None = "report.pdf",
        http_method: str = "POST",
        path: str = "/document",
        request_id: str = "test-request-id-123",
    ) -> dict:
        event = {
            "resource": path,
            "path": path,
            "httpMethod": http_method,
            "headers": {
                "Content-Type": "application/octet-stream",
                "filename": filename,
                "User-Agent": "curl/8.0.1",
                "Accept": "*/*",
            },
            "multiValueHeaders": {
                "Content-Type": ["application/octet-stream"],
                "filename": [filename],
                "User-Agent": ["curl/8.0.1"],
                "Accept": ["*/*"],
            },
            "queryStringParameters": None,
            "multiValueQueryStringParameters": None,
            "pathParameters": None,
            "stageVariables": None,
            "requestContext": {
                "resourceId": "abc123",
                "resourcePath": path,
                "httpMethod": http_method,
                "requestId": request_id,
                "accountId": "123456789012",
                "identity": {
                    "sourceIp": "203.0.113.1",
                    "userAgent": "curl/8.0.1",
                },
                "stage": "prod",
                "apiId": "api123",
            },
            "body": base64.b64encode(body).decode("utf-8") if body is not None else None,
            "isBase64Encoded": True,
        }
        return event

    return _build
