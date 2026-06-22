"""Reusable UI Components for Data Analyst Pro"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Optional, Any, Tuple

from utils import get_column_stats, compute_data_quality_score, generate_data_dictionary

def render_kpi_card(label: str, value: str, delta: Optional[str] = None) -> None:
    """Render KPI card"""
    st.markdown(f'''
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
    st.dataframe(dict_df, width='stretch', use_container_width=True)
    
    # Download button
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
        
        # Basic info
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Count", f"{stats['count']:,}")
        c2.metric("Missing", f"{stats['missing']:,}")
        c3.metric("Missing %", f"{stats['missing_pct']}%")
        c4.metric("Unique", f"{stats['unique']:,}")
        
        # Type-specific stats
        if selected_col in num_cols:
            st.markdown("#### 📊 Numeric Statistics")
            c1, c2, c3 = st.columns(3)
            c1.metric("Min", f"{stats['min']:,.4f}")
            c2.metric("Max", f"{stats['max']:,.4f}")
            c1.metric("Mean", f"{stats['mean']:,.4f}")
            c2.metric("Median", f"{stats['median']:,.4f}")
            c3.metric("Std", f"{stats['std']:,.4f}")
            c3.metric("IQR", f"{stats['iqr']:,.4f}")
            
            # Distribution plot
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
            
            # Bar chart
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
    
    # Overall score
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 Completeness", f"{quality['completeness']}%")
    c2.metric("🎯 Uniqueness", f"{quality['uniqueness']}%")
    c3.metric("✅ Validity", f"{quality['validity']}%")
    c4.metric("🏆 Overall Score", f"{quality['overall']}%",
             delta="Tốt ✅" if quality['overall'] >= 80 else "Trung bình ⚠️" if quality['overall'] >= 60 else "Kém ❌")
    
    # Gauge chart
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
    
    # Issues summary
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
        **Chào mừng đến với Data Analyst Pro!** Đây là 4 bước để bắt đầu:
        
        ### 1️⃣ Upload dữ liệu
        - Click vào **Browse files** ở sidebar
        - Chọn file CSV hoặc Excel
        - Hoặc kết nối Database/Google Sheets
        
        ### 2️⃣ Khám phá Overview
        - Xem KPI dashboard: số dòng, cột, chất lượng dữ liệu
        - Sparkline trends cho các cột numeric
        - Biểu đồ tự động: phân phối, top categories
        
        ### 3️⃣ Deep Analysis
        - Tab **🧠 Deep Analysis** có 7 modules chuyên sâu:
          - 📊 Thống kê nâng cao (T-test, ANOVA, Chi-Square)
          - 📈 Chuỗi thời gian (ADF/KPSS, ACF/PACF, Dự báo)
          - 🧬 Phân cụm (K-Means, DBSCAN, Hierarchical)
          - 🎯 PCA & t-SNE (Giảm chiều)
          - 🔧 Feature Engineering
          - 🏆 So sánh mô hình
          - ✅ Chất lượng dữ liệu
        
        ### 4️⃣ AI Chat (Optional)
        - Vào sidebar → **AI Setup**
        - Nhập Gemini API Key (lấy miễn phí tại [aistudio.google.com](https://aistudio.google.com/apikey))
        - Hỏi đáp dữ liệu bằng tiếng Việt!
        
        ---
        
        **💡 Tips:**
        - Click nút 🌓 để chuyển Dark/Light mode
        - Dùng **Export** để tải dữ liệu đã xử lý
        - Xem **Data Dictionary** để hiểu metadata
        """)

def render_sidebar_stats(df: pd.DataFrame) -> None:
    """Render dataset stats trong sidebar"""
    if df is not None:
        st.markdown("---")
        with st.expander("📊 Dataset Stats", expanded=False):
            n = df.select_dtypes(include=[np.number]).columns.tolist()
            c = df.select_dtypes(include=["object", "str", "category"]).columns.tolist()
            st.metric("Rows", f"{len(df):,}")
            st.metric("Columns", len(df.columns))
            st.metric("Numeric", len(n))
            st.metric("Categorical", len(c))
            
            # Quick quality check
            quality = compute_data_quality_score(df)
            st.metric("Quality Score", f"{quality['overall']}%")

def render_file_uploader() -> Optional[st.runtime.uploaded_file_manager.UploadedFile]:
    """
    Render file upload section.

    Returns:
        UploadedFile object nếu có file được upload, None nếu không
    """
    st.markdown("**📂 Upload dữ liệu**")
    uploaded = st.file_uploader("CSV / Excel", type=["csv", "xlsx", "xls"], key="fu")
    return uploaded

def render_db_connection() -> Tuple[Optional[Any], Optional[pd.DataFrame]]:
    """
    Render database connection section.

    Returns:
        Tuple[Optional[Engine], Optional[DataFrame]]: (engine, tables)
        - engine: SQLAlchemy engine nếu connect thành công, None nếu lỗi
        - tables: DataFrame chứa danh sách tables, None nếu lỗi
    """
    st.markdown("**🗄 Database Connection**")
    try:
        from sqlalchemy import create_engine
        db_type = st.selectbox("Type", ["MySQL", "PostgreSQL", "SQL Server", "SQLite"], key="db_type")
        
        if db_type != "SQLite":
            host = st.text_input("Host", "localhost", key="db_host")
            port = st.text_input("Port", "3306" if db_type == "MySQL" else "5432", key="db_port")
        else:
            path = st.text_input("Path", "database.db", key="db_path")
        
        db_name = st.text_input("Database", key="db_name")
        user = st.text_input("User", key="db_user")
        password = st.text_input("Password", type="password", key="db_pass")
        
        if st.button("Connect", key="db_connect", use_container_width=True):
            if db_type == "SQLite":
                conn_str = f"sqlite:///{path}"
            elif db_type == "MySQL":
                conn_str = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
            else:
                conn_str = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
            
            engine = create_engine(conn_str)
            with engine.connect() as conn:
                tables = pd.read_sql("SHOW TABLES" if db_type == "MySQL" else "SELECT table_name FROM information_schema.tables WHERE table_schema='public'", conn)
            st.success(f"✅ {len(tables)} tables found")
            return engine, tables
    except Exception as e:
        st.error(f"❌ Connection error: {str(e)}")
    
    return None, None