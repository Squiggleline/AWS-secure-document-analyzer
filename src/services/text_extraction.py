"""
Text Extraction Service
=======================

Handles text extraction from documents using Amazon Textract.

Documents are passed as raw bytes (from the API Gateway request body)
and processed directly by Textract — no S3 bucket is required.
"""

import logging

import boto3

logger = logging.getLogger(__name__)

try:
    textract_client = boto3.client("textract")
except Exception:  # pragma: no cover - permits import without AWS configuration
    textract_client = None


def extract_text(
    content: bytes,
    feature_types: list[str] | None = None,
) -> dict:
    """
    Extract text from a document using Amazon Textract.

    If ``feature_types`` is provided, uses ``analyze_document`` (which can
    detect TABLES and FORMS). Otherwise uses ``detect_document_text`` for
    simpler LINE/WORD extraction.

    Parameters:
        content (bytes): The raw document bytes (PDF, PNG, JPG, TIFF).
        feature_types (list[str], optional): Textract features. Valid values:
            TABLES, FORMS, QUERIES, SIGNATURES, LAYOUT.

    Returns:
        dict: The raw Textract response.

    Raises:
        ClientError: If Textract rejects the request.
    """
    if textract_client is None:  # pragma: no cover
        raise RuntimeError("Textract client not initialized")

    if feature_types:
        response = textract_client.analyze_document(
            Document={"Bytes": content},
            FeatureTypes=feature_types,
        )
    else:
        response = textract_client.detect_document_text(
            Document={"Bytes": content}
        )

    logger.info(
        "Text extraction complete",
        extra={
            "content_size_bytes": len(content),
            "block_count": len(response.get("Blocks", [])),
        },
    )
    return response


def parse_text_blocks(response: dict) -> list[dict]:
    """
    Parse a Textract response and extract LINE block text with confidence.

    Filters the response for blocks of type ``LINE`` that contain text,
    returning each line's text and confidence score.

    Parameters:
        response (dict): The raw Textract response containing a
            ``Blocks`` list.

    Returns:
        list[dict]: A list of dicts, each with ``text`` (str) and
            ``confidence`` (float, rounded to 2 decimal places) keys.
            Returns an empty list if no LINE blocks are found.
    """
    lines = []
    for block in response.get("Blocks", []):
        if block.get("BlockType") == "LINE" and block.get("Text"):
            lines.append(
                {
                    "text": block["Text"],
                    "confidence": round(block.get("Confidence", 0.0), 2),
                }
            )
    return lines


def extract_lines(content: bytes) -> list[dict]:
    """
    Extract LINE blocks with text and confidence from a document.

    Parameters:
        content (bytes): The raw document bytes (PDF, PNG, JPG, TIFF).

    Returns:
        list[dict]: A list of dicts, each with ``text`` and ``confidence``
            keys for every LINE block in the document.

    Raises:
        ClientError: If Textract rejects the request.
    """
    response = extract_text(content)
    return parse_text_blocks(response)
