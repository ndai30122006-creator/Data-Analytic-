# ═══════════════════════════════════════════════════════════════════
# Learning Analytics Thống kê — Multi-stage Docker build
#
#   base     : Python 3.11 runtime + toàn bộ pip dependencies (dùng chung)
#   backend  : FastAPI application  → port 8000
#   frontend : Streamlit application → port 8501
#
# Build từng image:  docker build -t la-backend . --target backend
#                     docker build -t la-frontend . --target frontend
# Build cả hệ thống: docker compose up --build
# ═══════════════════════════════════════════════════════════════════

# ── Stage 0: base ──────────────────────────────────────────────────
FROM python:3.11-slim AS base

# Runtime tuning: không ghi .pyc, log flush ngay, pip không cache
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore

WORKDIR /app

# System deps — chỉ cần curl cho healthcheck.
# Mọi package đều có sẵn manylinux wheels → KHÔNG cần build-essential.
# (Nếu sau này tăng thêm package bắt buộc compile từ source, thêm build-essential tại đây.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements trước → tận dụng Docker layer caching
COPY requirements/base.txt requirements/base.txt

# Cài dependencies (chung cho cả API lẫn frontend)
RUN pip install --no-cache-dir -r requirements/base.txt

# ── Stage 1: backend (FastAPI, port 8000) ──────────────────────────
FROM base AS backend

# LƯU Ý: api.py import từ package src/ → phải copy CẢ src/
COPY api.py .
COPY src/ ./src/

# Thư mục dữ liệu bền vững (users.db) — mount Docker volume tại đây
RUN mkdir -p /app/data

# Healthcheck dùng curl (đã cài ở base; image slim KHÔNG có curl mặc định)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

# ── Stage 2: frontend (Streamlit, port 8501) ───────────────────────
FROM base AS frontend

# Copy toàn bộ mã nguồn (tôn trọng .dockerignore)
COPY . /app

# Streamlit health endpoint chuẩn: /_stcore/health
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://localhost:8501/_stcore/health || exit 1

EXPOSE 8501

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.fileWatcherType=none", \
     "--browser.gatherUsageStats=false"]