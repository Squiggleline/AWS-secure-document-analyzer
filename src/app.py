"""
Secure Document Analyzer - Lambda Function
==========================================

This Lambda function handles document processing:
1. Receives file uploads from API Gateway
2. Stores documents in S3
3. Extracts text using Amazon Textract
4. Returns extracted text to the client

Architecture: User Upload -> API Gateway -> Lambda -> S3 -> Textract -> Return text
"""

import json
import boto3
import os
import base64
from botocore.exceptions import ClientError

# Initialize AWS clients (reused across invocations for performance)
s3_client = boto3.client('s3')
textract_client = boto3.client('textract')

# Configuration from environment variables
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'ai-security-uploads-2026')


def lambda_handler(event, context):
    """
    Main Lambda handler function.
    
    Parameters:
        event: The event data from API Gateway
        context: Lambda context (contains request ID, memory, etc.)
    
    Returns:
        dict: API Gateway response with extracted text or error message
    """
    
    try:
        # Step 1: Validate the request
        # API Gateway sends the file in the body (base64 encoded)
        if 'body' not in event:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'No file provided in request',
                    'message': 'Please provide a file in the request body'
                })
            }
        
        # Step 2: Decode the file content
        # The body is base64 encoded by API Gateway
        file_content = base64.b64decode(event['body'])
        
        # Step 3: Get filename from headers
        # Client should provide filename in the header
        headers = event.get('headers', {}) or {}
        filename = headers.get('filename', 'uploaded_document.pdf')
        
        # Step 4: Upload to S3
        # The document is stored in the configured bucket
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=file_content
        )
        
        # Step 5: Extract text with Textract
        # Textract processes PDF, PNG, JPG, and TIFF files
        response = textract_client.detect_document_text(
            Document={
                'S3Object': {
                    'Bucket': BUCKET_NAME,
                    'Name': filename
                }
            }
        )
        
        # Step 6: Parse the extracted text
        # Textract returns blocks; we extract LINE blocks
        extracted_text = ""
        for block in response.get('Blocks', []):
            if block['BlockType'] == 'LINE':
                extracted_text += block['Text'] + "\n"
        
        # Step 7: Return the response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # CORS for web clients
            },
            'body': json.dumps({
                'message': 'Document processed successfully',
                'filename': filename,
                'extracted_text': extracted_text
            })
        }
        
    except ClientError as e:
        # Handle AWS service errors
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = e.response.get('Error', {}).get('Message', str(e))
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'AWS Error: {error_code}',
                'message': error_message
            })
        }
    except Exception as e:
        # Handle unexpected errors
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal error',
                'message': str(e)
            })
        }


# For local testing
if __name__ == "__main__":
    print("Secure Document Analyzer - Lambda Function")
    print("=" * 50)
    print("\nThis function is designed to be deployed to AWS Lambda.")
    print("It will be triggered by API Gateway when a file is uploaded.")
    print("\nFor local testing, you can use the CLI version in backend/main.py")