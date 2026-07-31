"""
Unit tests for src/utils/errors.py (AWS error -> HTTP status mapping).
"""

import pytest

from utils.errors import http_status_for_aws_error


class TestHttpStatusForAwsError:
    """Test cases for AWS error code to HTTP status mapping."""

    def test_access_denied_maps_to_403(self):
        assert http_status_for_aws_error("AccessDenied") == 403

    def test_invalid_parameter_maps_to_400(self):
        assert http_status_for_aws_error("InvalidParameter") == 400
        assert http_status_for_aws_error("InvalidS3ObjectException") == 400

    def test_entity_too_large_maps_to_413(self):
        assert http_status_for_aws_error("EntityTooLarge") == 413
        assert http_status_for_aws_error("DocumentTooLargeException") == 413

    def test_unsupported_document_maps_to_415(self):
        assert http_status_for_aws_error("UnsupportedDocumentException") == 415

    def test_bad_document_maps_to_422(self):
        assert http_status_for_aws_error("BadDocumentException") == 422

    def test_not_found_maps_to_404(self):
        assert http_status_for_aws_error("NoSuchBucket") == 404
        assert http_status_for_aws_error("NoSuchKey") == 404

    def test_throttling_maps_to_429(self):
        assert http_status_for_aws_error("Throttling") == 429
        assert http_status_for_aws_error("SlowDown") == 429

    def test_service_unavailable_maps_to_503(self):
        assert http_status_for_aws_error("ServiceUnavailable") == 503

    def test_unknown_error_defaults_to_500(self):
        assert http_status_for_aws_error("SomeUnknownError") == 500
        assert http_status_for_aws_error("") == 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])