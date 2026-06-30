"""Regression Diagnostics — VIF, Heteroskedasticity, Durbin-Watson (Book Ch.4)"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .base import apply_theme, insight_card, validate_df

try:
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    from statsmodels.stats.diagnostic import het_breuschpagan
    from statsmodels.stats.stattools import durbin_watson
    from statsmodels.tools.tools import add_constant
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from scipy.stats import probplot
    STATS_AVAIL = True
except Exception:
    STATS_AVAIL = False


def render_diagnostics_tab(df, num):
    if not STATS_AVAIL:
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

            X_const = add_constant(X)
            model = LinearRegression()
            model.fit(X, y)
            y_pred = model.predict(X)
            residuals = y - y_pred

            tabs = st.tabs(["📊 VIF", "📈 Heteroskedasticity", "📉 Durbin-Watson", "📋 Residuals"])

            with tabs[0]:
                st.markdown("#### 📊 Variance Inflation Factor (VIF)")
                st.caption("Đo lường đa cộng tuyến (Multicollinearity)")
                vif_data = pd.DataFrame()
                vif_data["Feature"] = features
                vif_data["VIF"] = [variance_inflation_factor(X_const.values, i+1) for i in range(len(features))]
                vif_data["Tolerance"] = 1 / vif_data["VIF"]
                vif_data["Severe? (VIF>10)"] = vif_data["VIF"].apply(lambda x: "⚠️ Yes" if x > 10 else "✅ No")
                vif_data["Moderate? (VIF>5)"] = vif_data["VIF"].apply(lambda x: "⚠️ Yes" if x > 5 else "✅ No")
                st.dataframe(vif_data.style.highlight_max(axis=0, color='#f8717140'), width="stretch")
                max_vif = vif_data["VIF"].max()
                if max_vif > 10:
                    insight_card("⚠️", "Severe Multicollinearity",
                                f"Có VIF={max_vif:.1f} > 10 — nên loại bỏ hoặc kết hợp features", "danger")
                elif max_vif > 5:
                    insight_card("⚠️", "Moderate Multicollinearity",
                                f"Có VIF={max_vif:.1f} > 5 — cần xem xét", "warning")
                else:
                    insight_card("✅", "No Multicollinearity", "Tất cả VIF < 5 — không có đa cộng tuyến đáng kể", "good")

            with tabs[1]:
                st.markdown("#### 📈 Heteroskedasticity Test (Breusch-Pagan)")
                try:
                    lm_stat, lm_p, f_stat, f_p = het_breuschpagan(residuals, X_const)
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("LM Statistic", f"{lm_stat:.4f}")
                    c2.metric("LM p-value", f"{lm_p:.6f}")
                    c3.metric("F Statistic", f"{f_stat:.4f}")
                    c4.metric("F p-value", f"{f_p:.6f}")
                    if lm_p < 0.05:
                        insight_card("⚠️", "Heteroskedasticity Detected",
                                    f"p = {lm_p:.6f} < 0.05 — Phương sai sai số thay đổi", "warning")
                    else:
                        insight_card("✅", "Homoskedasticity",
                                    f"p = {lm_p:.4f} ≥ 0.05 — Phương sai sai số đồng đều", "good")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=y_pred, y=residuals, mode='markers',
                                            marker=dict(color="#818cf8", size=6, opacity=0.6), name="Residuals"))
                    fig.add_hline(y=0, line_dash="dash", line_color="#f87171")
                    fig.update_layout(title="Residuals vs Fitted Values",
                                     xaxis_title="Fitted Values", yaxis_title="Residuals", height=350)
                    apply_theme(fig)
                    st.plotly_chart(fig, width='stretch')
                except Exception as e:
                    st.warning(f"Breusch-Pagan test không khả dụng: {e}")

            with tabs[2]:
                st.markdown("#### 📉 Durbin-Watson Test (Autocorrelation)")
                dw = durbin_watson(residuals)
                st.metric("Durbin-Watson Statistic", f"{dw:.4f}")
                dw_msg = (f"⚠️ Có tự tương quan dương (DW gần 0)" if dw < 1.5 else
                         f"✅ Không có tự tương quan (DW gần 2)" if 1.5 <= dw <= 2.5 else
                         f"⚠️ Có tự tương quan âm (DW gần 4)")
                insight_card("📊", "Interpretation", f"DW = {dw:.4f}. {dw_msg}",
                            "good" if 1.5 <= dw <= 2.5 else "warning")
                fig = go.Figure()
                fig.add_trace(go.Histogram(x=residuals, nbinsx=30, marker_color="#818cf8",
                                          opacity=0.7, name="Residuals"))
                fig.update_layout(title="Distribution of Residuals", height=300,
                                 xaxis_title="Residual", yaxis_title="Frequency")
                apply_theme(fig)
                st.plotly_chart(fig, width='stretch')

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
                coef_df = pd.DataFrame({
                    "Feature": ["Intercept"] + features,
                    "Coefficient": [model.intercept_] + list(model.coef_)
                })
                st.dataframe(coef_df, width="stretch")
                fig = make_subplots(rows=1, cols=2,
                                   subplot_titles=("Q-Q Plot (Normality)", "Residuals vs Fitted"))
                (osm, osr), (slope, intercept, _r) = probplot(residuals, dist="norm")
                fig.add_trace(go.Scatter(x=osm, y=osr, mode='markers',
                                        marker=dict(color="#818cf8", size=4), showlegend=False), row=1, col=1)
                fig.add_trace(go.Scatter(x=osm, y=slope * osm + intercept, mode='lines',
                                        line=dict(color="#f87171", dash="dash"), showlegend=False), row=1, col=1)
                fig.add_trace(go.Scatter(x=y_pred, y=residuals, mode='markers',
                                        marker=dict(color="#34d399", size=4, opacity=0.6), showlegend=False), row=1, col=2)
                fig.add_hline(y=0, line_dash="dash", line_color="#f87171", row=1, col=2)
                fig.update_layout(height=400, title="Regression Diagnostics")
                apply_theme(fig)
                st.plotly_chart(fig, width='stretch')