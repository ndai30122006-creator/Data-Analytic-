"""Landing page — hero section and feature grid shown when no data is loaded"""
import streamlit as st

from components import render_quick_start_tutorial


def render_landing_page() -> None:
    """
    Render the landing page with hero section, feature cards, and quick start tutorial.

    Displays a hero banner, a grid of feature cards (Upload, Learning, Statistics,
    Bootstrap, A/B Testing, Logistic), info/success/warning hints, and a quick start
    tutorial expander for new users.

    Returns:
        None — renders directly into Streamlit
    """
    st.markdown("""
    <div class="hero-bg">
        <div class="hero">
            <h1>Learning Analytics Thống kê</h1>
            <p>Phân tích dữ liệu học tập, điểm số, nhóm rủi ro và kiểm định thống kê cho sinh viên ngành Thống kê</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card"><div class="icon">📂</div><div class="title">Upload</div><div class="desc">CSV & Excel</div></div>
        <div class="feature-card"><div class="icon">🎓</div><div class="title">Learning</div><div class="desc">Điểm & rủi ro</div></div>
        <div class="feature-card"><div class="icon">🔬</div><div class="title">Statistics</div><div class="desc">Hypothesis Testing</div></div>
        <div class="feature-card"><div class="icon">🎲</div><div class="title">Bootstrap</div><div class="desc">Confidence Intervals</div></div>
        <div class="feature-card"><div class="icon">⚗️</div><div class="title">A/B Testing</div><div class="desc">Power Analysis</div></div>
        <div class="feature-card"><div class="icon">🔴</div><div class="title">Logistic</div><div class="desc">ROC & AUC</div></div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.info("**📂 Upload** — CSV hoặc Excel từ sidebar")
    c2.success("**🎓 Learning Analytics** — điểm số, tỷ lệ đạt, nhóm rủi ro")
    c3.warning("**🧠 Deep Analysis** — 11 modules phân tích chuyên sâu")

    st.caption("Upload dữ liệu từ sidebar để bắt đầu →")
    render_quick_start_tutorial()