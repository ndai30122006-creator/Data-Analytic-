"""Advanced analytics engine — deep analysis module"""
import logging

logger = logging.getLogger(__name__)

try:
    from src.analytics.analytics_main import render_deep_analysis_tab
except ImportError:
    logger.warning("src.analytics module not available")

    def render_deep_analysis_tab(df, num, cat, dat) -> None:
        """Placeholder when src.analytics is unavailable."""
        import streamlit as st
        st.error("Advanced Analytics module unavailable. Install: pip install scipy scikit-learn statsmodels matplotlib seaborn")
