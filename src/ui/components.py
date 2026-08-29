"""Reusable UI Components — Pro Max Data-Dense Edition"""
from typing import List, Optional, Any, Dict
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.utils.validators import get_column_stats, compute_data_quality_score, generate_data_dictionary
from src.utils.config import get_chart_theme

# Lucide SVG icons (Pro Max: no emoji as icons)
_LUCIDE = {
    "chart": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><path d="M3 3v18h18"/><path d="M7 16l4-4 4 4 4-6"/></svg>',
    "check": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    "alert": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    "info": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="16"/><line x1="12" y1="8" x2="12" y2="12"/></svg>',
}


def _lucide(name: str) -> str:
    return _LUCIDE.get(name, _LUCIDE["info"])


def render_kpi_card(container: st.delta_generator.DeltaGenerator, label: str, value: str, delta: Optional[str] = None) -> None:
    """
    Render a KPI metric card inside a Streamlit container.

    Args:
        container: Streamlit column/container to render into
        label: Short label describing the metric (e.g. "Rows", "Quality")
        value: Formatted value string to display (e.g. "1,234", "95.2%")
        delta: Optional delta/change indicator string (e.g. "+5%")

    Returns:
        None — renders HTML directly into the container
    """
    container.markdown(f'''
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {f'<div class="kpi-delta">{delta}</div>' if delta else ''}
    </div>
    ''', unsafe_allow_html=True)


def render_skeleton_card(height: str = "84px") -> None:
    """Pro Max: skeleton loader for data-dense cards (shimmer)."""
    st.markdown(f'<div class="skeleton skeleton-card" style="height:{height}"></div>', unsafe_allow_html=True)


def render_insight_card(icon: str, title: str, msg: str, type: str = "info") -> None:
    """
    Render insight card — Pro Max a11y: icon + border (not color-only), SVG preferred.
    type: info | success | warning | danger | good
    """
    # Map emoji fallback to Lucide for a11y
    svg = ""
    if icon.strip() in ("📊", "✅", "⚠️", "❌", "ℹ️", "🎯", "📦"):
        map_icon = {"📊": "chart", "✅": "check", "⚠️": "alert", "❌": "alert", "ℹ️": "info"}.get(icon.strip(), "info")
        svg = _lucide(map_icon) + " "
        icon = ""
    title_html = f"{svg}{icon} {title}".strip()
    st.markdown(
        f'<div class="insight-card insight-{type}" role="status">'
        f'<strong>{title_html}</strong><br><span style="overflow-wrap:break-word">{msg}</span></div>',
        unsafe_allow_html=True
    )


def render_data_dictionary(df: pd.DataFrame) -> None:
    """
    Render Data Dictionary — Pro Max: overflow-x-auto wrapper + sticky header.
    """
    st.markdown("### Data Dictionary")
    st.caption("Metadata chi tiết từng cột — cuộn ngang nếu bảng rộng")

    dict_df = generate_data_dictionary(df)
    st.markdown('<div class="dataframe-wrapper">', unsafe_allow_html=True)
    st.dataframe(dict_df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    csv = dict_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download Data Dictionary (CSV)",
        csv,
        "data_dictionary.csv",
        "text/csv"
    )


