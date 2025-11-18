"""
FastAPI backend for Table EDA Analyzer
"""
import logging
from io import StringIO
from typing import List, Optional

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from analyzer import TableAnalyzer
from visualizations import ChartGenerator
from file_reader import MultiFormatReader, FileFormatError

app = FastAPI(title="Table EDA Analyzer")

# Simple in-memory cache for uploaded dataframes and analyzers
# In production, use Redis or similar
dataframe_cache = {}
analyzer_cache = {}

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Serve the frontend"""
    return FileResponse("../frontend/index.html")


@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    """
    Upload a data file and get automatic EDA analysis
    Supports: CSV, Excel, JSON, TSV, Parquet, Feather, Pickle, SQLite, HDF5, ORC
    """
    logger = logging.getLogger("uvicorn")

    logger.info(f"Received file: {file.filename}, content_type: {file.content_type}")

    # Validate file type
    if not MultiFormatReader.is_supported(file.filename):
        supported = ", ".join(MultiFormatReader.get_supported_formats())
        logger.warning(f"Rejected unsupported file: {file.filename}")
        raise HTTPException(
            status_code=400, detail=f"Unsupported file format. Supported formats: {supported}"
        )

    try:
        # Read file content
        contents = await file.read()
        logger.info(f"Read {len(contents)} bytes from {file.filename}")

        if len(contents) == 0:
            logger.warning(f"Empty file uploaded: {file.filename}")
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        # Parse file using MultiFormatReader
        df = MultiFormatReader.read_file(contents, file.filename)

        # Check if dataframe is empty
        if df.empty:
            logger.warning(f"File parsed but dataframe is empty: {file.filename}")
            raise HTTPException(status_code=400, detail="File is empty or contains no data")

        logger.info(f"Successfully parsed {file.filename}, shape: {df.shape}")

        # Analyze the data
        analyzer = TableAnalyzer(df)
        analysis = analyzer.analyze_all()

        # Store both dataframe and analyzer in cache with filename as key
        cache_key = file.filename
        dataframe_cache[cache_key] = df
        analyzer_cache[cache_key] = analyzer

        logger.info(f"Analysis complete for {file.filename}")

        return {
            "status": "success",
            "filename": file.filename,
            "cache_key": cache_key,
            "file_format": MultiFormatReader.detect_format(file.filename),
            "analysis": analysis
        }

    except FileFormatError as e:
        logger.error(f"FileFormatError for {file.filename}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except pd.errors.EmptyDataError:
        logger.error(f"EmptyDataError for {file.filename}")
        raise HTTPException(status_code=400, detail="File is empty or invalid")
    except pd.errors.ParserError as e:
        logger.error(f"ParserError for {file.filename}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")
    except UnicodeDecodeError as e:
        logger.error(f"UnicodeDecodeError for {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="File encoding error. Please ensure the file is UTF-8 encoded.",
        )
    except Exception as e:
        logger.error(f"Unexpected error analyzing {file.filename}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error analyzing file: {str(e)}")


class CustomChartRequest(BaseModel):
    cache_key: str
    chart_type: str
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    y_columns: Optional[List[str]] = None
    columns: Optional[List[str]] = None
    color_column: Optional[str] = None
    size_column: Optional[str] = None
    group_by: Optional[str] = None
    title: Optional[str] = None
    color_scheme: str = "viridis"
    top_n: int = 10
    orientation: str = "v"


@app.post("/custom_chart")
async def create_custom_chart(request: CustomChartRequest):
    """
    Generate a custom chart based on user preferences
    """
    # Get dataframe from cache
    if request.cache_key not in dataframe_cache:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found. Please upload a file first."
        )

    df = dataframe_cache[request.cache_key]
    generator = ChartGenerator(df)

    try:
        if request.chart_type == "scatter":
            if not request.x_column or not request.y_column:
                raise HTTPException(
                    status_code=400,
                    detail="Scatter plot requires x_column and y_column"
                )
            chart_json = generator.scatter_plot(
                x_column=request.x_column,
                y_column=request.y_column,
                color_column=request.color_column,
                size_column=request.size_column,
                title=request.title,
                color_scheme=request.color_scheme
            )

        elif request.chart_type == "box":
            if not request.columns:
                raise HTTPException(
                    status_code=400,
                    detail="Box plot requires at least one column"
                )
            chart_json = generator.box_plot(
                columns=request.columns,
                group_by=request.group_by,
                title=request.title,
                color_scheme=request.color_scheme
            )

        elif request.chart_type == "violin":
            if not request.columns:
                raise HTTPException(
                    status_code=400,
                    detail="Violin plot requires at least one column"
                )
            chart_json = generator.violin_plot(
                columns=request.columns,
                group_by=request.group_by,
                title=request.title,
                color_scheme=request.color_scheme
            )

        elif request.chart_type == "correlation":
            chart_json = generator.correlation_heatmap(
                columns=request.columns,
                title=request.title,
                color_scheme=request.color_scheme
            )

        elif request.chart_type == "line":
            if not request.x_column or not request.y_columns:
                raise HTTPException(
                    status_code=400,
                    detail="Line chart requires x_column and y_columns"
                )
            chart_json = generator.line_chart(
                x_column=request.x_column,
                y_columns=request.y_columns,
                title=request.title,
                color_scheme=request.color_scheme
            )

        elif request.chart_type == "pie":
            if not request.x_column:
                raise HTTPException(
                    status_code=400,
                    detail="Pie chart requires a column (x_column)"
                )
            chart_json = generator.pie_chart(
                column=request.x_column,
                top_n=request.top_n,
                title=request.title,
                color_scheme=request.color_scheme
            )

        elif request.chart_type == "bar":
            if not request.x_column or not request.y_column:
                raise HTTPException(
                    status_code=400,
                    detail="Bar chart requires x_column and y_column"
                )
            chart_json = generator.bar_chart(
                x_column=request.x_column,
                y_column=request.y_column,
                orientation=request.orientation,
                title=request.title,
                color_scheme=request.color_scheme
            )

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown chart type: {request.chart_type}"
            )

        return {
            "status": "success",
            "chart": chart_json
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating chart: {str(e)}"
        )


@app.get("/column_info/{cache_key}")
async def get_column_info(cache_key: str):
    """
    Get column names and types for a cached dataset
    """
    if cache_key not in dataframe_cache:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found. Please upload a file first."
        )

    df = dataframe_cache[cache_key]
    analyzer = TableAnalyzer(df)

    # Categorize columns by type
    numeric_columns = [
        col for col, dtype in analyzer.column_types.items()
        if dtype == "numeric"
    ]
    categorical_columns = [
        col for col, dtype in analyzer.column_types.items()
        if dtype == "categorical"
    ]
    all_columns = list(df.columns)

    return {
        "all_columns": all_columns,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "column_types": analyzer.column_types
    }


@app.get("/supported_formats")
async def get_supported_formats():
    """Get list of supported file formats"""
    return {
        "formats": MultiFormatReader.get_supported_formats(),
        "descriptions": {
            ".csv": "Comma-Separated Values",
            ".tsv": "Tab-Separated Values",
            ".txt": "Text file (auto-detect delimiter)",
            ".xlsx": "Excel 2007+ (OpenXML)",
            ".xls": "Excel 97-2003",
            ".json": "JavaScript Object Notation",
            ".parquet": "Apache Parquet (columnar)",
            ".feather": "Apache Arrow Feather",
            ".pkl": "Python Pickle",
            ".pickle": "Python Pickle",
            ".db": "SQLite Database",
            ".sqlite": "SQLite Database",
            ".sqlite3": "SQLite Database",
            ".h5": "HDF5 (Hierarchical Data Format)",
            ".hdf5": "HDF5 (Hierarchical Data Format)",
            ".orc": "Apache ORC (Optimized Row Columnar)"
        }
    }


class TypeOverrideRequest(BaseModel):
    cache_key: str
    column: str
    new_type: str


@app.post("/override_type")
async def override_column_type(request: TypeOverrideRequest):
    """
    Override the detected type for a column and re-analyze it
    """
    # Get analyzer from cache
    if request.cache_key not in analyzer_cache:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found. Please upload a file first."
        )

    analyzer = analyzer_cache[request.cache_key]

    try:
        # Store old type for response
        old_type = analyzer.column_types.get(request.column, "unknown")

        # Override the column type and get new analysis
        column_analysis = analyzer.override_column_type(request.column, request.new_type)

        # Update the cache with the modified analyzer and dataframe
        analyzer_cache[request.cache_key] = analyzer
        dataframe_cache[request.cache_key] = analyzer.df

        return {
            "status": "success",
            "column": request.column,
            "old_type": old_type,
            "new_type": request.new_type,
            "analysis": column_analysis
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error overriding type: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
