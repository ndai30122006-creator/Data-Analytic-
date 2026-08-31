"""Sidebar component — data upload, dataset management, session management, PDF export"""

import logging
import time
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)

from src.services.report_service import generate_pdf_report
from src.services.session_service import get_session_info, has_saved_session, load_session_state, save_session_state
from src.ui.components import render_sidebar_stats
from src.utils.helpers import load_and_process_data
from src.utils.validators import compute_data_quality_score


def render_sidebar():
    """Render the sidebar with data upload, dataset management, session, and PDF export"""
    try:
        with st.sidebar:

            # HEADER — Branding (no external image, no nested columns issue)
            st.markdown(
                "<div style='display:flex;align-items:center;gap:10px;margin-bottom:4px'>"
                "<div style='width:40px;height:40px;border-radius:8px;background:var(--primary);display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:1.1rem;flex-shrink:0'>LA</div>"
                "<div style='line-height:1.25'><div style='font-size:0.95rem;font-weight:700;color:var(--text-primary)'>Learning Analytics</div>"
                "<div style='font-size:0.70rem;color:var(--text-tertiary);letter-spacing:0.04em;text-transform:uppercase'>Pro Max Data-Dense</div></div></div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<hr style='margin:0.75rem 0;border:none;border-top:1px solid var(--border-light);'>",
            unsafe_allow_html=True,
        )

        # 1. DATA INPUT — Pro Max filter sidebar (dense)
        st.markdown("#### DATA INPUT")
        st.caption("CSV / Excel — 50MB max")

        uploaded = st.file_uploader(
            "Upload CSV / Excel",
            type=["csv", "xlsx", "xls"],
            key=f"fu_{st.session_state.file_uploader_key}",
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

        if uploaded:
            for file in uploaded:
                if file.name not in st.session_state.datasets:
                    with st.spinner(f"Loading {file.name}..."):
                        time.sleep(0.3)
                        loaded_df = load_and_process_data(file)
                        if loaded_df is not None:
                            st.session_state.datasets[file.name] = loaded_df
                            st.success(f"{file.name} — OK")

        st.caption("Supported: .csv, .xlsx · cuộn ngang khi bảng rộng")

        st.markdown(
            "<hr style='margin:0.75rem 0;border:none;border-top:1px solid var(--border-light);'>",
            unsafe_allow_html=True,
        )

        # ═══════════════════════════════════════════
        # 2. DATASET MANAGER
        # ═══════════════════════════════════════════
        if st.session_state.datasets:
            st.markdown("#### DATASET MANAGER")

            dataset_names = list(st.session_state.datasets.keys())
            current_selection = st.session_state.get("dataset_selector", "-- Chọn --")
            if current_selection == "-- Chọn --" and dataset_names:
                current_selection = dataset_names[0]

            selected_dataset = st.selectbox(
                "Select dataset",
                ["-- Chọn --"] + dataset_names,
                index=(
                    (["-- Chọn --"] + dataset_names).index(current_selection)
                    if current_selection in ["-- Chọn --"] + dataset_names
                    else 0
                ),
                key="dataset_selector",
                label_visibility="collapsed",
            )

            if selected_dataset != "-- Chọn --":
                if st.session_state.filename != selected_dataset:
                    st.session_state.df = st.session_state.datasets[selected_dataset]
                    st.session_state.filename = selected_dataset
                    st.session_state.cleaned_df = None
                    st.rerun()

            # ── Current Dataset Info Card ──
            if st.session_state.df is not None:
                df = st.session_state.df
                rows = len(df)
                cols = len(df.columns)
                try:
                    quality_pct = compute_data_quality_score(df)["overall"]
                except Exception:
                    quality_pct = 0.0

                st.markdown(
                    f"""
                <div style="
                    background: var(--card);
                    border: 1px solid var(--border-light);
                    border-radius: var(--radius-md);
                    padding: 10px 12px;
                    margin: 6px 0;
                ">
                    <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap">
                        <span style="font-weight:600;font-size:0.82rem;color:var(--text-primary);overflow-wrap:break-word;flex:1">{st.session_state.filename}</span>
                        <span class="badge badge-success" style="flex-shrink:0">{quality_pct}%</span>
                    </div>
                    <div style="font-size:0.72rem;color:var(--text-tertiary);margin-top:4px;font-family:var(--font-mono)">
                        {rows:,} rows × {cols} cols
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                if st.button("Reset", use_container_width=True, key="sidebar_reset"):
                    st.session_state.df = None
                    st.session_state.filename = ""
                    st.session_state.datasets = {}
                    st.session_state.cleaned_df = None
                    st.session_state.file_uploader_key += 1
                    st.rerun()

                if selected_dataset != "-- Chọn --":
                    if st.button(f"Remove “{selected_dataset}”", use_container_width=True, key="del_dataset"):
                        del st.session_state.datasets[selected_dataset]
                        if st.session_state.filename == selected_dataset:
                            st.session_state.df = None
                            st.session_state.filename = ""
                        st.rerun()

        st.markdown(
            "<hr style='margin:0.75rem 0;border:none;border-top:1px solid var(--border-light);'>",
            unsafe_allow_html=True,
        )

        # 3. SETTINGS — Pro Max both modes supported
        st.markdown("#### SETTINGS")
        theme_col1, theme_col2 = st.columns(2)
        with theme_col1:
            if st.button("Light", use_container_width=True, help="Light — Pro Max Data-Dense"):
                st.session_state.theme_mode = "light"
                st.rerun()
        with theme_col2:
            if st.button("Dark", use_container_width=True, help="Dark — Pro Max"):
                st.session_state.theme_mode = "dark"
                st.rerun()

        mode_name = "Light" if st.session_state.get("theme_mode", "light") == "light" else "Dark"
        st.caption(f"Current: **{mode_name}** — Pro Max")

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        # ═══════════════════════════════════════════
        # 4. SESSION & EXPORT (only when data loaded)
        # ═══════════════════════════════════════════
        if st.session_state.df is not None:
            st.markdown("#### SESSION & EXPORT")

            sess_col1, sess_col2 = st.columns(2)
            with sess_col1:
                if st.button("Save Session", use_container_width=True, key="save_sess"):
                    ok, msg = save_session_state()
                    st.success(msg) if ok else st.error(msg)
            with sess_col2:
                if st.button("Load Session", use_container_width=True, key="load_sess"):
                    ok, msg = load_session_state()
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.warning(msg)

            if has_saved_session():
                info = get_session_info()
                if info:
                    st.caption(f"Last: {info['filename']} ({info['rows']} × {info['cols']})")

            df = st.session_state.df
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

            if st.button("Generate PDF Report", use_container_width=True, key="gen_pdf"):
                with st.spinner("Generating PDF report..."):
                    try:
                        pdf_bytes = generate_pdf_report(
                            df, num_cols, cat_cols, filename=st.session_state.get("filename", "dataset")
                        )
                        st.session_state["_pdf_bytes"] = pdf_bytes
                        st.session_state["_pdf_filename"] = f"report_{datetime.now():%Y%m%d_%H%M}.pdf"
                        st.success("PDF Report generated!")
                    except Exception as e:
                        logger.error("PDF generation failed: %s", e, exc_info=True)
                        st.error(f"Lỗi tạo PDF: {str(e)}")

            if st.session_state.get("_pdf_bytes"):
                st.download_button(
                    "Download PDF Report",
                    st.session_state["_pdf_bytes"],
                    st.session_state.get("_pdf_filename", "report.pdf"),
                    "application/pdf",
                    key="dl_pdf",
                )

        # ── Bottom spacer ──
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    except Exception as exc:
        # Fallback so sidebar never crashes the whole app (was reported as "side bar đang bị lỗi")
        import traceback

        logger.error("render_sidebar failed: %s", exc, exc_info=True)
        try:
            st.sidebar.error(f"Sidebar lỗi: {exc}")
            st.sidebar.caption("Thử `streamlit run app.py` lại hoặc xóa `st.session_state`")
            if st.sidebar.button("Reset session", key="sidebar_error_reset"):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()
        except Exception:
            pass
        # Also log to main area if sidebar context missing
        try:
            st.error(f"Sidebar lỗi: {exc}")
        except Exception:
            pass
