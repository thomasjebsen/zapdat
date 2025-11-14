"""
Quick test script for the analyzer
"""
import pandas as pd
import sys
sys.path.append('backend')
from analyzer import TableAnalyzer

# Load sample data
df = pd.read_csv('sample_data.csv')
print(f"Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
print(f"Columns: {list(df.columns)}")

# Analyze
analyzer = TableAnalyzer(df)
print(f"\nDetected column types:")
for col, col_type in analyzer.column_types.items():
    print(f"  {col}: {col_type}")

# Get overview
overview = analyzer.get_overview()
print(f"\nOverview:")
print(f"  Rows: {overview['rows']}")
print(f"  Columns: {overview['columns']}")
print(f"  Duplicates: {overview['duplicates']}")

# Test numeric analysis
print(f"\nNumeric column 'age' stats:")
age_analysis = analyzer.analyze_numeric('age')
for key, value in age_analysis['stats'].items():
    print(f"  {key}: {value}")

# Test categorical analysis
print(f"\nCategorical column 'department' stats:")
dept_analysis = analyzer.analyze_categorical('department')
for key, value in dept_analysis['stats'].items():
    print(f"  {key}: {value}")

print("\n✅ Analyzer test passed!")
