"""Overview tab — Bento Grid dashboard with KPI cards, charts, data quality, preview and export."""

from datetime import datetime
from io import BytesIO

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.ui.components import render_column_profiler, render_data_dictionary, render_data_quality_report
from src.utils.config import MAX_DISPLAY_ROWS, MIN_ROWS_VALIDATION
from src.utils.helpers import apply_theme, convert_df_to_csv, sparkline
from src.utils.validators import validate_dataframe

try:
    from src.ui.theme import gradient_text, icon, metric_card, status_badge
except ImportError:

    def metric_card(title, value, change="", icon="chart", color="primary"):
        return f'<div class="metric-card"><h4>{icon} {title}</h4><h2>{value}</h2></div>'

    def status_badge(text, status="primary"):
        return f"<span>{text}</span>"

    def gradient_text(text, c1="#1E40AF", c2="#D97706"):
        return f"<span style='font-weight:700'>{text}</span>"

    def icon(name, size=""):
        return ""


def render_bento_dashboard(df, num, cat):
    """Pro Max Bento Grid — Data-Dense: 12-col KPI row, compact, Lucide icons."""
    # ── KPI row — Data-Dense compact (gap 8px, padding 12px) ──
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(
            metric_card("Tổng quan dữ liệu", f"{len(df):,} dòng · {df.shape[1]} cột", icon="database", color="primary"),
            unsafe_allow_html=True,
        )
    with col2:
        if num:
            st.markdown(
                metric_card(
                    "Điểm TB", f"{df[num[0]].mean():.2f}", f"Min: {df[num[0]].min():.1f}", "trending", color="accent"
                ),
                unsafe_allow_html=True,
            )
        else:
            st.markdown(metric_card("Điểm TB", "N/A", icon="trending", color="primary"), unsafe_allow_html=True)
    with col3:
        if num:
            pass_rate = (df[num[0]] >= 5.0).mean() * 100
            st.markdown(
                metric_card("Tỷ lệ đạt", f"{pass_rate:.1f}%", f"≥ 5.0", "check", color="success"),
                unsafe_allow_html=True,
            )
        else:
            st.markdown(metric_card("Tỷ lệ đạt", "N/A", icon="check", color="success"), unsafe_allow_html=True)

    # ── Trends + Distribution — dense layout ──
    col_left, col_right = st.columns([1, 2])
    with col_left:
        st.markdown("#### Top trends")
        st.caption("Sparkline — 200 điểm gần nhất")
        if num:
            for c in num[:2]:
                st.markdown(f"**{c}**")
                st.plotly_chart(sparkline(df[c].dropna().head(200)), use_container_width=True)
    with col_right:
        st.markdown("#### Phân phối điểm")
        if num:
            fig = px.histogram(
                df, x=num[0], nbins=30, marginal="box", title=f"{num[0]}", color_discrete_sequence=["#1E40AF"]
            )
            fig.update_traces(marker_line_width=0, opacity=0.85)
            apply_theme(fig)
            st.plotly_chart(fig, use_container_width=True)


def render_interactive_table(df):
    """Pro Max: filter bar + overflow-x-auto wrapper + dense table."""
    st.markdown("#### Dữ liệu chi tiết")
    st.caption("Lọc cột, nhóm, và sắp xếp — cuộn ngang khi bảng rộng")

    # Filter bar — Pro Max smooth filter animations
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    group_col = st.selectbox("Nhóm theo:", ["Không"] + df.columns.tolist(), key="group_by")
    st.markdown("</div>", unsafe_allow_html=True)
    if group_col != "Không":
        grouped = df.groupby(group_col).agg(["mean", "count", "sum"]).reset_index()
        st.markdown('<div class="dataframe-wrapper">', unsafe_allow_html=True)
        st.dataframe(grouped, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        cols = st.multiselect("Hiển thị cột:", df.columns.tolist(), default=df.columns.tolist()[:5])
        if cols:
            col_config = {}
            for c in cols:
                if pd.api.types.is_numeric_dtype(df[c].dtype):
                    col_config[c] = st.column_config.NumberColumn(c)
                elif "date" in c.lower() or "time" in c.lower():
                    col_config[c] = st.column_config.DatetimeColumn(c)
                else:
                    col_config[c] = st.column_config.TextColumn(c)
            st.markdown('<div class="dataframe-wrapper">', unsafe_allow_html=True)
            st.dataframe(df[cols], use_container_width=True, column_config=col_config)
            st.markdown("</div>", unsafe_allow_html=True)


def render_overview_tab(df, num, cat):
    """Pro Max Overview — Bento + Data Quality + Preview + Export."""
    is_valid, msg = validate_dataframe(df, min_rows=MIN_ROWS_VALIDATION)
    if not is_valid:
        st.error(f"{msg}")
        return

    render_bento_dashboard(df, num, cat)

    st.markdown("### Data Quality")
    st.caption("Pro Max — gauge `#1E40AF`/amber, tabular nums")
    render_data_quality_report(df)
    st.divider()

    render_interactive_table(df)
    st.divider()

    chart_left, chart_right = st.columns([1, 1])
    with chart_left:
        if cat:
            st.markdown("### Top Categories")
            vc = df[cat[0]].value_counts().head(10)
            fig = px.bar(
                y=vc.index,
                x=vc.values,
                orientation="h",
                title=f"Top {cat[0]}",
                color=vc.values,
                color_continuous_scale="Blues",
            )
            fig.update_traces(marker_line_width=0)
            apply_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
    with chart_right:
        st.markdown("### Data Preview")
        st.caption("Cuộn ngang khi nhiều cột — 100 dòng đầu")
        col_config = {}
        for c in df.columns:
            if pd.api.types.is_numeric_dtype(df[c].dtype):
                col_config[c] = st.column_config.NumberColumn(c)
            elif "date" in c.lower() or "time" in c.lower():
                col_config[c] = st.column_config.DatetimeColumn(c)
            else:
                col_config[c] = st.column_config.TextColumn(c)
        st.markdown('<div class="dataframe-wrapper">', unsafe_allow_html=True)
        st.dataframe(df.head(MAX_DISPLAY_ROWS), use_container_width=True, column_config=col_config, height=280)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Export")
    fmt = st.radio("Format:", ["CSV", "Excel"], horizontal=True, label_visibility="collapsed")
    if fmt == "CSV":
        st.download_button(
            "Download CSV",
            convert_df_to_csv(df),
            f"data_{datetime.now():%Y%m%d}.csv",
            "text/csv",
            use_container_width=True,
        )
    else:
        out = BytesIO()
        with pd.ExcelWriter(out, engine="openpyxl") as w:
            df.to_excel(w, index=False, sheet_name="Data")
        st.download_button(
            "Download Excel",
            out.getvalue(),
            f"data_{datetime.now():%Y%m%d}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    with st.expander("Data Dictionary & Column Profiler", expanded=False):
        rt = st.tabs(["Dictionary", "Profiler"])
        with rt[0]:
            render_data_dictionary(df)
        with rt[1]:
            render_column_profiler(df, num, cat)
