"""
AWS Error-to-HTTP Status Mapping
================================

Maps AWS service error codes to meaningful HTTP status codes so the API
Gateway response layer can return appropriate status codes for S3 and
Textract failures. Unmapped codes default to 500 (Internal Server Error).
"""

# AWS error code -> HTTP status code
_AWS_ERROR_STATUS_MAP = {
    # ------------------------------------------------------------------
    # Authentication / authorization (403)
    # ------------------------------------------------------------------
    "AccessDenied": 403,
    "AccessDeniedException": 403,
    "InvalidAccessKeyId": 403,
    # ------------------------------------------------------------------
    # Invalid input (400)
    # ------------------------------------------------------------------
    "InvalidParameter": 400,
    "InvalidParameterException": 400,
    "InvalidRequest": 400,
    "InvalidS3ObjectException": 400,
    "InvalidBucketName": 400,
    "InvalidArgumentException": 400,
    "MalformedPolicy": 400,
    # ------------------------------------------------------------------
    # Payload too large (413)
    # ------------------------------------------------------------------
    "EntityTooLarge": 413,
    "DocumentTooLargeException": 413,
    "MaxMessageLengthExceeded": 413,
    # ------------------------------------------------------------------
    # Unsupported media type (415)
    # ------------------------------------------------------------------
    "UnsupportedDocumentException": 415,
    # ------------------------------------------------------------------
    # Unprocessable content (422)
    # ------------------------------------------------------------------
    "BadDocumentException": 422,
    # ------------------------------------------------------------------
    # Not found (404)
    # ------------------------------------------------------------------
    "NoSuchBucket": 404,
    "NoSuchKey": 404,
    "NotFoundException": 404,
    "ResourceNotFoundException": 404,
    "KMSNotFoundException": 404,
    # ------------------------------------------------------------------
    # Conflict / already exists (409)
    # ------------------------------------------------------------------
    "BucketAlreadyExists": 409,
    "BucketAlreadyOwnedByYou": 409,
    "Conflict": 409,
    "FileAlreadyExists": 409,
    # ------------------------------------------------------------------
    # Throttling (429)
    # ------------------------------------------------------------------
    "Throttling": 429,
    "ThrottlingException": 429,
    "ProvisionedThroughputExceededException": 429,
    "RequestLimitExceeded": 429,
    "SlowDown": 429,
    # ------------------------------------------------------------------
    # Server errors (5xx)
    # ------------------------------------------------------------------
    "InternalServerError": 500,
    "ServiceUnavailable": 503,
    "KMSInternalException": 503,
    "KMSInvalidStateException": 500,
}

_DEFAULT_ERROR_STATUS = 500


def http_status_for_aws_error(error_code: str) -> int:
    """
    Map an AWS service error code to a meaningful HTTP status code.

    Parameters:
        error_code (str): The AWS error code from the service response.

    Returns:
        int: HTTP status code. Unmapped codes default to 500.
    """
    return _AWS_ERROR_STATUS_MAP.get(error_code, _DEFAULT_ERROR_STATUS)