def render_column_profiler(df: pd.DataFrame, num_cols: List[str], cat_cols: List[str]) -> None:
    """
    Render an interactive column profiler with statistics and visualizations.

    Allows user to select a column and view:
    - Count, missing %, unique count
    - Numeric stats (min, max, mean, median, std, IQR) + histogram for numeric columns
    - Value counts + bar chart for categorical columns

    Args:
        df: Input DataFrame containing the column
        num_cols: List of numeric column names in df
        cat_cols: List of categorical column names in df

    Returns:
        None — renders selectbox + stats + chart into Streamlit
    """
    st.markdown("### Column Profiler")
    st.caption("Phân tích chi tiết từng cột — chọn cột để xem thống kê")

    all_cols = df.columns.tolist()
    selected_col = st.selectbox("Chọn cột để phân tích:", all_cols, key="profiler_col")

    if selected_col:
        stats = get_column_stats(df, selected_col)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Count", f"{stats['count']:,}")
        c2.metric("Missing", f"{stats['missing']:,}")
        c3.metric("Missing %", f"{stats['missing_pct']}%")
        c4.metric("Unique", f"{stats['unique']:,}")

        if selected_col in num_cols:
            st.markdown("#### Numeric Statistics")
            r1c1, r1c2, r1c3 = st.columns(3)
            r1c1.metric("Min", f"{stats['min']:,.4f}")
            r1c2.metric("Max", f"{stats['max']:,.4f}")
            r1c3.metric("Mean", f"{stats['mean']:,.4f}")
            r2c1, r2c2, r2c3 = st.columns(3)
            r2c1.metric("Median", f"{stats['median']:,.4f}")
            r2c2.metric("Std", f"{stats['std']:,.4f}")
            r2c3.metric("IQR", f"{stats['iqr']:,.4f}")

            fig = px.histogram(df, x=selected_col, nbins=50,
                             title=f"Distribution of {selected_col}",
                             marginal="box")
            fig.update_traces(marker_line_width=0, opacity=0.8)
            fig.update_layout(template="plotly_white", **get_chart_theme())
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("#### Categorical Statistics")
            st.markdown('<div class="dataframe-wrapper">', unsafe_allow_html=True)
            st.dataframe(
                df[selected_col].value_counts().head(20).to_frame(),
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
            vc = df[selected_col].value_counts().head(15)
            fig = px.bar(x=vc.index.astype(str), y=vc.values,
                        title=f"Top 15 values in {selected_col}",
                        color=vc.values, color_continuous_scale="Blues")
            fig.update_layout(template="plotly_white", **get_chart_theme())
            st.plotly_chart(fig, use_container_width=True)


def render_data_quality_report(df: pd.DataFrame) -> None:
    """
    Render a comprehensive data quality scorecard with gauge chart.

    Computes and displays:
    - Completeness, Uniqueness, Validity percentages
    - Overall quality score as a gauge indicator
    - List of detected issues (duplicates, outliers, missing values)

    Args:
        df: Input DataFrame to evaluate

    Returns:
        None — renders metrics + gauge + issues into Streamlit
    """
    st.markdown("### Data Quality Report")
    st.caption("Đánh giá tổng thể chất lượng dữ liệu — Pro Max palette")

    quality = compute_data_quality_score(df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Completeness", f"{quality['completeness']}%")
    c2.metric("Uniqueness", f"{quality['uniqueness']}%")
    c3.metric("Validity", f"{quality['validity']}%")
    c4.metric("Overall Score", f"{quality['overall']}%",
             delta="Tốt" if quality['overall'] >= 80 else "Trung bình" if quality['overall'] >= 60 else "Kém")

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=quality['overall'],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Data Quality Score"},
        delta={'reference': 80},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#1E40AF"},
            'steps': [
                {'range': [0, 40], 'color': "#DC2626"},
                {'range': [40, 70], 'color': "#D97706"},
                {'range': [70, 100], 'color': "#059669"}
            ],
            'threshold': {
                'line': {'color': "#1E3A8A", 'width': 3},
                'thickness': 0.75,
                'value': 80
            }
        }
    ))
    fig.update_layout(height=280, **get_chart_theme())
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Vấn đề phát hiện")
    issues: List[str] = []
    if quality['dup_rows'] > 0:
        issues.append(f"{quality['dup_rows']:,} dòng trùng lặp")
    if quality['outlier_count'] > 0:
        issues.append(f"{quality['outlier_count']:,} giá trị ngoại lai")
    if quality['filled_cells'] < quality['total_cells']:
        missing = quality['total_cells'] - quality['filled_cells']
        issues.append(f"{missing:,} giá trị thiếu")

    if not issues:
        issues.append("Dữ liệu sạch, không phát hiện vấn đề!")

    for issue in issues:
        is_ok = "sạch" in issue
        render_insight_card("check" if is_ok else "alert", "", issue, "good" if is_ok else "warning")


