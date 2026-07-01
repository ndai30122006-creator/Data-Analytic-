"""Analytics tab — Anomaly Detection, Profiling, Data Cleaning, AutoML"""
import logging
from typing import List, Dict, Any
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from config import MIN_ROWS_VALIDATION, PARAM_GRIDS, PROFILER_TABS
from utils import validate_dataframe
from helpers import apply_theme
from exceptions import handle_error, ModelTrainingError, DataValidationError

logger = logging.getLogger(__name__)

try:
    from sklearn.ensemble import IsolationForest
    SKLEARN_ENSEMBLE_AVAIL = True
except ImportError:
    SKLEARN_ENSEMBLE_AVAIL = False
    logger.warning("sklearn.ensemble not available - anomaly detection disabled")
except Exception as e:
    SKLEARN_ENSEMBLE_AVAIL = False
    logger.error("Failed to load sklearn.ensemble: %s", e)


def render_analytics_tab(df, num, cat):
    """Render the Analytics tab with 4 sub-tabs: Anomaly, Profiling, Cleaning, AutoML"""
    is_valid, msg = validate_dataframe(df, min_rows=MIN_ROWS_VALIDATION)
    if not is_valid:
        st.error(f"❌ {msg}")
        return

    from config import ANALYTICS_TABS
    an_tabs = st.tabs(ANALYTICS_TABS)

    with an_tabs[0]: _render_anomaly(df, num)
    with an_tabs[1]: _render_profiling(df, num, cat)
    with an_tabs[2]: _render_cleaning(df, num)
    with an_tabs[3]: _render_automl(df, num)


def _render_anomaly(df, num):
    if not num:
        st.warning("Need numeric columns")
        return
    ac = st.multiselect("Columns:", num, default=num[:min(3, len(num))], key="an")
    ct = st.slider("Contamination:", 0.01, 0.5, 0.05, 0.01)
    if st.button("🔍 Detect", key="anr") and ac and SKLEARN_ENSEMBLE_AVAIL:
        with st.spinner("..."):
            X = df[ac].dropna().copy()
            iso = IsolationForest(contamination=ct, random_state=42)
            p = iso.fit_predict(X)
        normal_count, anomaly_count = (p == 1).sum(), (p == -1).sum()
        col_metrics1, col_metrics2, col_metrics3 = st.columns(3)
        col_metrics1.metric("✅ Normal", normal_count)
        col_metrics2.metric("🚨 Anomalies", anomaly_count)
        if (normal_count + anomaly_count) > 0:
            col_metrics3.metric("Ratio", f"{anomaly_count/(normal_count+anomaly_count)*100:.1f}%")
        else:
            col_metrics3.metric("Ratio", "N/A")
        if len(ac) >= 2:
            X["A"] = p
            fig = px.scatter(X, x=ac[0], y=ac[1], color=X["A"].map({1: "Normal", -1: "Anomaly"}),
                           title="Anomalies", color_discrete_map={"Normal": "#818cf8", "Anomaly": "#ef4444"})
            apply_theme(fig)
            st.plotly_chart(fig, width='stretch')


def _render_profiling(df, num, cat):
    ni = df.select_dtypes(include=[np.number])
    ci = df.select_dtypes(include=["object", "category"])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", df.shape[0])
    c2.metric("Columns", df.shape[1])
    c3.metric("Numeric", len(ni.columns))
    c4.metric("Categorical", len(ci.columns))

    pt = st.tabs(PROFILER_TABS)
    with pt[0]:
        for c_ in df.columns:
            with st.expander(f"**{c_}** ({df[c_].dtype})"):
                a, b, c = st.columns(3)
                a.metric("Count", len(df[c_]))
                b.metric("Missing", df[c_].isnull().sum())
                c.metric("Unique", df[c_].nunique())
                if c_ in num:
                    d, e, f = st.columns(3)
                    d.metric("Min", f"{df[c_].min():,.4f}")
                    e.metric("Mean", f"{df[c_].mean():,.4f}")
                    f.metric("Max", f"{df[c_].max():,.4f}")
                    fig = px.histogram(df, x=c_, nbins=30, title="Distribution")
                    apply_theme(fig)
                    st.plotly_chart(fig, width='stretch')
                else:
                    vc = df[c_].value_counts().head(15)
                    fig = px.bar(x=vc.index.astype(str), y=vc.values, title="Top 15",
                               color=vc.values, color_continuous_scale="Viridis")
                    apply_theme(fig)
                    st.plotly_chart(fig, width='stretch')

    with pt[1]:
        if num:
            sc = st.selectbox("Column:", num, key="pd_")
            fig = px.histogram(df, x=sc, nbins=50, marginal="box", title=f"Distribution of {sc}")
            apply_theme(fig)
            st.plotly_chart(fig, width='stretch')
            fig2 = px.box(df, y=sc, title=f"Box Plot — {sc}")
            apply_theme(fig2)
            st.plotly_chart(fig2, width='stretch')

    with pt[2]:
        if len(num) >= 2:
            corr = df[num].corr()
            fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r",
                           zmin=-1, zmax=1, title="Correlation Matrix", aspect='auto')
            fig.update_layout(height=600)
            apply_theme(fig)
            st.plotly_chart(fig, width='stretch')


