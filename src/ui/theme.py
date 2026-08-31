"""
🎨 Theme — Glassmorphism Aurora (Plan A)
Hoàn toàn khác Data-Dense: kính mờ, aurora gradient, dark
"""

from typing import Dict

import streamlit as st

from src.utils.config import set_chart_mode

COLORS = {
    "light": {
        "primary": "#8B5CF6",
        "primary_hover": "#7C3AED",
        "primary_light": "rgba(139,92,246,0.15)",
        "secondary": "#EC4899",
        "secondary_hover": "#DB2777",
        "success": "#10B981",
        "warning": "#F59E0B",
        "danger": "#EF4444",
        "info": "#06B6D4",
        "bg_primary": "#0A0A1A",
        "bg_secondary": "rgba(255,255,255,0.08)",
        "bg_tertiary": "rgba(255,255,255,0.05)",
        "bg_hover": "rgba(255,255,255,0.12)",
        "text_primary": "rgba(255,255,255,0.92)",
        "text_secondary": "rgba(255,255,255,0.65)",
        "text_tertiary": "rgba(255,255,255,0.45)",
        "text_inverse": "#0A0A1A",
        "border": "rgba(255,255,255,0.18)",
        "border_light": "rgba(255,255,255,0.10)",
        "chart_bg": "rgba(0,0,0,0)",
        "chart_grid": "rgba(255,255,255,0.08)",
    },
    "dark": {
        "primary": "#A78BFA",
        "primary_hover": "#8B5CF6",
        "primary_light": "rgba(167,139,250,0.15)",
        "secondary": "#F472B6",
        "secondary_hover": "#EC4899",
        "success": "#34D399",
        "warning": "#FBBF24",
        "danger": "#F87171",
        "info": "#22D3EE",
        "bg_primary": "#0A0A1A",
        "bg_secondary": "rgba(255,255,255,0.08)",
        "bg_tertiary": "rgba(255,255,255,0.05)",
        "bg_hover": "rgba(255,255,255,0.12)",
        "text_primary": "rgba(255,255,255,0.92)",
        "text_secondary": "rgba(255,255,255,0.65)",
        "text_tertiary": "rgba(255,255,255,0.45)",
        "text_inverse": "#0A0A1A",
        "border": "rgba(255,255,255,0.18)",
        "border_light": "rgba(255,255,255,0.10)",
        "chart_bg": "rgba(0,0,0,0)",
        "chart_grid": "rgba(255,255,255,0.08)",
    },
}

_GLASS_TOKENS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root {
    --primary: #8B5CF6; --primary-hover: #7C3AED; --primary-soft: rgba(139,92,246,0.18);
    --primary-glow: rgba(139,92,246,0.45); --secondary: #EC4899; --accent: #06B6D4;
    --success: #10B981; --warning: #F59E0B; --danger: #EF4444; --info: #06B6D4;
    --bg-primary: #0A0A1A; --bg-secondary: rgba(255,255,255,0.08); --bg-tertiary: rgba(255,255,255,0.05);
    --bg-hover: rgba(255,255,255,0.12); --text-primary: rgba(255,255,255,0.92);
    --text-secondary: rgba(255,255,255,0.65); --text-tertiary: rgba(255,255,255,0.45);
    --text-inverse: #0A0A1A; --border: rgba(255,255,255,0.18); --border-light: rgba(255,255,255,0.10);
    --ring: #8B5CF6;
    --radius-sm: 12px; --radius-md: 16px; --radius-lg: 24px; --radius-xl: 32px;
    --shadow-glass: 0 8px 32px rgba(31,38,135,0.37), inset 0 1px 0 rgba(255,255,255,0.15);
    --font: 'Outfit', system-ui, sans-serif; --font-display: 'Space Grotesk', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
}
"""

_BASE_CSS = """
* { font-family: var(--font); -webkit-font-smoothing: antialiased; box-sizing: border-box; }
html, body, .stApp {
    background: #0A0A1A !important;
    background-image:
        radial-gradient(at 20% 30%, rgba(139,92,246,0.35) 0px, transparent 50%),
        radial-gradient(at 80% 20%, rgba(236,72,153,0.30) 0px, transparent 50%),
        radial-gradient(at 50% 80%, rgba(6,182,214,0.25) 0px, transparent 50%),
        radial-gradient(at 0% 100%, rgba(139,92,246,0.15) 0px, transparent 40%) !important;
    background-attachment: fixed !important;
    color: var(--text-primary);
}
h1, h2, h3, h4 { font-family: var(--font-display); color: var(--text-primary); letter-spacing: -0.02em; }

