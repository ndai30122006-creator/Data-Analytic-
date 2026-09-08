"""System router — root/health/env."""

import os

from fastapi import APIRouter

from src.utils.security import get_cors_origins, validate_environment

router = APIRouter(tags=["system"])


@router.get("/")
async def root():
    return {"message": "Learning Analytics API", "version": "1.3.0"}


@router.get("/health")
async def health_check():
    return {"status": "healthy"}


@router.get("/static/terminal-swagger.css", include_in_schema=False)
async def terminal_swagger_css():
    """CSS Terminal Dark cho Swagger /docs (khong can them dependency staticfiles)."""
    from pathlib import Path

    from fastapi.responses import Response

    css_path = Path(__file__).resolve().parents[3] / "static" / "terminal-swagger.css"
    try:
        content = css_path.read_text(encoding="utf-8")
    except Exception:
        content = "/* terminal theme missing */"
    return Response(content=content, media_type="text/css")


@router.get("/env/validate")
async def validate_env():
    """Validate environment configuration and return warnings."""
    import logging as _logging

    from src.api import deps as _deps

    _logger = _logging.getLogger(__name__)
    allow_all_cors = os.environ.get("CORS_ALLOW_ALL", "false").lower() == "true"
    if allow_all_cors:
        _logger.warning("CORS_ALLOW_ALL is enabled. This is insecure for production.")
    warnings = validate_environment()
    return {
        "status": "warning" if warnings else "ok",
        "warnings": warnings,
        "cors_origins": ["*"] if allow_all_cors else get_cors_origins(),
        "rate_limiter": "redis" if _deps._redis_available else "in-memory",
    }
