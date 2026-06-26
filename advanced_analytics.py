"""Advanced Analytics Module — Practical Statistics for Data Scientists, 2nd Ed"""
import warnings

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Optional Imports ──────────────────────────────────────────────────────────
try:
    from scipy import stats as scipy_stats
    from scipy.stats import (
        ttest_ind, f_oneway, chi2_contingency, shapiro, normaltest,
        kstest, mannwhitneyu, kruskal, probplot, ttest_1samp, ttest_rel,
        pearsonr, spearmanr
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
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc, precision_recall_curve
    from sklearn.model_selection import cross_val_score
    from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet, LogisticRegression
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.svm import SVR
    from sklearn.neighbors import KNeighborsRegressor
    from sklearn.ensemble import (
        RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor,
        ExtraTreesRegressor, RandomForestClassifier
    )
    from sklearn.naive_bayes import GaussianNB, CategoricalNB
    from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression
    from sklearn.metrics.pairwise import cosine_similarity
    from scipy.cluster.hierarchy import linkage as scipy_linkage, dendrogram
    SKLEARN_AVAIL = True
except Exception:
    SKLEARN_AVAIL = False

try:
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    from statsmodels.stats.diagnostic import het_breuschpagan, acorr_ljungbox
    from statsmodels.tsa.stattools import adfuller, acf, pacf, kpss
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.stats.stattools import durbin_watson
    from statsmodels.tools.tools import add_constant
    STATSMODELS_AVAIL = True
except Exception:
    STATSMODELS_AVAIL = False

warnings.filterwarnings("ignore")

# ── Chart Theme ───────────────────────────────────────────────────────────────
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


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: Validate dataframe
# ═══════════════════════════════════════════════════════════════════════════════
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


# ═══════════════════════════════════════════════════════════════════════════════
# 1. BOOTSTRAP & CONFIDENCE INTERVALS (Book Ch.2)
# ═══════════════════════════════════════════════════════════════════════════════
def render_bootstrap_tab(df, num):
    if not SCIPY_AVAIL:
        st.warning("⚠️ Cài đặt: pip install scipy")
        return

    st.markdown("### 🎲 Bootstrap & Confidence Intervals")
    st.caption("Phương pháp resampling để ước lượng độ tin cậy (Book Ch.2)")

    if not num:
        st.warning("Cần cột numeric")
        return

    col = st.selectbox("Chọn cột:", num, key="da_boot_col")
    n_iter = st.slider("Số lần resampling:", 100, 5000, 1000, 100, key="da_boot_iter")
    conf_level = st.slider("Confidence Level (%):", 80, 99, 95, 1, key="da_boot_conf")

    stat_choice = st.selectbox("Thống kê:", ["Mean", "Median", "Std"], key="da_boot_stat")
    stat_map = {"Mean": np.mean, "Median": np.median, "Std": np.std}

    if st.button("🎲 Run Bootstrap", key="da_boot_run"):
        with st.spinner("Đang resampling..."):
            data = df[col].dropna().values
            n = len(data)
            original = stat_map[stat_choice](data)
            
            # Bootstrap
            np.random.seed(42)
            boot_stats = []
            for _ in range(n_iter):
                sample = np.random.choice(data, size=n, replace=True)
                boot_stats.append(stat_map[stat_choice](sample))
            
            boot_stats = np.array(boot_stats)
            alpha = (100 - conf_level) / 200
            ci_lower = np.percentile(boot_stats, alpha * 100)
            ci_upper = np.percentile(boot_stats, (1 - alpha) * 100)
            boot_std = np.std(boot_stats)

            # Display
            c1, c2, c3 = st.columns(3)
            c1.metric(f"Original {stat_choice}", f"{original:.4f}")
            c2.metric("Bootstrap Std Error", f"{boot_std:.4f}")
            c3.metric(f"{conf_level}% CI", f"[{ci_lower:.4f}, {ci_upper:.4f}]")

            # Histogram of bootstrap distribution
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=boot_stats, nbinsx=50, marker_color="#818cf8",
                                      opacity=0.7, name="Bootstrap distribution"))
            fig.add_vline(x=original, line_dash="dash", line_color="#34d399",
                         annotation_text=f"Original={original:.3f}")
            fig.add_vline(x=ci_lower, line_dash="dot", line_color="#f87171",
                         annotation_text=f"CI Lower={ci_lower:.3f}")
            fig.add_vline(x=ci_upper, line_dash="dot", line_color="#f87171",
                         annotation_text=f"CI Upper={ci_upper:.3f}")
            fig.update_layout(title=f"Bootstrap Distribution of {stat_choice} (n_iter={n_iter})",
                            height=400, xaxis_title=stat_choice, yaxis_title="Frequency")
            apply_theme(fig)
            st.plotly_chart(fig, width="stretch")

            insight_card("💡", "Interpretation",
                        f"Với {conf_level}% confidence, {stat_choice.lower()} nằm trong khoảng "
                        f"[{ci_lower:.4f}, {ci_upper:.4f}]. "
                        f"Bootstrap SD = {boot_std:.4f} (Standard Error).",
                        "good")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. A/B TESTING (Book Ch.3)
