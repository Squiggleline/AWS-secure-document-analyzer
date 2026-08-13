# =============================================================================
# Secure Document Analyzer - SAM Local Testing Script (PowerShell)
# =============================================================================
# Builds the SAM application and invokes the Lambda function locally with
# the sample API Gateway events.
#
# Usage:
#   .\scripts\local.ps1            # Build + invoke with valid event
#   .\scripts\local.ps1 -Api       # Build + start API Gateway locally
#   .\scripts\local.ps1 -All       # Build + invoke all sample events
# =============================================================================

param(
    [switch]$Api,
    [switch]$All
)

$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RootDir

Write-Host "=========================================="
Write-Host "Secure Document Analyzer - SAM Local"
Write-Host "=========================================="

Write-Host "Building SAM application..."
sam build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($Api) {
    Write-Host ""
    Write-Host "Starting API Gateway locally at http://localhost:3000"
    Write-Host "POST /document to test the upload endpoint."
    sam local start-api
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
elseif ($All) {
    Write-Host ""
    Write-Host "Invoking with valid event (expects 200)..."
    sam local invoke DocumentAnalyzerFunction --event events/document-upload-valid.json
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host ""
    Write-Host "Invoking with missing-body event (expects 400)..."
    sam local invoke DocumentAnalyzerFunction --event events/document-upload-missing-body.json
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host ""
    Write-Host "Invoking with invalid-base64 event (expects 400)..."
    sam local invoke DocumentAnalyzerFunction --event events/document-upload-invalid-base64.json
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
else {
    Write-Host ""
    Write-Host "Invoking with valid event (expects 200)..."
    sam local invoke DocumentAnalyzerFunction --event events/document-upload-valid.json
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Host ""
Write-Host "Done."