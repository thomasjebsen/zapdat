"""
FastAPI backend for Table EDA Analyzer
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pandas as pd
from io import StringIO
from analyzer import TableAnalyzer

app = FastAPI(title="Table EDA Analyzer")

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

        # Analyze the data
        analyzer = TableAnalyzer(df)
        analysis = analyzer.analyze_all()

        return {
            "status": "success",
            "filename": file.filename,
            "analysis": analysis
        }

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty or invalid")
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"Error parsing CSV: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing file: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
