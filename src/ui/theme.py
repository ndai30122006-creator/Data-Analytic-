"""
🎨 Theme — Mono Glass (trắng/xám darkmode, đen/xám đậm lightmode)
Toàn bộ mono, không màu, theo yêu cầu
"""

from typing import Dict

import streamlit as st

from src.utils.config import set_chart_mode

COLORS = {
    "light": {
        "primary": "#111827",
        "primary_hover": "#0B1220",
        "primary_light": "#E5E7EB",
        "secondary": "#4B5563",
        "secondary_hover": "#1F2937",
        "success": "#374151",
        "warning": "#6B7280",
        "danger": "#1F2937",
        "info": "#4B5563",
        "bg_primary": "#F9FAFB",
        "bg_secondary": "#FFFFFF",
        "bg_tertiary": "#F3F4F6",
        "bg_hover": "#E5E7EB",
        "text_primary": "#111827",
        "text_secondary": "#4B5563",
        "text_tertiary": "#6B7280",
        "text_inverse": "#FFFFFF",
        "border": "#D1D5DB",
        "border_light": "#E5E7EB",
        "chart_bg": "#FFFFFF",
        "chart_grid": "#E5E7EB",
    },
    "dark": {
        "primary": "#FFFFFF",
        "primary_hover": "#F9FAFB",
        "primary_light": "rgba(255,255,255,0.12)",
        "secondary": "#D1D5DB",
        "secondary_hover": "#9CA3AF",
        "success": "#9CA3AF",
        "warning": "#D1D5DB",
        "danger": "#F3F4F6",
        "info": "#9CA3AF",
        "bg_primary": "#0A0A1A",
        "bg_secondary": "rgba(255,255,255,0.06)",
        "bg_tertiary": "rgba(255,255,255,0.04)",
        "bg_hover": "rgba(255,255,255,0.10)",
        "text_primary": "#F9FAFB",
        "text_secondary": "#D1D5DB",
        "text_tertiary": "#9CA3AF",
        "text_inverse": "#0A0A1A",
        "border": "rgba(255,255,255,0.14)",
        "border_light": "rgba(255,255,255,0.08)",
        "chart_bg": "rgba(0,0,0,0)",
        "chart_grid": "rgba(255,255,255,0.08)",
    },
}

_LIGHT_TOKENS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&family=Quicksand:wght@400;500;600;700&family=Varela+Round&display=swap');
:root {
    --primary: #111827; --primary-hover: #0B1220; --primary-soft: rgba(17,24,39,0.08);
    --primary-glow: rgba(17,24,39,0.15); --secondary: #4B5563; --accent: #6B7280;
    --success: #374151; --warning: #6B7280; --danger: #1F2937; --info: #4B5563;
    --bg-primary: #F9FAFB; --bg-secondary: #FFFFFF; --bg-tertiary: #F3F4F6;
    --bg-hover: #E5E7EB; --text-primary: #111827; --text-secondary: #4B5563; --text-tertiary: #6B7280;
    --text-inverse: #FFFFFF; --border: #D1D5DB; --border-light: #E5E7EB; --ring: #111827;
    --radius-sm: 12px; --radius-md: 16px; --radius-lg: 24px; --radius-xl: 32px;
    --shadow-glass: 0 4px 24px rgba(17,24,39,0.08), 0 1px 4px rgba(17,24,39,0.06);
    --font: 'Nunito', 'Varela Round', system-ui, sans-serif; --font-display: 'Quicksand', 'Nunito', sans-serif; --font-mono: 'JetBrains Mono', monospace;
}
"""

_DARK_TOKENS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&family=Quicksand:wght@400;500;600;700&family=Varela+Round&display=swap');
:root {
    --primary: #FFFFFF; --primary-hover: #F9FAFB; --primary-soft: rgba(255,255,255,0.12);
    --primary-glow: rgba(255,255,255,0.18); --secondary: #D1D5DB; --accent: #9CA3AF;
    --success: #9CA3AF; --warning: #D1D5DB; --danger: #F3F4F6; --info: #9CA3AF;
    --bg-primary: #0A0A1A; --bg-secondary: rgba(255,255,255,0.06); --bg-tertiary: rgba(255,255,255,0.04);
    --bg-hover: rgba(255,255,255,0.10); --text-primary: #F9FAFB; --text-secondary: #D1D5DB; --text-tertiary: #9CA3AF;
    --text-inverse: #0A0A1A; --border: rgba(255,255,255,0.14); --border-light: rgba(255,255,255,0.08); --ring: #FFFFFF;
    --radius-sm: 12px; --radius-md: 16px; --radius-lg: 24px; --radius-xl: 32px;
    --shadow-glass: 0 8px 32px rgba(0,0,0,0.40), inset 0 1px 0 rgba(255,255,255,0.08);
    --font: 'Nunito', 'Varela Round', system-ui, sans-serif; --font-display: 'Quicksand', 'Nunito', sans-serif; --font-mono: 'JetBrains Mono', monospace;
}
"""

