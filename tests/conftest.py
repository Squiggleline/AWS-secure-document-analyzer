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
