"""
Document Storage Service
=========================

Handles S3 operations for document storage.

Service layer used by the Lambda handler to persist documents uploaded
through API Gateway.
"""

import logging

import boto3

logger = logging.getLogger(__name__)

try:
    s3_client = boto3.client("s3")
except Exception:  # pragma: no cover - permits import without AWS configuration
    s3_client = None


def store_document(
    bucket_name: str,
    key: str,
    body: bytes,
    kms_key_id: str | None = None,
) -> None:
    """
    Store a document in S3.

    Parameters:
        bucket_name (str): Name of the S3 bucket.
        key (str): Object key (filename) in the bucket.
        body (bytes): Raw file content to store.
        kms_key_id (str, optional): KMS key ID for server-side encryption.

    Raises:
        ClientError: If S3 rejects the request.
    """
    if s3_client is None:  # pragma: no cover
        raise RuntimeError("S3 client not initialized")

    extra_args = {}
    if kms_key_id:
        extra_args["ServerSideEncryption"] = "aws:kms"
        extra_args["SSEKMSKeyId"] = kms_key_id

    s3_client.put_object(Bucket=bucket_name, Key=key, Body=body, **extra_args)
    logger.info("Document stored", extra={"bucket": bucket_name, "key": key})