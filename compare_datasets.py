"""Compare Datasets tab — side-by-side comparison of multiple datasets"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from helpers import apply_theme


def render_compare_tab():
    """Render the Compare Datasets tab"""
    st.markdown("### ⚖️ So sánh Datasets")
    st.caption("So sánh cấu trúc và thống kê giữa các datasets")

    if len(st.session_state.datasets) < 2:
        st.warning("⚠️ Cần ít nhất 2 datasets để so sánh. Upload thêm datasets từ sidebar.")
        return

    dataset_names = list(st.session_state.datasets.keys())
    col1, col2 = st.columns(2)
    with col1:
        ds1 = st.selectbox("Dataset 1:", dataset_names, key="compare_ds1")
    with col2:
        ds2 = st.selectbox("Dataset 2:", [n for n in dataset_names if n != ds1], key="compare_ds2")

    if ds1 and ds2:
        df1 = st.session_state.datasets[ds1]
        df2 = st.session_state.datasets[ds2]

        st.markdown("#### 📊 So sánh cơ bản")
        comp_data = {
            "Metric": ["Rows", "Columns", "Numeric Columns", "Categorical Columns", "Missing Values", "Memory Usage (MB)"],
            ds1: [len(df1), len(df1.columns),
                  len(df1.select_dtypes(include=[np.number]).columns),
                  len(df1.select_dtypes(include=["object", "category"]).columns),
                  df1.isnull().sum().sum(),
                  round(df1.memory_usage(deep=True).sum() / 1024 / 1024, 2)],
            ds2: [len(df2), len(df2.columns),
                  len(df2.select_dtypes(include=[np.number]).columns),
                  len(df2.select_dtypes(include=["object", "category"]).columns),
                  df2.isnull().sum().sum(),
                  round(df2.memory_usage(deep=True).sum() / 1024 / 1024, 2)]
        }
        st.dataframe(pd.DataFrame(comp_data), width='stretch', hide_index=True)

        st.markdown("#### 🔗 So sánh columns")
        cols1 = set(df1.columns)
        cols2 = set(df2.columns)
        common_cols = cols1.intersection(cols2)
        only_in_1 = cols1 - cols2
        only_in_2 = cols2 - cols1

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Common Columns", len(common_cols))
            if common_cols:
                with st.expander("Xem danh sách"):
                    st.write(", ".join(sorted(common_cols)))
        with c2:
            st.metric(f"Only in {ds1}", len(only_in_1))
            if only_in_1:
                with st.expander("Xem danh sách"):
                    st.write(", ".join(sorted(only_in_1)))
        with c3:
            st.metric(f"Only in {ds2}", len(only_in_2))
            if only_in_2:
                with st.expander("Xem danh sách"):
                    st.write(", ".join(sorted(only_in_2)))

        if common_cols:
            st.markdown("#### 📈 So sánh thống kê (các cột numeric chung)")
            common_num = [c for c in common_cols
                         if c in df1.select_dtypes(include=[np.number]).columns
                         and c in df2.select_dtypes(include=[np.number]).columns]
            if common_num:
                stat_comp = []
                for col in common_num[:10]:
                    s1 = df1[col].dropna()
                    s2 = df2[col].dropna()
                    if len(s1) > 0 and len(s2) > 0:
                        stat_comp.append({
                            "Column": col,
                            f"{ds1} - Mean": round(s1.mean(), 4),
                            f"{ds2} - Mean": round(s2.mean(), 4),
                            "Diff": round(s1.mean() - s2.mean(), 4),
                            f"{ds1} - Std": round(s1.std(), 4),
                            f"{ds2} - Std": round(s2.std(), 4),
                        })
                if stat_comp:
                    st.dataframe(pd.DataFrame(stat_comp), width='stretch', hide_index=True)
                    if st.button("📊 Vẽ biểu đồ so sánh", key="plot_compare"):
                        for col in common_num[:5]:
                            fig = go.Figure()
                            fig.add_trace(go.Box(y=df1[col].dropna(), name=ds1, marker_color="#818cf8"))
                            fig.add_trace(go.Box(y=df2[col].dropna(), name=ds2, marker_color="#34d399"))
                            fig.update_layout(title=f"Compare: {col}", height=300)
                            apply_theme(fig)
                            st.plotly_chart(fig, width='stretch')