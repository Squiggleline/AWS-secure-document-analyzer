"""
Unit tests for src/utils/validators.py (file type, size, and filename validation).
"""

import base64

import pytest

from utils.validators import (
    InvalidRequestError,
    _validate_filename,
    _validate_file_size,
    parse_upload_event,
)


def _b64(data: bytes) -> str:
    """Encode bytes to a base64 string for event bodies."""
    return base64.b64encode(data).decode("utf-8")


class TestValidateFilename:
    """Test cases for filename validation."""

    @pytest.mark.parametrize(
        "filename",
        ["document.pdf", "image.PNG", "photo.JPG", "scan.tiff", "file.JPEG"],
    )
    def test_valid_filenames(self, filename):
        assert _validate_filename(filename) == filename

    def test_strips_whitespace(self):
        assert _validate_filename("  report.pdf  ") == "report.pdf"

    def test_empty_filename_rejected(self):
        with pytest.raises(InvalidRequestError, match="must not be empty"):
            _validate_filename("")

    def test_whitespace_only_filename_rejected(self):
        with pytest.raises(InvalidRequestError, match="must not be empty"):
            _validate_filename("   ")

    @pytest.mark.parametrize(
        "filename",
        ["../secret.pdf", "..\\secret.pdf", ".hidden.pdf"],
    )
    def test_path_traversal_rejected(self, filename):
        with pytest.raises(InvalidRequestError, match="path traversal"):
            _validate_filename(filename)

    @pytest.mark.parametrize(
        "filename",
        ["path/to/file.pdf", "dir\\file.pdf", "file\x00.pdf"],
    )
    def test_unsafe_characters_rejected(self, filename):
        with pytest.raises(InvalidRequestError, match="invalid characters"):
            _validate_filename(filename)

    @pytest.mark.parametrize(
        "filename",
        ["document.txt", "file.docx", "noextension", "file.exe"],
    )
    def test_unsupported_extension_rejected(self, filename):
        with pytest.raises(InvalidRequestError, match="Unsupported file type"):
            _validate_filename(filename)

    def test_filename_too_long_rejected(self):
        long_name = "a" * 256 + ".pdf"
        with pytest.raises(InvalidRequestError, match="maximum length"):
            _validate_filename(long_name)


class TestValidateFileSize:
    """Test cases for file size validation."""

    def test_small_file_accepted(self):
        _validate_file_size(b"x" * 1024)  # 1 KB

    def test_empty_file_accepted(self):
        # Empty content is caught earlier in parse_upload_event;
        # _validate_file_size itself only checks the upper bound.
        _validate_file_size(b"")

    def test_oversized_file_rejected(self):
        # Create content larger than the default 10 MB limit
        oversized = b"x" * (10 * 1024 * 1024 + 1)
        with pytest.raises(InvalidRequestError, match="exceeds maximum"):
            _validate_file_size(oversized)


class TestParseUploadEventValidation:
    """Integration tests for parse_upload_event with validation."""

    def test_valid_pdf_upload(self):
        event = {
            "body": _b64(b"fake pdf content"),
            "headers": {"filename": "report.pdf"},
        }
        result = parse_upload_event(event)
        assert result.filename == "report.pdf"
        assert result.content == b"fake pdf content"

    def test_unsupported_file_type_returns_400(self):
        event = {
            "body": _b64(b"content"),
            "headers": {"filename": "document.txt"},
        }
        with pytest.raises(InvalidRequestError, match="Unsupported file type"):
            parse_upload_event(event)

    def test_oversized_file_returns_400(self):
        event = {
            "body": _b64(b"x" * (10 * 1024 * 1024 + 1)),
            "headers": {"filename": "big.pdf"},
        }
        with pytest.raises(InvalidRequestError, match="exceeds maximum"):
            parse_upload_event(event)

    def test_path_traversal_filename_returns_400(self):
        event = {
            "body": _b64(b"content"),
            "headers": {"filename": "../../../etc/passwd.pdf"},
        }
        with pytest.raises(InvalidRequestError, match="path traversal"):
            parse_upload_event(event)

    def test_default_filename_is_valid_pdf(self):
        event = {"body": _b64(b"content")}
        result = parse_upload_event(event)
        assert result.filename == "uploaded_document.pdf"

    def test_uppercase_extension_accepted(self):
        event = {
            "body": _b64(b"content"),
            "headers": {"filename": "photo.PNG"},
        }
        result = parse_upload_event(event)
        assert result.filename == "photo.PNG"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])