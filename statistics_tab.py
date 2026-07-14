"""Statistics tab — Delegates to shared modules from advanced_analytics.
This tab is a slim wrapper; all actual computation lives in advanced_analytics/.
"""
import logging
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from config import MIN_ROWS_VALIDATION
from utils import validate_dataframe
from helpers import apply_theme
from src.utils.exceptions import handle_error, DataValidationError

try:
    from theme_config import metric_card, status_badge, gradient_text
except ImportError:
    def metric_card(title, value, change="", icon="📊", color="primary"):
        return f'<div class="metric-card"><h4>{icon} {title}</h4><h2>{value}</h2></div>'
    def status_badge(text, status="primary"):
        return f"<span>{text}</span>"
    def gradient_text(text, c1="#1877F2", c2="#E4405F"):
        return f"<span style='font-weight:700'>{text}</span>"

# ── Delegate to shared modules (DRY) with unique key_prefix ──
try:
    from advanced_analytics.bootstrap import render_bootstrap_tab as _render_bootstrap
except ImportError:
    _render_bootstrap = None
try:
    from advanced_analytics.ab_testing import render_ab_testing_tab as _render_ab_testing
except ImportError:
    _render_ab_testing = None
try:
    from advanced_analytics.logistic import render_logistic_tab as _render_logistic
except ImportError:
    _render_logistic = None
try:
    from advanced_analytics.naive_bayes import render_naive_bayes_tab as _render_naive_bayes
except ImportError:
    _render_naive_bayes = None
try:
    from advanced_analytics.diagnostics import render_diagnostics_tab as _render_diagnostics
except ImportError:
    _render_diagnostics = None

logger = logging.getLogger(__name__)


