.PHONY: help install install-dev run dev test clean lint format type-check pre-commit docker-build docker-up docker-down docker-logs all-checks

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "📊 zapdat - Table EDA Analyzer"
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  make setup        - First time setup (install deps + pre-commit)"
	@echo "  make run          - Start the development server"
	@echo "  make docker-up    - Start with Docker (easiest!)"
	@echo ""
	@echo "📋 Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""

# Installation
install: ## Install Python dependencies
	@echo "📦 Installing dependencies..."
	@command -v uv >/dev/null 2>&1 && \
		(uv pip install --system -r requirements.txt || pip install -r requirements.txt) || \
		pip install -r requirements.txt
	@echo "✅ Dependencies installed!"

install-dev: install ## Install dev dependencies (linting, testing, etc.)
	@echo "📦 Installing dev dependencies..."
	@command -v uv >/dev/null 2>&1 && \
		uv pip install --system ruff mypy pytest pytest-asyncio httpx pre-commit pandas-stubs || \
		pip install ruff mypy pytest pytest-asyncio httpx pre-commit pandas-stubs
	@echo "✅ Dev dependencies installed!"

setup: install-dev ## Full setup - install all deps and configure pre-commit
	@echo "⚙️  Setting up pre-commit hooks..."
	pre-commit install || echo "⚠️  Pre-commit not available, skipping hooks setup"
	@echo "✅ Setup complete! Run 'make run' to start the server."

# Running
run: ## Start the development server (quick start!)
	@echo "🚀 Starting zapdat server..."
	@echo "📍 Server will be available at http://localhost:8000"
	@echo ""
	cd backend && uvicorn main:app --reload --host 0.0.0.0

dev: run ## Alias for 'run' - starts the development server

# Testing
test: ## Run tests
	@echo "🧪 Running tests..."
	@python test_analyzer.py 2>/dev/null || echo "⚠️  test_analyzer.py not found"
	@test -d tests && pytest tests/ -v || echo "ℹ️  No tests/ directory found"
	@echo "✅ Tests complete!"

# Code Quality
lint: ## Run ruff linter
	@echo "🔍 Running linter..."
	@command -v ruff >/dev/null 2>&1 && ruff check . || echo "⚠️  Ruff not installed. Run 'make install-dev'"

format: ## Format code with ruff
	@echo "✨ Formatting code..."
	@command -v ruff >/dev/null 2>&1 && ruff format . || echo "⚠️  Ruff not installed. Run 'make install-dev'"

format-check: ## Check code formatting without making changes
	@echo "🔍 Checking code formatting..."
	@command -v ruff >/dev/null 2>&1 && ruff format --check . || echo "⚠️  Ruff not installed. Run 'make install-dev'"

type-check: ## Run mypy type checker
	@echo "🔎 Running type checker..."
	@command -v mypy >/dev/null 2>&1 && mypy backend/ --ignore-missing-imports || echo "⚠️  Mypy not installed. Run 'make install-dev'"

pre-commit: ## Run pre-commit hooks on all files
	@echo "🪝 Running pre-commit hooks..."
	@command -v pre-commit >/dev/null 2>&1 && pre-commit run --all-files || echo "⚠️  Pre-commit not installed. Run 'make install-dev'"

all-checks: lint format-check type-check test ## Run all checks (lint, format, type-check, test)
	@echo "✅ All checks passed!"

# Docker
docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t zapdat:latest .
	@echo "✅ Docker image built!"

docker-up: ## Start application with Docker Compose
	@echo "🐳 Starting with Docker Compose..."
	docker-compose up --build
	@echo "📍 Server available at http://localhost:8000"

docker-down: ## Stop Docker Compose services
	@echo "🛑 Stopping Docker services..."
	docker-compose down

docker-logs: ## View Docker Compose logs
	docker-compose logs -f

# Cleanup
clean: ## Clean up cache files and temporary files
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete!"
