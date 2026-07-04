"""Landing page — hero section and feature grid shown when no data is loaded"""
import streamlit as st

from components import render_quick_start_tutorial


def render_landing_page() -> None:
    """Render the landing page with hero section, feature cards, and quick start tutorial."""
    st.markdown("""
    <div class="hero-bg">
        <div class="hero">
            <h1 class="hero-title">Learning Analytics Thống kê</h1>
            <p class="hero-subtitle">Phân tích dữ liệu học tập, điểm số, nhóm rủi ro và kiểm định thống kê cho sinh viên ngành Thống kê</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Feature Grid: 3 columns × 2 rows ──
    features = [
        ("📂", "Upload", "CSV & Excel"),
        ("🎓", "Learning", "Điểm & rủi ro"),
        ("🔬", "Statistics", "Hypothesis Testing"),
        ("🎲", "Bootstrap", "Confidence Intervals"),
        ("⚗️", "A/B Testing", "Power Analysis"),
        ("🔴", "Logistic", "ROC & AUC"),
    ]

    for row_start in range(0, 6, 3):
        cols = st.columns(3)
        for i in range(3):
            icon, title, subtitle = features[row_start + i]
            with cols[i]:
                st.markdown(f"""
                <div class="feature-card">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-title">{title}</div>
                    <div class="feature-subtitle">{subtitle}</div>
                </div>
                """, unsafe_allow_html=True)

    # ── Info hints ──
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.info("**📂 Upload** — CSV hoặc Excel từ sidebar")
    c2.success("**🎓 Learning Analytics** — điểm số, tỷ lệ đạt, nhóm rủi ro")
    c3.warning("**🧠 Deep Analysis** — 11 modules phân tích chuyên sâu")

    st.caption("Upload dữ liệu từ sidebar để bắt đầu →")
    render_quick_start_tutorial()