# Secure Document Analyzer - Architecture

## Current Architecture:
```
User Upload -> API Gateway -> Lambda -> Textract -> Return extracted text
```

## Components:

### 1. API Gateway
- REST API endpoint for document upload (`POST /document`)
- CORS enabled for web clients
- Passes the base64-encoded file body to the Lambda function

### 2. Lambda Function (`src/app.py`)
- Receives file from API Gateway
- Validates and parses the upload event (`src/utils/validators.py`)
- Extracts text directly from the uploaded document bytes using Amazon Textract
- Returns extracted text to the user

### 3. Textract
- Extracts text from documents
- Supports PDF, PNG, JPG, TIFF
- Documents are passed as raw bytes (no S3 required)

## Infrastructure (AWS SAM - `template.yaml`)
- `AWS::Serverless::Function` - Lambda with python3.12 runtime, Textract permissions
- `AWS::Serverless::Api` - API Gateway REST API
- Least-privilege IAM policy (Textract only)

## Code Organization
```
src/
├── app.py                  # Thin Lambda handler (orchestration)
├── requirements.txt        # Runtime dependencies
├── services/
│   └── text_extraction.py  # Textract text extraction
└── utils/
    ├── __init__.py
    ├── errors.py            # AWS error -> HTTP status mapping
    ├── logger.py            # Structured logging
    └── validators.py        # Event validation & parsing
```

## Testing
- Unit tests in `tests/unit/` target the deployed `src/` code
- AWS clients are mocked via pytest fixtures in `tests/conftest.py`
- Sample API Gateway events in `events/` for `sam local invoke`

## Deployment
- `sam build` + `sam deploy` (defaults in `samconfig.toml`)
- Alternatively: `make build` / `make deploy`
