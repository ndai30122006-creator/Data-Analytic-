"""Base utilities shared across all advanced analytics modules."""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ── Chart Theme ──
CHART_THEME = dict(
    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family="Inter, -apple-system, sans-serif", size=13, color="#e2e8f0"),
    title=dict(font=dict(size=16, color="#f1f5f9"), x=0.5, xanchor='center'),
    xaxis=dict(gridcolor='rgba(255,255,255,0.06)', zerolinecolor='rgba(255,255,255,0.1)'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.06)', zerolinecolor='rgba(255,255,255,0.1)'),
    hoverlabel=dict(bgcolor="#1e293b", font_size=12, font_family="Inter"),
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(font=dict(size=12), bgcolor='rgba(0,0,0,0)'),
    colorway=['#818cf8', '#34d399', '#fbbf24', '#f87171', '#38bdf8', '#a78bfa']
)

def apply_theme(fig):
    fig.update_layout(**CHART_THEME)
    return fig

def insight_card(icon, title, msg, type="info"):
    st.markdown(f'<div class="insight-card insight-{type}"><strong>{icon} {title}</strong><br>{msg}</div>',
                unsafe_allow_html=True)

def validate_df(df, num, cat=None, min_rows=5, min_numeric=1):
    if df is None or len(df) == 0:
        st.error("❌ Dataset rỗng")
        return False
    if len(df) < min_rows:
        st.warning(f"⚠️ Cần ít nhất {min_rows} dòng (hiện có {len(df)})")
        return False
    if len(num) < min_numeric:
        st.warning(f"⚠️ Cần ít nhất {min_numeric} cột numeric (hiện có {len(num)})")
        return False
    return True

def make_key(base: str, prefix: str = "") -> str:
    """Create a unique Streamlit widget key to avoid duplicates when
    the same module is used in multiple tabs."""
    return f"{prefix}_{base}" if prefix else base