# Data Type Analysis Rules & Logic

This document outlines the comprehensive rules and logic for how different data types are analyzed and displayed in the EDA analyzer.

## Overview

The analyzer now provides type-specific analysis with smart cutoffs, outlier detection, and meaningful statistics tailored to each data type.

### Supported File Formats

The application supports a wide range of data file formats:
- **Tabular**: CSV, TSV, Excel (.xlsx, .xls)
- **JSON**: Structured JSON data
- **Big Data**: Parquet, Feather, ORC
- **Python**: Pickle (.pkl, .pickle)
- **Databases**: SQLite (.db, .sqlite, .sqlite3)
- **Scientific**: HDF5 (.h5, .hdf5)

---

## 1. CATEGORICAL Data

### Detection
- Boolean columns
- Binary 0/1 numeric values
- String columns with <50% unique values (low cardinality)

### Analysis Rules

#### Cardinality-Based Display Cutoffs
| Unique Values | Display Limit | Chart Limit | Level | Behavior |
|--------------|---------------|-------------|-------|----------|
| ≤10 | All | All | Low | Show all categories |
| 11-30 | Top 15 | Top 12 | Medium | Show top values + "X more" |
| 31-100 | Top 10 | Top 10 | High | Show top values with note |
| >100 | Top 10 | Top 10 | Very High | Warning: might be text/ID |

#### Statistics Provided
- **count**: Non-null values
- **unique**: Number of unique categories
- **mode**: Most common value
- **mode_freq**: Frequency of mode
- **mode_pct**: Percentage of mode
- **missing**: Null values count
- **diversity**: Diversity level assessment
  - Low diversity: <10% unique ratio
  - Medium diversity: 10-50% unique ratio
  - High diversity: 50-90% unique ratio
  - Very high diversity: >90% unique ratio

#### Display Features
- **Value Counts Table**: Shows category name, count, and percentage
- **Scrollable**: For many categories (max-height: 300px)
- **Summary Line**: "... + X more categories" when truncated
- **Bar Chart**: Visual representation of top categories

---

## 2. NUMERICAL Data

### Detection
- Numeric dtype columns (excluding boolean-like 0/1)

### Analysis Rules

#### Outlier Detection (IQR Method)
```
IQR = Q3 - Q1
Lower Bound = Q1 - 1.5 × IQR
Upper Bound = Q3 + 1.5 × IQR
Outliers = values < Lower Bound OR > Upper Bound
```

#### Distribution Shape Classification
| Skewness | Classification |
|----------|----------------|
| \|skew\| < 0.5 | Normal |
| 0.5 ≤ skew < 1 | Right-skewed |
| skew ≥ 1 | Highly right-skewed |
| -1 < skew ≤ -0.5 | Left-skewed |
| skew ≤ -1 | Highly left-skewed |

#### Statistics Provided
- **Basic Stats**: count, mean, median, std, min, max, Q25, Q75, missing
- **Outlier Stats**:
  - outliers: Count of outlier values
  - outlier_pct: Percentage of outliers
- **Distribution Stats**:
  - skewness: Numerical skewness value
  - distribution_shape: Human-readable classification
- **Special Counts**:
  - zeros: Count of zero values
  - negatives: Count of negative values
- **Typical Range**:
  - typical_min: Minimum without outliers
  - typical_max: Maximum without outliers

#### Display Features
- **Histogram**: Distribution visualization with auto-binning
- **All Stats**: Comprehensive statistics grid
- **Outlier Awareness**: Helps identify data quality issues

---

## 3. TEXT Data

### Detection
- String columns with ≥50% unique values (high cardinality)

### Analysis Rules

#### Pattern Detection
Automatically detects common patterns:
- **Email addresses**: Matches email regex (>50% match rate)
- **URLs**: Starts with http/https (>50% match rate)
- **Numeric IDs**: All digits (>50% match rate)
- **IDs/Codes**: Uppercase alphanumeric with dashes/underscores (>50% match rate)
- **Free text**: Default if no pattern detected

#### Statistics Provided
- **count**: Non-null values
- **unique**: Number of unique values
- **missing**: Null values count
- **avg_length**: Average text length
- **min_length**: Shortest text length
- **max_length**: Longest text length
- **pattern_hint**: Detected pattern type

#### Display Features
- **Sample Values**: Shows first 5 unique values
- **Pattern Hint**: Helps understand data nature
- **Length Stats**: Useful for validation and storage planning

---

## 4. DATETIME Data

### Detection
- Columns with datetime64 dtype

### Analysis Rules

