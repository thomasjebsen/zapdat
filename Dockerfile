FROM python:3.11-slim

WORKDIR /app

# Install uv for faster dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml ./
COPY requirements.txt ./

# Install dependencies using uv (falls back to pip if needed)
RUN uv pip install --system -r requirements.txt || pip install -r requirements.txt

# Copy application code
COPY backend ./backend
COPY frontend ./frontend

# Expose port
EXPOSE 8000

# Set working directory to backend for correct imports
WORKDIR /app/backend

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
