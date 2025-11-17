"""
LLM-powered dataset insights using local Ollama model
"""
import ollama
from typing import Dict, Any
import json


class DatasetInsightGenerator:
    """Generates natural language insights about datasets using a local LLM"""

    def __init__(self, model_name: str = "qwen2.5:0.5b"):
        """
        Initialize the insight generator with a specific model

        Args:
            model_name: The Ollama model to use (default: qwen2.5:0.5b)
        """
        self.model_name = model_name

    def generate_insight(self, analysis_summary: Dict[str, Any]) -> str:
        """
        Generate a natural language insight about the dataset

        Args:
            analysis_summary: Dictionary containing column names, types, and basic stats

        Returns:
            A natural language description of what the dataset appears to be about
        """
        # Create a concise prompt with just the key information
        prompt = self._create_prompt(analysis_summary)

        try:
            # Call Ollama with the local model
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data analyst. Given information about a dataset, provide a brief 2-3 sentence insight about what the dataset appears to be about and its likely purpose. Be concise and specific."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    "temperature": 0.3,  # Lower temperature for more focused responses
                    "num_predict": 150,   # Limit response length to ~2-3 sentences
                }
            )

            # Extract the response text
            insight = response['message']['content'].strip()
            return insight

        except Exception as e:
            # If LLM fails, return a graceful error message
            return f"Unable to generate insight: {str(e)}"

    def _create_prompt(self, analysis_summary: Dict[str, Any]) -> str:
        """
        Create a concise prompt from the analysis summary

        Args:
            analysis_summary: Dictionary with overview and column information

        Returns:
            A formatted prompt string
        """
        overview = analysis_summary.get("overview", {})
        columns = analysis_summary.get("columns", {})

        # Extract key information
        num_rows = overview.get("rows", 0)
        num_cols = overview.get("columns", 0)
        column_names = overview.get("column_names", [])
        column_types = overview.get("column_types", {})

        # Build a compact representation
        prompt_parts = [
            f"Dataset: {num_rows} rows, {num_cols} columns",
            "\nColumns:"
        ]

        # Add column information (name + type + key stat)
        for col_name in column_names[:20]:  # Limit to first 20 columns
            col_type = column_types.get(col_name, "unknown")
            col_info = columns.get(col_name, {})
            analysis = col_info.get("analysis", {})
            stats = analysis.get("stats", {})

            # Get a key stat based on type
            if col_type == "numeric":
                stat_info = f"(mean: {stats.get('mean', 'N/A')})"
            elif col_type == "categorical":
                stat_info = f"({stats.get('unique', 'N/A')} unique values)"
            else:
                stat_info = f"({stats.get('unique', 'N/A')} unique)"

            prompt_parts.append(f"  - {col_name} [{col_type}] {stat_info}")

        if len(column_names) > 20:
            prompt_parts.append(f"  ... and {len(column_names) - 20} more columns")

        prompt_parts.append("\nWhat is this dataset likely about and what might it be used for?")

        return "\n".join(prompt_parts)

    def check_model_availability(self) -> bool:
        """
        Check if the model is available in Ollama

        Returns:
            True if model is available, False otherwise
        """
        try:
            models = ollama.list()
            available_models = [m['name'] for m in models.get('models', [])]
            return self.model_name in available_models
        except:
            return False
