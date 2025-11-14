.PHONY: help install run dev test clean

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "📊 zapdat - Table EDA Analyzer"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

install: ## Install Python dependencies
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed!"

run: ## Start the development server (quick start!)
	@echo "🚀 Starting zapdat server..."
	@echo "📍 Server will be available at http://localhost:8000"
	@echo ""
	cd backend && uvicorn main:app --reload --host 0.0.0.0

dev: run ## Alias for 'run' - starts the development server

test: ## Run tests
	@echo "🧪 Running tests..."
	python test_analyzer.py
	@echo "✅ Tests complete!"

clean: ## Clean up cache files and temporary files
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete!"

setup: install ## Full setup - install dependencies
	@echo "✅ Setup complete! Run 'make run' to start the server."
