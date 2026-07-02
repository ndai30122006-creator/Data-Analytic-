"""Compare tab — wraps original module"""
import logging
logger = logging.getLogger(__name__)

try:
    from compare_datasets import render_compare_tab
except ImportError as e:
    logger.error("Failed to load compare_datasets: %s", e)
    import streamlit as st
    def render_compare_tab() -> None:
        st.info("Compare tab loading...")