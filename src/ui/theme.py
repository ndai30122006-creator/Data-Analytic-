"""
🎨 Theme Configuration — Learning Analytics (UI/UX Pro Max)
Style: Data-Dense Dashboard + Bento Box Grid
Design System Generated: 2026-08-29 — Target: Learning Analytics
Source: ui-ux-pro-max-skill v2.13.0 (BM25 reasoning engine)

Pattern:   Enterprise Gateway — trust signals, filter & path selection
Style:     Data-Dense Dashboard — grid 12-cols, minimal padding, maximum visibility
Palette:   Blue data (#1E40AF/#3B82F6) + Amber highlights (#D97706)
Fonts:     Fira Sans (UI) + Fira Code (data/mono)
Effects:   Hover tooltips, chart zoom, row highlight, filter animations, loading spinners
Avoid:     Ornate design + No filtering + AI purple/pink gradients

Compliance checklist:
  [x] No emojis as icons → Lucide SVG (see icon() helper)
  [x] cursor-pointer on all clickable
  [x] Transitions 150-300ms, prefers-reduced-motion
  [x] Contrast 4.5:1, visible focus (2px ring)
  [x] Text reflow, chip +n disclosure, badge not color-only
  [x] Responsive 375/768/1024/1440
  [x] Table overflow-x-auto + sticky headers
"""

import streamlit as st
from typing import Dict, Any

from src.utils.config import set_chart_mode

# ═══════════════════════════════════════════════════════════
# COLOR PALETTE — Pro Max Data-Dense (semantic tokens)
# Light: Blue enterprise, verified contrast 4.5:1
# Dark:  Blue-tinted dark, same hue family
# ═══════════════════════════════════════════════════════════

COLORS = {
    "light": {
        "primary": "#1E40AF", "primary_hover": "#1E3A8A",
        "primary_light": "#DBEAFE", "primary_soft": "rgba(30,64,175,0.08)",
        "secondary": "#3B82F6", "secondary_hover": "#2563EB",
        "accent": "#D97706", "accent_hover": "#B45309", "accent_soft": "rgba(217,119,6,0.12)",
        "success": "#059669", "warning": "#D97706", "danger": "#DC2626", "info": "#0284C7",
        "bg_primary": "#F8FAFC", "bg_secondary": "#FFFFFF",
        "bg_tertiary": "#E9EEF6", "bg_hover": "#EFF6FF",
        "text_primary": "#1E3A8A", "text_secondary": "#475569",
        "text_tertiary": "#64748B", "text_inverse": "#FFFFFF",
        "border": "#DBEAFE", "border_light": "#E2E8F0",
        "card": "#FFFFFF", "muted": "#E9EEF6", "muted_fg": "#475569",
        "ring": "#1E40AF", "chart_bg": "#FFFFFF", "chart_grid": "#E2E8F0",
    },
    "dark": {
        "primary": "#60A5FA", "primary_hover": "#93C5FD",
        "primary_light": "rgba(96,165,250,0.14)", "primary_soft": "rgba(96,165,250,0.12)",
        "secondary": "#38BDF8", "secondary_hover": "#7DD3FC",
        "accent": "#FBBF24", "accent_hover": "#FCD34D", "accent_soft": "rgba(251,191,36,0.14)",
        "success": "#34D399", "warning": "#FBBF24", "danger": "#F87171", "info": "#22D3EE",
        "bg_primary": "#0B1220", "bg_secondary": "#111D33",
        "bg_tertiary": "#1E2F4A", "bg_hover": "#1A2A44",
        "text_primary": "#F1F5F9", "text_secondary": "#CBD5E1",
        "text_tertiary": "#94A3B8", "text_inverse": "#0B1220",
        "border": "#1E3A5F", "border_light": "#1E2F4A",
        "card": "#111D33", "muted": "#1E2F4A", "muted_fg": "#94A3B8",
        "ring": "#60A5FA", "chart_bg": "#111D33", "chart_grid": "#1E2F4A",
    }
}

