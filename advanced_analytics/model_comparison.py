"""Model Comparison & Cross-Validation (Book Ch.6)"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from .base import apply_theme, insight_card, validate_df
from src.utils.performance import safe_n_jobs

try:
    from sklearn.model_selection import cross_val_score, train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.svm import SVR
    from sklearn.neighbors import KNeighborsRegressor
    from sklearn.ensemble import (RandomForestRegressor, GradientBoostingRegressor,
                                 AdaBoostRegressor, ExtraTreesRegressor)
    SKLEARN_AVAIL = True
except Exception:
    SKLEARN_AVAIL = False


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

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42)
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            model_map = {
                "Linear Regression": LinearRegression(),
                "Ridge": Ridge(alpha=1.0),
                "Lasso": Lasso(alpha=0.01),
                "ElasticNet": ElasticNet(alpha=0.01, l1_ratio=0.5),
                "Decision Tree": DecisionTreeRegressor(max_depth=10),
                "Random Forest": RandomForestRegressor(n_estimators=100, n_jobs=safe_n_jobs(-1)),
                "Gradient Boosting": GradientBoostingRegressor(n_estimators=100),
                "AdaBoost": AdaBoostRegressor(n_estimators=50),
                "Extra Trees": ExtraTreesRegressor(n_estimators=100, n_jobs=safe_n_jobs(-1)),
                "KNN": KNeighborsRegressor(n_neighbors=5),
                "SVR": SVR(kernel='rbf')
            }

            results = []
            for name in models_to_compare:
                model = model_map[name]
                try:
                    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=cv_folds, scoring='r2', n_jobs=safe_n_jobs(1))
                    cv_mean = cv_scores.mean()
                    cv_std = cv_scores.std()
                except:
                    cv_mean = cv_std = 0

                model.fit(X_train_scaled, y_train)
                train_score = model.score(X_train_scaled, y_train)
                test_score = model.score(X_test_scaled, y_test)

                results.append({
                    "Model": name, "Train R²": round(train_score, 4),
                    "Test R²": round(test_score, 4),
                    "CV R²": round(cv_mean, 4), "CV Std": round(cv_std, 4)
                })

            results_df = pd.DataFrame(results).sort_values("Test R²", ascending=False)
            st.dataframe(results_df, width="stretch")

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
                        f"Test R² = {best['Test R²']:.4f} | CV R² = {best['CV R²']:.4f}", "good")