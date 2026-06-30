"""Main orchestrator for Deep Analysis tab — dispatches to 11 sub-modules"""
import streamlit as st

from .advanced_stats import render_advanced_stats_tab
from .bootstrap import render_bootstrap_tab
from .ab_testing import render_ab_testing_tab
from .logistic import render_logistic_tab
from .naive_bayes import render_naive_bayes_tab
from .diagnostics import render_diagnostics_tab
from .clustering import render_clustering_tab
from .pca import render_pca_tab
from .feature_engineering import render_feature_engineering_tab
from .model_comparison import render_model_comparison_tab
from .data_quality import render_data_quality_tab


def render_deep_analysis_tab(df, num, cat, dat):
    """Main entry point for Deep Analysis tab — 11 modules"""
    st.markdown("""
    <div class="hero-bg" style="padding: 1.5rem 1rem; margin-bottom: 0.5rem;">
        <div class="hero" style="text-align: center;">
            <h1 style="font-size: 1.8rem; font-weight: 800; background: linear-gradient(135deg, #5b6bf7, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            🧠 Practical Statistics for Data Scientists
            </h1>
            <p style="color: var(--fg-muted);">Based on the book by Peter Bruce, Andrew Bruce & Peter Gedeck</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    deep_tabs = st.tabs([
        "📊 Advanced Stats", "🎲 Bootstrap", "⚗️ A/B Testing",
        "🔴 Logistic", "🧮 Naive Bayes", "🔧 Diagnostics",
        "🧬 Clustering", "🎯 PCA & t-SNE", "🔧 Feature Engineering",
        "🏆 Model Comparison", "✅ Data Quality"
    ])

    with deep_tabs[0]: render_advanced_stats_tab(df, num, cat)
    with deep_tabs[1]: render_bootstrap_tab(df, num)
    with deep_tabs[2]: render_ab_testing_tab(df, num, cat)
    with deep_tabs[3]: render_logistic_tab(df, num, cat)
    with deep_tabs[4]: render_naive_bayes_tab(df, num, cat)
    with deep_tabs[5]: render_diagnostics_tab(df, num)
    with deep_tabs[6]: render_clustering_tab(df, num)
    with deep_tabs[7]: render_pca_tab(df, num)
    with deep_tabs[8]: render_feature_engineering_tab(df, num, cat)
    with deep_tabs[9]: render_model_comparison_tab(df, num)
    with deep_tabs[10]: render_data_quality_tab(df, num, cat)