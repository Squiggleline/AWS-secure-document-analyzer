# Secure Document Analyzer

A serverless document processing application built with AWS SAM that extracts text from documents using Amazon Textract.

## Architecture

```
User Upload -> API Gateway -> Lambda -> S3 -> Textract -> Return extracted text
```

### Components

| Component | Purpose |
|-----------|---------|
| **API Gateway** | REST API endpoint for document uploads |
| **Lambda** | Serverless compute for document processing |
| **S3** | Secure document storage (KMS encrypted) |
| **Textract** | Text extraction from PDF, PNG, JPG, TIFF |

## Project Structure

```
secure-document-analyzer/
├── template.yaml                    # AWS SAM template (single source of truth)
├── samconfig.toml                   # SAM deployment defaults
├── Makefile                         # Build/test/deploy/clean tasks
├── requirements-dev.txt             # Dev/test dependencies (pytest + runtime)
├── src/                             # Lambda function code
│   ├── app.py                       # Thin Lambda handler (orchestration)
│   ├── requirements.txt             # Runtime dependencies (deployed to Lambda)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document_storage.py      # S3 storage operations
│   │   └── text_extraction.py       # Textract text extraction
│   └── utils/
│       ├── __init__.py
│       ├── errors.py                # AWS error -> HTTP status mapping
│       ├── logger.py                # Structured logging configuration
│       └── validators.py            # Event validation & parsing
├── events/                          # Sample events for `sam local invoke`
│   ├── document-upload-valid.json
│   └── document-upload-missing-body.json
├── tests/
│   ├── conftest.py                  # Shared fixtures & path setup
│   └── unit/
│       ├── __init__.py
│       ├── test_app.py              # Handler tests
│       ├── test_document_storage.py # S3 service tests
│       └── test_text_extraction.py  # Textract service tests
├── scripts/                         # Cross-platform automation
│   ├── deploy.sh                    # Bash deployment
│   ├── deploy.ps1                   # PowerShell deployment
│   ├── test.sh                      # Bash test runner
│   └── test.ps1                     # PowerShell test runner
├── infrastructure/
│   ├── iam_policy.json              # IAM permissions reference
│   └── README.md
├── docs/
│   ├── architecture.md              # Architecture documentation
│   └── deployment.md                # Deployment guide
├── frontend/                        # Web client (if applicable)
└── .gitignore
```

## Features

- ✅ **Serverless** - No servers to manage, scales automatically
- ✅ **Secure** - KMS encryption for document storage
- ✅ **Fast** - Text extraction in seconds
- ✅ **Cost-effective** - Pay only for what you use
- ✅ **Portfolio-ready** - Well-documented, production-ready code

## Prerequisites

1. AWS CLI installed and configured (`aws configure`)
2. AWS SAM CLI installed (`sam --version`)
3. Python 3.12+

## Quick Start

### 1. Build the Application

```bash
make build
# or: sam build
```

### 2. Deploy to AWS

```bash
make deploy
# or: sam deploy --guided
```

The first deployment will prompt for parameters. Subsequent deployments use `samconfig.toml` defaults.

#### Deployment Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `CreateBucket` | Create new S3 bucket (true) or use existing (false) | `false` |
| `DocumentBucketName` | S3 bucket name for document storage | `ai-security-uploads-2026` |
| `KmsKeyId` | KMS key ID for encryption (optional) | (empty) |
| `LogLevel` | Logging level for the Lambda function | `INFO` |
| `MaxFileSizeBytes` | Maximum upload file size in bytes | `10485760` (10 MB) |

### 3. Test the API

After deployment, you'll get an API URL. Test with curl:

```bash
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/prod/document \
  -H "Content-Type: application/json" \
  -H "filename: test.pdf" \
  --data-binary @test.pdf
```

## Local Development

### Install Dev Dependencies

```bash
pip install -r requirements-dev.txt
```

This installs pytest plus the runtime dependencies (boto3) needed to run the test suite locally.

