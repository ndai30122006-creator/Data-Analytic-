"""
🎨 Theme Configuration — Learning Analytics

Single global stylesheet injected with st.markdown(unsafe_allow_html=True).

Design tokens (exact spec):
  * Font: Inter (Google Fonts), applied app-wide.
  * Background: #F8FAFC · Text: #1E293B
  * Sidebar: #1E293B background, white text.
  * st.metric: white card, soft shadow, 12px radius, 4px left border #2563EB.
  * Buttons: #2563EB background, white text, 8px radius, darker on hover.
  * Tabs: active #2563EB · inactive #94A3B8.
  * Dataframe: no vertical gridlines, larger padding, faded header.
"""

from typing import Any, Dict

import streamlit as st

from src.utils.config import set_chart_mode

# ═══════════════════════════════════════════════════════════
# COLOR PALETTE (semantic tokens, exported for get_theme_colors)
# ═══════════════════════════════════════════════════════════

COLORS = {
    "light": {
        "primary": "#2563EB",
        "primary_hover": "#1D4ED8",
        "primary_light": "#EFF6FF",
        "secondary": "#EC4899",
        "secondary_hover": "#DB2777",
        "success": "#10B981",
        "warning": "#F59E0B",
        "danger": "#EF4444",
        "info": "#06B6D4",
        "bg_primary": "#F8FAFC",
        "bg_secondary": "#FFFFFF",
        "bg_tertiary": "#F1F5F9",
        "bg_hover": "#EFF6FF",
        "text_primary": "#1E293B",
        "text_secondary": "#475569",
        "text_tertiary": "#64748B",
        "text_inverse": "#FFFFFF",
        "border": "#CBD5E1",
        "border_light": "#E2E8F0",
        "chart_bg": "#FFFFFF",
        "chart_grid": "#E2E8F0",
        "sidebar_bg": "#1E293B",
        "sidebar_text": "#FFFFFF",
    },
    "dark": {
        "primary": "#2563EB",
        "primary_hover": "#3B82F6",
        "primary_light": "#1E3A8A",
        "secondary": "#EC4899",
        "secondary_hover": "#DB2777",
        "success": "#10B981",
        "warning": "#F59E0B",
        "danger": "#EF4444",
        "info": "#06B6D4",
        "bg_primary": "#F8FAFC",
        "bg_secondary": "#FFFFFF",
        "bg_tertiary": "#F1F5F9",
        "bg_hover": "#EFF6FF",
        "text_primary": "#1E293B",
        "text_secondary": "#475569",
        "text_tertiary": "#64748B",
        "text_inverse": "#FFFFFF",
        "border": "#CBD5E1",
        "border_light": "#E2E8F0",
        "chart_bg": "#FFFFFF",
        "chart_grid": "#E2E8F0",
        "sidebar_bg": "#1E293B",
        "sidebar_text": "#FFFFFF",
    },
}

