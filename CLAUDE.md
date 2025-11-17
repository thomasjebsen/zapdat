# CLAUDE.md - Project Guide

## Product Vision

**zapdat** is a quick insights tool for CSV data analysis. Upload a file, instantly see the numbers that matter most.

**Key differentiator**: Client-side processing (privacy-first, no data sent to servers) - currently prototyping with FastAPI backend, migrating to danfo.js.

**Target users**: Data analysts and business users who need fast, essential insights without writing code.

## Current Architecture (v1 - Server-side)

```
zapdat/
├── backend/
│   ├── main.py       # FastAPI: /analyze endpoint
│   ├── analyzer.py   # TableAnalyzer class (type detection, stats, plots)
├── frontend/
│   └── index.html    # Drag-drop upload, Plotly visualizations
├── test_analyzer.py  # Unit tests
└── sample_data.csv   # Test data
```

**Tech stack**: FastAPI, pandas, plotly (Python) + Plotly.js (frontend)

## What It Does

1. **Auto type detection**: numeric, categorical, text, datetime
2. **Essential stats**: mean/median for numbers, top values for categories
3. **Quick visualizations**: histograms, bar charts
4. **Data quality**: missing values, duplicates

## Key Components

### `TableAnalyzer` (backend/analyzer.py)
- `_detect_types()` - Smart detection (e.g., 0/1 → categorical)
- `analyze_numeric()` - Stats + histogram
- `analyze_categorical()` - Frequencies + bar chart
- `analyze_all()` - Full dataset analysis
- **Safety**: Uses `safe_float()`, `safe_int()` for NaN/inf handling

### API (backend/main.py)
- `POST /analyze` - Upload CSV, get JSON analysis
- Error handling for empty/malformed files

### Frontend (frontend/index.html)
- Clean light theme UI
- Drag-and-drop upload
- Renders stats + Plotly charts

## Development Commands

```bash
# Run server
cd backend && uvicorn main:app --reload

# Run tests
pytest test_analyzer.py -v
```

## Slash Commands (Specialized Agents)

Invoke with `/command` to delegate tasks:

- `/dev` - Backend features, bug fixes, tests (e.g., `/dev Add correlation matrix`)
- `/design` - UI/UX improvements (e.g., `/design Improve error messages`)
- `/test` - Quality assurance, edge cases (e.g., `/test Verify empty CSV handling`)

## Priority Roadmap

1. **Client-side processing** (danfo.js) - THE differentiator
2. Correlation matrix for numeric columns
3. DateTime analysis with time series plots
4. Export reports (JSON/HTML)
5. Excel/XLSX support

## Development Guidelines

- **Preserve safety**: Always use `safe_float()`, `safe_int()` for data conversions
- **Test edge cases**: Empty data, all NaN, single column, large files
- **JSON serialization**: Ensure all outputs are JSON-safe
- **Keep it fast**: Focus on essential insights, not exhaustive analysis

## Quick Reference

**Add analysis logic**: `backend/analyzer.py`
**API changes**: `backend/main.py`
**UI updates**: `frontend/index.html`
**Tests**: `test_analyzer.py`
