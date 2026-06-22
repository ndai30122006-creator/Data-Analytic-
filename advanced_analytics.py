"""Advanced Analytics Module — Deep statistical & ML analysis for Data Analyst Pro"""
import warnings

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Optional Imports ────────────────────────────────────────
try:
    from scipy import stats as scipy_stats
    from scipy.stats import (
        ttest_ind, f_oneway, chi2_contingency, shapiro, normaltest,
        kstest, mannwhitneyu, kruskal, probplot
    )
    SCIPY_AVAIL = True
except Exception:
    SCIPY_AVAIL = False

try:
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
    from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
    from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    from sklearn.model_selection import cross_val_score
    from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.svm import SVR
    from sklearn.neighbors import KNeighborsRegressor
    from sklearn.ensemble import (
        RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor,
        ExtraTreesRegressor
    )
    from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression
    from sklearn.metrics.pairwise import cosine_similarity
    from scipy.cluster.hierarchy import linkage as scipy_linkage, dendrogram
    SKLEARN_AVAIL = True
except Exception:
    SKLEARN_AVAIL = False

try:
    from statsmodels.tsa.stattools import adfuller, acf, pacf, kpss
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.stats.diagnostic import acorr_ljungbox
    STATSMODELS_AVAIL = True
except Exception:
    STATSMODELS_AVAIL = False

warnings.filterwarnings("ignore")

# ── Chart Theme (matches app.py) ────────────────────────────
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

def render_kpi(container, label, value, delta=None):
    container.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
                       f'<div class="kpi-value">{value}</div>'
                       f'{"<div class=\"kpi-delta\">" + str(delta) + "</div>" if delta else ""}</div>',
                       unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# 1. ADVANCED STATISTICS — Hypothesis Testing, Normality, etc.
# ═══════════════════════════════════════════════════════════════
def validate_dataframe(df, num, cat, min_rows=5, min_numeric=1):
    """Kiểm tra dataframe có đủ dữ liệu cho phân tích không"""
    if df is None or len(df) == 0:
        st.error("❌ Dataset rỗng")
        return False
    if len(df) < min_rows:
        st.warning(f"⚠️ Cần ít nhất {min_rows} dòng để phân tích (hiện có {len(df)})")
        return False
    if len(num) < min_numeric:
        st.warning(f"⚠️ Cần ít nhất {min_numeric} cột numeric (hiện có {len(num)})")
        return False
    return True

