"""Statistics tab — wraps original module"""
import logging
logger = logging.getLogger(__name__)

try:
    from statistics_tab import render_statistics_tab
except ImportError as e:
    logger.error("Failed to load statistics_tab: %s", e)
    import streamlit as st
    def render_statistics_tab(df, num, cat) -> None:
        st.info("Statistics tab loading...")