# ═══════════════════════════════════════════════════════════════════════════════
def render_ab_testing_tab(df, num, cat):
    if not SCIPY_AVAIL:
        st.warning("⚠️ Cài đặt: pip install scipy")
        return

    st.markdown("### ⚗️ A/B Testing & Power Analysis")
    st.caption("Thiết kế thử nghiệm, phân tích power, effect size (Book Ch.3)")

    tabs = st.tabs(["🔬 Two-Proportion Test", "📐 Sample Size Calculator", "📊 Power Analysis"])

    # ── Two-Proportion Test ──
    with tabs[0]:
        st.markdown("#### 🔬 Two-Proportion Z-Test")
        if len(cat) >= 1:
            grp_col = st.selectbox("Cột nhóm (2 groups):", cat, key="da_ab_grp")
            grps = df[grp_col].dropna().unique()[:5]
            if len(grps) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    g1 = st.selectbox("Group A:", grps, key="da_ab_g1")
                    g1_success = st.number_input("Successes A:", min_value=0, value=50, key="da_ab_s1")
                    g1_total = st.number_input("Total A:", min_value=1, value=200, key="da_ab_t1")
                with col2:
                    _g2 = st.selectbox("Group B:", [g for g in grps if g != g1], key="da_ab_g2")
                    g2_success = st.number_input("Successes B:", min_value=0, value=60, key="da_ab_s2")
                    g2_total = st.number_input("Total B:", min_value=1, value=200, key="da_ab_t2")
                
                if st.button("🔬 Run A/B Test", key="da_ab_run"):
                    p1 = g1_success / g1_total
                    p2 = g2_success / g2_total
                    p_pool = (g1_success + g2_success) / (g1_total + g2_total)
                    se = np.sqrt(p_pool * (1 - p_pool) * (1/g1_total + 1/g2_total))
                    z_stat = (p1 - p2) / se if se > 0 else 0
                    p_value = 2 * (1 - scipy_stats.norm.cdf(abs(z_stat)))
                    
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Group A Rate", f"{p1:.2%}")
                    c2.metric("Group B Rate", f"{p2:.2%}")
                    c3.metric("Z-statistic", f"{z_stat:.4f}")
                    c4.metric("p-value", f"{p_value:.6f}")
                    
                    # Effect size (Cohen's h)
                    h = 2 * np.arcsin(np.sqrt(p1)) - 2 * np.arcsin(np.sqrt(p2))
                    st.metric("Effect Size (Cohen's h)", f"{abs(h):.4f}",
                             delta="Lớn" if abs(h) > 0.8 else "Trung bình" if abs(h) > 0.5 else "Nhỏ")
                    
                    # Visualization
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
            else:
                st.warning("Cần ít nhất 2 nhóm")
        else:
            st.warning("Cần cột categorical")

    # ── Sample Size Calculator ──
    with tabs[1]:
        st.markdown("#### 📐 Sample Size Calculator (Power Analysis)")
        baseline = st.slider("Baseline conversion rate (%):", 1, 99, 10, 1, key="da_ab_base")
        min_effect = st.slider("Minimum detectable effect (%):", 0.5, 30.0, 5.0, 0.5, key="ab_effect")
        alpha = st.selectbox("Significance level (α):", [0.01, 0.05, 0.10], index=1, key="da_ab_alpha")
        power = st.selectbox("Statistical power (1-β):", [0.80, 0.85, 0.90, 0.95], index=0, key="da_ab_power")
        
        if st.button("📐 Calculate", key="ab_sample_run"):
            # Using normal approximation
            p1 = baseline / 100
            p2 = (baseline + min_effect) / 100
            p_pool = (p1 + p2) / 2
            z_alpha = scipy_stats.norm.ppf(1 - alpha / 2)
            z_beta = scipy_stats.norm.ppf(power)
            
            n = ((z_alpha * np.sqrt(2 * p_pool * (1 - p_pool)) + 
                  z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2) / ((p2 - p1) ** 2)
            n = int(np.ceil(n))
            
            st.success(f"### 📊 Cần {n:,} samples per group (total: {n*2:,})")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Baseline", f"{baseline}%")
            col2.metric("Detectable effect", f"{min_effect}%")
            col3.metric("Power", f"{power:.0%}")
            
            insight_card("💡", "Sample Size", 
                        f"Cần {n:,} observations mỗi nhóm (total {n*2:,}) để phát hiện "
                        f"effect {min_effect}% từ baseline {baseline}% với power={power:.0%}, α={alpha}.",
                        "good")

    # ── Power Analysis ──
    with tabs[2]:
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
                    power_val = scipy_stats.norm.cdf(z_beta)
                    powers.append(power_val)
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
                            yaxis_title="Statistical Power",
                            height=400)
            apply_theme(fig)
            st.plotly_chart(fig, width='stretch')


# ═══════════════════════════════════════════════════════════════════════════════
# 3. LOGISTIC REGRESSION & CLASSIFICATION (Book Ch.5)
# ═══════════════════════════════════════════════════════════════════════════════
def render_logistic_tab(df, num, cat):
    if not SKLEARN_AVAIL:
        st.warning("⚠️ Cài đặt: pip install scikit-learn")
        return
    if not validate_df(df, num, cat, min_rows=10, min_numeric=1):
        return

    st.markdown("### 🔴 Logistic Regression & Classification")
    st.caption("Phân loại nhị phân, Confusion Matrix, ROC Curve (Book Ch.5)")

    # Create binary target
    target_options = num + cat
    target_col = st.selectbox("Chọn biến mục tiêu (binary):", target_options, key="da_log_target")
    
    # Binarize if needed
    if target_col in num:
        threshold = st.slider("Threshold để tạo binary:", 
                            float(df[target_col].min()), float(df[target_col].max()),
                            float(df[target_col].median()), key="da_log_thresh")
        y = (df[target_col] > threshold).astype(int)
        target_name = f"{target_col} > {threshold:.2f}"
    else:
        vals = df[target_col].dropna().unique()[:5]
        pos_class = st.selectbox("Positive class:", vals, key="log_pos")
        y = (df[target_col] == pos_class).astype(int)
        target_name = f"{target_col} = {pos_class}"

    # Features
    features = st.multiselect("Chọn features:", num, default=num[:min(4, len(num))], key="log_feats")
    
    if len(features) >= 1 and st.button("🔴 Train Logistic Regression", key="log_run"):
        with st.spinner("Đang huấn luyện..."):
            X = df[features].dropna()
            y_aligned = y.loc[X.index]
            
            if len(X) < 10 or len(np.unique(y_aligned)) < 2:
                st.error("Cần ít nhất 10 mẫu và cả 2 classes")
                return
            
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_aligned, test_size=0.3, random_state=42, stratify=y_aligned)
            
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            model = LogisticRegression(random_state=42, max_iter=500)
            model.fit(X_train_scaled, y_train)
            
            # Predictions
            y_pred = model.predict(X_test_scaled)
            y_prob = model.predict_proba(X_test_scaled)[:, 1]
            
            # Metrics
            cm = confusion_matrix(y_test, y_pred)
            tn, fp, fn, tp = cm.ravel()
            
            accuracy = (tp + tn) / (tp + tn + fp + fn)
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            # ROC
            fpr, tpr, _ = roc_curve(y_test, y_prob)
            auc_score = auc(fpr, tpr)
            
            # Display
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Accuracy", f"{accuracy:.2%}")
            col2.metric("Precision", f"{precision:.2%}")
            col3.metric("Recall", f"{recall:.2%}")
            col4.metric("F1-Score", f"{f1:.2%}")
            col5.metric("AUC", f"{auc_score:.3f}")
            
            # Confusion Matrix
            st.markdown("#### 📊 Confusion Matrix")
            fig_cm = px.imshow(cm, text_auto=True, 
                              x=["Predicted Negative", "Predicted Positive"],
                              y=["Actual Negative", "Actual Positive"],
                              color_continuous_scale="Blues", aspect='auto')
            fig_cm.update_layout(height=350)
            apply_theme(fig_cm)
            st.plotly_chart(fig_cm, width='stretch')
            
            # ROC Curve
            st.markdown("#### 📈 ROC Curve")
            fig_roc = go.Figure()
            fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, mode='lines',
                                        name=f'ROC (AUC={auc_score:.3f})',
                                        line=dict(color="#818cf8", width=2),
                                        fill='tozeroy', fillcolor='rgba(129,140,248,0.1)'))
            fig_roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines',
                                        name='Random Classifier',
                                        line=dict(color="#f87171", dash="dash")))
            fig_roc.update_layout(title=f"ROC Curve — {target_name}",
                                 xaxis_title="False Positive Rate (1 - Specificity)",
                                 yaxis_title="True Positive Rate (Sensitivity)",
                                 height=400)
            apply_theme(fig_roc)
            st.plotly_chart(fig_roc, width='stretch')
            
            # Coefficients
            st.markdown("#### 📋 Coefficients")
            coef_df = pd.DataFrame({
                "Feature": features,
                "Coefficient": model.coef_[0],
                "Odds Ratio": np.exp(model.coef_[0])
            })
            st.dataframe(coef_df, width="stretch")
            
            insight_card("💡", "Interpretation",
                        f"Mô hình Logistic đạt Accuracy={accuracy:.1%}, AUC={auc_score:.3f}. "
                        f"Precision={precision:.1%}, Recall={recall:.1%}, F1={f1:.1%}",
                        "good" if auc_score > 0.7 else "warning")
            
            # ── SHAP Explainability ──
            st.markdown("#### 🔮 SHAP Explainability")
            st.caption("SHAP values show how each feature contributes to predictions")
            try:
                import shap
                SHAP_AVAIL = True
            except:
                SHAP_AVAIL = False
            
            if SHAP_AVAIL:
                show_shap = st.checkbox("🔮 Show SHAP Explanation", value=False, key="log_shap")
                if show_shap:
                    with st.spinner("⏳ Computing SHAP values..."):
                        try:
                            # Use a subset of test data for speed
                            sample_size = min(100, len(X_test_scaled))
                            X_sample = X_test_scaled[:sample_size]
                            
                            # Create SHAP explainer
                            explainer = shap.Explainer(model, X_train_scaled)
                            shap_values = explainer(X_sample)
                            
                            # SHAP summary plot (bar)
                            fig, ax = plt.subplots(figsize=(8, 4))
                            shap.summary_plot(shap_values, X_sample, feature_names=features,
                                            plot_type="bar", show=False)
                            ax.set_title("SHAP Feature Importance (Bar)", fontsize=12)
                            plt.tight_layout()
                            st.pyplot(fig)
                            plt.close()
                            
                            # SHAP summary plot (dot)
                            fig, ax = plt.subplots(figsize=(8, 5))
                            shap.summary_plot(shap_values, X_sample, feature_names=features,
                                            show=False)
                            ax.set_title("SHAP Summary (Dot)", fontsize=12)
                            plt.tight_layout()
                            st.pyplot(fig)
                            plt.close()
                            
                            # SHAP waterfall for first prediction
                            st.markdown("##### 📊 SHAP Waterfall (First Prediction)")
                            fig, ax = plt.subplots(figsize=(8, 4))
                            shap.plots.waterfall(shap_values[0], max_display=10, show=False)
                            plt.tight_layout()
                            st.pyplot(fig)
                            plt.close()
                            
                            insight_card("🔮", "SHAP Insights",
                                        f"Top features: {', '.join(features[:3])}. "
                                        f"SHAP explains how each feature pushes prediction away from baseline.",
                                        "good")
                        except Exception as e:
                            st.warning(f"SHAP visualization error: {str(e)}")
            else:
                st.info("Install SHAP: pip install shap")