def render_quick_start_tutorial() -> None:
    """
    Render an expandable quick start guide for new users.

    Displays step-by-step instructions for uploading data, navigating tabs,
    and using key features of the application.

    Returns:
        None — renders markdown inside an expander
    """
    st.markdown("### 🚀 Quick Start Guide")
    st.caption("Hướng dẫn nhanh để bắt đầu")

    with st.expander("📖 Click để xem hướng dẫn", expanded=True):
        st.markdown("""
        **Chào mừng đến với Data Analyst Pro v3.0!** Phiên bản dựa trên cuốn *Practical Statistics for Data Scientists*.

        ### 1️⃣ Upload dữ liệu
        - Click vào **Browse files** ở sidebar
        - Chọn file CSV hoặc Excel

        ### 2️⃣ Khám phá Overview
        - Xem KPI dashboard: số dòng, cột, chất lượng dữ liệu
        - Sparkline trends cho các cột numeric
        - Biểu đồ tự động: phân phối, top categories

        ### 3️⃣ Statistics (Tính năng mới!)
        - **🔬 Hypothesis Testing** — T-test, ANOVA, Chi-Square, Mann-Whitney
        - **🎲 Bootstrap** — Confidence intervals, resampling
        - **⚗️ A/B Testing** — Power analysis, effect size, sample size
        - **📈 Regression** — Linear regression with diagnostics
        - **🔴 Logistic** — Logistic regression, confusion matrix, ROC
        - **🧮 Naive Bayes** — Gaussian & Categorical NB
        - **🔧 Diagnostics** — VIF, Heteroskedasticity, Durbin-Watson

        ### 4️⃣ Deep Analysis
        - 7 modules phân tích chuyên sâu

        ---

        **💡 Tips:**
        - Click nút 🌓 để chuyển Dark/Light mode
        - Dùng **Export** để tải dữ liệu đã xử lý
        """)


def render_sidebar_stats(df: pd.DataFrame) -> None:
    """
    Render dataset statistics in the sidebar.

    Displays row count, column count, numeric/categorical breakdown,
    and overall data quality score.

    Args:
        df: Input DataFrame whose stats to display

    Returns:
        None — renders metrics inside sidebar expander
    """
    if df is not None:
        st.markdown("---")
        with st.expander("📊 Dataset Stats", expanded=False):
            n: List[str] = df.select_dtypes(include=[np.number]).columns.tolist()
            c: List[str] = df.select_dtypes(include=["object", "category"]).columns.tolist()
            st.metric("Rows", f"{len(df):,}")
            st.metric("Columns", len(df.columns))
            st.metric("Numeric", len(n))
            st.metric("Categorical", len(c))

            quality: Dict[str, Any] = compute_data_quality_score(df)
            st.metric("Quality Score", f"{quality['overall']}%")


def render_confusion_matrix(cm: np.ndarray, labels: List[str]) -> go.Figure:
    """
    Render a confusion matrix as a Plotly heatmap.

    Args:
        cm: 2D numpy array of shape (n_classes, n_classes) with confusion counts
        labels: List of class label strings for x and y axes

    Returns:
        Plotly Figure with heatmap visualization

    Example:
        >>> cm = np.array([[50, 10], [5, 35]])
        >>> fig = render_confusion_matrix(cm, ["Negative", "Positive"])
        >>> st.plotly_chart(fig)
    """
    fig = px.imshow(cm, text_auto=True, x=labels, y=labels,
                    color_continuous_scale="Blues", aspect='auto',
                    title="Confusion Matrix")
    fig.update_layout(height=400)
    return fig


def render_roc_curve(fpr: np.ndarray, tpr: np.ndarray, auc_score: float) -> go.Figure:
    """
    Render ROC curve — Pro Max palette (blue primary #1E40AF, danger dash).
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fpr, y=tpr, mode='lines',
                            name=f'ROC (AUC={auc_score:.3f})',
                            line=dict(color="#1E40AF", width=2)))
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines',
                            name='Random', line=dict(color="#DC2626", dash="dash")))
    fig.update_layout(title="ROC Curve", xaxis_title="False Positive Rate",
                     yaxis_title="True Positive Rate", height=400, **get_chart_theme())
    return fig