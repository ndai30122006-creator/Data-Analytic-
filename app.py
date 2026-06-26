"""Data Analyst Pro v3.0 — Practical Statistics for Data Scientists Edition"""
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from io import BytesIO
import warnings, time
from datetime import datetime

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split

try:
    from sklearn.ensemble import IsolationForest
    SKLEARN_ENSEMBLE_AVAIL = True
except Exception:
    SKLEARN_ENSEMBLE_AVAIL = False

warnings.filterwarnings("ignore")

# ── Custom Modules ────────────────────────────────────────
from utils import (
    load_and_process_data, validate_dataframe
)
from components import (
    render_kpi_card, render_data_dictionary,
    render_column_profiler, render_data_quality_report,
    render_quick_start_tutorial, render_sidebar_stats
)
from config import (
    MIN_ROWS_VALIDATION, MAX_DISPLAY_ROWS,
    PARAM_GRIDS, CHART_THEME,
    MAIN_TABS, STATISTICS_TABS, ANALYTICS_TABS, PROFILER_TABS,
)
from report_utils import (
    save_session_state, load_session_state, has_saved_session, get_session_info,
    generate_pdf_report
)
from ai_insights import render_ai_insights_tab

try:
    from advanced_analytics import render_deep_analysis_tab
    DEEP_ANALYSIS_AVAIL = True
except Exception as e:
    DEEP_ANALYSIS_AVAIL = False
    st.error(f"❌ Lỗi load advanced_analytics: {e}")

# ── Session State Init ────────────────────────────────────
SESSION_DEFAULTS = [
    ("df", None), ("filename", ""), ("cleaned_df", None),
    ("file_uploader_key", 0),
    ("datasets", {}), ("compare_datasets", []),
    ("ai_report", None),
]
for key, default in SESSION_DEFAULTS:
    if key not in st.session_state: st.session_state[key] = default

st.set_page_config(page_title="Learning Analytics Thống kê", page_icon="🎓", layout="wide",
                   initial_sidebar_state="expanded")

