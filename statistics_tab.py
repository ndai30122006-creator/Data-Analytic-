"""Statistics tab — Hypothesis Tests, Bootstrap, A/B Testing, Regression, Logistic, Naive Bayes, Diagnostics"""
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

logger = logging.getLogger(__name__)


def render_statistics_tab(df, num, cat):
    """Render the Statistics tab with 7 sub-tabs"""
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
    with stats_tabs[1]: _render_bootstrap(df, num)
    with stats_tabs[2]: _render_ab_testing(df, num, cat)
    with stats_tabs[3]: _render_regression(df, num)
    with stats_tabs[4]: _render_logistic(df, num)
    with stats_tabs[5]: _render_naive_bayes_placeholder()
    with stats_tabs[6]: _render_diagnostics_placeholder()


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
                stat, p, dof, expected = chi2_contingency(ct)
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


def _render_bootstrap(df, num):
    if not num:
        st.warning("Need numeric column")
        return
    st.markdown("### 🎲 Bootstrap (Book Ch.2)")
    col = st.selectbox("Column:", num, key="boot_col")
    n_iter = st.slider("Iterations:", 100, 5000, 1000, 100, key="boot_iter")
    conf_level = st.slider("Confidence Level (%):", 80, 99, 95, 1, key="boot_conf")
    if st.button("🎲 Run Bootstrap", key="boot_run"):
        data = df[col].dropna().values
        n = len(data)
        original = np.mean(data)
        np.random.seed(42)
        boot_means = [np.mean(np.random.choice(data, size=n, replace=True)) for _ in range(n_iter)]
        alpha = (100 - conf_level) / 200
        ci_lower = np.percentile(boot_means, alpha * 100)
        ci_upper = np.percentile(boot_means, (1 - alpha) * 100)
        c1, c2, c3 = st.columns(3)
        c1.metric("Mean", f"{original:.4f}")
        c2.metric("Std Error", f"{np.std(boot_means):.4f}")
        c3.metric(f"{conf_level}% CI", f"[{ci_lower:.4f}, {ci_upper:.4f}]")
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=boot_means, nbinsx=50, marker_color="#818cf8", opacity=0.7))
        fig.add_vline(x=original, line_dash="dash", line_color="#34d399", annotation_text=f"Mean={original:.3f}")
        fig.add_vline(x=ci_lower, line_dash="dot", line_color="#f87171", annotation_text=f"Lower={ci_lower:.3f}")
        fig.add_vline(x=ci_upper, line_dash="dot", line_color="#f87171", annotation_text=f"Upper={ci_upper:.3f}")
        fig.update_layout(title=f"Bootstrap Distribution (n={n_iter})", height=400)
        apply_theme(fig)
        st.plotly_chart(fig, width='stretch')


def _render_ab_testing(df, num, cat):
    st.markdown("### ⚗️ A/B Testing (Book Ch.3)")
    tabs_ab = st.tabs(["🔬 Two-Proportion Test", "📐 Sample Size", "📊 Power Curve"])
    with tabs_ab[0]:
        st.markdown("#### Two-Proportion Z-Test")
        col1, col2 = st.columns(2)
        with col1:
            g1_s = st.number_input("Successes A:", min_value=0, value=50, key="ab_s1")
            g1_t = st.number_input("Total A:", min_value=1, value=200, key="ab_t1")
        with col2:
            g2_s = st.number_input("Successes B:", min_value=0, value=60, key="ab_s2")
            g2_t = st.number_input("Total B:", min_value=1, value=200, key="ab_t2")
        if st.button("🔬 Run Test", key="ab_run"):
            from scipy.stats import norm
            p1, p2 = g1_s/g1_t, g2_s/g2_t
            p_pool = (g1_s+g2_s)/(g1_t+g2_t)
            se = np.sqrt(p_pool*(1-p_pool)*(1/g1_t+1/g2_t))
            z = (p1-p2)/se if se > 0 else 0
            p_val = 2*(1-norm.cdf(abs(z)))
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("A Rate", f"{p1:.2%}")
            c2.metric("B Rate", f"{p2:.2%}")
            c3.metric("Z-stat", f"{z:.4f}")
            c4.metric("p-value", f"{p_val:.6f}")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=["A", "B"], y=[p1, p2], text=[f"{p1:.1%}", f"{p2:.1%}"],
                                textposition='outside', marker_color=['#818cf8', '#34d399']))
            fig.update_layout(title="Conversion Rates", height=350)
            apply_theme(fig)
            st.plotly_chart(fig, width='stretch')
            st.info(f"**Conclusion:** {'Significant difference 🎯' if p_val < 0.05 else 'Not significant ❌'}")

    with tabs_ab[1]:
        baseline = st.slider("Baseline (%):", 1, 99, 10, 1, key="ab_base")
        effect = st.slider("Min effect (%):", 0.5, 30.0, 5.0, 0.5, key="ab_eff")
        if st.button("📐 Calculate Sample Size", key="ab_ss"):
            from scipy.stats import norm
            p1, p2 = baseline/100, (baseline+effect)/100
            if abs(p2 - p1) < 1e-9:
                st.error("❌ Effect size must be > 0")
                return
            z_a = norm.ppf(0.975)
            z_b = norm.ppf(0.80)
            n = ((z_a*np.sqrt(2*(p1+p2)/2*(1-(p1+p2)/2)) + z_b*np.sqrt(p1*(1-p1)+p2*(1-p2)))**2) / ((p2-p1)**2)
            n = int(np.ceil(n))
            st.success(f"### 📊 Need {n:,} per group (total: {n*2:,})")

    with tabs_ab[2]:
        from scipy.stats import norm
        n_per = st.slider("Sample size:", 10, 10000, 500, 10, key="ab_power_n")
        base_rate = st.slider("Baseline (%):", 1, 99, 10, 1, key="ab_power_base")
        if st.button("📊 Generate Power Curve", key="ab_power_run"):
            effects = np.linspace(0.01, 0.20, 50)
            p1 = base_rate / 100
            powers = []
            for eff in effects:
                p2 = p1 + eff
                if p2 > 1:
                    continue
                try:
                    z_b = (np.sqrt(n_per)*abs(p2-p1) - norm.ppf(0.975)*np.sqrt(2*(p1+p2)/2*(1-(p1+p2)/2))) / np.sqrt(p1*(1-p1)+p2*(1-p2))
                    powers.append(norm.cdf(z_b))
                except (ValueError, ZeroDivisionError, RuntimeError):
                    logger.warning(f"Power calculation failed for effect={eff:.4f}")
                    powers.append(0)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=effects*100, y=powers, mode='lines', line=dict(color="#818cf8", width=2)))
            fig.add_hline(y=0.8, line_dash="dash", line_color="#34d399", annotation_text="Power=80%")
            fig.update_layout(title=f"Power Curve (n={n_per})", height=350, xaxis_title="Effect Size (%)", yaxis_title="Power")
            apply_theme(fig)
            st.plotly_chart(fig, width='stretch')


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