def _render_cleaning(df, num):
    st.markdown("### 🧹 Data Cleaning & Transformation")

    if "cleaned_df" not in st.session_state or st.session_state.cleaned_df is None:
        st.session_state.cleaned_df = df.copy()
    work_df = st.session_state.cleaned_df

    # Missing Values
    st.markdown("#### 🔲 Missing Values")
    missing_counts = work_df.isnull().sum()
    missing_cols = missing_counts[missing_counts > 0]

    if len(missing_cols) > 0:
        st.write(f"**{len(missing_cols)} columns with missing values:**")
        missing_df = pd.DataFrame({
            "Column": missing_cols.index,
            "Missing": missing_cols.values,
            "Missing %": [f"{v/len(work_df)*100:.1f}%" for v in missing_cols.values]
        })
        st.dataframe(missing_df, width='stretch', hide_index=True)

        col1, col2 = st.columns(2)
        with col1:
            mv_action = st.selectbox("Action:",
                ["Drop rows with any NaN", "Drop rows with all NaN",
                 "Fill with Mean", "Fill with Median", "Fill with Mode", "Fill with 0",
                 "Forward Fill", "Backward Fill"], key="mv_action")
        with col2:
            mv_cols = st.multiselect("Apply to:", missing_cols.index.tolist(),
                                    default=missing_cols.index.tolist(), key="mv_cols")

        if st.button("✨ Apply", key="mv_apply"):
            try:
                if mv_action == "Drop rows with any NaN":
                    work_df = work_df.dropna(subset=mv_cols)
                elif mv_action == "Drop rows with all NaN":
                    work_df = work_df.dropna(how='all', subset=mv_cols)
                elif mv_action == "Fill with Mean":
                    for c in mv_cols:
                        if pd.api.types.is_numeric_dtype(work_df[c].dtype):
                            work_df[c] = work_df[c].fillna(work_df[c].mean())
                elif mv_action == "Fill with Median":
                    for c in mv_cols:
                        if pd.api.types.is_numeric_dtype(work_df[c].dtype):
                            work_df[c] = work_df[c].fillna(work_df[c].median())
                elif mv_action == "Fill with Mode":
                    for c in mv_cols:
                        mode_val = work_df[c].mode()
                        if len(mode_val) > 0:
                            work_df[c] = work_df[c].fillna(mode_val[0])
                elif mv_action == "Fill with 0":
                    for c in mv_cols:
                        work_df[c] = work_df[c].fillna(0)
                elif mv_action == "Forward Fill":
                    for c in mv_cols:
                        work_df[c] = work_df[c].ffill()
                elif mv_action == "Backward Fill":
                    for c in mv_cols:
                        work_df[c] = work_df[c].bfill()
                st.session_state.cleaned_df = work_df
                st.success(f"✅ Applied: {mv_action}")
                st.rerun()
            except Exception as e:
                logger.error("Cleaning operation failed: %s", e, exc_info=True)
                st.error(f"❌ **Lỗi xử lý dữ liệu:** {str(e)}")
                st.caption("💡 Thử lại với lựa chọn khác")
    else:
        st.success("✅ No missing values")

    st.markdown("---")

    # Duplicates
    st.markdown("#### 🔁 Duplicate Rows")
    dup_count = work_df.duplicated().sum()
    if dup_count > 0:
        st.warning(f"⚠️ **{dup_count}** duplicate rows ({dup_count/len(work_df)*100:.1f}%)")
        if st.button("🗑 Remove Duplicates", key="dup_remove"):
            work_df = work_df.drop_duplicates()
            st.session_state.cleaned_df = work_df
            st.success(f"✅ Removed {dup_count} duplicate rows")
            st.rerun()
    else:
        st.success("✅ No duplicate rows")

    st.markdown("---")

    # Outliers
    st.markdown("#### 📊 Outliers")
    num_cols_clean = work_df.select_dtypes(include=[np.number]).columns.tolist()
    if num_cols_clean:
        outlier_col = st.selectbox("Column:", num_cols_clean, key="outlier_col")
        q1, q3 = work_df[outlier_col].quantile(0.25), work_df[outlier_col].quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5*iqr, q3 + 1.5*iqr
        outliers = work_df[(work_df[outlier_col] < lower) | (work_df[outlier_col] > upper)]
        st.write(f"**{len(outliers)} outliers detected**")
        if len(outliers) > 0:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✂️ Remove", key="out_remove"):
                    work_df = work_df.drop(outliers.index)
                    st.session_state.cleaned_df = work_df
                    st.success(f"✅ Removed {len(outliers)} outliers")
                    st.rerun()
            with col2:
                if st.button("🔒 Cap Outliers", key="out_cap"):
                    work_df[outlier_col] = work_df[outlier_col].clip(lower, upper)
                    st.session_state.cleaned_df = work_df
                    st.success("✅ Capped outliers")
                    st.rerun()

    st.markdown("---")

    # Encoding
    st.markdown("#### 🔤 Encoding")
    cat_cols_clean = work_df.select_dtypes(include=["object", "category"]).columns.tolist()
    if cat_cols_clean:
        enc_cols = st.multiselect("Categorical columns:", cat_cols_clean, key="enc_cols")
        enc_method = st.selectbox("Method:", ["One-Hot", "Label", "Frequency"], key="enc_method")
        if st.button("🔄 Apply") and enc_cols:
            try:
                if enc_method == "One-Hot":
                    work_df = pd.get_dummies(work_df, columns=enc_cols)
                elif enc_method == "Label":
                    for c in enc_cols:
                        work_df[c] = work_df[c].astype('category').cat.codes
                elif enc_method == "Frequency":
                    for c in enc_cols:
                        freq = work_df[c].value_counts(normalize=True)
                        work_df[c] = work_df[c].map(freq)
                st.session_state.cleaned_df = work_df
                st.success("✅ Applied encoding")
                st.rerun()
            except Exception as e:
                logger.error("Encoding operation failed: %s", e, exc_info=True)
                st.error(f"❌ **Lỗi encoding:** {str(e)}")
                st.caption("💡 Kiểm tra lại kiểu dữ liệu của cột được chọn")

    st.markdown("---")

    # Summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Original Rows", len(df))
    with col2:
        st.metric("Current Rows", len(work_df))
    with col3:
        st.metric("Current Cols", len(work_df.columns))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reset to Original", width="stretch"):
            st.session_state.cleaned_df = df.copy()
            st.success("✅ Reset")
            st.rerun()
    with col2:
        if st.button("💾 Save Cleaned Data", width="stretch"):
            st.session_state.df = work_df.copy()
            st.success("✅ Saved")
            st.rerun()