# ═══════════════════════════════════════════════════════════════════════════════
# 4. NAIVE BAYES (Book Ch.5)
# ═══════════════════════════════════════════════════════════════════════════════
def render_naive_bayes_tab(df, num, cat):
    if not SKLEARN_AVAIL:
        st.warning("⚠️ Cài đặt: pip install scikit-learn")
        return
    if not validate_df(df, num, cat, min_rows=10, min_numeric=1):
        return

    st.markdown("### 🧮 Naive Bayes Classification")
    st.caption("Phân loại xác suất với Gaussian & Categorical Naive Bayes (Book Ch.5)")

    # Target
    target_options = num + cat
    target_col = st.selectbox("Chọn biến mục tiêu:", target_options, key="nb_target")
    
    if target_col in num:
        threshold = st.slider("Threshold:", float(df[target_col].min()), float(df[target_col].max()),
                            float(df[target_col].median()), key="nb_thresh")
        y = (df[target_col] > threshold).astype(int)
    else:
        vals = df[target_col].dropna().unique()[:10]
        if len(vals) < 2:
            st.warning("Cần ít nhất 2 classes")
            return
        pos_class = st.selectbox("Positive class:", vals, key="nb_pos")
        y = (df[target_col] == pos_class).astype(int)
    
    features = st.multiselect("Chọn features:", num, default=num[:min(4, len(num))], key="nb_feats")
    
    if len(features) >= 1 and st.button("🧮 Train Naive Bayes", key="nb_run"):
        with st.spinner("Đang huấn luyện..."):
            X = df[features].dropna()
            y_aligned = y.loc[X.index]
            
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(X, y_aligned, test_size=0.3, random_state=42)
            
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Gaussian NB
            gnb = GaussianNB()
            gnb.fit(X_train_scaled, y_train)
            y_pred = gnb.predict(X_test_scaled)
            y_prob = gnb.predict_proba(X_test_scaled)[:, 1]
            
            # Metrics
            cm = confusion_matrix(y_test, y_pred)
            tn, fp, fn, tp = cm.ravel() if len(cm.ravel()) == 4 else (0, 0, 0, 0)
            
            accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            # ROC
            if len(np.unique(y_test)) == 2:
                fpr, tpr, _ = roc_curve(y_test, y_prob)
                auc_score = auc(fpr, tpr)
            else:
                auc_score = 0
            
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Accuracy", f"{accuracy:.2%}")
            c2.metric("Precision", f"{precision:.2%}")
            c3.metric("Recall", f"{recall:.2%}")
            c4.metric("F1-Score", f"{f1:.2%}")
            c5.metric("AUC", f"{auc_score:.3f}")
            
            # Confusion Matrix
            fig = px.imshow(cm, text_auto=True,
                          x=["Pred Neg", "Pred Pos"],
                          y=["Actual Neg", "Actual Pos"],
                          color_continuous_scale="Purples", aspect='auto')
            fig.update_layout(height=350, title="Confusion Matrix — Naive Bayes")
            apply_theme(fig)
            st.plotly_chart(fig, width='stretch')
            
            # Prior probabilities
            st.markdown("#### 📋 Class Priors")
            priors = pd.DataFrame({
                "Class": ["Negative (0)", "Positive (1)"],
                "Prior Probability": gnb.class_prior_,
                "Theta (mean)": [gnb.theta_[0, 0] if gnb.theta_.shape[1] > 0 else 0,
                                gnb.theta_[1, 0] if gnb.theta_.shape[1] > 0 else 0]
            })
            st.dataframe(priors, width="stretch")


