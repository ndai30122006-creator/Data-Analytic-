"""Overview tab — KPI cards, sparklines, charts, data dictionary, profiler, export"""
from io import BytesIO
from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from config import MIN_ROWS_VALIDATION, MAX_DISPLAY_ROWS
from utils import validate_dataframe
from components import (
    render_kpi_card, render_data_dictionary, render_column_profiler,
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
    """Render the Overview tab with KPIs, charts, data dictionary, profiler, and export"""
    is_valid, msg = validate_dataframe(df, min_rows=MIN_ROWS_VALIDATION)
    if not is_valid:
        st.error(f"❌ {msg}")
        return

    # ═══════════════════════════════════════
    # KPI METRIC CARDS — with hover effect
    # ═══════════════════════════════════════
    st.markdown("### 📊 Key Metrics")
    pct = round((1 - df.isnull().sum().sum() / (len(df) * df.shape[1])) * 100, 1)
    missing = df.isnull().sum().sum()
    kpi_data = [
        ("📦 Rows", f"{len(df):,}", "↑ 0%", "📦"),
        ("🔧 Columns", str(df.shape[1]), "→ 0%", "🔧"),
        ("✅ Quality", f"{pct}%", f"{'↑' if pct >= 80 else '↓'} {pct:.1f}%", "✅"),
        ("❌ Missing", f"{missing:,}", f"{'↓' if missing == 0 else '↑'} {missing}", "❌"),
    ]
    kpi_cols = st.columns(4)
    for i, (label, value, change, icon) in enumerate(kpi_data):
        with kpi_cols[i]:
            st.markdown(metric_card(label, value, change, icon), unsafe_allow_html=True)

    # Data Quality Report
    render_data_quality_report(df)

    # ═══════════════════════════════════════
    # SPARKLINE TRENDS
    # ═══════════════════════════════════════
    if num:
        st.markdown("### 📈 Data Trends")
        spark_cols = st.columns(min(len(num), 4))
        for i, c in enumerate(num[:4]):
            with spark_cols[i]:
                st.markdown(f"**{c}**")
                st.plotly_chart(sparkline(df[c].dropna().head(200)), width='stretch')

    # Charts
    cc = st.columns(2)
    with cc[0]:
        if cat:
            vc = df[cat[0]].value_counts().head(10)
            fig = px.bar(y=vc.index, x=vc.values, orientation='h', title=f"Top {cat[0]}",
                        color=vc.values, color_continuous_scale="Viridis")
            fig.update_traces(marker_line_width=0)
            apply_theme(fig)
            st.plotly_chart(fig, width='stretch')
    with cc[1]:
        if num:
            fig = px.histogram(df, x=num[0], nbins=30, title=f"Distribution of {num[0]}", marginal="box",
                             color_discrete_sequence=["#818cf8"])
            fig.update_traces(marker_line_width=0, opacity=0.8)
            apply_theme(fig)
            st.plotly_chart(fig, width='stretch')

    # Data Dictionary
    with st.expander("📖 Data Dictionary", expanded=False):
        render_data_dictionary(df)

    # Column Profiler
    with st.expander("🔍 Column Profiler", expanded=False):
        render_column_profiler(df, num, cat)

    # Data preview
    with st.expander("📋 Data Preview", expanded=False):
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
            width='stretch',
            column_config=col_config,
        )

    # Export
    with st.expander("📤 Export", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            fmt = st.radio("Format:", ["CSV", "Excel"])
            if fmt == "CSV":
                st.download_button("📥 Download CSV", convert_df_to_csv(df),
                                 f"data_{datetime.now():%Y%m%d}.csv", "text/csv")
            else:
                out = BytesIO()
                with pd.ExcelWriter(out, engine="openpyxl") as w:
                    df.to_excel(w, index=False, sheet_name="Data")
                st.download_button("📥 Download Excel", out.getvalue(),
                                 f"data_{datetime.now():%Y%m%d}.xlsx",
                                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with col2:
            if st.button("🔄 Reset Session", width="stretch"):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()