_BASE_CSS = """
* { font-family: var(--font); -webkit-font-smoothing: antialiased; box-sizing: border-box; }
html, body, .stApp { background: var(--bg-primary) !important; color: var(--text-primary); }
h1, h2, h3, h4 { font-family: var(--font-display); color: var(--text-primary); letter-spacing: -0.01em; }
.metric-card, .kpi-card, .feature-card, .panel, [data-testid="stMetric"] {
    background: var(--bg-secondary) !important;
    backdrop-filter: blur(12px) saturate(150%) !important;
    border: 1px solid var(--border) !important;
    border-radius: 24px !important;
    box-shadow: var(--shadow-glass) !important;
    padding: 16px 18px !important;
}
.metric-card .metric-label { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-tertiary); }
.metric-card .metric-value { font-size: 1.7rem; font-weight: 700; color: var(--text-primary); font-family: var(--font-display); }
.badge { display:inline-flex; align-items:center; gap:6px; padding: 6px 14px; border-radius: 999px; font-size: 0.73rem; font-weight: 600; border: 1px solid var(--border); }
.badge-primary { background: var(--primary); color: var(--text-inverse); }
.badge-success { background: var(--bg-tertiary); color: var(--text-secondary); border-color: var(--border-light); }
.badge-warning { background: var(--bg-tertiary); color: var(--text-secondary); }
.badge-danger { background: var(--primary); color: var(--text-inverse); opacity: 0.9; }
.hero-bg { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 32px; box-shadow: var(--shadow-glass); }
.stButton > button, .stDownloadButton > button { background: var(--primary) !important; color: var(--text-inverse) !important; border: 1px solid var(--border) !important; border-radius: 999px !important; font-weight: 700 !important; }
.stButton > button:hover { background: var(--primary-hover) !important; transform: translateY(-1px); }
.stTabs [role="tab"] { color: var(--text-tertiary) !important; border-radius: 999px !important; }
.stTabs [role="tab"][aria-selected="true"] { color: var(--text-primary) !important; background: var(--bg-tertiary) !important; border: 1px solid var(--border); }
.stTextInput input, .stSelectbox [data-baseweb="select"] > div, .stTextArea textarea, .stNumberInput input {
    background: var(--bg-secondary) !important; color: var(--text-primary) !important; border: 1px solid var(--border) !important; border-radius: 999px !important;
}
.stTextArea textarea { border-radius: 20px !important; }
.stDataFrame { background: var(--bg-secondary) !important; border: 1px solid var(--border-light) !important; border-radius: 20px !important; }
[data-testid="stSidebar"] { background: var(--bg-secondary) !important; border-right: 1px solid var(--border-light) !important; }
"""

_ANIM = """
<style>
@keyframes floatIn { from { opacity:0; transform: translateY(8px); } to { opacity:1; transform: none; } }
.animate-fade-in { animation: floatIn 400ms cubic-bezier(0.16,1,0.3,1); }
@media (prefers-reduced-motion: reduce) { *,*::before,*::after { animation: none !important; transition: none !important; } }
</style>
"""

def get_light_mode_css():
    return _LIGHT_TOKENS + _BASE_CSS + _ANIM

def get_dark_mode_css():
    return _DARK_TOKENS + _BASE_CSS + _ANIM

def metric_card(title, value, change="", icon="◯", color="primary"):
    tone = "" if color == "primary" else f"tone-{color}"
    change_html = f'<span class="badge badge-{color}">{change}</span>' if change else ""
    return f'''
    <div class="metric-card {tone} animate-fade-in">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <span class="metric-label">{title}</span><span style="font-size:18px">{icon}</span>
        </div>
        <div class="metric-value">{value}</div>{change_html}
    </div>'''

def status_badge(text, status="primary"):
    return f'<span class="badge badge-{status}">{text}</span>'

def gradient_text(text, color1="#111827", color2="#6B7280"):
    return f'<span style="font-weight:800; font-family:var(--font-display); color:var(--text-primary); font-size:1.15em">{text}</span>'

def render_theme():
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "dark"
    mode = st.session_state.theme_mode
    set_chart_mode(mode)
    css = get_dark_mode_css() if mode == "dark" else get_light_mode_css()
    st.markdown(css, unsafe_allow_html=True)

def get_theme_colors(mode="light"):
    return COLORS.get(mode, COLORS["light"])

def render_theme_switcher():
    c1,c2 = st.columns(2)
    with c1:
        if st.button("Light", use_container_width=True):
            st.session_state.theme_mode = "light"; st.rerun()
    with c2:
        if st.button("Dark", use_container_width=True):
            st.session_state.theme_mode = "dark"; st.rerun()
    st.caption(f"Mono — {st.session_state.theme_mode}")

def debug_theme_config():
    if st.checkbox("Debug Mono"):
        st.json(COLORS)