# ═══════════════════════════════════════════════════════════════════════════════
# 5. REGRESSION DIAGNOSTICS (Book Ch.4)
# ═══════════════════════════════════════════════════════════════════════════════
def render_diagnostics_tab(df, num):
    if not STATSMODELS_AVAIL or not SKLEARN_AVAIL:
        st.warning("⚠️ Cài đặt: pip install statsmodels scikit-learn")
        return
    if not validate_df(df, num, None, min_rows=10, min_numeric=2):
        return

    st.markdown("### 🔧 Regression Diagnostics")
    st.caption("Multicollinearity (VIF), Heteroskedasticity, Autocorrelation (Book Ch.4)")

    target = st.selectbox("Biến mục tiêu:", num, key="diag_target")
    features = st.multiselect("Biến độc lập:", [c for c in num if c != target],
                             default=[c for c in num if c != target][:min(3, len(num)-1)], key="diag_feats")
    
    if len(features) >= 1 and st.button("🔧 Run Diagnostics", key="diag_run"):
        with st.spinner("Đang phân tích..."):
            X = df[features].dropna()
            y = df.loc[X.index, target]
            
            if len(X) < 10:
                st.error("Cần ít nhất 10 mẫu")
                return
            
            # Fit model
            X_const = add_constant(X)
            model = LinearRegression()
            model.fit(X, y)
            y_pred = model.predict(X)
            residuals = y - y_pred
            
            tabs = st.tabs(["📊 VIF", "📈 Heteroskedasticity", "📉 Durbin-Watson", "📋 Residuals"])
            
            # ── VIF ──
            with tabs[0]:
                st.markdown("#### 📊 Variance Inflation Factor (VIF)")
                st.caption("Đo lường đa cộng tuyến (Multicollinearity)")
                
                vif_data = pd.DataFrame()
                vif_data["Feature"] = features
                vif_data["VIF"] = [variance_inflation_factor(X_const.values, i+1) for i in range(len(features))]
                vif_data["Tolerance"] = 1 / vif_data["VIF"]
                vif_data["Severe? (VIF>10)"] = vif_data["VIF"].apply(lambda x: "⚠️ Yes" if x > 10 else "✅ No")
                vif_data["Moderate? (VIF>5)"] = vif_data["VIF"].apply(lambda x: "⚠️ Yes" if x > 5 else "✅ No")
                
                st.dataframe(vif_data.style.highlight_max(axis=0, color='#f8717140'), 
                            width="stretch")
                
                max_vif = vif_data["VIF"].max()
                if max_vif > 10:
                    insight_card("⚠️", "Severe Multicollinearity",
                                f"Có VIF={max_vif:.1f} > 10 — nên loại bỏ hoặc kết hợp features",
                                "danger")
                elif max_vif > 5:
                    insight_card("⚠️", "Moderate Multicollinearity",
                                f"Có VIF={max_vif:.1f} > 5 — cần xem xét",
                                "warning")
                else:
                    insight_card("✅", "No Multicollinearity",
                                "Tất cả VIF < 5 — không có đa cộng tuyến đáng kể",
                                "good")
            
            # ── Heteroskedasticity ──
            with tabs[1]:
                st.markdown("#### 📈 Heteroskedasticity Test (Breusch-Pagan)")
                st.caption("Kiểm tra phương sai sai số thay đổi")
                
                try:
                    lm_stat, lm_p, f_stat, f_p = het_breuschpagan(residuals, X_const)
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("LM Statistic", f"{lm_stat:.4f}")
                    c2.metric("LM p-value", f"{lm_p:.6f}")
                    c3.metric("F Statistic", f"{f_stat:.4f}")
                    c4.metric("F p-value", f"{f_p:.6f}")
                    
                    if lm_p < 0.05:
                        insight_card("⚠️", "Heteroskedasticity Detected",
                                    f"p = {lm_p:.6f} < 0.05 — Phương sai sai số thay đổi (cần robust SE)",
                                    "warning")
                    else:
                        insight_card("✅", "Homoskedasticity",
                                    f"p = {lm_p:.4f} ≥ 0.05 — Phương sai sai số đồng đều",
                                    "good")
                    
                    # Residuals vs Fitted plot
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=y_pred, y=residuals, mode='markers',
                                            marker=dict(color="#818cf8", size=6, opacity=0.6),
                                            name="Residuals"))
                    fig.add_hline(y=0, line_dash="dash", line_color="#f87171")
                    fig.update_layout(title="Residuals vs Fitted Values",
                                     xaxis_title="Fitted Values", yaxis_title="Residuals",
                                     height=350)
                    apply_theme(fig)
                    st.plotly_chart(fig, width='stretch')
                except Exception as e:
                    st.warning(f"Breusch-Pagan test không khả dụng: {e}")
            
            # ── Durbin-Watson ──
            with tabs[2]:
                st.markdown("#### 📉 Durbin-Watson Test (Autocorrelation)")
                st.caption("Kiểm tra tự tương quan phần dư")
                
                dw = durbin_watson(residuals)
                st.metric("Durbin-Watson Statistic", f"{dw:.4f}")
                
                insight_card("📊", "Interpretation",
                            f"DW = {dw:.4f}. "
                            f"{'⚠️ Có tự tương quan dương (DW gần 0)' if dw < 1.5 else ''}"
                            f"{'✅ Không có tự tương quan (DW gần 2)' if 1.5 <= dw <= 2.5 else ''}"
                            f"{'⚠️ Có tự tương quan âm (DW gần 4)' if dw > 2.5 else ''}",
                            "good" if 1.5 <= dw <= 2.5 else "warning")
                
                # Histogram of residuals
                fig = go.Figure()
                fig.add_trace(go.Histogram(x=residuals, nbinsx=30, marker_color="#818cf8",
                                          opacity=0.7, name="Residuals"))
                fig.update_layout(title="Distribution of Residuals", height=300,
                                 xaxis_title="Residual", yaxis_title="Frequency")
                apply_theme(fig)
                st.plotly_chart(fig, width='stretch')
            
            # ── Residuals ──
            with tabs[3]:
                st.markdown("#### 📋 Residual Analysis")
                
                r2 = r2_score(y, y_pred)
                mae = mean_absolute_error(y, y_pred)
                rmse = np.sqrt(mean_squared_error(y, y_pred))
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("R²", f"{r2:.4f}")
                c2.metric("MAE", f"{mae:.4f}")
                c3.metric("RMSE", f"{rmse:.4f}")
                c4.metric("Residual Std", f"{residuals.std():.4f}")
                
                # Coefficients
                coef_df = pd.DataFrame({
                    "Feature": ["Intercept"] + features,
                    "Coefficient": [model.intercept_] + list(model.coef_)
                })
                st.dataframe(coef_df, width="stretch")
                
                # Q-Q Plot
                fig = make_subplots(rows=1, cols=2, 
                                   subplot_titles=("Q-Q Plot (Normality)", "Residuals vs Fitted"))
                
                (osm, osr), (slope, intercept, _r) = probplot(residuals, dist="norm")
                fig.add_trace(go.Scatter(x=osm, y=osr, mode='markers',
                                        marker=dict(color="#818cf8", size=4),
                                        showlegend=False), row=1, col=1)
                fig.add_trace(go.Scatter(x=osm, y=slope * osm + intercept, mode='lines',
                                        line=dict(color="#f87171", dash="dash"),
                                        showlegend=False), row=1, col=1)
                
                fig.add_trace(go.Scatter(x=y_pred, y=residuals, mode='markers',
                                        marker=dict(color="#34d399", size=4, opacity=0.6),
                                        showlegend=False), row=1, col=2)
                fig.add_hline(y=0, line_dash="dash", line_color="#f87171", row=1, col=2)
                
                fig.update_layout(height=400, title="Regression Diagnostics")
                apply_theme(fig)
                st.plotly_chart(fig, width='stretch')


