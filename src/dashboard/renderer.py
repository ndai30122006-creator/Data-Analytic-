"""Renderer — spec -> plotly (Plan 05, filter thừa: chỉ 6 types)."""

import re
from typing import List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.dashboard.spec_schema import ChartSpec, DashboardSpec
from src.utils.helpers import apply_theme
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


def render_chart(chart: ChartSpec, df: pd.DataFrame) -> go.Figure:
    t = chart.type.lower()
    if t == "kpi" and chart.metric:
        col = chart.metric.get("column")
        agg = chart.metric.get("aggregation", "mean")
        if col in df.columns:
            val = getattr(df[col], agg)() if hasattr(df[col], agg) else df[col].mean()
            fig = go.Figure(go.Indicator(mode="number", value=float(val), title={"text": chart.title}))
            apply_theme(fig)
            return fig
    if t == "hist" and chart.x and chart.x in df.columns:
        fig = px.histogram(df, x=chart.x, nbins=chart.bins or 20, title=chart.title)
        apply_theme(fig)
        return fig
    if t == "bar" and chart.x and chart.x in df.columns:
        # Use count per x
        vc = df[chart.x].value_counts().head(20)
        fig = px.bar(x=vc.index.astype(str), y=vc.values, title=chart.title, labels={"x": chart.x, "y": "count"})
        apply_theme(fig)
        return fig
    if t == "box" and chart.x and chart.y and chart.x in df.columns and chart.y in df.columns:
        fig = px.box(df, x=chart.x, y=chart.y, title=chart.title)
        apply_theme(fig)
        return fig
    if t == "line" and chart.x and chart.y and chart.x in df.columns and chart.y in df.columns:
        fig = px.line(df.sort_values(chart.x), x=chart.x, y=chart.y, title=chart.title)
        apply_theme(fig)
        return fig
    if t == "scatter" and chart.x and chart.y and chart.x in df.columns and chart.y in df.columns:
        fig = px.scatter(df, x=chart.x, y=chart.y, title=chart.title)
        apply_theme(fig)
        return fig
    # Fallback
    fig = go.Figure()
    fig.update_layout(title=chart.title)
    return fig


def render(spec: DashboardSpec) -> List[go.Figure]:
    """Render DashboardSpec -> list of figures."""
    figs = []
    for chart in spec.charts:
        df = fetch_data(chart, spec.source)
        figs.append(render_chart(chart, df))
    return figs