def render_advanced_stats_tab(df, num, cat):
    if not SCIPY_AVAIL:
        st.warning("Install: pip install scipy")
        return
    if not validate_dataframe(df, num, cat):
        return

    st.markdown("### 📊 Thống kê nâng cao (Advanced Statistics)")
    st.caption("Kiểm định giả thuyết, phân phối chuẩn, tương quan nâng cao")

    tabs = st.tabs(["📋 Mô tả chi tiết", "🔬 Kiểm định giả thuyết", "📈 Tương quan nâng cao", "📊 Phân phối"])

    # ── Descriptive Stats ──
    with tabs[0]:
        if num:
            desc = df[num].describe().T
            desc["skewness"] = df[num].skew()
            desc["kurtosis"] = df[num].kurtosis()
            desc["variance"] = df[num].var()
            desc["range"] = df[num].max() - df[num].min()
            desc["cv"] = (df[num].std() / df[num].mean()) * 100  # Coefficient of Variation
            desc["iqr"] = df[num].quantile(0.75) - df[num].quantile(0.25)
            desc["missing"] = df[num].isnull().sum()
            desc["missing_pct"] = (df[num].isnull().sum() / len(df)) * 100

            # Format
            display = desc.copy()
            for c in display.columns:
                if c in ["skewness", "kurtosis", "cv"]:
                    display[c] = display[c].round(2)
                elif c in ["missing_pct"]:
                    display[c] = display[c].round(1).astype(str) + "%"
                elif c != "count":
                    display[c] = display[c].round(4)

            st.dataframe(display, width='stretch', use_container_width=True)

            # Interpretation
            st.markdown("#### 📌 Phát hiện nhanh")
            for c in num:
                skew = df[c].skew()
                kurt = df[c].kurtosis()
                msgs = []
                if abs(skew) > 1:
                    msgs.append(f"⚠️ **{c}**: Lệch {'phải' if skew > 0 else 'trái'} mạnh (skew={skew:.2f})")
                if kurt > 3:
                    msgs.append(f"⚠️ **{c}**: Phân phối nhọn (kurtosis={kurt:.2f}) — nhiều giá trị ngoại lai")
                elif kurt < -1:
                    msgs.append(f"ℹ️ **{c}**: Phân phối dẹt (kurtosis={kurt:.2f})")
                if df[c].isnull().sum() > 0:
                    msgs.append(f"⚠️ **{c}**: {df[c].isnull().sum():,} giá trị thiếu ({df[c].isnull().sum()/len(df)*100:.1f}%)")
                for m in msgs:
                    insight_card("📊", "", m, "warning" if "⚠️" in m else "info")
        else:
            st.info("Không có cột số để phân tích thống kê")

    # ── Hypothesis Testing ──
    with tabs[1]:
        st.markdown("#### 🔬 Kiểm định giả thuyết (Hypothesis Testing)")

        test_type = st.selectbox("Loại kiểm định:", [
            "T-test (2 mẫu độc lập)",
            "T-test (1 mẫu)",
            "ANOVA (nhiều mẫu)",
            "Mann-Whitney U (phi tham số)",
            "Kruskal-Wallis (phi tham số)",
            "Chi-Square (độc lập)"
        ], key="ht_type")

        if "T-test (2 mẫu)" in test_type:
            if len(num) >= 1 and len(cat) >= 1:
                val_col = st.selectbox("Cột giá trị (numeric):", num, key="ht_val")
                grp_col = st.selectbox("Cột nhóm (categorical):", cat, key="ht_grp")
                grps = df[grp_col].dropna().unique()[:5]
                if len(grps) >= 2:
                    g1 = st.selectbox("Nhóm 1:", grps, key="ht_g1")
                    g2 = st.selectbox("Nhóm 2:", [g for g in grps if g != g1], key="ht_g2")
                    if st.button("🔬 Chạy kiểm định", key="ht_run"):
                        s1 = df[df[grp_col] == g1][val_col].dropna()
                        s2 = df[df[grp_col] == g2][val_col].dropna()
                        if len(s1) > 1 and len(s2) > 1:
                            stat, p = ttest_ind(s1, s2, equal_var=False)
                            c1, c2, c3 = st.columns(3)
                            c1.metric("t-statistic", f"{stat:.4f}")
                            c2.metric("p-value", f"{p:.6f}")
                            c3.metric("Kết luận", "Có khác biệt 🎯" if p < 0.05 else "Không có khác biệt ❌")
                            insight_card("📊", "Kết quả",
                                        f"p-value = {p:.6f} {'< 0.05 → Bác bỏ H0: Có sự khác biệt có ý nghĩa thống kê' if p < 0.05 else '≥ 0.05 → Không đủ bằng chứng bác bỏ H0'}",
                                        "good" if p < 0.05 else "info")
                            # Visualization
                            fig = go.Figure()
                            fig.add_trace(go.Violin(y=s1, name=g1, box_visible=True, meanline_visible=True))
                            fig.add_trace(go.Violin(y=s2, name=g2, box_visible=True, meanline_visible=True))
                            fig.update_layout(title=f"So sánh {val_col}: {g1} vs {g2} (p={p:.4f})")
                            apply_theme(fig)
                            st.plotly_chart(fig, width='stretch')
                        else: st.error("Cần ít nhất 2 giá trị mỗi nhóm")
                else: st.warning("Cần ít nhất 2 nhóm")
            else: st.warning("Cần 1 cột numeric + 1 cột categorical")

        elif "1 mẫu" in test_type:
            if num:
                val_col = st.selectbox("Cột giá trị:", num, key="ht_1s")
                mu0 = st.number_input("Giá trị trung bình giả định (μ₀):", value=0.0, key="ht_mu")
                if st.button("🔬 Chạy kiểm định", key="ht_1s_run"):
                    s = df[val_col].dropna()
                    stat, p = scipy_stats.ttest_1samp(s, mu0)
                    c1, c2 = st.columns(2)
                    c1.metric("t-statistic", f"{stat:.4f}")
                    c2.metric("p-value", f"{p:.6f}")
                    mean_val = s.mean()
                    insight_card("📊", "Kết quả",
                                f"Trung bình mẫu = {mean_val:.4f} vs μ₀ = {mu0:.4f}. "
                                f"p = {p:.6f} → {'Bác bỏ H0: Trung bình khác μ₀' if p < 0.05 else 'Không đủ bằng chứng bác bỏ H0'}",
                                "good" if p < 0.05 else "info")
            else: st.warning("Cần cột numeric")

        elif "ANOVA" in test_type:
            if len(num) >= 1 and len(cat) >= 1:
                val_col = st.selectbox("Cột giá trị:", num, key="ht_anova_val")
                grp_col = st.selectbox("Cột nhóm:", cat, key="ht_anova_grp")
                if st.button("🔬 Chạy ANOVA", key="ht_anova_run"):
                    grps = df[grp_col].dropna().unique()
                    groups = [df[df[grp_col] == g][val_col].dropna().values for g in grps if len(df[df[grp_col] == g]) > 1]
                    if len(groups) >= 2:
                        stat, p = f_oneway(*groups)
                        c1, c2 = st.columns(2)
                        c1.metric("F-statistic", f"{stat:.4f}")
                        c2.metric("p-value", f"{p:.6f}")
                        insight_card("📊", "Kết quả ANOVA",
                                    f"p = {p:.6f} → {'Có khác biệt giữa các nhóm' if p < 0.05 else 'Không có khác biệt giữa các nhóm'}",
                                    "good" if p < 0.05 else "info")
                        # Box plot
                        fig = px.box(df, x=grp_col, y=val_col, title=f"ANOVA: {val_col} theo {grp_col}")
                        apply_theme(fig)
                        st.plotly_chart(fig, width='stretch')
                    else: st.error("Cần ít nhất 2 nhóm có dữ liệu")
            else: st.warning("Cần 1 numeric + 1 categorical")

        elif "Mann-Whitney" in test_type:
            if len(num) >= 1 and len(cat) >= 1:
                val_col = st.selectbox("Cột giá trị:", num, key="ht_mw_val")
                grp_col = st.selectbox("Cột nhóm:", cat, key="ht_mw_grp")
                grps = df[grp_col].dropna().unique()[:5]
                if len(grps) >= 2:
                    g1 = st.selectbox("Nhóm 1:", grps, key="ht_mw_g1")
                    g2 = st.selectbox("Nhóm 2:", [g for g in grps if g != g1], key="ht_mw_g2")
                    if st.button("🔬 Chạy Mann-Whitney", key="ht_mw_run"):
                        s1 = df[df[grp_col] == g1][val_col].dropna()
                        s2 = df[df[grp_col] == g2][val_col].dropna()
                        if len(s1) > 1 and len(s2) > 1:
                            stat, p = mannwhitneyu(s1, s2)
                            c1, c2 = st.columns(2)
                            c1.metric("U-statistic", f"{stat:.2f}")
                            c2.metric("p-value", f"{p:.6f}")
                            insight_card("📊", "Kết quả Mann-Whitney",
                                        f"p = {p:.6f} → {'Có khác biệt' if p < 0.05 else 'Không có khác biệt'} (phi tham số)",
                                        "good" if p < 0.05 else "info")
                        else: st.error("Cần ít nhất 2 giá trị mỗi nhóm")
            else: st.warning("Cần 1 numeric + 1 categorical")

        elif "Kruskal" in test_type:
            if len(num) >= 1 and len(cat) >= 1:
                val_col = st.selectbox("Cột giá trị:", num, key="ht_kw_val")
                grp_col = st.selectbox("Cột nhóm:", cat, key="ht_kw_grp")
                if st.button("🔬 Chạy Kruskal-Wallis", key="ht_kw_run"):
                    grps = df[grp_col].dropna().unique()
                    groups = [df[df[grp_col] == g][val_col].dropna().values for g in grps if len(df[df[grp_col] == g]) > 1]
                    if len(groups) >= 2:
                        stat, p = kruskal(*groups)
                        c1, c2 = st.columns(2)
                        c1.metric("H-statistic", f"{stat:.4f}")
                        c2.metric("p-value", f"{p:.6f}")
                        insight_card("📊", "Kết quả Kruskal-Wallis",
                                    f"p = {p:.6f} → {'Có khác biệt' if p < 0.05 else 'Không có khác biệt'} (phi tham số)",
                                    "good" if p < 0.05 else "info")
                    else: st.error("Cần ít nhất 2 nhóm")
            else: st.warning("Cần 1 numeric + 1 categorical")

        elif "Chi-Square" in test_type:
            if len(cat) >= 2:
                c1 = st.selectbox("Cột 1:", cat, key="ht_cs1")
                c2 = st.selectbox("Cột 2:", [c for c in cat if c != c1], key="ht_cs2")
                if st.button("🔬 Chạy Chi-Square", key="ht_cs_run"):
                    ct = pd.crosstab(df[c1], df[c2])
                    stat, p, dof, expected = chi2_contingency(ct)
                    c1, c2, c3 = st.columns(3)
                    c1.metric("χ²-statistic", f"{stat:.4f}")
                    c2.metric("p-value", f"{p:.6f}")
                    c3.metric("Bậc tự do", dof)
                    insight_card("📊", "Kết quả Chi-Square",
                                f"p = {p:.6f} → {'Có mối liên hệ giữa 2 biến' if p < 0.05 else 'Không có mối liên hệ'}",
                                "good" if p < 0.05 else "info")
                    # Heatmap
                    fig = px.imshow(ct, text_auto=True, title=f"Contingency Table: {c1} vs {c2}",
                                   color_continuous_scale="Viridis", aspect='auto')
                    apply_theme(fig)
                    st.plotly_chart(fig, width='stretch')
            else: st.warning("Cần ít nhất 2 cột categorical")

    # ── Advanced Correlation ──
    with tabs[2]:
        if len(num) >= 2:
            st.markdown("#### 📈 Tương quan nâng cao")
            corr_method = st.selectbox("Phương pháp:", ["Pearson", "Spearman", "Kendall"], key="corr_m")
            corr_map = {"Pearson": "pearson", "Spearman": "spearman", "Kendall": "kendall"}
            method = corr_map[corr_method]

            corr = df[num].corr(method=method)

            # Heatmap
            fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r",
                           zmin=-1, zmax=1, title=f"Ma trận tương quan ({corr_method})", aspect='auto')
            fig.update_layout(height=600)
            apply_theme(fig)
            st.plotly_chart(fig, width='stretch')

            # Top correlations
            st.markdown("#### 🔗 Top tương quan mạnh nhất")
            pairs = []
            for i in range(len(num)):
                for j in range(i+1, len(num)):
                    pairs.append((num[i], num[j], corr.iloc[i, j]))
            pairs.sort(key=lambda x: abs(x[2]), reverse=True)

            for a, b, r in pairs[:10]:
                icon = "🟢" if abs(r) > 0.7 else ("🟡" if abs(r) > 0.4 else "⚪")
                insight_card(icon, f"{a} ↔ {b}", f"r = {r:.4f} ({corr_method}) — {'Tương quan mạnh' if abs(r) > 0.7 else 'Tương quan trung bình' if abs(r) > 0.4 else 'Tương quan yếu'}",
                            "good" if abs(r) > 0.7 else "warning" if abs(r) > 0.4 else "info")

            # Partial correlation matrix (scatter matrix for top pairs)
            if len(pairs) > 0:
                top_n = min(5, len(pairs))
                top_vars = list(set([p[0] for p in pairs[:top_n]] + [p[1] for p in pairs[:top_n]]))
                if len(top_vars) >= 2 and len(top_vars) <= 10:
                    fig = px.scatter_matrix(df[top_vars], title="Scatter Matrix — Top tương quan",
                                           dimensions=top_vars, opacity=0.5)
                    fig.update_traces(diagonal_visible=False, showupperhalf=False)
                    fig.update_layout(height=700)
                    apply_theme(fig)
                    st.plotly_chart(fig, width='stretch')
        else:
            st.info("Cần ít nhất 2 cột numeric")

    # ── Distribution Tests ──
    with tabs[3]:
        if num:
            st.markdown("#### 📊 Kiểm định phân phối chuẩn (Normality Tests)")
            sel_col = st.selectbox("Chọn cột:", num, key="norm_col")

            if st.button("📊 Kiểm tra phân phối", key="norm_run"):
                s = df[sel_col].dropna()
                n = len(s)

                # Multiple normality tests
                results = {}
                if n >= 3 and n <= 5000:
                    stat, p = shapiro(s)
                    results["Shapiro-Wilk"] = (stat, p)
                if n >= 8:
                    stat, p = normaltest(s)
                    results["D'Agostino-Pearson"] = (stat, p)
                stat, p = kstest(s, 'norm', args=(s.mean(), s.std()))
                results["Kolmogorov-Smirnov"] = (stat, p)

                cols = st.columns(len(results))
                for i, (name, (stat, p)) in enumerate(results.items()):
                    with cols[i]:
                        st.metric(name, f"p={p:.6f}", delta="Normal ✅" if p > 0.05 else "Không normal ❌",
                                 delta_color="off" if p > 0.05 else "inverse")

                # Visualization
                fig = make_subplots(rows=1, cols=3,
                                   subplot_titles=("Histogram + KDE", "Q-Q Plot", "Box Plot"),
                                   specs=[[{"type": "xy"}, {"type": "xy"}, {"type": "xy"}]])
                
                # Histogram
                fig.add_trace(go.Histogram(x=s, nbinsx=40, name="Histogram", marker_color="#818cf8",
                                          opacity=0.7, showlegend=False), row=1, col=1)
                
                # Q-Q Plot
                (osm, osr), (slope, intercept, r) = probplot(s, dist="norm")
                fig.add_trace(go.Scatter(x=osm, y=osr, mode='markers', name="Q-Q",
                                        marker=dict(color="#818cf8", size=4)), row=1, col=2)
                fig.add_trace(go.Scatter(x=osm, y=slope * osm + intercept, mode='lines',
                                        name="Theoretical", line=dict(color="#f87171", dash="dash")),
                             row=1, col=2)
                
                # Box Plot
                fig.add_trace(go.Box(y=s, name="Box Plot", marker_color="#34d399",
                                    boxmean=True, showlegend=False), row=1, col=3)
                
                fig.update_layout(height=400, title=f"Phân phối của {sel_col}")
                apply_theme(fig)
                st.plotly_chart(fig, width='stretch')

                # Skewness & Kurtosis interpretation
                skew = s.skew()
                kurt = s.kurtosis()
                c1, c2 = st.columns(2)
                c1.metric("Skewness (Độ lệch)", f"{skew:.4f}",
                         delta="Đối xứng" if abs(skew) < 0.5 else "Lệch" if abs(skew) < 1 else "Lệch mạnh")
                c2.metric("Kurtosis (Độ nhọn)", f"{kurt:.4f}",
                         delta="Chuẩn" if abs(kurt) < 0.5 else "Nhọn" if kurt > 0.5 else "Dẹt")
        else:
            st.info("Không có cột numeric để kiểm tra phân phối")


