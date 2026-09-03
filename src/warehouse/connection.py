"""Warehouse connection — DuckDB local-first (Plan 02)."""

from pathlib import Path

import duckdb

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = _PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
_DB_PATH = DATA_DIR / "warehouse.duckdb"


def get_conn() -> duckdb.DuckDBPyConnection:
    """Return new DuckDB connection (per request, not global)."""
    return duckdb.connect(str(_DB_PATH))


def get_db_path() -> Path:
    return _DB_PATH
