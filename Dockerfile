# Multi-stage build for Learning Analytics SaaS
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements/base.txt requirements/base.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements/base.txt

# ── Stage 1: Backend API ──────────────────────────────────────────────────────
FROM base as backend

# Copy backend code
COPY api.py .

# Expose API port
EXPOSE 8000

# Run API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

# ── Stage 2: Frontend (Streamlit) ─────────────────────────────────────────────
FROM base as frontend

# Copy entire application
COPY . /app

# Remove backend-only file
RUN rm -f api.py

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]