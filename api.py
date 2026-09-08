"""FastAPI Backend for Learning Analytics SaaS — JWT + bcrypt + SQLAlchemy + rate limiting.

Mục 7: composition root mỏng — routes nằm ở src/api/routers/*, deps dùng chung ở src/api/deps.py.
Giữ `from api import app` tương thích (tests/E2E/uvicorn api:app).
"""

import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from src.api.routers import analysis, auth, brief, dashboards, datasets, pipelines, system
from src.utils.security import get_cors_origins, validate_environment

logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan: replace deprecated @app.on_event('startup')."""
    try:
        from src.core.database import init_db

        init_db()
    except Exception as exc:
        logger.warning("DB init on startup failed: %s", exc)
    yield


app = FastAPI(title="Learning Analytics API", version="1.3.0", lifespan=lifespan)


# ── CORS Configuration ──
cors_origins = get_cors_origins()
allow_all_cors = os.environ.get("CORS_ALLOW_ALL", "false").lower() == "true"

if allow_all_cors:
    logger.warning("CORS_ALLOW_ALL is enabled. This is insecure for production.")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # Must be False when allow_origins=["*"] per Fetch spec
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )


# ── Standardized error handlers (P1.1.3, mục 11) ──
from fastapi import HTTPException as _HTTPException
from fastapi import status as _status

from src.utils.exceptions import make_error_response


@app.exception_handler(_HTTPException)
async def http_exception_handler(request: Request, exc: _HTTPException):
    # Already standardized (AppHTTPException) → keep as is
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        content = exc.detail
    else:
        # Legacy raise HTTPException(detail="string") → wrap
        content = make_error_response(exc.status_code, str(exc.detail), code=f"E{exc.status_code}")
    return JSONResponse(status_code=exc.status_code, content=content, headers=exc.headers)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception: %s | Path: %s | Detail: %s", type(exc).__name__, request.url.path, str(exc), exc_info=True
    )
    content = make_error_response(
        _status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error. Please try again later.", str(exc), code="E500"
    )
    return JSONResponse(status_code=_status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)


# ── Routers ──
app.include_router(system.router)
app.include_router(auth.router)
app.include_router(datasets.router)
app.include_router(pipelines.router)
app.include_router(brief.router)
app.include_router(dashboards.router)
app.include_router(analysis.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
