"""Configuration constants for Data Analyst Pro v3.0 — Practical Statistics Edition"""

from typing import Any, Dict, List

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
        "model__n_estimators": [50, 100, 200],
        "model__max_depth": [5, 10, None],
        "model__min_samples_split": [2, 5, 10],
        "model__min_samples_leaf": [1, 2, 4],
    },
    "XGBoost": {
        "model__n_estimators": [50, 100, 200],
        "model__max_depth": [3, 6, 10],
        "model__learning_rate": [0.01, 0.05, 0.1],
        "model__subsample": [0.8, 1.0],
    },
    "Gradient Boosting": {
        "model__n_estimators": [50, 100, 200],
        "model__max_depth": [3, 5, 7],
        "model__learning_rate": [0.01, 0.05, 0.1],
        "model__min_samples_split": [2, 5],
    },
    "Ridge": {"model__alpha": [0.01, 0.1, 1.0, 10.0, 100.0], "model__solver": ["auto", "svd", "cholesky"]},
    "Lasso": {"model__alpha": [0.001, 0.01, 0.1, 1.0, 10.0], "model__selection": ["cyclic", "random"]},
    "Logistic Regression": {
        "model__C": [0.01, 0.1, 1.0, 10.0, 100.0],
        "model__solver": ["lbfgs", "liblinear"],
        "model__max_iter": [100, 200, 500],
    },
}

# ── Chart Theme ─────────────────────────────────────────────
# Pro Max Data-Dense: Fira Sans + blue/amber palette — 4.5:1 contrast
FONT_FAMILY = "'Fira Sans', 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif"

# Light-mode chart theme — Pro Max blue data (#1E40AF) + amber (#D97706) highlights
CHART_THEME_LIGHT: Dict[str, Any] = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family=FONT_FAMILY, size=12, color="#475569"),
    title=dict(font=dict(size=15, color="#1E3A8A"), x=0.5, xanchor="center"),
    xaxis=dict(gridcolor="rgba(30,64,175,0.08)", zerolinecolor="rgba(30,64,175,0.12)"),
    yaxis=dict(gridcolor="rgba(30,64,175,0.08)", zerolinecolor="rgba(30,64,175,0.12)"),
    hoverlabel=dict(bgcolor="#FFFFFF", font_size=11, font_family="Fira Sans"),
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
    colorway=["#1E40AF", "#3B82F6", "#D97706", "#059669", "#0284C7", "#DC2626", "#7C3AED"],
)

# Dark-mode chart theme — Pro Max dark (light blue / amber)
CHART_THEME_DARK: Dict[str, Any] = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family=FONT_FAMILY, size=12, color="#CBD5E1"),
    title=dict(font=dict(size=15, color="#F1F5F9"), x=0.5, xanchor="center"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)"),
    hoverlabel=dict(bgcolor="#111D33", font_size=11, font_family="Fira Sans"),
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
    colorway=["#60A5FA", "#38BDF8", "#FBBF24", "#34D399", "#22D3EE", "#F87171", "#A78BFA"],
)

# Back-compat alias (dark theme was the only theme before mode-aware charts).
CHART_THEME: Dict[str, Any] = CHART_THEME_DARK

# Currently active chart mode ("light" | "dark"). Set by src.ui.theme.render_theme().
_CHART_MODE: str = "light"


def set_chart_mode(mode: str) -> None:
    """Set the active chart theme mode ("light" or "dark")."""
    global _CHART_MODE
    _CHART_MODE = "dark" if str(mode).lower() in ("dark", "prod") else "light"


def get_chart_mode() -> str:
    """Return the active chart theme mode."""
    return _CHART_MODE


def get_chart_theme(mode: str | None = None) -> Dict[str, Any]:
    """Return the chart theme dict for the given mode (or the active one)."""
    if mode is None:
        mode = _CHART_MODE
    return CHART_THEME_DARK if str(mode).lower() == "dark" else CHART_THEME_LIGHT


# ── Shared Chart Colors (Pro Max: blue data + amber) ───────
CHART_COLORS: Dict[str, str] = {
    "primary": "#1E40AF",
    "primary_alt": "#3B82F6",
    "secondary": "#3B82F6",
    "accent": "#D97706",
    "success": "#059669",
    "warning": "#D97706",
    "danger": "#DC2626",
    "info": "#0284C7",
}

