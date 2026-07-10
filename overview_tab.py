"""Overview tab — Bento Grid dashboard with KPI cards, charts, data quality, preview and export."""
from io import BytesIO
from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from config import MIN_ROWS_VALIDATION, MAX_DISPLAY_ROWS
from utils import validate_dataframe
from components import (
    render_data_dictionary, render_column_profiler,
    render_data_quality_report
)
from helpers import convert_df_to_csv, sparkline, apply_theme

try:
    from theme_config import metric_card, status_badge, gradient_text
except ImportError:
    def metric_card(title, value, change="", icon="📊", color="primary"):
        return f'<div class="metric-card"><h4>{icon} {title}</h4><h2>{value}</h2></div>'
    def status_badge(text, status="primary"):
        return f"<span>{text}</span>"
    def gradient_text(text, c1="#1877F2", c2="#E4405F"):
        return f"<span style='font-weight:700'>{text}</span>"


def render_overview_tab(df, num, cat):
    """Render the Overview tab with Bento Grid layout."""
    is_valid, msg = validate_dataframe(df, min_rows=MIN_ROWS_VALIDATION)
    if not is_valid:
        st.error(f"❌ {msg}")
        return

    pct = round((1 - df.isnull().sum().sum() / (len(df) * df.shape[1])) * 100, 1)
    missing = df.isnull().sum().sum()

    # ═══════════════════════════════════════════════════════════
    # BENTO GRID LAYOUT
    # ┌─────────────┬─────────────┬─────────────┐
    # │  📊 Tổng    │  📈 Điểm TB  │  🎯 Tỷ lệ   │
    # │  quan (Lớn) │  87.4 (Nhỏ) │  đạt (Nhỏ)  │
    # ├─────────────┼─────────────┴─────────────┤
    # │  🔥 Trends  │  📉 Phân phối điểm        │
    # │  (Vừa)      │  (Biểu đồ lớn)            │
    # ├─────────────┼────────────────────────────┤
    # │  ⚠️ Quality │  📋 Data Preview          │
    # └─────────────┴────────────────────────────┘
    # ═══════════════════════════════════════════════════════════

    # ── Row 1: KPI Cards (3 across) ──
    r1_cols = st.columns([2, 1.2, 1.2])
    with r1_cols[0]:
        st.markdown(metric_card("📊 Tổng quan", f"{len(df):,} rows",
                                 f"{df.shape[1]} columns", "📊"), unsafe_allow_html=True)
    with r1_cols[1]:
        delta_quality = f"{'↑' if pct >= 80 else '↓'} {pct:.1f}%"
        st.markdown(metric_card("✅ Chất lượng", f"{pct}%", delta_quality, "✅"), unsafe_allow_html=True)
    with r1_cols[2]:
        delta_missing = f"{'↓' if missing == 0 else '↑'} {missing:,}"
        st.markdown(metric_card("❌ Thiếu", f"{missing:,}", delta_missing, "❌"), unsafe_allow_html=True)

    # ── Row 2: Trends (left) + Distribution chart (right) ──
    r2_cols = st.columns([1, 1.8])
    with r2_cols[0]:
        st.markdown("### 🔥 Data Trends")
        if num:
            for i, c in enumerate(num[:3]):
                st.markdown(f"**{c}**")
                st.plotly_chart(sparkline(df[c].dropna().head(200)), use_container_width=True)
    with r2_cols[1]:
        # Distribution chart (larger)
        if num:
            st.markdown("### 📉 Phân phối điểm")
            fig = px.histogram(df, x=num[0], nbins=30, marginal="box",
                             title=f"{num[0]}", color_discrete_sequence=["#6366F1"])
            fig.update_traces(marker_line_width=0, opacity=0.8)
            apply_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

    # ── Row 3: Quality Report (left) + Data Preview (right) ──
    r3_cols = st.columns([1, 1.8])
    with r3_cols[0]:
        st.markdown("### ⚠️ Data Quality")
        render_data_quality_report(df)

    with r3_cols[1]:
        st.markdown("### 📋 Data Preview")
        col_config = {}
        for c in df.columns:
            if pd.api.types.is_numeric_dtype(df[c].dtype):
                col_config[c] = st.column_config.NumberColumn(c)
            elif "date" in c.lower() or "time" in c.lower():
                col_config[c] = st.column_config.DatetimeColumn(c)
            else:
                col_config[c] = st.column_config.TextColumn(c)
        st.dataframe(
            df.head(MAX_DISPLAY_ROWS),
            use_container_width=True,
            column_config=col_config,
            height=280
        )

    # ── Row 4: Categorical chart + Export ──
    r4_cols = st.columns([1, 1])
    with r4_cols[0]:
        if cat:
            st.markdown("### 🏷️ Top Categories")
            vc = df[cat[0]].value_counts().head(10)
            fig = px.bar(y=vc.index, x=vc.values, orientation='h', title=f"Top {cat[0]}",
                        color=vc.values, color_continuous_scale="Viridis")
            fig.update_traces(marker_line_width=0)
            apply_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

    with r4_cols[1]:
        st.markdown("### 📤 Export")
        fmt = st.radio("Format:", ["CSV", "Excel"], horizontal=True)
        col_a, col_b = st.columns(2)
        with col_a:
            if fmt == "CSV":
                st.download_button("📥 Download CSV", convert_df_to_csv(df),
                                 f"data_{datetime.now():%Y%m%d}.csv", "text/csv",
                                 use_container_width=True)
            else:
                out = BytesIO()
                with pd.ExcelWriter(out, engine="openpyxl") as w:
                    df.to_excel(w, index=False, sheet_name="Data")
                st.download_button("📥 Download Excel", out.getvalue(),
                                 f"data_{datetime.now():%Y%m%d}.xlsx",
                                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 use_container_width=True)
        with col_b:
            if st.button("🔄 Reset Session", use_container_width=True):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()

    # ── Data Dictionary & Column Profiler (expandable) ──
    with st.expander("📖 Data Dictionary & Column Profiler", expanded=False):
        rt = st.tabs(["📖 Dictionary", "🔍 Profiler"])
        with rt[0]: render_data_dictionary(df)
        with rt[1]: render_column_profiler(df, num, cat)