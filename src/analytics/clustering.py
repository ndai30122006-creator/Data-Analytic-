"""Clustering — K-Means, DBSCAN, Hierarchical (Book Ch.6)"""
import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from .base import apply_theme, insight_card, validate_df

try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
    from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
    from scipy.cluster.hierarchy import linkage as scipy_linkage, dendrogram
    SKLEARN_AVAIL = True
except Exception:
    SKLEARN_AVAIL = False


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
        _render_kmeans(X, X_scaled, cols, scaler)
    elif method == "DBSCAN":
        _render_dbscan(X, X_scaled, cols)
    elif "Hierarchical" in method:
        _render_hierarchical(X, X_scaled, cols)


def _render_kmeans(X, X_scaled, cols, scaler):
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


def _render_dbscan(X, X_scaled, cols):
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


def _render_hierarchical(X, X_scaled, cols):
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
        try:
            import matplotlib.pyplot as plt
            linkage_matrix = scipy_linkage(X_scaled, method=linkage)
            fig, ax = plt.subplots(figsize=(10, 5))
            dendrogram(linkage_matrix, ax=ax, color_threshold=0.7 * max(linkage_matrix[:, 2]),
                      above_threshold_color='gray')
            ax.set_title("Dendrogram")
            st.pyplot(fig)
            plt.close()
        except:
            pass