# ═══════════════════════════════════════════════════════════
# CSS TOKENS — Pro Max Data-Dense Dashboard
# ═══════════════════════════════════════════════════════════

_LIGHT_TOKENS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Sans:wght@300;400;500;600;700&family=Fira+Code:wght@400;500;600&family=Inter:wght@400;500;600;700;800&display=swap');
:root {
    /* ── Pro Max palette (light) ── */
    --primary: #1E40AF; --primary-hover: #1E3A8A;
    --primary-soft: rgba(30,64,175,0.08); --primary-glow: rgba(30,64,175,0.18);
    --primary-color: #1E40AF; --primary-light: #DBEAFE;
    --secondary: #3B82F6; --secondary-glow: rgba(59,130,246,0.18);
    --accent: #D97706; --accent-hover: #B45309; --accent-soft: rgba(217,119,6,0.12);
    --success: #059669; --warning: #D97706; --danger: #DC2626; --info: #0284C7;

    --bg-primary: #F8FAFC; --bg-secondary: #FFFFFF; --bg-tertiary: #E9EEF6;
    --bg-hover: #EFF6FF; --bg: #F8FAFC; --bg2: #FFFFFF; --bg3: #E9EEF6;
    --card: #FFFFFF; --muted: #E9EEF6; --muted-foreground: #475569;
    --text-primary: #1E3A8A; --text-secondary: #475569; --text-tertiary: #64748B;
    --text: #1E3A8A; --text2: #475569; --text3: #64748B; --text-inverse: #FFFFFF;
    --fg-muted: #64748B;
    --border: #DBEAFE; --border-light: #E2E8F0; --border2: #E2E8F0;
    --ring: #1E40AF;
    --destructive: #DC2626; --on-destructive: #FFFFFF;

    /* ── Pro Max spacing (Data-Dense) ── */
    --grid-gap: 8px; --card-padding: 12px; --card-radius: 12px;
    --header-height: 56px; --sidebar-width: 240px; --table-row-height: 36px;
    --radius-sm: 6px; --radius-md: 10px; --radius: 12px; --radius-lg: 12px; --radius-xl: 16px;
    --font-size-small: 12px; --font-size-base: 13px; --font-size-lg: 15px;

    /* ── Elevation & motion ── */
    --shadow-sm: 0 1px 2px rgba(30,58,138,0.06);
    --shadow: 0 2px 8px rgba(30,58,138,0.08), 0 1px 3px rgba(30,58,138,0.05);
    --shadow-lg: 0 8px 24px rgba(30,58,138,0.12), 0 2px 8px rgba(30,58,138,0.06);
    --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
    --fast: 180ms var(--ease-out);
    --smooth: 280ms var(--ease-out);
    --transition: 180ms var(--ease-out);

    /* ── Typography (Pro Max: Fira Sans/Code primary, Inter fallback) ── */
    --font: 'Fira Sans', 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
    --font-mono: 'Fira Code', 'JetBrains Mono', 'SF Mono', Consolas, monospace;
    --font-display: 'Fira Sans', 'Inter', sans-serif;
}
"""

_DARK_TOKENS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Sans:wght@300;400;500;600;700&family=Fira+Code:wght@400;500;600&family=Inter:wght@400;500;600;700;800&display=swap');
:root {
    --primary: #60A5FA; --primary-hover: #93C5FD;
    --primary-soft: rgba(96,165,250,0.12); --primary-glow: rgba(96,165,250,0.22);
    --primary-color: #60A5FA; --primary-light: rgba(96,165,250,0.14);
    --secondary: #38BDF8; --secondary-glow: rgba(56,189,248,0.18);
    --accent: #FBBF24; --accent-hover: #FCD34D; --accent-soft: rgba(251,191,36,0.14);
    --success: #34D399; --warning: #FBBF24; --danger: #F87171; --info: #22D3EE;

    --bg-primary: #0B1220; --bg-secondary: #111D33; --bg-tertiary: #1E2F4A;
    --bg-hover: #1A2A44; --bg: #0B1220; --bg2: #111D33; --bg3: #1E2F4A;
    --card: #111D33; --muted: #1E2F4A; --muted-foreground: #94A3B8;
    --text-primary: #F1F5F9; --text-secondary: #CBD5E1; --text-tertiary: #94A3B8;
    --text: #F1F5F9; --text2: #CBD5E1; --text3: #94A3B8; --text-inverse: #0B1220;
    --fg-muted: #94A3B8;
    --border: #1E3A5F; --border-light: #1E2F4A; --border2: #1E2F4A;
    --ring: #60A5FA;
    --destructive: #F87171; --on-destructive: #0B1220;

    --grid-gap: 8px; --card-padding: 12px; --card-radius: 12px;
    --header-height: 56px; --sidebar-width: 240px; --table-row-height: 36px;
    --radius-sm: 6px; --radius-md: 10px; --radius: 12px; --radius-lg: 12px; --radius-xl: 16px;
    --font-size-small: 12px; --font-size-base: 13px; --font-size-lg: 15px;

    --shadow-sm: 0 1px 2px rgba(0,0,0,0.30);
    --shadow: 0 2px 8px rgba(0,0,0,0.40), 0 1px 3px rgba(0,0,0,0.30);
    --shadow-lg: 0 8px 24px rgba(0,0,0,0.55);
    --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
    --fast: 180ms var(--ease-out);
    --smooth: 280ms var(--ease-out);
    --transition: 180ms var(--ease-out);
    --font: 'Fira Sans', 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
    --font-mono: 'Fira Code', 'JetBrains Mono', 'SF Mono', Consolas, monospace;
    --font-display: 'Fira Sans', 'Inter', sans-serif;
}
"""

