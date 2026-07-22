"""Unit tests for AI Service (src/core/ai_service.py)"""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pandas as pd
import numpy as np

from src.core.ai_service import AIService, AIInsight, AIReport


class TestAIServiceInitialization:
    """Tests for AIService initialization."""

    def test_init_no_api_key(self):
        """Service should initialize without API key and fallback to rule-based."""
        service = AIService(api_key="")
        assert service.api_key == ""
        assert service._llm is None
        assert not service._initialized

    def test_init_with_api_key(self):
        """Service should store API key on init."""
        service = AIService(api_key="sk-test-key")
        assert service.api_key == "sk-test-key"

    def test_init_unknown_provider(self):
        """Service should handle unknown provider gracefully."""
        service = AIService(api_key="key", provider="unknown")
        result = service._init_llm()
        assert result is False


class TestAIServiceRuleBased:
    """Tests for rule-based insight generation (fallback)."""

    @pytest.fixture
    def service(self):
        return AIService(api_key="")

    @pytest.fixture
    def sample_df(self):
        np.random.seed(42)
        return pd.DataFrame({
            "student_id": [f"S{i:03d}" for i in range(1, 101)],
            "score": np.random.normal(6.5, 1.5, 100).clip(0, 10),
            "attendance": np.random.uniform(60, 100, 100),
        })

    def test_generate_overview_report(self, service, sample_df):
        """Test generating overview report with rule-based insights."""
        report = service.generate_report(sample_df, analysis_type="overview")
        assert isinstance(report, AIReport)
        assert report.analysis_type == "overview"
        assert report.model_used == "rule-based"
        assert len(report.ai_insights) > 0
        assert len(report.recommendations) > 0

    def test_generate_learning_report(self, service, sample_df):
        """Test generating learning analytics report."""
        report = service.generate_report(
            sample_df, analysis_type="learning",
            score_col="score", group_col=None
        )
        assert isinstance(report, AIReport)
        assert report.analysis_type == "learning"
        assert len(report.ai_insights) > 0

    def test_generate_learning_report_with_group(self, service, sample_df):
        """Test generating learning report with group column."""
        sample_df["class"] = np.random.choice(["A", "B"], 100)
        report = service.generate_report(
            sample_df, analysis_type="learning",
            score_col="score", group_col="class"
        )
        assert isinstance(report, AIReport)
        assert len(report.recommendations) > 0

    def test_empty_dataframe(self, service):
        """Test with empty dataframe."""
        df = pd.DataFrame()
        report = service.generate_report(df, analysis_type="overview")
        assert isinstance(report, AIReport)
        assert report.model_used == "rule-based"

    def test_dataframe_no_numeric(self, service):
        """Test with dataframe that has no numeric columns."""
        df = pd.DataFrame({"name": ["A", "B"], "city": ["HN", "HCM"]})
        report = service.generate_report(df, analysis_type="overview")
        assert isinstance(report, AIReport)

    def test_insight_types(self, service, sample_df):
        """Test that insights have correct types."""
        report = service.generate_report(sample_df, analysis_type="overview")
        for insight in report.ai_insights:
            assert isinstance(insight, AIInsight)
            assert insight.type in ("success", "info", "warning", "danger")
            assert isinstance(insight.icon, str)
            assert isinstance(insight.title, str)
            assert isinstance(insight.message, str)

    def test_missing_score_column(self, service, sample_df):
        """Test learning report with non-existent score column."""
        report = service.generate_report(
            sample_df, analysis_type="learning",
            score_col="nonexistent"
        )
        assert isinstance(report, AIReport)

    def test_recommendations_not_empty(self, service, sample_df):
        """Test that recommendations are generated."""
        report = service.generate_report(sample_df, analysis_type="overview")
        assert len(report.recommendations) > 0
        for rec in report.recommendations:
            assert isinstance(rec, str)
            assert len(rec) > 0


class TestAIServiceEdgeCases:
    """Tests for edge cases in AI service."""

    def test_single_row_dataframe(self):
        """Test with single row dataframe."""
        service = AIService(api_key="")
        df = pd.DataFrame({"x": [1.0], "y": [2.0]})
        report = service.generate_report(df, analysis_type="overview")
        assert isinstance(report, AIReport)

    def test_dataframe_with_duplicates(self):
        """Test with dataframe containing many duplicates."""
        service = AIService(api_key="")
        df = pd.DataFrame({
            "score": [5.0] * 50 + [8.0] * 50,
            "class": ["A"] * 50 + ["B"] * 50,
        })
        report = service.generate_report(df, analysis_type="learning", score_col="score")
        assert isinstance(report, AIReport)
        # Should have a warning about duplicate-like data

    def test_prompt_building(self):
        """Test that prompt is built correctly."""
        service = AIService(api_key="")
        df = pd.DataFrame({
            "num_col": [1.0, 2.0, 3.0],
            "cat_col": ["a", "b", "c"],
        })
        prompt = service._build_prompt(df, "overview")
        assert "Rows: 3" in prompt
        assert "num_col" in prompt
        assert "cat_col" in prompt
        assert "Missing values" in prompt

    def test_prompt_with_learning(self):
        """Test learning-specific prompt content."""
        service = AIService(api_key="")
        df = pd.DataFrame({
            "score": [7.0, 6.0, 4.0, 8.0, 5.0],
            "class": ["A", "A", "B", "B", "A"],
        })
        prompt = service._build_prompt(df, "learning", score_col="score", group_col="class")
        assert "Pass rate" in prompt
        assert "Risk rate" in prompt
        assert "Group analysis" in prompt