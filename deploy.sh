#!/bin/bash
# =============================================================================
# Secure Document Analyzer - Deployment Script
# =============================================================================
# This script packages and deploys the Lambda function using AWS CLI
# Alternative to SAM CLI for users who prefer manual deployment
# =============================================================================

set -e  # Exit on error

# Configuration
STACK_NAME="secure-document-analyzer"
REGION="us-east-1"
BUCKET_NAME="ai-security-uploads-2026"
LAMBDA_BUCKET="your-lambda-deployment-bucket"  # Change this to your S3 bucket
LAMBDA_KEY="secure-document-analyzer.zip"
TEMPLATE_FILE="infrastructure/cloudformation/lambda-api.yml"

echo "=========================================="
echo "Secure Document Analyzer - Deployment Script"
echo "=========================================="

# Step 1: Build the Lambda package
echo ""
echo "Step 1: Building Lambda package..."
cd src
pip install -r requirements.txt -t .
zip -r ../${LAMBDA_KEY} .
cd ..

# Step 2: Upload Lambda code to S3
echo ""
echo "Step 2: Uploading Lambda code to S3..."
echo "Note: Make sure ${LAMBDA_BUCKET} exists and you have write access"
aws s3 cp ${LAMBDA_KEY} s3://${LAMBDA_BUCKET}/${LAMBDA_KEY} --region ${REGION}

# Step 3: Deploy CloudFormation stack
echo ""
echo "Step 3: Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file ${TEMPLATE_FILE} \
    --stack-name ${STACK_NAME} \
    --parameter-overrides \
        BucketName=${BUCKET_NAME} \
        LambdaS3Bucket=${LAMBDA_BUCKET} \
        LambdaS3Key=${LAMBDA_KEY} \
    --capabilities CAPABILITY_IAM \
    --region ${REGION}

# Step 4: Get API URL
echo ""
echo "Step 4: Getting API URL..."
API_URL=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --region ${REGION} \
    --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
    --output text)

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo "API URL: ${API_URL}"
echo ""
echo "Test with:"
echo "curl -X POST ${API_URL} -H 'Content-Type: application/json' -H 'filename: test.pdf' --data-binary @test.pdf"