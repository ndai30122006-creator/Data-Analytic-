"""Warehouse connection — DuckDB local-first (Plan 02)."""

from pathlib import Path

import duckdb

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
_DB_PATH = DATA_DIR / "warehouse.duckdb"


def get_conn() -> duckdb.DuckDBPyConnection:
    """Return new DuckDB connection (per request, not global)."""
    return duckdb.connect(str(_DB_PATH))


def get_db_path() -> Path:
    return _DB_PATH
