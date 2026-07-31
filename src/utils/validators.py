"""
Request Validators
==================

Helpers for validating and normalizing API Gateway events.
"""

import base64
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class UploadRequest:
    """Normalized upload request parsed from an API Gateway event."""

    filename: str
    content: bytes


_DEFAULT_FILENAME = "uploaded_document.pdf"


class InvalidRequestError(Exception):
    """Raised when the API Gateway event is malformed or missing required data."""


def parse_upload_event(event: dict) -> UploadRequest:
    """
    Parse and validate an API Gateway upload event.

    Parameters:
        event (dict): The raw API Gateway event.

    Returns:
        UploadRequest: Normalized filename and decoded content.

    Raises:
        InvalidRequestError: If ``body`` is missing or undecodable.
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

    headers = event.get("headers") or {}
    filename = headers.get("filename") or _DEFAULT_FILENAME

    logger.info(
        "Parsed upload request",
        extra={"document_name": filename, "file_size_bytes": len(content)},
    )
    return UploadRequest(filename=filename, content=content)
