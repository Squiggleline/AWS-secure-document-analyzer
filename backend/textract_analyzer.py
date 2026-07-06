#!/usr/bin/env python
"""
Secure Document Analyzer - Textract Module
This module handles text extraction from documents using Amazon Textract.
"""

import boto3
from botocore.exceptions import ClientError

# Create a Textract client - this is our connection to AWS Textract
textract_client = boto3.client('textract')

def extract_text_from_document(bucket_name, document_name, feature_types=['TABLES', 'FORMS']):
    """
    Extract text from a document stored in S3 using Amazon Textract.
    
    Parameters:
        bucket_name (str): Name of the S3 bucket containing the document
        document_name (str): Name of the document in S3
        feature_types (list, optional): Features to extract. 
                                       Options: 'TABLES', 'FORMS', 'QUERIES', 'SIGNATURES', 'LAYOUT'
    
    Returns:
        dict: The response from Textract containing extracted text and data
    """
    
    try:
        # Call Textract to analyze the document
        response = textract_client.analyze_document(
            Document={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': document_name
                }
            },
            FeatureTypes=feature_types
        )
        
        print(f"[OK] Successfully extracted text from s3://{bucket_name}/{document_name}")
        return response
        
    except ClientError as e:
        print(f"[ERROR] Error extracting text: {e}")
        return None

def extract_text_simple(bucket_name, document_name):
    """
    Simple text extraction - just the raw text without special features.
    
    Parameters:
        bucket_name (str): Name of the S3 bucket containing the document
        document_name (str): Name of the document in S3
    
    Returns:
        str: The extracted text as a string
    """
    
    try:
        # Call Textract to detect text (simpler, just text - no tables/forms)
        response = textract_client.detect_document_text(
            Document={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': document_name
                }
            }
        )
        
        # Extract just the text from the response
        extracted_text = ""
        for block in response.get('Blocks', []):
            if block['BlockType'] == 'LINE':
                extracted_text += block['Text'] + "\n"
        
        print(f"[OK] Successfully extracted text from s3://{bucket_name}/{document_name}")
        return extracted_text
        
    except ClientError as e:
        print(f"[ERROR] Error extracting text: {e}")
        return None

# This code runs when you execute the script directly
if __name__ == "__main__":
    print("Textract Module for Secure Document Analyzer")
    print("=" * 50)
    
    print("\nTo use this module:")
    print("1. Upload a document to S3 using s3_upload.py")
    print("2. Call extract_text_from_document('your-bucket', 'document.pdf')")
    print("\nNote: Textract works with PDF and image files (PNG, JPG, etc.)")