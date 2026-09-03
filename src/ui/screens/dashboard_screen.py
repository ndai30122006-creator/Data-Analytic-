"""Dashboard screen — Phase 0 skeleton."""

import streamlit as st


def render_dashboard_screen(*args, **kwargs):
    st.markdown("## 📊 Dashboard — AI Generation")
    st.caption("Phase 0 skeleton — sinh 4-6 charts từ DashboardSpec (P4)")
    st.markdown('<div class="skeleton skeleton-card" style="height:160px"></div>', unsafe_allow_html=True)
    st.selectbox("Chart type (placeholder)", ["Bar", "Line", "Scatter", "KPI"], key="dash_type_ph")
