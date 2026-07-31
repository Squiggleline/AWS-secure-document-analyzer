#!/usr/bin/env bash
# =============================================================================
# Secure Document Analyzer - Deployment Script
# =============================================================================
# Builds and deploys the SAM application using samconfig.toml defaults.
#
# Usage:
#   ./scripts/deploy.sh [stage]
#
# Examples:
#   ./scripts/deploy.sh          # Deploy using samconfig.toml default stage
#   ./scripts/deploy.sh prod     # Deploy with an explicit stage
# =============================================================================

set -euo pipefail

STAGE="${1:-default}"

echo "=========================================="
echo "Secure Document Analyzer - Deploy"
echo "Stage: ${STAGE}"
echo "=========================================="

echo ""
echo "Step 1: Building the SAM application..."
sam build --parallel

echo ""
echo "Step 2: Deploying the SAM application..."
sam deploy --config-env "${STAGE}" --no-confirm-changeset --resolve-s3

echo ""
echo "=========================================="
echo "Deployment complete!"
echo "=========================================="
echo ""
echo "Test with:"
echo "  curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/prod/document \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -H 'filename: test.pdf' \\"
echo "    --data-binary @test.pdf"