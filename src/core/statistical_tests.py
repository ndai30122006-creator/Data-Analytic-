"""Shared statistical test logic — used by both Statistics tab and Deep Analysis tab.
Separates computation from UI rendering (clean architecture)."""
import logging
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats as scipy_stats

logger = logging.getLogger(__name__)

# ── Constants ──
SIGNIFICANCE_LEVEL = 0.05


# ═══════════════════════════════════════════════════════════════
# HYPOTHESIS TESTING
# ═══════════════════════════════════════════════════════════════

def run_ttest_independent(s1: np.ndarray, s2: np.ndarray) -> Dict[str, Any]:
    """Two-sample independent t-test with Cohen's d."""
    stat, p = scipy_stats.ttest_ind(s1, s2, equal_var=False)
    pooled_std = np.sqrt((s1.std()**2 + s2.std()**2) / 2)
    cohens_d = (s1.mean() - s2.mean()) / pooled_std if pooled_std > 0 else 0
    return {
        "statistic": stat,
        "p_value": p,
        "cohens_d": abs(cohens_d),
        "significant": p < SIGNIFICANCE_LEVEL,
        "test_name": "Independent T-test"
    }


def run_ttest_onesample(s: np.ndarray, mu0: float) -> Dict[str, Any]:
    """One-sample t-test."""
    stat, p = scipy_stats.ttest_1samp(s, mu0)
    return {
        "statistic": stat,
        "p_value": p,
        "significant": p < SIGNIFICANCE_LEVEL,
        "test_name": "One-Sample T-test"
    }


def run_ttest_paired(before: np.ndarray, after: np.ndarray) -> Dict[str, Any]:
    """Paired t-test."""
    stat, p = scipy_stats.ttest_rel(before, after)
    return {
        "statistic": stat,
        "p_value": p,
        "significant": p < SIGNIFICANCE_LEVEL,
        "test_name": "Paired T-test"
    }


def run_anova(*groups: np.ndarray) -> Dict[str, Any]:
    """One-way ANOVA with eta-squared effect size."""
    stat, p = scipy_stats.f_oneway(*groups)
    all_data = np.concatenate(groups)
    ss_between = sum(len(g) * (np.mean(g) - np.mean(all_data))**2 for g in groups)
    ss_total = sum(((g - np.mean(all_data))**2).sum() for g in groups)
    eta_sq = float(ss_between / ss_total) if ss_total > 0 else 0.0
    return {
        "statistic": stat,
        "p_value": p,
        "eta_squared": eta_sq,
        "significant": p < SIGNIFICANCE_LEVEL,
        "test_name": "ANOVA"
    }


def run_mannwhitney(s1: np.ndarray, s2: np.ndarray) -> Dict[str, Any]:
    """Mann-Whitney U test with effect size r."""
    stat, p = scipy_stats.mannwhitneyu(s1, s2, alternative='two-sided')
    n1, n2 = len(s1), len(s2)
    z = (stat - n1*n2/2) / np.sqrt(n1*n2*(n1+n2+1)/12)
    r = abs(z) / np.sqrt(n1 + n2)
    return {
        "statistic": stat,
        "p_value": p,
        "effect_size_r": r,
        "significant": p < SIGNIFICANCE_LEVEL,
        "test_name": "Mann-Whitney U"
    }


def run_kruskal(*groups: np.ndarray) -> Dict[str, Any]:
    """Kruskal-Wallis H-test."""
    stat, p = scipy_stats.kruskal(*groups)
    return {
        "statistic": stat,
        "p_value": p,
        "significant": p < SIGNIFICANCE_LEVEL,
        "test_name": "Kruskal-Wallis"
    }


def run_chisquare(contingency_table: pd.DataFrame) -> Dict[str, Any]:
    """Chi-square test of independence with Cramer's V."""
    stat, p, dof, expected = scipy_stats.chi2_contingency(contingency_table)
    n = contingency_table.sum().sum()
    cramer_v = np.sqrt(stat / (n * min(contingency_table.shape[0]-1, contingency_table.shape[1]-1))) if n > 0 else 0
    return {
        "statistic": stat,
        "p_value": p,
        "dof": dof,
        "cramer_v": cramer_v,
        "significant": p < SIGNIFICANCE_LEVEL,
        "test_name": "Chi-Square"
    }


