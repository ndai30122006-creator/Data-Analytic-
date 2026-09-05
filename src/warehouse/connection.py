"""Warehouse connection — DuckDB local-first (Plan 02)."""

import threading
from contextlib import contextmanager
from pathlib import Path

import duckdb

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = _PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
_DB_PATH = DATA_DIR / "warehouse.duckdb"

# ── Medium fix: serialize DuckDB writes (single-writer) ──
# DuckDB cho phép đọc song song nhưng ghi phải tuần tự.
# Dùng threading.Lock cho single-worker + file-lock best-effort cho multi-worker.
_WRITE_LOCK = threading.RLock()
_FILE_LOCK_PATH = _DB_PATH.with_suffix(".duckdb.lock")


@contextmanager
def warehouse_write_lock(timeout: float = 30.0):
    """Acquire exclusive warehouse write lock (thread + file)."""
    # 1. Thread lock (in-process, fast path)
    acquired = _WRITE_LOCK.acquire(timeout=timeout)
    if not acquired:
        raise TimeoutError("warehouse write lock timeout (thread)")
    # 2. File lock best-effort (multi-process, ví dụ uvicorn --workers>1)
    # Dùng msvcrt (Windows) / fcntl (Unix) nếu có, fallback là no-op nếu lỗi.
    fh = None
    try:
        try:
            # Mở/ tạo file lock
            fh = open(_FILE_LOCK_PATH, "a+")
            try:
                import msvcrt  # Windows

                # _locking với timeout polling
                import time

                start = time.time()
                while True:
                    try:
                        msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
                        break
                    except OSError:
                        if time.time() - start > timeout:
                            raise TimeoutError("warehouse file lock timeout (msvcrt)")
                        time.sleep(0.05)
            except ImportError:
                try:
                    import fcntl  # Unix

                    fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
                except Exception:
                    pass  # fallback: chỉ dùng thread lock
        except Exception:
            fh = None
        yield
    finally:
        if fh is not None:
            try:
                try:
                    import msvcrt

                    msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
                except ImportError:
                    try:
                        import fcntl

                        fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
                    except Exception:
                        pass
                fh.close()
            except Exception:
                pass
        _WRITE_LOCK.release()


def get_conn() -> duckdb.DuckDBPyConnection:
    """Return new DuckDB connection (per request, not global)."""
    return duckdb.connect(str(_DB_PATH))


def get_db_path() -> Path:
    return _DB_PATH
