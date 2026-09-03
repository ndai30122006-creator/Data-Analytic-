"""Lab screen — gộp Statistics + Deep Analysis (P0 Commit 1)."""

import streamlit as st


def render_lab_screen(df=None, num=None, cat=None, dat=None):
    """Lab = Statistics Lab — giữ nguyên engine trong src/core / src/analytics."""
    st.markdown("## 🧪 Lab — Statistics & Deep Analysis")
    st.caption("Gộp Statistics + Deep Analysis cũ — engine giữ nguyên `src/core/analytics_engine`, `src/analytics`")

    # Thử render Deep Analysis nếu có df, fallback skeleton
    try:
        from src.core.analytics_engine import render_deep_analysis_tab

        if df is not None:
            # dat may be None if caller didn't pass
            if dat is None:
                import numpy as np

                dat = df.select_dtypes(include=["datetime"]).columns.tolist() if df is not None else []
            render_deep_analysis_tab(df, num or [], cat or [], dat or [])
        else:
            st.info("Upload dữ liệu để dùng Lab. Hiện hiển thị deep analysis demo.")
            st.markdown('<div class="skeleton skeleton-card" style="height:200px"></div>', unsafe_allow_html=True)
    except Exception as exc:
        st.warning(f"Lab chưa sẵn sàng: {exc}")
        st.markdown('<div class="skeleton skeleton-card" style="height:200px"></div>', unsafe_allow_html=True)

    # Also expose statistics tab as second section for quick access
    with st.expander("Statistics (legacy tab)", expanded=False):
        try:
            from src.ui.tabs.statistics import render_statistics_tab

            if df is not None:
                render_statistics_tab(df, num or [], cat or [])
            else:
                st.caption("Cần dữ liệu để chạy Statistics")
        except Exception as e:
            st.caption(f"Statistics fallback: {e}")
