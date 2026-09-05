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

# Thư mục dữ liệu bền vững (users.db + warehouse.duckdb) — mount Docker volume tại đây
RUN mkdir -p /app/data
VOLUME ["/app/data"]

# Healthcheck dùng curl (đã cài ở base; image slim KHÔNG có curl mặc định)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

# ── Stage 2: web frontend (Node.js, Vite) ──────────────────────────
# Build React web+mobile via Node, serve via nginx (production)
FROM node:20-alpine AS web-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/pnpm-workspace.yaml frontend/pnpm-lock.yaml ./
COPY frontend/shared ./shared
COPY frontend/web ./web
COPY frontend/mobile ./mobile
RUN corepack enable && pnpm install --frozen-lockfile && pnpm -r build

FROM nginx:alpine AS frontend
COPY --from=web-build /app/frontend/web/dist /usr/share/nginx/html/web
COPY --from=web-build /app/frontend/mobile/dist /usr/share/nginx/html/mobile
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]