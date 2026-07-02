"""Helper functions extracted from app.py"""
from typing import Optional, List, Any, Dict
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
from datetime import datetime

from src.utils.config import CHART_THEME

# ── Constants ──
SPARKLINE_DEFAULT_COLOR: str = '#5b6bf7'
SPARKLINE_DEFAULT_HEIGHT: int = 40


def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """
    Convert DataFrame to CSV bytes for download.

    Args:
        df: Input DataFrame to convert

    Returns:
        UTF-8 encoded CSV bytes
    """
    return df.to_csv(index=False).encode("utf-8")


def apply_theme(fig: go.Figure) -> go.Figure:
    """
    Apply consistent dark theme to a Plotly figure.

    Args:
        fig: Plotly figure object to theme

    Returns:
        The same figure with CHART_THEME layout applied (mutated in-place)

    Raises:
        ValueError: If fig is None
    """
    if fig is None:
        raise ValueError("Figure cannot be None")
    fig.update_layout(**CHART_THEME)
    return fig


def sparkline(series: pd.Series, color: str = SPARKLINE_DEFAULT_COLOR, height: int = SPARKLINE_DEFAULT_HEIGHT) -> go.Figure:
    """
    Generate a minimal sparkline chart for inline trend display.

    Args:
        series: Numeric data series to plot
        color: Hex color string for the line (default SPARKLINE_DEFAULT_COLOR)
        height: Chart height in pixels (default SPARKLINE_DEFAULT_HEIGHT)

    Returns:
        Plotly Figure with axes hidden, suitable for inline display

    Raises:
        ValueError: If series is None
    """
    if series is None:
        raise ValueError("Series cannot be None")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=series.values, mode='lines',
        line=dict(color=color, width=1.5),
        fill='tozeroy', fillcolor=f'rgba(91,107,247,0.06)',
        showlegend=False, hoverinfo='skip'
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False, showticklabels=False),
        yaxis=dict(visible=False, showticklabels=False),
    )
    return fig


def guess_learning_column(columns: List[str], keywords: List[str]) -> Optional[str]:
    """
    Guess which column name matches learning-related keywords.

    Args:
        columns: List of column names to search through
        keywords: List of substrings to match against (case-insensitive)

    Returns:
        The first matching column name, or None if no match found
    """
    if not columns or not keywords:
        return None
    normalized = {c: str(c).lower().replace(" ", "_") for c in columns}
    for col, name in normalized.items():
        if any(keyword in name for keyword in keywords):
            return col
    return None