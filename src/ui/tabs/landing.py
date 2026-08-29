"""Landing page — Pro Max Data-Dense + Bento Grid, Lucide icons (no emoji)."""
import streamlit as st

from src.ui.components import render_quick_start_tutorial

try:
    from src.ui.theme import metric_card, gradient_text, status_badge, icon
except ImportError:
    def metric_card(title, value, change="", icon="chart", color="primary"):
        return f'<div class="metric-card"><h4>{icon} {title}</h4><h2>{value}</h2></div>'

    def gradient_text(text, color1="#1E40AF", color2="#D97706"):
        return f"<span style='font-weight:700'>{text}</span>"

    def status_badge(text, status="primary"):
        return f"<span>{text}</span>"

    def icon(name, size=""):
        return ""


def render_landing_page() -> None:
    """Render the landing page with hero, metric cards, quick start guide and CTA."""

    # ═══════════════════════════════════════════════════
    # HERO SECTION
    # ═══════════════════════════════════════════════════
    # Hero — Pro Max: subtle, data-dense, blue→amber accent, Fira Sans
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 2.5rem 1rem 1.5rem;
        background: var(--card);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-lg);
        margin-bottom: 12px;
        box-shadow: var(--shadow-sm);
    ">
        <div style="display:flex;justify-content:center;margin-bottom:8px">{icon("graduation")}</div>
        <h1 style="font-size: 2.1rem; font-weight: 700; letter-spacing: -0.02em; margin: 0; font-family: var(--font-display);">
            Learning Analytics <span style="color: var(--primary);">Thống kê</span>
        </h1>
        <p style="font-size: 0.92rem; color: var(--text-secondary); max-width: 560px; margin: 6px auto 0; line-height: 1.5;">
            Phân tích dữ liệu học tập, điểm số, nhóm rủi ro và kiểm định thống kê
        </p>
        <p style="font-size: 0.78rem; color: var(--text-tertiary); margin: 4px 0 0;">
            Practical Statistics for Data Scientists, 2nd Ed — <span style="color:var(--accent);font-weight:600">Pro Max Data-Dense</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════
    # CAPABILITY CARDS  —  what you can do with this tool
    # ═══════════════════════════════════════════════════
    # Capability cards — Pro Max Bento: Lucide icons, compact
    caps = [
        ("upload", "Upload dữ liệu", "CSV / Excel — nhiều file cùng lúc, 50MB", "primary"),
        ("chart", "Khám phá", "Dashboard tổng quan, profiling, quality", "success"),
        ("trending", "Thống kê & ML", "T-test, ANOVA, Bootstrap, Regression, PCA", "info"),
        ("sparkles", "AI Insights", "Tóm tắt & khuyến nghị tự động", "accent"),
    ]
    cap_cols = st.columns(4)
    for i, (ic, title, desc, color) in enumerate(caps):
        with cap_cols[i]:
            st.markdown(f"""
            <div class="feature-card tone-{color} animate-fade-in" style="display:flex;flex-direction:column;gap:6px;min-height:132px;">
                <div style="color: var(--{color if color!='accent' else 'accent'});">{icon(ic)}</div>
                <div style="font-size:0.88rem;font-weight:600;color:var(--text-primary)">{title}</div>
                <div style="color:var(--text-secondary);font-size:0.80rem;line-height:1.4;overflow-wrap:break-word">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='sp-md'></div>", unsafe_allow_html=True)

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
        <div class="cta-banner animate-fade-in">
            📥 Upload dữ liệu từ sidebar để bắt đầu
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='sp-md'></div>", unsafe_allow_html=True)

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