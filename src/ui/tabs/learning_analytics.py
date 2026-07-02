"""Learning Analytics tab — wraps original module"""
import logging
logger = logging.getLogger(__name__)

try:
    from learning_analytics import render_learning_analytics_tab
except ImportError as e:
    logger.error("Failed to load learning_analytics: %s", e)
    import streamlit as st
    def render_learning_analytics_tab(df, num, cat) -> None:
        st.info("Learning Analytics tab loading...")