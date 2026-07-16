@echo off
REM =============================================================================
REM Secure Document Analyzer - Deployment Script (Windows)
REM =============================================================================
REM This script packages and deploys the Lambda function using AWS CLI
REM Alternative to SAM CLI for users who prefer manual deployment
REM =============================================================================

setlocal enabledelayedexpansion

REM Configuration
set STACK_NAME=secure-document-analyzer
set REGION=us-east-1
set BUCKET_NAME=ai-security-uploads-2026
set LAMBDA_BUCKET=your-lambda-deployment-bucket
set LAMBDA_KEY=secure-document-analyzer.zip
set TEMPLATE_FILE=infrastructure\cloudformation\lambda-api.yml

echo ==========================================
echo Secure Document Analyzer - Deployment Script
echo ==========================================

REM Step 1: Build the Lambda package
echo.
echo Step 1: Building Lambda package...
cd src
pip install -r requirements.txt -t .
powershell -Command "Compress-Archive -Path * -DestinationPath ..\%LAMBDA_KEY% -Force"
cd ..

REM Step 2: Upload Lambda code to S3
echo.
echo Step 2: Uploading Lambda code to S3...
echo Note: Make sure %LAMBDA_BUCKET% exists and you have write access
aws s3 cp %LAMBDA_KEY% s3://%LAMBDA_BUCKET%/%LAMBDA_KEY% --region %REGION%

REM Step 3: Deploy CloudFormation stack
echo.
echo Step 3: Deploying CloudFormation stack...
aws cloudformation deploy ^
    --template-file %TEMPLATE_FILE% ^
    --stack-name %STACK_NAME% ^
    --parameter-overrides ^
        BucketName=%BUCKET_NAME% ^
        LambdaS3Bucket=%LAMBDA_BUCKET% ^
        LambdaS3Key=%LAMBDA_KEY% ^
    --capabilities CAPABILITY_IAM ^
    --region %REGION%

REM Step 4: Get API URL
echo.
echo Step 4: Getting API URL...
for /f "delims=" %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --region %REGION% --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text') do set API_URL=%%i

echo.
echo ==========================================
echo Deployment Complete!
echo ==========================================
echo API URL: %API_URL%
echo.
echo Test with:
echo curl -X POST %API_URL% -H "Content-Type: application/json" -H "filename: test.pdf" --data-binary @test.pdf

endlocal