/* Glass cards */
.metric-card, .kpi-card, .feature-card, .panel, [data-testid="stMetric"] {
    background: rgba(255,255,255,0.08) !important;
    backdrop-filter: blur(16px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 24px !important;
    box-shadow: var(--shadow-glass) !important;
    padding: 16px 18px !important;
    transition: transform 300ms cubic-bezier(0.16,1,0.3,1), box-shadow 300ms, border-color 300ms !important;
}
.metric-card:hover, .kpi-card:hover, .feature-card:hover {
    transform: translateY(-4px) scale(1.01);
    border-color: rgba(139,92,246,0.45) !important;
    box-shadow: 0 12px 40px rgba(139,92,246,0.25), inset 0 1px 0 rgba(255,255,255,0.2) !important;
}
.metric-card .metric-label { font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(255,255,255,0.55); }
.metric-card .metric-value { font-size: 1.8rem; font-weight: 700; color: #FFFFFF; font-family: var(--font-display); }
.kpi-card .kpi-label { font-size: 0.70rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(255,255,255,0.55); }
.kpi-card .kpi-value { font-size: 1.6rem; font-weight: 700; color: #FFFFFF; font-family: var(--font-display); }
.insight-card {
    background: rgba(255,255,255,0.06); backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.12); border-left: 3px solid var(--primary);
    border-radius: 16px; padding: 12px 14px; color: rgba(255,255,255,0.85);
}
.badge { display:inline-flex; align-items:center; gap:6px; padding: 6px 14px; border-radius: 999px; font-size: 0.73rem; font-weight: 600; backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.15); }
.badge-primary { background: rgba(139,92,246,0.20); color: #DDD6FE; }
.badge-success { background: rgba(16,185,129,0.18); color: #A7F3D0; }
.badge-warning { background: rgba(245,158,11,0.18); color: #FDE68A; }
.badge-danger { background: rgba(239,68,68,0.18); color: #FECACA; }
.badge-info { background: rgba(6,182,214,0.18); color: #A5F3FC; }
.hero-bg { background: rgba(255,255,255,0.06); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.15); border-radius: 32px; box-shadow: var(--shadow-glass); }
.cta-banner { background: linear-gradient(135deg, #8B5CF6, #EC4899); color: white; border-radius: 16px; padding: 12px 18px; font-weight: 600; box-shadow: 0 8px 24px rgba(139,92,246,0.35); }

/* Buttons glass */
.stButton > button, .stDownloadButton > button {
    background: rgba(139,92,246,0.9) !important; color: white !important; border: 1px solid rgba(255,255,255,0.2) !important;
    backdrop-filter: blur(12px) !important; border-radius: 16px !important; font-weight: 600 !important;
    box-shadow: 0 4px 16px rgba(139,92,246,0.35) !important; transition: all 300ms !important;
}
.stButton > button:hover { background: rgba(124,58,237,1) !important; transform: translateY(-2px); box-shadow: 0 8px 24px rgba(139,92,246,0.45) !important; }

/* Tabs glass */
.stTabs [role="tab"] { color: rgba(255,255,255,0.55) !important; border-radius: 12px !important; }
.stTabs [role="tab"][aria-selected="true"] { color: #FFFFFF !important; background: rgba(255,255,255,0.10) !important; backdrop-filter: blur(8px); box-shadow: inset 0 0 0 1px rgba(255,255,255,0.15); }

/* Inputs glass */
.stTextInput input, .stSelectbox [data-baseweb="select"] > div, .stTextArea textarea {
    background: rgba(255,255,255,0.06) !important; color: white !important; border: 1px solid rgba(255,255,255,0.12) !important;
    backdrop-filter: blur(12px) !important; border-radius: 12px !important;
}
.stTextInput input:focus { border-color: rgba(139,92,246,0.5) !important; box-shadow: 0 0 0 3px rgba(139,92,246,0.15) !important; }
.stDataFrame { background: rgba(255,255,255,0.05) !important; backdrop-filter: blur(12px) !important; border: 1px solid rgba(255,255,255,0.10) !important; border-radius: 20px !important; overflow: hidden; }

/* Sidebar glass */
[data-testid="stSidebar"] { background: rgba(10,10,26,0.70) !important; backdrop-filter: blur(20px) saturate(180%) !important; border-right: 1px solid rgba(255,255,255,0.10) !important; }
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }
[data-testid="stSidebar"] .stCaption { color: rgba(255,255,255,0.55) !important; }

::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.45); border-radius: 4px; }
"""

_ANIM = """
<style>
@keyframes auroraShift { 0% { filter: hue-rotate(0deg); } 50% { filter: hue-rotate(15deg); } 100% { filter: hue-rotate(0deg); } }
.stApp { animation: auroraShift 20s ease-in-out infinite; }
@keyframes floatIn { from { opacity:0; transform: translateY(12px) scale(0.98); } to { opacity:1; transform: none; } }
.animate-fade-in { animation: floatIn 600ms cubic-bezier(0.16,1,0.3,1); }
@media (prefers-reduced-motion: reduce) { *,*::before,*::after { animation: none !important; transition: none !important; } }
</style>
"""


def get_light_mode_css():
    return _GLASS_TOKENS + _BASE_CSS + _ANIM


def get_dark_mode_css():
    return _GLASS_TOKENS + _BASE_CSS + _ANIM


def metric_card(title, value, change="", icon="✨", color="primary"):
    tone = "" if color == "primary" else f"tone-{color}"
    change_html = f'<span class="badge badge-{color}">{change}</span>' if change else ""
    return f"""
    <div class="metric-card {tone} animate-fade-in">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <span class="metric-label">{title}</span><span style="font-size:20px">{icon}</span>
        </div>
        <div class="metric-value">{value}</div>{change_html}
    </div>"""


def status_badge(text, status="primary"):
    return f'<span class="badge badge-{status}">{text}</span>'


def gradient_text(text, color1="#8B5CF6", color2="#EC4899"):
    return f'<span style="background: linear-gradient(135deg,{color1},{color2}); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-weight:800; font-family:var(--font-display); font-size:1.15em">{text}</span>'


def render_theme():
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "dark"
    set_chart_mode("dark")
    st.markdown(get_light_mode_css(), unsafe_allow_html=True)


def get_theme_colors(mode="light"):
    return COLORS["light"]


def render_theme_switcher():
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Dark Glass", use_container_width=True):
            st.session_state.theme_mode = "dark"
            st.rerun()
    with c2:
        if st.button("Light Glass", use_container_width=True):
            st.session_state.theme_mode = "light"
            st.rerun()
    st.caption("Glassmorphism Aurora — Plan A")


def debug_theme_config():
    if st.checkbox("Debug Glass"):
        st.json(COLORS)
