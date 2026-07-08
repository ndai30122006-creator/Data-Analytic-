"""
🎨 Theme Configuration — Meta-style Modern Design System
Palette: Facebook/Instagram colors with dark mode support
"""

import streamlit as st
from typing import Dict, Any
import json

# ═══════════════════════════════════════════════════════════════════════════════
# COLOR PALETTE (Meta Design System)
# ═══════════════════════════════════════════════════════════════════════════════

COLORS = {
    "light": {
        "primary": "#1877F2",          # Meta Blue
        "primary_hover": "#0A66C2",    # Darker blue on hover
        "secondary": "#E4405F",        # Instagram warm
        "success": "#31A24C",          # Green
        "warning": "#F5A623",          # Orange
        "danger": "#F02849",           # Red/Pink
        "info": "#0A66C2",             # Info blue
        
        "bg_primary": "#FFFFFF",       # White
        "bg_secondary": "#F0F2F5",     # Light gray
        "bg_tertiary": "#E4E6EB",      # Medium gray
        "bg_hover": "#F5F5F5",         # Hover gray
        
        "text_primary": "#000000",     # Black
        "text_secondary": "#65676B",   # Medium gray
        "text_tertiary": "#8A8D91",    # Light gray
        "text_inverse": "#FFFFFF",     # White (on dark)
        
        "border": "#CED0D4",           # Border gray
        "border_light": "#E4E6EB",     # Light border
        
        "chart_bg": "#FFFFFF",
        "chart_grid": "#E4E6EB",
    },
    "dark": {
        "primary": "#1877F2",          # Meta Blue (same)
        "primary_hover": "#1E86E8",    # Lighter blue on hover
        "secondary": "#E4405F",        # Instagram warm
        "success": "#31A24C",          # Green
        "warning": "#F5A623",          # Orange
        "danger": "#F02849",           # Red/Pink
        "info": "#0A66C2",             # Info blue
        
        "bg_primary": "#111828",       # Almost black
        "bg_secondary": "#1F2937",     # Dark gray
        "bg_tertiary": "#374151",      # Medium gray
        "bg_hover": "#2D3748",         # Hover gray
        
        "text_primary": "#F9FAFB",     # Almost white
        "text_secondary": "#D1D5DB",   # Medium gray
        "text_tertiary": "#9CA3AF",    # Light gray
        "text_inverse": "#111828",     # Dark (on light)
        
        "border": "#4B5563",           # Border gray
        "border_light": "#2D3748",     # Light border
        
        "chart_bg": "#1F2937",
        "chart_grid": "#374151",
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# STREAMLIT THEME INJECTION
# ═══════════════════════════════════════════════════════════════════════════════

STREAMLIT_CONFIG = {
    "theme": {
        "primaryColor": COLORS["light"]["primary"],
        "backgroundColor": COLORS["light"]["bg_primary"],
        "secondaryBackgroundColor": COLORS["light"]["bg_secondary"],
        "textColor": COLORS["light"]["text_primary"],
        "font": "sans serif"
    },
    "client": {
        "showErrorDetails": False,
        "toolbarMode": "minimal",
    },
    "logger": {
        "level": "info",
    },
    "ui": {
        "hideStreamlitMenuItems": False,
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS FOR META-STYLE COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def get_light_mode_css() -> str:
    """Light mode CSS with Meta design tokens"""
    return """
    <style>
    /* ═══════════════════════════════════════════════════════════ */
    /* GLOBAL STYLES */
    /* ═══════════════════════════════════════════════════════════ */
    :root {
        --primary-color: #1877F2;
        --primary-hover: #0A66C2;
        --secondary-color: #E4405F;
        --success-color: #31A24C;
        --warning-color: #F5A623;
        --danger-color: #F02849;
        --info-color: #0A66C2;
        
        --bg-primary: #FFFFFF;
        --bg-secondary: #F0F2F5;
        --bg-tertiary: #E4E6EB;
        --bg-hover: #F5F5F5;
        
        --text-primary: #000000;
        --text-secondary: #65676B;
        --text-tertiary: #8A8D91;
        
        --border-color: #CED0D4;
        --border-light: #E4E6EB;
        
        --radius-sm: 4px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --radius-xl: 16px;
        
        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
        --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.1);
        
        --transition: 300ms cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    * {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", sans-serif;
    }
    
    body {
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* STREAMLIT OVERRIDES */
    /* ═══════════════════════════════════════════════════════════ */
    
    /* Main container */
    .main {
        background-color: var(--bg-primary);
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: var(--bg-secondary);
        border-right: 1px solid var(--border-light);
    }
    
    /* Header/Title */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary);
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    h1 {
        font-size: 32px;
        margin-bottom: 24px;
    }
    
    h2 {
        font-size: 24px;
        margin-bottom: 20px;
        border-bottom: 2px solid var(--border-light);
        padding-bottom: 12px;
    }
    
    h3 {
        font-size: 20px;
        margin-bottom: 16px;
    }
    
    /* Body text */
    p, span, div {
        color: var(--text-primary);
    }
    
    small, .text-secondary {
        color: var(--text-secondary);
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* BUTTONS */
    /* ═══════════════════════════════════════════════════════════ */
    
    button[kind="primary"] {
        background-color: var(--primary-color) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 10px 16px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        transition: all var(--transition) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    button[kind="primary"]:hover {
        background-color: var(--primary-hover) !important;
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-1px);
    }
    
    button[kind="primary"]:active {
        transform: translateY(0);
        box-shadow: var(--shadow-sm) !important;
    }
    
    button[kind="secondary"] {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        padding: 10px 16px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        transition: all var(--transition) !important;
    }
    
    button[kind="secondary"]:hover {
        background-color: var(--bg-tertiary) !important;
        border-color: var(--border-color) !important;
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* CARDS & CONTAINERS */
    /* ═══════════════════════════════════════════════════════════ */
    
    .metric-card {
        background-color: var(--bg-secondary);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-lg);
        padding: 20px;
        box-shadow: var(--shadow-sm);
        transition: all var(--transition);
    }
    
    .metric-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-4px);
        border-color: var(--primary-color);
    }
    
    .card {
        background-color: var(--bg-primary);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-lg);
        padding: 24px;
        box-shadow: var(--shadow-md);
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* INPUTS & FORMS */
    /* ═══════════════════════════════════════════════════════════ */
    
    input, select, textarea {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        padding: 10px 12px !important;
        transition: all var(--transition) !important;
    }
    
    input:focus, select:focus, textarea:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(24, 119, 242, 0.1) !important;
        outline: none !important;
    }
    
    input::placeholder {
        color: var(--text-tertiary) !important;
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* TABS */
    /* ═══════════════════════════════════════════════════════════ */
    
    .stTabs {
        margin-bottom: 1.5rem !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-secondary) !important;
        border-radius: var(--radius-lg) !important;
        padding: 4px !important;
        gap: 2px !important;
        border: 1px solid var(--border-light) !important;
    }
    
    .stTabs [role="tab"] {
        border-radius: var(--radius-md) !important;
        padding: 10px 18px !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        color: var(--text-secondary) !important;
        background-color: transparent !important;
        border: none !important;
        transition: all var(--transition) !important;
    }
    
    .stTabs [role="tab"]:hover {
        color: var(--primary-color) !important;
        background-color: var(--bg-tertiary) !important;
    }
    
    .stTabs [role="tab"][aria-selected="true"] {
        color: #fff !important;
        background: var(--primary-color) !important;
        box-shadow: 0 2px 8px rgba(24, 119, 242, 0.3) !important;
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* TABLES */
    /* ═══════════════════════════════════════════════════════════ */
    
    .stDataFrame {
        background-color: var(--bg-primary) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-lg) !important;
        overflow: hidden !important;
    }
    
    .stDataFrame thead {
        background-color: var(--bg-secondary) !important;
        border-bottom: 2px solid var(--border-color) !important;
    }
    
    .stDataFrame tbody tr {
        border-bottom: 1px solid var(--border-light) !important;
    }
    
    .stDataFrame tbody tr:hover {
        background-color: var(--bg-secondary) !important;
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* ALERTS & NOTIFICATIONS */
    /* ═══════════════════════════════════════════════════════════ */
    
    .stAlert {
        border-radius: var(--radius-md) !important;
        border-left: 4px solid !important;
        padding: 16px !important;
    }
    
    .stSuccess {
        background-color: #E8F5E9 !important;
        border-left-color: var(--success-color) !important;
        color: #1B5E20 !important;
    }
    
    .stWarning {
        background-color: #FFF3E0 !important;
        border-left-color: var(--warning-color) !important;
        color: #E65100 !important;
    }
    
    .stError {
        background-color: #FFEBEE !important;
        border-left-color: var(--danger-color) !important;
        color: #B71C1C !important;
    }
    
    .stInfo {
        background-color: #E3F2FD !important;
        border-left-color: var(--info-color) !important;
        color: #0D47A1 !important;
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* BADGES & LABELS */
    /* ═══════════════════════════════════════════════════════════ */
    
    .badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    .badge-primary {
        background-color: rgba(24, 119, 242, 0.1);
        color: var(--primary-color);
    }
    
    .badge-success {
        background-color: rgba(49, 162, 76, 0.1);
        color: var(--success-color);
    }
    
    .badge-warning {
        background-color: rgba(245, 166, 35, 0.1);
        color: var(--warning-color);
    }
    
    .badge-danger {
        background-color: rgba(240, 40, 73, 0.1);
        color: var(--danger-color);
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* EXPANDER */
    /* ═══════════════════════════════════════════════════════════ */
    
    .streamlit-expander {
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-md) !important;
        background-color: var(--bg-secondary) !important;
    }
    
    .streamlit-expanderHeader {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: var(--bg-tertiary) !important;
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* SCROLLBAR */
    /* ═══════════════════════════════════════════════════════════ */
    
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-secondary);
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* ANIMATIONS */
    /* ═══════════════════════════════════════════════════════════ */
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-10px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
    }
    
    .animate-fade-in {
        animation: fadeIn var(--transition) ease-out;
    }
    
    .animate-slide-in {
        animation: slideIn var(--transition) ease-out;
    }
    
    .animate-pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    </style>
    """

def get_dark_mode_css() -> str:
    """Dark mode CSS with Meta design tokens"""
    return """
    <style>
    :root {
        --primary-color: #1877F2;
        --primary-hover: #1E86E8;
        --secondary-color: #E4405F;
        --success-color: #31A24C;
        --warning-color: #F5A623;
        --danger-color: #F02849;
        --info-color: #0A66C2;
        
        --bg-primary: #111828;
        --bg-secondary: #1F2937;
        --bg-tertiary: #374151;
        --bg-hover: #2D3748;
        
        --text-primary: #F9FAFB;
        --text-secondary: #D1D5DB;
        --text-tertiary: #9CA3AF;
        
        --border-color: #4B5563;
        --border-light: #2D3748;
        
        --radius-sm: 4px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --radius-xl: 16px;
        
        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
        --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);
        --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);
        --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.6);
        
        --transition: 300ms cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    * {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", sans-serif;
    }
    
    body {
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }
    
    .main {
        background-color: var(--bg-primary);
    }
    
    .sidebar .sidebar-content {
        background-color: var(--bg-secondary);
        border-right: 1px solid var(--border-light);
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary);
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    p, span, div {
        color: var(--text-primary);
    }
    
    small, .text-secondary {
        color: var(--text-secondary);
    }
    
    button[kind="primary"] {
        background-color: var(--primary-color) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 10px 16px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        transition: all var(--transition) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    button[kind="primary"]:hover {
        background-color: var(--primary-hover) !important;
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-1px);
    }
    
    button[kind="secondary"] {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        padding: 10px 16px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        transition: all var(--transition) !important;
    }
    
    button[kind="secondary"]:hover {
        background-color: var(--bg-tertiary) !important;
        border-color: var(--primary-color) !important;
    }
    
    .metric-card {
        background-color: var(--bg-secondary);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-lg);
        padding: 20px;
        box-shadow: var(--shadow-sm);
        transition: all var(--transition);
    }
    
    .metric-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-4px);
        border-color: var(--primary-color);
    }
    
    .card {
        background-color: var(--bg-secondary);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-lg);
        padding: 24px;
        box-shadow: var(--shadow-md);
    }
    
    input, select, textarea {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        padding: 10px 12px !important;
        transition: all var(--transition) !important;
    }
    
    input:focus, select:focus, textarea:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(24, 119, 242, 0.2) !important;
        outline: none !important;
    }
    
    input::placeholder {
        color: var(--text-tertiary) !important;
    }
    
    .stTabs {
        margin-bottom: 1.5rem !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-secondary) !important;
        border-radius: var(--radius-lg) !important;
        padding: 4px !important;
        gap: 2px !important;
        border: 1px solid var(--border-light) !important;
    }
    
    .stTabs [role="tab"] {
        border-radius: var(--radius-md) !important;
        padding: 10px 18px !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        color: var(--text-secondary) !important;
        background-color: transparent !important;
        border: none !important;
        transition: all var(--transition) !important;
    }
    
    .stTabs [role="tab"]:hover {
        color: var(--primary-color) !important;
        background-color: var(--bg-tertiary) !important;
    }
    
    .stTabs [role="tab"][aria-selected="true"] {
        color: #fff !important;
        background: var(--primary-color) !important;
        box-shadow: 0 2px 8px rgba(24, 119, 242, 0.3) !important;
    }
    
    .stDataFrame {
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-lg) !important;
        overflow: hidden !important;
    }
    
    .stDataFrame thead {
        background-color: var(--bg-tertiary) !important;
        border-bottom: 2px solid var(--border-color) !important;
    }
    
    .stDataFrame tbody tr {
        border-bottom: 1px solid var(--border-light) !important;
    }
    
    .stDataFrame tbody tr:hover {
        background-color: var(--bg-tertiary) !important;
    }
    
    .stAlert {
        border-radius: var(--radius-md) !important;
        border-left: 4px solid !important;
        padding: 16px !important;
    }
    
    .stSuccess {
        background-color: rgba(49, 162, 76, 0.15) !important;
        border-left-color: var(--success-color) !important;
        color: #9AED7D !important;
    }
    
    .stWarning {
        background-color: rgba(245, 166, 35, 0.15) !important;
        border-left-color: var(--warning-color) !important;
        color: #FFD700 !important;
    }
    
    .stError {
        background-color: rgba(240, 40, 73, 0.15) !important;
        border-left-color: var(--danger-color) !important;
        color: #FF6B9D !important;
    }
    
    .stInfo {
        background-color: rgba(24, 119, 242, 0.15) !important;
        border-left-color: var(--info-color) !important;
        color: #87CEEB !important;
    }
    
    .badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    .badge-primary {
        background-color: rgba(24, 119, 242, 0.15);
        color: #87CEEB;
    }
    
    .badge-success {
        background-color: rgba(49, 162, 76, 0.15);
        color: #9AED7D;
    }
    
    .badge-warning {
        background-color: rgba(245, 166, 35, 0.15);
        color: #FFD700;
    }
    
    .badge-danger {
        background-color: rgba(240, 40, 73, 0.15);
        color: #FF6B9D;
    }
    
    .streamlit-expander {
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-md) !important;
        background-color: var(--bg-secondary) !important;
    }
    
    .streamlit-expanderHeader {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: var(--bg-tertiary) !important;
    }
    
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-secondary);
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-10px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
    }
    
    .animate-fade-in {
        animation: fadeIn var(--transition) ease-out;
    }
    
    .animate-slide-in {
        animation: slideIn var(--transition) ease-out;
    }
    
    .animate-pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    </style>
    """

# ═══════════════════════════════════════════════════════════════════════════════
# THEME COMPONENTS (Reusable)
# ═══════════════════════════════════════════════════════════════════════════════

def metric_card(title: str, value: str, change: str = "", icon: str = "📊",
                color: str = "primary") -> str:
    """Generate a beautiful metric card HTML"""
    
    change_class = ""
    if "↑" in change:
        change_class = "badge-success"
    elif "↓" in change:
        change_class = "badge-danger"
    
    html = f"""
    <div class="metric-card animate-fade-in">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <h4 style="margin: 0; font-size: 14px; font-weight: 500; opacity: 0.7;">{title}</h4>
            <span style="font-size: 24px;">{icon}</span>
        </div>
        <h2 style="margin: 8px 0; font-size: 28px; font-weight: 700;">{value}</h2>
        {f'<span class="badge {change_class}">{change}</span>' if change else ""}
    </div>
    """
    return html

def status_badge(text: str, status: str = "primary") -> str:
    """Generate a status badge"""
    status_colors = {
        "success": "#31A24C",
        "warning": "#F5A623",
        "danger": "#F02849",
        "primary": "#1877F2",
        "info": "#0A66C2",
    }
    color = status_colors.get(status, status_colors["primary"])
    
    return f"""
    <span class="badge badge-{status}" style="background-color: rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.15); 
                                             color: {color}; padding: 8px 12px; border-radius: 20px; font-size: 13px; font-weight: 600;">
        {text}
    </span>
    """

def gradient_text(text: str, color1: str = "#1877F2", color2: str = "#E4405F") -> str:
    """Generate gradient text"""
    return f"""
    <span style="
        background: linear-gradient(135deg, {color1} 0%, {color2} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        font-size: 1.1em;
    ">{text}</span>
    """

# ═══════════════════════════════════════════════════════════════════════════════
# RENDER FUNCTION (Main Theme Injector)
# ═══════════════════════════════════════════════════════════════════════════════

def render_theme() -> None:
    """Initialize and render the theme (light/dark mode aware)"""
    
    # Initialize theme mode in session state
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "light"  # Default to light
    
    # Inject appropriate CSS based on theme
    if st.session_state.theme_mode == "light":
        st.markdown(get_light_mode_css(), unsafe_allow_html=True)
    else:
        st.markdown(get_dark_mode_css(), unsafe_allow_html=True)
    
    # Inject custom HTML for header styling
    st.markdown("""
    <style>
    /* Custom header styling */
    div[data-testid="stVerticalBlock"] > div:first-child {
        padding-top: 24px;
        padding-bottom: 24px;
        border-bottom: 1px solid var(--border-light);
        margin-bottom: 24px;
    }
    
    /* Main content padding */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Reduce header bottom margin */
    h1 {
        margin-bottom: 24px !important;
    }
    
    h2 {
        margin-top: 32px !important;
        margin-bottom: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

def get_theme_colors(mode: str = "light") -> Dict[str, str]:
    """Get color palette for a specific theme mode"""
    return COLORS.get(mode, COLORS["light"])

def render_theme_switcher() -> None:
    """Render theme mode switcher in sidebar"""
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("☀️ Light", use_container_width=True,
                    help="Switch to light mode"):
            st.session_state.theme_mode = "light"
            st.rerun()
    
    with col2:
        if st.button("🌙 Dark", use_container_width=True,
                    help="Switch to dark mode"):
            st.session_state.theme_mode = "dark"
            st.rerun()
    
    # Show current mode
    mode_name = "Light Mode ☀️" if st.session_state.theme_mode == "light" else "Dark Mode 🌙"
    st.caption(f"Current: **{mode_name}**")

# ═══════════════════════════════════════════════════════════════════════════════
# DEBUG HELPER (View theme config)
# ═══════════════════════════════════════════════════════════════════════════════

def debug_theme_config() -> None:
    """Display theme configuration (development only)"""
    if st.checkbox("🔧 Debug: Show Theme Config"):
        st.json({
            "Light Mode": COLORS["light"],
            "Dark Mode": COLORS["dark"],
        })


if __name__ == "__main__":
    """Test theme in standalone mode"""
    st.set_page_config(page_title="Theme Preview", page_icon="🎨", layout="wide")
    
    render_theme()
    render_theme_switcher()
    
    st.markdown("---")
    
    st.title("🎨 Theme Preview — Meta Design System")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(metric_card("Total Users", "45,230", "↑ 12.5%", "👥"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(metric_card("Revenue", "$123K", "↑ 8.3%", "💰"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(metric_card("Conversion", "3.2%", "↓ 0.5%", "📈"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### Status Badges")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(status_badge("Success", "success"), unsafe_allow_html=True)
    with col2:
        st.markdown(status_badge("Warning", "warning"), unsafe_allow_html=True)
    with col3:
        st.markdown(status_badge("Danger", "danger"), unsafe_allow_html=True)
    with col4:
        st.markdown(status_badge("Primary", "primary"), unsafe_allow_html=True)
    with col5:
        st.markdown(status_badge("Info", "info"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### Gradient Text")
    st.markdown(gradient_text("🚀 Modern Analytics Platform"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    debug_theme_config()