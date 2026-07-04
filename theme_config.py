"""Theme configuration — đen + xanh mint, sinh động"""
import streamlit as st


def render_theme() -> None:
    """Inject vibrant dark mint theme CSS."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    :root {
        --bg: #000000;
        --bg2: #050d1a;
        --card: #0a1628;
        --card-hover: #0f1f3a;
        --text: #e2e8f0;
        --text2: #94a3b8;
        --text3: #64748b;
        --mint: #14b8a6;
        --mint-light: #5eead4;
        --mint-dark: #0f766e;
        --mint-glow: rgba(20, 184, 166, 0.25);
        --mint-glow-strong: rgba(20, 184, 166, 0.4);
        --border: #1a2744;
        --success: #22c55e;
        --warning: #eab308;
        --danger: #ef4444;
        --radius: 12px;
        --radius-sm: 8px;
    }

    html, body, .stApp {
        background: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }

    /* ── Animated background particles ── */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background:
            radial-gradient(ellipse 80% 60% at 20% 20%, rgba(20, 184, 166, 0.04) 0%, transparent 60%),
            radial-gradient(ellipse 60% 50% at 80% 80%, rgba(20, 184, 166, 0.03) 0%, transparent 60%),
            radial-gradient(ellipse 40% 40% at 50% 50%, rgba(20, 184, 166, 0.02) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }

    /* ── Typography ── */
    h1, h2, h3, h4, h5, h6 { color: var(--text) !important; font-weight: 600 !important; letter-spacing: -0.02em !important; }
    p, li, span, div { color: var(--text2); }
    a { color: var(--mint-light) !important; text-decoration: none !important; transition: all 0.2s !important; }
    a:hover { color: var(--mint) !important; text-shadow: 0 0 20px var(--mint-glow) !important; }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020812, #050d1a) !important;
        border-right: 1px solid var(--border) !important;
    }
    section[data-testid="stSidebar"] .stButton button {
        width: 100%;
        background: linear-gradient(135deg, var(--card), #0c1a30) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.45rem 0.9rem !important;
        font-size: 0.85rem !important;
        transition: all 0.25s !important;
        position: relative !important;
        overflow: hidden !important;
    }
    section[data-testid="stSidebar"] .stButton button::after {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, var(--mint-glow), transparent);
        transition: left 0.5s;
    }
    section[data-testid="stSidebar"] .stButton button:hover::after { left: 100%; }
    section[data-testid="stSidebar"] .stButton button:hover {
        border-color: var(--mint) !important;
        background: var(--card-hover) !important;
        box-shadow: 0 0 20px var(--mint-glow) !important;
        transform: translateY(-1px);
    }

    /* ── KPI Cards ── */
    .kpi-card {
        background: linear-gradient(135deg, var(--card), #080f20) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 1.2rem !important;
        transition: all 0.3s !important;
        position: relative !important;
        overflow: hidden !important;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, transparent, var(--mint), transparent);
        opacity: 0;
        transition: opacity 0.3s;
    }
    .kpi-card:hover::before { opacity: 1; }
    .kpi-card:hover {
        border-color: var(--mint) !important;
        box-shadow: 0 0 30px var(--mint-glow) !important;
        transform: translateY(-3px) !important;
    }
    .kpi-label { color: var(--text3) !important; font-size: 0.7rem !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; font-weight: 600 !important; }
    .kpi-value { color: var(--mint-light) !important; font-size: 1.8rem !important; font-weight: 800 !important; letter-spacing: -0.03em !important; }
    .kpi-delta { color: var(--success) !important; font-size: 0.85rem !important; font-weight: 600 !important; }

    .insight-card { background: var(--card) !important; border: 1px solid var(--border) !important; border-radius: var(--radius-sm) !important; padding: 0.7rem 1rem !important; margin-bottom: 0.5rem !important; transition: all 0.2s !important; }
    .insight-card:hover { background: var(--card-hover) !important; border-color: var(--mint) !important; }
    .insight-info { border-left: 3px solid var(--mint) !important; }
    .insight-success { border-left: 3px solid var(--success) !important; }
    .insight-warning { border-left: 3px solid var(--warning) !important; }
    .insight-danger { border-left: 3px solid var(--danger) !important; }
    .insight-good { border-left: 3px solid var(--success) !important; }

    /* ── Hero Section ── */
    .hero-bg {
        text-align: center;
        padding: 3.5rem 2rem;
        background: linear-gradient(135deg, #050d1a 0%, #000000 50%, #020812 100%);
        border-radius: var(--radius);
        border: 1px solid var(--border);
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .hero-bg::before {
        content: '';
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background:
            radial-gradient(circle at 30% 40%, rgba(20, 184, 166, 0.06) 0%, transparent 50%),
            radial-gradient(circle at 70% 60%, rgba(94, 234, 212, 0.04) 0%, transparent 50%);
        animation: heroGlow 8s ease-in-out infinite alternate;
    }
    @keyframes heroGlow {
        0% { transform: translate(0, 0) rotate(0deg); }
        100% { transform: translate(-5%, 5%) rotate(3deg); }
    }
    .hero-title {
        font-size: 2.5rem !important; font-weight: 800 !important;
        background: linear-gradient(135deg, #5eead4 0%, #14b8a6 50%, #0d9488 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        margin-bottom: 0.75rem !important;
        position: relative !important;
        z-index: 1 !important;
        animation: titleFade 1s ease-out;
    }
    @keyframes titleFade {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .hero-title::after {
        content: '✨';
        position: absolute;
        font-size: 1.5rem;
        -webkit-text-fill-color: initial;
        animation: sparkle 2s ease-in-out infinite;
    }
    @keyframes sparkle {
        0%, 100% { opacity: 0.3; transform: translate(0, 0); }
        50% { opacity: 1; transform: translate(10px, -10px); }
    }
    .hero-subtitle {
        color: var(--text3) !important;
        font-size: 1.05rem !important;
        max-width: 560px !important;
        margin: 0 auto !important;
        position: relative !important;
        z-index: 1 !important;
        animation: subtitleFade 1s ease-out 0.3s both;
    }
    @keyframes subtitleFade {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ── Feature Cards ── */
    .feature-card {
        background: #0d1f3c;
        border: 1px solid #2a4a7f;
        border-radius: var(--radius);
        padding: 0.6rem 0.4rem;
        text-align: center;
        transition: all 0.3s;
        min-height: 100%;
        position: relative;
        overflow: hidden;
    }
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, transparent, var(--mint), transparent);
        opacity: 0;
        transition: opacity 0.3s;
    }
    .feature-card:hover::before { opacity: 1; }
    .feature-card:hover {
        border-color: var(--mint);
        transform: translateY(-3px);
        box-shadow: 0 6px 24px var(--mint-glow);
        background: #112a50;
    }
    @keyframes cardIn {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .feature-card:nth-child(1) { animation: cardIn 0.4s ease-out 0.1s both; }
    .feature-card:nth-child(2) { animation: cardIn 0.4s ease-out 0.18s both; }
    .feature-card:nth-child(3) { animation: cardIn 0.4s ease-out 0.26s both; }
    .feature-card:nth-child(4) { animation: cardIn 0.4s ease-out 0.34s both; }
    .feature-card:nth-child(5) { animation: cardIn 0.4s ease-out 0.42s both; }
    .feature-card:nth-child(6) { animation: cardIn 0.4s ease-out 0.5s both; }
    .feature-icon { font-size: 1.5rem; display: block; line-height: 1; margin-bottom: 0.3rem; transition: transform 0.3s; }
    .feature-card:hover .feature-icon { transform: scale(1.15); }
    .feature-title { color: var(--text); font-weight: 600; font-size: 0.78rem; display: block; margin-bottom: 0.1rem; }
    .feature-subtitle { color: var(--mint-light); font-size: 0.68rem; font-weight: 400; display: block; opacity: 0.9; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0 !important; background: var(--bg2) !important;
        border-radius: var(--radius-sm) !important; padding: 4px !important;
        border: 1px solid var(--border) !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important; color: var(--text3) !important;
        border-radius: 5px !important; padding: 0.4rem 1rem !important;
        font-size: 0.82rem !important; font-weight: 500 !important;
        transition: all 0.2s !important; border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--mint), #0d9488) !important;
        color: #000000 !important;
        box-shadow: 0 0 20px var(--mint-glow) !important;
    }
    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        color: var(--mint-light) !important;
        background: rgba(20, 184, 166, 0.08) !important;
    }

    /* ── Buttons ── */
    .stButton button {
        background: linear-gradient(135deg, var(--mint), #0d9488) !important;
        color: #000000 !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.45rem 1.3rem !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        transition: all 0.25s !important;
        box-shadow: 0 4px 15px var(--mint-glow) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    .stButton button::after {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
        transition: left 0.5s;
    }
    .stButton button:hover::after { left: 100%; }
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px var(--mint-glow-strong) !important;
    }
    .stButton button:active {
        transform: translateY(0) !important;
    }
    .stButton button[kind="secondary"] {
        background: var(--card) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        box-shadow: none !important;
    }
    .stButton button[kind="secondary"]::after { display: none !important; }
    .stButton button[kind="secondary"]:hover {
        border-color: var(--mint) !important;
        box-shadow: 0 0 20px var(--mint-glow) !important;
    }

    /* ── Metrics ── */
    [data-testid="stMetricValue"] { color: var(--mint-light) !important; font-size: 1.8rem !important; font-weight: 800 !important; letter-spacing: -0.03em !important; }
    [data-testid="stMetricLabel"] { color: var(--text3) !important; font-size: 0.82rem !important; font-weight: 500 !important; }
    [data-testid="stMetricDelta"] { font-size: 0.85rem !important; font-weight: 600 !important; }

    /* ── Tables ── */
    [data-testid="stDataFrame"] { border-radius: var(--radius-sm) !important; border: 1px solid var(--border) !important; overflow: hidden !important; }
    [data-testid="stDataFrame"] th { background: var(--card) !important; color: var(--text2) !important; font-weight: 600 !important; font-size: 0.82rem !important; }
    [data-testid="stDataFrame"] td { color: var(--text) !important; background: #000000 !important; }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, var(--card), #080f20) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text) !important;
        font-weight: 600 !important;
        border: 1px solid var(--border) !important;
        transition: all 0.2s !important;
    }
    .streamlit-expanderHeader:hover { border-color: var(--mint) !important; box-shadow: 0 0 15px var(--mint-glow) !important; }
    .streamlit-expanderContent { background: var(--bg2) !important; border: 1px solid var(--border) !important; border-top: none !important; border-radius: 0 0 var(--radius-sm) var(--radius-sm) !important; padding: 1rem !important; }

    /* ── Select / Input ── */
    [data-baseweb="select"] { background: var(--card) !important; border-radius: var(--radius-sm) !important; border: 1px solid var(--border) !important; transition: all 0.2s !important; }
    [data-baseweb="select"]:hover { border-color: var(--mint) !important; box-shadow: 0 0 15px var(--mint-glow) !important; }
    [data-baseweb="input"] { background: var(--card) !important; border: 1px solid var(--border) !important; border-radius: var(--radius-sm) !important; color: var(--text) !important; transition: all 0.2s !important; }
    [data-baseweb="input"]:focus { border-color: var(--mint) !important; box-shadow: 0 0 15px var(--mint-glow) !important; }

    /* ── File Uploader ── */
    [data-testid="stFileUploader"] {
        background: var(--card) !important;
        border: 2px dashed var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 1rem !important;
        transition: all 0.3s !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: var(--mint) !important;
        background: var(--card-hover) !important;
        box-shadow: 0 0 25px var(--mint-glow) !important;
        transform: translateY(-2px) !important;
    }

    /* ── Progress ── */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--mint), var(--mint-light), var(--mint)) !important;
        background-size: 200% 100% !important;
        animation: progressShine 2s linear infinite;
    }
    @keyframes progressShine {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #000000; }
    ::-webkit-scrollbar-thumb { background: var(--card); border-radius: 4px; transition: all 0.2s; }
    ::-webkit-scrollbar-thumb:hover { background: var(--mint); }

    /* ── Dividers ── */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, var(--mint-dark), var(--mint), var(--mint-dark), transparent) !important;
        margin: 1.5rem 0 !important;
    }

    /* ── Code ── */
    code { background: var(--card) !important; color: var(--mint-light) !important; border-radius: 4px !important; padding: 0.15rem 0.35rem !important; font-size: 0.85rem !important; }
    pre { background: var(--card) !important; border: 1px solid var(--border) !important; border-radius: var(--radius-sm) !important; }

    /* ── Alerts ── */
    .stAlert { background: var(--card) !important; border: 1px solid var(--border) !important; color: var(--text) !important; border-radius: var(--radius-sm) !important; }
    .stAlert [data-testid="stAlert"] { color: var(--text) !important; }

    /* ── Spinner ── */
    .stSpinner > div > div { border-color: var(--mint) transparent transparent transparent !important; }

    /* ── Info boxes ── */
    .st-info, .st-success, .st-warning, .st-error { border-radius: var(--radius-sm) !important; }
    </style>
    """, unsafe_allow_html=True)