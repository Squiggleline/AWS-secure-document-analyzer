# =============================================================================
# Secure Document Analyzer - Development & Deployment Tasks
# =============================================================================
# Usage:
#   make test         # Run unit tests
#   make build        # Build SAM artifacts
#   make deploy       # Deploy with SAM (uses samconfig.toml defaults)
#   make local        # Start API Gateway locally via SAM
#   make clean        # Remove build artifacts and caches
# =============================================================================

.DEFAULT_GOAL := help

.PHONY: help test build deploy local clean

help:
	@echo "Secure Document Analyzer"
	@echo "-----------------------"
	@echo "  make test      Run unit tests"
	@echo "  make build     Build SAM artifacts"
	@echo "  make deploy    Deploy with SAM (uses samconfig.toml defaults)"
	@echo "  make local     Start API Gateway locally via SAM"
	@echo "  make clean     Remove build artifacts and caches"

test:
	python -m pytest

build:
	sam build

deploy: build
	sam deploy --config-env default

local:
	sam local start-api

clean:
	rm -rf .aws-sam .pytest_cache htmlcov
	find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true