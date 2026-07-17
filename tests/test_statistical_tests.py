"""Unit tests for src/core/statistical_tests.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pandas as pd
import numpy as np

from src.core.statistical_tests import (
    run_ttest_independent,
    run_ttest_onesample,
    run_ttest_paired,
    run_anova,
    run_chisquare,
    run_mannwhitney,
    run_kruskal,
    run_bootstrap,
    run_two_proportion_ztest,
    calculate_sample_size,
    compute_regression_metrics,
)


class TestTTest:
    """Tests for t-test functions."""

    def test_ttest_independent(self, sample_df):
        """Test independent t-test between two groups."""
        m_scores = sample_df[sample_df["gender"] == "M"]["score"].values
        f_scores = sample_df[sample_df["gender"] == "F"]["score"].values
        result = run_ttest_independent(m_scores, f_scores)
        assert "statistic" in result
        assert "p_value" in result
        assert "cohens_d" in result
        assert "significant" in result
        assert isinstance(result["statistic"], float)
        assert isinstance(result["p_value"], float)
        assert 0 <= result["p_value"] <= 1

    def test_ttest_onesample(self, sample_df):
        """Test one-sample t-test."""
        scores = sample_df["score"].values
        result = run_ttest_onesample(scores, 5.0)
        assert "statistic" in result
        assert "p_value" in result
        assert "significant" in result

    def test_ttest_paired(self, sample_df):
        """Test paired t-test."""
        before = sample_df["score"].values[:50]
        after = sample_df["score"].values[50:100]
        result = run_ttest_paired(before, after)
        assert "statistic" in result
        assert "p_value" in result
        assert "significant" in result

    def test_ttest_identical_groups(self):
        """Test t-test with identical groups."""
        data = np.ones(50) * 5.0
        result = run_ttest_independent(data, data)
        # With identical data, p_value may be NaN due to precision loss
        # but cohens_d should be 0
        assert result["cohens_d"] == 0.0


class TestANOVA:
    """Tests for ANOVA."""

    def test_basic_anova(self, sample_df):
        """Test basic one-way ANOVA."""
        groups = [
            sample_df[sample_df["department"] == d]["score"].values
            for d in sample_df["department"].unique()
        ]
        result = run_anova(*groups)
        assert "statistic" in result
        assert "p_value" in result
        assert "eta_squared" in result
        assert isinstance(result["statistic"], float)
        assert isinstance(result["p_value"], float)

    def test_anova_two_groups(self, sample_df):
        """Test ANOVA with two groups."""
        m_scores = sample_df[sample_df["gender"] == "M"]["score"].values
        f_scores = sample_df[sample_df["gender"] == "F"]["score"].values
        result = run_anova(m_scores, f_scores)
        assert "statistic" in result
        assert "p_value" in result


class TestChiSquare:
    """Tests for chi-square test."""

    def test_basic_chi_square(self, sample_df):
        """Test basic chi-square test of independence."""
        contingency = pd.crosstab(sample_df["grade"], sample_df["department"])
        result = run_chisquare(contingency)
        assert "statistic" in result
        assert "p_value" in result
        assert "dof" in result
        assert "cramer_v" in result
        assert isinstance(result["statistic"], float)
        assert isinstance(result["p_value"], float)

    def test_chi_square_expected(self):
        """Test chi-square with known expected values."""
        data = pd.DataFrame({
            "A": [10, 20, 30],
            "B": [15, 25, 35]
        }, index=["X", "Y", "Z"])
        result = run_chisquare(data)
        assert "statistic" in result
        assert "p_value" in result


class TestMannWhitney:
    """Tests for Mann-Whitney U test."""

    def test_basic_mann_whitney(self, sample_df):
        """Test basic Mann-Whitney U test."""
        m_scores = sample_df[sample_df["gender"] == "M"]["score"].values
        f_scores = sample_df[sample_df["gender"] == "F"]["score"].values
        result = run_mannwhitney(m_scores, f_scores)
        assert "statistic" in result
        assert "p_value" in result
        assert "effect_size_r" in result
        assert "significant" in result
        assert isinstance(result["statistic"], float)
        assert isinstance(result["p_value"], float)


class TestKruskal:
    """Tests for Kruskal-Wallis test."""

    def test_basic_kruskal(self, sample_df):
        """Test basic Kruskal-Wallis H test."""
        groups = [
            sample_df[sample_df["department"] == d]["score"].values
            for d in sample_df["department"].unique()
        ]
        result = run_kruskal(*groups)
        assert "statistic" in result
        assert "p_value" in result
        assert "significant" in result
        assert isinstance(result["statistic"], float)
        assert isinstance(result["p_value"], float)


class TestBootstrap:
    """Tests for bootstrap resampling."""

    def test_bootstrap_mean(self, sample_df):
        """Test bootstrap on mean."""
        data = sample_df["score"].values
        result = run_bootstrap(data, n_iter=100, conf_level=95)
        assert "original" in result
        assert "boot_stats" in result
        assert "ci_lower" in result
        assert "ci_upper" in result
        assert "boot_std" in result
        assert abs(result["original"] - data.mean()) < 0.01
        assert result["ci_lower"] < result["ci_upper"]

    def test_bootstrap_median(self, sample_df):
        """Test bootstrap on median."""
        data = sample_df["score"].values
        result = run_bootstrap(data, n_iter=100, stat_func=np.median)
        assert "original" in result
        assert abs(result["original"] - np.median(data)) < 0.01


class TestABTesting:
    """Tests for A/B testing utilities."""

    def test_two_proportion_ztest(self):
        """Test two-proportion Z-test."""
        result = run_two_proportion_ztest(100, 500, 120, 500)
        assert "p1" in result
        assert "p2" in result
        assert "z_stat" in result
        assert "p_value" in result
        assert "cohens_h" in result
        assert 0 <= result["p_value"] <= 1

    def test_two_proportion_equal(self):
        """Test with equal proportions."""
        result = run_two_proportion_ztest(50, 200, 50, 200)
        assert abs(result["z_stat"]) < 0.01
        assert result["p_value"] > 0.9

    def test_calculate_sample_size(self):
        """Test sample size calculation."""
        n = calculate_sample_size(10, 5, alpha=0.05, power=0.8)
        assert isinstance(n, int)
        assert n > 0

    def test_calculate_sample_size_no_effect(self):
        """Test sample size with no effect."""
        n = calculate_sample_size(10, 0, alpha=0.05, power=0.8)
        assert n == 0


class TestRegressionMetrics:
    """Tests for regression metrics."""

    def test_perfect_prediction(self):
        """Test metrics with perfect predictions."""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        result = compute_regression_metrics(y_true, y_pred)
        assert abs(result["r2"] - 1.0) < 0.001
        assert result["mae"] == 0.0
        assert result["rmse"] == 0.0

    def test_worst_prediction(self):
        """Test metrics with constant predictions."""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([3.0, 3.0, 3.0, 3.0, 3.0])
        result = compute_regression_metrics(y_true, y_pred)
        assert result["mae"] > 0
        assert result["rmse"] > 0

    def test_with_nan_values(self):
        """Test metrics with NaN values."""
        y_true = np.array([1.0, 2.0, np.nan, 4.0, 5.0])
        y_pred = np.array([1.0, 2.0, 3.0, np.nan, 5.0])
        result = compute_regression_metrics(y_true, y_pred)
        assert "r2" in result
        assert "mae" in result
        assert "rmse" in result


# ── Edge Cases ──

class TestEdgeCases:
    """Tests for edge cases across all statistical functions."""

    def test_empty_arrays(self):
        """Test with empty arrays (should return NaN results, not crash)."""
        result = run_ttest_independent(np.array([]), np.array([1.0, 2.0]))
        assert "statistic" in result
        assert "p_value" in result

    def test_single_value_arrays(self):
        """Test with single-value arrays (should return results, not crash)."""
        result = run_ttest_independent(np.array([1.0]), np.array([2.0]))
        assert "statistic" in result
        assert "p_value" in result

    def test_all_same_values(self):
        """Test with constant arrays."""
        result = run_ttest_independent(
            np.ones(50) * 5.0,
            np.ones(50) * 5.0
        )
        # With identical data, p_value may be NaN due to precision loss
        assert result["cohens_d"] == 0.0

    def test_bootstrap_small_sample(self):
        """Test bootstrap with very small sample."""
        data = np.array([1.0, 2.0, 3.0])
        result = run_bootstrap(data, n_iter=50)
        assert "original" in result
        assert "ci_lower" in result
        assert "ci_upper" in result