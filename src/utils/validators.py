"""
Request Validators
==================

Helpers for validating and normalizing API Gateway events.

Validates:
- File type (extension must be supported by Amazon Textract)
- File size (must not exceed the configured maximum)
- Filename (must be safe — no path traversal, no invalid characters)
"""

import base64
import logging
import os
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration (from environment variables, set by SAM)
# ---------------------------------------------------------------------------
# Maximum upload size in bytes. Textract synchronous DetectDocumentText
# supports up to 5 MB for PDF and up to 15 MB for images. We default to
# 10 MB as a conservative upper bound; override via MAX_FILE_SIZE_BYTES.
_MAX_FILE_SIZE_BYTES = int(os.environ.get("MAX_FILE_SIZE_BYTES", "10485760"))

# File extensions supported by Amazon Textract (DetectDocumentText).
# Reference: https://docs.aws.amazon.com/textract/latest/dg/supported-formats.html
_ALLOWED_EXTENSIONS = frozenset({"pdf", "png", "jpg", "jpeg", "tiff"})

# ---------------------------------------------------------------------------
# Filename validation rules
# ---------------------------------------------------------------------------
# Reject path separators, null bytes, and other characters that are unsafe
# as S3 object keys or could enable path traversal.
_UNSAFE_FILENAME_PATTERN = re.compile(r"[\\/\x00-\x1f]")

# S3 object keys can be up to 1024 bytes; we enforce a conservative limit.
_MAX_FILENAME_LENGTH = 255


@dataclass
class UploadRequest:
    """Normalized upload request parsed from an API Gateway event."""

    filename: str
    content: bytes


_DEFAULT_FILENAME = "uploaded_document.pdf"


class InvalidRequestError(Exception):
    """Raised when the API Gateway event is malformed or fails validation."""


def _validate_filename(filename: str) -> str:
    """
    Validate and normalize the filename.

    Parameters:
        filename (str): The raw filename from the request header.

    Returns:
        str: The validated filename (lowercased extension for comparison).

    Raises:
        InvalidRequestError: If the filename is empty, too long, contains
            unsafe characters, or has an unsupported extension.
    """
    if not filename or not filename.strip():
        raise InvalidRequestError("Filename must not be empty")

    filename = filename.strip()

    if len(filename) > _MAX_FILENAME_LENGTH:
        raise InvalidRequestError(
            f"Filename exceeds maximum length of {_MAX_FILENAME_LENGTH} characters"
        )

    # Reject directory traversal attempts (e.g., "../secret.pdf")
    if ".." in filename or filename.startswith("."):
        raise InvalidRequestError("Filename must not contain path traversal sequences")

    if _UNSAFE_FILENAME_PATTERN.search(filename):
        raise InvalidRequestError(
            "Filename contains invalid characters (path separators or control characters)"
        )

    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in _ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(_ALLOWED_EXTENSIONS))
        raise InvalidRequestError(
            f"Unsupported file type: '.{extension}'. "
            f"Allowed types: {allowed}"
        )

    return filename


def _validate_file_size(content: bytes) -> None:
    """
    Validate that the file content does not exceed the maximum size.

    Parameters:
        content (bytes): The decoded file content.

    Raises:
        InvalidRequestError: If the file exceeds the configured maximum.
    """
    size = len(content)
    if size > _MAX_FILE_SIZE_BYTES:
        max_mb = _MAX_FILE_SIZE_BYTES / (1024 * 1024)
        actual_mb = size / (1024 * 1024)
        raise InvalidRequestError(
            f"File size {actual_mb:.1f} MB exceeds maximum of {max_mb:.1f} MB"
        )


def parse_upload_event(event: dict) -> UploadRequest:
    """
    Parse and validate an API Gateway upload event.

    Performs the following checks in order:
    1. Body is present and valid base64.
    2. Decoded content is non-empty.
    3. File size does not exceed the configured maximum.
    4. Filename is safe (no path traversal, valid length, valid characters).
    5. File extension is supported by Amazon Textract.

    Parameters:
        event (dict): The raw API Gateway event.

    Returns:
        UploadRequest: Normalized filename and decoded content.

    Raises:
        InvalidRequestError: If any validation check fails.
    """
    body = event.get("body")
    if body is None:
        logger.warning("Request missing body")
        raise InvalidRequestError("No file provided in request")

    try:
        content = base64.b64decode(body, validate=True)
    except (base64.binascii.Error, ValueError, TypeError) as exc:
        logger.warning("Request body is not valid base64", extra={"error": str(exc)})
        raise InvalidRequestError("Request body is not valid base64") from exc

    if not content:
        logger.warning("Request body is empty")
        raise InvalidRequestError("Empty file content")

    # Validate file size before any S3/Textract calls
    _validate_file_size(content)

    # Extract and validate the filename
    headers = event.get("headers") or {}
    raw_filename = headers.get("filename") or _DEFAULT_FILENAME
    filename = _validate_filename(raw_filename)

    logger.info(
        "Parsed upload request",
        extra={
            "document_name": filename,
            "file_size_bytes": len(content),
            "max_file_size_bytes": _MAX_FILE_SIZE_BYTES,
        },
    )
    return UploadRequest(filename=filename, content=content)