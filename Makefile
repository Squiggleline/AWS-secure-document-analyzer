# =============================================================================
# Secure Document Analyzer - Development & Deployment Tasks
# =============================================================================
# Usage:
#   make test              # Run unit tests
#   make build             # Build SAM artifacts
#   make deploy            # Deploy with SAM (uses samconfig.toml defaults)
#   make local-invoke      # Invoke the Lambda locally with a sample event
#   make local-invoke-err  # Invoke locally with the missing-body event (expects 400)
#   make local-api         # Start API Gateway locally via SAM
#   make local             # Alias for local-api
#   make clean             # Remove build artifacts and caches
# =============================================================================

.DEFAULT_GOAL := help

.PHONY: help test build deploy local-invoke local-invoke-err local-api local clean

help:
	@echo "Secure Document Analyzer"
	@echo "-----------------------"
	@echo "  make test              Run unit tests"
	@echo "  make build             Build SAM artifacts"
	@echo "  make deploy            Deploy with SAM (uses samconfig.toml defaults)"
	@echo "  make local-invoke      Invoke the Lambda locally with a valid event"
	@echo "  make local-invoke-err  Invoke locally with the missing-body event (expects 400)"
	@echo "  make local-api         Start API Gateway locally via SAM"
	@echo "  make local             Alias for local-api"
	@echo "  make clean             Remove build artifacts and caches"

test:
	python -m pytest

build:
	sam build

deploy: build
	sam deploy --config-env default

local-invoke: build
	sam local invoke DocumentAnalyzerFunction --event events/document-upload-valid.json

local-invoke-err: build
	sam local invoke DocumentAnalyzerFunction --event events/document-upload-missing-body.json

local-api: build
	sam local start-api

local: local-api

clean:
	rm -rf .aws-sam .pytest_cache htmlcov
	find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true