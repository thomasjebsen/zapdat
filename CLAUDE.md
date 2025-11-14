# CLAUDE.md - Project Guide for AI Assistants

## Project Overview

**zapdat** is a Table EDA (Exploratory Data Analysis) Analyzer that provides automatic data insights for CSV files. Users upload CSV files and instantly receive comprehensive statistical analysis and interactive visualizations.

### Core Purpose
- Automatic type detection (numeric, categorical, boolean, text)
- Smart statistical analysis based on column types
- Interactive visualizations using Plotly
- Data quality checks (missing values, duplicates)
- Modern, user-friendly interface

## Architecture

### Tech Stack
- **Backend**: Python 3.x with FastAPI
- **Data Processing**: pandas, numpy
- **Visualization**: plotly
- **Frontend**: Vanilla JavaScript with Plotly.js
- **Server**: uvicorn (ASGI server)

### Project Structure
```
zapdat/
├── backend/
│   ├── main.py           # FastAPI app with endpoints
│   ├── analyzer.py       # Core analysis logic (TableAnalyzer class)
├── frontend/
│   └── index.html        # Single-page web interface
├── requirements.txt      # Python dependencies
├── test_analyzer.py      # Unit tests for analyzer
├── sample_data.csv       # Sample data for testing
└── README.md            # User documentation
```

## Key Components

### 1. FastAPI Backend (`backend/main.py`)
- **Endpoints**:
  - `GET /` - Serves the frontend HTML
  - `POST /analyze` - Accepts CSV upload, returns analysis
  - `GET /health` - Health check endpoint
- **Features**: CORS middleware, file validation, error handling

### 2. TableAnalyzer (`backend/analyzer.py`)
- **Type Detection**: Automatically detects column types
- **Analysis Methods**:
  - `analyze_numeric()` - Mean, median, std dev, quartiles, histograms
  - `analyze_categorical()` - Unique counts, frequencies, bar charts
  - `analyze_all()` - Complete dataset analysis
- **Data Safety**: Handles NaN, infinity, empty data gracefully

### 3. Frontend (`frontend/index.html`)
- Modern glassmorphism design with dark theme
- Drag-and-drop file upload
- Real-time analysis display
- Interactive Plotly visualizations

## Common Development Tasks

### Running the Application
```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
cd backend
uvicorn main:app --reload
```

### Running Tests
```bash
pytest test_analyzer.py -v
```

## Suggested AI Agents for Subtasks

When working on this project, consider using specialized agents for these tasks:

### 1. **test-runner**
**When to use**: Running and fixing tests
**Tasks**:
- Run pytest and report failures
- Analyze test output and suggest fixes
- Add new test cases for new features
- Ensure test coverage

**Example**: "Run the test suite and fix any failing tests"

### 2. **bug-fixer**
**When to use**: Debugging issues or errors
**Tasks**:
- Analyze error messages and stack traces
- Debug type detection issues
- Fix data handling edge cases (empty files, malformed CSVs)
- Handle NaN/infinity values in statistics

**Example**: "Debug why categorical columns with 100% missing values crash the analyzer"

### 3. **feature-implementer**
**When to use**: Adding new functionality
**Tasks**:
- Implement roadmap features (correlation matrix, box plots, datetime analysis)
- Add support for new file formats (Excel/XLSX)
- Implement export functionality (PDF, HTML reports)
- Add new statistical measures or visualizations

**Example**: "Add a correlation matrix visualization for numeric columns"

### 4. **api-developer**
**When to use**: Working on backend endpoints
**Tasks**:
- Add new FastAPI endpoints
- Improve error handling and validation
- Add authentication/rate limiting
- Implement batch upload functionality

**Example**: "Add an endpoint to compare two CSV files"

### 5. **frontend-developer**
**When to use**: UI/UX improvements
**Tasks**:
- Enhance the web interface design
- Add interactive features (filtering, sorting)
- Improve visualization layouts
- Add dark/light theme toggle
- Implement responsive design

**Example**: "Add a filter to show only numeric columns in the analysis"

### 6. **performance-optimizer**
**When to use**: Improving speed or efficiency
**Tasks**:
- Optimize pandas operations for large files
- Implement chunked file reading
- Add caching for repeated analyses
- Profile and optimize slow functions

**Example**: "Optimize the analyzer to handle CSV files larger than 100MB"

### 7. **documentation-writer**
**When to use**: Creating or updating docs
**Tasks**:
- Update README with new features
- Add API documentation
- Create user guides
- Write inline code documentation

**Example**: "Add docstrings to all functions in analyzer.py"

### 8. **refactoring-specialist**
**When to use**: Code quality improvements
**Tasks**:
- Extract repeated code into utilities
- Improve code organization
- Add type hints
- Implement design patterns

**Example**: "Refactor analyzer.py to separate visualization logic from statistics calculation"

### 9. **security-auditor**
**When to use**: Security reviews
**Tasks**:
- Review file upload security
- Check for injection vulnerabilities
- Validate CORS configuration
- Review dependency vulnerabilities

**Example**: "Audit the file upload endpoint for security vulnerabilities"

### 10. **integration-tester**
**When to use**: End-to-end testing
**Tasks**:
- Test the full upload-analyze-display flow
- Test with various CSV formats and edge cases
- Verify visualization rendering
- Cross-browser testing

**Example**: "Test the application with various CSV files including edge cases"

## Development Guidelines

### Adding New Features
1. Update `analyzer.py` for new analysis methods
2. Modify the `/analyze` endpoint if needed
3. Update frontend to display new results
4. Add tests in `test_analyzer.py`
5. Update README.md

### Code Quality
- Use type hints in Python code
- Handle edge cases (empty data, NaN, infinity)
- Add error handling with descriptive messages
- Write unit tests for new functions
- Keep functions focused and small

### Testing Strategy
- Unit tests for analyzer functions
- Test edge cases (empty files, single column, all NaN)
- Test type detection accuracy
- Validate JSON output structure

## Roadmap Items

Priority tasks for future development:
1. Client-side processing with danfo.js (no server upload needed)
2. Excel/XLSX file support
3. Correlation matrix for numeric columns
4. Box plots for outlier detection
5. DateTime column analysis with time series plots
6. Export analysis reports as PDF/HTML
7. Comparison mode for multiple datasets
8. Custom statistical tests

## Quick Reference

### Key Files to Modify
- **Add analysis features**: `backend/analyzer.py`
- **Add API endpoints**: `backend/main.py`
- **Update UI**: `frontend/index.html`
- **Add tests**: `test_analyzer.py`
- **Update dependencies**: `requirements.txt`

### Important Classes/Functions
- `TableAnalyzer` - Main analysis class
- `_detect_types()` - Column type detection logic
- `analyze_numeric()` - Numeric column analysis
- `analyze_categorical()` - Categorical column analysis
- `safe_float()`, `safe_int()` - Safe type conversion utilities

## Tips for AI Assistants

1. **Always test after changes**: Run tests and verify the app still works
2. **Preserve error handling**: The code has robust error handling - maintain it
3. **Type safety**: Use the safe_float() and safe_int() utilities for data conversions
4. **Check edge cases**: Empty data, all NaN values, single row/column
5. **JSON serialization**: Ensure all returned data is JSON-serializable
6. **Frontend sync**: If backend output changes, update frontend parsing
7. **Plotly versions**: Keep plotly version compatible between Python and JS

## Getting Help

- **Tests**: Run `pytest test_analyzer.py -v` to see what's working
- **API docs**: Visit `http://localhost:8000/docs` when server is running
- **Sample data**: Use `sample_data.csv` for quick testing
- **Logs**: Check uvicorn output for server errors
