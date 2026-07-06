#!/usr/bin/env python
"""
Secure Document Analyzer - Lambda Function
This function handles document upload and text extraction via API Gateway.
"""

import json
import boto3
import os
import base64
from botocore.exceptions import ClientError

# Create AWS clients
s3_client = boto3.client('s3')
textract_client = boto3.client('textract')

# Configuration - use environment variables in Lambda
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'ai-security-uploads-2026')

def lambda_handler(event, context):
    """
    Main Lambda handler function.
    
    Parameters:
        event: The event data from API Gateway
        context: Lambda context
    
    Returns:
        dict: Response with extracted text or error message
    """
    
    try:
        # Step 1: Get the file from the request
        # API Gateway sends the file in the body (base64 encoded)
        if 'body' not in event:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No file provided in request'})
            }
        
        # Decode the base64 file content
        file_content = base64.b64decode(event['body'])
        
        # Get filename from headers or use a default
        filename = event.get('headers', {}).get('filename', 'uploaded_document.pdf')
        
        # Step 2: Upload to S3
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=file_content
        )
        
        # Step 3: Extract text with Textract
        response = textract_client.detect_document_text(
            Document={
                'S3Object': {
                    'Bucket': BUCKET_NAME,
                    'Name': filename
                }
            }
        )
        
        # Extract text from response
        extracted_text = ""
        for block in response.get('Blocks', []):
            if block['BlockType'] == 'LINE':
                extracted_text += block['Text'] + "\n"
        
        # Step 4: Return the extracted text
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # For CORS
            },
            'body': json.dumps({
                'message': 'Document processed successfully',
                'filename': filename,
                'extracted_text': extracted_text
            })
        }
        
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Internal error: {str(e)}'})
        }

# For local testing
if __name__ == "__main__":
    print("Lambda function for Secure Document Analyzer")
    print("=" * 50)
    print("\nThis function is designed to be deployed to AWS Lambda.")
    print("It will be triggered by API Gateway when a file is uploaded.")
    print("\nFor local testing, you can use the main.py CLI instead.")