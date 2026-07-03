"""Sidebar component — data upload, dataset management, session management, PDF export"""
import logging
import time
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

from utils import load_and_process_data
from components import render_sidebar_stats
from report_utils import save_session_state, load_session_state, has_saved_session, get_session_info, generate_pdf_report


def render_sidebar():
    """Render the sidebar with data upload, dataset management, session, and PDF export"""
    with st.sidebar:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image("https://cdn-icons-png.flaticon.com/512/4727/4727496.png", width=50)
        with col2:
            st.markdown("### 🎓 Learning Analytics")

        st.markdown("---")

        # ── File Upload & Dataset Management ──
        with st.expander("📂 Data Input", expanded=(st.session_state.df is None)):
            uploaded = st.file_uploader(
                "Upload CSV / Excel", type=["csv", "xlsx", "xls"],
                key=f"fu_{st.session_state.file_uploader_key}",
                accept_multiple_files=True
            )

            if uploaded:
                for file in uploaded:
                    if file.name not in st.session_state.datasets:
                        with st.spinner(f"Loading {file.name}..."):
                            time.sleep(0.3)
                            loaded_df = load_and_process_data(file)
                            if loaded_df is not None:
                                st.session_state.datasets[file.name] = loaded_df
                                st.success(f"✅ {file.name}")

            if st.session_state.datasets:
                st.markdown("#### 📊 Datasets")
                dataset_names = list(st.session_state.datasets.keys())
                current_selection = st.session_state.get("dataset_selector", "-- Chọn --")
                if current_selection == "-- Chọn --" and dataset_names:
                    current_selection = dataset_names[0]

                selected_dataset = st.selectbox(
                    "Chọn dataset:", ["-- Chọn --"] + dataset_names,
                    index=(["-- Chọn --"] + dataset_names).index(current_selection) if current_selection in ["-- Chọn --"] + dataset_names else 0,
                    key="dataset_selector"
                )

                if selected_dataset != "-- Chọn --":
                    if st.session_state.filename != selected_dataset:
                        st.session_state.df = st.session_state.datasets[selected_dataset]
                        st.session_state.filename = selected_dataset
                        st.session_state.cleaned_df = None
                        st.rerun()

                if selected_dataset != "-- Chọn --":
                    if st.button(f"🗑 Xóa {selected_dataset}", key="del_dataset", use_container_width=True):
                        del st.session_state.datasets[selected_dataset]
                        if st.session_state.filename == selected_dataset:
                            st.session_state.df = None
                            st.session_state.filename = ""
                        st.rerun()

            if st.session_state.df is not None:
                st.caption(f"📄 {st.session_state.filename}")
                if st.button("🗑 Clear All", key="clr", use_container_width=True):
                    st.session_state.df = None
                    st.session_state.filename = ""
                    st.session_state.datasets = {}
                    st.session_state.cleaned_df = None
                    st.session_state.file_uploader_key += 1
                    st.rerun()

        # ── Dataset Stats & Session Management ──
        if st.session_state.df is not None:
            st.markdown("---")
            render_sidebar_stats(st.session_state.df)

            df = st.session_state.df
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

            with st.expander("💾 Session Management", expanded=False):
                sess_col1, sess_col2 = st.columns(2)
                with sess_col1:
                    if st.button("💾 Save Session", use_container_width=True, key="save_sess"):
                        ok, msg = save_session_state()
                        st.success(msg) if ok else st.error(msg)
                with sess_col2:
                    if st.button("📂 Load Session", use_container_width=True, key="load_sess"):
                        ok, msg = load_session_state()
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.warning(msg)

                if has_saved_session():
                    info = get_session_info()
                    if info:
                        st.caption(f"📁 Last: {info['filename']} ({info['rows']} × {info['cols']})")

            with st.expander("📄 Export PDF Report", expanded=False):
                st.caption("Generate a beautiful PDF report of your analysis")
                if st.button("📄 Generate PDF Report", use_container_width=True, key="gen_pdf"):
                    with st.spinner("⏳ Generating PDF report..."):
                        try:
                            pdf_bytes = generate_pdf_report(
                                df, num_cols, cat_cols,
                                filename=st.session_state.get("filename", "dataset")
                            )
                            st.download_button(
                                "📥 Download PDF Report",
                                pdf_bytes,
                                f"report_{datetime.now():%Y%m%d_%H%M}.pdf",
                                "application/pdf",
                                key="dl_pdf"
                            )
                            st.success("✅ PDF Report generated!")
                        except Exception as e:
                            logger.error("PDF generation failed: %s", e, exc_info=True)
                            st.error(f"❌ **Lỗi tạo PDF:** {str(e)}")
                            st.caption("💡 Kiểm tra lại dữ liệu hoặc thử lại sau")