def render_statistics_tab(df, num, cat):
    """Render the Statistics tab with shared sub-modules (DRY)."""
    is_valid, msg = validate_dataframe(df, min_rows=MIN_ROWS_VALIDATION)
    if not is_valid:
        st.error(f"❌ {msg}")
        return

    st.markdown("""
    <div class="hero-bg" style="padding: 1.5rem 1rem; margin-bottom: 0.5rem;">
        <div class="hero" style="text-align: center;">
            <h1 style="font-size: 1.8rem; font-weight: 800; background: linear-gradient(135deg, #5b6bf7, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            📈 Statistics for Data Scientists
            </h1>
            <p style="color: var(--fg-muted);">Hypothesis Testing · Bootstrap · A/B Testing · Logistic · Naive Bayes · Diagnostics</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    from config import STATISTICS_TABS
    stats_tabs = st.tabs(STATISTICS_TABS)

    with stats_tabs[0]: _render_hypothesis_testing(df, num, cat)

    # ── Delegate to shared modules (DRY) — pass key_prefix="st" to avoid duplicates ──
    with stats_tabs[1]:
        if _render_bootstrap:
            _render_bootstrap(df, num, key_prefix="st")
        else:
            st.warning("⚠️ Bootstrap module not loaded")
    with stats_tabs[2]:
        if _render_ab_testing:
            _render_ab_testing(df, num, cat, key_prefix="st")
        else:
            st.warning("⚠️ A/B Testing module not loaded")
    with stats_tabs[3]: _render_regression(df, num)
    with stats_tabs[4]:
        if _render_logistic:
            _render_logistic(df, num, cat, key_prefix="st")
        else:
            st.warning("⚠️ Logistic Regression module not loaded")
    with stats_tabs[5]:
        if _render_naive_bayes:
            _render_naive_bayes(df, num, cat, key_prefix="st")
        else:
            st.markdown("### 🧮 Naive Bayes (Book Ch.5)")
            st.info("Naive Bayes is available in the **Deep Analysis** tab with full features.")
    with stats_tabs[6]:
        if _render_diagnostics:
            _render_diagnostics(df, num, key_prefix="st")
        else:
            st.markdown("### 🔧 Diagnostics (Book Ch.4)")
            st.info("Regression Diagnostics (VIF, Heteroskedasticity, Durbin-Watson) are available in the **Deep Analysis** tab.")


# ── Hypothesis Testing — only kept here (unique to this tab) ──
def _render_hypothesis_testing(df, num, cat):
    if not num and not cat:
        st.warning("Cần dữ liệu numeric hoặc categorical")
        return
    from scipy.stats import ttest_ind, ttest_1samp, ttest_rel, f_oneway, mannwhitneyu, kruskal, chi2_contingency

    test_type = st.selectbox("Test type:", [
        "T-test (2 independent samples)", "T-test (1 sample)", "T-test (paired)",
        "ANOVA", "Mann-Whitney U", "Kruskal-Wallis", "Chi-Square"
    ], key="ht_type")
    SIGNIFICANCE_LEVEL = 0.05

    if "2 independent" in test_type:
        if len(num) >= 1 and len(cat) >= 1:
            val_col = st.selectbox("Value column:", num, key="ht_val")
            grp_col = st.selectbox("Group column:", cat, key="ht_grp")
            grps = df[grp_col].dropna().unique()[:5]
            if len(grps) >= 2:
                g1 = st.selectbox("Group 1:", grps, key="ht_g1")
                g2 = st.selectbox("Group 2:", [g for g in grps if g != g1], key="ht_g2")
                if st.button("🔬 Run", key="ht_run"):
                    try:
                        s1 = df[df[grp_col] == g1][val_col].dropna()
                        s2 = df[df[grp_col] == g2][val_col].dropna()
                        if len(s1) > 1 and len(s2) > 1:
                            stat, p = ttest_ind(s1, s2, equal_var=False)
                            pooled_std = np.sqrt((s1.std()**2 + s2.std()**2) / 2)
                            cohens_d = (s1.mean() - s2.mean()) / pooled_std if pooled_std > 0 else 0
                            c1, c2, c3, c4 = st.columns(4)
                            c1.metric("t-statistic", f"{stat:.4f}")
                            c2.metric("p-value", f"{p:.6f}")
                            c3.metric("Cohen's d", f"{abs(cohens_d):.4f}")
                            c4.metric("Conclusion", "Significant 🎯" if p < SIGNIFICANCE_LEVEL else "Not significant ❌")
                            fig = go.Figure()
                            fig.add_trace(go.Violin(y=s1, name=g1, box_visible=True, meanline_visible=True))
                            fig.add_trace(go.Violin(y=s2, name=g2, box_visible=True, meanline_visible=True))
                            fig.update_layout(title=f"{val_col}: {g1} vs {g2} (p={p:.4f}, d={abs(cohens_d):.3f})")
                            apply_theme(fig)
                            st.plotly_chart(fig, width='stretch')
                        else:
                            st.error("Need ≥2 values per group")
                    except Exception as e:
                        handle_error(e, f"T-test: {val_col} by {grp_col}")
            else:
                st.warning("Need ≥2 groups")
        else:
            st.warning("Need 1 numeric + 1 categorical column")

    elif "1 sample" in test_type:
        if num:
            val_col = st.selectbox("Value column:", num, key="ht_1s")
            mu0 = st.number_input("Hypothesized mean (μ₀):", value=0.0, key="ht_mu")
            if st.button("🔬 Run", key="ht_1s_run"):
                s = df[val_col].dropna()
                stat, p = ttest_1samp(s, mu0)
                c1, c2 = st.columns(2)
                c1.metric("t-statistic", f"{stat:.4f}")
                c2.metric("p-value", f"{p:.6f}")
                st.info(f"**Conclusion:** {'Different from μ₀ 🎯' if p < SIGNIFICANCE_LEVEL else 'Not different from μ₀ ❌'}")
        else:
            st.warning("Need numeric column")

    elif "paired" in test_type:
        if len(num) >= 2:
            col_before = st.selectbox("Before:", num, key="ht_pa")
            col_after = st.selectbox("After:", [c for c in num if c != col_before], key="ht_pb")
            if st.button("🔬 Run", key="ht_p_run"):
                s = df[[col_before, col_after]].dropna()
                stat, p = ttest_rel(s[col_before], s[col_after])
                c1, c2 = st.columns(2)
                c1.metric("t-statistic", f"{stat:.4f}")
                c2.metric("p-value", f"{p:.6f}")
                st.info(f"**Conclusion:** {'Significant difference 🎯' if p < SIGNIFICANCE_LEVEL else 'Not significant ❌'}")

    elif "ANOVA" in test_type:
        if len(num) >= 1 and len(cat) >= 1:
            val_col = st.selectbox("Value:", num, key="ht_anova_val")
            grp_col = st.selectbox("Group:", cat, key="ht_anova_grp")
            if st.button("🔬 Run", key="ht_anova_run"):
                grps = df[grp_col].dropna().unique()
                groups = [df[df[grp_col] == g][val_col].dropna().values for g in grps if len(df[df[grp_col] == g]) > 1]
                if len(groups) >= 2:
                    stat, p = f_oneway(*groups)
                    c1, c2 = st.columns(2)
                    c1.metric("F-statistic", f"{stat:.4f}")
                    c2.metric("p-value", f"{p:.6f}")
                    st.info(f"**Conclusion:** {'Groups differ 🎯' if p < SIGNIFICANCE_LEVEL else 'No difference ❌'}")
                    fig = px.box(df, x=grp_col, y=val_col, title=f"ANOVA: {val_col} by {grp_col}")
                    apply_theme(fig)
                    st.plotly_chart(fig, width='stretch')

    elif "Mann-Whitney" in test_type:
        if len(num) >= 1 and len(cat) >= 1:
            val_col = st.selectbox("Value column:", num, key="mw_val")
            grp_col = st.selectbox("Group column:", cat, key="mw_grp")
            grps = df[grp_col].dropna().unique()[:5]
            if len(grps) >= 2:
                g1 = st.selectbox("Group 1:", grps, key="mw_g1")
                g2 = st.selectbox("Group 2:", [g for g in grps if g != g1], key="mw_g2")
                if st.button("🔬 Run", key="mw_run"):
                    s1 = df[df[grp_col] == g1][val_col].dropna()
                    s2 = df[df[grp_col] == g2][val_col].dropna()
                    if len(s1) > 1 and len(s2) > 1:
                        stat, p = mannwhitneyu(s1, s2, alternative='two-sided')
                        c1, c2, c3 = st.columns(3)
                        c1.metric("U-statistic", f"{stat:.4f}")
                        c2.metric("p-value", f"{p:.6f}")
                        c3.metric("Conclusion", "Significant 🎯" if p < SIGNIFICANCE_LEVEL else "Not significant ❌")

    elif "Kruskal-Wallis" in test_type:
        if len(num) >= 1 and len(cat) >= 1:
            val_col = st.selectbox("Value:", num, key="kw_val")
            grp_col = st.selectbox("Group:", cat, key="kw_grp")
            if st.button("🔬 Run", key="kw_run"):
                grps = df[grp_col].dropna().unique()
                groups = [df[df[grp_col] == g][val_col].dropna().values for g in grps if len(df[df[grp_col] == g]) > 1]
                if len(groups) >= 2:
                    stat, p = kruskal(*groups)
                    c1, c2 = st.columns(2)
                    c1.metric("H-statistic", f"{stat:.4f}")
                    c2.metric("p-value", f"{p:.6f}")
                    st.info(f"**Conclusion:** {'Groups differ 🎯' if p < SIGNIFICANCE_LEVEL else 'No difference ❌'}")
                    fig = px.box(df, x=grp_col, y=val_col, title=f"Kruskal-Wallis: {val_col} by {grp_col}")
                    apply_theme(fig)
                    st.plotly_chart(fig, width='stretch')

    elif "Chi-Square" in test_type:
        if len(cat) >= 2:
            col1_name = st.selectbox("Column 1:", cat, key="ht_cs1")
            col2_name = st.selectbox("Column 2:", [c for c in cat if c != col1_name], key="ht_cs2")
            if st.button("🔬 Run", key="ht_cs_run"):
                ct = pd.crosstab(df[col1_name], df[col2_name])
                stat, p, dof, _expected = chi2_contingency(ct)
                c1, c2, c3 = st.columns(3)
                c1.metric("χ²", f"{stat:.4f}")
                c2.metric("p-value", f"{p:.6f}")
                c3.metric("DoF", dof)
                st.info(f"**Conclusion:** {'Variables are related 🎯' if p < SIGNIFICANCE_LEVEL else 'No relationship ❌'}")
                fig = px.imshow(ct, text_auto=True, title="Contingency Table",
                               color_continuous_scale="Viridis", aspect='auto')
                apply_theme(fig)
                st.plotly_chart(fig, width='stretch')
        else:
            st.warning("Need ≥2 categorical columns")


# ── Linear Regression — kept in statistics (unique code path) ──
def _render_regression(df, num):
    if len(num) < 2:
        st.warning("Need ≥2 numeric columns")
        return
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split

    st.markdown("### 📈 Linear Regression (Book Ch.4)")
    target = st.selectbox("Target:", num, key="reg_target")
    features = st.multiselect("Features:", [c for c in num if c != target],
                            default=[c for c in num if c != target][:min(3, len(num)-1)], key="reg_feats")
    if len(features) >= 1 and st.button("📈 Run Regression", key="reg_run"):
        X = df[features].dropna()
        y = df.loc[X.index, target]
        if len(X) >= 10:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            scaler = StandardScaler()
            X_train_s = scaler.fit_transform(X_train)
            X_test_s = scaler.transform(X_test)
            model = LinearRegression()
            model.fit(X_train_s, y_train)
            train_r2 = model.score(X_train_s, y_train)
            test_r2 = model.score(X_test_s, y_test)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Train R²", f"{train_r2:.4f}")
            c2.metric("Test R²", f"{test_r2:.4f}")
            c3.metric("Intercept", f"{model.intercept_:.4f}")
            c4.metric("Features", f"{len(features)}")
            coef_df = pd.DataFrame({"Feature": features, "Coefficient": model.coef_})
            st.dataframe(coef_df, width='stretch')
            y_pred = model.predict(X_test_s)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=y_test, y=y_pred, mode='markers', marker=dict(color="#818cf8", size=6, opacity=0.6)))
            fig.add_trace(go.Scatter(x=[y_test.min(), y_test.max()], y=[y_test.min(), y_test.max()],
                                    mode='lines', line=dict(color="#f87171", dash="dash"), name="Perfect Fit"))
            fig.update_layout(title=f"Actual vs Predicted (R²={test_r2:.4f})",
                            xaxis_title="Actual", yaxis_title="Predicted", height=350)
            apply_theme(fig)
            st.plotly_chart(fig, width='stretch')
        else:
            st.error("Need ≥10 samples")