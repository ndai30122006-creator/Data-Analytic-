"""Registry — datasets catalog (SQLite meta + DuckDB data) (Plan 02)."""

from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base

# Reuse Base from database to keep Alembic single metadata
from src.core.database import Base  # noqa: F401

# Extend Dataset via helper functions (actual table alteration via Alembic 003)
# Helpers operate on src.core.database.Dataset


def register_dataset(user: str, name: str, table: str, file_path: str = "", profile_json: str = ""):
    """Register dataset metadata (call after ingest)."""
    from src.core.database import SessionLocal, Dataset

    with SessionLocal() as s:
        ds = Dataset(username=user, dataset_name=name, rows=0, cols=0)
        # If 003 cols exist, set them dynamically
        if hasattr(ds, "duckdb_table"):
            ds.duckdb_table = table
        if hasattr(ds, "file_path"):
            ds.file_path = file_path
        if hasattr(ds, "profile_json"):
            ds.profile_json = profile_json
        s.add(ds)
        s.commit()
        s.refresh(ds)
        return ds


def list_datasets(user: str):
    from src.core.database import list_datasets as _list

    return _list(user)


def get_profile(dataset_id: int) -> Optional[str]:
    from src.core.database import SessionLocal, Dataset

    with SessionLocal() as s:
        ds = s.query(Dataset).filter(Dataset.id == dataset_id).first()
        if ds and hasattr(ds, "profile_json"):
            return ds.profile_json
        return None
