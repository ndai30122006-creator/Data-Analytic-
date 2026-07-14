"""Performance utilities — safe n_jobs, file size limits, resource guards."""
import logging
import os

logger = logging.getLogger(__name__)

# Optional psutil for memory monitoring
try:
    import psutil  # type: ignore[import-unused]
    _PSUTIL_AVAIL = True
except ImportError:
    _PSUTIL_AVAIL = False
    logger.info("psutil not installed; memory monitoring disabled. pip install psutil")


def safe_n_jobs(requested: int = -1, max_jobs: int = 4) -> int:
    """Clamp n_jobs to a safe maximum to avoid resource exhaustion.
    
    Args:
        requested: Requested n_jobs value (-1 means all CPUs).
        max_jobs: Hard cap (default 4).
    
    Returns:
        Safe n_jobs value (≥1).
    """
    cpu_count = os.cpu_count() or 1
    if requested == -1 or requested > cpu_count:
        effective = cpu_count
    else:
        effective = max(1, requested)
    return min(effective, max_jobs)


def check_file_size(file_size_bytes: int, max_bytes: int = 50 * 1024 * 1024) -> tuple[bool, str]:
    """Check if file size is within limits.
    
    Returns:
        (is_valid, message)
    """
    if file_size_bytes > max_bytes:
        mb = file_size_bytes / (1024 * 1024)
        max_mb = max_bytes / (1024 * 1024)
        return False, f"File size ({mb:.1f} MB) exceeds maximum allowed ({max_mb:.0f} MB)"
    return True, ""


def get_memory_usage() -> float:
    """Get current process memory usage in MB."""
    if not _PSUTIL_AVAIL:
        return 0.0
    try:
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return 0.0


def warn_if_large_dataset(df_rows: int, df_cols: int,
                          max_rows: int = 500_000, max_cols: int = 200) -> str | None:
    """Return a warning message if the dataset is large, or None."""
    warnings = []
    if df_rows > max_rows:
        warnings.append(f"⚠️ Large dataset: {df_rows:,} rows (max recommended: {max_rows:,})")
    if df_cols > max_cols:
        warnings.append(f"⚠️ Many columns: {df_cols} columns (max recommended: {max_cols})")
    return "\n".join(warnings) if warnings else None
