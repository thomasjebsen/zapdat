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

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Server

```bash
cd backend
uvicorn main:app --reload
```

The app will be available at `http://localhost:8000`

### 3. Upload Your CSV

Open your browser and navigate to `http://localhost:8000`, then drag and drop your CSV file or click to upload.

## Project Structure

```
zapdat/
├── backend/
│   ├── main.py       # FastAPI application
│   └── analyzer.py   # Data analysis logic
├── frontend/
│   └── index.html    # Web interface
├── requirements.txt  # Python dependencies
└── sample_data.csv   # Sample CSV for testing
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