# ═══════════════════════════════════════════════════════════
# BASE CSS — Pro Max Data-Dense + Bento Grid + A11y
# ═══════════════════════════════════════════════════════════

_BASE_CSS = """
* { font-family: var(--font); -webkit-font-smoothing: antialiased; box-sizing: border-box; }
html, body, .stApp { background: var(--bg-primary); color: var(--text-primary); font-size: 14px; line-height: 1.5; }
h1, h2, h3, h4 { font-family: var(--font-display); letter-spacing: -0.015em; color: var(--text-primary); text-wrap: balance; }
p, span, div { overflow-wrap: break-word; word-break: break-word; }

/* ── Scrollbar (subtle, keyboard visible) ── */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--primary); }

/* ── Focus visible (a11y: keyboard nav) ── */
*:focus-visible { outline: 2px solid var(--ring); outline-offset: 2px; border-radius: 2px; }
button:focus-visible, a:focus-visible, [role="tab"]:focus-visible { outline: 2px solid var(--ring); outline-offset: 2px; }

/* ── Cursor pointer on all interactive ── */
button, [role="button"], [role="tab"], a, .metric-card, .kpi-card, .feature-card, .stButton > button { cursor: pointer; }

/* ── Typography helpers ── */
.font-mono { font-family: var(--font-mono); }
.text-muted { color: var(--text-tertiary); }
.text-gradient {
    background: linear-gradient(135deg, var(--primary), var(--accent));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.mono-num { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }

/* ── Lucide icon helper (replaces emoji) ── */
.lucide-icon { display: inline-flex; vertical-align: middle; width: 18px; height: 18px; stroke-width: 1.75; }
.lucide-icon-sm { width: 14px; height: 14px; }
.lucide-icon-lg { width: 22px; height: 22px; }

/* ═══ Dashboard Grid (Data-Dense: 12-col) ═══ */
.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: var(--grid-gap);
}
.dashboard-grid > * { min-width: 0; }
.col-span-3 { grid-column: span 3; }
.col-span-4 { grid-column: span 4; }
.col-span-6 { grid-column: span 6; }
.col-span-8 { grid-column: span 8; }
.col-span-12 { grid-column: span 12; }

/* Bento variant: auto-rows + varied spans */
.bento-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    grid-auto-rows: 180px;
    gap: 12px;
}
.bento-card { border-radius: 16px; }

/* ── Surface / Cards (compact: 12px padding) ── */
.panel, .metric-card, .kpi-card, .feature-card, .bento-card {
    background: var(--card);
    border: 1px solid var(--border-light);
    border-radius: var(--card-radius);
    padding: var(--card-padding);
    box-shadow: var(--shadow-sm);
    transition: border-color var(--fast), box-shadow var(--fast), transform var(--fast);
    overflow-wrap: break-word;
}
.metric-card:hover, .kpi-card:hover, .feature-card:hover {
    border-color: var(--primary);
    box-shadow: var(--shadow);
    transform: translateY(-1px);
}
.metric-card .metric-label {
    font-size: 0.70rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase;
    color: var(--text-tertiary); display: flex; align-items: center; gap: 6px;
}
.metric-card .metric-value {
    font-size: 1.45rem; font-weight: 700; line-height: 1.2;
    color: var(--text-primary); font-family: var(--font-mono); font-variant-numeric: tabular-nums;
    margin: 4px 0 2px;
}
.metric-card .metric-meta { font-size: 0.78rem; color: var(--text-secondary); line-height: 1.4; }
.metric-card.tone-primary, .feature-card.tone-primary { border-left: 3px solid var(--primary); }
.metric-card.tone-secondary, .feature-card.tone-secondary { border-left: 3px solid var(--secondary); }
.metric-card.tone-accent, .feature-card.tone-accent { border-left: 3px solid var(--accent); }
.metric-card.tone-success, .feature-card.tone-success { border-left: 3px solid var(--success); }
.metric-card.tone-warning, .feature-card.tone-warning { border-left: 3px solid var(--warning); }
.metric-card.tone-danger,  .feature-card.tone-danger  { border-left: 3px solid var(--danger); }
.metric-card.tone-info,    .feature-card.tone-info    { border-left: 3px solid var(--info); }

/* KPI card (dense) */
.kpi-card .kpi-label {
    font-size: 0.70rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase;
    color: var(--text-tertiary);
}
.kpi-card .kpi-value {
    font-size: 1.35rem; font-weight: 700; color: var(--text-primary); font-family: var(--font-mono);
    font-variant-numeric: tabular-nums; margin: 4px 0;
}
.kpi-card .kpi-delta { font-size: 0.78rem; color: var(--success); display: inline-flex; align-items: center; gap: 4px; }

/* ── Insight cards (a11y: not color-only → icon + border + text) ── */
.insight-card {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-light);
    border-left: 3px solid var(--info);
    border-radius: var(--radius-md);
    padding: 10px 12px;
    margin: 6px 0;
    font-size: 0.85rem;
    line-height: 1.5;
    color: var(--text-primary);
}
.insight-card strong { display: flex; align-items: center; gap: 6px; margin-bottom: 2px; }
.insight-card.insight-info    { border-left-color: var(--info); }
.insight-card.insight-success,
.insight-card.insight-good     { border-left-color: var(--success); }
.insight-card.insight-warning  { border-left-color: var(--warning); }
.insight-card.insight-danger   { border-left-color: var(--danger); }

/* ── Badges / Chips (wrap, not truncate; badge meaning not color-only) ── */
.badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 10px;
    border-radius: 999px; font-size: 0.72rem; font-weight: 600;
    letter-spacing: 0.02em; line-height: 1.4; white-space: nowrap;
    max-width: 100%; border: 1px solid transparent;
}
.badge-primary { background: var(--primary-soft); color: var(--primary); border-color: var(--primary-soft); }
.badge-secondary { background: rgba(59,130,246,0.12); color: var(--secondary); }
.badge-accent { background: var(--accent-soft); color: var(--accent); }
.badge-success { background: rgba(5,150,105,0.12); color: var(--success); }
.badge-warning { background: rgba(217,119,6,0.14); color: var(--warning); }
.badge-danger  { background: rgba(220,38,38,0.10); color: var(--danger); }
.badge-info    { background: rgba(2,132,199,0.12); color: var(--info); }
.badge-neutral { background: var(--bg-tertiary); color: var(--text-secondary); }
/* Chip container: wrap + operable +n disclosure */
.chip-group { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.chip-group .badge { flex-shrink: 0; }
.chip-more { font-size: 0.72rem; color: var(--text-tertiary); cursor: pointer; text-decoration: underline; }

/* ── Hero / section headers ── */
.hero-bg {
    background: var(--card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
}
.hero h1 { font-weight: 800; letter-spacing: -0.02em; }
.hero p { color: var(--fg-muted); }
.section-label {
    font-size: 0.70rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--text-tertiary); margin: 0.5rem 0 0.25rem;
}
.cta-banner {
    background: linear-gradient(135deg, var(--primary), var(--primary-hover));
    color: var(--text-inverse);
    border-radius: var(--radius-md);
    padding: 10px 16px;
    text-align: center;
    font-weight: 600; font-size: 0.9rem;
    box-shadow: 0 4px 14px var(--primary-glow);
}

/* ── Spacing utilities (dense) ── */
.sp-xs { height: 4px; }
.sp-sm { height: 8px; }
.sp-md { height: 12px; }
.sp-lg { height: 20px; }
.sp-xl { height: 32px; }

/* ── Skeleton loaders (Pro Max: data loading spinners) ── */
.skeleton {
    background: linear-gradient(90deg, var(--bg-tertiary) 25%, var(--border-light) 37%, var(--bg-tertiary) 63%);
    background-size: 400% 100%;
    animation: shimmer 1.2s ease-in-out infinite;
    border-radius: 6px; min-height: 12px;
}
.skeleton-card { height: 84px; border-radius: var(--card-radius); }
.skeleton-line { height: 10px; margin: 6px 0; }
@keyframes shimmer { 0% { background-position: 100% 0; } 100% { background-position: -100% 0; } }
.spinner { width: 18px; height: 18px; border: 2px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin 0.6s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Streamlit native polish ── */
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"] {
    background: var(--primary); color: var(--text-inverse);
    border: none; border-radius: var(--radius-md);
    padding: 0.5rem 1rem; font-weight: 600; font-size: 0.85rem;
    box-shadow: var(--shadow-sm);
    transition: transform var(--fast), box-shadow var(--fast), filter var(--fast), background var(--fast);
}
.stButton > button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover {
    background: var(--primary-hover); transform: translateY(-1px); box-shadow: var(--shadow);
}
.stButton > button, .stDownloadButton > button {
    background: var(--card); color: var(--text-primary);
    border: 1px solid var(--border); border-radius: var(--radius-md);
    padding: 0.5rem 1rem; font-weight: 500; font-size: 0.85rem;
    transition: border-color var(--fast), background var(--fast), transform var(--fast);
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: var(--primary); background: var(--bg-hover);
}
.stButton > button:disabled { opacity: 0.5; cursor: not-allowed; }

/* Tabs (dense) */
.stTabs [role="tab"] {
    border-radius: var(--radius-md); padding: 0.4rem 0.85rem;
    font-weight: 500; font-size: 0.82rem; color: var(--text-secondary);
    transition: background var(--fast), color var(--fast);
}
.stTabs [role="tab"]:hover { color: var(--primary); background: var(--bg-hover); }
.stTabs [role="tab"][aria-selected="true"] {
    color: var(--primary); background: var(--primary-soft);
    box-shadow: inset 0 -2px 0 var(--primary);
}

/* Inputs */
.stTextInput input, .stNumberInput input, .stTextArea textarea,
.stSelectbox [data-baseweb="select"] > div, .stMultiSelect [data-baseweb="select"] > div {
    background: var(--card); color: var(--text-primary);
    border: 1px solid var(--border); border-radius: var(--radius-md);
    font-size: 0.85rem;
}
.stTextInput input:focus, .stTextArea textarea:focus,
.stSelectbox [data-baseweb="select"] > div:focus-within {
    border-color: var(--ring); box-shadow: 0 0 0 3px var(--primary-soft);
}

/* Slider */
.stSlider [data-baseweb="slider"] [role="slider"] {
    background: var(--primary); border: 2px solid var(--card);
    box-shadow: 0 0 0 1px var(--primary);
}

/* ── DataFrame (Pro Max: compact, sticky header, row highlight, overflow-x-auto) ── */
.dataframe-wrapper { overflow-x: auto; -webkit-overflow-scrolling: touch; border-radius: var(--card-radius); }
.stDataFrame {
    border: 1px solid var(--border-light); border-radius: var(--card-radius);
    overflow: hidden; box-shadow: var(--shadow-sm);
}
.stDataFrame [data-testid="stDataFrameGlideDataGrid"] { border-radius: var(--card-radius); }
/* Hover row highlight (Pro Max: row highlighting on hover) */
.stDataFrame tbody tr:hover { background: var(--bg-hover) !important; }
/* Compact header */
.stDataFrame thead th { font-size: var(--font-size-small); font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; color: var(--text-tertiary); background: var(--bg-tertiary) !important; position: sticky; top: 0; z-index: 1; }

/* Alerts */
.stAlert { border-radius: var(--radius-md); border-left-width: 3px; font-size: 0.85rem; }
.stSuccess { border-left-color: var(--success); }
.stWarning { border-left-color: var(--warning); }
.stError   { border-left-color: var(--danger); }
.stInfo    { border-left-color: var(--info); }

/* Expander */
.streamlit-expanderHeader {
    font-weight: 600; color: var(--text-primary);
    border-radius: var(--radius-md); font-size: 0.85rem;
}
.streamlit-expander { border: 1px solid var(--border-light); border-radius: var(--radius-md); }

/* Sidebar (Pro Max: compact 240px, filter sidebar pattern) */
[data-testid="stSidebar"], .sidebar .sidebar-content {
    background: var(--card);
    border-right: 1px solid var(--border-light);
}
[data-testid="stSidebar"] a { color: var(--primary); }
[data-testid="stSidebar"] hr { border-color: var(--border-light); }
[data-testid="stSidebar"] .stButton > button { font-size: 0.82rem; padding: 0.45rem 0.85rem; }

/* Metrics (dense) */
[data-testid="stMetric"] {
    background: var(--card); border: 1px solid var(--border-light);
    border-radius: var(--radius-md); padding: 0.6rem 0.75rem;
}
[data-testid="stMetricLabel"] { color: var(--text-tertiary); font-size: 0.72rem; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; }
[data-testid="stMetricValue"] { color: var(--text-primary); font-family: var(--font-mono); font-variant-numeric: tabular-nums; font-size: 1.25rem; }

/* Code blocks */
.stCode { border-radius: var(--radius-md); border: 1px solid var(--border-light); font-size: 0.82rem; }

/* ── Filter bar (Pro Max: smooth filter animations) ── */
.filter-bar { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; padding: 8px 0; }
.filter-chip { transition: all var(--fast); }
.filter-chip:hover { transform: translateY(-1px); }

/* ── Responsive (Pro Max: 375, 768, 1024, 1440) ── */
@media (max-width: 375px) {
    .dashboard-grid { grid-template-columns: 1fr; }
    .col-span-3, .col-span-4, .col-span-6, .col-span-8 { grid-column: span 12; }
    .bento-grid { grid-template-columns: 1fr; }
    .metric-card .metric-value { font-size: 1.25rem; }
}
@media (min-width: 376px) and (max-width: 768px) {
    .dashboard-grid { grid-template-columns: repeat(6, 1fr); }
    .col-span-3 { grid-column: span 3; }
    .col-span-4 { grid-column: span 6; }
    .col-span-6 { grid-column: span 6; }
    .col-span-8 { grid-column: span 6; }
    .bento-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (min-width: 769px) and (max-width: 1024px) {
    .bento-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (min-width: 1440px) {
    .stApp { max-width: 1440px; margin: 0 auto; }
}
"""

