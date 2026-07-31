# =============================================================================
# Secure Document Analyzer - Deployment Script (PowerShell)
# =============================================================================
# Builds and deploys the SAM application using samconfig.toml defaults.
#
# Usage:
#   .\scripts\deploy.ps1 [stage]
#
# Examples:
#   .\scripts\deploy.ps1          # Deploy using samconfig.toml default stage
#   .\scripts\deploy.ps1 prod     # Deploy with an explicit stage
# =============================================================================

param(
    [string]$Stage = "default"
)

Write-Host "=========================================="
Write-Host "Secure Document Analyzer - Deploy"
Write-Host "Stage: $Stage"
Write-Host "=========================================="

Write-Host ""
Write-Host "Step 1: Building the SAM application..."
sam build --parallel
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Step 2: Deploying the SAM application..."
sam deploy --config-env $Stage --no-confirm-changeset --resolve-s3
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "=========================================="
Write-Host "Deployment complete!"
Write-Host "=========================================="
Write-Host ""
Write-Host "Test with:"
Write-Host '  curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/prod/document -H "Content-Type: application/json" -H "filename: test.pdf" --data-binary @test.pdf'