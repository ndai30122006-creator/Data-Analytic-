"""
🎨 Theme Configuration — Ultra-fluid Modern Design System
Vibrant gradient morphing, glassmorphism, particles, 3D effects
"""

import streamlit as st
from typing import Dict, Any

# ═══════════════════════════════════════════════════════════════════════════════
# COLOR PALETTE
# ═══════════════════════════════════════════════════════════════════════════════

COLORS = {
    "light": {
        "primary": "#6366F1", "primary_hover": "#4F46E5",
        "primary_light": "#A5B4FC", "secondary": "#EC4899",
        "secondary_hover": "#DB2777", "success": "#10B981",
        "warning": "#F59E0B", "danger": "#EF4444", "info": "#06B6D4",
        "bg_primary": "#FAFBFC", "bg_secondary": "#F1F5F9",
        "bg_tertiary": "#E2E8F0", "bg_hover": "#F8FAFC",
        "text_primary": "#0F172A", "text_secondary": "#475569",
        "text_tertiary": "#94A3B8", "text_inverse": "#FFFFFF",
        "border": "#CBD5E1", "border_light": "#E2E8F0",
        "chart_bg": "#FFFFFF", "chart_grid": "#E2E8F0",
    },
    "dark": {
        "primary": "#818CF8", "primary_hover": "#A5B4FC",
        "primary_light": "rgba(129, 140, 248, 0.3)", "secondary": "#F472B6",
        "secondary_hover": "#F9A8D4", "success": "#34D399",
        "warning": "#FBBF24", "danger": "#F87171", "info": "#22D3EE",
        "bg_primary": "#080D1A", "bg_secondary": "#111827",
        "bg_tertiary": "#1F2937", "bg_hover": "#1A233A",
        "text_primary": "#F1F5F9", "text_secondary": "#CBD5E1",
        "text_tertiary": "#64748B", "text_inverse": "#080D1A",
        "border": "#334155", "border_light": "#1E293B",
        "chart_bg": "#111827", "chart_grid": "#1F2937",
    }
}