# ═══════════════════════════════════════════════════════════════════════════════
# 6. ADVANCED STATISTICS — Hypothesis Testing, Normality (Book Ch.2-3)
# ═══════════════════════════════════════════════════════════════════════════════
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
        "T-test (2 mẫu độc lập)",
        "T-test (1 mẫu)",
        "T-test (bắt cặp)",
        "ANOVA (nhiều mẫu)",
        "Mann-Whitney U (phi tham số)",
        "Kruskal-Wallis (phi tham số)",
        "Chi-Square (độc lập)"
    ], key="ht_type_adv")

        if "T-test (2 mẫu)" in test_type:
            if len(num) >= 1 and len(cat) >= 1:
                val_col = st.selectbox("Cột giá trị:", num, key="ht_val_adv")
                grp_col = st.selectbox("Cột nhóm:", cat, key="ht_grp_adv")
                grps = df[grp_col].dropna().unique()[:5]
                if len(grps) >= 2:
                    g1 = st.selectbox("Nhóm 1:", grps, key="ht_g1_adv")
                    g2 = st.selectbox("Nhóm 2:", [g for g in grps if g != g1], key="ht_g2_adv")
                    if st.button("🔬 Run", key="ht_run_adv"):
                        s1 = df[df[grp_col] == g1][val_col].dropna()
                        s2 = df[df[grp_col] == g2][val_col].dropna()
                        if len(s1) > 1 and len(s2) > 1:
                            stat, p = ttest_ind(s1, s2, equal_var=False)
                            # Effect size (Cohen's d)
                            pooled_std = np.sqrt((s1.std()**2 + s2.std()**2) / 2)
                            cohens_d = (s1.mean() - s2.mean()) / pooled_std if pooled_std > 0 else 0
                            
                            c1, c2, c3, c4 = st.columns(4)
                            c1.metric("t-statistic", f"{stat:.4f}")
                            c2.metric("p-value", f"{p:.6f}")
                            c3.metric("Cohen's d", f"{abs(cohens_d):.4f}")
                            c4.metric("Effect", "Lớn 🎯" if abs(cohens_d) > 0.8 else "TB" if abs(cohens_d) > 0.5 else "Nhỏ")
                            
                            insight_card("📊", "Kết quả",
                                        f"p = {p:.6f} {'< 0.05 → Có khác biệt có ý nghĩa' if p < 0.05 else '≥ 0.05 → Không có khác biệt'}. "
                                        f"Cohen's d = {abs(cohens_d):.3f}",
                                        "good" if p < 0.05 else "info")
                            
                            fig = go.Figure()
                            fig.add_trace(go.Violin(y=s1, name=g1, box_visible=True, meanline_visible=True))
                            fig.add_trace(go.Violin(y=s2, name=g2, box_visible=True, meanline_visible=True))
                            fig.update_layout(title=f"So sánh {val_col}: {g1} vs {g2} (p={p:.4f}, d={abs(cohens_d):.3f})")
                            apply_theme(fig)
                            st.plotly_chart(fig, width='stretch')
                        else: st.error("Cần ít nhất 2 giá trị mỗi nhóm")
        elif "1 mẫu" in test_type:
            if num:
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

        elif "bắt cặp" in test_type:
            if len(num) >= 2:
                c1 = st.selectbox("Cột trước:", num, key="ht_pa_adv")
                c2 = st.selectbox("Cột sau:", [c for c in num if c != c1], key="ht_pb_adv")
                if st.button("🔬 Run", key="ht_p_run_adv"):
                    s = df[[c1, c2]].dropna()
                    stat, p = ttest_rel(s[c1], s[c2])
                    cohens_d = (s[c1] - s[c2]).mean() / (s[c1] - s[c2]).std() if (s[c1] - s[c2]).std() > 0 else 0
                    c1, c2 = st.columns(2)
                    c1.metric("t-statistic", f"{stat:.4f}")
                    c2.metric("p-value", f"{p:.6f}")
                    insight_card("📊", "Kết quả",
                                f"Paired t-test: p = {p:.6f}, Cohen's d = {abs(cohens_d):.3f}",
                                "good" if p < 0.05 else "info")

        elif "ANOVA" in test_type:
            if len(num) >= 1 and len(cat) >= 1:
                val_col = st.selectbox("Cột giá trị:", num, key="ht_anova_val_adv")
                grp_col = st.selectbox("Cột nhóm:", cat, key="ht_anova_grp_adv")
                if st.button("🔬 Run", key="ht_anova_run_adv"):
                    grps = df[grp_col].dropna().unique()
                    groups = [df[df[grp_col] == g][val_col].dropna().values for g in grps if len(df[df[grp_col] == g]) > 1]
                    if len(groups) >= 2:
                        stat, p = f_oneway(*groups)
                        # Eta-squared
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

        elif "Mann-Whitney" in test_type:
            if len(num) >= 1 and len(cat) >= 1:
                val_col = st.selectbox("Cột giá trị:", num, key="ht_mw_val_adv")
                grp_col = st.selectbox("Cột nhóm:", cat, key="ht_mw_grp_adv")
                grps = df[grp_col].dropna().unique()[:5]
                if len(grps) >= 2:
                    g1 = st.selectbox("Nhóm 1:", grps, key="ht_mw_g1_adv")
                    g2 = st.selectbox("Nhóm 2:", [g for g in grps if g != g1], key="ht_mw_g2_adv")
                    if st.button("🔬 Run", key="ht_mw_run_adv"):
                        s1 = df[df[grp_col] == g1][val_col].dropna()
                        s2 = df[df[grp_col] == g2][val_col].dropna()
                        if len(s1) > 1 and len(s2) > 1:
                            stat, p = mannwhitneyu(s1, s2)
                            # Effect size r = Z / sqrt(N)
                            n1, n2 = len(s1), len(s2)
                            z = (stat - n1*n2/2) / np.sqrt(n1*n2*(n1+n2+1)/12)
                            r = abs(z) / np.sqrt(n1 + n2)
                            
                            c1, c2, c3 = st.columns(3)
                            c1.metric("U-statistic", f"{stat:.2f}")
                            c2.metric("p-value", f"{p:.6f}")
                            c3.metric("Effect size (r)", f"{r:.4f}")
                            insight_card("📊", "Kết quả",
                                        f"Mann-Whitney: p = {p:.6f}, r = {r:.4f}",
                                        "good" if p < 0.05 else "info")

        elif "Chi-Square" in test_type:
            if len(cat) >= 2:
                c1 = st.selectbox("Cột 1:", cat, key="ht_cs1_adv")
                c2 = st.selectbox("Cột 2:", [c for c in cat if c != c1], key="ht_cs2_adv")
                if st.button("🔬 Run", key="ht_cs_run_adv"):
                    ct = pd.crosstab(df[c1], df[c2])
                    stat, p, dof, _expected = chi2_contingency(ct)
                    # Cramer's V
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
                    
                    fig = px.imshow(ct, text_auto=True, title=f"Contingency Table",
                                   color_continuous_scale="Viridis", aspect='auto')
                    apply_theme(fig)
                    st.plotly_chart(fig, width='stretch')

        else:
            st.warning("Chưa implement")

    # ── Normality Tests ──
    with tabs[1]:
        if not num:
            st.info("Không có cột numeric")
        else:
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
                
                # Visualization
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

    # ── Correlation ──
    with tabs[2]:
        if len(num) >= 2:
            st.markdown("#### 📈 Advanced Correlation")
            corr_method = st.selectbox("Method:", ["Pearson", "Spearman", "Kendall"], key="corr_m")
            method_map = {"Pearson": "pearson", "Spearman": "spearman", "Kendall": "kendall"}
            
            corr = df[num].corr(method=method_map[corr_method])
            
            fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r",
                           zmin=-1, zmax=1, title=f"Correlation Matrix ({corr_method})", aspect='auto')
            fig.update_layout(height=500)
            apply_theme(fig)
            st.plotly_chart(fig, width='stretch')
            
            # Top correlations
            st.markdown("#### 🔗 Top Correlations")
            pairs = []
            for i in range(len(num)):
                for j in range(i+1, len(num)):
                    pairs.append((num[i], num[j], corr.iloc[i, j]))
            pairs.sort(key=lambda x: abs(x[2]), reverse=True)
            
            for a, b, r in pairs[:10]:
                icon = "🟢" if abs(r) > 0.7 else ("🟡" if abs(r) > 0.4 else "⚪")
                insight_card(icon, f"{a} ↔ {b}",
                            f"r = {r:.4f} ({corr_method})",
                            "good" if abs(r) > 0.7 else "warning" if abs(r) > 0.4 else "info")
        else:
            st.info("Cần ít nhất 2 cột numeric")


