# Secure Document Analyzer - Architecture

## Current MVP Flow:
```
User Upload -> S3 -> Textract -> Return extracted text
```

## Planned Flow with API Gateway and Lambda:
```
User Upload -> API Gateway -> Lambda -> S3 -> Textract -> Return extracted text
```

## Components:

### 1. API Gateway
- REST API endpoint for document upload
- Handles file uploads from users
- Triggers Lambda function

### 2. Lambda Function
- Receives file from API Gateway
- Uploads to S3
- Calls Textract for text extraction
- Returns extracted text to user

### 3. S3 Bucket
- Secure storage for uploaded documents
- KMS encryption enabled

### 4. Textract
- Extracts text from documents
- Supports PDF, PNG, JPG, TIFF

## Next Steps:
1. Create Lambda function code
2. Set up API Gateway
3. Configure IAM roles for Lambda
4. Test the complete flow