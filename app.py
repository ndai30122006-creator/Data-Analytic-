"""Data Analyst Pro v2.0 - Enterprise AI Data Platform"""
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from io import BytesIO
import warnings, json, os, time
from datetime import datetime

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
    load_and_process_data, get_column_stats, compute_data_quality_score,
    generate_data_dictionary, validate_dataframe, safe_execute
)
from components import (
    render_kpi_card, render_insight_card, render_data_dictionary,
    render_column_profiler, render_data_quality_report,
    render_quick_start_tutorial, render_sidebar_stats
)
from config import (
    MIN_ROWS_VALIDATION, TOP_N_VALUES, TOP_N_CATEGORIES, TOP_N_DISTRIBUTION,
    SPARKLINE_SAMPLE_SIZE, DATA_PREVIEW_ROWS, MAX_DISPLAY_ROWS,
    DEFAULT_TEST_SIZE, DEFAULT_CV_FOLDS, DEFAULT_CONTAMINATION,
    DEFAULT_FORECAST_DAYS, RANDOM_STATE, AUTOML_DEFAULT_MODELS,
    AUTOML_DEFAULT_FEATURES, AUTOML_POLYNOMIAL_DEGREE, AUTOML_N_ITER_RANDOMIZED,
    PARAM_GRIDS, CHART_THEME, SPARKLINE_HEIGHT, SPARKLINE_COLOR, KPI_COLUMNS,
    DEFAULT_DB_HOST, DEFAULT_DB_PORT_MYSQL, DEFAULT_DB_PORT_POSTGRES, DEFAULT_DB_PATH,
    GEMINI_MODEL, AI_CHAT_INPUT_PLACEHOLDER, QUICK_PROMPTS,
    PROPHET_YEARLY_SEASONALITY, PROPHET_WEEKLY_SEASONALITY, PROPHET_DAILY_SEASONALITY,
    ANOMALY_CONTAMINATION_RANGE, ANOMALY_CONTAMINATION_DEFAULT, ANOMALY_CONTAMINATION_STEP,
    WHATIF_CHANGE_RANGE, WHATIF_CHANGE_DEFAULT, WHATIF_CHANGE_STEP,
    PDF_TITLE_DEFAULT, PDF_MAX_COLUMNS, PDF_TOP_CORRELATIONS,
    SESSION_KEYS, MAIN_TABS, AI_TABS, ANALYTICS_TABS, PROFILER_TABS,
    SUPPORTED_FILE_TYPES, FILE_UPLOADER_LABEL, DB_TYPES,
    THEME_DARK, THEME_LIGHT, EXPORT_FORMAT_CSV, EXPORT_FORMAT_EXCEL,
    TUNING_METHODS, AUTOML_MODELS, QUALITY_THRESHOLD_GOOD, QUALITY_THRESHOLD_WARNING,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER, COLOR_ACCENT, COLOR_PRIMARY, COLOR_SECONDARY
)

# ── Optional Imports ────────────────────────────────────────
try:
    from prophet import Prophet
    PROPHET_AVAIL = True
except Exception: PROPHET_AVAIL = False

try:
    import xgboost as xgb
    XGB_AVAIL = True
except Exception: XGB_AVAIL = False

try:
    from sqlalchemy import create_engine
    SQL_AVAIL = True
except Exception: SQL_AVAIL = False

try:
    import google.generativeai as genai
    GENAI_AVAIL = True
except Exception: GENAI_AVAIL = False

try:
    from fpdf import FPDF
    PDF_AVAIL = True
except Exception: PDF_AVAIL = False

try:
    import gspread
    GSHEET_AVAIL = True
except Exception: GSHEET_AVAIL = False

try:
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler, PolynomialFeatures
    SKLEARN_AVAIL = True
except Exception:
    SKLEARN_AVAIL = False

try:
    from solar_system import render_solar_system_tab
    SOLAR_SYSTEM_AVAIL = True
except Exception:
    SOLAR_SYSTEM_AVAIL = False

try:
    from advanced_analytics import render_deep_analysis_tab
    DEEP_ANALYSIS_AVAIL = True
except Exception:
    DEEP_ANALYSIS_AVAIL = False

# ── Session State Init ────────────────────────────────────
for key, default in [
    ("df", None), ("filename", ""), ("cleaned_df", None),
    ("genai_chat", []), ("db_config", {}), ("theme", "dark"),
    ("genai_key", os.getenv("GEMINI_API_KEY", "")),
]:
    if key not in st.session_state: st.session_state[key] = default

st.set_page_config(page_title="Data Analyst Pro", page_icon="📊", layout="wide",
                   initial_sidebar_state="expanded")

