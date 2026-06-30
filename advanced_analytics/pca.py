"""PCA & Dimensionality Reduction (Book Ch.6)"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .base import apply_theme, validate_df

try:
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAIL = True
except Exception:
    SKLEARN_AVAIL = False


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
                _render_pca(X_scaled, cols)
            if method in ["t-SNE", "Both"]:
                _render_tsne(X_scaled, cols)


def _render_pca(X_scaled, cols):
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

    pca_2d = PCA(n_components=2)
    X_pca_2d = pca_2d.fit_transform(X_scaled)
    pca_df = pd.DataFrame({"PC1": X_pca_2d[:, 0], "PC2": X_pca_2d[:, 1]})
    var_text = f"{pca_2d.explained_variance_ratio_[0]:.1%} + {pca_2d.explained_variance_ratio_[1]:.1%}"
    fig = px.scatter(pca_df, x="PC1", y="PC2",
                    title=f"PCA 2D ({var_text})",
                    opacity=0.6, color_discrete_sequence=["#818cf8"])
    apply_theme(fig)
    st.plotly_chart(fig, width='stretch')

    loadings = pd.DataFrame(pca.components_[:min(4, len(cols))].T,
                           columns=[f"PC{i+1}" for i in range(min(4, len(cols)))],
                           index=cols)
    st.markdown("#### 📋 Loadings")
    st.dataframe(loadings, width="stretch")


def _render_tsne(X_scaled, cols):
    perplexity = st.slider("Perplexity:", 5, min(50, len(X_scaled)-1),
                          min(30, len(X_scaled)//2), key="tsne_perp")
    tsne = TSNE(n_components=2, perplexity=perplexity, random_state=42)
    X_tsne = tsne.fit_transform(X_scaled)
    tsne_df = pd.DataFrame({"t-SNE 1": X_tsne[:, 0], "t-SNE 2": X_tsne[:, 1]})
    fig = px.scatter(tsne_df, x="t-SNE 1", y="t-SNE 2",
                    title=f"t-SNE (perplexity={perplexity})",
                    opacity=0.6, color_discrete_sequence=["#34d399"])
    apply_theme(fig)
    st.plotly_chart(fig, width='stretch')