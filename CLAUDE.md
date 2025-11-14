# CLAUDE.md - zapdat Project Guide

## Project Overview
**zapdat** is a data analysis project focused on providing powerful data analysis capabilities for data scientists and analysts.

## Project Type
Data Analysis & Processing

## Technology Stack
This project appears to be in early development. Common data analysis stacks include:
- Python (pandas, numpy, scikit-learn, matplotlib)
- SQL databases
- Jupyter notebooks
- Data visualization tools

## Recommended Agents

### 1. **data-validator**
**Purpose**: Validate data quality, check for missing values, outliers, and data integrity issues
**When to use**:
- After loading new datasets
- Before running analysis pipelines
- When debugging unexpected results

**Example usage**:
```
Review the loaded dataset and check for:
- Missing values and null handling
- Data type consistency
- Outliers and anomalies
- Duplicate records
```

### 2. **code-reviewer**
**Purpose**: Review data processing code for bugs, performance issues, and best practices
**When to use**:
- After implementing new analysis functions
- Before committing significant data transformation code
- When optimizing data pipelines

**Example usage**:
```
Review the data processing pipeline for:
- Efficient pandas operations (avoid iterrows)
- Proper error handling
- Memory management for large datasets
- Code readability and documentation
```

### 3. **test-writer**
**Purpose**: Generate unit tests for data processing functions
**When to use**:
- After creating new data transformation functions
- When building reusable analysis modules
- To ensure reproducibility

**Example usage**:
```
Create unit tests for the data cleaning functions that:
- Test edge cases (empty datasets, single row, all nulls)
- Verify transformation logic
- Check output data types and shapes
```

### 4. **documentation-generator**
**Purpose**: Generate documentation for analysis methods, functions, and results
**When to use**:
- After completing analysis workflows
- When creating reusable analysis modules
- To document findings and methodology

**Example usage**:
```
Generate documentation for the analysis pipeline including:
- Function docstrings with parameter descriptions
- Analysis methodology overview
- Data source descriptions
- Interpretation guidelines
```

### 5. **performance-optimizer**
**Purpose**: Optimize data processing code for speed and memory efficiency
**When to use**:
- When working with large datasets
- If pipelines are running slowly
- Before production deployment

**Example usage**:
```
Optimize the analysis pipeline for:
- Vectorized operations instead of loops
- Chunked processing for large files
- Efficient memory usage
- Parallel processing where applicable
```

### 6. **sql-assistant**
**Purpose**: Help write, optimize, and debug SQL queries for data extraction
**When to use**:
- When writing complex data queries
- Optimizing database performance
- Joining multiple data sources

**Example usage**:
```
Help write a SQL query to:
- Extract data with proper filtering
- Optimize query performance
- Handle complex joins
- Aggregate data efficiently
```

## Code Style Guidelines

### Python
- Follow PEP 8 style guide
- Use type hints for function parameters and returns
- Document functions with clear docstrings
- Prefer pandas/numpy vectorized operations over loops
- Handle missing data explicitly

### Data Processing Best Practices
- Always validate input data
- Log data transformations for reproducibility
- Use version control for datasets (consider DVC)
- Document data sources and update dates
- Create reproducible analysis pipelines

### Testing
- Write unit tests for data transformation functions
- Include edge case tests (empty data, nulls, outliers)
- Test with sample datasets before running on full data
- Validate output data shapes and types

## Common Tasks

### Loading and Exploring Data
```python
import pandas as pd

# Load data
df = pd.read_csv('data.csv')

# Basic exploration
print(df.info())
print(df.describe())
print(df.isnull().sum())
```

### Data Cleaning Pipeline
```python
def clean_data(df):
    """Clean and prepare data for analysis."""
    # Handle missing values
    # Remove duplicates
    # Fix data types
    # Remove outliers
    return df
```

### Analysis Workflow
1. Load and explore data
2. Clean and validate data
3. Perform exploratory data analysis (EDA)
4. Run statistical analysis or modeling
5. Visualize results
6. Document findings

## Directory Structure (Recommended)
```
zapdat/
├── data/           # Raw and processed data
├── notebooks/      # Jupyter notebooks for exploration
├── src/            # Source code for analysis modules
├── tests/          # Unit tests
├── reports/        # Analysis reports and visualizations
├── scripts/        # Utility scripts
└── docs/           # Documentation
```

## Development Workflow

1. **Explore**: Use notebooks for initial data exploration
2. **Develop**: Convert working code into modules in `src/`
3. **Test**: Write tests for data processing functions
4. **Document**: Add docstrings and update documentation
5. **Review**: Use code-reviewer agent before committing
6. **Deploy**: Package for production use if needed

## Agent Usage Tips

- **Use data-validator** early and often to catch issues
- **Use code-reviewer** before committing significant changes
- **Use test-writer** to ensure reproducibility
- **Use performance-optimizer** when working with large datasets
- **Use documentation-generator** to maintain clear documentation

## Notes for Claude

- Prioritize data quality and validation
- Always check for missing values and data types
- Suggest vectorized operations over loops
- Recommend appropriate visualization for insights
- Consider memory efficiency for large datasets
- Suggest proper error handling for data pipelines
- Encourage reproducible analysis practices