### Run Tests

```bash
make test
# or: python -m pytest
```

### Invoke Locally with SAM

```bash
# Valid upload event
sam local invoke --event events/document-upload-valid.json

# Missing body event (expects a 400 response)
sam local invoke --event events/document-upload-missing-body.json

# Start the API locally
sam local start-api
```

### Manual Scripts

For environments without `make`:

```bash
# Bash
./scripts/test.sh
./scripts/deploy.sh

# PowerShell
.\scripts\test.ps1
.\scripts\deploy.ps1
```

## Code Layout

Thin handler design keeps `app.py` focused on orchestration:

```
API Gateway event
    │
    ▼
app.lambda_handler ──► utils/validators.parse_upload_event
    │
    ├──► services/document_storage.store_document  (S3)
    └──► services/text_extraction.extract_lines    (Textract)
```

- **`app.py`** - Parses the event, orchestrates the workflow, builds the response.
- **`services/`** - Reusable business logic (S3 storage, Textract extraction).
- **`utils/`** - Cross-cutting helpers (logging, validation, AWS error-to-HTTP mapping).
- **`tests/unit/`** - Tests for the deployed Lambda code, using pytest fixtures to mock AWS clients.

## Error Handling

The handler returns meaningful HTTP status codes for different failure categories:

| Status | Scenario |
|--------|----------|
| `400` | Missing/invalid request body, invalid base64, `InvalidParameter`, `InvalidS3ObjectException` |
| `403` | `AccessDenied` / authorization failures |
| `404` | `NoSuchBucket`, `NoSuchKey`, `ResourceNotFoundException` |
| `409` | `BucketAlreadyExists`, `Conflict` |
| `413` | `EntityTooLarge`, `DocumentTooLargeException` |
| `415` | `UnsupportedDocumentException` (unsupported file type) |
| `422` | `BadDocumentException` (corrupt/unreadable document) |
| `429` | `Throttling`, `SlowDown`, rate limits |
| `500` | Unexpected runtime errors / unmapped AWS codes |
| `503` | `ServiceUnavailable` |

The mapping lives in `src/utils/errors.py` and every failure is logged with structured context (`error_code`, `error_message`, `http_status`).

## IAM Permissions (Least-Privilege)

The Lambda execution role includes only the necessary permissions:

- **S3** - GetObject, PutObject for the document bucket
- **Textract** - DetectDocumentText for text extraction
- **KMS** - Decrypt, Encrypt, GenerateDataKey for encryption
- **CloudWatch** - Basic execution role for logging

## S3 Bucket Protection

When the bucket is created by the template (`CreateBucket=true`), the following protections are enabled:

| Protection | Purpose |
|------------|---------|
| **KMS encryption** | Server-side encryption with `aws:kms` on all objects |
| **Public access block** | Blocks all public ACLs and bucket policies |
| **Versioning** | Preserves all object versions — protects against accidental overwrites when the same filename is re-uploaded |
| **Lifecycle rule** | Transitions noncurrent versions to Glacier after 90 days and expires them after 365 days (controls cost while retaining recent history) |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/document` | Upload a document for text extraction |
| OPTIONS | `/document` | CORS preflight request |

## Supported File Types

- PDF
- PNG
- JPG/JPEG
- TIFF

## Environment Variables

All configuration is injected by SAM via the template (`Environment.Variables`) — no values are hardcoded in the Lambda code.

| Variable | Description | Source |
|----------|-------------|--------|
| `BUCKET_NAME` | S3 bucket for document storage | Set by SAM from the `DocumentBucketName` parameter (**required** — no fallback) |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | Set by SAM from the `LogLevel` parameter |
| `MAX_FILE_SIZE_BYTES` | Maximum upload file size in bytes | Set by SAM from the `MaxFileSizeBytes` parameter (default: 10 MB) |

## License

MIT License - Feel free to use this project for learning and portfolio purposes.

## Author

Zach Ilkay - [GitHub](https://github.com/Squiggleline)