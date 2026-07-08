"""Landing page — hero section, KPI metrics, quick-start guide, and CTA when no data is loaded."""
import streamlit as st

from components import render_quick_start_tutorial

try:
    from theme_config import metric_card, gradient_text, status_badge
except ImportError:
    # Fallback stubs if theme_config is unavailable
    def metric_card(title, value, change="", icon="📊", color="primary"):
        return f'<div class="metric-card"><h4>{icon} {title}</h4><h2>{value}</h2></div>'

    def gradient_text(text, color1="#1877F2", color2="#E4405F"):
        return f"<span style='font-weight:700'>{text}</span>"

    def status_badge(text, status="primary"):
        return f"<span>{text}</span>"


def render_landing_page() -> None:
    """Render the landing page with hero, metric cards, quick start guide and CTA."""

    # ═══════════════════════════════════════════════════
    # HERO SECTION
    # ═══════════════════════════════════════════════════
    st.markdown("""
    <div style="
        text-align: center;
        padding: 3.5rem 1rem 2rem;
        background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-light);
        margin-bottom: 1.5rem;
    ">
        <h1 style="font-size: 2.5rem; font-weight: 800; letter-spacing: -1px; margin-bottom: 0.5rem;">
            🎓 Learning Analytics Thống kê
        </h1>
        <p style="font-size: 1.05rem; color: var(--text-secondary); max-width: 560px; margin: 0 auto 0.5rem;">
            Phân tích dữ liệu học tập, điểm số, nhóm rủi ro và kiểm định thống kê
        </p>
        <p style="font-size: 0.85rem; color: var(--text-tertiary); margin-top: 0;">
            Practical Statistics for Data Scientists, 2nd Ed
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════
    # KPI METRIC CARDS  —  row of 4
    # ═══════════════════════════════════════════════════
    kpis = [
        ("Total Students", "1,250", "↑ 5.3%", "👥"),
        ("Avg Score",      "87.4",  "↑ 2.1%", "📚"),
        ("Courses",        "24",    "→ 0%",   "🎯"),
        ("Graduation",     "94.2%", "↑ 1.8%", "🎓"),
    ]
    cols = st.columns(4)
    for i, (label, value, change, icon) in enumerate(kpis):
        with cols[i]:
            st.markdown(metric_card(label, value, change, icon),
                        unsafe_allow_html=True)

    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════
    # QUICK START GUIDE  (step-by-step)
    # ═══════════════════════════════════════════════════
    st.markdown("### 🚀 Quick Start Guide")
    st.caption("4 bước đơn giản để bắt đầu phân tích dữ liệu của bạn")

    step_cols = st.columns(4)
    steps = [
        ("1️⃣", "Upload", "Tải lên file CSV hoặc Excel từ sidebar", "primary"),
        ("2️⃣", "Overview", "Khám phá dashboard tổng quan dữ liệu", "success"),
        ("3️⃣", "Phân tích", "Chọn tab Statistics, AI Insights,...", "warning"),
        ("4️⃣", "Export", "Xuất báo cáo PDF / CSV kết quả", "danger"),
    ]
    for i, (num, title, desc, badge) in enumerate(steps):
        with step_cols[i]:
            st.markdown(f"""
            <div style="
                background: var(--bg-secondary);
                border: 1px solid var(--border-light);
                border-radius: var(--radius-lg);
                padding: 1.25rem 1rem;
                text-align: center;
                min-height: 140px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                gap: 0.3rem;
                transition: all var(--transition);
            ">
                <div style="font-size: 2rem;">{num}</div>
                <div style="font-weight: 600; color: var(--text-primary); font-size: 1rem;">{title}</div>
                <div style="color: var(--text-secondary); font-size: 0.82rem; line-height: 1.4;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════
    # CALL-TO-ACTION  +  ADVANCED BADGES
    # ═══════════════════════════════════════════════════
    cta_col1, cta_col2, cta_col3 = st.columns([1, 2, 1])
    with cta_col2:
        st.markdown("""
        <div style="
            background: var(--primary-color);
            color: #fff;
            border-radius: var(--radius-md);
            padding: 0.75rem 1.5rem;
            text-align: center;
            font-weight: 600;
            font-size: 1.1rem;
            box-shadow: 0 4px 15px rgba(24, 119, 242, 0.3);
            cursor: default;
        ">
            📥 Upload dữ liệu từ sidebar để bắt đầu
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 0.75rem'></div>", unsafe_allow_html=True)

    # Feature badges row
    badge_cols = st.columns(5)
    badges = [
        ("📊", "Statistics", "success"),
        ("🤖", "AI Insights", "primary"),
        ("🧠", "Deep Analysis", "warning"),
        ("⚖️", "Compare", "info"),
        ("🔬", "Analytics", "danger"),
    ]
    for i, (icon, label, color) in enumerate(badges):
        with badge_cols[i]:
            st.markdown(
                f"<div style='text-align:center; padding:0.25rem 0;'>"
                f"{status_badge(f'{icon} {label}', color)}"
                f"</div>",
                unsafe_allow_html=True
            )

    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════
    # DETAILED TUTORIAL (expandable)
    # ═══════════════════════════════════════════════════
    render_quick_start_tutorial()