# ═══════════════════════════════════════════════════════════════════════════════
# 7. CLUSTERING (Book Ch.6)
# ═══════════════════════════════════════════════════════════════════════════════
def render_clustering_tab(df, num):
    if not SKLEARN_AVAIL:
        st.warning("⚠️ Cài đặt: pip install scikit-learn")
        return
    if not validate_df(df, num, None, min_rows=10, min_numeric=2):
        return

    st.markdown("### 🧬 Clustering (Book Ch.6)")
    st.caption("K-Means, DBSCAN, Hierarchical")

    if len(num) < 2:
        st.warning("Cần ít nhất 2 cột numeric")
        return

    cols = st.multiselect("Columns:", num, default=num[:min(4, len(num))], key="cl_cols")
    if len(cols) < 2:
        st.warning("Chọn ít nhất 2 cột")
        return

    X = df[cols].dropna().copy()
    if len(X) < 10:
        st.error("Cần ít nhất 10 mẫu")
        return

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    method = st.selectbox("Algorithm:", ["K-Means", "DBSCAN", "Hierarchical"], key="cl_method")

    if method == "K-Means":
        max_k = min(15, len(X) - 1)
        n_clusters = st.slider("K:", 2, max_k, min(5, max_k), key="cl_k")
        if st.button("🧬 Run", key="cl_k_run"):
            with st.spinner("..."):
                km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                labels = km.fit_predict(X_scaled)
                X["Cluster"] = labels.astype(str)
                
                sil = silhouette_score(X_scaled, labels)
                ch = calinski_harabasz_score(X_scaled, labels)
                db = davies_bouldin_score(X_scaled, labels)
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Silhouette", f"{sil:.4f}")
                c2.metric("Calinski-Harabasz", f"{ch:.2f}")
                c3.metric("Davies-Bouldin", f"{db:.4f}")
                
                if len(cols) >= 2:
                    fig = px.scatter(X, x=cols[0], y=cols[1], color="Cluster",
                                    title=f"K-Means (K={n_clusters})",
                                    color_discrete_sequence=px.colors.qualitative.Set2)
                    centroids = scaler.inverse_transform(km.cluster_centers_)
                    cent_df = pd.DataFrame(centroids, columns=cols)
                    fig.add_trace(go.Scatter(x=cent_df[cols[0]], y=cent_df[cols[1]],
                                            mode='markers', marker=dict(symbol='x', size=12, color='red'),
                                            name="Centroids"))
                    apply_theme(fig)
                    st.plotly_chart(fig, width='stretch')
                
                profile = X.groupby("Cluster")[cols].agg(["mean", "std", "count"]).round(2)
                st.dataframe(profile, width="stretch")

    elif method == "DBSCAN":
        eps = st.slider("Epsilon:", 0.1, 5.0, 0.5, 0.1, key="cl_eps")
        min_samples = st.slider("Min Samples:", 2, 20, 5, key="cl_ms")
        if st.button("🧬 Run", key="cl_db_run"):
            db = DBSCAN(eps=eps, min_samples=min_samples)
            labels = db.fit_predict(X_scaled)
            X["Cluster"] = labels.astype(str)
            
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            n_noise = list(labels).count(-1)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Clusters", n_clusters)
            c2.metric("Noise", n_noise)
            c3.metric("Noise %", f"{n_noise/len(labels)*100:.1f}%")
            
            if len(cols) >= 2:
                fig = px.scatter(X, x=cols[0], y=cols[1], color="Cluster",
                                title=f"DBSCAN (eps={eps})",
                                color_discrete_sequence=px.colors.qualitative.Set2 + ["#000"])
                apply_theme(fig)
                st.plotly_chart(fig, width='stretch')

    elif "Hierarchical" in method:
        n_clusters = st.slider("K:", 2, min(15, len(X)-1), 5, key="cl_hc")
        linkage = st.selectbox("Linkage:", ["ward", "complete", "average", "single"], key="cl_link")
        if st.button("🧬 Run", key="cl_hc_run"):
            hc = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage)
            labels = hc.fit_predict(X_scaled)
            X["Cluster"] = labels.astype(str)
            
            sil = silhouette_score(X_scaled, labels)
            st.metric("Silhouette", f"{sil:.4f}")
            
            if len(cols) >= 2:
                fig = px.scatter(X, x=cols[0], y=cols[1], color="Cluster",
                                title=f"Hierarchical (K={n_clusters})",
                                color_discrete_sequence=px.colors.qualitative.Set2)
                apply_theme(fig)
                st.plotly_chart(fig, width='stretch')
            
            linkage_matrix = scipy_linkage(X_scaled, method=linkage)
            fig, ax = plt.subplots(figsize=(10, 5))
            dendrogram(linkage_matrix, ax=ax, color_threshold=0.7 * max(linkage_matrix[:, 2]),
                      above_threshold_color='gray')
            ax.set_title("Dendrogram")
            st.pyplot(fig)
            plt.close()


