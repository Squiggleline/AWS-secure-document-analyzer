"""
Secure Document Analyzer - Lambda Handler
==========================================

Thin Lambda handler that orchestrates the document analysis workflow:

1. Parse the API Gateway upload event.
2. Store the document in S3.
3. Extract text with Amazon Textract.
4. Return the extracted text to the client.

Architecture: User Upload -> API Gateway -> Lambda -> S3 -> Textract -> Response
"""

import json
import os
import time

from botocore.exceptions import ClientError

from services.document_storage import store_document
from services.text_extraction import extract_lines
from utils.errors import http_status_for_aws_error
from utils.logger import get_logger
from utils.validators import InvalidRequestError, parse_upload_event

logger = get_logger()

BUCKET_NAME = os.environ["BUCKET_NAME"]

CORS_ALLOWED_ORIGIN = os.environ.get("CORS_ALLOWED_ORIGIN", "*")

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": CORS_ALLOWED_ORIGIN,
    "Access-Control-Allow-Methods": "POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type,filename,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
}


def _json_response(status_code: int, body: dict) -> dict:
    """Build a standard API Gateway JSON response."""
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(body),
    }


def _error_response(
    status_code: int,
    error_code: str,
    message: str,
    start_time: float,
    filename: str | None = None,
) -> dict:
    """
    Build a consistent error response.

    All error responses share the same structure:
    - ``filename``: the document filename (or None if not yet known)
    - ``status``: always ``"error"``
    - ``processingTime``: elapsed time since ``start_time``
    - ``error``: a short error code (e.g. ``"InvalidRequest"``, ``"AccessDenied"``)
    - ``message``: a human-readable error description

    Parameters:
        status_code (int): HTTP status code.
        error_code (str): Short error code for programmatic handling.
        message (str): Human-readable error description.
        start_time (float): ``time.perf_counter()`` value from handler start.
        filename (str, optional): The document filename, if known.

    Returns:
        dict: API Gateway response with a consistent error body.
    """
    return _json_response(
        status_code,
        {
            "filename": filename,
            "status": "error",
            "processingTime": f"{time.perf_counter() - start_time:.3f}s",
            "error": error_code,
            "message": message,
        },
    )


def lambda_handler(event: dict, context=None) -> dict:
    """
    Main Lambda handler function.

    Parameters:
        event (dict): The event data from API Gateway.
        context: Lambda context (optional; used for request tracing).

    Returns:
        dict: API Gateway response with extracted text or an error message.
    """
    start_time = time.perf_counter()

    try:
        request = parse_upload_event(event)

        logger.info(
            "Lambda invocation started",
            extra={
                "request_id": getattr(context, "aws_request_id", "local"),
                "document_name": request.filename,
            },
        )

        # Persist the document to S3 (with metadata: timestamp, content type, filename)
        store_document(
            BUCKET_NAME,
            request.filename,
            request.content,
            original_filename=request.filename,
        )

        # Extract text using Textract (returns lines with confidence scores)
        extracted_lines = extract_lines(BUCKET_NAME, request.filename)
        extracted_text = "\n".join(line["text"] for line in extracted_lines)

        processing_time = time.perf_counter() - start_time

        return _json_response(
            200,
            {
                "filename": request.filename,
                "status": "success",
                "processingTime": f"{processing_time:.3f}s",
                "text": extracted_text,
                "lines": extracted_lines,
            },
        )

    except InvalidRequestError as e:
        logger.warning("Invalid request", extra={"reason": str(e)})
        return _error_response(400, "InvalidRequest", str(e), start_time)

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))
        status_code = http_status_for_aws_error(error_code)
        logger.error(
            "AWS service error",
            extra={
                "error_code": error_code,
                "error_message": error_message,
                "http_status": status_code,
            },
        )
        return _error_response(status_code, error_code, error_message, start_time)

    except Exception as e:  # noqa: BLE001 - last-resort guard for the handler
        logger.error(
            "Unexpected error",
            extra={"error_type": type(e).__name__, "error_message": str(e)},
        )
        return _error_response(500, "InternalError", str(e), start_time)


# For local testing
if __name__ == "__main__":
    logger.info(
        "Secure Document Analyzer - Lambda Handler",
        extra={"module": __name__},
    )
    logger.info(
        "This module is deployed as an AWS Lambda function and "
        "triggered by API Gateway when a document is uploaded.",
        extra={"architecture": "User Upload -> API Gateway -> Lambda -> S3 -> Textract -> Response"},
    )
    logger.info(
        "For local invocation, use the AWS SAM CLI",
        extra={"command": "sam local invoke --event events/document-upload-valid.json"},
    )
