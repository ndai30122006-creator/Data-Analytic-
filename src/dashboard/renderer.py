"""Data fetcher — 1 query per chart on DuckDB (Plan 05).

Luu y: cac ham render Plotly cu (render_chart/render) da xoa — frontend
dung ApexCharts voi JSON tu routers/dashboards.py.
"""

import re

import pandas as pd

from src.dashboard.spec_schema import ChartSpec
from src.warehouse.connection import get_conn

_VALID_SRC = re.compile(r"^(raw|mart)\.[a-zA-Z_][a-zA-Z0-9_]{0,63}$")


def _q(src: str) -> str:
    if not _VALID_SRC.match(src):
        raise ValueError(f"Invalid source {src!r}")
    s, t = src.split(".", 1)
    return f'"{s}"."{t}"'


def fetch_data(chart: ChartSpec, source: str) -> pd.DataFrame:
    """Each chart 1 query on DuckDB (Plan 05)."""
    conn = get_conn()
    try:
        q = _q(source)
        return conn.execute(f"SELECT * FROM {q} LIMIT 1000").fetchdf()
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()