# ═══════════════════════════════════════════════════════════
# MODERN THEME
# ═══════════════════════════════════════════════════════════
THEME_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
:root {
    --bg: #0b0d11; --bg-soft: #111318; --bg-card: #181a20; --bg-hover: #1e2028;
    --fg: #e8eaed; --fg-muted: #7c8290; --accent: #5b6bf7;
    --border: #22242b; --success: #22c55e; --warning: #eab308; --danger: #ef4444;
    --radius: 10px;
}
.stApp { background: var(--bg); color: var(--fg); font-family: 'Inter', -apple-system, sans-serif; font-size: 14px; }
section[data-testid="stSidebar"] { background: var(--bg-soft); border-right: 1px solid var(--border); padding: 0.75rem; }
.main-header { font-size: 1.3rem; font-weight: 700; color: var(--fg); padding: 0.4rem 0; letter-spacing: -0.3px; }
.insight-card, .kpi-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 0.8rem 1rem; margin-bottom: 0.4rem; color: var(--fg); transition: border-color 0.15s, background 0.15s; }
.insight-card:hover, .kpi-card:hover { background: var(--bg-hover); }
.insight-warning { border-left: 2px solid var(--warning); }
.insight-good { border-left: 2px solid var(--success); }
.insight-danger { border-left: 2px solid var(--danger); }
.kpi-label { font-size: 0.6rem; color: var(--fg-muted); text-transform: uppercase; letter-spacing: 0.8px; font-weight: 600; }
.kpi-value { font-size: 1.2rem; font-weight: 700; color: var(--fg); letter-spacing: -0.3px; }
.stTabs [data-baseweb="tab-list"] { gap: 0; background: transparent; border-bottom: 1px solid var(--border); padding: 0; border-radius: 0; }
.stTabs [data-baseweb="tab"] { padding: 6px 12px; color: var(--fg-muted); font-size: 0.78rem; font-weight: 450; border-bottom: 2px solid transparent; margin-bottom: -1px; transition: color 0.15s; }
.stTabs [aria-selected="true"] { color: var(--fg); border-bottom: 2px solid var(--accent); }
.stTabs [data-baseweb="tab"]:hover { color: var(--fg); }
.stButton button { border-radius: 8px; font-weight: 500; font-size: 0.82rem; border: 1px solid var(--border); background: transparent; color: var(--fg); padding: 0.3rem 0.9rem; transition: all 0.15s; }
.stButton button:hover { border-color: #3a3d48; background: var(--bg-hover); }
.stButton button[kind="primary"] { background: var(--accent); color: #fff; border: none; }
.stButton button[kind="primary"]:hover { background: #4a5ae6; box-shadow: 0 0 0 2px rgba(91,107,247,0.2); }
[data-testid="stMetric"] { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 8px 12px; }
[data-testid="stMetric"] label { color: var(--fg-muted) !important; font-size: 0.6rem !important; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; }
[data-testid="stMetric"] [data-testid="stMetricValue"] { color: var(--fg) !important; font-weight: 700; font-size: 1.2rem !important; letter-spacing: -0.3px; }
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"], .stMultiSelect div[data-baseweb="select"] { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; color: var(--fg); font-size: 0.85rem; }
.stSlider > div > div > div { background: var(--border); }
.stSlider > div > div > div > div { background: var(--accent); }
.stDataFrame { border-radius: var(--radius); overflow: hidden; border: 1px solid var(--border); }
.streamlit-expanderHeader { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; font-size: 0.85rem; }
[data-testid="stFileUploader"] section { border: 1px dashed var(--border); border-radius: var(--radius); padding: 1rem; }
[data-testid="stFileUploader"] section:hover { border-color: var(--accent); }
.stAlert { border-radius: 8px; border: 1px solid var(--border); font-size: 0.85rem; }
.stSpinner > div > div { border-color: var(--accent) !important; }
hr { border-color: var(--border); margin: 0.6rem 0; }
h1, h2, h3, h4 { font-weight: 600; letter-spacing: -0.3px; color: var(--fg); }
.stMarkdown { font-size: 0.88rem; }
div[data-baseweb="select"] > div { background: var(--bg-card) !important; }
.stCheckbox label, .stRadio label { font-size: 0.85rem; }

.hero-bg { position: relative; overflow: hidden; border-radius: 16px; padding: 2.5rem 1rem; margin-bottom: 0.5rem; background: linear-gradient(135deg, rgba(91,107,247,0.05), rgba(167,139,250,0.05)); border: 1px solid var(--border); }
.hero { text-align: center; padding: 1.5rem 0; }
.hero h1 { font-size: 2.2rem; font-weight: 800; letter-spacing: -0.5px; background: linear-gradient(135deg, #5b6bf7, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.hero p { font-size: 1rem; color: var(--fg-muted); margin-top: 0.3rem; }
.feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.5rem; margin: 1rem 0; }
.feature-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem; text-align: center; transition: all 0.2s; }
.feature-card:hover { border-color: var(--accent); transform: translateY(-2px); }
.feature-card .icon { font-size: 1.8rem; }
.feature-card .title { font-size: 0.8rem; font-weight: 600; margin-top: 0.3rem; }
.feature-card .desc { font-size: 0.7rem; color: var(--fg-muted); }
.st-emotion-cache-1wivap2 { background: var(--bg-card); }
.hero-bg::before, .hero-bg::after {
    content: ''; position: absolute; border-radius: 50%;
    filter: blur(60px); opacity: 0.3; z-index: 0; pointer-events: none;
}
.hero-bg::before {
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(91,107,247,0.3), transparent);
    top: -80px; left: -80px;
    animation: meshMove1 8s ease-in-out infinite;
}
.hero-bg::after {
    width: 350px; height: 350px;
    background: radial-gradient(circle, rgba(167,139,250,0.25), transparent);
    bottom: -100px; right: -100px;
    animation: meshMove2 10s ease-in-out infinite;
}
@keyframes meshMove1 { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(30px,-20px) scale(1.1); } }
@keyframes meshMove2 { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(-30px,20px) scale(1.05); } }
@keyframes shimmer { 0% { opacity: 0.4; } 50% { opacity: 0.8; } 100% { opacity: 0.4; } }
.skeleton { background: var(--bg-card); border-radius: var(--radius); height: 60px; animation: shimmer 1.5s ease-in-out infinite; margin-bottom: 0.5rem; }
.skeleton-sm { height: 40px; }
.skeleton-lg { height: 200px; }
"""
st.markdown(f"<style>{THEME_CSS}</style>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")

def apply_theme(fig):
    fig.update_layout(**CHART_THEME)
    return fig

def sparkline(series, color='#5b6bf7', height=40):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=series.values, mode='lines',
        line=dict(color=color, width=1.5),
        fill='tozeroy', fillcolor=f'rgba(91,107,247,0.06)',
        showlegend=False, hoverinfo='skip'
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False, showticklabels=False),
        yaxis=dict(visible=False, showticklabels=False),
    )
    return fig

def guess_learning_column(columns, keywords):
    normalized = {c: str(c).lower().replace(" ", "_") for c in columns}
    for col, name in normalized.items():
        if any(keyword in name for keyword in keywords):
            return col
    return None

def render_learning_analytics_tab(df, num_cols, cat_cols):
    st.markdown("### 🎓 Phân tích dữ liệu học tập ngành Thống kê")
    st.caption("Phân tích điểm số, nhóm học tập, tỷ lệ đạt và dấu hiệu cần hỗ trợ sớm.")

    if not num_cols:
        st.warning("Cần ít nhất một cột số, ví dụ: điểm giữa kỳ, điểm cuối kỳ, điểm tổng kết.")
        return

    score_guess = guess_learning_column(
        num_cols,
        ["score", "grade", "mark", "point", "diem", "gpa", "final", "tong_ket", "cuoi_ky"]
    )
    student_guess = guess_learning_column(
        df.columns,
        ["student", "learner", "mssv", "ma_sv", "masv", "sinh_vien", "id"]
    )
    group_guess = guess_learning_column(
        cat_cols,
        ["class", "lop", "course", "mon", "subject", "major", "nganh", "group", "nhom", "gender", "gioi_tinh"]
    )

    score_default = num_cols.index(score_guess) if score_guess in num_cols else 0
    group_default = cat_cols.index(group_guess) + 1 if group_guess in cat_cols else 0

    control_cols = st.columns([2, 2, 1, 1])
    with control_cols[0]:
        score_col = st.selectbox("Cột điểm/kết quả", num_cols, index=score_default, key="la_score_col")
    with control_cols[1]:
        group_options = ["Không phân nhóm"] + cat_cols
        group_col = st.selectbox("Phân tích theo nhóm", group_options, index=group_default, key="la_group_col")
    with control_cols[2]:
        pass_mark = st.number_input("Ngưỡng đạt", value=5.0, step=0.5, key="la_pass_mark")
    with control_cols[3]:
        risk_mark = st.number_input("Ngưỡng rủi ro", value=4.0, step=0.5, key="la_risk_mark")

    analysis_df = df[[score_col] + ([group_col] if group_col != "Không phân nhóm" else [])].copy()
    analysis_df[score_col] = pd.to_numeric(analysis_df[score_col], errors="coerce")
    analysis_df = analysis_df.dropna(subset=[score_col])

    if analysis_df.empty:
        st.warning("Cột điểm đã chọn không có giá trị số hợp lệ.")
        return

    score = analysis_df[score_col]
    pass_rate = (score >= pass_mark).mean() * 100
    risk_rate = (score < risk_mark).mean() * 100

    kpis = st.columns(5)
    render_kpi_card(kpis[0], "Số quan sát", f"{len(analysis_df):,}")
    render_kpi_card(kpis[1], "Điểm TB", f"{score.mean():.2f}")
    render_kpi_card(kpis[2], "Trung vi", f"{score.median():.2f}")
    render_kpi_card(kpis[3], "Tỷ lệ đạt", f"{pass_rate:.1f}%")
    render_kpi_card(kpis[4], "Nhóm rủi ro", f"{risk_rate:.1f}%")

    chart_cols = st.columns(2)
    with chart_cols[0]:
        fig = px.histogram(
            analysis_df, x=score_col, nbins=30, marginal="box",
            title=f"Phân phối {score_col}", color_discrete_sequence=["#34d399"]
        )
        fig.add_vline(x=pass_mark, line_dash="dash", line_color="#22c55e", annotation_text="Đạt")
        fig.add_vline(x=risk_mark, line_dash="dash", line_color="#ef4444", annotation_text="Rủi ro")
        apply_theme(fig)
        st.plotly_chart(fig, width="stretch")

    with chart_cols[1]:
        categories = pd.cut(
            score,
            bins=[-np.inf, risk_mark, pass_mark, np.inf],
            labels=["Cần hỗ trợ", "Cần theo dõi", "Đạt"]
        )
        status_counts = categories.value_counts().reindex(["Cần hỗ trợ", "Cần theo dõi", "Đạt"]).fillna(0)
        fig = px.bar(
            x=status_counts.index.astype(str), y=status_counts.values,
            title="Phân loại kết quả học tập",
            color=status_counts.index.astype(str),
            color_discrete_map={"Cần hỗ trợ": "#ef4444", "Cần theo dõi": "#eab308", "Đạt": "#22c55e"}
        )
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Số lượng")
        apply_theme(fig)
        st.plotly_chart(fig, width="stretch")

    if group_col != "Không phân nhóm":
        st.markdown("#### So sánh theo nhóm")
        summary = analysis_df.groupby(group_col, dropna=False)[score_col].agg(["count", "mean", "median", "std"]).reset_index()
        summary["pass_rate"] = analysis_df.groupby(group_col, dropna=False)[score_col].apply(lambda s: (s >= pass_mark).mean() * 100).values
        summary["risk_rate"] = analysis_df.groupby(group_col, dropna=False)[score_col].apply(lambda s: (s < risk_mark).mean() * 100).values
        summary = summary.sort_values("mean", ascending=False)
        st.dataframe(summary.round(2), width="stretch", hide_index=True)

        fig = px.box(analysis_df, x=group_col, y=score_col, points="outliers", title=f"{score_col} theo {group_col}")
        apply_theme(fig)
        st.plotly_chart(fig, width="stretch")

    st.markdown("#### Gợi ý đọc kết quả")
    if risk_rate >= 25:
        st.warning("Tỷ lệ nhóm rủi ro đang cao. Nên xem lại phân bố điểm, độ khó học phần, và các nhóm/lớp có điểm trung bình thấp.")
    elif pass_rate >= 80:
        st.success("Tỷ lệ đạt khá tốt. Có thể tiếp tục xem nhóm xuất sắc và các yếu tố liên quan đến kết quả cao.")
    else:
        st.info("Kết quả ở mức cần theo dõi. Nên kết hợp thêm cột chuyên cần, bài tập, LMS hoặc điểm thành phần để phân tích sâu hơn.")

    if student_guess:
        st.caption(f"Đã phát hiện cột định danh sinh viên có thể dùng cho phân tích cá nhân hóa: {student_guess}")

# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    col1, col2 = st.columns([1, 3])
    with col1: st.image("https://cdn-icons-png.flaticon.com/512/4727/4727496.png", width=50)
    with col2: st.markdown("### 🎓 Learning Analytics")
    
    st.markdown("---")
    
    # File upload - Multiple datasets
    with st.expander("📂 Data Input", expanded=(st.session_state.df is None)):
        uploaded = st.file_uploader("Upload CSV / Excel", type=["csv", "xlsx", "xls"], 
                                    key=f"fu_{st.session_state.file_uploader_key}",
                                    accept_multiple_files=True)
        
        if uploaded:
            for file in uploaded:
                if file.name not in st.session_state.datasets:
                    with st.spinner(f"Loading {file.name}..."):
                        time.sleep(0.3)
                        loaded_df = load_and_process_data(file)
                        if loaded_df is not None:
                            st.session_state.datasets[file.name] = loaded_df
                            st.success(f"✅ {file.name}")
        
        # Dataset selector
        if st.session_state.datasets:
            st.markdown("#### 📊 Datasets")
            dataset_names = list(st.session_state.datasets.keys())
            
            # Auto-select first dataset if none selected
            current_selection = st.session_state.get("dataset_selector", "-- Chọn --")
            if current_selection == "-- Chọn --" and dataset_names:
                current_selection = dataset_names[0]
            
            selected_dataset = st.selectbox("Chọn dataset:", ["-- Chọn --"] + dataset_names, 
                                           index=(["-- Chọn --"] + dataset_names).index(current_selection) if current_selection in ["-- Chọn --"] + dataset_names else 0,
                                           key="dataset_selector")
            
            if selected_dataset != "-- Chọn --":
                if st.session_state.filename != selected_dataset:
                    st.session_state.df = st.session_state.datasets[selected_dataset]
                    st.session_state.filename = selected_dataset
                    st.session_state.cleaned_df = None
                    st.rerun()
            
            # Delete dataset button
            if selected_dataset != "-- Chọn --":
                if st.button(f"🗑 Xóa {selected_dataset}", key="del_dataset", width="stretch"):
                    del st.session_state.datasets[selected_dataset]
                    if st.session_state.filename == selected_dataset:
                        st.session_state.df = None
                        st.session_state.filename = ""
                    st.rerun()
        
        if st.session_state.df is not None:
            st.caption(f"📄 {st.session_state.filename}")
            if st.button("🗑 Clear All", key="clr", width="stretch"):
                st.session_state.df = None
                st.session_state.filename = ""
                st.session_state.datasets = {}
                st.session_state.cleaned_df = None
                st.session_state.file_uploader_key += 1
                st.rerun()
    
    if st.session_state.df is not None:
        st.markdown("---")
        render_sidebar_stats(st.session_state.df)
        
        # Get current data for PDF and session
        raw_sidebar = st.session_state.df
        num_sidebar = raw_sidebar.select_dtypes(include=[np.number]).columns.tolist()
        cat_sidebar = raw_sidebar.select_dtypes(include=["object", "category"]).columns.tolist()
        
        # Session Management
        with st.expander("💾 Session Management", expanded=False):
            sess_col1, sess_col2 = st.columns(2)
            with sess_col1:
                if st.button("💾 Save Session", width="stretch", key="save_sess"):
                    ok, msg = save_session_state()
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
            with sess_col2:
                if st.button("📂 Load Session", width="stretch", key="load_sess"):
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
        
        # PDF Report
        with st.expander("📄 Export PDF Report", expanded=False):
            st.caption("Generate a beautiful PDF report of your analysis")
            if st.button("📄 Generate PDF Report", width="stretch", key="gen_pdf"):
                with st.spinner("⏳ Generating PDF report..."):
                    try:
                        pdf_bytes = generate_pdf_report(
                            raw_sidebar, num_sidebar, cat_sidebar,
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
                        st.error(f"❌ PDF generation error: {str(e)}")

# ═══════════════════════════════════════════════════════════
# LANDING PAGE
# ═══════════════════════════════════════════════════════════
if st.session_state.df is None:
    st.markdown("""
    <div class="hero-bg">
        <div class="hero">
            <h1>Learning Analytics Thống kê</h1>
            <p>Phân tích dữ liệu học tập, điểm số, nhóm rủi ro và kiểm định thống kê cho sinh viên ngành Thống kê</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card"><div class="icon">📂</div><div class="title">Upload</div><div class="desc">CSV & Excel</div></div>
        <div class="feature-card"><div class="icon">🎓</div><div class="title">Learning</div><div class="desc">Điểm & rủi ro</div></div>
        <div class="feature-card"><div class="icon">🔬</div><div class="title">Statistics</div><div class="desc">Hypothesis Testing</div></div>
        <div class="feature-card"><div class="icon">🎲</div><div class="title">Bootstrap</div><div class="desc">Confidence Intervals</div></div>
        <div class="feature-card"><div class="icon">⚗️</div><div class="title">A/B Testing</div><div class="desc">Power Analysis</div></div>
        <div class="feature-card"><div class="icon">🔴</div><div class="title">Logistic</div><div class="desc">ROC & AUC</div></div>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.info("**📂 Upload** — CSV hoặc Excel từ sidebar")
    c2.success("**🎓 Learning Analytics** — điểm số, tỷ lệ đạt, nhóm rủi ro")
    c3.warning("**🧠 Deep Analysis** — 11 modules phân tích chuyên sâu")
    
    st.caption("Upload dữ liệu từ sidebar để bắt đầu →")
    render_quick_start_tutorial()

