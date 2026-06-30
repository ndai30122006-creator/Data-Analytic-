"""Theme configuration — CSS styles and chart theme for the app"""
import streamlit as st

from config import CHART_THEME

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

def apply_chart_theme(fig):
    """Apply global chart theme to a plotly figure"""
    fig.update_layout(**CHART_THEME)
    return fig

def render_theme():
    """Inject CSS theme into the app"""
    st.markdown(f"<style>{THEME_CSS}</style>", unsafe_allow_html=True)