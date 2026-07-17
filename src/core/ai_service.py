"""
AI Service — LangChain-powered LLM integration for generating insights.

Supports OpenAI and Google Gemini models.
Falls back to rule-based insights when no API key is configured.
"""
import logging
import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class AIInsight:
    """A single AI-generated insight."""
    type: str  # "success", "info", "warning", "danger"
    icon: str
    title: str
    message: str


@dataclass
class AIReport:
    """Complete AI-generated report."""
    summary: str
    specific_insights: str
    ai_insights: List[AIInsight]
    recommendations: List[str]
    analysis_type: str
    model_used: str = "rule-based"  # "openai", "gemini", or "rule-based"


class AIService:
    """
    AI Service that uses LangChain to call OpenAI/Gemini APIs.
    Falls back to rule-based insights when no API key is available.
    """

    def __init__(self, api_key: Optional[str] = None, provider: str = "openai"):
        self.api_key = api_key or os.environ.get("AI_API_KEY", "")
        self.provider = provider.lower()
        self._llm = None
        self._initialized = False

    def _init_llm(self) -> bool:
        """Initialize the LangChain LLM. Returns True if successful."""
        if self._initialized:
            return self._llm is not None

        if not self.api_key:
            logger.info("No AI API key configured; using rule-based insights")
            self._initialized = True
            return False

        try:
            if self.provider == "openai":
                from langchain_openai import ChatOpenAI
                self._llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    temperature=0.3,
                    api_key=self.api_key,
                )
                logger.info("OpenAI LLM initialized (gpt-4o-mini)")
            elif self.provider == "gemini":
                from langchain_google_genai import ChatGoogleGenerativeAI
                self._llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",
                    temperature=0.3,
                    google_api_key=self.api_key,
                )
                logger.info("Gemini LLM initialized (gemini-2.0-flash)")
            else:
                logger.warning("Unknown provider '%s'; falling back to rule-based", self.provider)
                self._initialized = True
                return False

            self._initialized = True
            return True
        except ImportError as exc:
            logger.warning(
                "Failed to import LangChain provider '%s': %s. "
                "Install with: pip install langchain-%s",
                self.provider, exc, self.provider,
            )
            self._initialized = True
            return False
        except Exception as exc:
            logger.error("Failed to initialize LLM: %s", exc, exc_info=True)
            self._initialized = True
            return False

    def _build_prompt(self, df: pd.DataFrame, analysis_type: str,
                      score_col: Optional[str] = None,
                      group_col: Optional[str] = None) -> str:
        """Build a prompt for the LLM based on the data and analysis type."""
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        date_cols = df.select_dtypes(include=["datetime64", "datetime64[ns]"]).columns.tolist()

        prompt = f"""You are a data science expert analyzing a dataset. Provide insights in Vietnamese.

Dataset Information:
- Rows: {len(df):,}
- Columns: {len(df.columns)}
- Numeric columns: {', '.join(num_cols[:10])}
- Categorical columns: {', '.join(cat_cols[:10])}
- Date columns: {', '.join(date_cols[:5])}

Missing values: {df.isnull().sum().sum():,} total
Duplicate rows: {df.duplicated().sum():,}

"""
        if num_cols:
            prompt += "\nNumeric column statistics:\n"
            for col in num_cols[:5]:
                stats = df[col].describe()
                prompt += f"- {col}: mean={stats['mean']:.2f}, std={stats['std']:.2f}, "
                prompt += f"min={stats['min']:.2f}, max={stats['max']:.2f}\n"

        if analysis_type == "learning" and score_col and score_col in df.columns:
            scores = pd.to_numeric(df[score_col], errors='coerce').dropna()
            if len(scores) > 0:
                prompt += f"\nLearning Analysis for '{score_col}':\n"
                prompt += f"- Mean: {scores.mean():.2f}\n"
                prompt += f"- Pass rate (>=5.0): {(scores >= 5.0).mean() * 100:.1f}%\n"
                prompt += f"- Risk rate (<4.0): {(scores < 4.0).mean() * 100:.1f}%\n"
                prompt += f"- Skewness: {scores.skew():.2f}\n"

                if group_col and group_col in df.columns:
                    prompt += f"\nGroup analysis by '{group_col}':\n"
                    groups = df.groupby(group_col)[score_col].agg(['count', 'mean', 'std']).round(2)
                    prompt += f"- Number of groups: {len(groups)}\n"
                    prompt += f"- Top group: {groups['mean'].idxmax()} ({groups['mean'].max():.2f})\n"
                    prompt += f"- Bottom group: {groups['mean'].idxmin()} ({groups['mean'].min():.2f})\n"

        prompt += """
Please provide:
1. Key findings and patterns in the data
2. Specific actionable insights
3. Potential issues or risks
4. Recommendations for further analysis

Format your response as JSON with these keys:
- summary: Brief data summary
- insights: List of insight objects with type (success/info/warning/danger), icon, title, message
- recommendations: List of recommendation strings
"""
        return prompt

    def _parse_llm_response(self, response_content: str) -> Dict[str, Any]:
        """Parse LLM response into structured format."""
        import json
        try:
            # Try to parse as JSON
            result = json.loads(response_content)
            return result
        except (json.JSONDecodeError, ValueError):
            # Fallback: extract sections from text
            logger.warning("LLM response was not valid JSON; parsing as text")
            return {
                "summary": response_content[:500],
                "insights": [
                    {"type": "info", "icon": "🤖", "title": "AI Analysis",
                     "message": response_content[:200]}
                ],
                "recommendations": ["Review the AI analysis above for detailed insights"]
            }

    def _generate_rule_based_insights(self, df: pd.DataFrame, analysis_type: str,
                                       score_col: Optional[str] = None,
                                       group_col: Optional[str] = None) -> AIReport:
        """Generate insights using rule-based logic (fallback when no LLM)."""
        from ai_insights import generate_data_summary, generate_learning_insights

        data_summary = generate_data_summary(df)
        specific_insights = ""
        if analysis_type == "learning" and score_col:
            specific_insights = generate_learning_insights(df, score_col, group_col)

        ai_insights_list = []
        missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100

        if missing_pct > 10:
            ai_insights_list.append(AIInsight(
                type="warning", icon="⚠️", title="Chất lượng dữ liệu",
                message=f"Dữ liệu có {missing_pct:.1f}% giá trị thiếu. Nên xử lý missing values trước khi phân tích sâu."
            ))
        elif missing_pct > 0:
            ai_insights_list.append(AIInsight(
                type="info", icon="ℹ️", title="Chất lượng dữ liệu",
                message=f"Dữ liệu có {missing_pct:.1f}% giá trị thiếu, ở mức chấp nhận được."
            ))
        else:
            ai_insights_list.append(AIInsight(
                type="success", icon="✅", title="Chất lượng dữ liệu",
                message="Dữ liệu hoàn toàn không có giá trị thiếu. Rất tốt!"
            ))

        dupes = df.duplicated().sum()
        if dupes > 0:
            ai_insights_list.append(AIInsight(
                type="warning", icon="🔁", title="Dữ liệu trùng lặp",
                message=f"Phát hiện {dupes:,} dòng trùng lặp ({dupes/len(df)*100:.1f}%). Nên xóa để tránh bias."
            ))

        if analysis_type == "learning" and score_col and score_col in df.columns:
            scores = pd.to_numeric(df[score_col], errors='coerce').dropna()
            if len(scores) > 0:
                pass_rate = (scores >= 5.0).mean() * 100
                risk_rate = (scores < 4.0).mean() * 100

                if risk_rate >= 25:
                    ai_insights_list.append(AIInsight(
                        type="danger", icon="🚨", title="Cảnh báo học tập",
                        message=f"Tỷ lệ sinh viên rủi ro ({risk_rate:.1f}%) quá cao. Cần can thiệp sớm."
                    ))
                elif pass_rate >= 80:
                    ai_insights_list.append(AIInsight(
                        type="success", icon="🎯", title="Kết quả học tập",
                        message=f"Tỷ lệ đạt khá tốt ({pass_rate:.1f}%)."
                    ))
                else:
                    ai_insights_list.append(AIInsight(
                        type="info", icon="📊", title="Kết quả học tập",
                        message=f"Tỷ lệ đạt {pass_rate:.1f}%."
                    ))

        recommendations = []
        if missing_pct > 10:
            recommendations.append("Xử lý missing values trước khi phân tích sâu")
        if dupes > 0:
            recommendations.append("Loại bỏ dữ liệu trùng lặp")
        if len(df.select_dtypes(include=[np.number]).columns) >= 2:
            recommendations.append("Thực hiện phân tích tương quan giữa các biến numeric")
        if analysis_type == "learning" and score_col:
            recommendations.append("Phân tích yếu tố ảnh hưởng đến điểm số")
            recommendations.append("Xây dựng mô hình dự đoán kết quả học tập")
        if not recommendations:
            recommendations.append("Tiếp tục khám phá dữ liệu với các công cụ phân tích khác")

        return AIReport(
            summary=data_summary,
            specific_insights=specific_insights,
            ai_insights=ai_insights_list,
            recommendations=recommendations,
            analysis_type=analysis_type,
            model_used="rule-based",
        )

    def generate_report(self, df: pd.DataFrame, analysis_type: str = "overview",
                        score_col: Optional[str] = None,
                        group_col: Optional[str] = None) -> AIReport:
        """
        Generate an AI-powered insights report.
        
        Uses LangChain to call LLM API if configured, otherwise falls back to rule-based.
        """
        if not self._init_llm() or self._llm is None:
            return self._generate_rule_based_insights(df, analysis_type, score_col, group_col)

        try:
            prompt = self._build_prompt(df, analysis_type, score_col, group_col)
            response = self._llm.invoke(prompt)
            parsed = self._parse_llm_response(response.content)

            insights_list = []
            for ins in parsed.get("insights", []):
                insights_list.append(AIInsight(
                    type=ins.get("type", "info"),
                    icon=ins.get("icon", "ℹ️"),
                    title=ins.get("title", "Insight"),
                    message=ins.get("message", ""),
                ))

            return AIReport(
                summary=parsed.get("summary", ""),
                specific_insights=parsed.get("specific_insights", ""),
                ai_insights=insights_list,
                recommendations=parsed.get("recommendations", []),
                analysis_type=analysis_type,
                model_used=self.provider,
            )
        except Exception as exc:
            logger.error("LLM report generation failed: %s", exc, exc_info=True)
            return self._generate_rule_based_insights(df, analysis_type, score_col, group_col)


# Singleton instance
_ai_service: Optional[AIService] = None


def get_ai_service(api_key: Optional[str] = None, provider: str = "openai") -> AIService:
    """Get or create the singleton AI service instance."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService(api_key, provider)
    return _ai_service