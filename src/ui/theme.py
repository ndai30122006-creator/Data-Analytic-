"""Theme configuration for Streamlit UI"""
import streamlit as st


def render_theme() -> None:
    """Inject custom CSS theme into the Streamlit app."""
    st.markdown("""
    <style>
    /* ── Base ── */
    .stApp { background: #0f172a; color: #e2e8f0; }
    .stApp > header { background: #1e293b !important; }
    .stApp > footer { display: none; }

    /* ── Typography ── */
    h1, h2, h3 { font-weight: 700 !important; letter-spacing: -0.02em; }
    h1 { font-size: 2rem !important; background: linear-gradient(135deg, #818cf8, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    h2 { font-size: 1.4rem !important; color: #f1f5f9 !important; }
    h3 { font-size: 1.1rem !important; color: #cbd5e1 !important; }
    p, li, .stMarkdown { color: #cbd5e1; }

    /* ── Cards ── */
    div[data-testid="stMetric"] {
        background: #1e293b; border: 1px solid #334155; border-radius: 12px;
        padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }
    div[data-testid="stMetric"] > div:first-child { color: #94a3b8; font-size: 0.8rem; }
    div[data-testid="stMetric"] > div:nth-child(2) { color: #f1f5f9; font-size: 1.6rem; font-weight: 700; }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #5b6bf7, #7c3aed); color: white;
        border: none; border-radius: 8px; padding: 0.5rem 1.2rem;
        font-weight: 600; transition: all 0.2s;
    }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(91,107,247,0.4); }

    /* ── DataFrames ── */
    .stDataFrame { background: #1e293b; border-radius: 12px; border: 1px solid #334155; }
    .stDataFrame th { background: #334155 !important; color: #e2e8f0 !important; }
    .stDataFrame td { color: #cbd5e1 !important; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; background: #1e293b; border-radius: 10px; padding: 4px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px; padding: 6px 14px; color: #94a3b8;
        font-weight: 500; transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] { background: #5b6bf7 !important; color: white !important; }

    /* ── Expanders ── */
    .streamlit-expanderHeader { background: #1e293b; border-radius: 8px; border: 1px solid #334155; }
    .streamlit-expanderContent { border: 1px solid #334155; border-top: none; border-radius: 0 0 8px 8px; padding: 12px; }

    /* ── Select / Input ── */
    .stSelectbox > div > div { background: #1e293b; border: 1px solid #334155; border-radius: 8px; color: #e2e8f0; }
    .stMultiSelect > div > div { background: #1e293b; border: 1px solid #334155; border-radius: 8px; }
    .stSlider > div > div > div { background: #5b6bf7 !important; }

    /* ── Alerts ── */
    .stAlert { border-radius: 10px; border: none; }
    div[data-testid="stAlert"] { background: #1e293b; border-left: 4px solid #5b6bf7; }

    /* ── Progress ── */
    .stProgress > div > div > div { background: linear-gradient(90deg, #5b6bf7, #a78bfa); }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] { background: #1e293b; border-right: 1px solid #334155; }
    section[data-testid="stSidebar"] .stMarkdown { color: #cbd5e1; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #475569; }

    /* ── Code blocks ── */
    code { background: #334155 !important; color: #a78bfa !important; border-radius: 4px; padding: 2px 6px; }
    pre code { background: #1e293b !important; color: #e2e8f0 !important; }

    /* ── Hero section ── */
    .hero-bg { background: linear-gradient(135deg, rgba(91,107,247,0.08), rgba(167,139,250,0.05)); border-radius: 16px; border: 1px solid rgba(91,107,247,0.15); }
    </style>
    """, unsafe_allow_html=True)