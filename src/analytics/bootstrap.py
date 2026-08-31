"""Bootstrap & Confidence Intervals (Book Ch.2)"""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from .base import apply_theme, insight_card


def render_bootstrap_tab(df, num, key_prefix="da"):
    """Bootstrap resampling for confidence intervals.

    Args:
        key_prefix: Prefix for Streamlit widget keys to avoid duplicates
                     when rendered in multiple tabs. Default "da" (deep analysis).
    """
    st.markdown("### Bootstrap & Confidence Intervals — via core")
    st.caption("Resampling via `core/statistical_tests.py:105` — fix stat_choice bug")

    if not num:
        st.warning("Cần cột numeric")
        return

    _k = lambda s: f"{key_prefix}_{s}"  # noqa: E731

    col = st.selectbox("Chọn cột:", num, key=_k("boot_col"))
    n_iter = st.slider("Số lần resampling:", 100, 5000, 1000, 100, key=_k("boot_iter"))
    conf_level = st.slider("Confidence Level (%):", 80, 99, 95, 1, key=_k("boot_conf"))
    stat_choice = st.selectbox("Thống kê:", ["Mean", "Median", "Std"], key=_k("boot_stat"))
    stat_map = {"Mean": np.mean, "Median": np.median, "Std": np.std}

    if st.button("Run Bootstrap", key=_k("boot_run")):
        with st.spinner("Đang resampling..."):
            from src.core.statistical_tests import run_bootstrap

            data = df[col].dropna().values
            stat_func = stat_map[stat_choice]
            res = run_bootstrap(data, n_iter=n_iter, conf_level=conf_level, stat_func=stat_func)
            original = res["original"]
            boot_stats = res["boot_stats"]
            ci_lower = res["ci_lower"]
            ci_upper = res["ci_upper"]
            boot_std = res["boot_std"]

            c1, c2, c3 = st.columns(3)
            c1.metric(f"Original {stat_choice}", f"{original:.4f}")
            c2.metric("Bootstrap Std Error", f"{boot_std:.4f}")
            c3.metric(f"{conf_level}% CI", f"[{ci_lower:.4f}, {ci_upper:.4f}]")

            fig = go.Figure()
            fig.add_trace(
                go.Histogram(
                    x=boot_stats, nbinsx=50, marker_color="#818cf8", opacity=0.7, name="Bootstrap distribution"
                )
            )
            fig.add_vline(
                x=original, line_dash="dash", line_color="#34d399", annotation_text=f"Original={original:.3f}"
            )
            fig.add_vline(x=ci_lower, line_dash="dot", line_color="#f87171", annotation_text=f"CI Lower={ci_lower:.3f}")
            fig.add_vline(x=ci_upper, line_dash="dot", line_color="#f87171", annotation_text=f"CI Upper={ci_upper:.3f}")
            fig.update_layout(
                title=f"Bootstrap Distribution of {stat_choice} (n_iter={n_iter})",
                height=400,
                xaxis_title=stat_choice,
                yaxis_title="Frequency",
            )
            apply_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

            insight_card(
                "💡",
                "Interpretation",
                f"Với {conf_level}% confidence, {stat_choice.lower()} nằm trong khoảng "
                f"[{ci_lower:.4f}, {ci_upper:.4f}]. "
                f"Bootstrap SD = {boot_std:.4f} (Standard Error).",
                "good",
            )
