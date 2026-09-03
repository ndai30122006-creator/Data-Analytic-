"""Ingest screen — Phase 0 skeleton (P0 Commit 1)."""

import streamlit as st


def render_ingest_screen(*args, **kwargs):
    """Skeleton for Ingest screen (P0)."""
    st.markdown("## 📥 Ingest — Upload & Profile")
    st.caption("Phase 0 skeleton — sẽ thay bằng upload → preview 20 rows → confirm ingest (P1)")
    st.info("Chưa có dữ liệu? Upload CSV/Excel ở sidebar để bắt đầu.")
    # Placeholder preview area
    if st.session_state.get("df") is not None:
        df = st.session_state.df
        st.markdown(f"**Preview:** {len(df):,} rows × {len(df.columns)} cols")
        st.dataframe(df.head(20), use_container_width=True)
    else:
        st.markdown('<div class="skeleton skeleton-card" style="height:120px"></div>', unsafe_allow_html=True)
