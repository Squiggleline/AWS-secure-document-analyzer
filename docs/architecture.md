# Secure Document Analyzer - Architecture

## Current Architecture:
```
User Upload -> API Gateway -> Lambda -> S3 -> Textract -> Return extracted text
```

## Components:

### 1. API Gateway
- REST API endpoint for document upload (`POST /document`)
- CORS enabled for web clients
- Triggers the Lambda function

### 2. Lambda Function (`src/app.py`)
- Receives file from API Gateway
- Validates and parses the upload event (`src/utils/validators.py`)
- Uploads document to S3 (`src/services/document_storage.py`)
- Calls Textract for text extraction (`src/services/text_extraction.py`)
- Returns extracted text to the user

### 3. S3 Bucket
- Secure storage for uploaded documents
- KMS encryption enabled
- Public access blocked

### 4. Textract
- Extracts text from documents
- Supports PDF, PNG, JPG, TIFF

## Infrastructure (AWS SAM - `template.yaml`)
- `AWS::Serverless::Function` - Lambda with python3.12 runtime
- `AWS::Serverless::Api` - API Gateway REST API
- Least-privilege IAM policies (S3, Textract, KMS)
- Optional S3 bucket creation with KMS encryption

## Code Organization
```
src/
├── app.py                  # Thin Lambda handler (orchestration)
├── services/
│   ├── document_storage.py # S3 storage operations
│   └── text_extraction.py  # Textract text extraction
└── utils/
    ├── logger.py           # Structured logging
    └── validators.py       # Event validation & parsing
```

## Testing
- Unit tests in `tests/unit/` target the deployed `src/` code
- AWS clients are mocked via pytest fixtures in `tests/conftest.py`
- Sample API Gateway events in `events/` for `sam local invoke`

## Deployment
- `sam build` + `sam deploy` (defaults in `samconfig.toml`)
- Alternatively: `make build` / `make deploy`