# ═══════════════════════════════════════════════════════════════════════════════
# 8. PCA & DIMENSIONALITY REDUCTION (Book Ch.6)
# ═══════════════════════════════════════════════════════════════════════════════
def render_pca_tab(df, num):
    if not SKLEARN_AVAIL:
        st.warning("⚠️ Cài đặt: pip install scikit-learn")
        return
    if not validate_df(df, num, None, min_rows=10, min_numeric=2):
        return

    st.markdown("### 🎯 Dimension Reduction (Book Ch.6)")
    st.caption("PCA & t-SNE")

    if len(num) < 2:
        st.warning("Cần ít nhất 2 cột numeric")
        return

    cols = st.multiselect("Columns:", num, default=num[:min(6, len(num))], key="pca_cols")
    if len(cols) < 2:
        st.warning("Chọn ít nhất 2 cột")
        return

    X = df[cols].dropna().copy()
    if len(X) < 10:
        st.error("Cần ít nhất 10 mẫu")
        return

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    method = st.selectbox("Method:", ["PCA", "t-SNE", "Both"], key="pca_method")
    if st.button("🎯 Run", key="pca_run"):
        with st.spinner("..."):
            if method in ["PCA", "Both"]:
                pca = PCA()
                _X_pca = pca.fit_transform(X_scaled)
                cum_var = np.cumsum(pca.explained_variance_ratio_)
                
                fig = make_subplots(rows=1, cols=2,
                                   subplot_titles=("Explained Variance", "Cumulative"),
                                   specs=[[{"type": "bar"}, {"type": "scatter"}]])
                fig.add_trace(go.Bar(x=[f"PC{i+1}" for i in range(len(pca.explained_variance_ratio_))],
                                    y=pca.explained_variance_ratio_,
                                    marker_color="#818cf8",
                                    text=[f"{v:.1%}" for v in pca.explained_variance_ratio_],
                                    textposition='outside'), row=1, col=1)
                fig.add_trace(go.Scatter(x=[f"PC{i+1}" for i in range(len(cum_var))], y=cum_var,
                                        mode='lines+markers', marker=dict(color="#34d399", size=8),
                                        line=dict(color="#34d399")), row=1, col=2)
                fig.add_hline(y=0.8, line_dash="dash", line_color="#f87171", row=1, col=2)
                fig.update_layout(height=350)
                apply_theme(fig)
                st.plotly_chart(fig, width='stretch')
                
                # 2D plot
                pca_2d = PCA(n_components=2)
                X_pca_2d = pca_2d.fit_transform(X_scaled)
                pca_df = pd.DataFrame({"PC1": X_pca_2d[:, 0], "PC2": X_pca_2d[:, 1]})
                
                var_text = f"{pca_2d.explained_variance_ratio_[0]:.1%} + {pca_2d.explained_variance_ratio_[1]:.1%}"
                fig = px.scatter(pca_df, x="PC1", y="PC2",
                                title=f"PCA 2D ({var_text})",
                                opacity=0.6, color_discrete_sequence=["#818cf8"])
                apply_theme(fig)
                st.plotly_chart(fig, width='stretch')
                
                # Loadings
                loadings = pd.DataFrame(pca.components_[:min(4, len(cols))].T,
                                       columns=[f"PC{i+1}" for i in range(min(4, len(cols)))],
                                       index=cols)
                st.markdown("#### 📋 Loadings")
                st.dataframe(loadings, width="stretch")

            if method in ["t-SNE", "Both"]:
                perplexity = st.slider("Perplexity:", 5, min(50, len(X)-1), min(30, len(X)//2), key="tsne_perp")
                tsne = TSNE(n_components=2, perplexity=perplexity, random_state=42)
                X_tsne = tsne.fit_transform(X_scaled)
                tsne_df = pd.DataFrame({"t-SNE 1": X_tsne[:, 0], "t-SNE 2": X_tsne[:, 1]})
                
                fig = px.scatter(tsne_df, x="t-SNE 1", y="t-SNE 2",
                                title=f"t-SNE (perplexity={perplexity})",
                                opacity=0.6, color_discrete_sequence=["#34d399"])
                apply_theme(fig)
                st.plotly_chart(fig, width='stretch')


# ═══════════════════════════════════════════════════════════════════════════════
# 9. FEATURE ENGINEERING (Book Ch.6)
# ═══════════════════════════════════════════════════════════════════════════════
def render_feature_engineering_tab(df, num, cat):
    st.markdown("### 🔧 Feature Engineering (Book Ch.6)")
    st.caption("Tạo đặc trưng, Scaling, Selection")

    tabs = st.tabs(["➕ Create Features", "📐 Scale & Encode", "🎯 Feature Selection"])

    with tabs[0]:
        feat_type = st.selectbox("Feature type:", [
            "Interaction", "Polynomial", "Binning", "Ratio", "Rolling Stats"
        ], key="fe_type")

        if feat_type == "Interaction" and len(num) >= 2:
            c1 = st.selectbox("Col 1:", num, key="fe_i1")
            c2 = st.selectbox("Col 2:", [c for c in num if c != c1], key="fe_i2")
            op = st.selectbox("Op:", ["*", "/", "+", "-"], key="fe_op")
            new_name = st.text_input("Name:", f"{c1}_{op}_{c2}", key="fe_iname")
            if st.button("➕ Create", key="fe_i_create"):
                ops = {"*": lambda a, b: a * b, "/": lambda a, b: a / b.replace(0, np.nan),
                       "+": lambda a, b: a + b, "-": lambda a, b: a - b}
                df[new_name] = ops[op](df[c1], df[c2])
                st.success(f"✅ Created '{new_name}'")
                st.dataframe(df[[c1, c2, new_name]].head(10), width="stretch")

        elif feat_type == "Polynomial" and num:
            c = st.selectbox("Col:", num, key="fe_pc")
            degree = st.slider("Degree:", 2, 5, 2, key="fe_pd")
            if st.button("➕ Create", key="fe_p_create"):
                df[f"{c}^{degree}"] = df[c] ** degree
                st.success(f"✅ Created '{c}^{degree}'")

        elif feat_type == "Binning" and num:
            c = st.selectbox("Col:", num, key="fe_bc")
            n_bins = st.slider("Bins:", 2, 10, 4, key="fe_bn")
            if st.button("➕ Create", key="fe_b_create"):
                df[f"{c}_bin"] = pd.qcut(df[c].rank(method='first'), q=n_bins,
                                        labels=[f"Q{i+1}" for i in range(n_bins)])
                st.success(f"✅ Created '{c}_bin'")

        elif feat_type == "Ratio" and len(num) >= 2:
            num_c = st.selectbox("Numerator:", num, key="fe_rn")
            den_c = st.selectbox("Denominator:", [c for c in num if c != num_c], key="fe_rd")
            if st.button("➕ Create", key="fe_r_create"):
                df[f"{num_c}_ratio_{den_c}"] = df[num_c] / df[den_c].replace(0, np.nan)
                st.success(f"✅ Created ratio")

        elif feat_type == "Rolling Stats" and num:
            c = st.selectbox("Col:", num, key="fe_rc")
            window = st.slider("Window:", 2, 50, 5, key="fe_rw")
            stat = st.selectbox("Stat:", ["Mean", "Std", "Min", "Max"], key="fe_rs")
            if st.button("➕ Create", key="fe_r_create2"):
                df[f"{c}_rolling_{stat.lower()}_{window}"] = df[c].rolling(window=window).agg(stat.lower())
                st.success(f"✅ Created rolling {stat}")

    with tabs[1]:
        st.markdown("#### 📐 Scaling & Encoding")
        if num:
            scale_cols = st.multiselect("Scale:", num, default=num[:min(3, len(num))], key="fe_sc")
            scaler_type = st.selectbox("Method:", ["StandardScaler", "MinMaxScaler"], key="fe_st")
            if st.button("📐 Scale", key="fe_scale_run") and scale_cols:
                s = StandardScaler() if "Standard" in scaler_type else MinMaxScaler()
                scaled = s.fit_transform(df[scale_cols])
                for i, c in enumerate(scale_cols):
                    suffix = '_zscore' if 'Standard' in scaler_type else '_minmax'
                    df[f"{c}{suffix}"] = scaled[:, i]
                st.success(f"✅ Scaled {len(scale_cols)} columns")

    with tabs[2]:
        st.markdown("#### 🎯 Feature Selection")
        if len(num) >= 3:
            target = st.selectbox("Target:", num, key="fe_fs_target")
            features = [c for c in num if c != target]
            k = st.slider("K features:", 1, len(features), min(3, len(features)), key="fe_fs_k")
            method = st.selectbox("Method:", ["f_regression", "Mutual Information"], key="fe_fs_method")
            if st.button("🎯 Select", key="fe_fs_run"):
                X = df[features].dropna()
                y = df.loc[X.index, target]
                score_func = f_regression if method == "f_regression" else mutual_info_regression
                selector = SelectKBest(score_func=score_func, k=k)
                _X_selected = selector.fit_transform(X, y)
                
                result = pd.DataFrame({"Feature": features, "Score": selector.scores_})
                result = result.sort_values("Score", ascending=True)
                
                fig = px.bar(result, x="Score", y="Feature", orientation='h',
                            title=f"Feature Scores ({method})",
                            color="Score", color_continuous_scale="Viridis")
                apply_theme(fig)
                st.plotly_chart(fig, width='stretch')
                
                selected = result.nlargest(k, "Score")
                st.success(f"✅ Top {k}: {', '.join(selected['Feature'].tolist())}")
        else:
            st.warning("Cần ít nhất 3 cột numeric")


# ═══════════════════════════════════════════════════════════════════════════════
# 10. MODEL COMPARISON (Book Ch.6)
# ═══════════════════════════════════════════════════════════════════════════════
def render_model_comparison_tab(df, num):
    if not SKLEARN_AVAIL:
        st.warning("⚠️ Cài đặt: pip install scikit-learn")
        return
    if not validate_df(df, num, None, min_rows=10, min_numeric=3):
        return

    st.markdown("### 🏆 Model Comparison (Book Ch.6)")
    st.caption("So sánh 11+ thuật toán với Cross-Validation")

    if len(num) < 3:
        st.warning("Cần ít nhất 3 cột numeric")
        return

    target = st.selectbox("Target:", num, key="mc_target")
    features = st.multiselect("Features:", [c for c in num if c != target],
                             default=[c for c in num if c != target][:min(4, len(num)-1)], key="mc_feats")
    if len(features) < 1:
        st.warning("Chọn ít nhất 1 feature")
        return

    cv_folds = st.slider("CV Folds:", 2, 10, 5, key="mc_cv")
    test_size = st.slider("Test size:", 0.1, 0.4, 0.2, 0.05, key="mc_ts")

    models_to_compare = st.multiselect(
        "Algorithms:",
        ["Linear Regression", "Ridge", "Lasso", "ElasticNet",
         "Decision Tree", "Random Forest", "Gradient Boosting", "AdaBoost",
         "Extra Trees", "KNN", "SVR"],
        default=["Linear Regression", "Random Forest", "Gradient Boosting", "Ridge"],
        key="mc_models"
    )

    if st.button("🏆 Compare", key="mc_run") and models_to_compare:
        with st.spinner("Đang huấn luyện..."):
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
                "Ridge": Ridge(alpha=1.0),
                "Lasso": Lasso(alpha=0.01),
                "ElasticNet": ElasticNet(alpha=0.01, l1_ratio=0.5),
                "Decision Tree": DecisionTreeRegressor(max_depth=10),
                "Random Forest": RandomForestRegressor(n_estimators=100, n_jobs=-1),
                "Gradient Boosting": GradientBoostingRegressor(n_estimators=100),
                "AdaBoost": AdaBoostRegressor(n_estimators=50),
                "Extra Trees": ExtraTreesRegressor(n_estimators=100, n_jobs=-1),
                "KNN": KNeighborsRegressor(n_neighbors=5),
                "SVR": SVR(kernel='rbf')
            }

            results = []
            for name in models_to_compare:
                model = model_map[name]
                try:
                    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=cv_folds, scoring='r2', n_jobs=-1)
                    cv_mean = cv_scores.mean()
                    cv_std = cv_scores.std()
                except:
                    cv_mean = cv_std = 0
                
                model.fit(X_train_scaled, y_train)
                train_score = model.score(X_train_scaled, y_train)
                test_score = model.score(X_test_scaled, y_test)
                
                results.append({
                    "Model": name,
                    "Train R²": round(train_score, 4),
                    "Test R²": round(test_score, 4),
                    "CV R²": round(cv_mean, 4),
                    "CV Std": round(cv_std, 4)
                })

            results_df = pd.DataFrame(results).sort_values("Test R²", ascending=False)
            st.dataframe(results_df, width="stretch")

            # Bar chart
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Train R²", x=results_df["Model"], y=results_df["Train R²"],
                                marker_color="#818cf8"))
            fig.add_trace(go.Bar(name="Test R²", x=results_df["Model"], y=results_df["Test R²"],
                                marker_color="#34d399"))
            fig.add_trace(go.Bar(name="CV R²", x=results_df["Model"], y=results_df["CV R²"],
                                marker_color="#fbbf24"))
            fig.update_layout(title="R² Comparison", barmode='group', height=400)
            apply_theme(fig)
            st.plotly_chart(fig, width='stretch')

            best = results_df.iloc[0]
            insight_card("🏆", f"Best: {best['Model']}",
                        f"Test R² = {best['Test R²']:.4f} | CV R² = {best['CV R²']:.4f}",
                        "good")


