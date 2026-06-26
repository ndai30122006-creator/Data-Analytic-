"""Configuration constants for Data Analyst Pro v3.0 — Practical Statistics Edition"""
from typing import Dict, Any, List

# ── Validation Constants ────────────────────────────────────
MIN_ROWS_VALIDATION = 10
MIN_COLS_VALIDATION = 1

# ── Data Processing Constants ───────────────────────────────
TOP_N_VALUES = 10
TOP_N_CATEGORIES = 10
TOP_N_DISTRIBUTION = 15
SPARKLINE_SAMPLE_SIZE = 200
DATA_PREVIEW_ROWS = 20
MAX_DISPLAY_ROWS = 100

# ── Model Constants ─────────────────────────────────────────
DEFAULT_TEST_SIZE = 0.2
DEFAULT_CV_FOLDS = 5
RANDOM_STATE = 42

# ── Bootstrap ───────────────────────────────────────────────
BOOTSTRAP_DEFAULT_ITERATIONS = 1000
BOOTSTRAP_DEFAULT_CONFIDENCE = 95

# ── A/B Testing ─────────────────────────────────────────────
AB_DEFAULT_ALPHA = 0.05
AB_DEFAULT_POWER = 0.8
AB_DEFAULT_EFFECT_SIZE = 0.2

# ── AutoML Constants ────────────────────────────────────────
AUTOML_DEFAULT_MODELS = ["Random Forest", "XGBoost"]
AUTOML_DEFAULT_FEATURES = 4
AUTOML_POLYNOMIAL_DEGREE = 2
AUTOML_N_ITER_RANDOMIZED = 10

# ── Hyperparameter Grids ────────────────────────────────────
PARAM_GRIDS = {
    "Random Forest": {
        'model__n_estimators': [50, 100, 200],
        'model__max_depth': [5, 10, None],
        'model__min_samples_split': [2, 5, 10],
        'model__min_samples_leaf': [1, 2, 4]
    },
    "XGBoost": {
        'model__n_estimators': [50, 100, 200],
        'model__max_depth': [3, 6, 10],
        'model__learning_rate': [0.01, 0.05, 0.1],
        'model__subsample': [0.8, 1.0]
    },
    "Gradient Boosting": {
        'model__n_estimators': [50, 100, 200],
        'model__max_depth': [3, 5, 7],
        'model__learning_rate': [0.01, 0.05, 0.1],
        'model__min_samples_split': [2, 5]
    },
    "Ridge": {
        'model__alpha': [0.01, 0.1, 1.0, 10.0, 100.0],
        'model__solver': ['auto', 'svd', 'cholesky']
    },
    "Lasso": {
        'model__alpha': [0.001, 0.01, 0.1, 1.0, 10.0],
        'model__selection': ['cyclic', 'random']
    },
    "Logistic Regression": {
        'model__C': [0.01, 0.1, 1.0, 10.0, 100.0],
        'model__solver': ['lbfgs', 'liblinear'],
        'model__max_iter': [100, 200, 500]
    }
}

# ── Chart Theme ─────────────────────────────────────────────
CHART_THEME: Dict[str, Any] = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family="Inter, -apple-system, sans-serif", size=13, color="#e2e8f0"),
    title=dict(font=dict(size=16, color="#f1f5f9"), x=0.5, xanchor='center'),
    xaxis=dict(gridcolor='rgba(255,255,255,0.06)', zerolinecolor='rgba(255,255,255,0.1)'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.06)', zerolinecolor='rgba(255,255,255,0.1)'),
    hoverlabel=dict(bgcolor="#1e293b", font_size=12, font_family="Inter"),
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(font=dict(size=12), bgcolor='rgba(0,0,0,0)'),
    colorway=['#818cf8', '#34d399', '#fbbf24', '#f87171', '#38bdf8', '#a78bfa']
)

# ── UI Constants ────────────────────────────────────────────
SPARKLINE_HEIGHT = 40
SPARKLINE_COLOR = '#5b6bf7'
KPI_COLUMNS = 4

# ── Session State Keys ──────────────────────────────────────
SESSION_KEYS = {
    "df": None,
    "cleaned_df": None,
}

# ── Tab Names ───────────────────────────────────────────────
TAB_OVERVIEW = "📊 Overview"
TAB_LEARNING_ANALYTICS = "🎓 Learning Analytics"
TAB_STATISTICS = "📈 Statistics"
TAB_COMPARE = "⚖️ Compare"
TAB_ANALYTICS = "🔬 Analytics"
TAB_AI_INSIGHTS = "🤖 AI Insights"
TAB_DEEP_ANALYSIS = "🧠 Deep Analysis"

MAIN_TABS: List[str] = [TAB_OVERVIEW, TAB_LEARNING_ANALYTICS, TAB_STATISTICS, TAB_COMPARE, TAB_ANALYTICS, TAB_AI_INSIGHTS, TAB_DEEP_ANALYSIS]

# ── Statistics Sub-tabs ─────────────────────────────────────
STATS_TAB_HYPOTHESIS = "🔬 Hypothesis Testing"
STATS_TAB_BOOTSTRAP = "🎲 Bootstrap"
STATS_TAB_ABTESTING = "⚗️ A/B Testing"
STATS_TAB_REGRESSION = "📈 Regression"
STATS_TAB_LOGISTIC = "🔴 Logistic"
STATS_TAB_NAIVEBAYES = "🧮 Naive Bayes"
STATS_TAB_DIAGNOSTICS = "🔧 Diagnostics"

STATISTICS_TABS: List[str] = [
    STATS_TAB_HYPOTHESIS, STATS_TAB_BOOTSTRAP, STATS_TAB_ABTESTING,
    STATS_TAB_REGRESSION, STATS_TAB_LOGISTIC, STATS_TAB_NAIVEBAYES, STATS_TAB_DIAGNOSTICS
]

# ── Analytics Sub-tabs ──────────────────────────────────────
ANALYTICS_TAB_ANOMALY = "🔍 Anomaly"
ANALYTICS_TAB_PROFILING = "📊 Profiling"
ANALYTICS_TAB_CLEANING = "🧹 Cleaning"
ANALYTICS_TAB_CLASSIFICATION = "🎯 Classification"

ANALYTICS_TABS: List[str] = [ANALYTICS_TAB_ANOMALY, ANALYTICS_TAB_PROFILING, ANALYTICS_TAB_CLEANING, ANALYTICS_TAB_CLASSIFICATION]

# ── Profiler Sub-tabs ───────────────────────────────────────
PROFILER_TAB_COLUMNS = "📋 Columns"
PROFILER_TAB_DISTRIBUTIONS = "📊 Distributions"
PROFILER_TAB_CORRELATIONS = "🔗 Correlations"

PROFILER_TABS: List[str] = [PROFILER_TAB_COLUMNS, PROFILER_TAB_DISTRIBUTIONS, PROFILER_TAB_CORRELATIONS]

# ── Data Quality Thresholds ─────────────────────────────────
QUALITY_THRESHOLD_GOOD = 80
QUALITY_THRESHOLD_WARNING = 60

# ── Color Scheme ────────────────────────────────────────────
COLOR_SUCCESS = "#22c55e"
COLOR_WARNING = "#eab308"
COLOR_DANGER = "#ef4444"
COLOR_ACCENT = "#5b6bf7"
COLOR_PRIMARY = "#818cf8"
COLOR_SECONDARY = "#34d399"
