"""Learning Analytics tab — scores, pass rates, risk groups"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from helpers import apply_theme, guess_learning_column
from components import render_kpi_card


def render_learning_analytics_tab(df, num_cols, cat_cols):
    st.markdown("### 🎓 Phân tích dữ liệu học tập ngành Thống kê")
    st.caption("Phân tích điểm số, nhóm học tập, tỷ lệ đạt và dấu hiệu cần hỗ trợ sớm.")

    if not num_cols:
        st.warning("Cần ít nhất một cột số, ví dụ: điểm giữa kỳ, điểm cuối kỳ, điểm tổng kết.")
        return

    score_guess = guess_learning_column(
        num_cols,
        ["score", "grade", "mark", "point", "diem", "gpa", "final", "tong_ket", "cuoi_ky"]
    )
    group_guess = guess_learning_column(
        cat_cols,
        ["class", "lop", "course", "mon", "subject", "major", "nganh", "group", "nhom", "gender", "gioi_tinh"]
    )

    score_default = num_cols.index(score_guess) if score_guess in num_cols else 0
    group_default = cat_cols.index(group_guess) + 1 if group_guess in cat_cols else 0

    control_cols = st.columns([2, 2, 1, 1])
    with control_cols[0]:
        score_col = st.selectbox("Cột điểm/kết quả", num_cols, index=score_default, key="la_score_col")
    with control_cols[1]:
        group_options = ["Không phân nhóm"] + cat_cols
        group_col = st.selectbox("Phân tích theo nhóm", group_options, index=group_default, key="la_group_col")
    with control_cols[2]:
        pass_mark = st.number_input("Ngưỡng đạt", value=5.0, step=0.5, key="la_pass_mark")
    with control_cols[3]:
        risk_mark = st.number_input("Ngưỡng rủi ro", value=4.0, step=0.5, key="la_risk_mark")

    analysis_df = df[[score_col] + ([group_col] if group_col != "Không phân nhóm" else [])].copy()
    analysis_df[score_col] = pd.to_numeric(analysis_df[score_col], errors="coerce")
    analysis_df = analysis_df.dropna(subset=[score_col])

    if analysis_df.empty:
        st.warning("Cột điểm đã chọn không có giá trị số hợp lệ.")
        return

    score = analysis_df[score_col]
    pass_rate = (score >= pass_mark).mean() * 100
    risk_rate = (score < risk_mark).mean() * 100

    kpis = st.columns(5)
    render_kpi_card(kpis[0], "Số quan sát", f"{len(analysis_df):,}")
    render_kpi_card(kpis[1], "Điểm TB", f"{score.mean():.2f}")
    render_kpi_card(kpis[2], "Trung vi", f"{score.median():.2f}")
    render_kpi_card(kpis[3], "Tỷ lệ đạt", f"{pass_rate:.1f}%")
    render_kpi_card(kpis[4], "Nhóm rủi ro", f"{risk_rate:.1f}%")

    chart_cols = st.columns(2)
    with chart_cols[0]:
        fig = px.histogram(
            analysis_df, x=score_col, nbins=30, marginal="box",
            title=f"Phân phối {score_col}", color_discrete_sequence=["#34d399"]
        )
        fig.add_vline(x=pass_mark, line_dash="dash", line_color="#22c55e", annotation_text="Đạt")
        fig.add_vline(x=risk_mark, line_dash="dash", line_color="#ef4444", annotation_text="Rủi ro")
        apply_theme(fig)
        st.plotly_chart(fig, width="stretch")

    with chart_cols[1]:
        categories = pd.cut(
            score,
            bins=[-np.inf, risk_mark, pass_mark, np.inf],
            labels=["Cần hỗ trợ", "Cần theo dõi", "Đạt"]
        )
        status_counts = categories.value_counts().reindex(["Cần hỗ trợ", "Cần theo dõi", "Đạt"]).fillna(0)
        fig = px.bar(
            x=status_counts.index.astype(str), y=status_counts.values,
            title="Phân loại kết quả học tập",
            color=status_counts.index.astype(str),
            color_discrete_map={"Cần hỗ trợ": "#ef4444", "Cần theo dõi": "#eab308", "Đạt": "#22c55e"}
        )
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Số lượng")
        apply_theme(fig)
        st.plotly_chart(fig, width="stretch")

    if group_col != "Không phân nhóm":
        st.markdown("#### So sánh theo nhóm")
        summary = analysis_df.groupby(group_col, dropna=False)[score_col].agg(
            ["count", "mean", "median", "std"]
        ).reset_index()
        summary["pass_rate"] = analysis_df.groupby(group_col, dropna=False)[score_col].apply(
            lambda s: (s >= pass_mark).mean() * 100
        ).values
        summary["risk_rate"] = analysis_df.groupby(group_col, dropna=False)[score_col].apply(
            lambda s: (s < risk_mark).mean() * 100
        ).values
        summary = summary.sort_values("mean", ascending=False)
        st.dataframe(summary.round(2), width="stretch", hide_index=True)

        fig = px.box(analysis_df, x=group_col, y=score_col, points="outliers",
                     title=f"{score_col} theo {group_col}")
        apply_theme(fig)
        st.plotly_chart(fig, width="stretch")

    st.markdown("#### Gợi ý đọc kết quả")
    if risk_rate >= 25:
        st.warning("Tỷ lệ nhóm rủi ro đang cao. Nên xem lại phân bố điểm, độ khó học phần, và các nhóm/lớp có điểm trung bình thấp.")
    elif pass_rate >= 80:
        st.success("Tỷ lệ đạt khá tốt. Có thể tiếp tục xem nhóm xuất sắc và các yếu tố liên quan đến kết quả cao.")
    else:
        st.info("Kết quả ở mức cần theo dõi. Nên kết hợp thêm cột chuyên cần, bài tập, LMS hoặc điểm thành phần để phân tích sâu hơn.")