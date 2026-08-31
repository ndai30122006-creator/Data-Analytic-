"""AI Auto Insights Module - LLM-powered report generation with LangChain integration"""

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import streamlit as st

from src.core.ai_service import AIInsight, AIReport, get_ai_service
from src.core.insights import generate_data_summary, generate_learning_insights


def generate_ai_report(
    df: pd.DataFrame, analysis_type: str = "overview", score_col: str = None, group_col: str = None
) -> Dict[str, Any]:
    """
    Generate AI-powered insights report.
    Uses LangChain to call LLM API (OpenAI/Gemini) if configured,
    otherwise falls back to rule-based insights.
    """
    # Get user's API key from session state if available
    api_key = st.session_state.get("ai_api_key", None)
    provider = st.session_state.get("ai_provider", "openai")

    # Use the AIService
    service = get_ai_service(api_key, provider)
    report = service.generate_report(df, analysis_type, score_col, group_col)

    # Convert to dict for backward compatibility
    return {
        "summary": report.summary,
        "specific_insights": report.specific_insights,
        "ai_insights": [
            {
                "type": ins.type,
                "icon": ins.icon,
                "title": ins.title,
                "message": ins.message,
            }
            for ins in report.ai_insights
        ],
        "recommendations": report.recommendations,
        "analysis_type": report.analysis_type,
        "model_used": report.model_used,
    }


try:
    from src.ui.theme import gradient_text, metric_card, status_badge
except ImportError:

    def metric_card(title, value, change="", icon="📊", color="primary"):
        return f'<div class="metric-card"><h4>{icon} {title}</h4><h2>{value}</h2></div>'

    def status_badge(text, status="primary"):
        return f"<span>{text}</span>"

    def gradient_text(text, c1="#1877F2", c2="#E4405F"):
        return f"<span style='font-weight:700'>{text}</span>"


def render_ai_insights_tab(df: pd.DataFrame, num_cols: List[str], cat_cols: List[str]):
    """Render AI Insights tab in Streamlit"""
    st.markdown("### 🤖 AI Auto Insights")
    st.caption("Phân tích tự động bằng AI, tạo báo cáo insights")

    # AI Provider configuration
    with st.expander("⚙️ Cấu hình AI", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            provider = st.selectbox(
                "AI Provider:",
                ["openai", "gemini"],
                format_func=lambda x: "OpenAI GPT" if x == "openai" else "Google Gemini",
                key="ai_provider_config",
            )
            st.session_state.ai_provider = provider
        with col2:
            api_key = st.text_input(
                "API Key:",
                type="password",
                value=st.session_state.get("ai_api_key", ""),
                help="Nhập API key của OpenAI hoặc Google Gemini. Để trống để dùng chế độ rule-based.",
                key="ai_api_key_input",
            )
            if api_key:
                st.session_state.ai_api_key = api_key
                st.success("✅ API Key đã được lưu trong session")
            else:
                st.info("ℹ️ Để trống sẽ dùng chế độ phân tích rule-based (không cần API key)")

    # Analysis type selector
    analysis_type = st.selectbox(
        "Loại phân tích:",
        ["overview", "learning"],
        format_func=lambda x: "📊 Tổng quan" if x == "overview" else "🎓 Học tập",
        key="ai_analysis_type",
    )

    # For learning analytics, select columns
    score_col = None
    group_col = None

    if analysis_type == "learning" and num_cols:
        score_guess = None
        for keyword in ["score", "grade", "mark", "point", "diem", "gpa", "final"]:
            for col in num_cols:
                if keyword in col.lower():
                    score_guess = col
                    break
            if score_guess:
                break

        score_col = st.selectbox(
            "Cột điểm/kết quả:", num_cols, index=num_cols.index(score_guess) if score_guess else 0, key="ai_score_col"
        )

        if cat_cols:
            group_col = st.selectbox("Cột phân nhóm (tùy chọn):", ["Không phân nhóm"] + cat_cols, key="ai_group_col")
            if group_col == "Không phân nhóm":
                group_col = None

    # Generate button
    if st.button("🤖 Generate AI Insights", type="primary", use_container_width=True, key="gen_ai_insights"):
        with st.spinner("Đang phân tích và tạo insights..."):
            report = generate_ai_report(df, analysis_type, score_col, group_col)

            # Store in session state
            st.session_state.ai_report = report

    # Display report
    if "ai_report" in st.session_state and st.session_state.ai_report is not None:
        report = st.session_state.ai_report

        st.markdown("---")
        st.markdown("## 📋 Báo cáo Insights")

        # Show which model was used
        model_used = report.get("model_used", "rule-based")
        if model_used == "rule-based":
            st.info(
                "ℹ️ Báo cáo được tạo bằng **rule-based engine** (không dùng LLM). Cấu hình API key để có phân tích AI mạnh hơn."
            )
        else:
            st.success(f"✅ Báo cáo được tạo bằng **{model_used}**")

        # Summary section
        with st.expander("📊 Tóm tắt dữ liệu", expanded=True):
            st.markdown(report["summary"])

        # Specific insights
        if report["specific_insights"]:
            with st.expander("🎯 Phân tích chi tiết", expanded=True):
                st.markdown(report["specific_insights"])

        # AI Insights
        st.markdown("### 💡 AI Insights")
        for insight in report["ai_insights"]:
            st.markdown(
                f"""
            <div class="insight-card insight-{insight['type']}">
                <strong>{insight['icon']} {insight['title']}</strong><br>
                {insight['message']}
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Recommendations
        st.markdown("### ✅ Khuyến nghị")
        for i, rec in enumerate(report["recommendations"], 1):
            st.markdown(f"{i}. {rec}")

        # Export report
        st.markdown("---")
        st.markdown("### 📥 Xuất báo cáo")

        # Generate text report
        report_text = f"""
# AI Insights Report
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
Model: {model_used}

## Summary
{report['summary']}

## Specific Insights
{report['specific_insights']}

## AI Insights
"""
        for insight in report["ai_insights"]:
            report_text += f"\n### {insight['icon']} {insight['title']}\n{insight['message']}\n"

        report_text += "\n## Recommendations\n"
        for i, rec in enumerate(report["recommendations"], 1):
            report_text += f"{i}. {rec}\n"

        st.download_button(
            "📥 Download Report (Markdown)",
            report_text,
            f"ai_insights_{pd.Timestamp.now():%Y%m%d_%H%M}.md",
            "text/markdown",
        )