def get_light_mode_css() -> str:
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@200;300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;600;700&display=swap');

    :root {
        --primary: #6366F1; --primary-hover: #4F46E5;
        --primary-glow: rgba(99,102,241,0.3); --primary-soft: rgba(99,102,241,0.08);
        --secondary: #EC4899; --secondary-glow: rgba(236,72,153,0.25);
        --accent: #06B6D4; --accent-glow: rgba(6,182,212,0.2);
        --success: #10B981; --warning: #F59E0B; --danger: #EF4444;
        --bg: #FAFBFC; --bg2: #F1F5F9; --bg3: #E2E8F0;
        --text: #0F172A; --text2: #475569; --text3: #94A3B8;
        --border: #CBD5E1; --border2: #E2E8F0;
        --radius-sm: 10px; --radius: 18px; --radius-lg: 28px; --radius-xl: 36px;

        --shadow-sm: 0 1px 2px rgba(0,0,0,0.04);
        --shadow: 0 4px 16px rgba(0,0,0,0.06), 0 2px 4px rgba(0,0,0,0.03);
        --shadow-lg: 0 12px 40px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.04);
        --shadow-xl: 0 24px 60px rgba(0,0,0,0.1);
        --glow: 0 0 30px var(--primary-glow);

        --ease: cubic-bezier(0.34, 1.56, 0.64, 1);
        --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
        --ease-in-out: cubic-bezier(0.76, 0, 0.24, 1);
        --fast: 200ms var(--ease-out);
        --smooth: 400ms var(--ease-out);
        --slow: 800ms var(--ease-out);
        --morph: 1500ms var(--ease-in-out);
    }

    * { font-family: 'Nunito', 'Quicksand', -apple-system, sans-serif; -webkit-font-smoothing: antialiased; }
    body { background: var(--bg); color: var(--text); overflow-x: hidden; }

    /* ═══════════════════════════════════════════
       MORPHING AMBIENT BACKGROUND — Fluid & Alive
       ═══════════════════════════════════════════ */
    .stApp::before {
        content: ''; position: fixed; inset: 0; z-index: 0; pointer-events: none;
        background:
            radial-gradient(ellipse 70% 40% at 15% 20%, rgba(99,102,241,0.06) 0%, transparent 60%),
            radial-gradient(ellipse 50% 35% at 85% 80%, rgba(236,72,153,0.04) 0%, transparent 55%),
            radial-gradient(ellipse 40% 30% at 50% 50%, rgba(6,182,212,0.03) 0%, transparent 50%),
            radial-gradient(ellipse 60% 40% at 30% 70%, rgba(16,185,129,0.03) 0%, transparent 50%);
        animation: morphBg 25s var(--ease-in-out) infinite alternate;
    }
    @keyframes morphBg {
        0% { transform: scale(1) rotate(0deg); opacity: 0.7; }
        33% { transform: scale(1.05) rotate(1deg); opacity: 1; }
        66% { transform: scale(0.97) rotate(-0.5deg); opacity: 0.8; }
        100% { transform: scale(1.02) rotate(0.5deg); opacity: 0.9; }
    }

    /* ═══════════════════════════════════════════
       FLOATING GLASS ORBS — 3D Depth
       ═══════════════════════════════════════════ */
    .stApp::after {
        content: ''; position: fixed; z-index: 0; pointer-events: none;
        width: 600px; height: 600px;
        background: radial-gradient(circle at center, rgba(99,102,241,0.08), transparent 70%);
        border-radius: 50%;
        top: -200px; right: -200px;
        animation: floatOrb1 18s var(--ease-out) infinite alternate;
    }
    @keyframes floatOrb1 {
        0% { transform: translate(0,0) scale(1); opacity: 0.5; }
        50% { transform: translate(-100px,80px) scale(1.2); opacity: 0.8; }
        100% { transform: translate(-50px,150px) scale(0.9); opacity: 0.4; }
    }

    /* Second floating orb */
    .main > div:first-child::before {
        content: ''; position: fixed; z-index: 0; pointer-events: none;
        width: 400px; height: 400px;
        background: radial-gradient(circle at center, rgba(236,72,153,0.06), transparent 70%);
        border-radius: 50%;
        bottom: -100px; left: -100px;
        animation: floatOrb2 22s var(--ease-out) infinite alternate;
    }
    @keyframes floatOrb2 {
        0% { transform: translate(0,0) scale(1); opacity: 0.3; }
        50% { transform: translate(100px,-60px) scale(1.3); opacity: 0.7; }
        100% { transform: translate(60px,-120px) scale(0.8); opacity: 0.4; }
    }

    /* ═══════════════════════════════════════════
       GLASSMORPHISM SIDEBAR
       ═══════════════════════════════════════════ */
    .sidebar .sidebar-content {
        background: rgba(250,251,252,0.85) !important;
        backdrop-filter: blur(20px) saturate(1.3) !important;
        -webkit-backdrop-filter: blur(20px) saturate(1.3) !important;
        border-right: 1px solid rgba(203,213,225,0.4) !important;
        box-shadow: 4px 0 24px rgba(0,0,0,0.04) !important;
    }

    /* ═══════════════════════════════════════════
       3D PERSPECTIVE CARDS
       ═══════════════════════════════════════════ */
    .metric-card {
        background: rgba(255,255,255,0.7) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(203,213,225,0.3) !important;
        border-radius: var(--radius-lg) !important;
        padding: 24px !important;
        box-shadow: var(--shadow) !important;
        transition: all 0.4s var(--ease-out) !important;
        position: relative !important;
        overflow: hidden !important;
        transform-style: preserve-3d !important;
        perspective: 800px !important;
    }

    .metric-card::before {
        content: ''; position: absolute; inset: 0;
        background: linear-gradient(135deg,
            rgba(99,102,241,0.03) 0%, transparent 50%,
            rgba(236,72,153,0.02) 100%);
        opacity: 0; transition: opacity 0.5s var(--ease-out);
    }

    .metric-card::after {
        content: ''; position: absolute; top: 0; left: -100%;
        width: 300%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(99,102,241,0.04), transparent);
        animation: shimmer 3s ease-in-out infinite;
    }
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }

    .metric-card:hover {
        transform: translateY(-8px) scale(1.02) rotateX(2deg) !important;
        box-shadow: var(--shadow-xl), 0 0 40px var(--primary-glow) !important;
        border-color: var(--primary) !important;
    }
    .metric-card:hover::before { opacity: 1; }

    /* ═══════════════════════════════════════════
       FLUID BUTTONS
       ═══════════════════════════════════════════ */
    button[kind="primary"] {
        background: linear-gradient(135deg, var(--primary), #4F46E5) !important;
        color: white !important; border: none !important;
        border-radius: var(--radius) !important;
        padding: 12px 24px !important;
        font-weight: 600 !important; font-size: 14px !important;
        transition: all 0.3s var(--ease-out) !important;
        box-shadow: var(--shadow), 0 0 0 0 var(--primary-glow) !important;
        position: relative !important; overflow: hidden !important;
    }

    button[kind="primary"]::before {
        content: ''; position: absolute; inset: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
        transform: translateX(-100%);
        transition: transform 0.6s var(--ease-out);
    }
    button[kind="primary"]:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: var(--shadow-lg), 0 0 40px var(--primary-glow) !important;
    }
    button[kind="primary"]:hover::before { transform: translateX(100%); }
    button[kind="primary"]:active { transform: translateY(0) scale(0.98) !important; }

    button[kind="secondary"] {
        background: rgba(255,255,255,0.6) !important;
        backdrop-filter: blur(8px) !important;
        color: var(--text) !important;
        border: 1px solid rgba(203,213,225,0.4) !important;
        border-radius: var(--radius) !important;
        padding: 12px 20px !important;
        font-weight: 500 !important;
        transition: all 0.3s var(--ease-out) !important;
    }
    button[kind="secondary"]:hover {
        background: rgba(255,255,255,0.9) !important;
        border-color: var(--primary) !important;
        box-shadow: 0 0 20px var(--primary-glow) !important;
        transform: translateY(-2px) !important;
    }

    /* ═══════════════════════════════════════════
       MORPHING TABS
       ═══════════════════════════════════════════ */
    .stTabs { margin-bottom: 1.5rem !important; animation: fadeUp 0.6s var(--ease-out); }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.5) !important;
        backdrop-filter: blur(12px) !important;
        border-radius: 16px !important;
        padding: 4px !important; gap: 2px !important;
        border: 1px solid rgba(203,213,225,0.3) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stTabs [role="tab"] {
        border-radius: 12px !important;
        padding: 10px 20px !important;
        font-weight: 500 !important; font-size: 0.88rem !important;
        color: var(--text2) !important;
        background: transparent !important;
        border: none !important;
        transition: all 0.3s var(--ease-out) !important;
    }
    .stTabs [role="tab"]:hover {
        color: var(--primary) !important;
        background: rgba(99,102,241,0.06) !important;
        transform: translateY(-2px);
    }
    .stTabs [role="tab"][aria-selected="true"] {
        color: #fff !important;
        background: linear-gradient(135deg, var(--primary), #4F46E5) !important;
        box-shadow: 0 4px 20px var(--primary-glow) !important;
        transform: translateY(-2px);
    }

    /* ═══════════════════════════════════════════
       GLASSMORPHISM INPUTS
       ═══════════════════════════════════════════ */
    input, select, textarea {
        background: rgba(255,255,255,0.6) !important;
        backdrop-filter: blur(8px) !important;
        color: var(--text) !important;
        border: 1px solid rgba(203,213,225,0.4) !important;
        border-radius: var(--radius) !important;
        padding: 12px 16px !important;
        font-size: 14px !important;
        transition: all 0.3s var(--ease-out) !important;
    }
    input:focus, select:focus, textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 4px rgba(99,102,241,0.1), 0 0 20px var(--primary-glow) !important;
        outline: none !important;
        background: rgba(255,255,255,0.9) !important;
        transform: translateY(-1px);
    }

    /* ═══════════════════════════════════════════
       FLUID DATAFRAMES
       ═══════════════════════════════════════════ */
    .stDataFrame {
        background: rgba(255,255,255,0.5) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(203,213,225,0.3) !important;
        border-radius: var(--radius-lg) !important;
        overflow: hidden !important;
        box-shadow: var(--shadow) !important;
    }
    .stDataFrame thead { background: rgba(241,245,249,0.5) !important; }
    .stDataFrame tbody tr {
        transition: all 0.2s var(--ease-out) !important;
    }
    .stDataFrame tbody tr:hover {
        background: rgba(99,102,241,0.04) !important;
        transform: scale(1.002);
    }

    /* ═══════════════════════════════════════════
       GLASS ALERTS
       ═══════════════════════════════════════════ */
    .stAlert {
        backdrop-filter: blur(12px) !important;
        border-radius: var(--radius) !important;
        border-left: 4px solid !important;
        padding: 16px 20px !important;
        box-shadow: var(--shadow) !important;
    }
    .stSuccess {
        background: rgba(16,185,129,0.08) !important;
        border-left-color: var(--success) !important;
    }
    .stWarning {
        background: rgba(245,158,11,0.08) !important;
        border-left-color: var(--warning) !important;
    }
    .stError {
        background: rgba(239,68,68,0.08) !important;
        border-left-color: var(--danger) !important;
    }
    .stInfo {
        background: rgba(6,182,212,0.08) !important;
        border-left-color: var(--info) !important;
    }

    /* ═══════════════════════════════════════════
       BADGES — Glowing pills
       ═══════════════════════════════════════════ */
    .badge {
        display: inline-block; padding: 6px 14px;
        border-radius: 9999px; font-size: 12px;
        font-weight: 600; letter-spacing: 0.3px;
        transition: all 0.3s var(--ease-out);
    }
    .badge-primary { background: rgba(99,102,241,0.12); color: var(--primary); }
    .badge-success { background: rgba(16,185,129,0.12); color: var(--success); }
    .badge-warning { background: rgba(245,158,11,0.12); color: var(--warning); }
    .badge-danger { background: rgba(239,68,68,0.12); color: var(--danger); }

    /* ═══════════════════════════════════════════
       EXPANDER — Glassmorphism
       ═══════════════════════════════════════════ */
    .streamlit-expander {
        background: rgba(255,255,255,0.4) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(203,213,225,0.3) !important;
        border-radius: var(--radius) !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.3s var(--ease-out) !important;
    }
    .streamlit-expander:hover {
        box-shadow: var(--shadow) !important;
        border-color: rgba(99,102,241,0.2) !important;
    }
    .streamlit-expanderHeader {
        background: transparent !important;
        color: var(--text) !important;
        font-weight: 500 !important;
        border-radius: var(--radius) !important;
        transition: all 0.2s var(--ease-out) !important;
    }
    .streamlit-expanderHeader:hover {
        background: rgba(99,102,241,0.04) !important;
    }

    /* ═══════════════════════════════════════════
       SCROLLBAR — Premium
       ═══════════════════════════════════════════ */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--primary), var(--secondary));
        border-radius: 4px; border: 2px solid transparent; background-clip: content-box;
    }
    ::-webkit-scrollbar-thumb:hover { background: linear-gradient(180deg, #4F46E5, #DB2777); }

    /* ═══════════════════════════════════════════
       ANIMATIONS LIBRARY
       ═══════════════════════════════════════════ */
    @keyframes fadeIn { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
    @keyframes slideIn { from { opacity:0; transform:translateX(-15px); } to { opacity:1; transform:translateX(0); } }
    @keyframes float { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-6px); } }
    @keyframes pulseGlow { 0%,100% { box-shadow:0 0 10px var(--primary-glow); } 50% { box-shadow:0 0 30px var(--primary-glow); } }
    @keyframes breathe { 0%,100% { opacity:0.6; } 50% { opacity:1; } }
    @keyframes tiltIn {
        from { opacity:0; transform: perspective(600px) rotateX(5deg) translateY(20px); }
        to { opacity:1; transform: perspective(600px) rotateX(0) translateY(0); }
    }

    .animate-fade-in { animation: fadeIn 0.5s var(--ease-out); }
    .animate-slide-in { animation: slideIn 0.5s var(--ease-out); }
    .animate-float { animation: float 3s var(--ease-in-out) infinite; }
    .animate-tilt { animation: tiltIn 0.6s var(--ease-out); }
    .animate-breathe { animation: breathe 3s var(--ease-in-out) infinite; }
    .animate-glow { animation: pulseGlow 2s var(--ease-in-out) infinite; }
    </style>
    """


def get_dark_mode_css() -> str:
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@200;300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;600;700&display=swap');

    :root {
        --primary: #818CF8; --primary-hover: #A5B4FC;
        --primary-glow: rgba(129,140,248,0.3); --primary-soft: rgba(129,140,248,0.08);
        --secondary: #F472B6; --secondary-glow: rgba(244,114,182,0.25);
        --accent: #22D3EE; --accent-glow: rgba(34,211,238,0.2);
        --success: #34D399; --warning: #FBBF24; --danger: #F87171;
        --bg: #080D1A; --bg2: #111827; --bg3: #1F2937;
        --text: #F1F5F9; --text2: #CBD5E1; --text3: #64748B;
        --border: #334155; --border2: #1E293B;
        --radius-sm: 10px; --radius: 18px; --radius-lg: 28px; --radius-xl: 36px;

        --shadow-sm: 0 1px 2px rgba(0,0,0,0.2);
        --shadow: 0 4px 16px rgba(0,0,0,0.3), 0 2px 4px rgba(0,0,0,0.2);
        --shadow-lg: 0 12px 40px rgba(0,0,0,0.4), 0 4px 12px rgba(0,0,0,0.2);
        --shadow-xl: 0 24px 60px rgba(0,0,0,0.5);
        --glow: 0 0 30px var(--primary-glow);

        --ease: cubic-bezier(0.34, 1.56, 0.64, 1);
        --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
        --ease-in-out: cubic-bezier(0.76, 0, 0.24, 1);
        --fast: 200ms var(--ease-out);
        --smooth: 400ms var(--ease-out);
        --slow: 800ms var(--ease-out);
        --morph: 1500ms var(--ease-in-out);
    }

    * { font-family: 'Nunito', 'Quicksand', -apple-system, sans-serif; -webkit-font-smoothing: antialiased; }
    body { background: var(--bg); color: var(--text); overflow-x: hidden; }

    /* ═══════════════════════════════════════════
       COSMIC AMBIENT BACKGROUND
       ═══════════════════════════════════════════ */
    .stApp::before {
        content: ''; position: fixed; inset: 0; z-index: 0; pointer-events: none;
        background:
            radial-gradient(ellipse 60% 35% at 20% 30%, rgba(129,140,248,0.08) 0%, transparent 60%),
            radial-gradient(ellipse 45% 30% at 80% 70%, rgba(244,114,182,0.05) 0%, transparent 55%),
            radial-gradient(ellipse 50% 40% at 40% 80%, rgba(34,211,238,0.04) 0%, transparent 50%),
            radial-gradient(ellipse 40% 30% at 60% 20%, rgba(52,211,153,0.03) 0%, transparent 50%);
        animation: cosmicDrift 30s var(--ease-in-out) infinite alternate;
    }
    @keyframes cosmicDrift {
        0% { transform: scale(1) rotate(0deg); opacity: 0.6; }
        25% { transform: scale(1.08) rotate(2deg); opacity: 1; }
        50% { transform: scale(0.95) rotate(-1deg); opacity: 0.7; }
        75% { transform: scale(1.04) rotate(1.5deg); opacity: 0.9; }
        100% { transform: scale(1.01) rotate(-0.5deg); opacity: 0.8; }
    }

    /* Floating nebula orbs */
    .stApp::after {
        content: ''; position: fixed; z-index: 0; pointer-events: none;
        width: 500px; height: 500px;
        background: radial-gradient(circle at center, rgba(129,140,248,0.1), transparent 65%);
        border-radius: 50%;
        top: -150px; right: -150px;
        animation: nebula1 20s var(--ease-out) infinite alternate;
    }
    @keyframes nebula1 {
        0% { transform: translate(0,0) scale(1); opacity: 0.4; }
        100% { transform: translate(-120px,100px) scale(1.3); opacity: 0.8; }
    }

    .main > div:first-child::before {
        content: ''; position: fixed; z-index: 0; pointer-events: none;
        width: 350px; height: 350px;
        background: radial-gradient(circle at center, rgba(244,114,182,0.07), transparent 65%);
        border-radius: 50%;
        bottom: -80px; left: -80px;
        animation: nebula2 25s var(--ease-out) infinite alternate;
    }
    @keyframes nebula2 {
        0% { transform: translate(0,0) scale(1); opacity: 0.3; }
        100% { transform: translate(80px,-100px) scale(1.4); opacity: 0.7; }
    }

    /* ═══════════════════════════════════════════
       DARK GLASS SIDEBAR
       ═══════════════════════════════════════════ */
    .sidebar .sidebar-content {
        background: rgba(8,13,26,0.85) !important;
        backdrop-filter: blur(24px) saturate(1.4) !important;
        -webkit-backdrop-filter: blur(24px) saturate(1.4) !important;
        border-right: 1px solid rgba(51,65,85,0.3) !important;
        box-shadow: 4px 0 40px rgba(0,0,0,0.3) !important;
    }

    /* ═══════════════════════════════════════════
       NEON GLASS CARDS — 3D Morph
       ═══════════════════════════════════════════ */
    .metric-card {
        background: linear-gradient(135deg, rgba(17,24,39,0.7), rgba(31,41,55,0.3)) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(51,65,85,0.2) !important;
        border-radius: var(--radius-lg) !important;
        padding: 24px !important;
        box-shadow: var(--shadow) !important;
        transition: all 0.5s var(--ease-out) !important;
        position: relative !important;
        overflow: hidden !important;
        transform-style: preserve-3d !important;
        perspective: 1000px !important;
    }

    .metric-card::before {
        content: ''; position: absolute; inset: 0;
        background: linear-gradient(135deg,
            rgba(129,140,248,0.04) 0%, transparent 40%,
            rgba(244,114,182,0.03) 100%);
        opacity: 0; transition: opacity 0.6s var(--ease-out);
    }

    .metric-card::after {
        content: ''; position: absolute; top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: conic-gradient(from 0deg,
            transparent, rgba(129,140,248,0.03), transparent,
            rgba(244,114,182,0.03), transparent);
        animation: rotateShimmer 6s linear infinite;
    }
    @keyframes rotateShimmer {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .metric-card:hover {
        transform: translateY(-10px) scale(1.03) rotateX(3deg) !important;
        box-shadow: var(--shadow-xl), 0 0 50px var(--primary-glow) !important;
        border-color: var(--primary) !important;
        background: linear-gradient(135deg, rgba(17,24,39,0.8), rgba(31,41,55,0.4)) !important;
    }
    .metric-card:hover::before { opacity: 1; }

    /* ═══════════════════════════════════════════
       NEON BUTTONS
       ═══════════════════════════════════════════ */
    button[kind="primary"] {
        background: linear-gradient(135deg, var(--primary), #6366F1) !important;
        color: #080D1A !important; border: none !important;
        border-radius: var(--radius) !important;
        padding: 12px 24px !important;
        font-weight: 700 !important; font-size: 14px !important;
        transition: all 0.4s var(--ease-out) !important;
        box-shadow: var(--shadow), 0 0 0 0 var(--primary-glow) !important;
        position: relative !important; overflow: hidden !important;
    }

    button[kind="primary"]::before {
        content: ''; position: absolute; inset: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
        transform: translateX(-100%);
        transition: transform 0.6s var(--ease-out);
    }
    button[kind="primary"]:hover {
        transform: translateY(-4px) scale(1.03) !important;
        box-shadow: var(--shadow-lg), 0 0 50px var(--primary-glow) !important;
    }
    button[kind="primary"]:hover::before { transform: translateX(100%); }
    button[kind="primary"]:active { transform: translateY(0) scale(0.97) !important; }

    button[kind="secondary"] {
        background: rgba(17,24,39,0.6) !important;
        backdrop-filter: blur(8px) !important;
        color: var(--text) !important;
        border: 1px solid rgba(51,65,85,0.4) !important;
        border-radius: var(--radius) !important;
        padding: 12px 20px !important;
        font-weight: 500 !important;
        transition: all 0.3s var(--ease-out) !important;
    }
    button[kind="secondary"]:hover {
        background: rgba(17,24,39,0.8) !important;
        border-color: var(--primary) !important;
        box-shadow: 0 0 25px var(--primary-glow) !important;
        transform: translateY(-2px) !important;
    }

    /* ═══════════════════════════════════════════
       NEON TABS
       ═══════════════════════════════════════════ */
    .stTabs { margin-bottom: 1.5rem !important; animation: fadeUp 0.6s var(--ease-out); }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .stTabs [data-baseweb="tab-list"] {
        background: rgba(17,24,39,0.6) !important;
        backdrop-filter: blur(16px) !important;
        border-radius: 16px !important;
        padding: 4px !important; gap: 2px !important;
        border: 1px solid rgba(51,65,85,0.3) !important;
        box-shadow: var(--shadow) !important;
    }

    .stTabs [role="tab"] {
        border-radius: 12px !important;
        padding: 10px 20px !important;
        font-weight: 500 !important; font-size: 0.88rem !important;
        color: var(--text2) !important;
        background: transparent !important;
        border: none !important;
        transition: all 0.3s var(--ease-out) !important;
    }
    .stTabs [role="tab"]:hover {
        color: var(--primary) !important;
        background: rgba(129,140,248,0.08) !important;
        transform: translateY(-2px);
    }
    .stTabs [role="tab"][aria-selected="true"] {
        color: #080D1A !important;
        background: linear-gradient(135deg, var(--primary), #A5B4FC) !important;
        box-shadow: 0 4px 20px var(--primary-glow) !important;
        transform: translateY(-2px);
    }

    /* ═══════════════════════════════════════════
       DARK INPUTS — Neon glow
       ═══════════════════════════════════════════ */
    input, select, textarea {
        background: rgba(17,24,39,0.6) !important;
        backdrop-filter: blur(8px) !important;
        color: var(--text) !important;
        border: 1px solid rgba(51,65,85,0.4) !important;
        border-radius: var(--radius) !important;
        padding: 12px 16px !important;
        font-size: 14px !important;
        transition: all 0.3s var(--ease-out) !important;
    }
    input:focus, select:focus, textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 4px rgba(129,140,248,0.12), 0 0 25px var(--primary-glow) !important;
        outline: none !important;
        background: rgba(17,24,39,0.8) !important;
        transform: translateY(-1px);
    }

    /* ═══════════════════════════════════════════
       DARK DATAFRAMES
       ═══════════════════════════════════════════ */
    .stDataFrame {
        background: rgba(17,24,39,0.5) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(51,65,85,0.3) !important;
        border-radius: var(--radius-lg) !important;
        overflow: hidden !important;
        box-shadow: var(--shadow) !important;
    }
    .stDataFrame thead { background: rgba(31,41,55,0.5) !important; }
    .stDataFrame tbody tr { transition: all 0.2s var(--ease-out) !important; }
    .stDataFrame tbody tr:hover {
        background: rgba(129,140,248,0.06) !important;
        transform: scale(1.002);
    }

    /* ═══════════════════════════════════════════
       DARK ALERTS
       ═══════════════════════════════════════════ */
    .stAlert {
        backdrop-filter: blur(12px) !important;
        border-radius: var(--radius) !important;
        border-left: 4px solid !important;
        padding: 16px 20px !important;
        box-shadow: var(--shadow) !important;
    }
    .stSuccess { background: rgba(52,211,153,0.1) !important; border-left-color: var(--success) !important; color: var(--success) !important; }
    .stWarning { background: rgba(251,191,36,0.1) !important; border-left-color: var(--warning) !important; color: var(--warning) !important; }
    .stError { background: rgba(248,113,113,0.1) !important; border-left-color: var(--danger) !important; color: var(--danger) !important; }
    .stInfo { background: rgba(34,211,238,0.1) !important; border-left-color: var(--accent) !important; color: var(--accent) !important; }

    /* ═══════════════════════════════════════════
       DARK BADGES
       ═══════════════════════════════════════════ */
    .badge-primary { background: rgba(129,140,248,0.15); color: var(--primary); }
    .badge-success { background: rgba(52,211,153,0.15); color: var(--success); }
    .badge-warning { background: rgba(251,191,36,0.15); color: var(--warning); }
    .badge-danger { background: rgba(248,113,113,0.15); color: var(--danger); }

    /* ═══════════════════════════════════════════
       DARK EXPANDER
       ═══════════════════════════════════════════ */
    .streamlit-expander {
        background: rgba(17,24,39,0.4) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(51,65,85,0.3) !important;
        border-radius: var(--radius) !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.3s var(--ease-out) !important;
    }
    .streamlit-expander:hover {
        box-shadow: var(--shadow) !important;
        border-color: rgba(129,140,248,0.2) !important;
    }
    .streamlit-expanderHeader {
        background: transparent !important; color: var(--text) !important;
        font-weight: 500 !important; transition: all 0.2s var(--ease-out) !important;
    }
    .streamlit-expanderHeader:hover { background: rgba(129,140,248,0.04) !important; }

    /* ═══════════════════════════════════════════
       SCROLLBAR — Cosmic
       ═══════════════════════════════════════════ */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--primary), var(--secondary));
        border-radius: 4px; border: 2px solid transparent; background-clip: content-box;
    }

    /* ═══════════════════════════════════════════
       ANIMATIONS
       ═══════════════════════════════════════════ */
    @keyframes fadeIn { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
    @keyframes slideIn { from { opacity:0; transform:translateX(-15px); } to { opacity:1; transform:translateX(0); } }
    @keyframes float { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-6px); } }
    @keyframes pulseGlow { 0%,100% { box-shadow:0 0 10px var(--primary-glow); } 50% { box-shadow:0 0 30px var(--primary-glow); } }
    @keyframes tiltIn {
        from { opacity:0; transform: perspective(600px) rotateX(5deg) translateY(20px); }
        to { opacity:1; transform: perspective(600px) rotateX(0) translateY(0); }
    }
    .animate-fade-in { animation: fadeIn 0.5s var(--ease-out); }
    .animate-slide-in { animation: slideIn 0.5s var(--ease-out); }
    .animate-float { animation: float 3s ease-in-out infinite; }
    .animate-tilt { animation: tiltIn 0.6s var(--ease-out); }
    </style>
    """


def metric_card(title: str, value: str, change: str = "", icon: str = "📊", color: str = "primary") -> str:
    change_class = ""
    if "↑" in change: change_class = "badge-success"
    elif "↓" in change: change_class = "badge-danger"
    return f'''
    <div class="metric-card animate-tilt">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
            <h4 style="margin:0;font-size:14px;font-weight:500;opacity:0.7">{title}</h4>
            <span style="font-size:24px">{icon}</span>
        </div>
        <h2 style="margin:8px 0;font-size:28px;font-weight:700">{value}</h2>
        {f'<span class="badge {change_class}">{change}</span>' if change else ""}
    </div>
    '''


def status_badge(text: str, status: str = "primary") -> str:
    return f'<span class="badge badge-{status}">{text}</span>'


def gradient_text(text: str, color1: str = "#6366F1", color2: str = "#EC4899") -> str:
    return f'''
    <span style="background:linear-gradient(135deg,{color1},{color2});
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
        background-clip:text;font-weight:800;font-size:1.15em">{text}</span>
    '''


def render_theme() -> None:
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "light"
    if st.session_state.theme_mode == "light":
        st.markdown(get_light_mode_css(), unsafe_allow_html=True)
    else:
        st.markdown(get_dark_mode_css(), unsafe_allow_html=True)


def get_theme_colors(mode: str = "light") -> Dict[str, str]:
    return COLORS.get(mode, COLORS["light"])


def render_theme_switcher() -> None:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("☀️ Light", use_container_width=True, help="Switch to light mode"):
            st.session_state.theme_mode = "light"
            st.rerun()
    with col2:
        if st.button("🌙 Dark", use_container_width=True, help="Switch to dark mode"):
            st.session_state.theme_mode = "dark"
            st.rerun()
    mode_name = "Light Mode ☀️" if st.session_state.theme_mode == "light" else "Dark Mode 🌙"
    st.caption(f"Current: **{mode_name}**")


def debug_theme_config() -> None:
    if st.checkbox("🔧 Debug: Show Theme Config"):
        st.json({"Light Mode": COLORS["light"], "Dark Mode": COLORS["dark"]})


if __name__ == "__main__":
    st.set_page_config(page_title="Theme Preview", page_icon="🎨", layout="wide")
    render_theme()
    render_theme_switcher()
    st.title("🎨 Theme Preview — Ultra-Fluid Design")
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(metric_card("Total Users", "45,230", "↑ 12.5%", "👥"), unsafe_allow_html=True)
    with col2: st.markdown(metric_card("Revenue", "$123K", "↑ 8.3%", "💰"), unsafe_allow_html=True)
    with col3: st.markdown(metric_card("Conversion", "3.2%", "↓ 0.5%", "📈"), unsafe_allow_html=True)