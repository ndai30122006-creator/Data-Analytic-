"""Ingest — CSV/Excel -> raw.<name> in DuckDB + profiling (Plan 02)."""

import re
from pathlib import Path

import pandas as pd

from src.analytics.data_quality import *  # reuse data_quality logic
from src.core.insights import generate_data_summary
from src.warehouse.connection import get_conn


def _sanitize_table(name: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name.lower())
    if not name or name[0].isdigit():
        name = f"t_{name}"
    return name[:64]


MAX_FILE_MB = 50

def ingest_file(user: str, file, table: str = None) -> dict:
    """Ingest file-like (CSV/Excel) into DuckDB raw schema. Returns profile."""
    fname = getattr(file, "name", None) or getattr(file, "filename", "") or "upload"
    if not fname.lower().endswith((".csv", ".xlsx", ".xls")):
        raise ValueError(f"Unsupported format: {fname} (chỉ .csv/.xlsx/.xls)")
    # FastAPI UploadFile (starlette) has .file SpooledTemporaryFile sync - avoid async helper
    if hasattr(file, "filename") and hasattr(file, "file"):
        try:
            file.file.seek(0, 2)
            size = file.file.tell()
            file.file.seek(0)
            if size <= 0:
                raise ValueError("File rỗng (0 bytes)")
            if size > MAX_FILE_MB * 1024 * 1024:
                raise ValueError(f"File quá lớn ({size/1024/1024:.1f}MB > {MAX_FILE_MB}MB)")
            if fname.lower().endswith(".csv"):
                df = pd.read_csv(file.file)
            else:
                df = pd.read_excel(file.file, engine="openpyxl")
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"File rỗng hoặc không đọc được: {e}")
        if df is None or df.empty or len(df.columns) == 0:
            raise ValueError("File rỗng hoặc không có cột dữ liệu")
    else:
        from src.utils.helpers import load_and_process_data

        df = load_and_process_data(file)
        if df is None or df.empty or len(df.columns) == 0:
            raise ValueError("File rỗng hoặc không có cột dữ liệu")
    tname = _sanitize_table(table or Path(fname).stem)
    full = f"raw.{tname}"

    conn = get_conn()
    try:
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
        conn.execute(f"DROP TABLE IF EXISTS {full}")
        # Register df as temp view then create table
        conn.register("df_tmp", df)
        conn.execute(f"CREATE TABLE {full} AS SELECT * FROM df_tmp")
        conn.unregister("df_tmp")
    finally:
        conn.close()

    # Profile via core/insights + data_quality
    profile = generate_data_summary(df)
    # Also compute quality
    from src.utils.validators import compute_data_quality_score

    quality = compute_data_quality_score(df)

    return {
        "table": full,
        "rows": len(df),
        "cols": len(df.columns),
        "profile": profile,
        "quality": quality,
    }
