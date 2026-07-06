#!/usr/bin/env python
"""
Secure Document Analyzer - S3 Upload Module
This module handles uploading documents to S3 for processing.
"""

import boto3
import os
from botocore.exceptions import ClientError

# Create an S3 client - this is our connection to AWS S3
s3_client = boto3.client('s3')

def upload_document(file_path, bucket_name, object_name=None, kms_key_id=None):
    """
    Upload a document to an S3 bucket.
    
    Parameters:
        file_path (str): Path to the file you want to upload
        bucket_name (str): Name of your S3 bucket
        object_name (str, optional): Name for the file in S3. 
                                   If not provided, uses the file's name.
        kms_key_id (str, optional): KMS key ID for encryption.
                                    If not provided, uses bucket default encryption.
    
    Returns:
        bool: True if upload was successful, False otherwise
    """
    
    # If no object name is provided, use the file's name
    if object_name is None:
        object_name = os.path.basename(file_path)
    
    # Set up encryption arguments
    extra_args = {}
    if kms_key_id:
        extra_args['ServerSideEncryption'] = 'aws:kms'
        extra_args['SSEKMSKeyId'] = kms_key_id
    
    try:
        # The actual upload command
        # This uploads the file to S3 with server-side encryption
        s3_client.upload_file(
            file_path,           # Local file path
            bucket_name,         # S3 bucket name
            object_name,         # Name in S3
            ExtraArgs=extra_args if extra_args else None
        )
        print(f"[OK] Successfully uploaded {file_path} to s3://{bucket_name}/{object_name}")
        return True
        
    except ClientError as e:
        print(f"[ERROR] Error uploading file: {e}")
        return False
    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}")
        return False

# This code runs when you execute the script directly
if __name__ == "__main__":
    print("S3 Upload Module for Secure Document Analyzer")
    print("=" * 50)
    
    # Example usage (you'll need to create a bucket first)
    # upload_document("my_document.pdf", "my-secure-bucket")
    
    print("\nTo use this module:")
    print("1. Create an S3 bucket in AWS")
    print("2. Call upload_document('path/to/file.pdf', 'your-bucket-name')")