def _render_logistic(df, num):
    if len(num) < 2:
        st.warning("Need ≥2 numeric columns")
        return
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import confusion_matrix, roc_curve, auc

    st.markdown("### 🔴 Logistic Regression (Book Ch.5)")
    target_col = st.selectbox("Target:", num, key="log_target")
    threshold = st.slider("Threshold:", float(df[target_col].min()), float(df[target_col].max()),
                         float(df[target_col].median()), key="log_thresh")
    y = (df[target_col] > threshold).astype(int)
    features = st.multiselect("Features:", num, default=num[:min(4, len(num))], key="log_feats2")
    if len(features) >= 1 and st.button("🔴 Train", key="log_run2"):
        X = df[features].dropna()
        y_aligned = y.loc[X.index]
        if len(np.unique(y_aligned)) >= 2 and len(X) >= 10:
            X_train, X_test, y_train, y_test = train_test_split(X, y_aligned, test_size=0.3, random_state=42, stratify=y_aligned)
            scaler = StandardScaler()
            X_train_s = scaler.fit_transform(X_train)
            X_test_s = scaler.transform(X_test)
            model = LogisticRegression(random_state=42, max_iter=500)
            model.fit(X_train_s, y_train)
            y_pred = model.predict(X_test_s)
            y_prob = model.predict_proba(X_test_s)[:, 1]
            cm = confusion_matrix(y_test, y_pred)
            tn, fp, fn, tp = cm.ravel()
            accuracy = (tp+tn)/(tp+tn+fp+fn)
            precision = tp/(tp+fp) if (tp+fp) > 0 else 0
            recall = tp/(tp+fn) if (tp+fn) > 0 else 0
            f1 = 2*precision*recall/(precision+recall) if (precision+recall) > 0 else 0
            fpr, tpr, _ = roc_curve(y_test, y_prob)
            auc_score = auc(fpr, tpr)
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Accuracy", f"{accuracy:.2%}")
            c2.metric("Precision", f"{precision:.2%}")
            c3.metric("Recall", f"{recall:.2%}")
            c4.metric("F1", f"{f1:.2%}")
            c5.metric("AUC", f"{auc_score:.3f}")
            fig_cm = px.imshow(cm, text_auto=True, x=["Pred Neg", "Pred Pos"], y=["Actual Neg", "Actual Pos"],
                              color_continuous_scale="Blues", aspect='auto')
            fig_cm.update_layout(height=300, title="Confusion Matrix")
            apply_theme(fig_cm)
            st.plotly_chart(fig_cm, width='stretch')
            fig_roc = go.Figure()
            fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, mode='lines', name=f'ROC (AUC={auc_score:.3f})',
                                        line=dict(color="#818cf8", width=2), fill='tozeroy'))
            fig_roc.add_trace(go.Scatter(x=[0,1], y=[0,1], mode='lines', name='Random',
                                        line=dict(color="#f87171", dash="dash")))
            fig_roc.update_layout(title="ROC Curve", height=300)
            apply_theme(fig_roc)
            st.plotly_chart(fig_roc, width='stretch')


def _render_naive_bayes_placeholder():
    st.markdown("### 🧮 Naive Bayes (Book Ch.5)")
    st.info("Naive Bayes is available in the Deep Analysis tab with full features.")


def _render_diagnostics_placeholder():
    st.markdown("### 🔧 Diagnostics (Book Ch.4)")
    st.info("Regression Diagnostics (VIF, Heteroskedasticity, Durbin-Watson) are available in the Deep Analysis tab.")