"""Custom exception classes for Data Workbench — standardized API errors."""

import logging
import uuid
from typing import Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def _trace_id() -> str:
    return uuid.uuid4().hex[:12]


def make_error_response(status_code: int, message: str, detail: Optional[str] = None, code: Optional[str] = None):
    """Standardized {code, message, detail, trace_id} body."""
    if code is None:
        code = f"E{status_code}"
    return {
        "code": code,
        "message": message,
        "detail": detail or message,
        "trace_id": _trace_id(),
    }


class DataAnalystError(Exception):
    """Base exception for all Data Workbench errors."""

    pass


class DataValidationError(DataAnalystError):
    """Raised when data validation fails."""

    pass


class ModelTrainingError(DataAnalystError):
    """Raised when model training fails."""

    pass


class ConfigurationError(DataAnalystError):
    """Raised when configuration is invalid."""

    pass


# ── Standardized HTTP exceptions ──
class AppHTTPException(HTTPException):
    """HTTPException with standardized body + trace_id."""

    def __init__(
        self, status_code: int, message: str, detail: Optional[str] = None, code: Optional[str] = None, headers=None
    ):
        body = make_error_response(status_code, message, detail, code)
        super().__init__(status_code=status_code, detail=body, headers=headers)
        self.body = body


class NotFoundError(AppHTTPException):
    def __init__(self, message: str = "Resource not found", detail: Optional[str] = None):
        super().__init__(status.HTTP_404_NOT_FOUND, message, detail, code="E404")


class AuthError(AppHTTPException):
    def __init__(self, message: str = "Unauthorized", detail: Optional[str] = None):
        super().__init__(
            status.HTTP_401_UNAUTHORIZED, message, detail, code="E401", headers={"WWW-Authenticate": "Bearer"}
        )


class ValidationError(AppHTTPException):
    def __init__(self, message: str = "Validation failed", detail: Optional[str] = None):
        super().__init__(status.HTTP_400_BAD_REQUEST, message, detail, code="E400")


class ConflictError(AppHTTPException):
    def __init__(self, message: str = "Conflict", detail: Optional[str] = None):
        super().__init__(status.HTTP_409_CONFLICT, message, detail, code="E409")


class RateLimitError(AppHTTPException):
    def __init__(self, message: str = "Rate limit exceeded", detail: Optional[str] = None):
        super().__init__(status.HTTP_429_TOO_MANY_REQUESTS, message, detail, code="E429")


def handle_error(error: Exception, context: str = "", user_message: str = "") -> dict:
    """
    Centralized error handler — logs structured error, returns user-friendly payload.

    (Streamlit đã gỡ khỏi dự án nên không còn st.error — caller hiển thị theo UI riêng.)

    Args:
        error: The exception that occurred
        context: Description of where/why the error happened
        user_message: Optional custom message for the user
    """
    error_name = type(error).__name__
    logger.error("[%s] %s | Context: %s", error_name, str(error), context, exc_info=True)
    return {"error": error_name, "message": user_message or str(error), "context": context}
