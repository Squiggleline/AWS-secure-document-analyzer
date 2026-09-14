# Secure Document Analyzer

A serverless document processing application built with AWS SAM that extracts text from documents using Amazon Textract.

## Architecture

```
User Upload -> API Gateway -> Lambda -> Textract -> Return extracted text
```

### Components

| Component | Purpose |
|-----------|---------|
| **API Gateway** | REST API endpoint for document uploads |
| **Lambda** | Serverless compute for document processing |
| **Textract** | Text extraction from PDF, PNG, JPG, TIFF |

Documents are passed directly as raw bytes to Textract — no S3 bucket or KMS key is needed, which simplifies the infrastructure and minimizes attack surface.

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
└── .gitignore
```

## Features

- ✅ **Serverless** - No servers to manage, scales automatically
- ✅ **Fast** - Text extraction in seconds
- ✅ **Secure** - Least-privilege IAM with Textract only (no S3/KMS needed)
- ✅ **Cost-effective** - Pay only for what you use (no storage costs)
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
# or: sam deploy --config-env default
```

The first deployment will prompt for parameters. Subsequent deployments use `samconfig.toml` defaults.

### 3. Test the API

After deployment, you'll get an API URL. Test with curl:
```bash
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/prod/document \
  -H "Content-Type: application/json" \
  -H "filename: test.pdf" \
  --data-binary @test.pdf
```

## Development

### Run Unit Tests
```bash
python -m pytest
# or: make test
```

### Invoke Locally
```bash
sam local invoke --event events/document-upload-valid.json
```

## Deployment Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `LogLevel` | Logging level for the Lambda function | `INFO` |
| `MaxFileSizeBytes` | Maximum upload file size in bytes | `10485760` (10 MB) |
| `CorsAllowedOrigin` | CORS allowed origin for API Gateway | `*` |

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
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | Set by SAM from the `LogLevel` parameter |
| `MAX_FILE_SIZE_BYTES` | Maximum upload file size in bytes | Set by SAM from the `MaxFileSizeBytes` parameter (default: 10 MB) |
| `CORS_ALLOWED_ORIGIN` | CORS allowed origin for API responses | Set by SAM from the `CorsAllowedOrigin` parameter (default: `*`) |

## Error Handling

The handler returns meaningful HTTP status codes for different failure categories:

| Status | Scenario |
|--------|----------|
| `400` | Missing/invalid request body, invalid base64, `InvalidParameter`, `InvalidS3ObjectException` |
| `403` | `AccessDenied` / authorization failures |
| `413` | `EntityTooLarge`, `DocumentTooLargeException` |
| `415` | `UnsupportedDocumentException` (unsupported file type) |
| `422` | `BadDocumentException` (corrupt/unreadable document) |
| `429` | `Throttling`, `SlowDown`, rate limits |
| `500` | Unexpected runtime errors / unmapped AWS codes |
| `503` | `ServiceUnavailable` |

The mapping lives in `src/utils/errors.py` and every failure is logged with structured context (`error_code`, `error_message`, `http_status`).

## IAM Permissions (Least-Privilege)

The Lambda execution role includes only the necessary permissions:

| Service | Actions | Resource | Notes |
|---------|---------|----------|-------|
| **Textract** | `textract:DetectDocumentText` | `*` | Textract does not support resource-level permissions, so `*` is required. Only `DetectDocumentText` is granted (not `AnalyzeDocument`). |
| **CloudWatch Logs** | `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` | Log group ARN | Managed by SAM's `AWS::Serverless::Function` (AWSLambdaBasicExecutionRole). |

## License

MIT License - Feel free to use this project for learning and portfolio purposes.

## Author

Zach Ilkay - [GitHub](https://github.com/Squiggleline)
