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
        """Analyze a numeric column"""
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
                "missing": safe_int(self.df[column].isnull().sum())
            }
        else:
            stats = {
                "count": safe_int(data.count()),
                "mean": safe_float(data.mean()),
                "median": safe_float(data.median()),
                "std": safe_float(data.std()),
                "min": safe_float(data.min()),
                "max": safe_float(data.max()),
                "q25": safe_float(data.quantile(0.25)),
                "q75": safe_float(data.quantile(0.75)),
                "missing": safe_int(self.df[column].isnull().sum())
            }

        # Create histogram
        fig = px.histogram(
            self.df,
            x=column,
            title=f"Distribution of {column}",
            nbins=30
        )
        fig.update_layout(
            showlegend=False,
            hovermode='x unified'
        )

        return {
            "stats": stats,
            "plot": fig.to_json()
        }

    def analyze_categorical(self, column: str) -> Dict[str, Any]:
        """Analyze a categorical column"""
        data = self.df[column].dropna()
        value_counts = data.value_counts()

        stats = {
            "count": safe_int(data.count()),
            "unique": safe_int(data.nunique()),
            "top": str(value_counts.index[0]) if len(value_counts) > 0 else None,
            "top_freq": safe_int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
            "missing": safe_int(self.df[column].isnull().sum())
        }

        # Create bar chart (top 10 values)
        top_values = value_counts.head(10)
        fig = px.bar(
            x=top_values.index,
            y=top_values.values,
            title=f"Top Values in {column}",
            labels={'x': column, 'y': 'Count'}
        )
        fig.update_layout(
            showlegend=False,
            hovermode='x unified'
        )

        return {
            "stats": stats,
            "value_counts": value_counts.head(20).to_dict(),
            "plot": fig.to_json()
        }

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
            else:
                # Basic stats for text columns
                column_analysis[col] = {
                    "type": col_type,
                    "analysis": {
                        "stats": {
                            "count": safe_int(self.df[col].count()),
                            "unique": safe_int(self.df[col].nunique()),
                            "missing": safe_int(self.df[col].isnull().sum())
                        }
                    }
                }

        return {
            "overview": overview,
            "columns": column_analysis
        }
