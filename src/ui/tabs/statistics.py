"""Statistics tab — core statistical workflows via src.core.statistical_tests (P1 deduplication)."""

import logging

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.core.statistical_tests import (
    SIGNIFICANCE_LEVEL,
    compute_regression_metrics,
    run_anova,
    run_chisquare,
    run_kruskal,
    run_mannwhitney,
    run_ttest_independent,
    run_ttest_onesample,
    run_ttest_paired,
)
from src.utils.config import MIN_ROWS_VALIDATION
from src.utils.exceptions import handle_error
from src.utils.helpers import apply_theme
from src.utils.validators import validate_dataframe

try:
    from src.ui.theme import gradient_text, metric_card, status_badge
except ImportError:

    def metric_card(title, value, change="", icon="📊", color="primary"):
        return f'<div class="metric-card"><h4>{icon} {title}</h4><h2>{value}</h2></div>'

    def status_badge(text, status="primary"):
        return f"<span>{text}</span>"

    def gradient_text(text, c1="#1877F2", c2="#E4405F"):
        return f"<span style='font-weight:700'>{text}</span>"


logger = logging.getLogger(__name__)


def render_statistics_tab(df, num, cat):
    """Render the Statistics tab with non-duplicated core workflows."""
    is_valid, msg = validate_dataframe(df, min_rows=MIN_ROWS_VALIDATION)
    if not is_valid:
        st.error(f"❌ {msg}")
        return

    st.markdown(
        """
    <div class="hero-bg" style="padding: 1.5rem 1rem; margin-bottom: 0.5rem;">
        <div class="hero" style="text-align: center;">
            <h1 style="font-size: 1.8rem; font-weight: 800; background: linear-gradient(135deg, #8B5CF6, #EC4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            Statistics for Data Scientists
            </h1>
            <p style="color: var(--fg-muted);">Hypothesis Testing · Linear Regression (via core)</p>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    from src.utils.config import STATISTICS_TABS

    stats_tabs = st.tabs(STATISTICS_TABS)

    with stats_tabs[0]:
        _render_hypothesis_testing(df, num, cat)
    with stats_tabs[1]:
        _render_regression(df, num)


# ── Hypothesis Testing — via core (single source of truth) ──
def _render_hypothesis_testing(df, num, cat):
    if not num and not cat:
        st.warning("Cần dữ liệu numeric hoặc categorical")
        return

    test_type = st.selectbox(
        "Test type:",
        [
            "T-test (2 independent samples)",
            "T-test (1 sample)",
            "T-test (paired)",
            "ANOVA",
            "Mann-Whitney U",
            "Kruskal-Wallis",
            "Chi-Square",
        ],
        key="ht_type",
    )

    if "2 independent" in test_type:
        if len(num) >= 1 and len(cat) >= 1:
            val_col = st.selectbox("Value column:", num, key="ht_val")
            grp_col = st.selectbox("Group column:", cat, key="ht_grp")
            grps = df[grp_col].dropna().unique()[:5]
            if len(grps) >= 2:
                g1 = st.selectbox("Group 1:", grps, key="ht_g1")
                g2 = st.selectbox("Group 2:", [g for g in grps if g != g1], key="ht_g2")
                if st.button("Run", key="ht_run"):
                    try:
                        s1 = df[df[grp_col] == g1][val_col].dropna().values
                        s2 = df[df[grp_col] == g2][val_col].dropna().values
                        if len(s1) > 1 and len(s2) > 1:
                            res = run_ttest_independent(s1, s2)
                            c1, c2, c3, c4 = st.columns(4)
                            c1.metric("t-statistic", f"{res['statistic']:.4f}")
                            c2.metric("p-value", f"{res['p_value']:.6f}")
                            c3.metric("Cohen's d", f"{abs(res['cohens_d']):.4f}")
                            c4.metric("Conclusion", "Significant" if res["significant"] else "Not significant")
                            fig = go.Figure()
                            fig.add_trace(go.Violin(y=s1, name=str(g1), box_visible=True, meanline_visible=True))
                            fig.add_trace(go.Violin(y=s2, name=str(g2), box_visible=True, meanline_visible=True))
                            fig.update_layout(
                                title=f"{val_col}: {g1} vs {g2} (p={res['p_value']:.4f}, d={abs(res['cohens_d']):.3f})"
                            )
                            apply_theme(fig)
                            st.plotly_chart(fig, use_container_width=True)
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
            if st.button("Run", key="ht_1s_run"):
                s = df[val_col].dropna().values
                res = run_ttest_onesample(s, mu0)
                c1, c2 = st.columns(2)
                c1.metric("t-statistic", f"{res['statistic']:.4f}")
                c2.metric("p-value", f"{res['p_value']:.6f}")
                st.info(f"**Conclusion:** {'Different from μ₀' if res['significant'] else 'Not different from μ₀'}")
        else:
            st.warning("Need numeric column")

    elif "paired" in test_type:
        if len(num) >= 2:
            col_before = st.selectbox("Before:", num, key="ht_pa")
            col_after = st.selectbox("After:", [c for c in num if c != col_before], key="ht_pb")
            if st.button("Run", key="ht_p_run"):
                s = df[[col_before, col_after]].dropna()
                res = run_ttest_paired(s[col_before].values, s[col_after].values)
                c1, c2 = st.columns(2)
                c1.metric("t-statistic", f"{res['statistic']:.4f}")
                c2.metric("p-value", f"{res['p_value']:.6f}")
                st.info(f"**Conclusion:** {'Significant difference' if res['significant'] else 'Not significant'}")

    elif "ANOVA" in test_type:
        if len(num) >= 1 and len(cat) >= 1:
            val_col = st.selectbox("Value:", num, key="ht_anova_val")
            grp_col = st.selectbox("Group:", cat, key="ht_anova_grp")
            if st.button("Run", key="ht_anova_run"):
                grps = df[grp_col].dropna().unique()
                groups = [df[df[grp_col] == g][val_col].dropna().values for g in grps if len(df[df[grp_col] == g]) > 1]
                if len(groups) >= 2:
                    res = run_anova(*groups)
                    c1, c2, c3 = st.columns(3)
                    c1.metric("F-statistic", f"{res['statistic']:.4f}")
                    c2.metric("p-value", f"{res['p_value']:.6f}")
                    c3.metric("η²", f"{res['eta_squared']:.3f}")
                    st.info(f"**Conclusion:** {'Groups differ' if res['significant'] else 'No difference'}")
                    fig = px.box(df, x=grp_col, y=val_col, title=f"ANOVA: {val_col} by {grp_col}")
                    apply_theme(fig)
                    st.plotly_chart(fig, use_container_width=True)

    elif "Mann-Whitney" in test_type:
        if len(num) >= 1 and len(cat) >= 1:
            val_col = st.selectbox("Value column:", num, key="mw_val")
            grp_col = st.selectbox("Group column:", cat, key="mw_grp")
            grps = df[grp_col].dropna().unique()[:5]
            if len(grps) >= 2:
                g1 = st.selectbox("Group 1:", grps, key="mw_g1")
                g2 = st.selectbox("Group 2:", [g for g in grps if g != g1], key="mw_g2")
                if st.button("Run", key="mw_run"):
                    s1 = df[df[grp_col] == g1][val_col].dropna().values
                    s2 = df[df[grp_col] == g2][val_col].dropna().values
                    if len(s1) > 1 and len(s2) > 1:
                        res = run_mannwhitney(s1, s2)
                        c1, c2, c3 = st.columns(3)
                        c1.metric("U-statistic", f"{res['statistic']:.4f}")
                        c2.metric("p-value", f"{res['p_value']:.6f}")
                        c3.metric("r", f"{res['r']:.3f}")
                        st.info("Significant" if res["significant"] else "Not significant")

    elif "Kruskal-Wallis" in test_type:
        if len(num) >= 1 and len(cat) >= 1:
            val_col = st.selectbox("Value:", num, key="kw_val")
            grp_col = st.selectbox("Group:", cat, key="kw_grp")
            if st.button("Run", key="kw_run"):
                grps = df[grp_col].dropna().unique()
                groups = [df[df[grp_col] == g][val_col].dropna().values for g in grps if len(df[df[grp_col] == g]) > 1]
                if len(groups) >= 2:
                    res = run_kruskal(*groups)
                    c1, c2 = st.columns(2)
                    c1.metric("H-statistic", f"{res['statistic']:.4f}")
                    c2.metric("p-value", f"{res['p_value']:.6f}")
                    st.info(f"**Conclusion:** {'Groups differ' if res['significant'] else 'No difference'}")
                    fig = px.box(df, x=grp_col, y=val_col, title=f"Kruskal-Wallis: {val_col} by {grp_col}")
                    apply_theme(fig)
                    st.plotly_chart(fig, use_container_width=True)

    elif "Chi-Square" in test_type:
        if len(cat) >= 2:
            col1_name = st.selectbox("Column 1:", cat, key="ht_cs1")
            col2_name = st.selectbox("Column 2:", [c for c in cat if c != col1_name], key="ht_cs2")
            if st.button("Run", key="ht_cs_run"):
                ct = pd.crosstab(df[col1_name], df[col2_name])
                res = run_chisquare(ct)
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("χ²", f"{res['statistic']:.4f}")
                c2.metric("p-value", f"{res['p_value']:.6f}")
                c3.metric("DoF", res["dof"])
                c4.metric("Cramer's V", f"{res['cramers_v']:.3f}")
                st.info(f"**Conclusion:** {'Variables are related' if res['significant'] else 'No relationship'}")
                fig = px.imshow(
                    ct, text_auto=True, title="Contingency Table", color_continuous_scale="Blues", aspect="auto"
                )
                apply_theme(fig)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Need ≥2 categorical columns")


# ── Linear Regression — via core metrics ──
def _render_regression(df, num):
    if len(num) < 2:
        st.warning("Need ≥2 numeric columns")
        return
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler

    st.markdown("###  Linear Regression (Book Ch.4) — via core")
    target = st.selectbox("Target:", num, key="reg_target")
    features = st.multiselect(
        "Features:",
        [c for c in num if c != target],
        default=[c for c in num if c != target][: min(3, len(num) - 1)],
        key="reg_feats",
    )
    if len(features) >= 1 and st.button("Run Regression", key="reg_run"):
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
            # Use core metrics for detailed report
            y_pred = model.predict(X_test_s)
            metrics = compute_regression_metrics(y_test.values, y_pred)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Train R²", f"{train_r2:.4f}")
            c2.metric("Test R²", f"{test_r2:.4f}")
            c3.metric("RMSE", f"{metrics['rmse']:.3f}")
            c4.metric("MAE", f"{metrics['mae']:.3f}")
            coef_df = pd.DataFrame({"Feature": features, "Coefficient": model.coef_})
            st.dataframe(coef_df, use_container_width=True)
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(x=y_test, y=y_pred, mode="markers", marker=dict(color="#8B5CF6", size=6, opacity=0.6))
            )
            fig.add_trace(
                go.Scatter(
                    x=[y_test.min(), y_test.max()],
                    y=[y_test.min(), y_test.max()],
                    mode="lines",
                    line=dict(color="#EC4899", dash="dash"),
                    name="Perfect Fit",
                )
            )
            fig.update_layout(
                title=f"Actual vs Predicted (R²={test_r2:.4f}, RMSE={metrics['rmse']:.2f})",
                xaxis_title="Actual",
                yaxis_title="Predicted",
                height=350,
            )
            apply_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Need ≥10 samples")