def _render_automl(df, num):
    try:
        import xgboost as xgb
        XGB_AVAIL = True
    except ImportError:
        XGB_AVAIL = False
        logger.warning("xgboost not available")
    except Exception as e:
        XGB_AVAIL = False
        logger.error("Failed to load xgboost: %s", e, exc_info=True)
    try:
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
        SKLEARN_AVAIL = True
    except ImportError:
        SKLEARN_AVAIL = False
        logger.warning("sklearn pipeline not available")
    except Exception as e:
        SKLEARN_AVAIL = False
        logger.error("Failed to load sklearn pipeline: %s", e, exc_info=True)

    if not XGB_AVAIL or not SKLEARN_AVAIL:
        st.info("Install: pip install xgboost scikit-learn")
        return

    from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, train_test_split
    from sklearn.linear_model import Ridge, Lasso
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor

    if len(num) < 2:
        st.warning("Need ≥2 numeric columns")
        return

    st.markdown("### 🚀 AutoML — Automated Model Selection")
    st.caption("Hyperparameter Tuning với 5 thuật toán")

    tg = st.selectbox("Target:", num, key="atg")
    feats = [c for c in num if c != tg]
    cols = st.multiselect("Features:", feats, default=feats[:min(4, len(feats))], key="atg_feats")
    if not cols:
        st.warning("Select ≥1 feature")
        return

    col1, col2 = st.columns(2)
    with col1:
        tune_method = st.selectbox("Tuning:", ["GridSearch", "RandomizedSearch", "None"], key="atg_tune")
        test_size = st.slider("Test size:", 0.1, 0.4, 0.2, 0.05, key="atg_ts")
    with col2:
        cv_folds = st.slider("CV folds:", 2, 10, 3, key="atg_cv")
        auto_models = st.multiselect("Models:",
            ["Random Forest", "XGBoost", "Gradient Boosting", "Ridge", "Lasso"],
            default=["Random Forest", "XGBoost"], key="atg_models")

    auto_scale = st.checkbox("📐 Auto Scaling", value=True, key="atg_scale")

    if st.button("🚀 Run AutoML", key="atg_run") and auto_models:
        try:
            with st.spinner("⏳ AutoML running..."):
                X = df[cols].dropna()
                y = df.loc[X.index, tg]
                if len(X) < 10:
                    st.error("Need ≥10 samples")
                    return

                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

                model_constructors = {
                    "Random Forest": RandomForestRegressor(random_state=42),
                    "XGBoost": xgb.XGBRegressor(random_state=42, verbosity=0),
                    "Gradient Boosting": GradientBoostingRegressor(random_state=42),
                    "Ridge": Ridge(),
                    "Lasso": Lasso(max_iter=5000)
                }

                results: List[Dict[str, Any]] = []
                best_overall: Dict[str, Any] = {"name": "", "score": -999}
                progress_bar = st.progress(0)

                for i, model_name in enumerate(auto_models):
                    try:
                        base_model = model_constructors[model_name]
                        param_grid = PARAM_GRIDS.get(model_name, {})

                        steps = []
                        if auto_scale:
                            steps.append(("scaler", StandardScaler()))
                        steps.append(("model", base_model))
                        pipeline = Pipeline(steps)

                        if tune_method == "GridSearch":
                            searcher = GridSearchCV(pipeline, param_grid, cv=cv_folds, scoring='r2', n_jobs=-1)
                        elif tune_method == "RandomizedSearch":
                            searcher = RandomizedSearchCV(pipeline, param_grid, n_iter=10, cv=cv_folds, scoring='r2', n_jobs=-1, random_state=42)
                        else:
                            searcher = None

                        if searcher:
                            searcher.fit(X_train, y_train)
                            best_model = searcher.best_estimator_
                            cv_score = searcher.best_score_
                        else:
                            pipeline.fit(X_train, y_train)
                            best_model = pipeline
                            cv_score = 0

                        train_score = best_model.score(X_train, y_train)
                        test_score = best_model.score(X_test, y_test)

                        results.append({
                            "Model": model_name,
                            "Train R²": round(train_score, 4),
                            "Test R²": round(test_score, 4),
                            "CV R²": round(cv_score, 4)
                        })

                        if test_score > best_overall["score"]:
                            best_overall = {"name": model_name, "score": test_score}
                    except (ValueError, MemoryError) as model_e:
                        logger.error("Model %s failed: %s", model_name, model_e, exc_info=True)
                        error_type_name = type(model_e).__name__
                        results.append({
                            "Model": model_name,
                            "Train R²": f"❌ {error_type_name}",
                            "Test R²": f"❌ {error_type_name}",
                            "CV R²": f"❌ {error_type_name}"
                        })
                        handle_error(model_e, f"_render_automl / {model_name}")
                    except Exception as model_e:
                        logger.error("Model %s failed: %s", model_name, model_e, exc_info=True)
                        results.append({
                            "Model": model_name,
                            "Train R²": "❌ Failed",
                            "Test R²": "❌ Failed",
                            "CV R²": "❌ Failed"
                        })
                        st.warning(f"⚠️ **{model_name}** failed: {str(model_e)}")
                    finally:
                        progress_bar.progress((i + 1) / len(auto_models))

            if not results:
                handle_error(ModelTrainingError("All models failed"), "_render_automl")
                return

            result_df = pd.DataFrame(results)
            if "Train R²" in result_df.columns:
                result_df = result_df.sort_values("Test R²", ascending=False) if result_df["Test R²"].dtype != 'object' else result_df
            st.dataframe(result_df, width='stretch', hide_index=True)
            if best_overall["name"]:
                st.success(f"🏆 **Best: {best_overall['name']}** — Test R² = {best_overall['score']:.4f}")

            fig = go.Figure()
            valid_results = [r for r in results if isinstance(r.get("Train R²"), (int, float))]
            if valid_results:
                df_plot = pd.DataFrame(valid_results)
                fig.add_trace(go.Bar(name="Train", x=df_plot["Model"], y=df_plot["Train R²"], marker_color="#818cf8"))
                fig.add_trace(go.Bar(name="Test", x=df_plot["Model"], y=df_plot["Test R²"], marker_color="#34d399"))
                fig.update_layout(title="AutoML Results", barmode='group', height=350)
                apply_theme(fig)
                st.plotly_chart(fig, width='stretch')
        except MemoryError:
            handle_error(MemoryError(), "_render_automl - Dataset quá lớn")
        except Exception as e:
            handle_error(e, "_render_automl", "AutoML pipeline thất bại")
