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
├── template.yaml                    # AWS SAM template (main entry point)
├── src/                            # Lambda function code
│   ├── app.py                      # Main Lambda handler
│   └── requirements.txt            # Python dependencies
├── backend/                        # CLI tools for local testing
│   ├── main.py                     # CLI interface
│   ├── s3_upload.py                # S3 upload module
│   └── textract_analyzer.py        # Textract module
├── infrastructure/
│   ├── cloudformation/
│   │   └── lambda-api.yml          # Alternative CloudFormation template
│   └── iam_policy.json             # IAM permissions reference
├── docs/
│   ├── architecture.md             # Architecture documentation
│   └── deployment.md               # Deployment guide
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
sam build
```

### 2. Deploy to AWS

```bash
sam deploy --guided
```

Answer the prompts:
- Stack name: `secure-document-analyzer`
- AWS Region: `us-east-1` (or your preferred region)
- Confirm changes before deploy: `Y`
- Allow SAM to create IAM roles: `Y`
- Save arguments to samconfig.toml: `Y`

#### Deployment Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `CreateBucket` | Create new S3 bucket (true) or use existing (false) | `false` |
| `DocumentBucketName` | S3 bucket name for document storage | `ai-security-uploads-2026` |
| `KmsKeyId` | KMS key ID for encryption (optional) | (empty) |

### 3. Test the API

After deployment, you'll get an API URL. Test with curl:

```bash
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/prod/document \
  -H "Content-Type: application/json" \
  -H "filename: test.pdf" \
  --data-binary @test.pdf
```

## Local Testing

Use the CLI version for local testing:

```bash
python backend/main.py <file_path> [bucket_name]
```

Example:
```bash
python backend/main.py my_document.pdf ai-security-uploads-2026
```

## IAM Permissions (Least-Privilege)

The Lambda execution role includes only the necessary permissions:

- **S3** - GetObject, PutObject for the document bucket
- **Textract** - DetectDocumentText for text extraction
- **KMS** - Decrypt, Encrypt, GenerateDataKey for encryption
- **CloudWatch** - Basic execution role for logging

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

| Variable | Description | Default |
|----------|-------------|---------|
| `BUCKET_NAME` | S3 bucket for document storage | `ai-security-uploads-2026` |

## License

MIT License - Feel free to use this project for learning and portfolio purposes.

## Author

Zach Ilkay - [GitHub](https://github.com/Squiggleline)