# ═══════════════════════════════════════════════════════════
# MODERN THEME — Linear/Vercel/Stripe inspired
# ═══════════════════════════════════════════════════════════
THEME_DARK = """
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
.stTextInput input:focus, .stTextArea textarea:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(91,107,247,0.1); }
.stSlider > div > div > div { background: var(--border); }
.stSlider > div > div > div > div { background: var(--accent); }
.stDataFrame { border-radius: var(--radius); overflow: hidden; border: 1px solid var(--border); }
.streamlit-expanderHeader { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; font-size: 0.85rem; }
[data-testid="stFileUploader"] section { border: 1px dashed var(--border); border-radius: var(--radius); padding: 1rem; }
[data-testid="stFileUploader"] section:hover { border-color: var(--accent); }
.stAlert { border-radius: 8px; border: 1px solid var(--border); font-size: 0.85rem; }
.stSpinner > div > div { border-color: var(--accent) !important; }
hr { border-color: var(--border); margin: 0.6rem 0; }
.stChatMessage { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 0.75rem; }
h1, h2, h3, h4 { font-weight: 600; letter-spacing: -0.3px; color: var(--fg); }
.stMarkdown { font-size: 0.88rem; }
div[data-baseweb="select"] > div { background: var(--bg-card) !important; }
.stCheckbox label, .stRadio label { font-size: 0.85rem; }
.st-bb { background: var(--bg-card); }

/* ── WOW EFFECTS ──────────────────────────── */

/* Animated gradient mesh background */
@keyframes meshMove {
    0% { transform: translate(0, 0) scale(1); }
    25% { transform: translate(30px, -20px) scale(1.1); }
    50% { transform: translate(-20px, 30px) scale(0.95); }
    75% { transform: translate(10px, -30px) scale(1.05); }
    100% { transform: translate(0, 0) scale(1); }
}
@keyframes meshMove2 {
    0% { transform: translate(0, 0) scale(1); }
    25% { transform: translate(-30px, 20px) scale(1.05); }
    50% { transform: translate(20px, -30px) scale(0.9); }
    75% { transform: translate(-10px, 30px) scale(1.1); }
    100% { transform: translate(0, 0) scale(1); }
}
.hero-bg {
    position: relative;
    overflow: hidden;
    border-radius: 16px;
    padding: 2.5rem 1rem;
    margin-bottom: 0.5rem;
    background: linear-gradient(135deg, rgba(91,107,247,0.05), rgba(167,139,250,0.05));
    border: 1px solid var(--border);
}
.hero-bg::before, .hero-bg::after {
    content: '';
    position: absolute;
    border-radius: 50%;
    filter: blur(60px);
    opacity: 0.3;
    z-index: 0;
    pointer-events: none;
}
.hero-bg::before {
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(91,107,247,0.3), transparent);
    top: -80px; left: -80px;
    animation: meshMove 8s ease-in-out infinite;
}
.hero-bg::after {
    width: 350px; height: 350px;
    background: radial-gradient(circle, rgba(167,139,250,0.25), transparent);
    bottom: -100px; right: -100px;
    animation: meshMove2 10s ease-in-out infinite;
}

/* Floating particles */
@keyframes float1 { 0%, 100% { transform: translateY(0) translateX(0); opacity: 0.3; } 50% { transform: translateY(-40px) translateX(20px); opacity: 0.7; } }
@keyframes float2 { 0%, 100% { transform: translateY(0) translateX(0); opacity: 0.2; } 50% { transform: translateY(30px) translateX(-30px); opacity: 0.6; } }
@keyframes float3 { 0%, 100% { transform: translateY(0) scale(1); opacity: 0.15; } 50% { transform: translateY(-50px) scale(1.5); opacity: 0.4; } }
.particle { position: absolute; border-radius: 50%; pointer-events: none; z-index: 0; }
.particle-1 { width: 8px; height: 8px; background: #5b6bf7; top: 20%; left: 10%; animation: float1 6s ease-in-out infinite; }
.particle-2 { width: 5px; height: 5px; background: #a78bfa; top: 60%; left: 85%; animation: float2 8s ease-in-out infinite; }
.particle-3 { width: 12px; height: 12px; background: rgba(91,107,247,0.4); top: 40%; left: 50%; animation: float3 7s ease-in-out infinite; }
.particle-4 { width: 6px; height: 6px; background: #34d399; top: 70%; left: 20%; animation: float1 9s ease-in-out infinite; }
.particle-5 { width: 4px; height: 4px; background: #fbbf24; top: 15%; left: 70%; animation: float2 5s ease-in-out infinite; }

/* Glow border cards */
@keyframes glowBorder {
    0%, 100% { border-color: var(--border); box-shadow: 0 0 0px rgba(91,107,247,0); }
    50% { border-color: rgba(91,107,247,0.3); box-shadow: 0 0 20px rgba(91,107,247,0.1); }
}
.feature-card.glow { animation: glowBorder 3s ease-in-out infinite; }

/* Typewriter effect */
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
@keyframes typewriter { from { width: 0; } to { width: 100%; } }
.typewriter {
    overflow: hidden;
    white-space: nowrap;
    animation: typewriter 2.5s steps(40) 0.5s forwards;
    width: 0;
    display: inline-block;
}
.typewriter-cursor::after {
    content: '|';
    animation: blink 0.8s step-end infinite;
    color: var(--accent);
    margin-left: 2px;
}

/* Glow pulse for hero title */
@keyframes gradientPulse {
    0%, 100% { background-size: 100% 100%; }
    50% { background-size: 150% 150%; }
}
.hero h1 {
    animation: gradientPulse 4s ease-in-out infinite;
    position: relative;
    z-index: 1;
}
.hero p { position: relative; z-index: 1; }

/* Feature cards with glass + glow */
.feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.5rem; margin: 1rem 0; position: relative; z-index: 1; }
.feature-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(10px);
}
.feature-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    border-radius: var(--radius);
    background: linear-gradient(135deg, rgba(91,107,247,0.1), transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
}
.feature-card:hover::before { opacity: 1; }
.feature-card:hover {
    border-color: var(--accent);
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 8px 30px rgba(91,107,247,0.15);
}
.feature-card .icon { font-size: 2rem; position: relative; z-index: 1; }
.feature-card .title { font-size: 0.8rem; font-weight: 600; margin-top: 0.3rem; position: relative; z-index: 1; }
.feature-card .desc { font-size: 0.7rem; color: var(--fg-muted); position: relative; z-index: 1; }

/* Skeleton loader */
@keyframes shimmer { 0% { opacity: 0.4; } 50% { opacity: 0.8; } 100% { opacity: 0.4; } }
.skeleton { background: var(--bg-card); border-radius: var(--radius); height: 60px; animation: shimmer 1.5s ease-in-out infinite; margin-bottom: 0.5rem; }
.skeleton-sm { height: 40px; }
.skeleton-lg { height: 200px; }

/* Quick prompts */
.quick-prompt { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 0.4rem 0.8rem; font-size: 0.78rem; color: var(--fg-muted); cursor: pointer; transition: all 0.15s; display: inline-block; margin: 0.15rem; }
.quick-prompt:hover { border-color: var(--accent); color: var(--fg); }
"""

