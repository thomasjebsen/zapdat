"""
FastAPI backend for Table EDA Analyzer
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
from io import StringIO
from analyzer import TableAnalyzer
from visualizations import ChartGenerator

app = FastAPI(title="Table EDA Analyzer")

# Simple in-memory cache for uploaded dataframes
# In production, use Redis or similar
dataframe_cache = {}

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
async def analyze_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file and get automatic EDA analysis
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    try:
        # Read CSV file
        contents = await file.read()
        csv_string = contents.decode('utf-8')
        df = pd.read_csv(StringIO(csv_string))

        # Check if dataframe is empty
        if df.empty:
            raise HTTPException(status_code=400, detail="CSV file is empty")

        # Store dataframe in cache with filename as key
        cache_key = file.filename
        dataframe_cache[cache_key] = df

        # Analyze the data
        analyzer = TableAnalyzer(df)
        analysis = analyzer.analyze_all()

        return {
            "status": "success",
            "filename": file.filename,
            "cache_key": cache_key,
            "analysis": analysis
        }

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty or invalid")
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"Error parsing CSV: {str(e)}")
    except Exception as e:
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


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
