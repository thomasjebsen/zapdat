"""
Data analysis module for automatic EDA
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List
import math


def safe_float(value):
    """Convert a value to float, handling NaN and inf"""
    if pd.isna(value) or math.isinf(value):
        return None
    return float(value)


def safe_int(value):
    """Convert a value to int, handling NaN"""
    if pd.isna(value):
        return 0
    return int(value)


class TableAnalyzer:
    """Analyzes uploaded tables and generates insights"""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.column_types = {}
        self._detect_types()

    def _detect_types(self):
        """Detect the type of each column"""
        for col in self.df.columns:
            # Check for boolean type first
            if pd.api.types.is_bool_dtype(self.df[col]):
                self.column_types[col] = "categorical"
            # Check for datetime
            elif pd.api.types.is_datetime64_any_dtype(self.df[col]):
                self.column_types[col] = "datetime"
            # Check for numeric (but not boolean)
            elif pd.api.types.is_numeric_dtype(self.df[col]):
                # Check if it's actually just 0/1 values (boolean-like)
                unique_vals = self.df[col].dropna().unique()
                if len(unique_vals) <= 2 and set(unique_vals).issubset({0, 1, 0.0, 1.0}):
                    self.column_types[col] = "categorical"
                else:
                    self.column_types[col] = "numeric"
            else:
                # Check if it's categorical (low cardinality)
                unique_ratio = self.df[col].nunique() / len(self.df)
                if unique_ratio < 0.5:  # Less than 50% unique values
                    self.column_types[col] = "categorical"
                else:
                    self.column_types[col] = "text"

    def get_overview(self) -> Dict[str, Any]:
        """Get basic dataset overview"""
        return {
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "column_names": list(self.df.columns),
            "column_types": self.column_types,
            "missing_values": self.df.isnull().sum().to_dict(),
            "duplicates": int(self.df.duplicated().sum())
        }

    def analyze_numeric(self, column: str) -> Dict[str, Any]:
        """Analyze a numeric column with outlier detection and distribution analysis"""
        data = self.df[column].dropna()

        # Handle empty data
        if len(data) == 0:
            stats = {
                "count": 0,
                "mean": None,
                "median": None,
                "std": None,
                "min": None,
                "max": None,
                "q25": None,
                "q75": None,
                "missing": safe_int(self.df[column].isnull().sum()),
                "outliers": 0,
                "outlier_pct": 0,
                "zeros": 0,
                "negatives": 0,
                "skewness": None,
                "distribution_shape": "N/A"
            }
            # No plot for empty data
            return {"stats": stats}

        # Calculate basic stats
        q1 = data.quantile(0.25)
        q3 = data.quantile(0.75)
        iqr = q3 - q1

        # Outlier detection (IQR method)
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = data[(data < lower_bound) | (data > upper_bound)]
        outlier_count = len(outliers)
        outlier_pct = (outlier_count / len(data) * 100) if len(data) > 0 else 0

        # Non-outlier range
        non_outliers = data[(data >= lower_bound) & (data <= upper_bound)]
        non_outlier_min = safe_float(non_outliers.min()) if len(non_outliers) > 0 else None
        non_outlier_max = safe_float(non_outliers.max()) if len(non_outliers) > 0 else None

        # Skewness and distribution shape
        try:
            skew = data.skew()
            if abs(skew) < 0.5:
                dist_shape = "Normal"
            elif skew > 1:
                dist_shape = "Highly right-skewed"
            elif skew > 0.5:
                dist_shape = "Right-skewed"
            elif skew < -1:
                dist_shape = "Highly left-skewed"
            else:
                dist_shape = "Left-skewed"
        except:
            skew = None
            dist_shape = "Unknown"

        # Count zeros and negatives
        zero_count = safe_int((data == 0).sum())
        negative_count = safe_int((data < 0).sum())

        stats = {
            "count": safe_int(data.count()),
            "mean": safe_float(data.mean()),
            "median": safe_float(data.median()),
            "std": safe_float(data.std()),
            "min": safe_float(data.min()),
            "max": safe_float(data.max()),
            "q25": safe_float(q1),
            "q75": safe_float(q3),
            "missing": safe_int(self.df[column].isnull().sum()),
            "outliers": outlier_count,
            "outlier_pct": safe_float(outlier_pct),
            "zeros": zero_count,
            "negatives": negative_count,
            "skewness": safe_float(skew),
            "distribution_shape": dist_shape,
            "typical_min": non_outlier_min,
            "typical_max": non_outlier_max
        }

        # Create histogram only if we have data
        try:
            fig = px.histogram(
                data,
                x=data.values,
                title=f"Distribution of {column}",
                nbins=min(30, len(data.unique()))
            )
            fig.update_layout(
                showlegend=False,
                hovermode='x unified',
                xaxis_title=column,
                yaxis_title="Count"
            )

            return {
                "stats": stats,
                "plot": fig.to_json()
            }
        except Exception as e:
            # If plot creation fails, return stats only
            return {"stats": stats}

    def analyze_categorical(self, column: str) -> Dict[str, Any]:
        """Analyze a categorical column with smart cutoffs based on cardinality"""
        data = self.df[column].dropna()

        # Handle empty data
        if len(data) == 0:
            stats = {
                "count": 0,
                "unique": 0,
                "mode": None,
                "mode_freq": 0,
                "mode_pct": 0,
                "missing": safe_int(self.df[column].isnull().sum()),
                "diversity": "N/A"
            }
            return {"stats": stats, "value_counts": {}}

        value_counts = data.value_counts()
        unique_count = data.nunique()

        # Calculate mode (most common) percentage
        mode_freq = safe_int(value_counts.iloc[0]) if len(value_counts) > 0 else 0
        mode_pct = safe_float((mode_freq / len(data) * 100)) if len(data) > 0 else 0

        # Determine diversity level
        unique_ratio = unique_count / len(data) if len(data) > 0 else 0
        if unique_ratio < 0.1:
            diversity = "Low diversity"
        elif unique_ratio < 0.5:
            diversity = "Medium diversity"
        elif unique_ratio < 0.9:
            diversity = "High diversity"
        else:
            diversity = "Very high diversity (might be ID/text)"

        # Smart cutoff rules based on cardinality
        if unique_count <= 10:
            # Low cardinality: show all
            display_limit = unique_count
            chart_limit = unique_count
            cardinality_level = "low"
        elif unique_count <= 30:
            # Medium cardinality: show top 15
            display_limit = 15
            chart_limit = 12
            cardinality_level = "medium"
        elif unique_count <= 100:
            # High cardinality: show top 10 with note
            display_limit = 10
            chart_limit = 10
            cardinality_level = "high"
        else:
            # Very high cardinality: show top 10 with warning
            display_limit = 10
            chart_limit = 10
            cardinality_level = "very_high"

        stats = {
            "count": safe_int(data.count()),
            "unique": safe_int(unique_count),
            "mode": str(value_counts.index[0]) if len(value_counts) > 0 else None,
            "mode_freq": mode_freq,
            "mode_pct": mode_pct,
            "missing": safe_int(self.df[column].isnull().sum()),
            "diversity": diversity,
            "cardinality_level": cardinality_level
        }

        # Prepare value counts for display
        display_value_counts = {str(k): int(v) for k, v in value_counts.head(display_limit).items()}
        remaining_count = unique_count - display_limit

        # Create bar chart only if we have data
        try:
            top_values = value_counts.head(chart_limit)
            fig = px.bar(
                x=top_values.index.astype(str),
                y=top_values.values,
                title=f"Top Values in {column}" + (f" (showing {chart_limit} of {unique_count})" if unique_count > chart_limit else ""),
                labels={'x': column, 'y': 'Count'}
            )
            fig.update_layout(
                showlegend=False,
                hovermode='x unified',
                xaxis_title=column,
                yaxis_title="Count"
            )

            return {
                "stats": stats,
                "value_counts": display_value_counts,
                "remaining_categories": remaining_count if remaining_count > 0 else 0,
                "plot": fig.to_json()
            }
        except Exception as e:
            # If plot creation fails, return stats only
            return {
                "stats": stats,
                "value_counts": display_value_counts,
                "remaining_categories": remaining_count if remaining_count > 0 else 0
            }

    def analyze_text(self, column: str) -> Dict[str, Any]:
        """Analyze a text column with pattern detection"""
        data = self.df[column].dropna()

        # Handle empty data
        if len(data) == 0:
            stats = {
                "count": 0,
                "unique": 0,
                "missing": safe_int(self.df[column].isnull().sum()),
                "avg_length": 0,
                "min_length": 0,
                "max_length": 0,
                "pattern_hint": "N/A"
            }
            return {"stats": stats, "samples": []}

        # Convert to string and calculate lengths
        data_str = data.astype(str)
        lengths = data_str.str.len()

        # Get sample values (first 5 unique non-null)
        samples = data_str.unique()[:5].tolist()

        # Pattern detection
        pattern_hint = "Free text"
        if data_str.str.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$').sum() > len(data) * 0.5:
            pattern_hint = "Email addresses"
        elif data_str.str.match(r'^https?://').sum() > len(data) * 0.5:
            pattern_hint = "URLs"
        elif data_str.str.match(r'^\d+$').sum() > len(data) * 0.5:
            pattern_hint = "Numeric IDs (as text)"
        elif data_str.str.match(r'^[A-Z0-9-_]+$').sum() > len(data) * 0.5:
            pattern_hint = "IDs/Codes"

        stats = {
            "count": safe_int(data.count()),
            "unique": safe_int(data.nunique()),
            "missing": safe_int(self.df[column].isnull().sum()),
            "avg_length": safe_float(lengths.mean()),
            "min_length": safe_int(lengths.min()),
            "max_length": safe_int(lengths.max()),
            "pattern_hint": pattern_hint
        }

        return {
            "stats": stats,
            "samples": samples
        }

    def analyze_datetime(self, column: str) -> Dict[str, Any]:
        """Analyze a datetime column"""
        data = self.df[column].dropna()

        # Handle empty data
        if len(data) == 0:
            stats = {
                "count": 0,
                "unique": 0,
                "missing": safe_int(self.df[column].isnull().sum()),
                "min_date": None,
                "max_date": None,
                "range_days": 0,
                "most_common": None
            }
            return {"stats": stats}

        # Calculate stats
        min_date = data.min()
        max_date = data.max()
        date_range = (max_date - min_date).days if pd.notna(min_date) and pd.notna(max_date) else 0

        # Find most common date
        value_counts = data.value_counts()
        most_common = str(value_counts.index[0]) if len(value_counts) > 0 else None

        stats = {
            "count": safe_int(data.count()),
            "unique": safe_int(data.nunique()),
            "missing": safe_int(self.df[column].isnull().sum()),
            "min_date": str(min_date) if pd.notna(min_date) else None,
            "max_date": str(max_date) if pd.notna(max_date) else None,
            "range_days": safe_int(date_range),
            "most_common": most_common
        }

        # Create timeline plot if we have data
        try:
            # Create a histogram of dates
            fig = px.histogram(
                data,
                x=data.values,
                title=f"Distribution of {column}",
                nbins=min(30, len(data.unique()))
            )
            fig.update_layout(
                showlegend=False,
                hovermode='x unified',
                xaxis_title=column,
                yaxis_title="Count"
            )

            return {
                "stats": stats,
                "plot": fig.to_json()
            }
        except Exception as e:
            return {"stats": stats}

    def analyze_all(self) -> Dict[str, Any]:
        """Perform complete analysis on all columns"""
        overview = self.get_overview()
        column_analysis = {}

        for col in self.df.columns:
            col_type = self.column_types[col]

            if col_type == "numeric":
                column_analysis[col] = {
                    "type": col_type,
                    "analysis": self.analyze_numeric(col)
                }
            elif col_type == "categorical":
                column_analysis[col] = {
                    "type": col_type,
                    "analysis": self.analyze_categorical(col)
                }
            elif col_type == "datetime":
                column_analysis[col] = {
                    "type": col_type,
                    "analysis": self.analyze_datetime(col)
                }
            else:  # text
                column_analysis[col] = {
                    "type": col_type,
                    "analysis": self.analyze_text(col)
                }

        return {
            "overview": overview,
            "columns": column_analysis
        }