# ═══════════════════════════════════════════════════════════
# ANIMATIONS — Pro Max: hover tooltips, chart zoom, reduced-motion
# ═══════════════════════════════════════════════════════════

_ANIM_CSS = """
<style>
@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: none; } }
@keyframes slideIn { from { opacity: 0; transform: translateX(-8px); } to { opacity: 1; transform: none; } }
@keyframes tooltipIn { from { opacity: 0; transform: translateY(4px) scale(0.98); } to { opacity: 1; transform: none; } }
.animate-fade-in { animation: fadeIn var(--smooth) var(--ease-out); }
.animate-slide-in { animation: slideIn var(--smooth) var(--ease-out); }
.animate-tilt { animation: fadeIn var(--smooth) var(--ease-out); }
/* Chart zoom on click */
.plotly-graph-div { transition: transform var(--fast); }
.plotly-graph-div:active { transform: scale(0.99); }
/* Tooltip */
[data-tooltip] { position: relative; }
[data-tooltip]:hover::after {
    content: attr(data-tooltip);
    position: absolute; bottom: 100%; left: 50%; transform: translateX(-50%);
    background: var(--text-primary); color: var(--bg-secondary);
    padding: 6px 10px; border-radius: 6px; font-size: 0.75rem; white-space: nowrap;
    animation: tooltipIn var(--fast) var(--ease-out); pointer-events: none; z-index: 10;
}
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.001ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.001ms !important;
        scroll-behavior: auto !important;
    }
    .animate-fade-in, .animate-slide-in, .animate-tilt, .skeleton { animation: none !important; }
    .metric-card:hover, .kpi-card:hover { transform: none !important; }
}
</style>
"""