# ═══════════════════════════════════════════════════════════════
# BOOTSTRAP
# ═══════════════════════════════════════════════════════════════

def run_bootstrap(data: np.ndarray, n_iter: int = 1000, conf_level: int = 95,
                  stat_func=np.mean) -> Dict[str, Any]:
    """Bootstrap resampling for any statistic.
    
    Returns:
        dict with original, boot_means, ci_lower, ci_upper, boot_std
    """
    n = len(data)
    original = stat_func(data)
    # Use a seeded RandomState for reproducibility without affecting global state
    rng = np.random.RandomState(42)
    boot_stats = [stat_func(rng.choice(data, size=n, replace=True)) for _ in range(n_iter)]
    boot_stats = np.array(boot_stats)
    alpha = (100 - conf_level) / 200
    ci_lower = np.percentile(boot_stats, alpha * 100)
    ci_upper = np.percentile(boot_stats, (1 - alpha) * 100)
    return {
        "original": original,
        "boot_stats": boot_stats,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "boot_std": np.std(boot_stats),
        "n_iter": n_iter,
        "conf_level": conf_level
    }


# ═══════════════════════════════════════════════════════════════
# A/B TESTING
# ═══════════════════════════════════════════════════════════════

def run_two_proportion_ztest(successes_a: int, total_a: int,
                              successes_b: int, total_b: int) -> Dict[str, Any]:
    """Two-proportion Z-test."""
    from scipy.stats import norm
    p1, p2 = successes_a/total_a, successes_b/total_b
    p_pool = (successes_a + successes_b) / (total_a + total_b)
    se = np.sqrt(p_pool * (1 - p_pool) * (1/total_a + 1/total_b))
    z = (p1 - p2) / se if se > 0 else 0
    p_val = 2 * (1 - norm.cdf(abs(z)))
    # Cohen's h effect size
    h = 2 * np.arcsin(np.sqrt(p1)) - 2 * np.arcsin(np.sqrt(p2))
    return {
        "p1": p1, "p2": p2,
        "z_stat": z, "p_value": p_val,
        "cohens_h": abs(h),
        "significant": p_val < SIGNIFICANCE_LEVEL
    }


def calculate_sample_size(baseline_pct: float, effect_pct: float,
                          alpha: float = 0.05, power: float = 0.8) -> int:
    """Calculate required sample size per group for A/B test."""
    from scipy.stats import norm
    p1 = baseline_pct / 100
    p2 = (baseline_pct + effect_pct) / 100
    if abs(p2 - p1) < 1e-9:
        return 0
    z_a = norm.ppf(1 - alpha / 2)
    z_b = norm.ppf(power)
    n = ((z_a * np.sqrt(2 * (p1+p2)/2 * (1-(p1+p2)/2)) +
          z_b * np.sqrt(p1*(1-p1) + p2*(1-p2))) ** 2) / ((p2-p1) ** 2)
    return int(np.ceil(n))


# ═══════════════════════════════════════════════════════════════
# REGRESSION METRICS
# ═══════════════════════════════════════════════════════════════

def compute_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Compute R², MAE, RMSE, MAPE."""
    from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
    mask = ~np.isnan(y_true) & ~np.isnan(y_pred)
    y_t, y_p = y_true[mask], y_pred[mask]
    if len(y_t) == 0:
        return {"r2": 0, "mae": 0, "rmse": 0, "mape": 0}
    mape = np.mean(np.abs((y_t - y_p) / (y_t + 1e-10))) * 100
    return {
        "r2": r2_score(y_t, y_p),
        "mae": mean_absolute_error(y_t, y_p),
        "rmse": np.sqrt(mean_squared_error(y_t, y_p)),
        "mape": mape
    }