# Secure Document Analyzer - Deployment Guide

## Prerequisites
1. AWS CLI installed and configured (`aws configure`)
2. AWS SAM CLI installed

## Installing SAM CLI

### Windows:
Download the installer from: https://github.com/aws/aws-sam-cli/releases/latest
Or use pip: `pip install aws-sam-cli`

### Verify installation:
```bash
sam --version
```

## Deploying with SAM

### Step 1: Build the application
```bash
sam build
```

### Step 2: Deploy (guided - first time)
```bash
sam deploy --guided
```

This will ask you:
- Stack name: `secure-document-analyzer`
- AWS Region: (your preferred region)
- Confirm changes before deploy: Y
- Allow SAM to create IAM roles: Y
- Save arguments to samconfig.toml: Y

### Step 3: Test the API
After deployment, you'll get an API URL. Test with curl:
```bash
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/prod/document \
  -H "Content-Type: application/json" \
  -H "filename: test.pdf" \
  --data-binary @test.pdf
```

## Local Testing
You can still use the CLI version:
```bash
python backend/main.py <file_path> [bucket_name]
```

## Files Structure
```
backend/
  - lambda_function.py  (Lambda handler)
  - s3_upload.py       (S3 upload module)
  - textract_analyzer.py (Textract module)
  - main.py            (CLI interface)
  - requirements.txt   (Python dependencies)
infrastructure/
  - sam-template.yaml  (SAM deployment template)
  - iam_policy.json    (IAM permissions)