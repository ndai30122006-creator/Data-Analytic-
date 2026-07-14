"""Unit tests for src/core/statistical_tests.py"""
import os
import sys
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.statistical_tests import (
    run_ttest_independent,
    run_ttest_onesample,
    run_ttest_paired,
    run_anova,
    run_mannwhitney,
    run_kruskal,
    run_chisquare,
    run_bootstrap,
    run_two_proportion_ztest,
    calculate_sample_size,
    compute_regression_metrics,
    SIGNIFICANCE_LEVEL,
)


class TestHypothesisTests:
    def test_ttest_independent(self):
        np.random.seed(42)
        s1 = np.random.normal(5, 1, 100)
        s2 = np.random.normal(6, 1, 100)
        result = run_ttest_independent(s1, s2)
        assert "statistic" in result
        assert "p_value" in result
        assert "cohens_d" in result
        assert result["significant"] in (True, False, np.True_, np.False_)
        # Should detect difference
        assert result["p_value"] < 0.05

    def test_ttest_onesample(self):
        s = np.random.normal(5.5, 1, 100)
        result = run_ttest_onesample(s, 5.0)
        assert result["p_value"] < 0.05  # mean is different from 5.0

    def test_ttest_paired(self):
        before = np.random.normal(5, 1, 50)
        after = before + np.random.normal(0.5, 0.5, 50)
        result = run_ttest_paired(before, after)
        assert "p_value" in result

    def test_anova(self):
        g1 = np.random.normal(5, 1, 30)
        g2 = np.random.normal(6, 1, 30)
        g3 = np.random.normal(7, 1, 30)
        result = run_anova(g1, g2, g3)
        assert result["p_value"] < 0.05
        assert result["eta_squared"] > 0

    def test_mannwhitney(self):
        s1 = np.random.normal(5, 1, 30)
        s2 = np.random.normal(6, 1, 30)
        result = run_mannwhitney(s1, s2)
        assert "effect_size_r" in result

    def test_kruskal(self):
        g1 = np.random.normal(5, 1, 20)
        g2 = np.random.normal(6, 1, 20)
        result = run_kruskal(g1, g2)
        assert "statistic" in result

    def test_chisquare(self):
        ct = pd.DataFrame([[50, 30], [20, 60]])
        result = run_chisquare(ct)
        assert "cramer_v" in result
        assert result["dof"] == 1


class TestBootstrap:
    def test_bootstrap_basic(self):
        data = np.random.normal(100, 15, 500)
        result = run_bootstrap(data, n_iter=500, conf_level=95)
        assert abs(result["original"] - 100) < 5
        assert result["ci_lower"] < result["original"]
        assert result["ci_upper"] > result["original"]
        assert result["boot_std"] > 0

    def test_bootstrap_median(self):
        data = np.random.exponential(scale=50, size=200)
        result = run_bootstrap(data, n_iter=200, stat_func=np.median)
        assert "ci_lower" in result
        assert "ci_upper" in result


class TestABTesting:
    def test_two_proportion_ztest(self):
        result = run_two_proportion_ztest(50, 200, 60, 200)
        assert 0 <= result["p1"] <= 1
        assert 0 <= result["p2"] <= 1
        assert "z_stat" in result
        assert "cohens_h" in result

    def test_sample_size(self):
        n = calculate_sample_size(10, 5, alpha=0.05, power=0.8)
        assert n > 0
        assert isinstance(n, int)


class TestRegressionMetrics:
    def test_compute_metrics(self):
        y_true = np.array([1, 2, 3, 4, 5])
        y_pred = np.array([1.1, 1.9, 3.2, 3.8, 5.1])
        result = compute_regression_metrics(y_true, y_pred)
        assert result["r2"] > 0.9  # good fit
        assert result["mae"] < 0.5
        assert result["rmse"] > 0