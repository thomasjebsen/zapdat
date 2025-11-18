"""
Data analysis module for automatic EDA
"""

import math
import re
from typing import Any

import pandas as pd
import plotly.express as px


# Semantic type detection patterns
SEMANTIC_PATTERNS = {
    "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "url": r"^https?://[\w\-\.]+(:\d+)?(/[\w\-\./?%&=]*)?$",
    "phone": r"^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}$",
    "currency": r"^[\$€£¥₹]?\s*-?\d{1,3}(,?\d{3})*(\.\d{2})?(\s*[\$€£¥₹])?$",
    "percentage": r"^-?\d+(\.\d+)?%$",
    "uuid": r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
    "ipv4": r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
    "ipv6": r"^(([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2})$",
    "postal_code_us": r"^\d{5}(-\d{4})?$",
    "postal_code_uk": r"^[A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}$",
    "postal_code_ca": r"^[A-Z]\d[A-Z]\s?\d[A-Z]\d$",
    "credit_card": r"^(\*{12}\d{4}|\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4})$",
    "boolean_text": r"^(true|false|yes|no|y|n|t|f|0|1)$",
    "iso_date": r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?)?$",
    "us_date": r"^(0?[1-9]|1[0-2])[-/](0?[1-9]|[12]\d|3[01])[-/]\d{2,4}$",
    "eu_date": r"^(0?[1-9]|[12]\d|3[01])[-/.](0?[1-9]|1[0-2])[-/.]\d{2,4}$",
}

