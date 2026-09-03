"""Main orchestrator for Deep Analysis tab — dispatches to 11 sub-modules"""

import streamlit as st

from .ab_testing import render_ab_testing_tab
from .advanced_stats import render_advanced_stats_tab
from .bootstrap import render_bootstrap_tab
from .data_quality import render_data_quality_tab
from .diagnostics import render_diagnostics_tab
from .logistic import render_logistic_tab
from .model_comparison import render_model_comparison_tab
from .naive_bayes import render_naive_bayes_tab

# Optional heavy modules (archived per docs/plan 01 — may be missing)
try:
    from .clustering import render_clustering_tab
except ImportError:
    render_clustering_tab = None
try:
    from .feature_engineering import render_feature_engineering_tab
except ImportError:
    render_feature_engineering_tab = None
try:
    from .pca import render_pca_tab
except ImportError:
    render_pca_tab = None


def render_deep_analysis_tab(df, num, cat, dat):
    """Main entry point for Deep Analysis tab — 11 modules"""
    st.markdown(
        """
    <div class="hero-bg" style="padding: 1.5rem 1rem; margin-bottom: 0.5rem;">
        <div class="hero" style="text-align: center;">
            <h1 style="font-size: 1.8rem; font-weight: 800; background: linear-gradient(135deg, #5b6bf7, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            🧠 Practical Statistics for Data Scientists
            </h1>
            <p style="color: var(--fg-muted);">Based on the book by Peter Bruce, Andrew Bruce & Peter Gedeck</p>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Tabs filtered per docs/plan 01 — archived 3 heavy modules
    tab_names = [
        "Advanced Stats",
        "Bootstrap",
        "A/B Testing",
        "Logistic",
        "Naive Bayes",
        "Diagnostics",
        "Model Comparison",
        "Data Quality",
    ]
    # Add optional tabs if available
    if render_clustering_tab:
        tab_names.append("Clustering")
    if render_pca_tab:
        tab_names.append("PCA & t-SNE")
    if render_feature_engineering_tab:
        tab_names.append("Feature Engineering")

    deep_tabs = st.tabs(tab_names)
    # Map index to renderer (handle optional)
    idx = 0
    with deep_tabs[idx]:
        render_advanced_stats_tab(df, num, cat)
    idx += 1
    with deep_tabs[idx]:
        render_bootstrap_tab(df, num)
    idx += 1
    with deep_tabs[idx]:
        render_ab_testing_tab(df, num, cat)
    idx += 1
    with deep_tabs[idx]:
        render_logistic_tab(df, num, cat)
    idx += 1
    with deep_tabs[idx]:
        render_naive_bayes_tab(df, num, cat)
    idx += 1
    with deep_tabs[idx]:
        render_diagnostics_tab(df, num)
    idx += 1
    with deep_tabs[idx]:
        render_model_comparison_tab(df, num)
    idx += 1
    with deep_tabs[idx]:
        render_data_quality_tab(df, num, cat)
    idx += 1
    if render_clustering_tab:
        with deep_tabs[idx]:
            render_clustering_tab(df, num)
        idx += 1
    if render_pca_tab:
        with deep_tabs[idx]:
            render_pca_tab(df, num)
        idx += 1
    if render_feature_engineering_tab:
        with deep_tabs[idx]:
            render_feature_engineering_tab(df, num, cat)