# ═══════════════════════════════════════════════════════════════════════════════
# 11. DATA QUALITY ADVANCED (Book Ch.1)
# ═══════════════════════════════════════════════════════════════════════════════
def render_data_quality_tab(df, num, cat):
    st.markdown("### ✅ Data Quality (Book Ch.1)")
    st.caption("Chất lượng dữ liệu, trùng lặp, schema validation, drift")

    tabs = st.tabs(["📋 Overview", "🔍 Duplicates", "📐 Schema", "📊 Drift"])

    with tabs[0]:
        total_cells = df.shape[0] * df.shape[1]
        filled_cells = total_cells - df.isnull().sum().sum()
        completeness = filled_cells / total_cells * 100 if total_cells > 0 else 0
        dup_rows = df.duplicated().sum()
        uniqueness = (1 - dup_rows / len(df)) * 100 if len(df) > 0 else 0
        
        outlier_count = 0
        for c in num:
            q1, q3 = df[c].quantile(0.25), df[c].quantile(0.75)
            iqr = q3 - q1
            outliers = ((df[c] < q1 - 1.5 * iqr) | (df[c] > q3 + 1.5 * iqr)).sum()
            outlier_count += outliers
        
        validity = max(0, 100 - (outlier_count / total_cells * 100) if total_cells > 0 else 0)
        quality_score = completeness * 0.3 + uniqueness * 0.25 + validity * 0.25 + 100 * 0.2

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Completeness", f"{completeness:.1f}%")
        c2.metric("Uniqueness", f"{uniqueness:.1f}%")
        c3.metric("Validity", f"{validity:.1f}%")
        c4.metric("Quality Score", f"{quality_score:.1f}%")

        issues = []
        if df.isnull().sum().sum() > 0:
            issues.append(f"⚠️ {df.isnull().sum().sum():,} missing values")
        if dup_rows > 0:
            issues.append(f"⚠️ {dup_rows:,} duplicate rows")
        if outlier_count > 0:
            issues.append(f"⚠️ {outlier_count:,} outliers")
        if not issues:
            issues.append("✅ Data is clean!")
        for issue in issues:
            insight_card("📊", "", issue, "good" if "✅" in issue else "warning")

    with tabs[1]:
        exact_dups = df.duplicated(keep=False)
        n_exact = exact_dups.sum()
        st.metric("Exact Duplicates", f"{n_exact:,} ({n_exact/len(df)*100:.1f}%)")
        if n_exact > 0:
            st.dataframe(df[exact_dups].head(20), width='stretch')

    with tabs[2]:
        schema = pd.DataFrame({
            "Column": df.columns,
            "Type": df.dtypes.astype(str),
            "Non-Null": df.count().values,
            "Null%": (df.isnull().sum().values / len(df) * 100).round(1).astype(str) + "%",
            "Unique": df.nunique().values
        })
        st.dataframe(schema, width="stretch")

    with tabs[3]:
        if len(num) >= 1:
            split_point = st.slider("Split point (%):", 10, 90, 50, 5, key="dq_split")
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
                                "Column": c, "KS Stat": round(stat, 4),
                                "p-value": round(p, 6),
                                "Drift": "⚠️ Yes" if p < 0.05 else "✅ No"
                            })
                        except: pass
                
                if drift_results:
                    st.dataframe(pd.DataFrame(drift_results), width='stretch')
                    n_drift = sum(1 for r in drift_results if r["Drift"] == "⚠️ Yes")
                    if n_drift > 0:
                        insight_card("⚠️", f"{n_drift} drifted columns",
                                    f"{n_drift}/{len(drift_results)} columns have different distributions",
                                    "warning" if n_drift <= len(drift_results)/2 else "danger")
                    else:
                        insight_card("✅", "No drift detected", "Data is stable", "good")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN RENDER FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════
def render_deep_analysis_tab(df, num, cat, dat):
    """Main entry point for Deep Analysis tab"""
    
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
        "📊 Advanced Stats",
        "🎲 Bootstrap",
        "⚗️ A/B Testing",
        "🔴 Logistic",
        "🧮 Naive Bayes",
        "🔧 Diagnostics",
        "🧬 Clustering",
        "🎯 PCA & t-SNE",
        "🔧 Feature Engineering",
        "🏆 Model Comparison",
        "✅ Data Quality"
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