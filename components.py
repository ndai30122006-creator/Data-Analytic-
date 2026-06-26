"""Reusable UI Components for Data Analyst Pro v3.0 — Practical Statistics Edition"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Optional, Any, Tuple

from utils import get_column_stats, compute_data_quality_score, generate_data_dictionary

def render_kpi_card(container, label: str, value: str, delta: Optional[str] = None) -> None:
    """Render KPI card inside a container"""
    container.markdown(f'''
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {f'<div class="kpi-delta">{delta}</div>' if delta else ''}
    </div>
    ''', unsafe_allow_html=True)

def render_insight_card(icon: str, title: str, msg: str, type: str = "info") -> None:
    """Render insight card với màu sắc"""
    st.markdown(f'<div class="insight-card insight-{type}"><strong>{icon} {title}</strong><br>{msg}</div>',
                unsafe_allow_html=True)

def render_data_dictionary(df: pd.DataFrame) -> None:
    """Render Data Dictionary table"""
    st.markdown("### 📖 Data Dictionary")
    st.caption("Metadata chi tiết về từng cột trong dataset")
    
    dict_df = generate_data_dictionary(df)
    st.dataframe(dict_df, width="stretch")
    
    csv = dict_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download Data Dictionary (CSV)",
        csv,
        "data_dictionary.csv",
        "text/csv"
    )

def render_column_profiler(df: pd.DataFrame, num_cols: List[str], cat_cols: List[str]) -> None:
    """Render detailed column profiling"""
    st.markdown("### 🔍 Column Profiler")
    st.caption("Phân tích chi tiết từng cột")
    
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
            st.markdown("#### 📊 Numeric Statistics")
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
            st.plotly_chart(fig, width='stretch')
        else:
            st.markdown("#### 📊 Categorical Statistics")
            st.dataframe(
                df[selected_col].value_counts().head(20).to_frame(),
                width='stretch'
            )
            vc = df[selected_col].value_counts().head(15)
            fig = px.bar(x=vc.index.astype(str), y=vc.values,
                        title=f"Top 15 values in {selected_col}",
                        color=vc.values, color_continuous_scale="Viridis")
            st.plotly_chart(fig, width='stretch')

def render_data_quality_report(df: pd.DataFrame) -> None:
    """Render comprehensive data quality report"""
    st.markdown("### ✅ Data Quality Report")
    st.caption("Đánh giá tổng thể chất lượng dữ liệu")
    
    quality = compute_data_quality_score(df)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 Completeness", f"{quality['completeness']}%")
    c2.metric("🎯 Uniqueness", f"{quality['uniqueness']}%")
    c3.metric("✅ Validity", f"{quality['validity']}%")
    c4.metric("🏆 Overall Score", f"{quality['overall']}%",
             delta="Tốt ✅" if quality['overall'] >= 80 else "Trung bình ⚠️" if quality['overall'] >= 60 else "Kém ❌")
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=quality['overall'],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Data Quality Score"},
        delta={'reference': 80},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#818cf8"},
            'steps': [
                {'range': [0, 40], 'color': "#f87171"},
                {'range': [40, 70], 'color': "#fbbf24"},
                {'range': [70, 100], 'color': "#34d399"}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': 80
            }
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, width='stretch')
    
    st.markdown("#### 📌 Vấn đề phát hiện")
    issues = []
    if quality['dup_rows'] > 0:
        issues.append(f"⚠️ {quality['dup_rows']:,} dòng trùng lặp")
    if quality['outlier_count'] > 0:
        issues.append(f"⚠️ {quality['outlier_count']:,} giá trị ngoại lai")
    if quality['filled_cells'] < quality['total_cells']:
        missing = quality['total_cells'] - quality['filled_cells']
        issues.append(f"⚠️ {missing:,} giá trị thiếu")
    
    if not issues:
        issues.append("✅ Dữ liệu sạch, không phát hiện vấn đề!")
    
    for issue in issues:
        render_insight_card("📊", "", issue, "good" if "✅" in issue else "warning")

def render_quick_start_tutorial() -> None:
    """Render quick start tutorial cho new users"""
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
    """Render dataset stats trong sidebar"""
    if df is not None:
        st.markdown("---")
        with st.expander("📊 Dataset Stats", expanded=False):
            n = df.select_dtypes(include=[np.number]).columns.tolist()
            c = df.select_dtypes(include=["object", "category"]).columns.tolist()
            st.metric("Rows", f"{len(df):,}")
            st.metric("Columns", len(df.columns))
            st.metric("Numeric", len(n))
            st.metric("Categorical", len(c))
            
            quality = compute_data_quality_score(df)
            st.metric("Quality Score", f"{quality['overall']}%")

def render_confusion_matrix(cm, labels):
    """Render confusion matrix as heatmap"""
    fig = px.imshow(cm, text_auto=True, x=labels, y=labels,
                    color_continuous_scale="Blues", aspect='auto',
                    title="Confusion Matrix")
    fig.update_layout(height=400)
    return fig

def render_roc_curve(fpr, tpr, auc_score):
    """Render ROC curve"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fpr, y=tpr, mode='lines',
                            name=f'ROC (AUC={auc_score:.3f})',
                            line=dict(color="#818cf8", width=2)))
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines',
                            name='Random', line=dict(color="#f87171", dash="dash")))
    fig.update_layout(title="ROC Curve", xaxis_title="False Positive Rate",
                     yaxis_title="True Positive Rate", height=400)
    return fig