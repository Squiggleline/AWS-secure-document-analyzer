"""
Document Storage Service
=========================

Handles S3 operations for document storage.

Service layer used by the Lambda handler to persist documents uploaded
through API Gateway.

Note: The S3 bucket is configured with default KMS encryption in the
SAM template (BucketEncryption.ServerSideEncryptionConfiguration).
Uploads therefore rely on the bucket default encryption - no
per-request ServerSideEncryption or SSEKMSKeyId parameters
are needed on put_object.
"""

import datetime
import logging

import boto3

logger = logging.getLogger(__name__)

try:
    s3_client = boto3.client("s3")
except Exception:  # pragma: no cover
    s3_client = None

_CONTENT_TYPES = {
    "pdf": "application/pdf",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "tiff": "image/tiff",
}


def _get_content_type(filename: str) -> str:
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return _CONTENT_TYPES.get(extension, "application/octet-stream")


def _build_metadata(original_filename: str) -> dict:
    return {
        "upload-timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "original-filename": original_filename,
    }


def store_document(
    bucket_name: str,
    key: str,
    body: bytes,
    original_filename: str | None = None,
) -> None:
    if s3_client is None:  # pragma: no cover
        raise RuntimeError("S3 client not initialized")

    filename = original_filename or key
    content_type = _get_content_type(filename)
    metadata = _build_metadata(filename)

    s3_client.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=body,
        ContentType=content_type,
        Metadata=metadata,
    )
    logger.info(
        "Document stored",
        extra={
            "bucket": bucket_name,
            "key": key,
            "content_type": content_type,
            "metadata_keys": list(metadata.keys()),
        },
    )
