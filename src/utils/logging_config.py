"""
Logging configuration with log rotation support.
"""
import logging
import logging.handlers
import os
import sys
from typing import Optional


def setup_logging(
    app_name: str = "data-analyst-pro",
    log_level: str = "INFO",
    log_dir: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
) -> logging.Logger:
    """
    Configure application-wide logging with rotation.
    
    Args:
        app_name: Name of the application (used for logger and file naming)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files (default: creates 'logs/' in project root)
        max_bytes: Maximum size per log file before rotation
        backup_count: Number of rotated log files to keep
    
    Returns:
        Root logger instance
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Determine log directory
    if log_dir is None:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
    
    os.makedirs(log_dir, exist_ok=True)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # ── Formatter ──
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # ── Console handler ──
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # ── Rotating file handler ──
    log_file = os.path.join(log_dir, f"{app_name}.log")
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except (IOError, OSError) as exc:
        root_logger.warning("Failed to create log file handler: %s", exc)
    
    # ── Error file handler (only WARNING+) ──
    error_log_file = os.path.join(log_dir, f"{app_name}_error.log")
    try:
        error_handler = logging.handlers.RotatingFileHandler(
            filename=error_log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.WARNING)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)
    except (IOError, OSError) as exc:
        root_logger.warning("Failed to create error log file handler: %s", exc)
    
    # ── Suppress noisy third-party loggers ──
    for noisy_logger in [
        "urllib3", "httpx", "httpcore", "chardet", "matplotlib",
        "PIL", "asyncio", "fsspec", "s3fs",
    ]:
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)
    
    root_logger.info(
        "Logging configured: level=%s, file=%s, max_bytes=%d, backup_count=%d",
        log_level, log_file, max_bytes, backup_count,
    )
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)