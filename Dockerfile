# Multi-stage build for Learning Analytics SaaS
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Stage 1: Backend API
FROM base as backend

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY api.py .

# Expose API port
EXPOSE 8000

# Run API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

# Stage 2: Frontend (Streamlit)
FROM base as frontend

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend code
COPY app.py .
COPY auth.py .
COPY ai_insights.py .
COPY utils.py .
COPY components.py .
COPY config.py .
COPY report_utils.py .
COPY advanced_analytics.py .

# Create directories
RUN mkdir -p .streamlit

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]

# Final stage: Combine both
FROM base

# Copy backend
COPY --from=backend /app /app/backend

# Copy frontend
COPY --from=frontend /app /app/frontend

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Starting Learning Analytics SaaS..."\n\
echo "Backend API: http://localhost:8000"\n\
echo "Frontend: http://localhost:8501"\n\
\n\
# Start backend in background\n\
cd /app/backend && uvicorn api:app --host 0.0.0.0 --port 8000 &\n\
\n\
# Start frontend\n\
cd /app/frontend && streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true\n\
' > /start.sh && chmod +x /start.sh

EXPOSE 8000 8501

CMD ["/start.sh"]