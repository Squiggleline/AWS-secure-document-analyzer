# =============================================================================
# Secure Document Analyzer - Test Script (PowerShell)
# =============================================================================
# Runs the unit test suite.
#
# Usage:
#   .\scripts\test.ps1
# =============================================================================

$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RootDir

Write-Host "=========================================="
Write-Host "Secure Document Analyzer - Unit Tests"
Write-Host "=========================================="

python -m pytest tests/unit -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "All tests passed!"