# ═══════════════════════════════════════════════════════════════
# 2. TIME SERIES DEEP ANALYSIS
# ═══════════════════════════════════════════════════════════════
def render_time_series_tab(df, dat, num):
    if not STATSMODELS_AVAIL:
        st.warning("Install: pip install statsmodels")
        return
    if not validate_dataframe(df, num, cat=None, min_rows=10, min_numeric=1):
        return
    if not dat:
        st.warning("⚠️ Không có cột datetime trong dataset")
        return

    st.markdown("### 📈 Phân tích chuỗi thời gian chuyên sâu")
    st.caption("Kiểm định dừng (ADF/KPSS), phân rã mùa vụ, tự tương quan (ACF/PACF)")

    if not dat or not num:
        st.warning("Cần ít nhất 1 cột datetime + 1 cột numeric")
        return

    dc = st.selectbox("Cột thời gian:", dat, key="ts_date")
    vc = st.selectbox("Cột giá trị:", num, key="ts_val")
    freq = st.selectbox("Tần suất:", ["D (Ngày)", "W (Tuần)", "M (Tháng)", "Q (Quý)", "Y (Năm)"], key="ts_freq")
    freq_map = {"D (Ngày)": "D", "W (Tuần)": "W", "M (Tháng)": "M", "Q (Quý)": "Q", "Y (Năm)": "Y"}
    freq_code = freq_map[freq]

    if st.button("📈 Phân tích chuỗi thời gian", key="ts_run"):
        with st.spinner("Đang phân tích chuỗi thời gian..."):
            # Prepare time series
            ts = df.groupby(pd.Grouper(key=dc, freq=freq_code))[vc].sum().dropna()
            if len(ts) < 10:
                st.error(f"Cần ít nhất 10 điểm dữ liệu (hiện có {len(ts)})")
                return

            tabs = st.tabs(["📊 Tổng quan", "🔬 Kiểm định dừng", "📉 Phân rã", "📊 ACF/PACF", "🔮 Dự báo"])

            # ── Overview ──
            with tabs[0]:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=ts.index, y=ts.values, mode='lines+markers',
                                        name=vc, line=dict(color="#818cf8", width=2),
                                        marker=dict(size=4, color="#818cf8")))
                # Add rolling means
                for w, c, l in [(7, "#34d399", "MA-7"), (30, "#fbbf24", "MA-30")]:
                    if len(ts) > w:
                        ma = ts.rolling(w).mean()
                        fig.add_trace(go.Scatter(x=ts.index, y=ma.values, mode='lines',
                                                name=l, line=dict(color=c, width=1.5, dash="dash")))
                fig.update_layout(title=f"Chuỗi thời gian: {vc} (tần suất {freq})", height=450)
                apply_theme(fig)
                st.plotly_chart(fig, width='stretch')

                # Basic stats
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Số điểm", len(ts))
                c2.metric("Trung bình", f"{ts.mean():,.2f}")
                c3.metric("Xu hướng", f"{ts.diff().mean():,.4f}/đơn vị")
                c4.metric("Biến động", f"{ts.std():,.2f}")

            # ── Stationarity Tests ──
            with tabs[1]:
                st.markdown("#### 🔬 Kiểm định tính dừng (Stationarity)")

                # ADF Test
                adf_stat, adf_p, _, _, adf_cv, _ = adfuller(ts.dropna())
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("ADF Statistic", f"{adf_stat:.6f}")
                    st.metric("p-value", f"{adf_p:.6f}")
                    is_stationary = adf_p < 0.05
                    insight_card("📊", "ADF Test",
                                f"p = {adf_p:.6f} → {'Dừng (Stationary) ✅' if is_stationary else 'Không dừng (Non-stationary) ❌ — Cần sai phân'}",
                                "good" if is_stationary else "danger")
                with c2:
                    st.write("**Critical Values:**")
                    for k, v in adf_cv.items():
                        st.write(f"  {k}: {v:.4f}")

                # KPSS Test
                try:
                    kpss_stat, kpss_p, _, kpss_cv = kpss(ts.dropna(), regression='c')
                    st.metric("KPSS Statistic", f"{kpss_stat:.6f}")
                    st.metric("p-value", f"{kpss_p:.6f}")
                    is_trend_stationary = kpss_p >= 0.05
                    insight_card("📊", "KPSS Test",
                                f"p = {kpss_p:.6f} → {'Xu hướng dừng (Trend Stationary) ✅' if is_trend_stationary else 'Không dừng ❌'}",
                                "good" if is_trend_stationary else "danger")
                except:
                    st.warning("KPSS test không khả dụng")

                # Differencing suggestion
                if not is_stationary:
                    st.markdown("#### 💡 Đề xuất: Sai phân bậc 1")
                    ts_diff = ts.diff().dropna()
                    adf_stat2, adf_p2, _, _, _, _ = adfuller(ts_diff)
                    st.metric("ADF sau sai phân bậc 1", f"p = {adf_p2:.6f}",
                             delta="Dừng ✅" if adf_p2 < 0.05 else "Chưa dừng ❌",
                             delta_color="off" if adf_p2 < 0.05 else "inverse")
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=ts_diff.index, y=ts_diff.values, mode='lines',
                                            name="Sai phân bậc 1", line=dict(color="#34d399")))
                    fig.update_layout(title="Chuỗi sau sai phân bậc 1", height=300)
                    apply_theme(fig)
                    st.plotly_chart(fig, width='stretch')

            # ── Decomposition ──
            with tabs[2]:
                st.markdown("#### 📉 Phân rã chuỗi thời gian (Seasonal Decompose)")
                model_type = st.radio("Mô hình:", ["Additive", "Multiplicative"], horizontal=True, key="ts_dec")
                period = st.slider("Chu kỳ mùa vụ:", 2, min(365, len(ts)//2), 
                                  min(12 if freq_code in ["M", "Q"] else 7 if freq_code == "D" else 4, len(ts)//2),
                                  key="ts_period")

                if len(ts) >= period * 2:
                    result = seasonal_decompose(ts.dropna(), model=model_type.lower(), period=period)
                    
                    fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                                       subplot_titles=("Gốc (Original)", "Xu hướng (Trend)", 
                                                      "Mùa vụ (Seasonal)", "Phần dư (Residual)"),
                                       vertical_spacing=0.05)
                    
                    for trace_data, name, color, row in [
                        (ts, "Original", "#818cf8", 1),
                        (result.trend, "Trend", "#34d399", 2),
                        (result.seasonal, "Seasonal", "#fbbf24", 3),
                        (result.resid, "Residual", "#f87171", 4)
                    ]:
                        valid = trace_data.dropna()
                        fig.add_trace(go.Scatter(x=valid.index, y=valid.values, mode='lines',
                                                name=name, line=dict(color=color, width=1.5)),
                                     row=row, col=1)
                    
                    fig.update_layout(height=700, title=f"Phân rã chuỗi thời gian ({model_type}, period={period})")
                    apply_theme(fig)
                    st.plotly_chart(fig, width='stretch')

                    # Residual analysis
                    resid = result.resid.dropna()
                    if len(resid) > 0:
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Phần dư - Mean", f"{resid.mean():.6f}")
                        c2.metric("Phần dư - Std", f"{resid.std():.6f}")
                        c3.metric("Phần dư - % tổng", f"{abs(resid).sum() / ts.sum() * 100:.2f}%")
                        
                        # Ljung-Box test for residual autocorrelation
                        try:
                            lb = acorr_ljungbox(resid, lags=[min(10, len(resid)//2-1)], return_df=True)
                            if not lb.empty:
                                lb_p = lb['lb_pvalue'].iloc[0]
                                insight_card("📊", "Ljung-Box Test (tự tương quan phần dư)",
                                            f"p = {lb_p:.4f} → {'Không có tự tương quan ✅' if lb_p > 0.05 else 'Có tự tương quan ❌'}",
                                            "good" if lb_p > 0.05 else "warning")
                        except: pass
                else:
                    st.error(f"Cần ít nhất {period * 2} điểm dữ liệu")

            # ── ACF/PACF ──
            with tabs[3]:
                st.markdown("#### 📊 Tự tương quan (ACF) & Tự tương quan riêng (PACF)")
                nlags = st.slider("Số lag:", 5, min(40, len(ts)//2-1), min(20, len(ts)//2-1), key="ts_lags")

                acf_vals = acf(ts.dropna(), nlags=nlags)
                pacf_vals = pacf(ts.dropna(), nlags=nlags)
                
                fig = make_subplots(rows=1, cols=2, subplot_titles=(f"ACF (Autocorrelation)", f"PACF (Partial ACF)"))
                
                # ACF
                fig.add_trace(go.Bar(x=list(range(len(acf_vals))), y=acf_vals, name="ACF",
                                    marker_color="#818cf8", showlegend=False), row=1, col=1)
                # Confidence interval ~ 1.96/sqrt(n)
                ci = 1.96 / np.sqrt(len(ts))
                fig.add_hline(y=ci, line_dash="dash", line_color="#f87171", row=1, col=1)
                fig.add_hline(y=-ci, line_dash="dash", line_color="#f87171", row=1, col=1)
                
                # PACF
                fig.add_trace(go.Bar(x=list(range(len(pacf_vals))), y=pacf_vals, name="PACF",
                                    marker_color="#34d399", showlegend=False), row=1, col=2)
                fig.add_hline(y=ci, line_dash="dash", line_color="#f87171", row=1, col=2)
                fig.add_hline(y=-ci, line_dash="dash", line_color="#f87171", row=1, col=2)
                
                fig.update_layout(height=400, title=f"ACF & PACF — {vc}")
                apply_theme(fig)
                st.plotly_chart(fig, width='stretch')

                # Interpretation
                st.markdown("#### 📌 Giải thích")
                # Count significant lags
                sig_acf = sum(1 for v in acf_vals[1:] if abs(v) > ci)
                sig_pacf = sum(1 for v in pacf_vals[1:] if abs(v) > ci)
                insight_card("📊", "Phát hiện",
                            f"ACF: {sig_acf} lag có ý nghĩa | PACF: {sig_pacf} lag có ý nghĩa. "
                            f"{'Dữ liệu có tính mùa vụ rõ rệt 📅' if sig_acf > 3 else 'Dữ liệu ít mùa vụ 📋'}",
                            "info")

            # ── Simple Forecast (Naive + MA) ──
            with tabs[4]:
                st.markdown("#### 🔮 Dự báo đơn giản")
                fwd = st.slider("Số bước dự báo:", 1, min(90, len(ts)), 10, key="ts_fwd")
                
                if st.button("🔮 Dự báo", key="ts_forecast"):
                    # Simple methods: Naive, Seasonal Naive, MA
                    train = ts.iloc[:-fwd] if len(ts) > fwd * 2 else ts
                    test = ts.iloc[-fwd:] if len(ts) > fwd * 2 else None
                    
                    # Naive forecast
                    naive = [train.iloc[-1]] * fwd
                    
                    # Seasonal naive
                    if len(train) > period:
                        seas_naive = [train.iloc[-period + i] if i < period else train.iloc[-period + (i % period)] 
                                     for i in range(fwd)]
                    else:
                        seas_naive = naive
                    
                    # Moving average
                    ma_window = min(period, len(train) // 2)
                    if ma_window > 0:
                        ma_forecast = [train.tail(ma_window).mean()] * fwd
                    else:
                        ma_forecast = naive
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=train.index, y=train.values, mode='lines',
                                            name="Train", line=dict(color="#818cf8", width=2)))
                    
                    if test is not None:
                        fig.add_trace(go.Scatter(x=test.index, y=test.values, mode='lines+markers',
                                                name="Actual", line=dict(color="#fff", width=2, dash="dot"),
                                                marker=dict(size=6, color="#fff")))
                    
                    fwd_idx = pd.date_range(start=train.index[-1] + pd.Timedelta(days=1) if freq_code == "D" 
                                           else train.index[-1] + pd.DateOffset(weeks=1) if freq_code == "W"
                                           else train.index[-1] + pd.DateOffset(months=1),
                                           periods=fwd, freq=freq_code)
                    
                    fig.add_trace(go.Scatter(x=fwd_idx, y=naive, mode='lines+markers',
                                            name="Naive", line=dict(color="#f87171", width=1.5, dash="dash"),
                                            marker=dict(size=5, color="#f87171")))
                    fig.add_trace(go.Scatter(x=fwd_idx, y=seas_naive, mode='lines+markers',
                                            name=f"Seasonal Naive (p={period})",
                                            line=dict(color="#fbbf24", width=1.5, dash="dash"),
                                            marker=dict(size=5, color="#fbbf24")))
                    fig.add_trace(go.Scatter(x=fwd_idx, y=ma_forecast, mode='lines+markers',
                                            name=f"MA-{ma_window}",
                                            line=dict(color="#34d399", width=1.5, dash="dash"),
                                            marker=dict(size=5, color="#34d399")))
                    
                    fig.update_layout(title=f"Dự báo {vc} — {fwd} bước", height=450)
                    apply_theme(fig)
                    st.plotly_chart(fig, width='stretch')

                    # Error metrics if test available
                    if test is not None:
                        st.markdown("#### 📊 Độ chính xác")
                        err_cols = st.columns(3)
                        for i, (name, pred) in enumerate([("Naive", naive), 
                                                         (f"Seasonal Naive", seas_naive),
                                                         (f"MA-{ma_window}", ma_forecast)]):
                            with err_cols[i]:
                                mae = mean_absolute_error(test.values[:len(pred)], pred[:len(test)])
                                rmse = np.sqrt(mean_squared_error(test.values[:len(pred)], pred[:len(test)]))
                                st.metric(f"{name} MAE", f"{mae:,.2f}")
                                st.metric(f"{name} RMSE", f"{rmse:,.2f}")


# ═══════════════════════════════════════════════════════════════
# 3. CLUSTERING ANALYSIS
# ═══════════════════════════════════════════════════════════════
def render_clustering_tab(df, num):
    if not SKLEARN_AVAIL:
        st.warning("Install: pip install scikit-learn")
        return
    if not validate_dataframe(df, num, cat=None, min_rows=10, min_numeric=2):
        return

    st.markdown("### 🧬 Phân cụm dữ liệu (Clustering)")
    st.caption("K-Means, DBSCAN, Hierarchical Clustering với đánh giá chất lượng")

    if len(num) < 2:
        st.warning("Cần ít nhất 2 cột numeric")
        return

    cols = st.multiselect("Chọn cột cho phân cụm:", num, default=num[:min(4, len(num))], key="cl_cols")
    if len(cols) < 2:
        st.warning("Chọn ít nhất 2 cột")
        return

    # Scale data
    X = df[cols].dropna().copy()
    if len(X) < 10:
        st.error("Cần ít nhất 10 mẫu sau khi loại bỏ NaN")
        return

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    method = st.selectbox("Thuật toán:", ["K-Means", "DBSCAN", "Hierarchical (Agglomerative)"], key="cl_method")

    if method == "K-Means":
        max_k = min(15, len(X) - 1)
        n_clusters = st.slider("Số cụm (K):", 2, max_k, min(5, max_k), key="cl_k")
        
        # Elbow & Silhouette
        if st.button("🧬 Chạy K-Means + Đánh giá", key="cl_k_run"):
            with st.spinner("Đang phân cụm..."):
                # Find optimal K
                inertias = []
                sil_scores = []
                k_range = range(2, max_k + 1)
                for k in k_range:
                    km = KMeans(n_clusters=k, random_state=42, n_init=10)
                    labels = km.fit_predict(X_scaled)
                    inertias.append(km.inertia_)
                    if len(set(labels)) > 1:
                        sil_scores.append(silhouette_score(X_scaled, labels))
                    else:
                        sil_scores.append(0)

                # Elbow chart
                fig = make_subplots(rows=1, cols=2, subplot_titles=("Elbow Method", "Silhouette Score"))
                fig.add_trace(go.Scatter(x=list(k_range), y=inertias, mode='lines+markers',
                                        name="Inertia", marker=dict(color="#818cf8", size=8)), row=1, col=1)
                fig.add_trace(go.Scatter(x=list(k_range), y=sil_scores, mode='lines+markers',
                                        name="Silhouette", marker=dict(color="#34d399", size=8)), row=1, col=2)
                fig.update_layout(height=400, title="Tìm K tối ưu")
                apply_theme(fig)
                st.plotly_chart(fig, width='stretch')

                # Best K
                best_k = list(k_range)[np.argmax(sil_scores)]
                insight_card("💡", "K tối ưu",
                            f"Silhouette Score cao nhất tại K = {best_k} (score = {max(sil_scores):.4f})",
                            "good")

                # Run with selected K
                km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                labels = km.fit_predict(X_scaled)
                X["Cluster"] = labels.astype(str)

                # Metrics
                sil = silhouette_score(X_scaled, labels)
                ch = calinski_harabasz_score(X_scaled, labels)
                db = davies_bouldin_score(X_scaled, labels)
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Silhouette Score", f"{sil:.4f}", help="Càng gần 1 càng tốt")
                c2.metric("Calinski-Harabasz", f"{ch:.2f}", help="Càng cao càng tốt")
                c3.metric("Davies-Bouldin", f"{db:.4f}", help="Càng thấp càng tốt")

                # 2D/3D visualization
                if len(cols) >= 2:
                    viz_cols = cols[:2]
                    fig = px.scatter(X, x=viz_cols[0], y=viz_cols[1], color="Cluster",
                                    title=f"K-Means (K={n_clusters}) — {viz_cols[0]} vs {viz_cols[1]}",
                                    color_discrete_sequence=px.colors.qualitative.Set2,
                                    opacity=0.7)
                    # Add centroids
                    centroids = scaler.inverse_transform(km.cluster_centers_)
                    cent_df = pd.DataFrame(centroids, columns=cols)
                    fig.add_trace(go.Scatter(x=cent_df[viz_cols[0]], y=cent_df[viz_cols[1]],
                                            mode='markers', marker=dict(symbol='x', size=15, color='red', line=dict(width=2)),
                                            name="Centroids"))
                    apply_theme(fig)
                    st.plotly_chart(fig, width='stretch')

                # Cluster profiles
                st.markdown("#### 📋 Hồ sơ các cụm (Cluster Profiles)")
                profile = X.groupby("Cluster")[cols].agg(["mean", "std", "count"]).round(2)
                profile.columns = [f"{c[0]}_{c[1]}" for c in profile.columns]
                st.dataframe(profile, width='stretch', use_container_width=True)

    elif method == "DBSCAN":
        eps = st.slider("Epsilon (bán kính):", 0.1, 5.0, 0.5, 0.1, key="cl_eps")
        min_samples = st.slider("Min Samples:", 2, 20, 5, key="cl_ms")
        
        if st.button("🧬 Chạy DBSCAN", key="cl_db_run"):
            with st.spinner("Đang phân cụm DBSCAN..."):
                db = DBSCAN(eps=eps, min_samples=min_samples)
                labels = db.fit_predict(X_scaled)
                X["Cluster"] = labels.astype(str)
                
                n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
                n_noise = list(labels).count(-1)
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Số cụm", n_clusters)
                c2.metric("Nhiễu (Noise)", n_noise)
                c3.metric("Tỷ lệ nhiễu", f"{n_noise/len(labels)*100:.1f}%")
                
                if n_clusters >= 2:
                    sil = silhouette_score(X_scaled[labels != -1], labels[labels != -1])
                    st.metric("Silhouette Score (không tính noise)", f"{sil:.4f}")
                
                if len(cols) >= 2:
                    viz_cols = cols[:2]
                    fig = px.scatter(X, x=viz_cols[0], y=viz_cols[1], color="Cluster",
                                    title=f"DBSCAN (eps={eps}, min_samples={min_samples})",
                                    color_discrete_sequence=px.colors.qualitative.Set2 + ["#000"],
                                    opacity=0.7)
                    apply_theme(fig)
                    st.plotly_chart(fig, width='stretch')

    elif "Hierarchical" in method:
        n_clusters = st.slider("Số cụm:", 2, min(15, len(X)-1), 5, key="cl_hc")
        linkage = st.selectbox("Linkage:", ["ward", "complete", "average", "single"], key="cl_link")
        
        if st.button("🧬 Chạy Hierarchical Clustering", key="cl_hc_run"):
            with st.spinner("Đang phân cụm phân cấp..."):
                hc = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage)
                labels = hc.fit_predict(X_scaled)
                X["Cluster"] = labels.astype(str)
                
                sil = silhouette_score(X_scaled, labels)
                st.metric("Silhouette Score", f"{sil:.4f}")
                
                if len(cols) >= 2:
                    viz_cols = cols[:2]
                    fig = px.scatter(X, x=viz_cols[0], y=viz_cols[1], color="Cluster",
                                    title=f"Hierarchical (K={n_clusters}, {linkage})",
                                    color_discrete_sequence=px.colors.qualitative.Set2,
                                    opacity=0.7)
                    apply_theme(fig)
                    st.plotly_chart(fig, width='stretch')
                
                # Dendrogram-like visualization (distance matrix heatmap)
                st.markdown("#### 🌳 Dendrogram")
                linkage_matrix = scipy_linkage(X_scaled, method=linkage)
                
                fig, ax = plt.subplots(figsize=(10, 5))
                dendrogram(linkage_matrix, ax=ax, color_threshold=0.7 * max(linkage_matrix[:, 2]),
                          above_threshold_color='gray')
                ax.set_title("Dendrogram")
                ax.set_xlabel("Mẫu")
                ax.set_ylabel("Khoảng cách")
                st.pyplot(fig)
                plt.close()


# ═══════════════════════════════════════════════════════════════
# 4. PCA & DIMENSIONALITY REDUCTION
# ═══════════════════════════════════════════════════════════════
def render_pca_tab(df, num):
    if not SKLEARN_AVAIL:
        st.warning("Install: pip install scikit-learn")
        return
    if not validate_dataframe(df, num, cat=None, min_rows=10, min_numeric=2):
        return

    st.markdown("### 🎯 Giảm chiều dữ liệu (PCA & t-SNE)")
    st.caption("Principal Component Analysis, t-SNE visualization")

    if len(num) < 2:
        st.warning("Cần ít nhất 2 cột numeric")
        return

    cols = st.multiselect("Chọn cột:", num, default=num[:min(6, len(num))], key="pca_cols")
    if len(cols) < 2:
        st.warning("Chọn ít nhất 2 cột")
        return

    X = df[cols].dropna().copy()
    if len(X) < 10:
        st.error("Cần ít nhất 10 mẫu")
        return

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    method = st.selectbox("Phương pháp:", ["PCA", "t-SNE", "Cả hai"], key="pca_method")

    if st.button("🎯 Giảm chiều", key="pca_run"):
        with st.spinner("Đang giảm chiều dữ liệu..."):
            if method in ["PCA", "Cả hai"]:
                st.markdown("#### 📊 Principal Component Analysis (PCA)")

                pca = PCA()
                X_pca = pca.fit_transform(X_scaled)

                # Explained variance
                cum_var = np.cumsum(pca.explained_variance_ratio_)
                
                fig = make_subplots(rows=1, cols=2, 
                                   subplot_titles=("Phương sai giải thích", "Tích lũy phương sai"),
                                   specs=[[{"type": "bar"}, {"type": "scatter"}]])
                
                fig.add_trace(go.Bar(x=[f"PC{i+1}" for i in range(len(pca.explained_variance_ratio_))],
                                    y=pca.explained_variance_ratio_,
                                    marker_color="#818cf8", name="Từng PC",
                                    text=[f"{v:.1%}" for v in pca.explained_variance_ratio_],
                                    textposition='outside'), row=1, col=1)
                fig.add_trace(go.Scatter(x=[f"PC{i+1}" for i in range(len(cum_var))], y=cum_var,
                                        mode='lines+markers', marker=dict(color="#34d399", size=8),
                                        name="Tích lũy", line=dict(color="#34d399", width=2)),
                             row=1, col=2)
                fig.add_hline(y=0.8, line_dash="dash", line_color="#f87171", row=1, col=2,
                             annotation_text="80% threshold")
                
                fig.update_layout(height=400, title="Phương sai giải thích bởi PCA")
                apply_theme(fig)
                st.plotly_chart(fig, width='stretch')

                # Number of components for 80% variance
                n_80 = np.argmax(cum_var >= 0.8) + 1
                insight_card("💡", "Số chiều tối ưu",
                            f"Cần {n_80} component để giải thích 80% phương sai (từ {len(cols)} chiều → {n_80} chiều)",
                            "good")

                # 2D PCA plot
                pca_2d = PCA(n_components=2)
                X_pca_2d = pca_2d.fit_transform(X_scaled)
                pca_df = pd.DataFrame({
                    "PC1": X_pca_2d[:, 0],
                    "PC2": X_pca_2d[:, 1]
                })
                
                fig = px.scatter(pca_df, x="PC1", y="PC2",
                                title=f"PCA 2D ({pca_2d.explained_variance_ratio_[0]:.1%} + {pca_2d.explained_variance_ratio_[1]:.1%} = {sum(pca_2d.explained_variance_ratio_):.1%})",
                                opacity=0.6, color_discrete_sequence=["#818cf8"])
                fig.update_traces(marker=dict(size=5))
                apply_theme(fig)
                st.plotly_chart(fig, width='stretch')

                # Loadings
                loadings = pd.DataFrame(
                    pca.components_[:min(4, len(cols))].T,
                    columns=[f"PC{i+1}" for i in range(min(4, len(cols)))],
                    index=cols
                )
                st.markdown("#### 📋 Hệ số tải (Loadings)")
                st.dataframe(loadings.style.background_gradient(cmap="RdBu_r", axis=None), 
                            width='stretch', use_container_width=True)

                # Feature contribution to PC1
                st.markdown("#### 🔑 Đóng góp vào PC1")
                contrib = pd.DataFrame({"Feature": cols, "Contribution": abs(pca.components_[0])})
                contrib = contrib.sort_values("Contribution", ascending=True)
                fig = px.bar(contrib, x="Contribution", y="Feature", orientation='h',
                            title="Feature Contribution to PC1",
                            color="Contribution", color_continuous_scale="Viridis")
                apply_theme(fig)
                st.plotly_chart(fig, width='stretch')

            if method in ["t-SNE", "Cả hai"]:
                st.markdown("#### 🌌 t-SNE Visualization")
                perplexity = st.slider("Perplexity:", 5, min(50, len(X)-1), min(30, len(X)//2), key="tsne_perp")
                
                with st.spinner("Đang tính t-SNE (có thể chậm)..."):
                    tsne = TSNE(n_components=2, perplexity=perplexity, random_state=42)
                    X_tsne = tsne.fit_transform(X_scaled)
                    
                    tsne_df = pd.DataFrame({"t-SNE 1": X_tsne[:, 0], "t-SNE 2": X_tsne[:, 1]})
                    
                    fig = px.scatter(tsne_df, x="t-SNE 1", y="t-SNE 2",
                                    title=f"t-SNE (perplexity={perplexity})",
                                    opacity=0.6, color_discrete_sequence=["#34d399"])
                    fig.update_traces(marker=dict(size=5))
                    apply_theme(fig)
                    st.plotly_chart(fig, width='stretch')


# ═══════════════════════════════════════════════════════════════
# 5. FEATURE ENGINEERING
# ═══════════════════════════════════════════════════════════════
def render_feature_engineering_tab(df, num, cat):
    st.markdown("### 🔧 Kỹ thuật đặc trưng (Feature Engineering)")
    st.caption("Tự động tạo đặc trưng mới từ dữ liệu hiện có")

    tabs = st.tabs(["➕ Tạo đặc trưng", "📐 Scaling & Encoding", "🎯 Feature Selection"])

    with tabs[0]:
        st.markdown("#### ➕ Tạo đặc trưng mới")

        feat_type = st.selectbox("Loại đặc trưng:", [
            "Tương tác (Interaction)",
            "Đa thức (Polynomial)",
            "Binning (Phân nhóm)",
            "Tỷ lệ (Ratio)",
            "Thống kê lăn (Rolling Stats)"
        ], key="fe_type")

        if feat_type == "Tương tác (Interaction)":
            if len(num) >= 2:
                c1 = st.selectbox("Cột 1:", num, key="fe_i1")
                c2 = st.selectbox("Cột 2:", [c for c in num if c != c1], key="fe_i2")
                op = st.selectbox("Phép toán:", ["Nhân (*)", "Chia (/)", "Cộng (+)", "Trừ (-)"], key="fe_op")
                new_name = st.text_input("Tên cột mới:", f"{c1}_{op[0]}_{c2}", key="fe_iname")
                
                if st.button("➕ Tạo", key="fe_i_create"):
                    ops = {"Nhân (*)": lambda a, b: a * b, "Chia (/)": lambda a, b: a / b.replace(0, np.nan),
                           "Cộng (+)": lambda a, b: a + b, "Trừ (-)": lambda a, b: a - b}
                    df[new_name] = ops[op](df[c1], df[c2])
                    st.success(f"✅ Đã tạo cột '{new_name}'")
                    st.dataframe(df[[c1, c2, new_name]].head(10), width='stretch', use_container_width=True)
                    
                    # Show correlation with existing features
                    if new_name in df.select_dtypes(include=[np.number]).columns:
                        corr_with = df[num + [new_name]].corr()[new_name].drop(new_name).abs().sort_values(ascending=False)
                        st.markdown("**Tương quan với các cột khác:**")
                        st.dataframe(corr_with.to_frame("|corr|"), width='stretch')
            else:
                st.warning("Cần ít nhất 2 cột numeric")

        elif feat_type == "Đa thức (Polynomial)":
            if num:
                c = st.selectbox("Cột:", num, key="fe_pc")
                degree = st.slider("Bậc:", 2, 5, 2, key="fe_pd")
                new_name = st.text_input("Tên cột:", f"{c}^{degree}", key="fe_pname")
                if st.button("➕ Tạo", key="fe_p_create"):
                    df[new_name] = df[c] ** degree
                    st.success(f"✅ Đã tạo cột '{new_name}'")
                    st.dataframe(df[[c, new_name]].head(10), width='stretch', use_container_width=True)
            else:
                st.warning("Cần cột numeric")

        elif feat_type == "Binning (Phân nhóm)":
            if num:
                c = st.selectbox("Cột:", num, key="fe_bc")
                n_bins = st.slider("Số nhóm:", 2, 10, 4, key="fe_bn")
                strategy = st.selectbox("Chiến lược:", ["Equal Width", "Equal Frequency (Quantile)", "Custom"], key="fe_bs")
                new_name = st.text_input("Tên cột:", f"{c}_bin", key="fe_bname")
                
                if st.button("➕ Tạo", key="fe_b_create"):
                    if strategy == "Equal Width":
                        df[new_name] = pd.cut(df[c], bins=n_bins, labels=[f"Q{i+1}" for i in range(n_bins)])
                    elif strategy == "Equal Frequency (Quantile)":
                        df[new_name] = pd.qcut(df[c].rank(method='first'), q=n_bins, 
                                              labels=[f"Q{i+1}" for i in range(n_bins)])
                    else:
                        bins = st.text_input("Ngưỡng (cách nhau bằng dấu phẩy):", 
                                            f"{df[c].min():.2f},{df[c].max():.2f}", key="fe_bins_custom")
                        try:
                            bin_vals = [float(x.strip()) for x in bins.split(",")]
                            df[new_name] = pd.cut(df[c], bins=bin_vals)
                        except: st.error("Định dạng không hợp lệ")
                    
                    if new_name in df.columns:
                        st.success(f"✅ Đã tạo cột '{new_name}'")
                        vc = df[new_name].value_counts().sort_index()
                        fig = px.bar(x=vc.index.astype(str), y=vc.values, title=f"Phân bố {new_name}",
                                    color=vc.values, color_continuous_scale="Viridis")
                        apply_theme(fig)
                        st.plotly_chart(fig, width='stretch')
            else:
                st.warning("Cần cột numeric")

        elif feat_type == "Tỷ lệ (Ratio)":
            if len(num) >= 2:
                num_c = st.selectbox("Tử số:", num, key="fe_rn")
                den_c = st.selectbox("Mẫu số:", [c for c in num if c != num_c], key="fe_rd")
                new_name = st.text_input("Tên cột:", f"{num_c}_ratio_{den_c}", key="fe_rname")
                if st.button("➕ Tạo", key="fe_r_create"):
                    df[new_name] = df[num_c] / df[den_c].replace(0, np.nan)
                    st.success(f"✅ Đã tạo cột '{new_name}'")
                    st.dataframe(df[[num_c, den_c, new_name]].head(10), width='stretch', use_container_width=True)
            else:
                st.warning("Cần ít nhất 2 cột numeric")

        elif feat_type == "Thống kê lăn (Rolling Stats)":
            if num:
                c = st.selectbox("Cột:", num, key="fe_rc")
                window = st.slider("Cửa sổ:", 2, 50, 5, key="fe_rw")
                stat = st.selectbox("Thống kê:", ["Mean", "Std", "Min", "Max", "Median", "Sum"], key="fe_rs")
                new_name = st.text_input("Tên cột:", f"{c}_rolling_{stat.lower()}_{window}", key="fe_rname2")
                if st.button("➕ Tạo", key="fe_r_create2"):
                    df[new_name] = df[c].rolling(window=window).agg(stat.lower())
                    st.success(f"✅ Đã tạo cột '{new_name}'")
                    # Show comparison
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(y=df[c].values[:200], mode='lines', name=c, line=dict(color="#818cf8")))
                    fig.add_trace(go.Scatter(y=df[new_name].values[:200], mode='lines', 
                                            name=new_name, line=dict(color="#34d399", width=2)))
                    fig.update_layout(title=f"So sánh: {c} vs {new_name} (window={window})", height=350)
                    apply_theme(fig)
                    st.plotly_chart(fig, width='stretch')
            else:
                st.warning("Cần cột numeric")

    with tabs[1]:
        st.markdown("#### 📐 Scaling & Encoding")
        
        st.info("ℹ️ Các thao tác này tạo bản sao đã biến đổi của dữ liệu gốc")
        
        if num:
            scale_col = st.multiselect("Cột cần Scale:", num, default=num[:min(3, len(num))], key="fe_sc")
            scaler_type = st.selectbox("Phương pháp Scale:", ["StandardScaler (Z-score)", "MinMaxScaler (0-1)"], key="fe_st")
            
            if st.button("📐 Scale", key="fe_scale_run") and scale_col:
                s = StandardScaler() if "Standard" in scaler_type else MinMaxScaler()
                scaled = s.fit_transform(df[scale_col])
                for i, c in enumerate(scale_col):
                    new_name = f"{c}_{'zscore' if 'Standard' in scaler_type else 'minmax'}"
                    df[new_name] = scaled[:, i]
                st.success(f"✅ Đã scale {len(scale_col)} cột")
                st.dataframe(df[[f"{c}_{'zscore' if 'Standard' in scaler_type else 'minmax'}" for c in scale_col]].head(10),
                            width='stretch', use_container_width=True)
        
        if cat:
            st.markdown("---")
            enc_col = st.selectbox("Cột cần Encode:", cat, key="fe_enc")
            if st.button("🔤 Encode", key="fe_enc_run"):
                le = LabelEncoder()
                new_name = f"{enc_col}_encoded"
                df[new_name] = le.fit_transform(df[enc_col].astype(str))
                mapping = dict(zip(le.classes_, le.transform(le.classes_)))
                st.success(f"✅ Đã encode '{enc_col}' → '{new_name}'")
                st.write("**Mapping:**")
                st.json(mapping)
                st.dataframe(df[[enc_col, new_name]].head(10), width='stretch', use_container_width=True)

    with tabs[2]:
        st.markdown("#### 🎯 Feature Selection (Chọn đặc trưng)")
        
        if len(num) >= 3:
            target = st.selectbox("Biến mục tiêu:", num, key="fe_fs_target")
            features = [c for c in num if c != target]
            k = st.slider("Số đặc trưng muốn chọn:", 1, len(features), min(3, len(features)), key="fe_fs_k")
            method = st.selectbox("Phương pháp:", ["f_regression", "Mutual Information"], key="fe_fs_method")
            
            if st.button("🎯 Chọn đặc trưng", key="fe_fs_run"):
                X = df[features].dropna()
                y = df.loc[X.index, target]
                
                if method == "f_regression":
                    selector = SelectKBest(score_func=f_regression, k=k)
                else:
                    selector = SelectKBest(score_func=mutual_info_regression, k=k)
                
                X_selected = selector.fit_transform(X, y)
                scores = selector.scores_
                
                result = pd.DataFrame({"Feature": features, "Score": scores})
                result = result.sort_values("Score", ascending=True)
                
                fig = px.bar(result, x="Score", y="Feature", orientation='h',
                            title=f"Feature Scores ({method}) — Top {k}",
                            color="Score", color_continuous_scale="Viridis")
                apply_theme(fig)
                st.plotly_chart(fig, width='stretch')
                
                selected = result.nlargest(k, "Score")
                st.success(f"✅ Top {k} đặc trưng: {', '.join(selected['Feature'].tolist())}")
                st.dataframe(selected, width='stretch', use_container_width=True)
        else:
            st.warning("Cần ít nhất 3 cột numeric")


# ═══════════════════════════════════════════════════════════════
# 6. MODEL COMPARISON
# ═══════════════════════════════════════════════════════════════
def render_model_comparison_tab(df, num):
    if not SKLEARN_AVAIL:
        st.warning("Install: pip install scikit-learn")
        return
    if not validate_dataframe(df, num, cat=None, min_rows=10, min_numeric=3):
        return

    st.markdown("### 🏆 So sánh mô hình (Model Comparison)")
    st.caption("So sánh nhiều thuật toán với Cross-Validation")

    if len(num) < 3:
        st.warning("Cần ít nhất 3 cột numeric")
        return

    target = st.selectbox("Biến mục tiêu:", num, key="mc_target")
    features = st.multiselect("Đặc trưng:", [c for c in num if c != target],
                             default=[c for c in num if c != target][:min(4, len(num)-1)], key="mc_feats")
    
    if len(features) < 1:
        st.warning("Chọn ít nhất 1 đặc trưng")
        return

    cv_folds = st.slider("Số folds (Cross-Validation):", 2, 10, 5, key="mc_cv")
    test_size = st.slider("Test size:", 0.1, 0.4, 0.2, 0.05, key="mc_ts")

    # Model selection
    st.markdown("#### 🤖 Chọn mô hình để so sánh")
    models_to_compare = st.multiselect(
        "Thuật toán:",
        ["Linear Regression", "Ridge", "Lasso", "ElasticNet",
         "Decision Tree", "Random Forest", "Gradient Boosting", "AdaBoost",
         "Extra Trees", "KNN", "SVR"],
        default=["Linear Regression", "Random Forest", "Gradient Boosting", "Ridge"],
        key="mc_models"
    )

    if st.button("🏆 So sánh mô hình", key="mc_run") and models_to_compare:
        with st.spinner("Đang huấn luyện và đánh giá..."):
            X = df[features].dropna()
            y = df.loc[X.index, target]
            
            if len(X) < 10:
                st.error("Cần ít nhất 10 mẫu")
                return

            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
            
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            model_map = {
                "Linear Regression": LinearRegression(),
                "Ridge": Ridge(alpha=1.0, random_state=42),
                "Lasso": Lasso(alpha=0.01, random_state=42),
                "ElasticNet": ElasticNet(alpha=0.01, l1_ratio=0.5, random_state=42),
                "Decision Tree": DecisionTreeRegressor(max_depth=10, random_state=42),
                "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
                "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
                "AdaBoost": AdaBoostRegressor(n_estimators=50, random_state=42),
                "Extra Trees": ExtraTreesRegressor(n_estimators=100, random_state=42, n_jobs=-1),
                "KNN": KNeighborsRegressor(n_neighbors=5),
                "SVR": SVR(kernel='rbf')
            }

            results = []
            cv_results = {}
            
            for name in models_to_compare:
                model = model_map[name]
                
                # Cross-validation
                try:
                    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=cv_folds, 
                                               scoring='r2', n_jobs=-1)
                    cv_mean = cv_scores.mean()
                    cv_std = cv_scores.std()
                except:
                    cv_mean = cv_std = 0
                
                # Train & Test
                model.fit(X_train_scaled, y_train)
                train_score = model.score(X_train_scaled, y_train)
                test_score = model.score(X_test_scaled, y_test)
                
                results.append({
                    "Model": name,
                    "Train R²": round(train_score, 4),
                    "Test R²": round(test_score, 4),
                    "CV R² (mean)": round(cv_mean, 4),
                    "CV R² (std)": round(cv_std, 4)
                })
                cv_results[name] = cv_scores

            results_df = pd.DataFrame(results).sort_values("Test R²", ascending=False)
            
            # Results table
            st.markdown("#### 📊 Kết quả so sánh")
            st.dataframe(results_df.style.highlight_max(axis=0, color='#22c55e40'),
                        width='stretch', use_container_width=True)

            # Visualization
            fig = go.Figure()
            for name in models_to_compare:
                if name in cv_results and len(cv_results[name]) > 0:
                    fig.add_trace(go.Box(y=cv_results[name], name=name, boxmean=True))
            fig.update_layout(title=f"Cross-Validation Scores ({cv_folds}-fold)", height=400)
            apply_theme(fig)
            st.plotly_chart(fig, width='stretch')

            # Bar chart comparison
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Train R²", x=results_df["Model"], y=results_df["Train R²"],
                                marker_color="#818cf8"))
            fig.add_trace(go.Bar(name="Test R²", x=results_df["Model"], y=results_df["Test R²"],
                                marker_color="#34d399"))
            fig.add_trace(go.Bar(name="CV R²", x=results_df["Model"], y=results_df["CV R² (mean)"],
                                marker_color="#fbbf24"))
            fig.update_layout(title="So sánh R² giữa các mô hình", barmode='group', height=400)
            apply_theme(fig)
            st.plotly_chart(fig, width='stretch')

            # Best model
            best = results_df.iloc[0]
            insight_card("🏆", f"Mô hình tốt nhất: {best['Model']}",
                        f"Test R² = {best['Test R²']:.4f} | CV R² = {best['CV R² (mean)']:.4f} ± {best['CV R² (std)']:.4f}",
                        "good")


# ═══════════════════════════════════════════════════════════════
# 7. DATA QUALITY ADVANCED
# ═══════════════════════════════════════════════════════════════
def render_data_quality_tab(df, num, cat):
    st.markdown("### ✅ Chất lượng dữ liệu nâng cao (Data Quality)")
    st.caption("Phát hiện trùng lặp, kiểm tra schema, phát hiện drift, đánh giá tổng thể")

    tabs = st.tabs(["📋 Tổng quan chất lượng", "🔍 Trùng lặp", "📐 Schema Validation", "📊 Drift Detection"])

    with tabs[0]:
        st.markdown("#### 📋 Điểm chất lượng tổng thể (Data Quality Score)")

        # Calculate quality metrics
        total_cells = df.shape[0] * df.shape[1]
        filled_cells = total_cells - df.isnull().sum().sum()
        completeness = filled_cells / total_cells * 100

        # Uniqueness
        dup_rows = df.duplicated().sum()
        uniqueness = (1 - dup_rows / len(df)) * 100 if len(df) > 0 else 0

        # Consistency (check for mixed types, outliers)
        consistency_issues = 0
        for c in df.columns:
            if df[c].dtype == "object":
                # Check for mixed types in object columns
                types = df[c].apply(type).nunique()
                if types > 2:  # More than just str + nan
                    consistency_issues += 1

        # Validity (outliers in numeric columns)
        outlier_count = 0
        for c in num:
            q1, q3 = df[c].quantile(0.25), df[c].quantile(0.75)
            iqr = q3 - q1
            outliers = ((df[c] < q1 - 1.5 * iqr) | (df[c] > q3 + 1.5 * iqr)).sum()
            outlier_count += outliers

        validity = max(0, 100 - (outlier_count / total_cells * 100) if total_cells > 0 else 0)

        # Overall score
        quality_score = (completeness * 0.3 + uniqueness * 0.25 + validity * 0.25 + 
                        (100 - consistency_issues * 10) * 0.2)

        # Display
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📦 Completeness", f"{completeness:.1f}%")
        c2.metric("🎯 Uniqueness", f"{uniqueness:.1f}%")
        c3.metric("✅ Validity", f"{validity:.1f}%")
        c4.metric("🏆 Overall", f"{quality_score:.1f}%",
                 delta="Tốt ✅" if quality_score >= 80 else "Trung bình ⚠️" if quality_score >= 60 else "Kém ❌",
                 delta_color="off" if quality_score >= 80 else "inverse")

        # Quality bar
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=quality_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Data Quality Score"},
            delta={'reference': 80},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#818cf8"},
                'steps': [
                    {'range': [0, 40], 'color': "#f87171"},
                    {'range': [40, 70], 'color': "#fbbf24"},
                    {'range': [70, 100], 'color': "#34d399"}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))
        fig.update_layout(height=300)
        apply_theme(fig)
        st.plotly_chart(fig, width='stretch')

        # Issues summary
        st.markdown("#### 📌 Vấn đề phát hiện")
        issues = []
        if df.isnull().sum().sum() > 0:
            issues.append(f"⚠️ {df.isnull().sum().sum():,} giá trị thiếu ({completeness:.1f}% đầy đủ)")
        if dup_rows > 0:
            issues.append(f"⚠️ {dup_rows:,} dòng trùng lặp ({uniqueness:.1f}% duy nhất)")
        if outlier_count > 0:
            issues.append(f"⚠️ {outlier_count:,} giá trị ngoại lai (IQR method)")
        if consistency_issues > 0:
            issues.append(f"⚠️ {consistency_issues} cột có kiểu dữ liệu hỗn hợp")
        if not issues:
            issues.append("✅ Dữ liệu sạch, không phát hiện vấn đề!")
        
        for issue in issues:
            insight_card("📊", "", issue, "good" if "✅" in issue else "warning")

    with tabs[1]:
        st.markdown("#### 🔍 Phân tích trùng lặp chi tiết")

        # Exact duplicates
        exact_dups = df.duplicated(keep=False)
        n_exact = exact_dups.sum()
        st.metric("Số dòng trùng lặp chính xác", f"{n_exact:,} ({n_exact/len(df)*100:.1f}%)" if len(df) > 0 else "0")

        if n_exact > 0:
            st.dataframe(df[exact_dups].sort_values(by=df.columns[0]).head(20),
                        width='stretch', use_container_width=True)

        # Partial duplicates (by key columns)
        st.markdown("---")
        st.markdown("#### 🔑 Trùng lặp theo cột khóa")
        key_cols = st.multiselect("Chọn cột khóa:", df.columns.tolist(), key="dq_keycols")
        if key_cols:
            dups = df[df.duplicated(subset=key_cols, keep=False)]
            st.metric(f"Số dòng trùng theo {', '.join(key_cols)}", f"{len(dups):,}")
            if len(dups) > 0:
                st.dataframe(dups.sort_values(by=key_cols).head(20), width='stretch', use_container_width=True)

        # Near duplicates (fuzzy matching - simplified)
        st.markdown("---")
        st.markdown("#### 📏 Trùng lặp gần (Near Duplicates)")
        st.info("ℹ️ Tính năng này so sánh các dòng dựa trên độ tương tự cosine của dữ liệu số")
        
        if len(num) >= 2:
            threshold = st.slider("Ngưỡng tương tự:", 0.9, 1.0, 0.95, 0.01, key="dq_thresh")
            if st.button("🔍 Tìm near duplicates", key="dq_near"):
                with st.spinner("Đang tìm..."):
                    X = df[num].fillna(0).values
                    sim = cosine_similarity(X)
                    sim[np.tril_indices_from(sim)] = 0  # Upper triangle only
                    pairs = np.argwhere(sim > threshold)
                    if len(pairs) > 0:
                        st.warning(f"Tìm thấy {len(pairs)} cặp có độ tương tự > {threshold}")
                        for i, j in pairs[:10]:
                            st.write(f"  • Dòng {i} ↔ Dòng {j}: tương tự = {sim[i, j]:.4f}")
                    else:
                        st.success("✅ Không tìm thấy near duplicates")
        else:
            st.warning("Cần ít nhất 2 cột numeric")

    with tabs[2]:
        st.markdown("#### 📐 Kiểm tra Schema (Schema Validation)")

        st.markdown("**Cấu trúc hiện tại:**")
        schema = pd.DataFrame({
            "Column": df.columns,
            "Type": df.dtypes.astype(str),
            "Non-Null": df.count().values,
            "Null%": (df.isnull().sum().values / len(df) * 100).round(1).astype(str) + "%",
            "Unique": df.nunique().values,
            "Sample": [str(df[c].dropna().iloc[0])[:50] if len(df[c].dropna()) > 0 else "N/A" for c in df.columns]
        })
        st.dataframe(schema, width='stretch', use_container_width=True)

        # Type inference issues
        st.markdown("#### ⚠️ Cảnh báo kiểu dữ liệu")
        for c in df.columns:
            inferred = pd.api.types.infer_dtype(df[c])
            actual = str(df[c].dtype)
            if "string" in inferred and "object" in actual:
                pass  # Normal
            elif "integer" in inferred and "float" in actual:
                # Check if all values are whole numbers
                if df[c].dropna().apply(lambda x: x == int(x)).all():
                    insight_card("⚠️", f"'{c}'", f"Kiểu float nhưng tất cả đều là số nguyên → nên đổi sang int", "warning")
            elif "date" in inferred.lower() and "object" in actual:
                insight_card("⚠️", f"'{c}'", f"Có vẻ là datetime nhưng đang ở dạng object → nên đổi sang datetime", "warning")

    with tabs[3]:
        st.markdown("#### 📊 Phát hiện Drift (Data Drift Detection)")
        st.info("ℹ️ So sánh phân phối giữa 2 nửa của dataset để phát hiện drift")

        if len(num) >= 1:
            split_point = st.slider("Điểm chia (% đầu tiên):", 10, 90, 50, 5, key="dq_split")
            split_idx = int(len(df) * split_point / 100)
            
            if split_idx > 0 and split_idx < len(df):
                df_a = df.iloc[:split_idx]
                df_b = df.iloc[split_idx:]
                
                drift_results = []
                for c in num:
                    a = df_a[c].dropna()
                    b = df_b[c].dropna()
                    if len(a) > 1 and len(b) > 1:
                        try:
                            stat, p = scipy_stats.ks_2samp(a, b)
                            drift_results.append({
                                "Column": c,
                                "KS Statistic": round(stat, 4),
                                "p-value": round(p, 6),
                                "Drift": "⚠️ Yes" if p < 0.05 else "✅ No",
                                "Mean A": round(a.mean(), 4),
                                "Mean B": round(b.mean(), 4)
                            })
                        except: pass
                
                if drift_results:
                    drift_df = pd.DataFrame(drift_results)
                    st.dataframe(drift_df, width='stretch')
                    
                    n_drift = sum(1 for r in drift_results if r["Drift"] == "⚠️ Yes")
                    if n_drift > 0:
                        insight_card("⚠️", f"Phát hiện {n_drift} cột có drift",
                                    f"{n_drift}/{len(drift_results)} cột có phân phối khác nhau giữa 2 nửa dữ liệu",
                                    "danger" if n_drift > len(drift_results)/2 else "warning")
                    else:
                        insight_card("✅", "Không phát hiện drift",
                                    "Phân phối dữ liệu ổn định giữa 2 nửa", "good")
                    
                    # Visualize drifted columns
                    drifted_cols = [r["Column"] for r in drift_results if r["Drift"] == "⚠️ Yes"]
                    if drifted_cols:
                        st.markdown("#### 📈 Phân phối các cột có drift")
                        for c in drifted_cols[:4]:
                            fig = go.Figure()
                            fig.add_trace(go.Histogram(x=df_a[c].dropna(), name=f"First {split_point}%",
                                                      opacity=0.6, marker_color="#818cf8"))
                            fig.add_trace(go.Histogram(x=df_b[c].dropna(), name=f"Last {100-split_point}%",
                                                      opacity=0.6, marker_color="#f87171"))
                            fig.update_layout(title=f"Drift: {c}", barmode='overlay', height=300)
                            apply_theme(fig)
                            st.plotly_chart(fig, width='stretch')
            else:
                st.error("Điểm chia không hợp lệ")
        else:
            st.warning("Cần cột numeric để phát hiện drift")


# ═══════════════════════════════════════════════════════════════
# MAIN RENDER FUNCTION
# ═══════════════════════════════════════════════════════════════
def render_deep_analysis_tab(df, num, cat, dat):
    """Main entry point for the Deep Analysis tab"""
    
    st.markdown("""
    <div class="hero-bg" style="padding: 1.5rem 1rem; margin-bottom: 0.5rem;">
        <div class="hero" style="text-align: center;">
            <h1 style="font-size: 1.8rem; font-weight: 800; background: linear-gradient(135deg, #5b6bf7, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            🧠 Phân tích chuyên sâu
            </h1>
            <p style="color: var(--fg-muted);">Thống kê nâng cao · Chuỗi thời gian · Phân cụm · PCA · Kỹ thuật đặc trưng · So sánh mô hình · Chất lượng dữ liệu</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    deep_tabs = st.tabs([
        "📊 Thống kê nâng cao",
        "📈 Chuỗi thời gian",
        "🧬 Phân cụm",
        "🎯 PCA & t-SNE",
        "🔧 Feature Engineering",
        "🏆 So sánh mô hình",
        "✅ Chất lượng dữ liệu"
    ])

    with deep_tabs[0]:
        render_advanced_stats_tab(df, num, cat)

    with deep_tabs[1]:
        render_time_series_tab(df, dat, num)

    with deep_tabs[2]:
        render_clustering_tab(df, num)

    with deep_tabs[3]:
        render_pca_tab(df, num)

    with deep_tabs[4]:
        render_feature_engineering_tab(df, num, cat)

    with deep_tabs[5]:
        render_model_comparison_tab(df, num)

    with deep_tabs[6]:
        render_data_quality_tab(df, num, cat)