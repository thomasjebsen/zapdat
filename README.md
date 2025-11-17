# 📊 zapdat - Table EDA Analyzer

Automatic Exploratory Data Analysis for your CSV files. Upload a table and instantly get insights!

## Features

- 🚀 **Automatic Type Detection** - Identifies numeric, categorical, boolean, and text columns
- 📈 **Interactive Visualizations** - Hover over charts to explore your data (powered by Plotly)
- 📊 **Smart Statistics** - Type-specific analysis (mean/median for numbers, frequency for categories)
- 🎯 **Data Quality Checks** - Missing values, duplicates, and more
- ⚡ **Fast & Simple** - Just upload and analyze
- 🎨 **Modern Design** - Clean, minimal interface with light theme

## Quick Start

### 🐳 Docker Setup (Easiest!)

The fastest way to get started with zero configuration:

```bash
docker-compose up
```

That's it! Visit `http://localhost:8000` and start analyzing your data.

### 🚀 Local Development Setup

#### Option 1: Using Make (Recommended)

```bash
# First time setup (install deps + pre-commit hooks)
make setup

# Start the development server
make run
```

Visit `http://localhost:8000` to use the app!

#### Option 2: Manual Setup

```bash
# Install dependencies (uses uv if available, falls back to pip)
pip install -r requirements.txt

# Run the server
cd backend
uvicorn main:app --reload
```

### 📋 Development Commands

Run `make help` to see all available commands:

**Quick Start**
- `make setup` - First time setup (install all dependencies + pre-commit)
- `make run` - Start the development server
- `make docker-up` - Start with Docker Compose

**Development**
- `make install` - Install Python dependencies
- `make install-dev` - Install dev dependencies (linting, testing, etc.)
- `make test` - Run tests
- `make clean` - Clean up cache files

**Code Quality** (2025 standards!)
- `make lint` - Run ruff linter
- `make format` - Auto-format code with ruff
- `make type-check` - Run mypy type checker
- `make pre-commit` - Run all pre-commit hooks
- `make all-checks` - Run all quality checks at once

**Docker**
- `make docker-build` - Build Docker image
- `make docker-up` - Start with Docker Compose
- `make docker-down` - Stop Docker services
- `make docker-logs` - View Docker logs

### 🛠️ Development Tools

This project uses modern 2025 Python tooling:

- **[uv](https://github.com/astral-sh/uv)** - Ultra-fast Python package installer (optional, falls back to pip)
- **[ruff](https://github.com/astral-sh/ruff)** - Lightning-fast Python linter and formatter
- **[mypy](https://mypy-lang.org/)** - Static type checker
- **[pre-commit](https://pre-commit.com/)** - Git hooks for code quality
- **[pytest](https://pytest.org/)** - Modern testing framework
- **GitHub Actions** - Automated CI/CD pipeline

### 🔄 CI/CD Pipeline

Every push and pull request automatically runs:
- ✅ Ruff linting and formatting checks
- ✅ Mypy type checking
- ✅ Pytest test suite
- ✅ Docker build verification

## Project Structure

```
zapdat/
├── backend/
│   ├── main.py              # FastAPI application
│   └── analyzer.py          # Data analysis logic
├── frontend/
│   └── index.html           # Web interface
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI/CD pipeline
├── pyproject.toml           # Modern Python project config (PEP 621)
├── requirements.txt         # Python dependencies (legacy support)
├── Dockerfile               # Production Docker image
├── Dockerfile.dev           # Development Docker image
├── docker-compose.yml       # Docker Compose configuration
├── .pre-commit-config.yaml  # Pre-commit hooks configuration
├── Makefile                 # Development commands
└── sample_data.csv          # Sample CSV for testing
```

## What Gets Analyzed

### Numeric Columns
- Mean, median, standard deviation
- Min, max, quartiles
- Distribution histogram

### Categorical Columns
- Unique values count
- Top values and frequencies
- Bar chart of top categories

### All Columns
- Missing value count
- Data type detection
- Basic statistics

## Roadmap

- [ ] Client-side processing (no data sent to server)
- [ ] Excel/XLSX support
- [ ] Correlation matrix visualization
- [ ] Box plots for outlier detection
- [ ] DateTime analysis
- [ ] Export analysis as PDF/HTML

## Tech Stack

- **Backend**: FastAPI + pandas + plotly
- **Frontend**: Vanilla JavaScript + Plotly.js
- **Future**: Migration to danfo.js for client-side processing
