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


def render_bento_dashboard(df, num, cat):
    """Render a clean Bento Grid layout for the overview dashboard."""
    # ── Hàng 1: 1 cột lớn + 2 cột nhỏ ──
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(metric_card("📊 Tổng quan dữ liệu", f"{len(df):,} dòng · {df.shape[1]} cột",
                                 icon="📊"), unsafe_allow_html=True)
    with col2:
        if num:
            st.markdown(metric_card("📈 Điểm TB", f"{df[num[0]].mean():.2f}",
                                     f"Min: {df[num[0]].min():.1f}", "📈"), unsafe_allow_html=True)
        else:
            st.markdown(metric_card("📈 Điểm TB", "N/A", icon="📈"), unsafe_allow_html=True)
    with col3:
        if num:
            pass_rate = (df[num[0]] >= 5.0).mean() * 100
            st.markdown(metric_card("✅ Tỷ lệ đạt", f"{pass_rate:.1f}%",
                                     f"≥ 5.0", "✅"), unsafe_allow_html=True)
        else:
            st.markdown(metric_card("✅ Tỷ lệ đạt", "N/A", icon="✅"), unsafe_allow_html=True)

    # ── Hàng 2: 1 cột trái (vừa) + 1 cột phải (lớn) ──
    col_left, col_right = st.columns([1, 2])
    with col_left:
        st.markdown("#### 🔥 Top trends")
        if num:
            for c in num[:2]:
                st.markdown(f"**{c}**")
                st.plotly_chart(sparkline(df[c].dropna().head(200)), width='stretch')
    with col_right:
        st.markdown("#### 📈 Phân phối điểm")
        if num:
            fig = px.histogram(df, x=num[0], nbins=30, marginal="box",
                             title=f"{num[0]}", color_discrete_sequence=["#6366F1"])
            fig.update_traces(marker_line_width=0, opacity=0.8)
            apply_theme(fig)
            st.plotly_chart(fig, width='stretch')


def render_interactive_table(df):
    """Render an interactive data table with grouping and column selection (Airtable-style)."""
    st.markdown("#### 📋 Dữ liệu chi tiết")

    # Chọn cột để nhóm
    group_col = st.selectbox("Nhóm theo:", ["Không"] + df.columns.tolist(), key="group_by")
    if group_col != "Không":
        grouped = df.groupby(group_col).agg(['mean', 'count', 'sum']).reset_index()
        st.dataframe(grouped, width='stretch')
    else:
        # Cho phép lọc cột
        cols = st.multiselect("Hiển thị cột:", df.columns.tolist(),
                              default=df.columns.tolist()[:5])
        if cols:
            # Smart column config
            col_config = {}
            for c in cols:
                if pd.api.types.is_numeric_dtype(df[c].dtype):
                    col_config[c] = st.column_config.NumberColumn(c)
                elif "date" in c.lower() or "time" in c.lower():
                    col_config[c] = st.column_config.DatetimeColumn(c)
                else:
                    col_config[c] = st.column_config.TextColumn(c)
            st.dataframe(df[cols], width='stretch', column_config=col_config)


def render_overview_tab(df, num, cat):
    """Render the Overview tab with Bento Grid layout."""
    is_valid, msg = validate_dataframe(df, min_rows=MIN_ROWS_VALIDATION)
    if not is_valid:
        st.error(f"❌ {msg}")
        return

    # Bento Dashboard
    render_bento_dashboard(df, num, cat)

    # ── Data Quality ──
    st.markdown("### ⚠️ Data Quality")
    render_data_quality_report(df)
    st.divider()

    # ── Interactive Table ──
    render_interactive_table(df)
    st.divider()

    # ── Charts ──
    chart_left, chart_right = st.columns([1, 1])
    with chart_left:
        if cat:
            st.markdown("### 🏷️ Top Categories")
            vc = df[cat[0]].value_counts().head(10)
            fig = px.bar(y=vc.index, x=vc.values, orientation='h', title=f"Top {cat[0]}",
                        color=vc.values, color_continuous_scale="Viridis")
            fig.update_traces(marker_line_width=0)
            apply_theme(fig)
            st.plotly_chart(fig, width='stretch')
    with chart_right:
        st.markdown("### 📋 Data Preview")
        col_config = {}
        for c in df.columns:
            if pd.api.types.is_numeric_dtype(df[c].dtype):
                col_config[c] = st.column_config.NumberColumn(c)
            elif "date" in c.lower() or "time" in c.lower():
                col_config[c] = st.column_config.DatetimeColumn(c)
            else:
                col_config[c] = st.column_config.TextColumn(c)
        st.dataframe(df.head(MAX_DISPLAY_ROWS), width='stretch',
                     column_config=col_config, height=280)

    # ── Export ──
    st.markdown("### 📤 Export")
    fmt = st.radio("Format:", ["CSV", "Excel"], horizontal=True)
    col_a, col_b = st.columns(2)
    with col_a:
        if fmt == "CSV":
            st.download_button("📥 Download CSV", convert_df_to_csv(df),
                             f"data_{datetime.now():%Y%m%d}.csv", "text/csv",
                             width='stretch')
        else:
            out = BytesIO()
            with pd.ExcelWriter(out, engine="openpyxl") as w:
                df.to_excel(w, index=False, sheet_name="Data")
            st.download_button("📥 Download Excel", out.getvalue(),
                             f"data_{datetime.now():%Y%m%d}.xlsx",
                             "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             width='stretch')
    with col_b:
        if st.button("🔄 Reset Session", width='stretch'):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    # ── Data Dictionary & Column Profiler ──
    with st.expander("📖 Data Dictionary & Column Profiler", expanded=False):
        rt = st.tabs(["📖 Dictionary", "🔍 Profiler"])
        with rt[0]: render_data_dictionary(df)
        with rt[1]: render_column_profiler(df, num, cat)