# ═══════════════════════════════════════════════════════════
# GLOBAL CSS  (single stylesheet for the whole app)
# ═══════════════════════════════════════════════════════════

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Design tokens ── */
:root {
    /* Brand */
    --primary: #2563EB;
    --primary-color: #2563EB;
    --primary-hover: #1D4ED8;
    --primary-soft: rgba(37, 99, 235, 0.12);
    --primary-glow: rgba(37, 99, 235, 0.28);
    --secondary: #EC4899;
    --accent: #06B6D4;
    --success: #10B981;
    --warning: #F59E0B;
    --danger: #EF4444;
    --info: #06B6D4;

    /* Surfaces */
    --bg: #F8FAFC;
    --bg-primary: #F8FAFC;
    --bg-secondary: #FFFFFF;
    --bg-tertiary: #F1F5F9;
    --bg-hover: #EFF6FF;
    --bg2: #FFFFFF;
    --bg3: #E2E8F0;

    /* Text */
    --text: #1E293B;
    --text-primary: #1E293B;
    --text-secondary: #475569;
    --text-tertiary: #64748B;
    --text2: #475569;
    --text3: #94A3B8;
    --text-inverse: #FFFFFF;
    --fg-muted: #64748B;

    /* Borders */
    --border: #CBD5E1;
    --border-light: #E2E8F0;
    --border2: #E2E8F0;

    /* Radius */
    --radius-sm: 6px;
    --radius-md: 8px;
    --radius: 12px;
    --radius-lg: 16px;
    --radius-xl: 24px;

    /* Shadows */
    --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.06);
    --shadow: 0 2px 8px rgba(15, 23, 42, 0.08), 0 1px 3px rgba(15, 23, 42, 0.05);
    --shadow-lg: 0 12px 32px rgba(15, 23, 42, 0.12);

    /* Motion */
    --ease: cubic-bezier(0.16, 1, 0.3, 1);
    --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
    --fast: 160ms ease;
    --smooth: 260ms ease;
    --transition: 160ms ease;

    /* Fonts */
    --font: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
    --font-mono: 'JetBrains Mono', 'SF Mono', 'Cascadia Code', Consolas, monospace;
    --font-display: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
    --font-size-small: 0.8rem;

    /* Alignment & components (compat tokens used by tabs) */
    --card: #FFFFFF;
    --card-padding: 20px 22px;
    --card-radius: 12px;
    --grid-gap: 12px;
    --ring: 0 0 0 3px rgba(37, 99, 235, 0.25);
    --accent-soft: rgba(6, 182, 212, 0.12);
}
/* ── Base ── */
* { font-family: var(--font) !important; }
html, body, .stApp {
    background-color: #F8FAFC;
    color: #1E293B;
    font-size: 15px;
}
h1, h2, h3, h4 { color: #1E293B; letter-spacing: -0.01em; }

/* Scrollbar */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #2563EB; }

/* ── Native metric cards (st.metric) ── */
[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border-radius: 12px;
    border-left: 4px solid #2563EB;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08), 0 1px 3px rgba(15, 23, 42, 0.05);
    padding: 16px 18px;
}
[data-testid="stMetricLabel"] { color: #64748B; font-size: 0.8rem; font-weight: 600; }
[data-testid="stMetricValue"] { color: #1E293B; font-weight: 700; font-family: var(--font-mono); }
[data-testid="stMetricDelta"] { color: #2563EB; }

/* ── Custom metric / KPI / feature cards (HTML components) ── */
.metric-card, .kpi-card, .feature-card, .panel {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-left: 4px solid #2563EB;
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
    transition: box-shadow var(--transition), transform var(--transition), border-color var(--transition);
}
.metric-card:hover, .kpi-card:hover, .feature-card:hover {
    box-shadow: 0 6px 20px rgba(15, 23, 42, 0.10);
    transform: translateY(-2px);
}
.metric-card .metric-label, .kpi-card .kpi-label {
    font-size: 0.78rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase;
    color: #64748B;
}
.metric-card .metric-value, .kpi-card .kpi-value {
    font-size: 1.6rem; font-weight: 700; color: #1E293B; font-family: var(--font-mono);
    line-height: 1.25; margin: 4px 0;
}
.metric-card .metric-meta { font-size: 0.82rem; color: #475569; }
.kpi-card .kpi-delta { font-size: 0.8rem; color: #2563EB; }
.metric-card.tone-primary, .feature-card.tone-primary  { border-left-color: #2563EB; }
.metric-card.tone-success, .feature-card.tone-success { border-left-color: #10B981; }
.metric-card.tone-warning, .feature-card.tone-warning { border-left-color: #F59E0B; }
.metric-card.tone-danger,  .feature-card.tone-danger  { border-left-color: #EF4444; }
.metric-card.tone-info,    .feature-card.tone-info    { border-left-color: #06B6D4; }
.metric-card.tone-accent, .feature-card.tone-accent { border-left-color: #06B6D4; }
.metric-card.tone-secondary, .feature-card.tone-secondary { border-left-color: #EC4899; }

/* ── Insight cards ── */
.insight-card {
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-left: 4px solid #06B6D4;
    border-radius: 10px;
    padding: 14px 16px;
    margin: 8px 0;
    font-size: 0.9rem;
    line-height: 1.5;
    color: #1E293B;
}
.insight-card strong { display: block; margin-bottom: 2px; color: #1E293B; }
.insight-card.insight-info    { border-left-color: #06B6D4; }
.insight-card.insight-success,
.insight-card.insight-good     { border-left-color: #10B981; }
.insight-card.insight-warning  { border-left-color: #F59E0B; }
.insight-card.insight-danger   { border-left-color: #EF4444; }

/* ── Badges ── */
.badge {
    display: inline-block; padding: 5px 12px;
    border-radius: 999px; font-size: 0.73rem; font-weight: 700; letter-spacing: 0.02em;
}
.badge-primary { background: rgba(37, 99, 235, 0.12); color: #2563EB; }
.badge-success { background: rgba(16, 185, 129, 0.12); color: #047857; }
.badge-warning { background: rgba(245, 158, 11, 0.14); color: #B45309; }
.badge-danger  { background: rgba(239, 68, 68, 0.12); color: #B91C1C; }
.badge-info    { background: rgba(6, 182, 212, 0.14); color: #0E7490; }
.badge-neutral { background: #F1F5F9; color: #475569; }

/* ── Hero / section headers ── */
.hero-bg {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
}
.hero h1 { color: #1E293B; }
.hero p  { color: #64748B; }

.text-gradient {
    background: linear-gradient(135deg, #2563EB, #EC4899);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.section-label {
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
    color: #64748B; margin: 0.6rem 0 0.3rem;
}
.cta-banner {
    background: linear-gradient(135deg, #2563EB, #1D4ED8);
    color: #FFFFFF;
    border-radius: 8px;
    padding: 12px 20px;
    text-align: center;
    font-weight: 600;
    box-shadow: 0 4px 16px rgba(37, 99, 235, 0.28);
}

/* Spacing utilities */
.sp-xs { height: 4px; } .sp-sm { height: 8px; }
.sp-md { height: 16px; } .sp-lg { height: 24px; } .sp-xl { height: 40px; }
/* ── Buttons ── */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button,
[data-testid="stButton"] button, [data-testid="stDownloadButton"] button {
    background-color: #2563EB;
    color: #FFFFFF !important;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.9rem;
    padding: 0.55rem 1.25rem;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
    transition: background-color var(--fast), box-shadow var(--fast), transform var(--fast);
}
.stButton > button:hover, .stDownloadButton > button:hover,
[data-testid="stButton"] button:hover, [data-testid="stDownloadButton"] button:hover {
    background-color: #1D4ED8;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.32);
    transform: translateY(-1px);
}
.stButton > button:active, .stDownloadButton > button:active {
    background-color: #1E40AF;
    transform: translateY(0);
}
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible {
    outline: 3px solid rgba(37, 99, 235, 0.4);
    outline-offset: 2px;
}
.stButton > button:disabled, .stDownloadButton > button:disabled {
    background-color: #94A3B8;
    cursor: not-allowed;
}

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] { gap: 4px; }
[data-testid="stTabs"] [data-baseweb="tab"],
[data-testid="stTabs"] [role="tab"] {
    color: #94A3B8 !important;
    font-weight: 600;
    font-size: 0.88rem;
    padding: 0.5rem 1rem;
    border-radius: 8px 8px 0 0;
    transition: color var(--fast), background-color var(--fast);
}
[data-testid="stTabs"] [data-baseweb="tab"]:hover,
[data-testid="stTabs"] [role="tab"]:hover { color: #2563EB !important; }
[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"],
[data-testid="stTabs"] [role="tab"][aria-selected="true"] { color: #2563EB !important; }
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color: #2563EB !important; }

/* ── Inputs (main area) ── */
.stTextInput input, .stNumberInput input, .stTextArea textarea,
.stSelectbox [data-baseweb="select"] > div, .stMultiSelect [data-baseweb="select"] > div {
    background-color: #FFFFFF;
    color: #1E293B;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    font-size: 0.9rem;
}
.stTextInput input:focus, .stTextArea textarea:focus,
.stSelectbox [data-baseweb="select"] > div:focus-within,
.stMultiSelect [data-baseweb="select"] > div:focus-within {
    border-color: #2563EB;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
}

/* ── Slider ── */
.stSlider [data-baseweb="slider"] [role="slider"] {
    background-color: #2563EB;
    border: 2px solid #FFFFFF;
    box-shadow: 0 0 0 1px #2563EB;
}

/* ── Dataframe (st.dataframe) ──
   Glide Data Grid v8 CSS variables:
   --gdg-border-color transparent -> bỏ đường kẻ (dọc)
   --gdg-bg-header / -has-focus   -> làm mờ header
   --gdg-bg-cell                  -> nền ô trắng          */
[data-testid="stDataFrame"] {
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
    padding: 6px 0;
}
[data-testid="stDataFrameResizable"] { padding: 6px 0; }
[data-testid="stDataFrame"] div[class*="gdg-"],
[data-testid="stDataFrameResizable"] div[class*="gdg-"] {
    --gdg-border-color: transparent !important;
    --gdg-bg-header: #F1F5F9 !important;
    --gdg-bg-header-has-focus: #F1F5F9 !important;
    --gdg-bg-cell: #FFFFFF !important;
}
[data-testid="stDataFrame"] .dvn-scroller,
[data-testid="stDataFrameResizable"] .dvn-scroller { padding: 4px; }

/* ── Alerts ── */
.stAlert { border-radius: 10px; border-left-width: 4px; }
.stSuccess { border-left-color: #10B981; }
.stWarning { border-left-color: #F59E0B; }
.stError   { border-left-color: #EF4444; }
.stInfo    { border-left-color: #06B6D4; }

/* ── Expander ── */
.streamlit-expanderHeader { font-weight: 600; color: #1E293B; border-radius: 8px; }
.streamlit-expander { border: 1px solid #E2E8F0; border-radius: 10px; }

/* Code */
.stCode { border-radius: 10px; border: 1px solid #E2E8F0; }
/* ═══════════════════════════════════════════════════════════
   SIDEBAR — nền #1E293B, chữ trắng
   ═══════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background-color: #1E293B !important;
    color: #FFFFFF;
    border-right: 1px solid #334155;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] strong,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] a,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] caption { color: #FFFFFF; }
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: #CBD5E1; }
[data-testid="stSidebar"] a:hover { color: #93C5FD; }
[data-testid="stSidebar"] hr { border-color: #334155; }

/* Sidebar inputs: nền tối + chữ trắng */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #0F172A !important;
    color: #FFFFFF !important;
    border: 1px solid #475569 !important;
    border-radius: 8px;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div * { color: #FFFFFF !important; }
[data-testid="stSidebar"] [data-baseweb="select"] > div:hover { border-color: #2563EB !important; }

/* Sidebar file uploader */
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"],
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] {
    background-color: #0F172A;
    border: 1px dashed #475569;
    border-radius: 8px;
    color: #FFFFFF;
}

/* Sidebar metrics (st.metric) */
[data-testid="stSidebar"] [data-testid="stMetric"] {
    background-color: #0F172A !important;
    border-left-color: #2563EB;
    border-radius: 10px;
}
[data-testid="stSidebar"] [data-testid="stMetricLabel"] { color: #94A3B8 !important; }
[data-testid="stSidebar"] [data-testid="stMetricValue"] { color: #FFFFFF !important; }

/* Sidebar expander */
[data-testid="stSidebar"] .streamlit-expanderHeader { color: #FFFFFF; }
[data-testid="stSidebar"] .streamlit-expander { border-color: #334155; }

/* ═══════════════════════════════════════════════════════════
   ANIMATIONS — gentle, reduced-motion aware
   ═══════════════════════════════════════════════════════════ */
@keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
.animate-fade-in { animation: fadeIn 320ms ease-out; }
.animate-slide-in { animation: fadeIn 320ms ease-out; }
.animate-tilt { animation: fadeIn 320ms ease-out; }

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.001ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.001ms !important;
        scroll-behavior: auto !important;
    }
    .animate-fade-in, .animate-slide-in, .animate-tilt { animation: none !important; }
}
</style>
"""
# ═══════════════════════════════════════════════════════════
# LUCIDE ICON HELPER  (kept for compatibility with landing/overview tabs)
# ═══════════════════════════════════════════════════════════

_LUCIDE_ICONS = {
    "chart": '<svg class="lucide-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 16l4-4 4 4 4-6"/></svg>',
    "graduation": '<svg class="lucide-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><path d="M12 10L2 7l10-5 10 5-10 3z"/><path d="M6 12v4c0 1.1.9 2 2 2h8a2 2 0 002-2v-4"/><path d="M22 10v6"/></svg>',
    "users": '<svg class="lucide-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>',
    "trending": '<svg class="lucide-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>',
    "database": '<svg class="lucide-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
    "check": '<svg class="lucide-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><polyline points="20 6 9 17 4 12"/></svg>',
    "alert": '<svg class="lucide-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
}


def icon(name: str = "chart", size: str = "") -> str:
    """Return an inline Lucide SVG icon (compat helper for landing/overview)."""
    svg = _LUCIDE_ICONS.get(name, _LUCIDE_ICONS["chart"])
    if size:
        svg = svg.replace('class="lucide-icon"', f'class="lucide-icon lucide-icon-{size}"')
    return svg


# ═══════════════════════════════════════════════════════════
# PUBLIC API — keep function names used across the app
# ═══════════════════════════════════════════════════════════


def get_light_mode_css() -> str:
    """Return the global CSS stylesheet."""
    return _CSS


def get_dark_mode_css() -> str:
    """Return the global CSS stylesheet (single light design per spec)."""
    return _CSS


def metric_card(title: str, value: str, change: str = "", icon: str = "📊", color: str = "primary") -> str:
    """Return an HTML metric card component."""
    tone = "" if color in ("primary", "neutral") else f"tone-{color}"
    change_html = ""
    if change:
        cls = "badge-success" if "↑" in change else ("badge-danger" if "↓" in change else "badge-neutral")
        change_html = f'<span class="badge {cls}">{change}</span>'
    return f"""
    <div class="metric-card {tone} animate-fade-in">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <span class="metric-label">{title}</span>
            <span style="font-size:20px;line-height:1">{icon}</span>
        </div>
        <div class="metric-value">{value}</div>
        {change_html}
    </div>
    """


def status_badge(text: str, status: str = "primary") -> str:
    """Return an HTML badge span."""
    return f'<span class="badge badge-{status}">{text}</span>'


def gradient_text(text: str, color1: str = "#2563EB", color2: str = "#EC4899") -> str:
    """Return an HTML span with gradient text."""
    return f'<span class="text-gradient" style="font-weight:800;font-size:1.15em">{text}</span>'


def render_theme() -> None:
    """Inject the global theme CSS for the whole app.

    Keeps the old signature. A single light design is applied app-wide
    (the exact color spec), so both light/dark session values render the
    same stylesheet. Chart theme is locked to light for consistency.
    """
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "light"
    set_chart_mode("light")  # charts follow the single light design
    st.markdown(_CSS, unsafe_allow_html=True)


def get_theme_colors(mode: str = "light") -> Dict[str, str]:
    """Return semantic color tokens for the given mode."""
    return COLORS.get(mode, COLORS["light"])


def render_theme_switcher() -> None:
    """Light/Dark toggle (kept for API compatibility; single design)."""
    col1, col2 = st.columns(2)
    with col1:
        if st.button("☀️ Light", use_container_width=True, help="Switch to light mode"):
            st.session_state.theme_mode = "light"
            st.rerun()
    with col2:
        if st.button("🌙 Dark", use_container_width=True, help="Switch to dark mode"):
            st.session_state.theme_mode = "light"
            st.rerun()
    st.caption(f"Current: **Light Mode ☀️**")


def debug_theme_config() -> None:
    """Show theme tokens for debugging."""
    if st.checkbox("🔧 Debug: Show Theme Config"):
        st.json({"Light Mode": COLORS["light"]})


if __name__ == "__main__":
    st.set_page_config(page_title="Theme Preview", page_icon="🎨", layout="wide")
    render_theme()
    render_theme_switcher()
    st.title("🎨 Theme Preview — Learning Analytics")
    cols = st.columns(3)
    vals = [
        ("Total Users", "45,230", "↑ 12.5%", icon("users"), "primary"),
        ("Revenue", "$123K", "↑ 8.3%", icon("trending"), "success"),
        ("Conversion", "3.2%", "↓ 0.5%", icon("chart"), "danger"),
    ]
    for i, (t, v, c, ic, color) in enumerate(vals):
        with cols[i]:
            st.markdown(metric_card(t, v, c, ic, color=color), unsafe_allow_html=True)