else:
    raw = st.session_state.df
    num = raw.select_dtypes(include=[np.number]).columns.tolist()
    cat = raw.select_dtypes(include=["object", "category"]).columns.tolist()
    dat = raw.select_dtypes(include=["datetime64", "datetime64[ns]"]).columns.tolist()
    df = st.session_state.cleaned_df if st.session_state.cleaned_df is not None else raw

    main_tabs = st.tabs(MAIN_TABS)

    # ═══════════════ OVERVIEW ═══════════════
    with main_tabs[0]:
        is_valid, msg = validate_dataframe(df, min_rows=MIN_ROWS_VALIDATION)
        if not is_valid:
            st.error(f"❌ {msg}")
        else:
            # KPI row
            row1 = st.columns(4)
            render_kpi_card(row1[0], "Rows", f"{len(df):,}")
            render_kpi_card(row1[1], "Columns", df.shape[1])
            pct = round((1 - df.isnull().sum().sum() / (len(df) * df.shape[1])) * 100, 1)
            render_kpi_card(row1[2], "Quality", f"{pct}%")
            render_kpi_card(row1[3], "Missing", f"{df.isnull().sum().sum():,}")
            
            # Data Quality Report
            render_data_quality_report(df)
        
        # Sparkline row
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
                    for k in list(st.session_state.keys()): del st.session_state[k]
                    st.rerun()

    # Learning Analytics
    with main_tabs[1]:
        is_valid, msg = validate_dataframe(df, min_rows=MIN_ROWS_VALIDATION)
        if not is_valid:
            st.error(f"❌ {msg}")
        else:
            render_learning_analytics_tab(df, num, cat)

    # ═══════════════ STATISTICS ═══════════════
    with main_tabs[2]:
        is_valid, msg = validate_dataframe(df, min_rows=MIN_ROWS_VALIDATION)
        if not is_valid:
            st.error(f"❌ {msg}")
        else:
            st.markdown("""
            <div class="hero-bg" style="padding: 1.5rem 1rem; margin-bottom: 0.5rem;">
                <div class="hero" style="text-align: center;">
                    <h1 style="font-size: 1.8rem; font-weight: 800; background: linear-gradient(135deg, #5b6bf7, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                    📈 Statistics for Data Scientists
                    </h1>
                    <p style="color: var(--fg-muted);">Hypothesis Testing · Bootstrap · A/B Testing · Logistic · Naive Bayes · Diagnostics</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            stats_tabs = st.tabs(STATISTICS_TABS)
            
            # ── Hypothesis Testing ──
            with stats_tabs[0]:
                if not num and not cat:
                    st.warning("Cần dữ liệu numeric hoặc categorical")
                else:
                    from scipy.stats import ttest_ind, ttest_1samp, ttest_rel, f_oneway, mannwhitneyu, kruskal, chi2_contingency
                    
                    test_type = st.selectbox("Test type:", [
                        "T-test (2 independent samples)",
                        "T-test (1 sample)",
                        "T-test (paired)",
                        "ANOVA",
                        "Mann-Whitney U",
                        "Kruskal-Wallis",
                        "Chi-Square"
                    ], key="ht_type")
                    
                    SIGNIFICANCE_LEVEL = 0.05
                    
                    if "2 independent" in test_type:
                        if len(num) >= 1 and len(cat) >= 1:
                            val_col = st.selectbox("Value column:", num, key="ht_val")
                            grp_col = st.selectbox("Group column:", cat, key="ht_grp")
                            grps = df[grp_col].dropna().unique()[:5]
                            if len(grps) >= 2:
                                g1 = st.selectbox("Group 1:", grps, key="ht_g1")
                                g2 = st.selectbox("Group 2:", [g for g in grps if g != g1], key="ht_g2")
                                if st.button("🔬 Run", key="ht_run"):
                                    s1 = df[df[grp_col] == g1][val_col].dropna()
                                    s2 = df[df[grp_col] == g2][val_col].dropna()
                                    if len(s1) > 1 and len(s2) > 1:
                                        stat, p = ttest_ind(s1, s2, equal_var=False)
                                        pooled_std = np.sqrt((s1.std()**2 + s2.std()**2) / 2)
                                        cohens_d = (s1.mean() - s2.mean()) / pooled_std if pooled_std > 0 else 0
                                        
                                        c1, c2, c3, c4 = st.columns(4)
                                        c1.metric("t-statistic", f"{stat:.4f}")
                                        c2.metric("p-value", f"{p:.6f}")
                                        c3.metric("Cohen's d", f"{abs(cohens_d):.4f}")
                                        c4.metric("Conclusion", "Significant 🎯" if p < SIGNIFICANCE_LEVEL else "Not significant ❌")
                                        
                                        fig = go.Figure()
                                        fig.add_trace(go.Violin(y=s1, name=g1, box_visible=True, meanline_visible=True))
                                        fig.add_trace(go.Violin(y=s2, name=g2, box_visible=True, meanline_visible=True))
                                        fig.update_layout(title=f"{val_col}: {g1} vs {g2} (p={p:.4f}, d={abs(cohens_d):.3f})")
                                        apply_theme(fig)
                                        st.plotly_chart(fig, width='stretch')
                                    else: st.error("Need ≥2 values per group")
                            else: st.warning("Need ≥2 groups")
                        else: st.warning("Need 1 numeric + 1 categorical column")
                    
                    elif "1 sample" in test_type:
                        if num:
                            val_col = st.selectbox("Value column:", num, key="ht_1s")
                            mu0 = st.number_input("Hypothesized mean (μ₀):", value=0.0, key="ht_mu")
                            if st.button("🔬 Run", key="ht_1s_run"):
                                s = df[val_col].dropna()
                                stat, p = ttest_1samp(s, mu0)
                                c1, c2 = st.columns(2)
                                c1.metric("t-statistic", f"{stat:.4f}")
                                c2.metric("p-value", f"{p:.6f}")
                                insight = "Different from μ₀ 🎯" if p < SIGNIFICANCE_LEVEL else "Not different from μ₀ ❌"
                                st.info(f"**Conclusion:** {insight}")
                        else: st.warning("Need numeric column")
                    
                    elif "paired" in test_type:
                        if len(num) >= 2:
                            c1 = st.selectbox("Before:", num, key="ht_pa")
                            c2 = st.selectbox("After:", [c for c in num if c != c1], key="ht_pb")
                            if st.button("🔬 Run", key="ht_p_run"):
                                s = df[[c1, c2]].dropna()
                                stat, p = ttest_rel(s[c1], s[c2])
                                c1, c2 = st.columns(2)
                                c1.metric("t-statistic", f"{stat:.4f}")
                                c2.metric("p-value", f"{p:.6f}")
                                st.info(f"**Conclusion:** {'Significant difference 🎯' if p < SIGNIFICANCE_LEVEL else 'Not significant ❌'}")
                    
                    elif "ANOVA" in test_type:
                        if len(num) >= 1 and len(cat) >= 1:
                            val_col = st.selectbox("Value:", num, key="ht_anova_val")
                            grp_col = st.selectbox("Group:", cat, key="ht_anova_grp")
                            if st.button("🔬 Run", key="ht_anova_run"):
                                grps = df[grp_col].dropna().unique()
                                groups = [df[df[grp_col] == g][val_col].dropna().values for g in grps if len(df[df[grp_col] == g]) > 1]
                                if len(groups) >= 2:
                                    stat, p = f_oneway(*groups)
                                    c1, c2 = st.columns(2)
                                    c1.metric("F-statistic", f"{stat:.4f}")
                                    c2.metric("p-value", f"{p:.6f}")
                                    st.info(f"**Conclusion:** {'Groups differ 🎯' if p < SIGNIFICANCE_LEVEL else 'No difference ❌'}")
                                    fig = px.box(df, x=grp_col, y=val_col, title=f"ANOVA: {val_col} by {grp_col}")
                                    apply_theme(fig)
                                    st.plotly_chart(fig, width='stretch')

                    elif "Mann-Whitney" in test_type:
                        if len(num) >= 1 and len(cat) >= 1:
                            val_col = st.selectbox("Value column:", num, key="mw_val")
                            grp_col = st.selectbox("Group column:", cat, key="mw_grp")
                            grps = df[grp_col].dropna().unique()[:5]
                            if len(grps) >= 2:
                                g1 = st.selectbox("Group 1:", grps, key="mw_g1")
                                g2 = st.selectbox("Group 2:", [g for g in grps if g != g1], key="mw_g2")
                                if st.button("🔬 Run", key="mw_run"):
                                    s1 = df[df[grp_col] == g1][val_col].dropna()
                                    s2 = df[df[grp_col] == g2][val_col].dropna()
                                    if len(s1) > 1 and len(s2) > 1:
                                        stat, p = mannwhitneyu(s1, s2, alternative='two-sided')
                                        c1, c2, c3 = st.columns(3)
                                        c1.metric("U-statistic", f"{stat:.4f}")
                                        c2.metric("p-value", f"{p:.6f}")
                                        c3.metric("Conclusion", "Significant 🎯" if p < SIGNIFICANCE_LEVEL else "Not significant ❌")
                                else: st.warning("Need ≥2 groups")
                        else: st.warning("Need 1 numeric + 1 categorical column")

                    elif "Kruskal-Wallis" in test_type:
                        if len(num) >= 1 and len(cat) >= 1:
                            val_col = st.selectbox("Value:", num, key="kw_val")
                            grp_col = st.selectbox("Group:", cat, key="kw_grp")
                            if st.button("🔬 Run", key="kw_run"):
                                grps = df[grp_col].dropna().unique()
                                groups = [df[df[grp_col] == g][val_col].dropna().values for g in grps if len(df[df[grp_col] == g]) > 1]
                                if len(groups) >= 2:
                                    stat, p = kruskal(*groups)
                                    c1, c2 = st.columns(2)
                                    c1.metric("H-statistic", f"{stat:.4f}")
                                    c2.metric("p-value", f"{p:.6f}")
                                    st.info(f"**Conclusion:** {'Groups differ 🎯' if p < SIGNIFICANCE_LEVEL else 'No difference ❌'}")
                                    fig = px.box(df, x=grp_col, y=val_col, title=f"Kruskal-Wallis: {val_col} by {grp_col}")
                                    apply_theme(fig)
                                    st.plotly_chart(fig, width='stretch')
                    
                    elif "Chi-Square" in test_type:
                        if len(cat) >= 2:
                            c1 = st.selectbox("Column 1:", cat, key="ht_cs1")
                            c2 = st.selectbox("Column 2:", [c for c in cat if c != c1], key="ht_cs2")
                            if st.button("🔬 Run", key="ht_cs_run"):
                                ct = pd.crosstab(df[c1], df[c2])
                                stat, p, dof, expected = chi2_contingency(ct)
                                c1, c2, c3 = st.columns(3)
                                c1.metric("χ²", f"{stat:.4f}")
                                c2.metric("p-value", f"{p:.6f}")
                                c3.metric("DoF", dof)
                                st.info(f"**Conclusion:** {'Variables are related 🎯' if p < SIGNIFICANCE_LEVEL else 'No relationship ❌'}")
                                fig = px.imshow(ct, text_auto=True, title="Contingency Table",
                                               color_continuous_scale="Viridis", aspect='auto')
                                apply_theme(fig)
                                st.plotly_chart(fig, width='stretch')
                        else: st.warning("Need ≥2 categorical columns")
            
            # ── Bootstrap ──
            with stats_tabs[1]:
                if not num:
                    st.warning("Need numeric column")
                else:
                    st.markdown("### 🎲 Bootstrap (Book Ch.2)")
                    col = st.selectbox("Column:", num, key="boot_col")
                    n_iter = st.slider("Iterations:", 100, 5000, 1000, 100, key="boot_iter")
                    conf_level = st.slider("Confidence Level (%):", 80, 99, 95, 1, key="boot_conf")
                    
                    if st.button("🎲 Run Bootstrap", key="boot_run"):
                        data = df[col].dropna().values
                        n = len(data)
                        original = np.mean(data)
                        
                        np.random.seed(42)
                        boot_means = [np.mean(np.random.choice(data, size=n, replace=True)) for _ in range(n_iter)]
                        
                        alpha = (100 - conf_level) / 200
                        ci_lower = np.percentile(boot_means, alpha * 100)
                        ci_upper = np.percentile(boot_means, (1 - alpha) * 100)
                        
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Mean", f"{original:.4f}")
                        c2.metric("Std Error", f"{np.std(boot_means):.4f}")
                        c3.metric(f"{conf_level}% CI", f"[{ci_lower:.4f}, {ci_upper:.4f}]")
                        
                        fig = go.Figure()
                        fig.add_trace(go.Histogram(x=boot_means, nbinsx=50, marker_color="#818cf8", opacity=0.7))
                        fig.add_vline(x=original, line_dash="dash", line_color="#34d399",
                                     annotation_text=f"Mean={original:.3f}")
                        fig.add_vline(x=ci_lower, line_dash="dot", line_color="#f87171",
                                     annotation_text=f"Lower={ci_lower:.3f}")
                        fig.add_vline(x=ci_upper, line_dash="dot", line_color="#f87171",
                                     annotation_text=f"Upper={ci_upper:.3f}")
                        fig.update_layout(title=f"Bootstrap Distribution (n={n_iter})", height=400)
                        apply_theme(fig)
                        st.plotly_chart(fig, width='stretch')
            
            # ── A/B Testing ──
            with stats_tabs[2]:
                st.markdown("### ⚗️ A/B Testing (Book Ch.3)")
                tabs_ab = st.tabs(["🔬 Two-Proportion Test", "📐 Sample Size", "📊 Power Curve"])
                
                with tabs_ab[0]:
                    st.markdown("#### Two-Proportion Z-Test")
                    col1, col2 = st.columns(2)
                    with col1:
                        g1_s = st.number_input("Successes A:", min_value=0, value=50, key="ab_s1")
                        g1_t = st.number_input("Total A:", min_value=1, value=200, key="ab_t1")
                    with col2:
                        g2_s = st.number_input("Successes B:", min_value=0, value=60, key="ab_s2")
                        g2_t = st.number_input("Total B:", min_value=1, value=200, key="ab_t2")
                    
                    if st.button("🔬 Run Test", key="ab_run"):
                        from scipy.stats import norm
                        p1, p2 = g1_s/g1_t, g2_s/g2_t
                        p_pool = (g1_s+g2_s)/(g1_t+g2_t)
                        se = np.sqrt(p_pool*(1-p_pool)*(1/g1_t+1/g2_t))
                        z = (p1-p2)/se if se > 0 else 0
                        p_val = 2*(1-norm.cdf(abs(z)))
                        
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("A Rate", f"{p1:.2%}")
                        c2.metric("B Rate", f"{p2:.2%}")
                        c3.metric("Z-stat", f"{z:.4f}")
                        c4.metric("p-value", f"{p_val:.6f}")
                        
                        fig = go.Figure()
                        fig.add_trace(go.Bar(x=["A", "B"], y=[p1, p2],
                                            text=[f"{p1:.1%}", f"{p2:.1%}"],
                                            textposition='outside',
                                            marker_color=['#818cf8', '#34d399']))
                        fig.update_layout(title="Conversion Rates", height=350)
                        apply_theme(fig)
                        st.plotly_chart(fig, width='stretch')
                        
                        st.info(f"**Conclusion:** {'Significant difference 🎯' if p_val < 0.05 else 'Not significant ❌'}")
                
                with tabs_ab[1]:
                    baseline = st.slider("Baseline (%):", 1, 99, 10, 1, key="ab_base")
                    effect = st.slider("Min effect (%):", 0.5, 30.0, 5.0, 0.5, key="ab_eff")
                    if st.button("📐 Calculate Sample Size", key="ab_ss"):
                        from scipy.stats import norm
                        p1, p2 = baseline/100, (baseline+effect)/100
                        z_a = norm.ppf(0.975)
                        z_b = norm.ppf(0.80)
                        n = ((z_a*np.sqrt(2*(p1+p2)/2*(1-(p1+p2)/2)) + z_b*np.sqrt(p1*(1-p1)+p2*(1-p2)))**2) / ((p2-p1)**2)
                        n = int(np.ceil(n))
                        st.success(f"### 📊 Need {n:,} per group (total: {n*2:,})")
                
                with tabs_ab[2]:
                    from scipy.stats import norm
                    n_per = st.slider("Sample size:", 10, 10000, 500, 10, key="ab_power_n")
                    base_rate = st.slider("Baseline (%):", 1, 99, 10, 1, key="ab_power_base")
                    if st.button("📊 Generate Power Curve", key="ab_power_run"):
                        effects = np.linspace(0.01, 0.20, 50)
                        p1 = base_rate / 100
                        powers = []
                        for eff in effects:
                            p2 = p1 + eff
                            if p2 > 1: continue
                            try:
                                z_b = (np.sqrt(n_per)*abs(p2-p1) - norm.ppf(0.975)*np.sqrt(2*(p1+p2)/2*(1-(p1+p2)/2))) / np.sqrt(p1*(1-p1)+p2*(1-p2))
                                powers.append(norm.cdf(z_b))
                            except: powers.append(0)
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=effects*100, y=powers, mode='lines',
                                                line=dict(color="#818cf8", width=2)))
                        fig.add_hline(y=0.8, line_dash="dash", line_color="#34d399",
                                     annotation_text="Power=80%")
                        fig.update_layout(title=f"Power Curve (n={n_per})", height=350,
                                         xaxis_title="Effect Size (%)", yaxis_title="Power")
                        apply_theme(fig)
                        st.plotly_chart(fig, width='stretch')
            
            # ── Regression ──
            with stats_tabs[3]:
                if len(num) >= 2:
                    from sklearn.linear_model import LinearRegression
                    from sklearn.preprocessing import StandardScaler
                    
                    st.markdown("### 📈 Linear Regression (Book Ch.4)")
                    target = st.selectbox("Target:", num, key="reg_target")
                    features = st.multiselect("Features:", [c for c in num if c != target],
                                            default=[c for c in num if c != target][:min(3, len(num)-1)], key="reg_feats")
                    
                    if len(features) >= 1 and st.button("📈 Run Regression", key="reg_run"):
                        X = df[features].dropna()
                        y = df.loc[X.index, target]
                        
                        if len(X) >= 10:
                            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                            
                            scaler = StandardScaler()
                            X_train_s = scaler.fit_transform(X_train)
                            X_test_s = scaler.transform(X_test)
                            
                            model = LinearRegression()
                            model.fit(X_train_s, y_train)
                            
                            train_r2 = model.score(X_train_s, y_train)
                            test_r2 = model.score(X_test_s, y_test)
                            
                            c1, c2, c3, c4 = st.columns(4)
                            c1.metric("Train R²", f"{train_r2:.4f}")
                            c2.metric("Test R²", f"{test_r2:.4f}")
                            c3.metric("Intercept", f"{model.intercept_:.4f}")
                            c4.metric("Features", f"{len(features)}")
                            
                            coef_df = pd.DataFrame({"Feature": features, "Coefficient": model.coef_})
                            st.dataframe(coef_df, width='stretch')
                            
                            # Scatter: Actual vs Predicted
                            y_pred = model.predict(X_test_s)
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(x=y_test, y=y_pred, mode='markers',
                                                    marker=dict(color="#818cf8", size=6, opacity=0.6)))
                            fig.add_trace(go.Scatter(x=[y_test.min(), y_test.max()], y=[y_test.min(), y_test.max()],
                                                    mode='lines', line=dict(color="#f87171", dash="dash"),
                                                    name="Perfect Fit"))
                            fig.update_layout(title=f"Actual vs Predicted (R²={test_r2:.4f})",
                                             xaxis_title="Actual", yaxis_title="Predicted", height=350)
                            apply_theme(fig)
                            st.plotly_chart(fig, width='stretch')
                        else: st.error("Need ≥10 samples")
                else: st.warning("Need ≥2 numeric columns")
            
            # ── Logistic ──
            with stats_tabs[4]:
                if SKLEARN_ENSEMBLE_AVAIL and len(num) >= 2:
                    from sklearn.linear_model import LogisticRegression
                    from sklearn.preprocessing import StandardScaler
                    from sklearn.metrics import confusion_matrix, roc_curve, auc
                    
                    st.markdown("### 🔴 Logistic Regression (Book Ch.5)")
                    target_col = st.selectbox("Target:", num, key="log_target")
                    threshold = st.slider("Threshold:", float(df[target_col].min()), float(df[target_col].max()),
                                        float(df[target_col].median()), key="log_thresh")
                    y = (df[target_col] > threshold).astype(int)
                    
                    features = st.multiselect("Features:", num, default=num[:min(4, len(num))], key="log_feats2")
                    
                    if len(features) >= 1 and st.button("🔴 Train", key="log_run2"):
                        X = df[features].dropna()
                        y_aligned = y.loc[X.index]
                        
                        if len(np.unique(y_aligned)) >= 2 and len(X) >= 10:
                            X_train, X_test, y_train, y_test = train_test_split(X, y_aligned, test_size=0.3, random_state=42, stratify=y_aligned)
                            
                            scaler = StandardScaler()
                            X_train_s = scaler.fit_transform(X_train)
                            X_test_s = scaler.transform(X_test)
                            
                            model = LogisticRegression(random_state=42, max_iter=500)
                            model.fit(X_train_s, y_train)
                            y_pred = model.predict(X_test_s)
                            y_prob = model.predict_proba(X_test_s)[:, 1]
                            
                            cm = confusion_matrix(y_test, y_pred)
                            tn, fp, fn, tp = cm.ravel()
                            accuracy = (tp+tn)/(tp+tn+fp+fn)
                            precision = tp/(tp+fp) if (tp+fp) > 0 else 0
                            recall = tp/(tp+fn) if (tp+fn) > 0 else 0
                            f1 = 2*precision*recall/(precision+recall) if (precision+recall) > 0 else 0
                            fpr, tpr, _ = roc_curve(y_test, y_prob)
                            auc_score = auc(fpr, tpr)
                            
                            c1, c2, c3, c4, c5 = st.columns(5)
                            c1.metric("Accuracy", f"{accuracy:.2%}")
                            c2.metric("Precision", f"{precision:.2%}")
                            c3.metric("Recall", f"{recall:.2%}")
                            c4.metric("F1", f"{f1:.2%}")
                            c5.metric("AUC", f"{auc_score:.3f}")
                            
                            fig_cm = px.imshow(cm, text_auto=True,
                                              x=["Pred Neg", "Pred Pos"],
                                              y=["Actual Neg", "Actual Pos"],
                                              color_continuous_scale="Blues", aspect='auto')
                            fig_cm.update_layout(height=300, title="Confusion Matrix")
                            apply_theme(fig_cm)
                            st.plotly_chart(fig_cm, width='stretch')
                            
                            fig_roc = go.Figure()
                            fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, mode='lines',
                                                        name=f'ROC (AUC={auc_score:.3f})',
                                                        line=dict(color="#818cf8", width=2),
                                                        fill='tozeroy'))
                            fig_roc.add_trace(go.Scatter(x=[0,1], y=[0,1], mode='lines',
                                                        name='Random', line=dict(color="#f87171", dash="dash")))
                            fig_roc.update_layout(title="ROC Curve", height=300)
                            apply_theme(fig_roc)
                            st.plotly_chart(fig_roc, width='stretch')
                else: st.warning("Need ≥2 numeric columns with sufficient data")
            
            # ── Naive Bayes ──
            with stats_tabs[5]:
                st.markdown("### 🧮 Naive Bayes (Book Ch.5)")
                st.info("Naive Bayes is available in the Deep Analysis tab with full features.")
                if st.button("🔗 Go to Naive Bayes in Deep Analysis", key="goto_nb"):
                    pass
            
            # ── Diagnostics ──
            with stats_tabs[6]:
                st.markdown("### 🔧 Diagnostics (Book Ch.4)")
                st.info("Regression Diagnostics (VIF, Heteroskedasticity, Durbin-Watson) are available in the Deep Analysis tab.")
                if st.button("🔗 Go to Diagnostics in Deep Analysis", key="goto_diag"):
                    pass

    # ═══════════════ COMPARE DATASETS ═══════════════
    with main_tabs[3]:
        st.markdown("### ⚖️ So sánh Datasets")
        st.caption("So sánh cấu trúc và thống kê giữa các datasets")
        
        if len(st.session_state.datasets) < 2:
            st.warning("⚠️ Cần ít nhất 2 datasets để so sánh. Upload thêm datasets từ sidebar.")
        else:
            # Select datasets to compare
            dataset_names = list(st.session_state.datasets.keys())
            col1, col2 = st.columns(2)
            with col1:
                ds1 = st.selectbox("Dataset 1:", dataset_names, key="compare_ds1")
            with col2:
                ds2 = st.selectbox("Dataset 2:", [n for n in dataset_names if n != ds1], key="compare_ds2")
            
            if ds1 and ds2:
                df1 = st.session_state.datasets[ds1]
                df2 = st.session_state.datasets[ds2]
                
                # Basic comparison
                st.markdown("#### 📊 So sánh cơ bản")
                comp_data = {
                    "Metric": ["Rows", "Columns", "Numeric Columns", "Categorical Columns", "Missing Values", "Memory Usage (MB)"],
                    ds1: [
                        len(df1),
                        len(df1.columns),
                        len(df1.select_dtypes(include=[np.number]).columns),
                        len(df1.select_dtypes(include=["object", "category"]).columns),
                        df1.isnull().sum().sum(),
                        round(df1.memory_usage(deep=True).sum() / 1024 / 1024, 2)
                    ],
                    ds2: [
                        len(df2),
                        len(df2.columns),
                        len(df2.select_dtypes(include=[np.number]).columns),
                        len(df2.select_dtypes(include=["object", "category"]).columns),
                        df2.isnull().sum().sum(),
                        round(df2.memory_usage(deep=True).sum() / 1024 / 1024, 2)
                    ]
                }
                comp_df = pd.DataFrame(comp_data)
                st.dataframe(comp_df, width='stretch', hide_index=True)
                
                # Column comparison
                st.markdown("#### 🔗 So sánh columns")
                cols1 = set(df1.columns)
                cols2 = set(df2.columns)
                common_cols = cols1.intersection(cols2)
                only_in_1 = cols1 - cols2
                only_in_2 = cols2 - cols1
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Common Columns", len(common_cols))
                    if common_cols:
                        with st.expander("Xem danh sách"):
                            st.write(", ".join(sorted(common_cols)))
                with col2:
                    st.metric(f"Only in {ds1}", len(only_in_1))
                    if only_in_1:
                        with st.expander("Xem danh sách"):
                            st.write(", ".join(sorted(only_in_1)))
                with col3:
                    st.metric(f"Only in {ds2}", len(only_in_2))
                    if only_in_2:
                        with st.expander("Xem danh sách"):
                            st.write(", ".join(sorted(only_in_2)))
                
                # Statistical comparison for common numeric columns
                if common_cols:
                    st.markdown("#### 📈 So sánh thống kê (các cột numeric chung)")
                    common_num = [c for c in common_cols if c in df1.select_dtypes(include=[np.number]).columns 
                                  and c in df2.select_dtypes(include=[np.number]).columns]
                    
                    if common_num:
                        stat_comp = []
                        for col in common_num[:10]:  # Limit to 10 columns
                            s1 = df1[col].dropna()
                            s2 = df2[col].dropna()
                            if len(s1) > 0 and len(s2) > 0:
                                stat_comp.append({
                                    "Column": col,
                                    f"{ds1} - Mean": round(s1.mean(), 4),
                                    f"{ds2} - Mean": round(s2.mean(), 4),
                                    "Diff": round(s1.mean() - s2.mean(), 4),
                                    f"{ds1} - Std": round(s1.std(), 4),
                                    f"{ds2} - Std": round(s2.std(), 4),
                                })
                        
                        if stat_comp:
                            stat_df = pd.DataFrame(stat_comp)
                            st.dataframe(stat_df, width='stretch', hide_index=True)
                            
                            # Visualization
                            if st.button("📊 Vẽ biểu đồ so sánh", key="plot_compare"):
                                for col in common_num[:5]:
                                    fig = go.Figure()
                                    fig.add_trace(go.Box(y=df1[col].dropna(), name=ds1, marker_color="#818cf8"))
                                    fig.add_trace(go.Box(y=df2[col].dropna(), name=ds2, marker_color="#34d399"))
                                    fig.update_layout(title=f"Compare: {col}", height=300)
                                    apply_theme(fig)
                                    st.plotly_chart(fig, width='stretch')

    # ═══════════════ ANALYTICS ═══════════════
    with main_tabs[4]:
        is_valid, msg = validate_dataframe(df, min_rows=MIN_ROWS_VALIDATION)
        if not is_valid:
            st.error(f"❌ {msg}")
        else:
            an_tabs = st.tabs(ANALYTICS_TABS)
            
            # ── Anomaly Detection ──
            with an_tabs[0]:
                if num:
                    ac = st.multiselect("Columns:", num, default=num[:min(3, len(num))], key="an")
                    ct = st.slider("Contamination:", 0.01, 0.5, 0.05, 0.01)
                    if st.button("🔍 Detect", key="anr") and ac:
                        with st.spinner("..."):
                            X = df[ac].dropna().copy()
                            iso = IsolationForest(contamination=ct, random_state=42)
                            p = iso.fit_predict(X)
                        nc, ac_ = (p == 1).sum(), (p == -1).sum()
                        c1, c2, c3 = st.columns(3)
                        c1.metric("✅ Normal", nc); c2.metric("🚨 Anomalies", ac_)
                        c3.metric("Ratio", f"{ac_/(nc+ac_)*100:.1f}%")
                        if len(ac) >= 2:
                            X["A"] = p
                            fig = px.scatter(X, x=ac[0], y=ac[1], color=X["A"].map({1:"Normal", -1:"Anomaly"}),
                                           title="Anomalies")
                            apply_theme(fig); st.plotly_chart(fig, width='stretch')
                else: st.warning("Need numeric columns")
            
            # ── Profiling ──
            with an_tabs[1]:
                ni = df.select_dtypes(include=[np.number])
                ci = df.select_dtypes(include=["object", "category"])
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Rows", df.shape[0]); c2.metric("Columns", df.shape[1])
                c3.metric("Numeric", len(ni.columns)); c4.metric("Categorical", len(ci.columns))
                
                pt = st.tabs(PROFILER_TABS)
                with pt[0]:
                    for c_ in df.columns:
                        with st.expander(f"**{c_}** ({df[c_].dtype})"):
                            a, b, c = st.columns(3)
                            a.metric("Count", len(df[c_])); b.metric("Missing", df[c_].isnull().sum())
                            c.metric("Unique", df[c_].nunique())
                            if c_ in num:
                                d, e, f = st.columns(3)
                                d.metric("Min", f"{df[c_].min():,.4f}")
                                e.metric("Mean", f"{df[c_].mean():,.4f}")
                                f.metric("Max", f"{df[c_].max():,.4f}")
                                fig = px.histogram(df, x=c_, nbins=30, title="Distribution")
                                apply_theme(fig); st.plotly_chart(fig, width='stretch')
                            else:
                                vc = df[c_].value_counts().head(15)
                                fig = px.bar(x=vc.index.astype(str), y=vc.values, title="Top 15",
                                           color=vc.values, color_continuous_scale="Viridis")
                                apply_theme(fig); st.plotly_chart(fig, width='stretch')
                with pt[1]:
                    if num:
                        sc = st.selectbox("Column:", num, key="pd_")
                        fig = px.histogram(df, x=sc, nbins=50, marginal="box", title=f"Distribution of {sc}")
                        apply_theme(fig); st.plotly_chart(fig, width='stretch')
                        fig2 = px.box(df, y=sc, title=f"Box Plot — {sc}")
                        apply_theme(fig2); st.plotly_chart(fig2, width='stretch')
                with pt[2]:
                    if len(num) >= 2:
                        corr = df[num].corr()
                        fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r",
                                       zmin=-1, zmax=1, title="Correlation Matrix", aspect='auto')
                        fig.update_layout(height=600)
                        apply_theme(fig); st.plotly_chart(fig, width='stretch')
            
            # ── Data Cleaning ──
            with an_tabs[2]:
                st.markdown("### 🧹 Data Cleaning & Transformation")
                
                if "cleaned_df" not in st.session_state or st.session_state.cleaned_df is None:
                    st.session_state.cleaned_df = df.copy()
                
                work_df = st.session_state.cleaned_df
                
                # Missing Values
                st.markdown("#### 🔲 Missing Values")
                missing_counts = work_df.isnull().sum()
                missing_cols = missing_counts[missing_counts > 0]
                
                if len(missing_cols) > 0:
                    st.write(f"**{len(missing_cols)} columns with missing values:**")
                    missing_df = pd.DataFrame({
                        "Column": missing_cols.index,
                        "Missing": missing_cols.values,
                        "Missing %": [f"{v/len(work_df)*100:.1f}%" for v in missing_cols.values]
                    })
                    st.dataframe(missing_df, width='stretch', hide_index=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        mv_action = st.selectbox("Action:", 
                            ["Drop rows with any NaN", "Drop rows with all NaN", 
                             "Fill with Mean", "Fill with Median", "Fill with Mode", "Fill with 0",
                             "Forward Fill", "Backward Fill"], key="mv_action")
                    with col2:
                        mv_cols = st.multiselect("Apply to:", missing_cols.index.tolist(),
                                                default=missing_cols.index.tolist(), key="mv_cols")
                    
                    if st.button("✨ Apply", key="mv_apply"):
                        try:
                            before = len(work_df)
                            if mv_action == "Drop rows with any NaN":
                                work_df = work_df.dropna(subset=mv_cols)
                            elif mv_action == "Drop rows with all NaN":
                                work_df = work_df.dropna(how='all', subset=mv_cols)
                            elif mv_action == "Fill with Mean":
                                for c in mv_cols:
                                    if pd.api.types.is_numeric_dtype(work_df[c].dtype):
                                        work_df[c] = work_df[c].fillna(work_df[c].mean())
                            elif mv_action == "Fill with Median":
                                for c in mv_cols:
                                    if pd.api.types.is_numeric_dtype(work_df[c].dtype):
                                        work_df[c] = work_df[c].fillna(work_df[c].median())
                            elif mv_action == "Fill with Mode":
                                for c in mv_cols:
                                    mode_val = work_df[c].mode()
                                    if len(mode_val) > 0:
                                        work_df[c] = work_df[c].fillna(mode_val[0])
                            elif mv_action == "Fill with 0":
                                for c in mv_cols:
                                    work_df[c] = work_df[c].fillna(0)
                            elif mv_action == "Forward Fill":
                                for c in mv_cols:
                                    work_df[c] = work_df[c].ffill()
                            elif mv_action == "Backward Fill":
                                for c in mv_cols:
                                    work_df[c] = work_df[c].bfill()
                            
                            st.session_state.cleaned_df = work_df
                            st.success(f"✅ Applied: {mv_action}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    st.success("✅ No missing values")
                
                st.markdown("---")
                
                # Duplicates
                st.markdown("#### 🔁 Duplicate Rows")
                dup_count = work_df.duplicated().sum()
                if dup_count > 0:
                    st.warning(f"⚠️ **{dup_count}** duplicate rows ({dup_count/len(work_df)*100:.1f}%)")
                    if st.button("🗑 Remove Duplicates", key="dup_remove"):
                        work_df = work_df.drop_duplicates()
                        st.session_state.cleaned_df = work_df
                        st.success(f"✅ Removed {dup_count} duplicate rows")
                        st.rerun()
                else:
                    st.success("✅ No duplicate rows")
                
                st.markdown("---")
                
                # Outliers
                st.markdown("#### 📊 Outliers")
                num_cols_clean = work_df.select_dtypes(include=[np.number]).columns.tolist()
                if num_cols_clean:
                    outlier_col = st.selectbox("Column:", num_cols_clean, key="outlier_col")
                    q1, q3 = work_df[outlier_col].quantile(0.25), work_df[outlier_col].quantile(0.75)
                    iqr = q3 - q1
                    lower, upper = q1 - 1.5*iqr, q3 + 1.5*iqr
                    outliers = work_df[(work_df[outlier_col] < lower) | (work_df[outlier_col] > upper)]
                    st.write(f"**{len(outliers)} outliers detected**")
                    
                    if len(outliers) > 0:
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✂️ Remove", key="out_remove"):
                                work_df = work_df.drop(outliers.index)
                                st.session_state.cleaned_df = work_df
                                st.success(f"✅ Removed {len(outliers)} outliers")
                                st.rerun()
                        with col2:
                            if st.button("🔒 Cap Outliers", key="out_cap"):
                                work_df[outlier_col] = work_df[outlier_col].clip(lower, upper)
                                st.session_state.cleaned_df = work_df
                                st.success("✅ Capped outliers")
                                st.rerun()
                
                st.markdown("---")
                
                # Encoding
                st.markdown("#### 🔤 Encoding")
                cat_cols_clean = work_df.select_dtypes(include=["object", "category"]).columns.tolist()
                if cat_cols_clean:
                    enc_cols = st.multiselect("Categorical columns:", cat_cols_clean, key="enc_cols")
                    enc_method = st.selectbox("Method:", ["One-Hot", "Label", "Frequency"], key="enc_method")
                    if st.button("🔄 Apply") and enc_cols:
                        try:
                            if enc_method == "One-Hot":
                                work_df = pd.get_dummies(work_df, columns=enc_cols)
                            elif enc_method == "Label":
                                for c in enc_cols:
                                    work_df[c] = work_df[c].astype('category').cat.codes
                            elif enc_method == "Frequency":
                                for c in enc_cols:
                                    freq = work_df[c].value_counts(normalize=True)
                                    work_df[c] = work_df[c].map(freq)
                            st.session_state.cleaned_df = work_df
                            st.success("✅ Applied encoding")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ {e}")
                
                st.markdown("---")
                
                # Summary
                col1, col2, col3 = st.columns(3)
                with col1: st.metric("Original Rows", len(df))
                with col2: st.metric("Current Rows", len(work_df))
                with col3: st.metric("Current Cols", len(work_df.columns))
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Reset to Original", width="stretch"):
                        st.session_state.cleaned_df = df.copy()
                        st.success("✅ Reset")
                        st.rerun()
                with col2:
                    if st.button("💾 Save Cleaned Data", width="stretch"):
                        st.session_state.df = work_df.copy()
                        st.success("✅ Saved")
                        st.rerun()
            
            # ── AutoML ──
            with an_tabs[3]:
                try:
                    import xgboost as xgb
                    XGB_AVAIL = True
                except: XGB_AVAIL = False
                try:
                    from sklearn.pipeline import Pipeline
                    from sklearn.preprocessing import StandardScaler, PolynomialFeatures
                    SKLEARN_AVAIL = True
                except: SKLEARN_AVAIL = False
                
                if XGB_AVAIL and SKLEARN_AVAIL:
                    from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
                    from sklearn.linear_model import Ridge, Lasso
                    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
                    
                    if len(num) >= 2:
                        st.markdown("### 🚀 AutoML — Automated Model Selection")
                        st.caption("Hyperparameter Tuning với 5 thuật toán")
                        
                        tg = st.selectbox("Target:", num, key="atg")
                        feats = [c for c in num if c != tg]
                        cols = st.multiselect("Features:", feats, default=feats[:min(4, len(feats))], key="atg_feats")
                        
                        if len(cols) >= 1:
                            col1, col2 = st.columns(2)
                            with col1:
                                tune_method = st.selectbox("Tuning:", ["GridSearch", "RandomizedSearch", "None"], key="atg_tune")
                                test_size = st.slider("Test size:", 0.1, 0.4, 0.2, 0.05, key="atg_ts")
                            with col2:
                                cv_folds = st.slider("CV folds:", 2, 10, 3, key="atg_cv")
                                auto_models = st.multiselect("Models:", 
                                    ["Random Forest", "XGBoost", "Gradient Boosting", "Ridge", "Lasso"],
                                    default=["Random Forest", "XGBoost"], key="atg_models")
                            
                            auto_scale = st.checkbox("📐 Auto Scaling", value=True, key="atg_scale")
                            
                            if st.button("🚀 Run AutoML", key="atg_run") and auto_models:
                                with st.spinner("⏳ AutoML running..."):
                                    X = df[cols].dropna()
                                    y = df.loc[X.index, tg]
                                    
                                    if len(X) >= 10:
                                        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
                                        
                                        model_constructors = {
                                            "Random Forest": RandomForestRegressor(random_state=42),
                                            "XGBoost": xgb.XGBRegressor(random_state=42, verbosity=0),
                                            "Gradient Boosting": GradientBoostingRegressor(random_state=42),
                                            "Ridge": Ridge(),
                                            "Lasso": Lasso(max_iter=5000)
                                        }
                                        
                                        results = []
                                        best_overall = {"name": "", "score": -999}
                                        
                                        progress_bar = st.progress(0)
                                        for i, model_name in enumerate(auto_models):
                                            base_model = model_constructors[model_name]
                                            param_grid = PARAM_GRIDS[model_name]
                                            
                                            steps = []
                                            if auto_scale:
                                                steps.append(("scaler", StandardScaler()))
                                            steps.append(("model", base_model))
                                            pipeline = Pipeline(steps)
                                            
                                            if tune_method == "GridSearch":
                                                searcher = GridSearchCV(pipeline, param_grid, cv=cv_folds, scoring='r2', n_jobs=-1)
                                            elif tune_method == "RandomizedSearch":
                                                searcher = RandomizedSearchCV(pipeline, param_grid, n_iter=10, cv=cv_folds, scoring='r2', n_jobs=-1, random_state=42)
                                            else:
                                                searcher = None
                                            
                                            if searcher:
                                                searcher.fit(X_train, y_train)
                                                best_model = searcher.best_estimator_
                                                best_params = searcher.best_params_
                                                cv_score = searcher.best_score_
                                            else:
                                                pipeline.fit(X_train, y_train)
                                                best_model = pipeline
                                                best_params = "Default"
                                                cv_score = 0
                                            
                                            train_score = best_model.score(X_train, y_train)
                                            test_score = best_model.score(X_test, y_test)
                                            
                                            results.append({
                                                "Model": model_name,
                                                "Train R²": round(train_score, 4),
                                                "Test R²": round(test_score, 4),
                                                "CV R²": round(cv_score, 4)
                                            })
                                            
                                            if test_score > best_overall["score"]:
                                                best_overall = {"name": model_name, "score": test_score, "params": best_params}
                                            
                                            progress_bar.progress((i + 1) / len(auto_models))
                                        
                                        result_df = pd.DataFrame(results).sort_values("Test R²", ascending=False)
                                        st.dataframe(result_df, width='stretch', hide_index=True)
                                        
                                        st.success(f"🏆 **Best: {best_overall['name']}** — Test R² = {best_overall['score']:.4f}")
                                        
                                        fig = go.Figure()
                                        fig.add_trace(go.Bar(name="Train", x=result_df["Model"], y=result_df["Train R²"], marker_color="#818cf8"))
                                        fig.add_trace(go.Bar(name="Test", x=result_df["Model"], y=result_df["Test R²"], marker_color="#34d399"))
                                        fig.update_layout(title="AutoML Results", barmode='group', height=350)
                                        apply_theme(fig)
                                        st.plotly_chart(fig, width='stretch')
                                    else: st.error("Need ≥10 samples")
                        else: st.warning("Select ≥1 feature")
                    else: st.warning("Need ≥2 numeric columns")
                else:
                    st.info("Install: pip install xgboost scikit-learn")

    # ═══════════════ AI INSIGHTS ═══════════════
    with main_tabs[5]:
        is_valid, msg = validate_dataframe(df, min_rows=MIN_ROWS_VALIDATION)
        if not is_valid:
            st.error(f"❌ {msg}")
        else:
            render_ai_insights_tab(df, num, cat)

    # ═══════════════ DEEP ANALYSIS ═══════════════
    with main_tabs[6]:
        is_valid, msg = validate_dataframe(df, min_rows=MIN_ROWS_VALIDATION)
        if not is_valid:
            st.error(f"❌ {msg}")
        elif DEEP_ANALYSIS_AVAIL:
            render_deep_analysis_tab(df, num, cat, dat)
        else:
            st.error("Advanced Analytics module unavailable. Check advanced_analytics.py")
            with st.expander("🔧 Install dependencies", expanded=True):
                st.code("pip install scipy scikit-learn statsmodels matplotlib seaborn")
                if st.button("🔄 Refresh", key="da_refresh"):
                    st.rerun()

st.caption("📊 Data Analyst Pro v3.0 — Practical Statistics for Data Scientists, 2nd Ed")