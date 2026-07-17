"""AI Auto Insights Module - LLM-powered report generation with LangChain integration"""
import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

from src.core.ai_service import get_ai_service, AIInsight, AIReport

def generate_data_summary(df: pd.DataFrame) -> str:
    """Generate comprehensive data summary for AI analysis"""
    summary = []
    
    # Basic info
    summary.append(f"Dataset có {len(df):,} dòng và {len(df.columns)} cột.")
    
    # Data types
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    date_cols = df.select_dtypes(include=["datetime64", "datetime64[ns]"]).columns.tolist()
    
    summary.append(f"- {len(num_cols)} cột numeric: {', '.join(num_cols[:5])}{'...' if len(num_cols) > 5 else ''}")
    summary.append(f"- {len(cat_cols)} cột categorical: {', '.join(cat_cols[:5])}{'...' if len(cat_cols) > 5 else ''}")
    if date_cols:
        summary.append(f"- {len(date_cols)} cột datetime: {', '.join(date_cols[:3])}")
    
    # Missing values
    missing = df.isnull().sum().sum()
    missing_pct = (missing / (len(df) * len(df.columns))) * 100
    summary.append(f"- {missing:,} giá trị thiếu ({missing_pct:.1f}%)")
    
    # Duplicates
    dupes = df.duplicated().sum()
    summary.append(f"- {dupes:,} dòng trùng lặp")
    
    # Numeric statistics
    if num_cols:
        summary.append("\nThống kê các cột numeric:")
        for col in num_cols[:5]:
            stats = df[col].describe()
            summary.append(f"- {col}: mean={stats['mean']:.2f}, std={stats['std']:.2f}, min={stats['min']:.2f}, max={stats['max']:.2f}")
    
    # Categorical statistics
    if cat_cols:
        summary.append("\nPhân phối các cột categorical (top 3):")
        for col in cat_cols[:3]:
            top_vals = df[col].value_counts().head(3)
            summary.append(f"- {col}: {', '.join([f'{idx} ({cnt})' for idx, cnt in top_vals.items()])}")
    
    return "\n".join(summary)

def generate_learning_insights(df: pd.DataFrame, score_col: str, group_col: str = None) -> str:
    """Generate insights specific to learning analytics"""
    insights = []
    
    # Score analysis
    if score_col in df.columns:
        scores = pd.to_numeric(df[score_col], errors='coerce').dropna()
        if len(scores) > 0:
            insights.append(f"Phân tích cột '{score_col}':")
            insights.append(f"- Điểm trung bình: {scores.mean():.2f}")
            insights.append(f"- Điểm cao nhất: {scores.max():.2f}")
            insights.append(f"- Điểm thấp nhất: {scores.min():.2f}")
            insights.append(f"- Độ lệch chuẩn: {scores.std():.2f}")
            
            # Pass rate (assuming 5.0 scale)
            pass_rate = (scores >= 5.0).mean() * 100
            insights.append(f"- Tỷ lệ đạt (>=5.0): {pass_rate:.1f}%")
            
            # Risk students (< 4.0)
            risk_rate = (scores < 4.0).mean() * 100
            insights.append(f"- Tỷ lệ rủi ro (<4.0): {risk_rate:.1f}%")
            
            # Distribution
            insights.append(f"- Phân phối: 25%={scores.quantile(0.25):.2f}, 50%={scores.median():.2f}, 75%={scores.quantile(0.75):.2f}")
    
    # Group analysis
    if group_col and group_col in df.columns:
        insights.append(f"\nPhân tích theo nhóm '{group_col}':")
        groups = df.groupby(group_col)[score_col].agg(['count', 'mean', 'std']).round(2)
        insights.append(f"Số nhóm: {len(groups)}")
        insights.append(f"Nhóm có điểm cao nhất: {groups['mean'].idxmax()} ({groups['mean'].max():.2f})")
        insights.append(f"Nhóm có điểm thấp nhất: {groups['mean'].idxmin()} ({groups['mean'].min():.2f})")
    
    return "\n".join(insights)

def generate_ai_report(df: pd.DataFrame, analysis_type: str = "overview", 
                       score_col: str = None, group_col: str = None) -> Dict[str, Any]:
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
    from theme_config import metric_card, status_badge, gradient_text
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
                key="ai_provider_config"
            )
            st.session_state.ai_provider = provider
        with col2:
            api_key = st.text_input(
                "API Key:",
                type="password",
                value=st.session_state.get("ai_api_key", ""),
                help="Nhập API key của OpenAI hoặc Google Gemini. Để trống để dùng chế độ rule-based.",
                key="ai_api_key_input"
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
        key="ai_analysis_type"
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
            "Cột điểm/kết quả:",
            num_cols,
            index=num_cols.index(score_guess) if score_guess else 0,
            key="ai_score_col"
        )
        
        if cat_cols:
            group_col = st.selectbox(
                "Cột phân nhóm (tùy chọn):",
                ["Không phân nhóm"] + cat_cols,
                key="ai_group_col"
            )
            if group_col == "Không phân nhóm":
                group_col = None
    
    # Generate button
    if st.button("🤖 Generate AI Insights", type="primary", width="stretch", key="gen_ai_insights"):
        with st.spinner("Đang phân tích và tạo insights..."):
            report = generate_ai_report(df, analysis_type, score_col, group_col)
            
            # Store in session state
            st.session_state.ai_report = report
    
    # Display report
    if 'ai_report' in st.session_state and st.session_state.ai_report is not None:
        report = st.session_state.ai_report
        
        st.markdown("---")
        st.markdown("## 📋 Báo cáo Insights")
        
        # Show which model was used
        model_used = report.get("model_used", "rule-based")
        if model_used == "rule-based":
            st.info("ℹ️ Báo cáo được tạo bằng **rule-based engine** (không dùng LLM). Cấu hình API key để có phân tích AI mạnh hơn.")
        else:
            st.success(f"✅ Báo cáo được tạo bằng **{model_used}**")
        
        # Summary section
        with st.expander("📊 Tóm tắt dữ liệu", expanded=True):
            st.markdown(report['summary'])
        
        # Specific insights
        if report['specific_insights']:
            with st.expander("🎯 Phân tích chi tiết", expanded=True):
                st.markdown(report['specific_insights'])
        
        # AI Insights
        st.markdown("### 💡 AI Insights")
        for insight in report['ai_insights']:
            st.markdown(f"""
            <div class="insight-card insight-{insight['type']}">
                <strong>{insight['icon']} {insight['title']}</strong><br>
                {insight['message']}
            </div>
            """, unsafe_allow_html=True)
        
        # Recommendations
        st.markdown("### ✅ Khuyến nghị")
        for i, rec in enumerate(report['recommendations'], 1):
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
        for insight in report['ai_insights']:
            report_text += f"\n### {insight['icon']} {insight['title']}\n{insight['message']}\n"
        
        report_text += "\n## Recommendations\n"
        for i, rec in enumerate(report['recommendations'], 1):
            report_text += f"{i}. {rec}\n"
        
        st.download_button(
            "📥 Download Report (Markdown)",
            report_text,
            f"ai_insights_{pd.Timestamp.now():%Y%m%d_%H%M}.md",
            "text/markdown"
        )