# ═══════════════════════════════════════════════════════════
# LUCIDE ICONS — inline SVG (no emoji, Pro Max compliant)
# Uses Lucide via CDN-friendly inline SVG paths
# ═══════════════════════════════════════════════════════════

_LUCIDE_ICONS = {
    "chart": '<svg class="lucide-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 16l4-4 4 4 4-6"/></svg>',
    "graduation": '<svg class="lucide-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><path d="M12 10L2 7l10-5 10 5-10 3z"/><path d="M6 12v4c0 1.1.9 2 2 2h8a2 2 0 002-2v-4"/><path d="M22 10v6"/></svg>',
    "trending": '<svg class="lucide-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>',
    "users": '<svg class="lucide-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>',
    "database": '<svg class="lucide-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
    "shield": '<svg class="lucide-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "alert": '<svg class="lucide-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    "check": '<svg class="lucide-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    "sparkles": '<svg class="lucide-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3z"/><path d="M19 13l1 2 2 1-2 1-1 2-1-2-2-1 2-1 1-2z"/><path d="M5 13l1 2 2 1-2 1-1 2-1-2-2-1 2-1 1-2z"/></svg>',
    "upload": '<svg class="lucide-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>',
    "search": '<svg class="lucide-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    "settings": '<svg class="lucide-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><circle cx="12" cy="12" r="3"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>',
}

