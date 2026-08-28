"""Feature Engineering — Creation, Scaling, Selection (Book Ch.6)"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from .base import apply_theme

try:
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression
    SKLEARN_AVAIL = True
except Exception:
    SKLEARN_AVAIL = False


def render_feature_engineering_tab(df, num, cat):
    st.markdown("### 🔧 Feature Engineering (Book Ch.6)")
    st.caption("Tạo đặc trưng, Scaling, Selection")

    tabs = st.tabs(["➕ Create Features", "📐 Scale & Encode", "🎯 Feature Selection"])

    with tabs[0]:
        _render_create_features(df, num)

    with tabs[1]:
        _render_scale_encode(df, num)

    with tabs[2]:
        _render_feature_selection(df, num)


def _render_create_features(df, num):
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


def _render_scale_encode(df, num):
    st.markdown("#### 📐 Scaling & Encoding")
    if not num:
        return
    scale_cols = st.multiselect("Scale:", num, default=num[:min(3, len(num))], key="fe_sc")
    scaler_type = st.selectbox("Method:", ["StandardScaler", "MinMaxScaler"], key="fe_st")
    if st.button("📐 Scale", key="fe_scale_run") and scale_cols:
        s = StandardScaler() if "Standard" in scaler_type else MinMaxScaler()
        scaled = s.fit_transform(df[scale_cols])
        for i, c in enumerate(scale_cols):
            suffix = '_zscore' if 'Standard' in scaler_type else '_minmax'
            df[f"{c}{suffix}"] = scaled[:, i]
        st.success(f"✅ Scaled {len(scale_cols)} columns")


def _render_feature_selection(df, num):
    st.markdown("#### 🎯 Feature Selection")
    if len(num) < 3:
        st.warning("Cần ít nhất 3 cột numeric")
        return
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