#!/usr/bin/env bash
# =============================================================================
# Secure Document Analyzer - Test Script
# =============================================================================
# Runs the unit test suite.
#
# Usage:
#   ./scripts/test.sh
# =============================================================================

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "=========================================="
echo "Secure Document Analyzer - Unit Tests"
echo "=========================================="

python -m pytest tests/unit -v

echo ""
echo "All tests passed!"