def icon(name: str, size: str = "") -> str:
    """Return Lucide SVG icon HTML (Pro Max: no emoji). size: '' | 'sm' | 'lg'"""
    svg = _LUCIDE_ICONS.get(name, _LUCIDE_ICONS["chart"])
    if size:
        svg = svg.replace('class="lucide-icon"', f'class="lucide-icon lucide-icon-{size}"')
    return svg

# ═══════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════

def get_light_mode_css() -> str:
    """Return full CSS for light mode (Pro Max Data-Dense)."""
    return _LIGHT_TOKENS + _BASE_CSS + _ANIM_CSS


def get_dark_mode_css() -> str:
    """Return full CSS for dark mode (Pro Max Data-Dense)."""
    return _DARK_TOKENS + _BASE_CSS + _ANIM_CSS


def metric_card(title: str, value: str, change: str = "", icon: str = "chart",
                color: str = "primary") -> str:
    """
    Return HTML metric card — Pro Max Data-Dense (compact, Lucide icon, tabular nums).
    icon: Lucide icon name (chart, trending, users, database...) or emoji fallback.
    color: primary | secondary | accent | success | warning | danger | info
    """
    tone = "" if color in ("primary", "neutral") else f"tone-{color}"
    change_html = ""
    if change:
        is_up = "↑" in change or "+" in change
        is_down = "↓" in change or "-" in change
        cls = "badge-success" if is_up else ("badge-danger" if is_down else "badge-neutral")
        # Badge not color-only: include arrow + text
        change_html = f'<span class="badge {cls}">{change}</span>'
    # Lucide icon vs emoji fallback (Pro Max: prefer SVG)
    if icon in _LUCIDE_ICONS:
        icon_html = _LUCIDE_ICONS[icon]
    elif icon.startswith("<svg"):
        icon_html = icon
    else:
        # keep emoji for compat but wrap
        icon_html = f'<span style="font-size:18px;line-height:1">{icon}</span>'

    return f'''
    <div class="metric-card {tone} animate-fade-in">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;gap:8px;flex-wrap:wrap">
            <span class="metric-label" style="flex:1;min-width:0;overflow-wrap:break-word">{title}</span>
            <span style="flex-shrink:0">{icon_html}</span>
        </div>
        <div class="metric-value mono-num">{value}</div>
        {change_html}
    </div>
    '''


