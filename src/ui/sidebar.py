"""Sidebar component for Streamlit UI"""
import streamlit as st
import pandas as pd
import logging

from src.utils.config import TAB_OVERVIEW, TAB_LEARNING_ANALYTICS, TAB_STATISTICS, TAB_COMPARE, TAB_ANALYTICS, TAB_AI_INSIGHTS, TAB_DEEP_ANALYSIS
from src.utils.helpers import apply_theme, sparkline
from src.utils.exceptions import handle_error

logger = logging.getLogger(__name__)


def render_sidebar() -> None:
    """Render the sidebar with navigation, data upload, and dataset management."""
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/bar-chart.png", width=64)
        st.markdown("""<h2 style='text-align: center; margin-top: -0.5rem;'>📊 Data Analyst</h2>""", unsafe_allow_html=True)
        st.markdown("""<p style='text-align: center; font-size: 0.8rem; color: #94a3b8; margin-bottom: 1.5rem;'>Practical Statistics for Data Scientists</p>""", unsafe_allow_html=True)

        st.markdown("### 📁 Data")

        uploaded_file = st.file_uploader(
            "Upload CSV / Excel",
            type=["csv", "xlsx", "xls"],
            key=f"file_uploader_{st.session_state.get('file_uploader_key', 0)}"
        )

        if uploaded_file is not None:
            from src.utils.validators import validate_dataframe
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file, engine="openpyxl")

                is_valid, msg = validate_dataframe(df)
                if is_valid:
                    st.session_state.df = df
                    st.session_state.filename = uploaded_file.name
                    st.session_state.cleaned_df = None
                    st.session_state.file_uploader_key += 1
                    st.success(f"✅ Loaded: {uploaded_file.name} ({df.shape[0]} rows × {df.shape[1]} cols)")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")
            except Exception as e:
                handle_error(e, "render_sidebar / file_upload", f"Lỗi đọc file {uploaded_file.name}")

        if st.session_state.get("df") is not None:
            st.markdown("---")
            st.markdown("### 📊 Current Dataset")
            df = st.session_state.df
            st.caption(f"**{st.session_state.filename}** — {df.shape[0]} rows × {df.shape[1]} cols")

            num_cols = df.select_dtypes(include=['number']).columns.tolist()
            if num_cols:
                with st.expander("📈 Quick Sparklines", expanded=False):
                    sel = st.selectbox("Column:", num_cols, key="side_spark")
                    fig = sparkline(df[sel].dropna())
                    st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.markdown("### 🗃️ Dataset Manager")
            if st.button("💾 Save to Manager", use_container_width=True, key="save_dataset"):
                from src.utils.config import SESSION_KEYS
                name = st.session_state.filename or f"Dataset_{len(st.session_state.datasets) + 1}"
                st.session_state.datasets[name] = df.copy()
                st.success(f"✅ Saved: {name}")

            datasets = st.session_state.get("datasets", {})
            if datasets:
                selected = st.selectbox("Load saved:", ["-- Select --"] + list(datasets.keys()), key="load_ds")
                if selected != "-- Select --":
                    st.session_state.df = datasets[selected].copy()
                    st.session_state.filename = selected
                    st.session_state.cleaned_df = None
                    st.rerun()

            if st.button("🔄 Reset Session", use_container_width=True, type="secondary"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()