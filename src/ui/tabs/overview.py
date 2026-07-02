"""Overview tab — wraps original overview_tab module for backward compatibility"""
import logging

logger = logging.getLogger(__name__)

try:
    from overview_tab import render_overview_tab
except ImportError as e:
    logger.error("Failed to load overview_tab: %s", e)
    import streamlit as st
    def render_overview_tab(df, num, cat) -> None:
        st.info("Overview tab loading...")