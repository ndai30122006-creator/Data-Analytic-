"""Custom exception classes for Data Analyst Pro"""
import logging

logger = logging.getLogger(__name__)


class DataAnalystError(Exception):
    """Base exception for all Data Analyst Pro errors."""
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


def handle_error(error: Exception, context: str = "", user_message: str = "") -> None:
    """
    Centralized error handler — logs and displays user-friendly message.

    Args:
        error: The exception that occurred
        context: Description of where/why the error happened
        user_message: Optional custom message for the user
    """
    import streamlit as st
    error_name = type(error).__name__
    logger.error("[%s] %s | Context: %s", error_name, str(error), context, exc_info=True)
    msg = user_message or f"**{error_name}:** {str(error)}"
    st.error(f"❌ {msg}")
    st.caption(f"📍 {context}")