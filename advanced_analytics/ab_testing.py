"""A/B Testing & Power Analysis (Book Ch.3)"""
import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from .base import apply_theme, insight_card


def render_ab_testing_tab(df, num, cat, key_prefix="da"):
    try:
        from scipy import stats as scipy_stats
    except ImportError:
        st.warning("⚠️ Cài đặt: pip install scipy")
        return

    st.markdown("### ⚗️ A/B Testing & Power Analysis")
    st.caption("Thiết kế thử nghiệm, phân tích power, effect size (Book Ch.3)")

    tabs = st.tabs(["🔬 Two-Proportion Test", "📐 Sample Size Calculator", "📊 Power Analysis"])

    with tabs[0]:
        _render_two_proportion_test(df, cat, scipy_stats)

    with tabs[1]:
        _render_sample_size_calculator(scipy_stats)

    with tabs[2]:
        _render_power_analysis(scipy_stats)


def _render_two_proportion_test(df, cat, scipy_stats):
    st.markdown("#### 🔬 Two-Proportion Z-Test")
    if not cat:
        st.warning("Cần cột categorical")
        return
    grp_col = st.selectbox("Cột nhóm (2 groups):", cat, key="da_ab_grp")
    grps = df[grp_col].dropna().unique()[:5]
    if len(grps) < 2:
        st.warning("Cần ít nhất 2 nhóm")
        return
    col1, col2 = st.columns(2)
    with col1:
        g1 = st.selectbox("Group A:", grps, key="da_ab_g1")
        g1_success = st.number_input("Successes A:", min_value=0, value=50, key="da_ab_s1")
        g1_total = st.number_input("Total A:", min_value=1, value=200, key="da_ab_t1")
    with col2:
        g2 = st.selectbox("Group B:", [g for g in grps if g != g1], key="da_ab_g2")
        g2_success = st.number_input("Successes B:", min_value=0, value=60, key="da_ab_s2")
        g2_total = st.number_input("Total B:", min_value=1, value=200, key="da_ab_t2")

    if st.button("🔬 Run A/B Test", key="da_ab_run"):
        p1 = g1_success / g1_total
        p2 = g2_success / g2_total
        p_pool = (g1_success + g2_success) / (g1_total + g2_total)
        se = np.sqrt(p_pool * (1 - p_pool) * (1/g1_total + 1/g2_total))
        z_stat = (p1 - p2) / se if se > 0 else 0
        p_value = 2 * (1 - scipy_stats.norm.cdf(abs(z_stat)))
        h = 2 * np.arcsin(np.sqrt(p1)) - 2 * np.arcsin(np.sqrt(p2))

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Group A Rate", f"{p1:.2%}")
        c2.metric("Group B Rate", f"{p2:.2%}")
        c3.metric("Z-statistic", f"{z_stat:.4f}")
        c4.metric("p-value", f"{p_value:.6f}")
        st.metric("Effect Size (Cohen's h)", f"{abs(h):.4f}",
                 delta="Lớn" if abs(h) > 0.8 else "Trung bình" if abs(h) > 0.5 else "Nhỏ")

        fig = go.Figure()
        fig.add_trace(go.Bar(x=["Group A", "Group B"], y=[p1, p2],
                            text=[f"{p1:.1%}", f"{p2:.1%}"],
                            textposition='outside',
                            marker_color=['#818cf8', '#34d399']))
        fig.update_layout(title="Conversion Rate Comparison", height=350,
                         yaxis_title="Rate", yaxis_tickformat=".0%")
        apply_theme(fig)
        st.plotly_chart(fig, width='stretch')

        result = "CÓ khác biệt có ý nghĩa thống kê 🎯" if p_value < 0.05 else "KHÔNG có khác biệt có ý nghĩa thống kê ❌"
        insight_card("📊", "Kết luận", f"p = {p_value:.6f} → {result}",
                    "good" if p_value < 0.05 else "info")


def _render_sample_size_calculator(scipy_stats):
    st.markdown("#### 📐 Sample Size Calculator (Power Analysis)")
    baseline = st.slider("Baseline conversion rate (%):", 1, 99, 10, 1, key="da_ab_base")
    min_effect = st.slider("Minimum detectable effect (%):", 0.5, 30.0, 5.0, 0.5, key="ab_effect")
    alpha = st.selectbox("Significance level (α):", [0.01, 0.05, 0.10], index=1, key="da_ab_alpha")
    power = st.selectbox("Statistical power (1-β):", [0.80, 0.85, 0.90, 0.95], index=0, key="da_ab_power")

    if st.button("📐 Calculate", key="ab_sample_run"):
        p1 = baseline / 100
        p2 = (baseline + min_effect) / 100
        p_pool = (p1 + p2) / 2
        z_alpha = scipy_stats.norm.ppf(1 - alpha / 2)
        z_beta = scipy_stats.norm.ppf(power)
        n = ((z_alpha * np.sqrt(2 * p_pool * (1 - p_pool)) +
              z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2) / ((p2 - p1) ** 2)
        n = int(np.ceil(n))
        st.success(f"### 📊 Cần {n:,} samples per group (total: {n*2:,})")
        c1, c2, c3 = st.columns(3)
        c1.metric("Baseline", f"{baseline}%")
        c2.metric("Detectable effect", f"{min_effect}%")
        c3.metric("Power", f"{power:.0%}")
        insight_card("💡", "Sample Size",
                    f"Cần {n:,} observations mỗi nhóm (total {n*2:,}) để phát hiện "
                    f"effect {min_effect}% từ baseline {baseline}% với power={power:.0%}, α={alpha}.",
                    "good")


def _render_power_analysis(scipy_stats):
    st.markdown("#### 📊 Power Analysis Curve")
    p_base = st.slider("Baseline rate (%):", 1, 99, 10, 1, key="da_ab_power_base",
                      help="Tỷ lệ chuyển đổi hiện tại")
    n_per_group = st.slider("Sample size per group:", 10, 10000, 500, 10, key="da_ab_power_n")

    if st.button("📊 Generate Power Curve", key="da_ab_power_run"):
        effects = np.linspace(0.01, 0.20, 50)
        p1 = p_base / 100
        z_alpha = scipy_stats.norm.ppf(1 - 0.05 / 2)
        powers = []
        for eff in effects:
            p2 = p1 + eff
            if p2 > 1:
                continue
            p_pool = (p1 + p2) / 2
            try:
                z_beta = (np.sqrt(n_per_group) * abs(p2 - p1) -
                         z_alpha * np.sqrt(2 * p_pool * (1 - p_pool))) / \
                         np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
                powers.append(scipy_stats.norm.cdf(z_beta))
            except:
                powers.append(0)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=effects * 100, y=powers, mode='lines',
                                name=f"n={n_per_group}",
                                line=dict(color="#818cf8", width=2)))
        fig.add_hline(y=0.8, line_dash="dash", line_color="#34d399",
                     annotation_text="Power=80%")
        fig.update_layout(title=f"Power Curve (n={n_per_group}, α=0.05, baseline={p_base}%)",
                        xaxis_title="Effect Size (absolute %)",
                        yaxis_title="Statistical Power", height=400)
        apply_theme(fig)
        st.plotly_chart(fig, width='stretch')