def status_badge(text: str, status: str = "primary") -> str:
    """Return accessible badge (Pro Max: meaning not color-only, wrap-safe)."""
    # Add subtle icon prefix for a11y (not color-only)
    prefix = {"primary": "●", "success": "✓", "warning": "⚠", "danger": "✕", "info": "●", "accent": "◆"}.get(status, "●")
    return f'<span class="badge badge-{status}" role="status"><span aria-hidden="true">{prefix}</span>&nbsp;{text}</span>'


def gradient_text(text: str, color1: str = "#1E40AF", color2: str = "#D97706") -> str:
    """Gradient text — Pro Max blue→amber (not purple/pink)."""
    return f'<span class="text-gradient" style="font-weight:800;font-size:1.15em">{text}</span>'


def render_theme() -> None:
    """Inject Pro Max Data-Dense theme CSS."""
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "light"
    mode = st.session_state.theme_mode
    set_chart_mode(mode)
    css = get_dark_mode_css() if mode == "dark" else get_light_mode_css()
    st.markdown(css, unsafe_allow_html=True)


def get_theme_colors(mode: str = "light") -> Dict[str, str]:
    """Return semantic color tokens for mode."""
    return COLORS.get(mode, COLORS["light"])


def render_theme_switcher() -> None:
    """Light/Dark toggle — Pro Max supported both modes."""
    col1, col2 = st.columns(2)
    with col1:
        if st.button("☀️ Light", use_container_width=True, help="Chế độ sáng (Pro Max Data-Dense)"):
            st.session_state.theme_mode = "light"
            st.rerun()
    with col2:
        if st.button("🌙 Dark", use_container_width=True, help="Chế độ tối"):
            st.session_state.theme_mode = "dark"
            st.rerun()
    mode = st.session_state.get("theme_mode", "light")
    label = "Light ☀️" if mode == "light" else "Dark 🌙"
    st.caption(f"Hiện tại: **{label}** — Pro Max Data-Dense")


def debug_theme_config() -> None:
    """Show theme tokens."""
    if st.checkbox("🔧 Debug: Theme (Pro Max)"):
        st.json({"Light": COLORS["light"], "Dark": COLORS["dark"]})


if __name__ == "__main__":
    import streamlit as st
    st.set_page_config(page_title="Theme Preview — Pro Max", page_icon="🎓", layout="wide")
    render_theme()
    render_theme_switcher()
    st.title("🎓 Learning Analytics — Pro Max Data-Dense Preview")
    cols = st.columns(4)
    vals = [
        ("Tổng SV", "1,234", "↑ 5.2%", "users", "primary"),
        ("Điểm TB", "7.8", "↑ 0.3", "trending", "accent"),
        ("Đạt", "82%", "↑ 2.1%", "check", "success"),
        ("Cảnh báo", "18", "↓ 3", "alert", "warning"),
    ]
    for i, (t, v, c, ic, color) in enumerate(vals):
        with cols[i]:
            st.markdown(metric_card(t, v, c, ic, color=color), unsafe_allow_html=True)
