"""Naive Bayes Classification (Book Ch.5)"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from .base import apply_theme, insight_card, validate_df

try:
    from sklearn.naive_bayes import GaussianNB
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import confusion_matrix, roc_curve, auc
    SKLEARN_AVAIL = True
except Exception:
    SKLEARN_AVAIL = False


def render_naive_bayes_tab(df, num, cat):
    if not SKLEARN_AVAIL:
        st.warning("⚠️ Cài đặt: pip install scikit-learn")
        return
    if not validate_df(df, num, cat, min_rows=10, min_numeric=1):
        return

    st.markdown("### 🧮 Naive Bayes Classification")
    st.caption("Phân loại xác suất với Gaussian & Categorical Naive Bayes (Book Ch.5)")

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
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_aligned, test_size=0.3, random_state=42)
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            gnb = GaussianNB()
            gnb.fit(X_train_scaled, y_train)
            y_pred = gnb.predict(X_test_scaled)
            y_prob = gnb.predict_proba(X_test_scaled)[:, 1]

            cm = confusion_matrix(y_test, y_pred)
            tn, fp, fn, tp = cm.ravel() if len(cm.ravel()) == 4 else (0, 0, 0, 0)
            accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

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

            fig = px.imshow(cm, text_auto=True,
                          x=["Pred Neg", "Pred Pos"],
                          y=["Actual Neg", "Actual Pos"],
                          color_continuous_scale="Purples", aspect='auto')
            fig.update_layout(height=350, title="Confusion Matrix — Naive Bayes")
            apply_theme(fig)
            st.plotly_chart(fig, width='stretch')

            st.markdown("#### 📋 Class Priors")
            priors = pd.DataFrame({
                "Class": ["Negative (0)", "Positive (1)"],
                "Prior Probability": gnb.class_prior_,
                "Theta (mean)": [gnb.theta_[0, 0] if gnb.theta_.shape[1] > 0 else 0,
                                gnb.theta_[1, 0] if gnb.theta_.shape[1] > 0 else 0]
            })
            st.dataframe(priors, width="stretch")