#### Statistics Provided
- **count**: Non-null values
- **unique**: Number of unique dates
- **missing**: Null values count
- **min_date**: Earliest date
- **max_date**: Latest date
- **range_days**: Time span in days
- **most_common**: Most frequently occurring date

#### Display Features
- **Timeline Histogram**: Distribution over time
- **Date Range**: Clear start and end dates
- **Temporal Insights**: Understand data collection period

---

## Design Principles

### 1. Smart Cutoffs
- Prevent overwhelming users with too much data
- Always show most important/frequent values first
- Provide summary counts when data is truncated

### 2. Context-Aware Display
- Different data types need different statistics
- Show what's most useful for each type
- Balance detail with readability

### 3. Data Quality Insights
- Outlier detection for numerical data
- Diversity assessment for categorical data
- Pattern recognition for text data
- Missing value tracking for all types

### 4. User-Friendly Formatting
- Readable labels (e.g., "Mode %" instead of "mode_pct")
- Proper number formatting (commas for thousands, 2 decimals)
- Color-coded visualizations
- Scrollable sections for long lists

### 5. Performance Optimization
- Limit chart data points to prevent slowdowns
- Cap display items while maintaining usefulness
- Efficient calculations for large datasets

### 6. Progressive Disclosure (UI)
- **Basic stats always visible**: Show most important information first
- **Collapsible sections** (collapsed by default):
  - Advanced Statistics (numerical: outliers, skewness, quartiles)
  - Category Breakdown (categorical: full table with percentages)
  - Sample Values (text: example entries)
- **Larger chart area**: Minimum 400px height for better visualization
- **Clean hierarchy**: Reduces cognitive load, focuses on key insights

### 7. Custom Chart Builder
- **Interactive chart creation**: Users can build custom visualizations beyond auto-generated charts
- **Multiple chart types supported**:
  - Scatter Plot: X vs Y correlation with optional color/size encoding
  - Line Chart: Trends over time or continuous data
  - Box Plot: Compare distributions across multiple columns
  - Violin Plot: Distribution density visualization
  - Heatmap: Correlation matrix for all numeric columns
  - Pie Chart: Proportional breakdown of categories (with top N limit)
  - Bar Chart: Compare values across categories
- **Visual color schemes**: 10 pre-designed color palettes with live previews
  - Scientific: viridis, plasma, inferno
  - Sequential: blues, purples
  - Thematic: ocean, sunset, rainbow
  - Categorical: pastel, bold
- **Real-time updates**: Charts regenerate instantly when options change
- **Smart column filtering**: Only relevant columns shown for each chart type
- **Form-based interface**: Intuitive dropdowns and selectors for chart configuration

---

## Example Use Cases

### Low Cardinality Categorical (e.g., Gender)
- Shows: All 2-3 categories with exact counts and percentages
- Chart: Simple bar chart with all categories
- Useful for: Understanding distribution of small categorical sets

### High Cardinality Categorical (e.g., US States)
- Shows: Top 10-15 states by frequency
- Chart: Top 10 bars
- Note: "+ 35 more categories"
- Useful for: Identifying most common values without clutter

### Numerical with Outliers (e.g., Income)
- Shows: All standard stats plus outlier count
- Highlights: "127 outliers (12.7%)"
- Typical range: "Typical values: $25K - $150K"
- Useful for: Data cleaning and understanding typical vs extreme values

### Text IDs (e.g., User IDs)
- Shows: Sample IDs, length stats
- Pattern: "IDs/Codes"
- Useful for: Verifying ID format and uniqueness

### Datetime (e.g., Order Dates)
- Shows: Date range, most common date
- Chart: Distribution over time
- Useful for: Understanding temporal patterns

---

## Future Enhancements

Potential improvements to consider:
1. ~~**Correlation analysis** between numerical columns~~ ✅ **IMPLEMENTED** (via Custom Chart Builder heatmap)
2. ~~**Multi-file format support**~~ ✅ **IMPLEMENTED** (CSV, Excel, JSON, Parquet, Feather, Pickle, SQLite, HDF5, ORC)
3. **Automatic anomaly detection** beyond basic outliers
4. **Suggested data transformations** (e.g., log scale for skewed data)
5. **Export capabilities** for analysis results (PDF/HTML reports)
6. **Custom thresholds** for outlier/cardinality rules
7. **Geospatial detection** for coordinates or addresses
8. **Enhanced time series analysis** for datetime columns (seasonality, trends)
9. **Client-side processing** with danfo.js for privacy-first analysis (in roadmap)