THEME_LIGHT = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
:root {
    --bg: #fafbfc; --bg-soft: #f0f2f5; --bg-card: #ffffff; --bg-hover: #f6f7f9;
    --fg: #1a1d23; --fg-muted: #6b7280; --accent: #5b6bf7;
    --border: #e5e7eb; --success: #22c55e; --warning: #eab308; --danger: #ef4444;
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
.stButton button:hover { border-color: #c4c8cf; background: var(--bg-hover); }
.stButton button[kind="primary"] { background: var(--accent); color: #fff; border: none; }
.stButton button[kind="primary"]:hover { background: #4a5ae6; box-shadow: 0 0 0 2px rgba(91,107,247,0.15); }
[data-testid="stMetric"] { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 8px 12px; }
[data-testid="stMetric"] label { color: var(--fg-muted) !important; font-size: 0.6rem !important; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; }
[data-testid="stMetric"] [data-testid="stMetricValue"] { color: var(--fg) !important; font-weight: 700; font-size: 1.2rem !important; letter-spacing: -0.3px; }
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"], .stMultiSelect div[data-baseweb="select"] { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; color: var(--fg); font-size: 0.85rem; }
.stTextInput input:focus, .stTextArea textarea:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(91,107,247,0.08); }
.stSlider > div > div > div { background: var(--border); }
.stSlider > div > div > div > div { background: var(--accent); }
.stDataFrame { border-radius: var(--radius); overflow: hidden; border: 1px solid var(--border); }
.streamlit-expanderHeader { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; font-size: 0.85rem; }
[data-testid="stFileUploader"] section { border: 1px dashed var(--border); border-radius: var(--radius); padding: 1rem; }
[data-testid="stFileUploader"] section:hover { border-color: var(--accent); }
.stAlert { border-radius: 8px; border: 1px solid var(--border); font-size: 0.85rem; }
.stSpinner > div > div { border-color: var(--accent) !important; }
hr { border-color: var(--border); margin: 0.6rem 0; }
.stChatMessage { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 0.75rem; }
h1, h2, h3, h4 { font-weight: 600; letter-spacing: -0.3px; color: var(--fg); }
.stMarkdown { font-size: 0.88rem; }
div[data-baseweb="select"] > div { background: var(--bg-card) !important; }
.stCheckbox label, .stRadio label { font-size: 0.85rem; }

.hero { text-align: center; padding: 1.5rem 0; }
.hero h1 { font-size: 2.2rem; font-weight: 800; letter-spacing: -0.5px; background: linear-gradient(135deg, #5b6bf7, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.hero p { font-size: 1rem; color: var(--fg-muted); margin-top: 0.3rem; }
.feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.5rem; margin: 1rem 0; }
.feature-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem; text-align: center; transition: all 0.2s; }
.feature-card:hover { border-color: var(--accent); transform: translateY(-2px); }
.feature-card .icon { font-size: 1.8rem; }
.feature-card .title { font-size: 0.8rem; font-weight: 600; margin-top: 0.3rem; }
.feature-card .desc { font-size: 0.7rem; color: var(--fg-muted); }
@keyframes shimmer { 0% { opacity: 0.4; } 50% { opacity: 0.8; } 100% { opacity: 0.4; } }
.skeleton { background: var(--bg-card); border-radius: var(--radius); height: 60px; animation: shimmer 1.5s ease-in-out infinite; margin-bottom: 0.5rem; }
.skeleton-sm { height: 40px; }
.skeleton-lg { height: 200px; }
.quick-prompt { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 0.4rem 0.8rem; font-size: 0.78rem; color: var(--fg-muted); cursor: pointer; transition: all 0.15s; display: inline-block; margin: 0.15rem; }
.quick-prompt:hover { border-color: var(--accent); color: var(--fg); }
"""

st.markdown(f"<style>{THEME_DARK if st.session_state.theme == 'dark' else THEME_LIGHT}</style>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


def convert_df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")


def show_skeleton(lines=3, large=False):
    cls = "skeleton skeleton-lg" if large else "skeleton skeleton-sm"
    for _ in range(lines):
        st.markdown(f'<div class="{cls}"></div>', unsafe_allow_html=True)
    st.rerun()

def apply_theme(fig):
    """Apply the chart theme from config to a plotly figure"""
    fig.update_layout(**CHART_THEME)
    return fig

# ── Sparkline helper ───────────────────────────────────────
def sparkline(series, color='#5b6bf7', height=40):
    """Mini sparkline chart"""
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

# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    col1, col2 = st.columns([1, 3])
    with col1: st.image("https://cdn-icons-png.flaticon.com/512/4727/4727496.png", width=50)
    with col2: st.markdown("### 📊 Data Analyst Pro")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🌓", key="theme_t", use_container_width=True):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()
    with c2:
        st.caption(f"{'🌙' if st.session_state.theme=='dark' else '☀️'}")
    
    st.markdown("---")
    
    with st.expander("📂 Data Input", expanded=(st.session_state.df is None)):
        uploaded = st.file_uploader(FILE_UPLOADER_LABEL, type=SUPPORTED_FILE_TYPES, key="fu")
        if uploaded and (st.session_state.filename != uploaded.name or st.session_state.df is None):
            with st.spinner("Loading..."):
                time.sleep(0.3)
                df = load_and_process_data(uploaded)
                if df is not None:
                    st.session_state.df = df; st.session_state.filename = uploaded.name
                    st.session_state.cleaned_df = None
                    st.success(f"✅ {uploaded.name}")
        
        if st.session_state.df is not None:
            st.caption(f"📄 {st.session_state.filename}")
            if st.button("🗑 Clear", key="clr", use_container_width=True):
                st.session_state.df = None; st.session_state.filename = ""
                st.rerun()
    
    with st.expander("🔌 Connections", expanded=False):
        tab_db, tab_gs = st.tabs(["🗄 DB", "☁️ Sheets"])
        with tab_db:
            if SQL_AVAIL:
                db_type = st.selectbox("Type", DB_TYPES, key="dbt")
                h = p = None  # Initialize to prevent NameError
                if db_type != "SQLite":
                    h = st.text_input("Host", "localhost", key="dbh")
                    p = st.text_input("Port", "3306" if db_type=="MySQL" else "5432", key="dbp")
                    st.text_input("DB", key="dbn"); st.text_input("User", key="dbu")
                    st.text_input("Pass", type="password", key="dbpw")
                else:
                    p = st.text_input("Path", "database.db", key="dbpa")
                if st.button("Connect", key="dbc", use_container_width=True):
                    try:
                        if db_type == "SQLite":
                            cs = f"sqlite:///{st.session_state.dbpa}"
                        elif db_type == "MySQL":
                            cs = f"mysql+pymysql://{st.session_state.dbu}:{st.session_state.dbpw}@{h}:{p}/{st.session_state.dbn}"
                        elif db_type == "PostgreSQL":
                            cs = f"postgresql://{st.session_state.dbu}:{st.session_state.dbpw}@{h}:{p}/{st.session_state.dbn}"
                        elif db_type == "SQL Server":
                            cs = f"mssql+pyodbc://{st.session_state.dbu}:{st.session_state.dbpw}@{h}:{p}/{st.session_state.dbn}?driver=ODBC+Driver+17+for+SQL+Server"
                        engine = create_engine(cs)
                        with engine.connect() as conn:
                            tables = pd.read_sql("SHOW TABLES" if db_type=="MySQL" else "SELECT table_name FROM information_schema.tables WHERE table_schema='public'", conn)
                        st.success(f"✅ {len(tables)} tables")
                        st.session_state.db_config = {"engine": engine, "tables": tables}
                    except Exception as e:
                        st.error(f"❌ Connection error: {str(e)}")
            else: st.warning("pip install sqlalchemy pymysql")
        with tab_gs:
            if GSHEET_AVAIL:
                gj = st.file_uploader("Service Account JSON", type=["json"], key="gsj")
                st.text_input("Sheet URL/ID", key="gsu")
                if st.button("Load", key="gsl", use_container_width=True) and gj:
                    try:
                        gc = gspread.service_account_from_dict(json.loads(gj.getvalue().decode()))
                        sh = gc.open_by_url(st.session_state.gsu) if "http" in st.session_state.gsu else gc.open_by_key(st.session_state.gsu)
                        ws = sh.sheet1; data = ws.get_all_values()
                        st.session_state.df = pd.DataFrame(data[1:], columns=data[0])
                        st.success(f"✅ {len(st.session_state.df)} rows")
                    except Exception as e: st.error(f"❌ {e}")
            else: st.warning("pip install gspread")
    
    with st.expander("⚙️ AI Setup", expanded=False):
        st.text_input("Gemini API Key", type="password", key="genai_key",
                     help="https://aistudio.google.com/apikey")
        if st.session_state.genai_key: st.success("✅ Key ready")
        else: st.warning("⚠️ Enter API key")
    
    if st.session_state.df is not None:
        st.markdown("---")
        render_sidebar_stats(st.session_state.df)

# ═══════════════════════════════════════════════════════════
# LANDING PAGE — Hero Section
# ═══════════════════════════════════════════════════════════
if st.session_state.df is None:
    st.markdown("""
    <div class="hero-bg">
        <div class="particle particle-1"></div>
        <div class="particle particle-2"></div>
        <div class="particle particle-3"></div>
        <div class="particle particle-4"></div>
        <div class="particle particle-5"></div>
        <div class="hero">
            <h1 class="typewriter-cursor"><span class="typewriter">Data Analyst Pro</span></h1>
            <p>Enterprise AI-powered data analysis platform</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card glow"><div class="icon">📂</div><div class="title">Upload</div><div class="desc">CSV, Excel, DB</div></div>
        <div class="feature-card"><div class="icon">🤖</div><div class="title">AI Chat</div><div class="desc">Gemini-powered</div></div>
        <div class="feature-card"><div class="icon">📈</div><div class="title">Forecast</div><div class="desc">Prophet</div></div>
        <div class="feature-card"><div class="icon">🧠</div><div class="title">AutoML</div><div class="desc">XGBoost + RF</div></div>
        <div class="feature-card"><div class="icon">🔍</div><div class="title">Anomaly</div><div class="desc">Detection</div></div>
        <div class="feature-card"><div class="icon">⚛️</div><div class="title">Molecule</div><div class="desc">3D viz</div></div>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.info("**📂 Upload** — CSV, Excel, Google Sheets, or Databases")
    c2.success("**🤖 AI Chat** — Natural language queries with Gemini")
    c3.warning("**📈 Analytics** — Forecast, AutoML, Anomaly detection, Profiling")
    
    st.caption("Upload data from the sidebar to get started →")
    
    # Quick start tutorial
    render_quick_start_tutorial()

else:
    raw = st.session_state.df
    num = raw.select_dtypes(include=[np.number]).columns.tolist()
    cat = raw.select_dtypes(include=["object","str","category"]).columns.tolist()
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
        
        # Sparkline row (if numeric cols)
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
                if df[c].dtype in [np.float64, np.int64]:
                    col_config[c] = st.column_config.NumberColumn(c)
                elif "date" in c.lower() or "time" in c.lower():
                    col_config[c] = st.column_config.DatetimeColumn(c)
                else:
                    col_config[c] = st.column_config.TextColumn(c)
            st.dataframe(
                df.head(100),
                width='stretch',
                column_config=col_config,
                use_container_width=True
            )
        
        # Export
        with st.expander("📤 Export", expanded=False):
            col1, col2, col3 = st.columns(3)
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
                if st.button("🔄 Reset Session", use_container_width=True):
                    for k in list(st.session_state.keys()): del st.session_state[k]
                    st.rerun()
            with col3:
                st.write(f"**{df.shape[0]:,}** rows × **{df.shape[1]:,}** cols")
                st.write(f"**{len(num)}** numeric, **{len(cat)}** categorical")

    # ═══════════════ AI & ML ═══════════════
    with main_tabs[1]:
        is_valid, msg = validate_dataframe(df, min_rows=MIN_ROWS_VALIDATION)
        if not is_valid:
            st.error(f"❌ {msg}")
        else:
            ai_tabs = st.tabs(AI_TABS)
            
            # ── AI Chat ──
            with ai_tabs[0]:
                if GENAI_AVAIL and st.session_state.genai_key:
                    try:
                        genai.configure(api_key=st.session_state.genai_key)
                        model = genai.GenerativeModel('gemini-2.0-flash')
                        
                        data_preview = df.head(20).to_string()
                        data_info = f"Dataset: {len(df)} rows, {len(num)} numeric, {len(cat)} categorical"
                        col_names = ", ".join(df.columns.tolist())
                        context = f"""You are a data analyst assistant.
Dataset: {data_info}
Columns: {col_names}
Sample data (first 20 rows):
{data_preview}
Answer in Vietnamese, provide insights from data."""
                        
                        # Welcome message
                        if not st.session_state.genai_chat:
                            st.info("💡 **Ask me anything about your data!**\n\nTry clicking a suggestion below:")
                            
                            # Quick prompts
                            prompts = [
                                "What are the top trends?",
                                "Which column has most outliers?",
                                "Show me correlations",
                                "Summarize the dataset",
                                "What's the best chart for this data?"
                            ]
                            cols = st.columns(len(prompts))
                            for i, p in enumerate(prompts):
                                with cols[i]:
                                    if st.button(f"💬 {p}", key=f"qp_{i}", use_container_width=True):
                                        st.session_state.genai_chat.append({"role": "user", "content": p})
                                        st.rerun()
                            st.markdown("---")
                        
                        for msg in st.session_state.genai_chat:
                            with st.chat_message(msg["role"]): st.markdown(msg["content"])
                        
                        if prompt := st.chat_input("💬 Ask about your data..."):
                            st.session_state.genai_chat.append({"role": "user", "content": prompt})
                            with st.chat_message("user"): st.markdown(prompt)
                            with st.chat_message("assistant"):
                                with st.spinner("..."):
                                    resp = model.generate_content(f"{context}\n\nQuestion: {prompt}")
                                    st.markdown(resp.text)
                                    st.session_state.genai_chat.append({"role": "assistant", "content": resp.text})
                    except Exception as e:
                        st.error(f"⚠️ {e}")
                else:
                    st.info("""
                ### 🤖 AI Chat with Gemini
                
                Ask questions about your data in natural language!
                
                **To get started:**
                1. Go to sidebar → **AI Setup**
                2. Enter your **Gemini API Key**
                3. Come back here and start chatting!
                
                *Get a free key at [aistudio.google.com](https://aistudio.google.com/apikey)*
                """)
        
        # ── Prophet Forecast ──
        with ai_tabs[1]:
            if PROPHET_AVAIL:
                if dat and num:
                    dc = st.selectbox("Date column:", dat, key="pd")
                    vc = st.selectbox("Value column:", num, key="pv")
                    per = st.slider("Forecast days:", 7, 365, DEFAULT_FORECAST_DAYS)
                    if st.button("📈 Run Forecast", key="prun"):
                        with st.spinner("Training Prophet..."):
                            ts = df.groupby(df[dc].dt.date)[vc].sum().reset_index()
                            ts.columns = ["ds", "y"]; ts["ds"] = pd.to_datetime(ts["ds"])
                            m = Prophet(yearly_seasonality=PROPHET_YEARLY_SEASONALITY, weekly_seasonality=PROPHET_WEEKLY_SEASONALITY, daily_seasonality=PROPHET_DAILY_SEASONALITY)
                            m.fit(ts)
                            fut = m.make_future_dataframe(periods=per)
                            fc = m.predict(fut)
                            fig1 = m.plot(fc, figsize=(12, 5)); st.pyplot(fig1); plt.close()
                            fig2 = m.plot_components(fc, figsize=(12, 6)); st.pyplot(fig2); plt.close()
                            st.dataframe(fc[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(per + 5),
                                        width='stretch', hide_index=True)
                else: st.warning("Need 1 datetime + 1 numeric column")
            else: st.warning("Install: pip install prophet")
        
        # ── AutoML (Automated ML Pipeline) ──
        with ai_tabs[2]:
            if XGB_AVAIL and SKLEARN_AVAIL:
                from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
                from sklearn.linear_model import Ridge, Lasso
                from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
                
                if len(num) >= 2:
                    st.markdown("### 🚀 AutoML Pipeline")
                    st.caption("Tự động tìm siêu tham số (Hyperparameter Tuning) & chọn mô hình tốt nhất")
                    
                    tg = st.selectbox("Target:", num, key="atg")
                    feats = [c for c in num if c != tg]
                    cols = st.multiselect("Features:", feats, default=feats[:min(4, len(feats))], key="atg_feats")
                    
                    if len(cols) >= 1:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            tune_method = st.selectbox("Tuning method:", ["GridSearch", "RandomizedSearch", "None"], key="atg_tune")
                        with col2:
                            cv_folds = st.slider("CV folds:", 2, 10, 3, key="atg_cv")
                        with col3:
                            test_size = st.slider("Test size:", 0.1, 0.4, 0.2, 0.05, key="atg_ts")
                    
                        auto_engineer = st.checkbox("🔧 Auto Feature Engineering (Polynomial degree 2)", True, key="atg_poly")
                        auto_scale = st.checkbox("📐 Auto Scaling (StandardScaler)", True, key="atg_scale")
                        auto_models = st.multiselect("🤖 Models to tune:", 
                            ["Random Forest", "XGBoost", "Gradient Boosting", "Ridge", "Lasso"],
                            default=["Random Forest", "XGBoost"], key="atg_models")
                    
                        if st.button("🚀 Run AutoML", key="atg_run") and auto_models:
                            with st.spinner("⏳ AutoML đang chạy — tuning hyperparameters..."):
                                X = df[cols].dropna()
                                y = df.loc[X.index, tg]
                                
                                if len(X) < 10:
                                    st.error("Cần ít nhất 10 mẫu")
                                else:
                                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
                                    
                                    # Use hyperparameter grids from config
                                    param_grids = PARAM_GRIDS
                                    
                                    model_constructors = {
                                        "Random Forest": RandomForestRegressor(random_state=42),
                                        "XGBoost": xgb.XGBRegressor(random_state=42, verbosity=0),
                                        "Gradient Boosting": GradientBoostingRegressor(random_state=42),
                                        "Ridge": Ridge(),
                                        "Lasso": Lasso(max_iter=5000)
                                    }
                                    
                                    results = []
                                    best_overall = {"name": "", "score": -999, "params": {}}
                                    
                                    progress_bar = st.progress(0)
                                    for i, model_name in enumerate(auto_models):
                                        base_model = model_constructors[model_name]
                                        param_grid = param_grids[model_name]
                                        
                                        # Build pipeline
                                        steps = []
                                        if auto_scale:
                                            steps.append(("scaler", StandardScaler()))
                                        if auto_engineer:
                                            steps.append(("poly", PolynomialFeatures(degree=2, include_bias=False)))
                                        steps.append(("model", base_model))
                                        
                                        pipeline = Pipeline(steps)
                                        
                                        # Tuning
                                        if tune_method == "GridSearch":
                                            searcher = GridSearchCV(pipeline, param_grid, cv=cv_folds, 
                                                                   scoring='r2', n_jobs=-1, verbose=0)
                                        elif tune_method == "RandomizedSearch":
                                            searcher = RandomizedSearchCV(pipeline, param_grid, n_iter=10, cv=cv_folds,
                                                                         scoring='r2', n_jobs=-1, random_state=42, verbose=0)
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
                                            "CV R²": round(cv_score, 4),
                                            "Params": str(best_params)[:120]
                                        })
                                        
                                        if test_score > best_overall["score"]:
                                            best_overall = {"name": model_name, "score": test_score, "params": best_params}
                                        
                                        progress_bar.progress((i + 1) / len(auto_models))
                                    
                                    # Results
                                    result_df = pd.DataFrame(results).sort_values("Test R²", ascending=False)
                                    
                                    st.markdown("#### 📊 Kết quả AutoML")
                                    st.dataframe(result_df, width='stretch', hide_index=True)
                                    
                                    # Best model highlight
                                    st.success(f"🏆 **Mô hình tốt nhất: {best_overall['name']}** — Test R² = {best_overall['score']:.4f}")
                                    st.code(f"Best params: {best_overall['params']}", language="json")
                                    
                                    # Comparison chart
                                    fig = go.Figure()
                                    fig.add_trace(go.Bar(name="Train R²", x=result_df["Model"], y=result_df["Train R²"],
                                                        marker_color="#818cf8"))
                                    fig.add_trace(go.Bar(name="Test R²", x=result_df["Model"], y=result_df["Test R²"],
                                                        marker_color="#34d399"))
                                    fig.update_layout(title="AutoML: So sánh R² (Test vs Train)", barmode='group', height=350)
                                    apply_theme(fig)
                                    st.plotly_chart(fig, width='stretch')
                                    
                                    # Hyperparameter importance insight
                                    if tune_method != "None" and len(auto_models) > 1:
                                        best_result = results[np.argmax([r["Test R²"] for r in results])]
                                        render_insight_card("💡", "Insight",
                                            f"AutoML đã thử {len(auto_models)} mô hình với tuning. "
                                            f"'{best_result['Model']}' đạt kết quả cao nhất (R²={best_result['Test R²']:.4f}). "
                                            f"Feature engineering {'đã' if auto_engineer else 'không'} được áp dụng.",
                                            "good")
                    else:
                        st.warning("Chọn ít nhất 1 feature")
                else:
                    st.warning("Cần ít nhất 2 cột numeric")
            else:
                st.info("Install: pip install xgboost scikit-learn")
                with st.expander("🔧 Install dependencies"):
                    st.code("pip install xgboost scikit-learn")

    # ═══════════════ ANALYTICS ═══════════════
    with main_tabs[2]:
        is_valid, msg = validate_dataframe(df, min_rows=MIN_ROWS_VALIDATION)
        if not is_valid:
            st.error(f"❌ {msg}")
        else:
            an_tabs = st.tabs(ANALYTICS_TABS)
            
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
                                           title="Anomalies", color_discrete_map={"Normal":"#34d399","Anomaly":"#f87171"})
                            apply_theme(fig); st.plotly_chart(fig, width='stretch')
                        render_insight_card("🚨", f"{ac_} anomalies detected",
                                    f"{ac_/(nc+ac_)*100:.1f}% of data — columns: {', '.join(ac)}",
                                    "danger" if ac_ > 10 else "warning")
                else: st.warning("Need numeric columns")
        
        with an_tabs[1]:
            ni = df.select_dtypes(include=[np.number])
            ci = df.select_dtypes(include=["object","str","category"])
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
                            fig = px.histogram(df, x=c_, nbins=30, title=f"Distribution")
                            apply_theme(fig); st.plotly_chart(fig, width='stretch')
                        else:
                            vc = df[c_].value_counts().head(15)
                            fig = px.bar(x=vc.index.astype(str), y=vc.values, title=f"Top 15",
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
                    fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                                  title="Correlation Matrix", aspect='auto')
                    fig.update_layout(height=600)
                    apply_theme(fig); st.plotly_chart(fig, width='stretch')
        
        with an_tabs[2]:
            if num:
                wc = st.selectbox("Variable:", num, key="wi")
                cur_t, cur_m = df[wc].sum(), df[wc].mean()
                pct = st.slider(f"Change {wc} (%):", -50, 100, 0, 1)
                new_t = cur_t * (1 + pct / 100)
                c1, c2, c3 = st.columns(3)
                c1.metric("Current", f"{cur_t:,.2f}")
                c2.metric("Scenario", f"{new_t:,.2f}", delta=f"{pct:+.1f}%")
                c3.metric("Avg", f"{cur_m:,.2f}")
                fig = go.Figure()
                fig.add_trace(go.Bar(x=["Current", "Scenario"], y=[cur_t, new_t],
                                    text=[f"{cur_t:,.2f}", f"{new_t:,.2f}"], textposition='outside',
                                    marker_color=['#818cf8', '#34d399' if pct >= 0 else '#f87171']))
                fig.update_layout(title=f"What-If: {wc} ± {abs(pct):.1f}%", height=400)
                st.plotly_chart(fig, width='stretch')
            else: st.warning("Need numeric columns")
        
        with an_tabs[3]:
            if PDF_AVAIL:
                title = st.text_input("Title", f"Report — {st.session_state.filename or 'Data'}")
                c1, c2 = st.columns(2)
                with c1:
                    inc_s = st.checkbox("Statistics", True)
                    inc_c = st.checkbox("Charts", True)
                with c2:
                    inc_corr = st.checkbox("Correlation", True)
                    inc_o = st.checkbox("Outliers", True)
                if st.button("📄 Generate PDF", key="pdfg"):
                    with st.spinner("Generating PDF..."):
                        pdf = FPDF(); pdf.add_page()
                        pdf.set_font("Helvetica", "B", 20); pdf.cell(0, 15, title, ln=True, align="C")
                        pdf.set_font("Helvetica", "", 10)
                        pdf.cell(0, 8, f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}", ln=True, align="C")
                        pdf.cell(0, 8, f"Dataset: {len(df)} rows x {len(df.columns)} cols", ln=True, align="C")
                        pdf.ln(5)
                        if inc_s:
                            pdf.set_font("Helvetica", "B", 14); pdf.cell(0, 10, "Statistics", ln=True)
                            pdf.set_font("Helvetica", "", 9)
                            for c in df.columns[:15]:
                                try:
                                    if df[c].dtype in [np.float64, np.int64]:
                                        pdf.cell(0, 5, f"{c}: Mean={df[c].mean():.2f}, Std={df[c].std():.2f}, Min={df[c].min():.2f}, Max={df[c].max():.2f}", ln=True)
                                    else:
                                        vc = df[c].value_counts()
                                        pdf.cell(0, 5, f"{c}: {df[c].nunique()} unique values", ln=True)
                                except Exception: pass
                        if inc_corr and len(num) >= 2:
                            pdf.set_font("Helvetica", "B", 14); pdf.cell(0, 10, "Top Correlations", ln=True)
                            pdf.set_font("Helvetica", "", 9)
                            corr = df[num].corr()
                            pairs = []
                            for i in range(len(num)):
                                for j in range(i+1, len(num)):
                                    pairs.append((num[i], num[j], corr.iloc[i, j]))
                            for a, b, r in sorted(pairs, key=lambda x: abs(x[2]), reverse=True)[:10]:
                                pdf.cell(0, 5, f"{a} vs {b}: r = {r:.3f}", ln=True)
                        st.download_button("📥 Download", bytes(pdf.output(dest="S")),
                                         f"report_{st.session_state.filename or 'data'}.pdf", "application/pdf")
            else: st.warning("Install: pip install fpdf2")

        # ── Data Cleaning ──
        with an_tabs[4]:
            st.markdown("### 🧹 Data Cleaning & Transformation")
            st.caption("Xử lý missing values, duplicates, outliers, encoding và scaling")
            
            # Initialize cleaned_df if not exists
            if "cleaned_df" not in st.session_state or st.session_state.cleaned_df is None:
                st.session_state.cleaned_df = df.copy()
            
            work_df = st.session_state.cleaned_df
            changes = []
            
            # Section 1: Missing Values
            st.markdown("#### 🔲 Missing Values")
            missing_counts = work_df.isnull().sum()
            missing_cols = missing_counts[missing_counts > 0]
            
            if len(missing_cols) > 0:
                st.write(f"**{len(missing_cols)} cột có missing values:**")
                missing_df = pd.DataFrame({
                    "Column": missing_cols.index,
                    "Missing": missing_cols.values,
                    "Missing %": [f"{v/len(work_df)*100:.1f}%" for v in missing_cols.values]
                })
                st.dataframe(missing_df, width='stretch', hide_index=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    mv_action = st.selectbox("Hành động:", 
                        ["Drop rows with any NaN", "Drop rows with all NaN", 
                         "Fill with Mean", "Fill with Median", "Fill with Mode", "Fill with 0",
                         "Forward Fill", "Backward Fill"], key="mv_action")
                with col2:
                    mv_cols = st.multiselect("Áp dụng cho cột:", 
                        missing_cols.index.tolist(), default=missing_cols.index.tolist(), key="mv_cols")
                
                if st.button("✨ Apply Missing Value Treatment", key="mv_apply"):
                    try:
                        if mv_action == "Drop rows with any NaN":
                            before = len(work_df)
                            work_df = work_df.dropna(subset=mv_cols)
                            changes.append(f"Dropped {before - len(work_df)} rows with NaN in {len(mv_cols)} columns")
                        elif mv_action == "Drop rows with all NaN":
                            before = len(work_df)
                            work_df = work_df.dropna(how='all', subset=mv_cols)
                            changes.append(f"Dropped {before - len(work_df)} rows with all NaN")
                        elif mv_action == "Fill with Mean":
                            for c in mv_cols:
                                if work_df[c].dtype in [np.float64, np.int64]:
                                    work_df[c] = work_df[c].fillna(work_df[c].mean())
                                    changes.append(f"Filled '{c}' with mean")
                        elif mv_action == "Fill with Median":
                            for c in mv_cols:
                                if work_df[c].dtype in [np.float64, np.int64]:
                                    work_df[c] = work_df[c].fillna(work_df[c].median())
                                    changes.append(f"Filled '{c}' with median")
                        elif mv_action == "Fill with Mode":
                            for c in mv_cols:
                                mode_val = work_df[c].mode()
                                if len(mode_val) > 0:
                                    work_df[c] = work_df[c].fillna(mode_val[0])
                                    changes.append(f"Filled '{c}' with mode")
                        elif mv_action == "Fill with 0":
                            for c in mv_cols:
                                work_df[c] = work_df[c].fillna(0)
                                changes.append(f"Filled '{c}' with 0")
                        elif mv_action == "Forward Fill":
                            for c in mv_cols:
                                work_df[c] = work_df[c].ffill()
                                changes.append(f"Forward filled '{c}'")
                        elif mv_action == "Backward Fill":
                            for c in mv_cols:
                                work_df[c] = work_df[c].bfill()
                                changes.append(f"Backward filled '{c}'")
                        
                        st.session_state.cleaned_df = work_df
                        st.success(f"✅ Applied: {mv_action}")
                        if changes:
                            st.info(f"📝 Changes: {'; '.join(changes[-3:])}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.success("✅ Không có missing values")
            
            st.markdown("---")
            
            # Section 2: Duplicates
            st.markdown("#### 🔁 Duplicate Rows")
            dup_count = work_df.duplicated().sum()
            if dup_count > 0:
                st.warning(f"⚠️ **{dup_count}** duplicate rows found ({dup_count/len(work_df)*100:.1f}%)")
                if st.button("🗑 Remove Duplicates", key="dup_remove"):
                    before = len(work_df)
                    work_df = work_df.drop_duplicates()
                    st.session_state.cleaned_df = work_df
                    st.success(f"✅ Removed {before - len(work_df)} duplicate rows")
                    st.rerun()
            else:
                st.success("✅ Không có duplicate rows")
            
            st.markdown("---")
            
            # Section 3: Outliers
            st.markdown("#### 📊 Outlier Detection & Treatment")
            num_cols = work_df.select_dtypes(include=[np.number]).columns.tolist()
            if num_cols:
                outlier_col = st.selectbox("Chọn cột numeric:", num_cols, key="outlier_col")
                outlier_method = st.selectbox("Phương pháp:", ["IQR (1.5x)", "Z-Score (3σ)"], key="outlier_method")
                
                if outlier_method == "IQR (1.5x)":
                    q1, q3 = work_df[outlier_col].quantile(0.25), work_df[outlier_col].quantile(0.75)
                    iqr = q3 - q1
                    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                    outliers = work_df[(work_df[outlier_col] < lower) | (work_df[outlier_col] > upper)]
                else:
                    z_scores = np.abs((work_df[outlier_col] - work_df[outlier_col].mean()) / work_df[outlier_col].std())
                    outliers = work_df[z_scores > 3]
                
                st.write(f"**{len(outliers)} outliers detected** (range: {work_df[outlier_col].min():.2f} - {work_df[outlier_col].max():.2f})")
                
                if len(outliers) > 0:
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✂️ Remove Outliers", key="out_remove"):
                            work_df = work_df.drop(outliers.index)
                            st.session_state.cleaned_df = work_df
                            st.success(f"✅ Removed {len(outliers)} outliers")
                            st.rerun()
                    with col2:
                        if st.button("🔒 Cap Outliers (clip to bounds)", key="out_cap"):
                            if outlier_method == "IQR (1.5x)":
                                work_df[outlier_col] = work_df[outlier_col].clip(lower, upper)
                            else:
                                mean, std = work_df[outlier_col].mean(), work_df[outlier_col].std()
                                work_df[outlier_col] = work_df[outlier_col].clip(mean - 3*std, mean + 3*std)
                            st.session_state.cleaned_df = work_df
                            st.success(f"✅ Capped {len(outliers)} outliers in '{outlier_col}'")
                            st.rerun()
            else:
                st.info("Không có cột numeric để detect outliers")
            
            st.markdown("---")
            
            # Section 4: Categorical Encoding
            st.markdown("#### 🔤 Categorical Encoding")
            cat_cols = work_df.select_dtypes(include=["object", "str", "category"]).columns.tolist()
            if cat_cols:
                enc_cols = st.multiselect("Chọn cột categorical:", cat_cols, key="enc_cols")
                enc_method = st.selectbox("Encoding method:", 
                    ["One-Hot Encoding", "Label Encoding", "Frequency Encoding"], key="enc_method")
                
                if st.button("🔄 Apply Encoding", key="enc_apply") and enc_cols:
                    try:
                        if enc_method == "One-Hot Encoding":
                            work_df = pd.get_dummies(work_df, columns=enc_cols, prefix=enc_cols)
                            changes.append(f"One-Hot encoded: {', '.join(enc_cols)}")
                        elif enc_method == "Label Encoding":
                            for c in enc_cols:
                                work_df[c] = work_df[c].astype('category').cat.codes
                                changes.append(f"Label encoded '{c}'")
                        elif enc_method == "Frequency Encoding":
                            for c in enc_cols:
                                freq = work_df[c].value_counts(normalize=True)
                                work_df[c] = work_df[c].map(freq)
                                changes.append(f"Frequency encoded '{c}'")
                        
                        st.session_state.cleaned_df = work_df
                        st.success(f"✅ Applied {enc_method}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.info("Không có cột categorical")
            
            st.markdown("---")
            
            # Section 5: Numeric Scaling
            st.markdown("#### 📐 Numeric Scaling")
            num_cols_now = work_df.select_dtypes(include=[np.number]).columns.tolist()
            if num_cols_now:
                scale_cols = st.multiselect("Chọn cột numeric:", num_cols_now, key="scale_cols")
                scale_method = st.selectbox("Scaling method:", 
                    ["StandardScaler (mean=0, std=1)", "MinMaxScaler (0-1)", "RobustScaler"], key="scale_method")
                
                if st.button("📏 Apply Scaling", key="scale_apply") and scale_cols:
                    try:
                        from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
                        
                        if scale_method == "StandardScaler (mean=0, std=1)":
                            scaler = StandardScaler()
                        elif scale_method == "MinMaxScaler (0-1)":
                            scaler = MinMaxScaler()
                        else:
                            scaler = RobustScaler()
                        
                        work_df[scale_cols] = scaler.fit_transform(work_df[scale_cols])
                        st.session_state.cleaned_df = work_df
                        st.success(f"✅ Applied {scale_method} to {len(scale_cols)} columns")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.info("Không có cột numeric")
            
            st.markdown("---")
            
            # Section 6: Summary & Actions
            st.markdown("#### 📋 Summary & Actions")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Original Rows", len(df))
            with c2:
                st.metric("Current Rows", len(work_df))
            with c3:
                st.metric("Current Cols", len(work_df.columns))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔄 Reset to Original", use_container_width=True, key="clean_reset"):
                    st.session_state.cleaned_df = df.copy()
                    st.success("✅ Reset to original data")
                    st.rerun()
            with col2:
                if st.button("💾 Save Cleaned Data", use_container_width=True, key="clean_save"):
                    st.session_state.df = work_df.copy()
                    st.success("✅ Cleaned data saved as main dataset")
                    st.rerun()
            with col3:
                if st.button("📥 Export Cleaned", use_container_width=True, key="clean_export"):
                    csv = work_df.to_csv(index=False).encode("utf-8")
                    st.download_button("Download CSV", csv, 
                        f"cleaned_{st.session_state.filename or 'data'}.csv", "text/csv",
                        key="clean_dl")

    # ═══════════════ DEEP ANALYSIS ═══════════════
    with main_tabs[3]:
        is_valid, msg = validate_dataframe(df, min_rows=MIN_ROWS_VALIDATION)
        if not is_valid:
            st.error(f"❌ {msg}")
        elif DEEP_ANALYSIS_AVAIL:
            render_deep_analysis_tab(df, num, cat, dat)
        else:
            st.error("Advanced Analytics module unavailable. Check advanced_analytics.py")
            with st.expander("🔧 Install dependencies", expanded=True):
                st.code("""
pip install scipy scikit-learn statsmodels matplotlib seaborn
                """)
                if st.button("🔄 Refresh", key="da_refresh"):
                    st.rerun()

    # ═══════════════ MOLECULE ═══════════════
    with main_tabs[4]:
        is_valid, msg = validate_dataframe(df, min_rows=MIN_ROWS_VALIDATION)
        if not is_valid:
            st.error(f"❌ {msg}")
        elif SOLAR_SYSTEM_AVAIL:
            render_solar_system_tab(df, st.session_state.filename or "Dataset")
        else:
            st.warning("Solar System module unavailable")

st.caption("📊 Data Analyst Pro v2.0 — Built with Streamlit, Gemini AI, Prophet, XGBoost & Plotly")