"""Logistic Regression & Classification (Book Ch.5)"""
import logging
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from .base import apply_theme, insight_card, validate_df

logger = logging.getLogger(__name__)

try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import confusion_matrix, roc_curve, auc
    SKLEARN_AVAIL = True
except ImportError:
    SKLEARN_AVAIL = False
    logger.warning("scikit-learn not available - logistic disabled")
except Exception as e:
    SKLEARN_AVAIL = False
    logger.error("Failed to load sklearn: %s", e, exc_info=True)


def render_logistic_tab(df, num, cat):
    if not SKLEARN_AVAIL:
        st.warning("⚠️ Cài đặt: pip install scikit-learn")
        return
    if not validate_df(df, num, cat, min_rows=10, min_numeric=1):
        return

    st.markdown("### 🔴 Logistic Regression & Classification")
    st.caption("Phân loại nhị phân, Confusion Matrix, ROC Curve (Book Ch.5)")

    target_options = num + cat
    target_col = st.selectbox("Chọn biến mục tiêu (binary):", target_options, key="da_log_target")

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

    features = st.multiselect("Chọn features:", num, default=num[:min(4, len(num))], key="log_feats")

    if len(features) >= 1 and st.button("🔴 Train Logistic Regression", key="log_run"):
        with st.spinner("Đang huấn luyện..."):
            X = df[features].dropna()
            y_aligned = y.loc[X.index]
            if len(X) < 10 or len(np.unique(y_aligned)) < 2:
                st.error("Cần ít nhất 10 mẫu và cả 2 classes")
                return

            X_train, X_test, y_train, y_test = train_test_split(
                X, y_aligned, test_size=0.3, random_state=42, stratify=y_aligned)
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            model = LogisticRegression(random_state=42, max_iter=500)
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            y_prob = model.predict_proba(X_test_scaled)[:, 1]

            cm = confusion_matrix(y_test, y_pred)
            tn, fp, fn, tp = cm.ravel()
            accuracy = (tp + tn) / (tp + tn + fp + fn)
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            fpr, tpr, _ = roc_curve(y_test, y_prob)
            auc_score = auc(fpr, tpr)

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Accuracy", f"{accuracy:.2%}")
            c2.metric("Precision", f"{precision:.2%}")
            c3.metric("Recall", f"{recall:.2%}")
            c4.metric("F1-Score", f"{f1:.2%}")
            c5.metric("AUC", f"{auc_score:.3f}")

            st.markdown("#### 📊 Confusion Matrix")
            fig_cm = px.imshow(cm, text_auto=True,
                              x=["Predicted Negative", "Predicted Positive"],
                              y=["Actual Negative", "Actual Positive"],
                              color_continuous_scale="Blues", aspect='auto')
            fig_cm.update_layout(height=350)
            apply_theme(fig_cm)
            st.plotly_chart(fig_cm, width='stretch')

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
                                 xaxis_title="False Positive Rate",
                                 yaxis_title="True Positive Rate", height=400)
            apply_theme(fig_roc)
            st.plotly_chart(fig_roc, width='stretch')

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

            # SHAP
            st.markdown("#### 🔮 SHAP Explainability")
            st.caption("SHAP values show how each feature contributes to predictions")
            try:
                import shap
                SHAP_AVAIL = True
            except ImportError:
                SHAP_AVAIL = False
                logger.debug("SHAP not installed")
            except Exception as e:
                SHAP_AVAIL = False
                logger.warning("SHAP import failed: %s", e)

            if SHAP_AVAIL:
                if st.checkbox("🔮 Show SHAP Explanation", value=False, key="log_shap"):
                    with st.spinner("⏳ Computing SHAP values..."):
                        try:
                            import matplotlib.pyplot as plt
                            sample_size = min(100, len(X_test_scaled))
                            X_sample = X_test_scaled[:sample_size]
                            explainer = shap.Explainer(model, X_train_scaled)
                            shap_values = explainer(X_sample)
                            fig, ax = plt.subplots(figsize=(8, 4))
                            shap.summary_plot(shap_values, X_sample, feature_names=features,
                                            plot_type="bar", show=False)
                            plt.tight_layout()
                            st.pyplot(fig)
                            plt.close()
                            fig, ax = plt.subplots(figsize=(8, 5))
                            shap.summary_plot(shap_values, X_sample, feature_names=features, show=False)
                            plt.tight_layout()
                            st.pyplot(fig)
                            plt.close()
                            insight_card("🔮", "SHAP Insights",
                                        f"Top features: {', '.join(features[:3])}.",
                                        "good")
                        except (ValueError, RuntimeError, ImportError) as e:
                            logger.warning("SHAP computation failed: %s", e)
                            st.warning(f"⚠️ **SHAP Error:** {str(e)}")
                        except Exception as e:
                            logger.error("Unexpected SHAP error: %s", e, exc_info=True)
                            st.error(f"🚨 **SHAP Error:** {str(e)}")
                            st.caption("💡 Thử lại hoặc bỏ chọn SHAP")
            else:
                st.info("Install SHAP: pip install shap")