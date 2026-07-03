"""Data Analyst Pro v3.0 — Practical Statistics for Data Scientists Edition"""
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import streamlit as st
import pandas as pd
import numpy as np

from src.ui.theme import render_theme
from sidebar import render_sidebar
from landing import render_landing_page
from overview_tab import render_overview_tab
from learning_analytics import render_learning_analytics_tab
from statistics_tab import render_statistics_tab
from compare_datasets import render_compare_tab
from analytics_tab import render_analytics_tab
from ai_insights import render_ai_insights_tab

from src.utils.exceptions import handle_error

try:
    from advanced_analytics import render_deep_analysis_tab
    DEEP_ANALYSIS_AVAIL = True
except ImportError as e:
    DEEP_ANALYSIS_AVAIL = False
    logger.warning("Advanced analytics module not available: %s", e)
except Exception as e:
    DEEP_ANALYSIS_AVAIL = False
    logger.error("Failed to load advanced analytics: %s", e, exc_info=True)

# ── Session State Init ──
SESSION_DEFAULTS = [
    ("df", None), ("filename", ""), ("cleaned_df", None),
    ("file_uploader_key", 0),
    ("datasets", {}), ("compare_datasets", []),
    ("ai_report", None),
]
for key, default in SESSION_DEFAULTS:
    if key not in st.session_state:
        st.session_state[key] = default

try:
    st.set_page_config(
        page_title="Learning Analytics Thống kê", page_icon="🎓",
        layout="wide", initial_sidebar_state="expanded"
    )
except Exception as e:
    logger.error("Page config failed: %s", e, exc_info=True)

# ── Inject Theme ──
render_theme()

# ── Sidebar ──
render_sidebar()

# ═══════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════
if st.session_state.df is None:
    render_landing_page()
else:
    raw = st.session_state.df
    num = raw.select_dtypes(include=[np.number]).columns.tolist()
    cat = raw.select_dtypes(include=["object", "category"]).columns.tolist()
    dat = raw.select_dtypes(include=["datetime64", "datetime64[ns]"]).columns.tolist()
    df = st.session_state.cleaned_df if st.session_state.cleaned_df is not None else raw

    from config import MAIN_TABS
    main_tabs = st.tabs(MAIN_TABS)

    with main_tabs[0]: render_overview_tab(df, num, cat)
    with main_tabs[1]: render_learning_analytics_tab(df, num, cat)
    with main_tabs[2]: render_statistics_tab(df, num, cat)
    with main_tabs[3]: render_compare_tab()
    with main_tabs[4]: render_analytics_tab(df, num, cat)
    with main_tabs[5]: render_ai_insights_tab(df, num, cat)
    with main_tabs[6]:
        if DEEP_ANALYSIS_AVAIL:
            render_deep_analysis_tab(df, num, cat, dat)
        else:
            st.error("Advanced Analytics module unavailable.")
            with st.expander("🔧 Install dependencies", expanded=True):
                st.code("pip install scipy scikit-learn statsmodels matplotlib seaborn")
                if st.button("🔄 Refresh", key="da_refresh"):
                    st.rerun()

st.caption("📊 Data Analyst Pro v3.0 — Practical Statistics for Data Scientists, 2nd Ed")
