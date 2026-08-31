"""Helper functions extracted from app.py"""

import logging
from datetime import datetime
from io import BytesIO
from typing import Any, Callable, Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.utils.config import (
    MAX_COLS_UPLOAD,
    MAX_FILE_SIZE_BYTES,
    MAX_ROWS_UPLOAD,
    get_chart_mode,
    get_chart_theme,
)
from src.utils.exceptions import DataValidationError, handle_error
from src.utils.performance import check_file_size, warn_if_large_dataset

logger = logging.getLogger(__name__)
SPARKLINE_DEFAULT_COLOR: str = "#5b6bf7"
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


def apply_theme(fig: go.Figure, mode: Optional[str] = None) -> go.Figure:
    """
    Apply consistent chart theme (light/dark aware) to a Plotly figure.

    Args:
        fig: Plotly figure object to theme
        mode: "light" or "dark"; defaults to the active session theme mode.

    Returns:
        The same figure with the chart theme layout applied (mutated in-place)

    Raises:
        ValueError: If fig is None
    """
    if fig is None:
        raise ValueError("Figure cannot be None")
    if mode is None:
        mode = get_chart_mode()
    fig.update_layout(**get_chart_theme(mode))
    return fig


def sparkline(
    series: pd.Series, color: str = SPARKLINE_DEFAULT_COLOR, height: int = SPARKLINE_DEFAULT_HEIGHT
) -> go.Figure:
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
    fig.add_trace(
        go.Scatter(
            y=series.values,
            mode="lines",
            line=dict(color=color, width=1.5),
            fill="tozeroy",
            fillcolor=f"rgba(91,107,247,0.06)",
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
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


@st.cache_data(hash_funcs={"streamlit.runtime.uploaded_file_manager.UploadedFile": lambda f: (f.name, f.size)})
def load_and_process_data(file) -> Optional[pd.DataFrame]:
    """
    Load và cache dữ liệu từ file upload (CSV/Excel).

    Args:
        file: Uploaded file object từ Streamlit file_uploader

    Returns:
        pd.DataFrame nếu thành công, None nếu lỗi

    Raises:
        Không raise — tất cả exception được catch và xử lý qua handle_error()
    """
    try:
        if file is None:
            raise DataValidationError("File không tồn tại")

        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        valid_size, size_msg = check_file_size(file_size, MAX_FILE_SIZE_BYTES)
        if not valid_size:
            raise DataValidationError(size_msg)

        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        elif file.name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file, engine="openpyxl")
        else:
            raise DataValidationError(
                f"Định dạng '{file.name.split('.')[-1]}' không hỗ trợ. " "Chấp nhận: .csv, .xlsx, .xls"
            )

        if df.empty:
            raise DataValidationError("File rỗng, không có dữ liệu")

        warning = warn_if_large_dataset(len(df), len(df.columns), MAX_ROWS_UPLOAD, MAX_COLS_UPLOAD)
        if warning:
            st.warning(warning)

        logger.info("Loaded file '%s': %d rows x %d cols", file.name, *df.shape)
        return df

    except DataValidationError as e:
        handle_error(e, "load_and_process_data")
        return None
    except pd.errors.EmptyDataError:
        handle_error(DataValidationError("File CSV rỗng"), "load_and_process_data")
        return None
    except pd.errors.ParserError as e:
        handle_error(DataValidationError(f"Lỗi parse file: {e}"), "load_and_process_data")
        return None
    except Exception as e:
        logger.error("Unexpected error loading file '%s': %s", getattr(file, "name", "unknown"), e, exc_info=True)
        st.error(f"❌ **Lỗi đọc file:** {str(e)}")
        st.caption("💡 Kiểm tra file có bị hỏng hoặc không đúng định dạng")
        return None
