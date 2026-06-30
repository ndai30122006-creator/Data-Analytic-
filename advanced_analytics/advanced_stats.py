"""Advanced Statistics — Hypothesis Testing, Normality, Correlation (Book Ch.2-3)"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .base import apply_theme, insight_card, validate_df

try:
    from scipy import stats as scipy_stats
    from scipy.stats import ttest_ind, ttest_1samp, ttest_rel, f_oneway
    from scipy.stats import mannwhitneyu, kruskal, chi2_contingency
    from scipy.stats import shapiro, normaltest, kstest, probplot
    SCIPY_AVAIL = True
except Exception:
    SCIPY_AVAIL = False


def render_advanced_stats_tab(df, num, cat):
    if not SCIPY_AVAIL:
        st.warning("⚠️ Cài đặt: pip install scipy")
        return
    if not validate_df(df, num, cat):
        return

    st.markdown("### 📊 Thống kê nâng cao (Book Ch.2-3)")
    st.caption("Kiểm định giả thuyết, Effect Size, Power")

    tabs = st.tabs(["🔬 Hypothesis Testing", "📊 Normality", "📈 Correlation"])

    # ── Hypothesis Testing ──
    with tabs[0]:
        test_type = st.selectbox("Loại kiểm định:", [
            "T-test (2 mẫu độc lập)", "T-test (1 mẫu)", "T-test (bắt cặp)",
            "ANOVA (nhiều mẫu)", "Mann-Whitney U (phi tham số)",
            "Kruskal-Wallis (phi tham số)", "Chi-Square (độc lập)"
        ], key="ht_type_adv")

        if "2 mẫu" in test_type:
            _render_ttest_2sample(df, num, cat)
        elif "1 mẫu" in test_type:
            _render_ttest_1sample(df, num)
        elif "bắt cặp" in test_type:
            _render_ttest_paired(df, num)
        elif "ANOVA" in test_type:
            _render_anova(df, num, cat)
        elif "Mann-Whitney" in test_type:
            _render_mannwhitney(df, num, cat)
        elif "Kruskal" in test_type:
            _render_kruskal(df, num, cat)
        elif "Chi-Square" in test_type:
            _render_chisquare(df, cat)

    # ── Normality Tests ──
    with tabs[1]:
        _render_normality(df, num)

    # ── Correlation ──
    with tabs[2]:
        _render_correlation(df, num)


def _render_ttest_2sample(df, num, cat):
    if not (len(num) >= 1 and len(cat) >= 1):
        st.warning("Cần 1 numeric + 1 categorical")
        return
    val_col = st.selectbox("Cột giá trị:", num, key="ht_val_adv")
    grp_col = st.selectbox("Cột nhóm:", cat, key="ht_grp_adv")
    grps = df[grp_col].dropna().unique()[:5]
    if len(grps) < 2:
        st.warning("Cần ≥2 nhóm")
        return
    g1 = st.selectbox("Nhóm 1:", grps, key="ht_g1_adv")
    g2 = st.selectbox("Nhóm 2:", [g for g in grps if g != g1], key="ht_g2_adv")
    if st.button("🔬 Run", key="ht_run_adv"):
        s1 = df[df[grp_col] == g1][val_col].dropna()
        s2 = df[df[grp_col] == g2][val_col].dropna()
        if len(s1) <= 1 or len(s2) <= 1:
            st.error("Cần ≥2 giá trị mỗi nhóm")
            return
        stat, p = ttest_ind(s1, s2, equal_var=False)
        pooled_std = np.sqrt((s1.std()**2 + s2.std()**2) / 2)
        cohens_d = (s1.mean() - s2.mean()) / pooled_std if pooled_std > 0 else 0
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("t-statistic", f"{stat:.4f}")
        c2.metric("p-value", f"{p:.6f}")
        c3.metric("Cohen's d", f"{abs(cohens_d):.4f}")
        c4.metric("Effect", "Lớn 🎯" if abs(cohens_d) > 0.8 else "TB" if abs(cohens_d) > 0.5 else "Nhỏ")
        insight_card("📊", "Kết quả",
                     f"p = {p:.6f} {'< 0.05 → Có khác biệt' if p < 0.05 else '≥ 0.05 → Không có khác biệt'}. "
                     f"Cohen's d = {abs(cohens_d):.3f}",
                     "good" if p < 0.05 else "info")
        fig = go.Figure()
        fig.add_trace(go.Violin(y=s1, name=g1, box_visible=True, meanline_visible=True))
        fig.add_trace(go.Violin(y=s2, name=g2, box_visible=True, meanline_visible=True))
        fig.update_layout(title=f"So sánh {val_col}: {g1} vs {g2} (p={p:.4f}, d={abs(cohens_d):.3f})")
        apply_theme(fig)
        st.plotly_chart(fig, width='stretch')


def _render_ttest_1sample(df, num):
    if not num:
        st.warning("Cần cột numeric")
        return
    val_col = st.selectbox("Cột giá trị:", num, key="ht_1s_adv")
    mu0 = st.number_input("Giá trị giả định (μ₀):", value=0.0, key="ht_mu_adv")
    if st.button("🔬 Run", key="ht_1s_run_adv"):
        s = df[val_col].dropna()
        stat, p = ttest_1samp(s, mu0)
        cohens_d = (s.mean() - mu0) / s.std() if s.std() > 0 else 0
        c1, c2 = st.columns(2)
        c1.metric("t-statistic", f"{stat:.4f}")
        c2.metric("p-value", f"{p:.6f}")
        insight_card("📊", "Kết quả",
                     f"Mean = {s.mean():.4f} vs μ₀ = {mu0:.4f}. Cohen's d = {abs(cohens_d):.3f}. "
                     f"{'Có khác biệt' if p < 0.05 else 'Không có khác biệt'}.",
                     "good" if p < 0.05 else "info")


def _render_ttest_paired(df, num):
    if len(num) < 2:
        st.warning("Cần ≥2 cột numeric")
        return
    c1 = st.selectbox("Cột trước:", num, key="ht_pa_adv")
    c2 = st.selectbox("Cột sau:", [c for c in num if c != c1], key="ht_pb_adv")
    if st.button("🔬 Run", key="ht_p_run_adv"):
        s = df[[c1, c2]].dropna()
        stat, p = ttest_rel(s[c1], s[c2])
        cohens_d = (s[c1] - s[c2]).mean() / (s[c1] - s[c2]).std() if (s[c1] - s[c2]).std() > 0 else 0
        c1, c2 = st.columns(2)
        c1.metric("t-statistic", f"{stat:.4f}")
        c2.metric("p-value", f"{p:.6f}")
        insight_card("📊", "Kết quả", f"Paired t-test: p = {p:.6f}, Cohen's d = {abs(cohens_d):.3f}",
                     "good" if p < 0.05 else "info")


def _render_anova(df, num, cat):
    if not (len(num) >= 1 and len(cat) >= 1):
        st.warning("Cần 1 numeric + 1 categorical")
        return
    val_col = st.selectbox("Cột giá trị:", num, key="ht_anova_val_adv")
    grp_col = st.selectbox("Cột nhóm:", cat, key="ht_anova_grp_adv")
    if st.button("🔬 Run", key="ht_anova_run_adv"):
        grps = df[grp_col].dropna().unique()
        groups = [df[df[grp_col] == g][val_col].dropna().values for g in grps if len(df[df[grp_col] == g]) > 1]
        if len(groups) < 2:
            st.warning("Cần ≥2 nhóm")
            return
        stat, p = f_oneway(*groups)
        all_data = np.concatenate(groups)
        ss_between = sum(len(g) * (np.mean(g) - np.mean(all_data))**2 for g in groups)
        ss_total = sum((g - np.mean(all_data))**2 for g in groups)
        eta_sq = ss_between / ss_total if ss_total > 0 else 0
        c1, c2, c3 = st.columns(3)
        c1.metric("F-statistic", f"{stat:.4f}")
        c2.metric("p-value", f"{p:.6f}")
        c3.metric("η² (Effect Size)", f"{eta_sq:.4f}")
        insight_card("📊", "Kết quả ANOVA",
                     f"p = {p:.6f}. η² = {eta_sq:.4f} {'(Lớn)' if eta_sq > 0.14 else '(TB)' if eta_sq > 0.06 else '(Nhỏ)'}",
                     "good" if p < 0.05 else "info")
        fig = px.box(df, x=grp_col, y=val_col, title=f"ANOVA: {val_col} theo {grp_col}")
        apply_theme(fig)
        st.plotly_chart(fig, width='stretch')


def _render_mannwhitney(df, num, cat):
    if not (len(num) >= 1 and len(cat) >= 1):
        st.warning("Cần 1 numeric + 1 categorical")
        return
    val_col = st.selectbox("Cột giá trị:", num, key="ht_mw_val_adv")
    grp_col = st.selectbox("Cột nhóm:", cat, key="ht_mw_grp_adv")
    grps = df[grp_col].dropna().unique()[:5]
    if len(grps) < 2:
        st.warning("Cần ≥2 nhóm")
        return
    g1 = st.selectbox("Nhóm 1:", grps, key="ht_mw_g1_adv")
    g2 = st.selectbox("Nhóm 2:", [g for g in grps if g != g1], key="ht_mw_g2_adv")
    if st.button("🔬 Run", key="ht_mw_run_adv"):
        s1 = df[df[grp_col] == g1][val_col].dropna()
        s2 = df[df[grp_col] == g2][val_col].dropna()
        if len(s1) <= 1 or len(s2) <= 1:
            st.error("Cần ≥2 giá trị mỗi nhóm")
            return
        stat, p = mannwhitneyu(s1, s2)
        n1, n2 = len(s1), len(s2)
        z = (stat - n1*n2/2) / np.sqrt(n1*n2*(n1+n2+1)/12)
        r = abs(z) / np.sqrt(n1 + n2)
        c1, c2, c3 = st.columns(3)
        c1.metric("U-statistic", f"{stat:.2f}")
        c2.metric("p-value", f"{p:.6f}")
        c3.metric("Effect size (r)", f"{r:.4f}")
        insight_card("📊", "Kết quả", f"Mann-Whitney: p = {p:.6f}, r = {r:.4f}",
                     "good" if p < 0.05 else "info")


def _render_kruskal(df, num, cat):
    if not (len(num) >= 1 and len(cat) >= 1):
        st.warning("Cần 1 numeric + 1 categorical")
        return
    val_col = st.selectbox("Cột giá trị:", num, key="ht_kw_val_adv")
    grp_col = st.selectbox("Cột nhóm:", cat, key="ht_kw_grp_adv")
    if st.button("🔬 Run", key="ht_kw_run_adv"):
        grps = df[grp_col].dropna().unique()
        groups = [df[df[grp_col] == g][val_col].dropna().values for g in grps if len(df[df[grp_col] == g]) > 1]
        if len(groups) < 2:
            st.warning("Cần ≥2 nhóm")
            return
        stat, p = kruskal(*groups)
        c1, c2 = st.columns(2)
        c1.metric("H-statistic", f"{stat:.4f}")
        c2.metric("p-value", f"{p:.6f}")
        insight_card("📊", "Kết quả", f"Kruskal-Wallis: p = {p:.6f}",
                     "good" if p < 0.05 else "info")


def _render_chisquare(df, cat):
    if len(cat) < 2:
        st.warning("Cần ≥2 cột categorical")
        return
    c1 = st.selectbox("Cột 1:", cat, key="ht_cs1_adv")
    c2 = st.selectbox("Cột 2:", [c for c in cat if c != c1], key="ht_cs2_adv")
    if st.button("🔬 Run", key="ht_cs_run_adv"):
        ct = pd.crosstab(df[c1], df[c2])
        stat, p, dof, _expected = chi2_contingency(ct)
        n = ct.sum().sum()
        cramer_v = np.sqrt(stat / (n * min(ct.shape[0]-1, ct.shape[1]-1))) if n > 0 else 0
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("χ²", f"{stat:.4f}")
        c2.metric("p-value", f"{p:.6f}")
        c3.metric("Bậc tự do", dof)
        c4.metric("Cramer's V", f"{cramer_v:.4f}")
        insight_card("📊", "Kết quả",
                     f"Chi-Square: p = {p:.6f}. Cramer's V = {cramer_v:.4f} "
                     f"{'(Mạnh)' if cramer_v > 0.5 else '(TB)' if cramer_v > 0.3 else '(Yếu)'}",
                     "good" if p < 0.05 else "info")
        fig = px.imshow(ct, text_auto=True, title="Contingency Table",
                        color_continuous_scale="Viridis", aspect='auto')
        apply_theme(fig)
        st.plotly_chart(fig, width='stretch')


def _render_normality(df, num):
    if not num:
        st.info("Không có cột numeric")
        return
    st.markdown("#### 📊 Normality Tests (Book Ch.2)")
    sel_col = st.selectbox("Chọn cột:", num, key="norm_col")
    if st.button("📊 Check Distribution", key="norm_run"):
        s = df[sel_col].dropna()
        n = len(s)
        results = {}
        if n >= 3 and n <= 5000:
            stat, p = shapiro(s)
            results["Shapiro-Wilk"] = (stat, p)
        if n >= 8:
            stat, p = normaltest(s)
            results["D'Agostino-Pearson"] = (stat, p)
        stat, p = kstest(s, 'norm', args=(s.mean(), s.std()))
        results["KS"] = (stat, p)
        cols = st.columns(len(results))
        for i, (name, (stat, p)) in enumerate(results.items()):
            with cols[i]:
                st.metric(name, f"p={p:.6f}", delta="Normal ✅" if p > 0.05 else "Not Normal ❌")
        fig = make_subplots(rows=1, cols=3,
                           subplot_titles=("Histogram", "Q-Q Plot", "Box Plot"),
                           specs=[[{"type": "xy"}, {"type": "xy"}, {"type": "xy"}]])
        fig.add_trace(go.Histogram(x=s, nbinsx=40, marker_color="#818cf8", opacity=0.7), row=1, col=1)
        (osm, osr), (slope, intercept, _r) = probplot(s, dist="norm")
        fig.add_trace(go.Scatter(x=osm, y=osr, mode='markers', marker=dict(color="#818cf8", size=4)), row=1, col=2)
        fig.add_trace(go.Scatter(x=osm, y=slope * osm + intercept, mode='lines',
                                line=dict(color="#f87171", dash="dash")), row=1, col=2)
        fig.add_trace(go.Box(y=s, marker_color="#34d399", boxmean=True), row=1, col=3)
        fig.update_layout(height=350)
        apply_theme(fig)
        st.plotly_chart(fig, width='stretch')


def _render_correlation(df, num):
    if len(num) < 2:
        st.info("Cần ít nhất 2 cột numeric")
        return
    st.markdown("#### 📈 Advanced Correlation")
    corr_method = st.selectbox("Method:", ["Pearson", "Spearman", "Kendall"], key="corr_m")
    method_map = {"Pearson": "pearson", "Spearman": "spearman", "Kendall": "kendall"}
    corr = df[num].corr(method=method_map[corr_method])
    fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r",
                   zmin=-1, zmax=1, title=f"Correlation Matrix ({corr_method})", aspect='auto')
    fig.update_layout(height=500)
    apply_theme(fig)
    st.plotly_chart(fig, width='stretch')
    st.markdown("#### 🔗 Top Correlations")
    pairs = []
    for i in range(len(num)):
        for j in range(i+1, len(num)):
            pairs.append((num[i], num[j], corr.iloc[i, j]))
    pairs.sort(key=lambda x: abs(x[2]), reverse=True)
    for a, b, r in pairs[:10]:
        icon = "🟢" if abs(r) > 0.7 else ("🟡" if abs(r) > 0.4 else "⚪")
        insight_card(icon, f"{a} ↔ {b}", f"r = {r:.4f} ({corr_method})",
                     "good" if abs(r) > 0.7 else "warning" if abs(r) > 0.4 else "info")