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

from botocore.exceptions import ClientError

from services.document_storage import store_document
from services.text_extraction import extract_lines
from utils.errors import http_status_for_aws_error
from utils.logger import get_logger
from utils.validators import InvalidRequestError, parse_upload_event

logger = get_logger()

BUCKET_NAME = os.environ.get("BUCKET_NAME", "ai-security-uploads-2026")

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",  # CORS for web clients
}


def _json_response(status_code: int, body: dict) -> dict:
    """Build a standard API Gateway JSON response."""
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(body),
    }


def lambda_handler(event: dict, context=None) -> dict:
    """
    Main Lambda handler function.

    Parameters:
        event (dict): The event data from API Gateway.
        context: Lambda context (optional; used for request tracing).

    Returns:
        dict: API Gateway response with extracted text or an error message.
    """
    try:
        request = parse_upload_event(event)

        logger.info(
            "Lambda invocation started",
            extra={
                "request_id": getattr(context, "aws_request_id", "local"),
                "document_name": request.filename,
            },
        )

        # Persist the document to S3
        store_document(BUCKET_NAME, request.filename, request.content)

        # Extract text using Textract
        extracted_text = extract_lines(BUCKET_NAME, request.filename)

        return _json_response(
            200,
            {
                "message": "Document processed successfully",
                "filename": request.filename,
                "extracted_text": extracted_text,
            },
        )

    except InvalidRequestError as e:
        logger.warning("Invalid request", extra={"reason": str(e)})
        return _json_response(400, {"error": str(e), "message": str(e)})

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
        return _json_response(
            status_code,
            {"error": f"AWS Error: {error_code}", "message": error_message},
        )

    except Exception as e:  # noqa: BLE001 - last-resort guard for the handler
        logger.error(
            "Unexpected error",
            extra={"error_type": type(e).__name__, "error_message": str(e)},
        )
        return _json_response(500, {"error": "Internal error", "message": str(e)})


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
