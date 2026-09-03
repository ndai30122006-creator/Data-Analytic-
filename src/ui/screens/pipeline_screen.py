"""Pipeline screen — Phase 0 skeleton."""

import streamlit as st


def render_pipeline_screen(*args, **kwargs):
    st.markdown("## ⚙️ Pipeline — AI ETL/ELT")
    st.caption("Phase 0 skeleton — sẽ là chat NL → YAML spec → dry-run → run → history (P3)")
    st.markdown('<div class="skeleton skeleton-card" style="height:140px"></div>', unsafe_allow_html=True)
    st.text_area("Mô tả pipeline (placeholder)", placeholder="VD: điền missing bằng median, xóa trùng...", height=100, key="pipeline_nl_ph")
