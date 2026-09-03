"""Brief screen — Phase 0 skeleton."""

import streamlit as st


def render_brief_screen(*args, **kwargs):
    st.markdown("## 📋 Brief — AI Data Summary")
    st.caption("Phase 0 skeleton — 1-click brief từ profile JSON (P2), BYOK hoặc rule-based fallback")
    if st.button("Generate Brief (skeleton)", key="brief_skel"):
        st.info("Sẽ gọi POST /brief/{id} — hiện chưa có warehouse, dùng rule-based `core/insights.py`")
    st.markdown('<div class="skeleton skeleton-line" style="height:16px;width:80%"></div>', unsafe_allow_html=True)
