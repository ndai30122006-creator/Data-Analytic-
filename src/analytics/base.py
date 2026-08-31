"""Base utilities shared across all advanced analytics modules."""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.utils.config import CHART_THEME, get_chart_theme  # CHART_THEME kept for back-compat


def apply_theme(fig):
    mode = st.session_state.get("theme_mode", "light")
    fig.update_layout(**get_chart_theme(mode))
    return fig


def insight_card(icon, title, msg, type="info"):
    st.markdown(
        f'<div class="insight-card insight-{type}"><strong>{icon} {title}</strong><br>{msg}</div>',
        unsafe_allow_html=True,
    )


def validate_df(df, num, cat=None, min_rows=5, min_numeric=1):
    if df is None or len(df) == 0:
        st.error("❌ Dataset rỗng")
        return False
    if len(df) < min_rows:
        st.warning(f"⚠️ Cần ít nhất {min_rows} dòng (hiện có {len(df)})")
        return False
    if len(num) < min_numeric:
        st.warning(f"⚠️ Cần ít nhất {min_numeric} cột numeric (hiện có {len(num)})")
        return False
    return True


def make_key(base: str, prefix: str = "") -> str:
    """Create a unique Streamlit widget key to avoid duplicates when
    the same module is used in multiple tabs."""
    return f"{prefix}_{base}" if prefix else base
