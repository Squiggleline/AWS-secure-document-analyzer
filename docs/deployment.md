# Deployment Guide

## Prerequisites

1. **AWS CLI** installed and configured:
   ```bash
   aws --version
   aws configure
   ```

2. **AWS SAM CLI** installed:
   ```bash
   sam --version
   ```

3. **Python 3.12+** installed locally

## Deploying with SAM

### Step 1: Build the application
```bash
sam build
# or: make build
```

### Step 2: Deploy
Using defaults (defined in `samconfig.toml`):
```bash
sam deploy --config-env default
# or: make deploy
```

First-time guided deployment:
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

## Local Development

### Run unit tests:
```bash
python -m pytest
# or: make test
# or: ./scripts/test.sh (Bash) / .\scripts\test.ps1 (PowerShell)
```

### Invoke the Lambda locally:
```bash
# Valid upload event
sam local invoke --event events/document-upload-valid.json

# Missing body event (expects a 400 response)
sam local invoke --event events/document-upload-missing-body.json

# Start the API locally
sam local start-api
```

## Project Structure
```
template.yaml                    # AWS SAM template (single source of truth)
samconfig.toml                   # SAM deployment defaults
src/
  - app.py                      (Lambda handler / orchestration)
  - requirements.txt            (Python dependencies)
  - services/
    - text_extraction.py        (Textract text extraction)
  - utils/
    - logger.py                 (Structured logging)
    - validators.py             (Event validation)
    - errors.py                 (AWS error -> HTTP mapping)
tests/
  - conftest.py                 (Shared fixtures)
  - unit/                       (Unit tests for src/)
events/                         (Sample events for sam local invoke)
scripts/                        (Cross-platform build/test/deploy helpers)
infrastructure/
  - iam_policy.json             (IAM permissions reference)
docs/
  - architecture.md             (Architecture documentation)
  - deployment.md               (This guide)
```