# ── UI Constants ────────────────────────────────────────────
SPARKLINE_HEIGHT = 40
SPARKLINE_COLOR = "#5b6bf7"
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

MAIN_TABS: List[str] = [
    TAB_OVERVIEW,
    TAB_LEARNING_ANALYTICS,
    TAB_STATISTICS,
    TAB_COMPARE,
    TAB_ANALYTICS,
    TAB_AI_INSIGHTS,
    TAB_DEEP_ANALYSIS,
]

# ── Statistics Sub-tabs ─────────────────────────────────────
STATS_TAB_HYPOTHESIS = "🔬 Hypothesis Testing"
STATS_TAB_REGRESSION = "📈 Regression"

STATISTICS_TABS: List[str] = [STATS_TAB_HYPOTHESIS, STATS_TAB_REGRESSION]

# ── Analytics Sub-tabs ──────────────────────────────────────
ANALYTICS_TAB_ANOMALY = "🔍 Anomaly"
ANALYTICS_TAB_PROFILING = "📊 Profiling"
ANALYTICS_TAB_CLEANING = "🧹 Cleaning"
ANALYTICS_TAB_CLASSIFICATION = "🎯 Classification"

ANALYTICS_TABS: List[str] = [
    ANALYTICS_TAB_ANOMALY,
    ANALYTICS_TAB_PROFILING,
    ANALYTICS_TAB_CLEANING,
    ANALYTICS_TAB_CLASSIFICATION,
]

# ── Profiler Sub-tabs ───────────────────────────────────────
PROFILER_TAB_COLUMNS = "📋 Columns"
PROFILER_TAB_DISTRIBUTIONS = "📊 Distributions"
PROFILER_TAB_CORRELATIONS = "🔗 Correlations"

PROFILER_TABS: List[str] = [PROFILER_TAB_COLUMNS, PROFILER_TAB_DISTRIBUTIONS, PROFILER_TAB_CORRELATIONS]

# ── Data Quality Thresholds ─────────────────────────────────
QUALITY_THRESHOLD_GOOD = 80
QUALITY_THRESHOLD_WARNING = 60

# ── Error / Info Message Constants ──────────────────────────
ERROR_INVALID_DATAFRAME = "❌ {msg}"
ERROR_NO_NUMERIC_COLS = "Need numeric columns"
ERROR_NO_CATEGORICAL_COLS = "Need categorical columns"
ERROR_EMPTY_DATAFRAME = "❌ DataFrame is empty"
ERROR_WORK_DF_NONE = "❌ Work DF is None"

# ── Performance & Security Limits ──────────────────────────
MAX_FILE_SIZE_MB = 50  # Max file upload size (megabytes)
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_ROWS_UPLOAD = 500_000  # Max rows before warning
MAX_COLS_UPLOAD = 200  # Max columns before warning
N_JOBS_MAX = 4  # Cap for n_jobs to avoid resource exhaustion
N_JOBS_DEFAULT = -1  # Will be clamped to N_JOBS_MAX at runtime
UPLOAD_TIMEOUT_SECONDS = 300  # Upload timeout

# ── Sample Limits for Heavy Algorithms ────────────────────
MAX_BOOTSTRAP_SAMPLES = 5000  # Max rows for bootstrap resampling
MAX_ML_SAMPLES = 5000  # Max rows for ML models (AutoML, Model Comparison)
MAX_CLUSTERING_SAMPLES = 5000  # Max rows for clustering
SAMPLING_STRATEGY = "random"  # "random" or "head" — how to subsample

# ── Feature Flags (reduce feature overload) ─────────────────
FEATURE_FLAGS = {
    "show_landing_page": True,  # Landing page hero
    "show_smart_search": True,  # Ctrl+K search bar
    "show_deep_analysis": True,  # Deep Analysis tab (11 subtabs)
    "show_compare_tab": True,  # Compare datasets tab
    "show_ai_insights": True,  # AI Insights tab
}

# ── Color Scheme (Pro Max Data-Dense) ───────────────────────
COLOR_SUCCESS = "#059669"
COLOR_WARNING = "#D97706"
COLOR_DANGER = "#DC2626"
COLOR_ACCENT = "#D97706"
COLOR_PRIMARY = "#1E40AF"
COLOR_SECONDARY = "#3B82F6"
