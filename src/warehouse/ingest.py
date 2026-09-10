"""Ingest — CSV/Excel -> raw.<name> in DuckDB + profiling (Plan 02)."""

import re
from pathlib import Path

import pandas as pd

from src.analytics.data_quality import *  # reuse data_quality logic
from src.core.insights import generate_data_summary
from src.warehouse.connection import get_conn, warehouse_write_lock


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
    return ingest_df(user, df, table or Path(fname).stem)


def ingest_df(user: str, df: "pd.DataFrame", table: str) -> dict:
    """Ingest DataFrame san co (demo 1-click, tests) — chung duong voi ingest_file."""
    import pandas as _pd

    if df is None or not isinstance(df, _pd.DataFrame) or df.empty or len(df.columns) == 0:
        raise ValueError("File rỗng hoặc không có cột dữ liệu")
    tname = _sanitize_table(table)
    full = f"raw.{tname}"

    conn = get_conn()
    try:
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
        # Atomic + serialized nhu executor (khong DROP+CREATE ho nhau)
        with warehouse_write_lock(timeout=30.0):
            conn.register("df_tmp", df)
            try:
                conn.execute(f"CREATE OR REPLACE TABLE {full} AS SELECT * FROM df_tmp")
            finally:
                try:
                    conn.unregister("df_tmp")
                except Exception:
                    pass
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


def demo_dataframe(n: int = 120) -> "pd.DataFrame":
    """Sinh demo data (onboarding 1-click) — giong scripts/generate_demo_data.py."""
    import numpy as _np

    _np.random.seed(42)
    df = pd.DataFrame(
        {
            "ma_sv": [f"SV{i:04d}" for i in range(1, n + 1)],
            "diem": _np.random.normal(6.5, 1.8, n).clip(0, 10).round(1),
            "lop": _np.random.choice(["L01", "L02", "L03"], n),
            "gio_hoc": _np.random.exponential(5, n).clip(0, 20).round(1),
        }
    )
    idx = _np.random.choice(n, max(1, n // 15), replace=False)
    df.loc[idx, "diem"] = float("nan")
    return df
