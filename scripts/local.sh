#!/usr/bin/env bash
# =============================================================================
# Secure Document Analyzer - SAM Local Testing Script
# =============================================================================
# Builds the SAM application and invokes the Lambda function locally with
# the sample API Gateway events.
#
# Usage:
#   ./scripts/local.sh            # Build + invoke with valid event
#   ./scripts/local.sh --api      # Build + start API Gateway locally
#   ./scripts/local.sh --all      # Build + invoke all sample events
# =============================================================================

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

MODE="${1:-invoke}"

echo "=========================================="
echo "Secure Document Analyzer - SAM Local"
echo "=========================================="

echo "Building SAM application..."
sam build

case "${MODE}" in
  --api)
    echo ""
    echo "Starting API Gateway locally at http://localhost:3000"
    echo "POST /document to test the upload endpoint."
    sam local start-api
    ;;
  --all)
    echo ""
    echo "Invoking with valid event (expects 200)..."
    sam local invoke DocumentAnalyzerFunction --event events/document-upload-valid.json

    echo ""
    echo "Invoking with missing-body event (expects 400)..."
    sam local invoke DocumentAnalyzerFunction --event events/document-upload-missing-body.json

    echo ""
    echo "Invoking with invalid-base64 event (expects 400)..."
    sam local invoke DocumentAnalyzerFunction --event events/document-upload-invalid-base64.json
    ;;
  *)
    echo ""
    echo "Invoking with valid event (expects 200)..."
    sam local invoke DocumentAnalyzerFunction --event events/document-upload-valid.json
    ;;
esac

echo ""
echo "Done."