# Datetime parsing formats
DATETIME_FORMATS = [
    "%Y-%m-%d",  # 2024-01-15
    "%Y-%m-%dT%H:%M:%S",  # 2024-01-15T10:30:00
    "%Y-%m-%dT%H:%M:%S.%f",  # 2024-01-15T10:30:00.123
    "%Y-%m-%dT%H:%M:%SZ",  # 2024-01-15T10:30:00Z
    "%m/%d/%Y",  # 01/15/2024
    "%m-%d-%Y",  # 01-15-2024
    "%d/%m/%Y",  # 15/01/2024
    "%d-%m-%Y",  # 15-01-2024
    "%d.%m.%Y",  # 15.01.2024
    "%b %d, %Y",  # Jan 15, 2024
    "%B %d, %Y",  # January 15, 2024
    "%d %b %Y",  # 15 Jan 2024
    "%d %B %Y",  # 15 January 2024
    "%Y/%m/%d",  # 2024/01/15
]


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

    def _detect_semantic_type(self, column: pd.Series) -> tuple[str | None, float]:
        """
        Detect semantic type of a column using pattern matching.

        Returns:
            tuple: (semantic_type, confidence_score)
                - semantic_type: The detected semantic type or None
                - confidence_score: Float between 0.0-1.0 indicating match percentage
        """
        # Skip empty columns
        if len(column) == 0:
            return None, 0.0

        # Sample up to 500 non-null values for performance
        sample_data = column.dropna().astype(str).head(500)

        if len(sample_data) == 0:
            return None, 0.0

        sample_size = len(sample_data)

        # Define pattern priority order (more specific patterns first)
        # This prevents phone pattern from matching IPs, etc.
        pattern_order = [
            "uuid",
            "email",
            "url",
            "credit_card",
            "ipv4",
            "ipv6",
            "iso_date",
            "us_date",
            "eu_date",
            "postal_code_us",
            "postal_code_uk",
            "postal_code_ca",
            "percentage",
            "currency",
            "boolean_text",
            "phone",  # Phone last because it's very permissive
        ]

        # Test patterns in priority order
        for semantic_type in pattern_order:
            pattern = SEMANTIC_PATTERNS[semantic_type]
            try:
                # Count matches (case-insensitive for boolean_text and postal codes)
                if semantic_type in ["boolean_text", "postal_code_uk", "postal_code_ca"]:
                    matches = sample_data.str.match(pattern, case=False, flags=re.IGNORECASE).sum()
                else:
                    matches = sample_data.str.match(pattern, case=True).sum()

                confidence = matches / sample_size

                # Return first pattern that meets threshold (>= 70%)
                if confidence >= 0.7:
                    return semantic_type, confidence
            except Exception:
                # Skip pattern if regex matching fails
                continue

        return None, 0.0

    def _try_parse_datetime(self, column: pd.Series) -> tuple[pd.Series | None, float]:
        """
        Attempt to parse a column as datetime using multiple formats.

        Returns:
            tuple: (parsed_series, confidence_score)
                - parsed_series: Successfully parsed datetime Series or None
                - confidence_score: Float between 0.0-1.0 indicating success rate
        """
        # Skip if already datetime
        if pd.api.types.is_datetime64_any_dtype(column):
            return column, 1.0

        # Sample non-null values
        sample_data = column.dropna().head(500)

        if len(sample_data) == 0:
            return None, 0.0

        sample_size = len(sample_data)
        best_parsed = None
        best_confidence = 0.0

        # Try pandas default parsing first
        try:
            parsed = pd.to_datetime(column, errors='coerce')
            valid_count = parsed.notna().sum()
            confidence = valid_count / len(column.dropna()) if len(column.dropna()) > 0 else 0.0

            if confidence > best_confidence:
                best_confidence = confidence
                best_parsed = parsed
        except Exception:
            pass

        # Try each format explicitly
        for fmt in DATETIME_FORMATS:
            try:
                parsed = pd.to_datetime(column, format=fmt, errors='coerce')
                valid_count = parsed.notna().sum()
                confidence = valid_count / len(column.dropna()) if len(column.dropna()) > 0 else 0.0

                if confidence > best_confidence:
                    best_confidence = confidence
                    best_parsed = parsed
            except Exception:
                continue

        # Return parsed series if confidence is above 70%
        if best_confidence >= 0.7:
            return best_parsed, best_confidence

        return None, best_confidence

    def _detect_types(self):
        """Detect the type of each column with semantic pattern recognition"""
        for col in self.df.columns:
            base_type = None
            semantic_type = None
            confidence = 1.0
            non_null_count = self.df[col].count()
            unique_count = self.df[col].nunique()

            # Check for boolean type first
            if pd.api.types.is_bool_dtype(self.df[col]):
                base_type = "categorical"
                semantic_type = "boolean"

            # Check for datetime
            elif pd.api.types.is_datetime64_any_dtype(self.df[col]):
                base_type = "datetime"

            # Check for numeric (but not boolean)
            elif pd.api.types.is_numeric_dtype(self.df[col]):
                # Check if it's actually just 0/1 values (boolean-like)
                unique_vals = self.df[col].dropna().unique()
                if len(unique_vals) <= 2 and set(unique_vals).issubset({0, 1}):
                    base_type = "categorical"
                    semantic_type = "boolean"
                else:
                    # Check if numeric column might be a semantic type (e.g., postal code)
                    detected_semantic, sem_confidence = self._detect_semantic_type(self.df[col])

                    if detected_semantic == "postal_code_us":
                        # Postal codes should be treated as categorical/text
                        base_type = "categorical"
                        semantic_type = detected_semantic
                        confidence = sem_confidence
                    else:
                        base_type = "numeric"

            else:
                # Non-numeric, non-datetime column - could be text, categorical, or datetime string
                # First, try to detect semantic types
                detected_semantic, sem_confidence = self._detect_semantic_type(self.df[col])

                # Check if it's a datetime string
                if detected_semantic in ["iso_date", "us_date", "eu_date"]:
                    parsed_datetime, dt_confidence = self._try_parse_datetime(self.df[col])
                    if parsed_datetime is not None:
                        # Replace the column with parsed datetime
                        self.df[col] = parsed_datetime
                        base_type = "datetime"
                        semantic_type = detected_semantic
                        confidence = dt_confidence
                    else:
                        base_type = "text"
                        semantic_type = detected_semantic
                        confidence = sem_confidence

                # Check for boolean text patterns
                elif detected_semantic == "boolean_text":
                    base_type = "categorical"
                    semantic_type = "boolean_text"
                    confidence = sem_confidence

                # Check for other semantic types
                elif detected_semantic is not None:
                    # Determine if it should be categorical or text based on cardinality
                    unique_ratio = unique_count / non_null_count if non_null_count > 0 else 0

                    # Enhanced categorical detection logic
                    if unique_count < 50 or unique_ratio < 0.5:
                        base_type = "categorical"
                    else:
                        base_type = "text"

                    semantic_type = detected_semantic
                    confidence = sem_confidence

                else:
                    # No semantic pattern detected - use cardinality-based detection
                    unique_ratio = unique_count / non_null_count if non_null_count > 0 else 0

                    # Enhanced categorical detection with multiple heuristics
                    is_categorical = False

                    # Rule 1: Low unique count (< 50 values)
                    if unique_count < 50:
                        is_categorical = True

                    # Rule 2: Low diversity (< 50% unique)
                    elif unique_ratio < 0.5:
                        is_categorical = True

                    # Rule 3: Medium cardinality with low diversity (< 100 values and < 30% unique)
                    elif unique_count < 100 and unique_ratio < 0.3:
                        is_categorical = True

                    if is_categorical:
                        base_type = "categorical"
                    else:
                        base_type = "text"

            # Store type information
            self.column_types[col] = {
                "type": base_type,
                "semantic_type": semantic_type,
                "confidence": confidence,
            }

    def get_overview(self) -> dict[str, Any]:
        """Get basic dataset overview"""
        return {
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "column_names": list(self.df.columns),
            "column_types": self.column_types,  # Now includes type, semantic_type, confidence
            "missing_values": self.df.isnull().sum().to_dict(),
            "duplicates": int(self.df.duplicated().sum()),
        }

    def analyze_numeric(self, column: str) -> dict[str, Any]:
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
                "distribution_shape": "N/A",
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
        except Exception:
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
            "typical_max": non_outlier_max,
        }

        # Create histogram only if we have data
        try:
            fig = px.histogram(
                data,
                x=data.values,
                title=f"Distribution of {column}",
                nbins=min(30, len(data.unique())),
            )
            fig.update_layout(
                showlegend=False, hovermode="x unified", xaxis_title=column, yaxis_title="Count"
            )

            return {"stats": stats, "plot": fig.to_json()}
        except Exception:
            # If plot creation fails, return stats only
            return {"stats": stats}

    def analyze_categorical(self, column: str) -> dict[str, Any]:
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
                "diversity": "N/A",
            }
            return {"stats": stats, "value_counts": {}}

        value_counts = data.value_counts()
        unique_count = data.nunique()

        # Calculate mode (most common) percentage
        mode_freq = safe_int(value_counts.iloc[0]) if len(value_counts) > 0 else 0
        mode_pct = safe_float(mode_freq / len(data) * 100) if len(data) > 0 else 0

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
            "cardinality_level": cardinality_level,
        }

        # Prepare value counts for display
        display_value_counts = {str(k): int(v) for k, v in value_counts.head(display_limit).items()}
        remaining_count = unique_count - display_limit

        # Create bar chart only if we have data
        try:
            top_values = value_counts.head(chart_limit)
            chart_title = f"Top Values in {column}"
            if unique_count > chart_limit:
                chart_title += f" (showing {chart_limit} of {unique_count})"
            fig = px.bar(
                x=top_values.index.astype(str),
                y=top_values.values,
                title=chart_title,
                labels={"x": column, "y": "Count"},
            )
            fig.update_layout(
                showlegend=False, hovermode="x unified", xaxis_title=column, yaxis_title="Count"
            )

            return {
                "stats": stats,
                "value_counts": display_value_counts,
                "remaining_categories": remaining_count if remaining_count > 0 else 0,
                "plot": fig.to_json(),
            }
        except Exception:
            # If plot creation fails, return stats only
            return {
                "stats": stats,
                "value_counts": display_value_counts,
                "remaining_categories": remaining_count if remaining_count > 0 else 0,
            }

    def analyze_text(self, column: str) -> dict[str, Any]:
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
                "pattern_hint": "N/A",
            }
            return {"stats": stats, "samples": []}

        # Convert to string and calculate lengths
        data_str = data.astype(str)
        lengths = data_str.str.len()

        # Get sample values (first 5 unique non-null)
        samples = data_str.unique()[:5].tolist()

        # Pattern detection
        pattern_hint = "Free text"
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if data_str.str.match(email_pattern).sum() > len(data) * 0.5:
            pattern_hint = "Email addresses"
        elif data_str.str.match(r"^https?://").sum() > len(data) * 0.5:
            pattern_hint = "URLs"
        elif data_str.str.match(r"^\d+$").sum() > len(data) * 0.5:
            pattern_hint = "Numeric IDs (as text)"
        elif data_str.str.match(r"^[A-Z0-9-_]+$").sum() > len(data) * 0.5:
            pattern_hint = "IDs/Codes"

        stats = {
            "count": safe_int(data.count()),
            "unique": safe_int(data.nunique()),
            "missing": safe_int(self.df[column].isnull().sum()),
            "avg_length": safe_float(lengths.mean()),
            "min_length": safe_int(lengths.min()),
            "max_length": safe_int(lengths.max()),
            "pattern_hint": pattern_hint,
        }

        return {"stats": stats, "samples": samples}

    def analyze_datetime(self, column: str) -> dict[str, Any]:
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
                "most_common": None,
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
            "most_common": most_common,
        }

        # Create timeline plot if we have data
        try:
            # Create a histogram of dates
            fig = px.histogram(
                data,
                x=data.values,
                title=f"Distribution of {column}",
                nbins=min(30, len(data.unique())),
            )
            fig.update_layout(
                showlegend=False, hovermode="x unified", xaxis_title=column, yaxis_title="Count"
            )

            return {"stats": stats, "plot": fig.to_json()}
        except Exception:
            return {"stats": stats}

    def analyze_all(self) -> dict[str, Any]:
        """Perform complete analysis on all columns"""
        overview = self.get_overview()
        column_analysis = {}

        for col in self.df.columns:
            col_info = self.column_types[col]
            col_type = col_info["type"]
            semantic_type = col_info.get("semantic_type")
            confidence = col_info.get("confidence", 1.0)

            # Perform type-specific analysis
            if col_type == "numeric":
                analysis = self.analyze_numeric(col)
            elif col_type == "categorical":
                analysis = self.analyze_categorical(col)
            elif col_type == "datetime":
                analysis = self.analyze_datetime(col)
            else:  # text
                analysis = self.analyze_text(col)

            # Add type information to the analysis
            column_analysis[col] = {
                "type": col_type,
                "semantic_type": semantic_type,
                "confidence": safe_float(confidence),
                "analysis": analysis,
            }

        return {"overview": overview, "columns": column_analysis}
