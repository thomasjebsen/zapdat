"""
Custom visualization generators for sexy charts
"""
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class ChartGenerator:
    """Generates custom visualizations based on user preferences"""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def _get_color_scheme(self, scheme: str) -> List[str]:
        """Get color palette based on scheme name"""
        schemes = {
            'viridis': px.colors.sequential.Viridis,
            'plasma': px.colors.sequential.Plasma,
            'inferno': px.colors.sequential.Inferno,
            'blues': px.colors.sequential.Blues,
            'purples': px.colors.sequential.Purples,
            'ocean': px.colors.sequential.Teal,
            'sunset': px.colors.sequential.Sunset,
            'rainbow': px.colors.qualitative.Vivid,
            'pastel': px.colors.qualitative.Pastel,
            'bold': px.colors.qualitative.Bold,
        }
        return schemes.get(scheme, px.colors.qualitative.Plotly)

    def scatter_plot(
        self,
        x_column: str,
        y_column: str,
        color_column: Optional[str] = None,
        size_column: Optional[str] = None,
        title: Optional[str] = None,
        color_scheme: str = 'viridis'
    ) -> str:
        """Create an interactive scatter plot"""
        if x_column not in self.df.columns or y_column not in self.df.columns:
            raise ValueError(f"Columns {x_column} or {y_column} not found")

        # Filter out rows with missing values in x or y
        df_clean = self.df[[x_column, y_column]].dropna()

        if color_column and color_column in self.df.columns:
            df_clean = self.df[[x_column, y_column, color_column]].dropna()

        if size_column and size_column in self.df.columns:
            cols_to_keep = [x_column, y_column, size_column]
            if color_column:
                cols_to_keep.append(color_column)
            df_clean = self.df[cols_to_keep].dropna()

        if len(df_clean) == 0:
            raise ValueError("No valid data points after removing missing values")

        # Try to add trendline if statsmodels is available
        trendline = None
        try:
            x_is_numeric = pd.api.types.is_numeric_dtype(df_clean[x_column])
            y_is_numeric = pd.api.types.is_numeric_dtype(df_clean[y_column])
            if x_is_numeric and y_is_numeric:
                import statsmodels  # noqa: F401

                trendline = "ols"
        except ImportError:
            pass  # statsmodels not available, skip trendline

        fig = px.scatter(
            df_clean,
            x=x_column,
            y=y_column,
            color=color_column,
            size=size_column,
            title=title or f"{y_column} vs {x_column}",
            color_continuous_scale=self._get_color_scheme(color_scheme),
            trendline=trendline
        )

        fig.update_traces(marker=dict(line=dict(width=0.5, color='rgba(255,255,255,0.3)')))
        fig.update_layout(
            hovermode='closest',
            height=600
        )

        return fig.to_json()

    def box_plot(
        self,
        columns: List[str],
        group_by: Optional[str] = None,
        title: Optional[str] = None,
        color_scheme: str = 'viridis'
    ) -> str:
        """Create box plots to compare distributions"""
        if not columns:
            raise ValueError("At least one column required")

        valid_columns = [col for col in columns if col in self.df.columns]
        if not valid_columns:
            raise ValueError("No valid columns found")

        if group_by:
            # Grouped box plot
            fig = px.box(
                self.df,
                x=group_by,
                y=valid_columns[0],
                title=title or f"Distribution of {valid_columns[0]} by {group_by}",
                color=group_by,
                color_discrete_sequence=self._get_color_scheme(color_scheme)
            )
        else:
            # Multiple box plots
            fig = go.Figure()
            colors = self._get_color_scheme(color_scheme)

            for i, col in enumerate(valid_columns):
                data = self.df[col].dropna()
                if len(data) > 0:
                    fig.add_trace(go.Box(
                        y=data,
                        name=col,
                        marker_color=colors[i % len(colors)],
                        boxmean='sd'  # Show mean and standard deviation
                    ))

            fig.update_layout(
                title=title or "Distribution Comparison",
                yaxis_title="Value",
                showlegend=True,
                height=600
            )

        return fig.to_json()

    def violin_plot(
        self,
        columns: List[str],
        group_by: Optional[str] = None,
        title: Optional[str] = None,
        color_scheme: str = 'viridis'
    ) -> str:
        """Create violin plots for distribution visualization"""
        if not columns:
            raise ValueError("At least one column required")

        valid_columns = [col for col in columns if col in self.df.columns]
        if not valid_columns:
            raise ValueError("No valid columns found")

        if group_by:
            fig = px.violin(
                self.df,
                x=group_by,
                y=valid_columns[0],
                title=title or f"Distribution of {valid_columns[0]} by {group_by}",
                color=group_by,
                box=True,
                points='outliers',
                color_discrete_sequence=self._get_color_scheme(color_scheme)
            )
        else:
            fig = go.Figure()
            colors = self._get_color_scheme(color_scheme)

            for i, col in enumerate(valid_columns):
                data = self.df[col].dropna()
                if len(data) > 0:
                    fig.add_trace(go.Violin(
                        y=data,
                        name=col,
                        marker_color=colors[i % len(colors)],
                        box_visible=True,
                        meanline_visible=True
                    ))

            fig.update_layout(
                title=title or "Distribution Comparison",
                yaxis_title="Value",
                showlegend=True,
                height=600
            )

        return fig.to_json()

    def correlation_heatmap(
        self,
        columns: Optional[List[str]] = None,
        title: Optional[str] = None,
        color_scheme: str = 'viridis'
    ) -> str:
        """Create a correlation heatmap for numeric columns"""
        # Get numeric columns
        numeric_df = self.df.select_dtypes(include=[np.number])

        if columns:
            valid_columns = [col for col in columns if col in numeric_df.columns]
            if valid_columns:
                numeric_df = numeric_df[valid_columns]

        if numeric_df.empty or len(numeric_df.columns) < 2:
            raise ValueError("Need at least 2 numeric columns for correlation")

        # Calculate correlation matrix
        corr_matrix = numeric_df.corr()

        fig = px.imshow(
            corr_matrix,
            title=title or "Correlation Heatmap",
            color_continuous_scale=self._get_color_scheme(color_scheme),
            aspect='auto',
            labels=dict(color="Correlation"),
            zmin=-1,
            zmax=1
        )

        fig.update_layout(
            height=max(400, len(corr_matrix) * 30),
            width=max(400, len(corr_matrix) * 30)
        )

        # Add correlation values as text
        fig.update_traces(
            text=corr_matrix.round(2).values,
            texttemplate='%{text}',
            textfont={"size": 10}
        )

        return fig.to_json()

    def line_chart(
        self,
        x_column: str,
        y_columns: List[str],
        title: Optional[str] = None,
        color_scheme: str = 'viridis'
    ) -> str:
        """Create a line chart for trends"""
        if x_column not in self.df.columns:
            raise ValueError(f"Column {x_column} not found")

        valid_y_columns = [col for col in y_columns if col in self.df.columns]
        if not valid_y_columns:
            raise ValueError("No valid Y columns found")

        # Sort by x column
        df_sorted = self.df.sort_values(x_column)

        fig = go.Figure()
        colors = self._get_color_scheme(color_scheme)

        for i, y_col in enumerate(valid_y_columns):
            # Remove NaN values for this trace
            mask = df_sorted[y_col].notna() & df_sorted[x_column].notna()
            x_data = df_sorted[x_column][mask]
            y_data = df_sorted[y_col][mask]

            if len(x_data) > 0:
                fig.add_trace(go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='lines+markers',
                    name=y_col,
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=6)
                ))

        fig.update_layout(
            title=title or f"Trend Analysis",
            xaxis_title=x_column,
            yaxis_title="Value",
            hovermode='x unified',
            height=600,
            showlegend=True
        )

        return fig.to_json()

    def pie_chart(
        self,
        column: str,
        top_n: int = 10,
        title: Optional[str] = None,
        color_scheme: str = 'rainbow'
    ) -> str:
        """Create a pie chart for categorical data"""
        if column not in self.df.columns:
            raise ValueError(f"Column {column} not found")

        value_counts = self.df[column].value_counts().head(top_n)

        if len(value_counts) == 0:
            raise ValueError("No data to display")

        fig = px.pie(
            values=value_counts.values,
            names=value_counts.index,
            title=title or f"Distribution of {column}",
            color_discrete_sequence=self._get_color_scheme(color_scheme)
        )

        hover_template = (
            '<b>%{label}</b><br>'
            'Count: %{value}<br>'
            'Percentage: %{percent}<extra></extra>'
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate=hover_template,
        )

        fig.update_layout(height=600)

        return fig.to_json()

    def bar_chart(
        self,
        x_column: str,
        y_column: str,
        orientation: str = 'v',
        title: Optional[str] = None,
        color_scheme: str = 'viridis'
    ) -> str:
        """Create a bar chart"""
        if x_column not in self.df.columns or y_column not in self.df.columns:
            raise ValueError(f"Columns {x_column} or {y_column} not found")

        # Remove NaN values
        df_clean = self.df[[x_column, y_column]].dropna()

        if len(df_clean) == 0:
            raise ValueError("No valid data after removing missing values")

        fig = px.bar(
            df_clean,
            x=x_column if orientation == 'v' else y_column,
            y=y_column if orientation == 'v' else x_column,
            title=title or f"{y_column} by {x_column}",
            color=y_column if orientation == 'v' else x_column,
            color_continuous_scale=self._get_color_scheme(color_scheme),
            orientation=orientation
        )

        fig.update_layout(
            hovermode='closest',
            height=600,
            showlegend=False
        )

        return fig.to_json()
