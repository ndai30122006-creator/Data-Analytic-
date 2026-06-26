"""AI Auto Insights Module - LLM-powered report generation"""
import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any

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
    Generate AI-powered insights report
    In production, this would call an LLM API (OpenAI, Gemini, etc.)
    """
    
    # Generate data summary
    data_summary = generate_data_summary(df)
    
    # Generate specific insights based on analysis type
    if analysis_type == "learning" and score_col:
        specific_insights = generate_learning_insights(df, score_col, group_col)
    else:
        specific_insights = ""
    
    # Simulate AI-generated insights (in production, call LLM API)
    ai_insights = []
    
    # Data quality insights
    missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    if missing_pct > 10:
        ai_insights.append({
            "type": "warning",
            "icon": "⚠️",
            "title": "Chất lượng dữ liệu",
            "message": f"Dữ liệu có {missing_pct:.1f}% giá trị thiếu. Nên xử lý missing values trước khi phân tích sâu."
        })
    elif missing_pct > 0:
        ai_insights.append({
            "type": "info",
            "icon": "ℹ️",
            "title": "Chất lượng dữ liệu",
            "message": f"Dữ liệu có {missing_pct:.1f}% giá trị thiếu, ở mức chấp nhận được."
        })
    else:
        ai_insights.append({
            "type": "success",
            "icon": "✅",
            "title": "Chất lượng dữ liệu",
            "message": "Dữ liệu hoàn toàn không có giá trị thiếu. Rất tốt!"
        })
    
    # Duplicate insights
    dupes = df.duplicated().sum()
    if dupes > 0:
        ai_insights.append({
            "type": "warning",
            "icon": "🔁",
            "title": "Dữ liệu trùng lặp",
            "message": f"Phát hiện {dupes:,} dòng trùng lặp ({dupes/len(df)*100:.1f}%). Nên xóa để tránh bias."
        })
    
    # Learning analytics insights
    if analysis_type == "learning" and score_col and score_col in df.columns:
        scores = pd.to_numeric(df[score_col], errors='coerce').dropna()
        if len(scores) > 0:
            pass_rate = (scores >= 5.0).mean() * 100
            risk_rate = (scores < 4.0).mean() * 100
            
            if risk_rate >= 25:
                ai_insights.append({
                    "type": "danger",
                    "icon": "🚨",
                    "title": "Cảnh báo học tập",
                    "message": f"Tỷ lệ sinh viên rủi ro ({risk_rate:.1f}%) quá cao. Cần can thiệp sớm và hỗ trợ đặc biệt."
                })
            elif pass_rate >= 80:
                ai_insights.append({
                    "type": "success",
                    "icon": "🎯",
                    "title": "Kết quả học tập",
                    "message": f"Tỷ lệ đạt khá tốt ({pass_rate:.1f}%). Có thể phân tích thêm yếu tố ảnh hưởng đến kết quả cao."
                })
            else:
                ai_insights.append({
                    "type": "info",
                    "icon": "📊",
                    "title": "Kết quả học tập",
                    "message": f"Tỷ lệ đạt {pass_rate:.1f}%. Nên kết hợp thêm dữ liệu chuyên cần, bài tập để phân tích sâu hơn."
                })
            
            # Distribution insight
            skewness = scores.skew()
            if abs(skewness) > 1:
                direction = "lệch phải" if skewness > 0 else "lệch trái"
                ai_insights.append({
                    "type": "info",
                    "icon": "📈",
                    "title": "Phân phối điểm",
                    "message": f"Phân phối điểm {direction} (skewness={skewness:.2f}). Điểm tập trung ở {'cao' if skewness < 0 else 'thấp'}."
                })
    
    # Correlation insights
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(num_cols) >= 2:
        corr_matrix = df[num_cols].corr()
        high_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    high_corr.append({
                        "cols": f"{corr_matrix.columns[i]} & {corr_matrix.columns[j]}",
                        "corr": corr_val
                    })
        
        if high_corr:
            ai_insights.append({
                "type": "info",
                "icon": "🔗",
                "title": "Tương quan mạnh",
                "message": f"Phát hiện {len(high_corr)} cặp biến có tương quan cao (>0.7): " + 
                           ", ".join([f"{h['cols']} (r={h['corr']:.2f})" for h in high_corr[:3]])
            })
    
    # Generate recommendations
    recommendations = []
    if missing_pct > 10:
        recommendations.append("Xử lý missing values trước khi phân tích sâu")
    if dupes > 0:
        recommendations.append("Loại bỏ dữ liệu trùng lặp")
    if len(num_cols) >= 2:
        recommendations.append("Thực hiện phân tích tương quan giữa các biến numeric")
    if analysis_type == "learning" and score_col:
        recommendations.append("Phân tích yếu tố ảnh hưởng đến điểm số")
        recommendations.append("Xây dựng mô hình dự đoán kết quả học tập")
    
    if not recommendations:
        recommendations.append("Tiếp tục khám phá dữ liệu với các công cụ phân tích khác")
    
    return {
        "summary": data_summary,
        "specific_insights": specific_insights,
        "ai_insights": ai_insights,
        "recommendations": recommendations,
        "analysis_type": analysis_type
    }

def render_ai_insights_tab(df: pd.DataFrame, num_cols: List[str], cat_cols: List[str]):
    """Render AI Insights tab in Streamlit"""
    st.markdown("### 🤖 AI Auto Insights")
    st.caption("Phân tích tự động bằng AI, tạo báo cáo insights")
    
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