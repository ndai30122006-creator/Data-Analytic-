"""Configuration constants for Data Analyst Pro"""
from typing import Dict, Any

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
DEFAULT_CV_FOLDS = 3
DEFAULT_CONTAMINATION = 0.05
DEFAULT_FORECAST_DAYS = 90
RANDOM_STATE = 42

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
    }
}

# ── Model Constructors ──────────────────────────────────────
MODEL_CONSTRUCTORS = {
    "Random Forest": "RandomForestRegressor",
    "XGBoost": "XGBRegressor",
    "Gradient Boosting": "GradientBoostingRegressor",
    "Ridge": "Ridge",
    "Lasso": "Lasso"
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

# ── Database Defaults ───────────────────────────────────────
DEFAULT_DB_HOST = "localhost"
DEFAULT_DB_PORT_MYSQL = "3306"
DEFAULT_DB_PORT_POSTGRES = "5432"
DEFAULT_DB_PATH = "database.db"

# ── AI Chat Constants ───────────────────────────────────────
GEMINI_MODEL = 'gemini-2.0-flash'
AI_CHAT_INPUT_PLACEHOLDER = "💬 Ask about your data..."
QUICK_PROMPTS = [
    "What are the top trends?",
    "Which column has most outliers?",
    "Show me correlations",
    "Summarize the dataset",
    "What's the best chart for this data?"
]

# ── Prophet Constants ───────────────────────────────────────
PROPHET_YEARLY_SEASONALITY = True
PROPHET_WEEKLY_SEASONALITY = True
PROPHET_DAILY_SEASONALITY = False

# ── Anomaly Detection ───────────────────────────────────────
ANOMALY_CONTAMINATION_RANGE = (0.01, 0.5)
ANOMALY_CONTAMINATION_DEFAULT = 0.05
ANOMALY_CONTAMINATION_STEP = 0.01

# ── What-If Analysis ────────────────────────────────────────
WHATIF_CHANGE_RANGE = (-50, 100)
WHATIF_CHANGE_DEFAULT = 0
WHATIF_CHANGE_STEP = 1

# ── PDF Report ──────────────────────────────────────────────
PDF_TITLE_DEFAULT = "Report — Data"
PDF_MAX_COLUMNS = 15
PDF_TOP_CORRELATIONS = 10

# ── Session State Keys ──────────────────────────────────────
SESSION_KEYS = {
    "df": None,
    "filename": "",
    "cleaned_df": None,
    "genai_chat": [],
    "db_config": {},
    "theme": "dark",
    "genai_key": ""
}

# ── Tab Names ───────────────────────────────────────────────
TAB_OVERVIEW = "📊 Overview"
TAB_AI_ML = "🤖 AI & ML"
TAB_ANALYTICS = "🔬 Analytics"
TAB_DEEP_ANALYSIS = "🧠 Deep Analysis"
TAB_MOLECULE = "⚛️ Molecule"

MAIN_TABS = [TAB_OVERVIEW, TAB_AI_ML, TAB_ANALYTICS, TAB_DEEP_ANALYSIS, TAB_MOLECULE]

# ── AI Chat Sub-tabs ────────────────────────────────────────
AI_TAB_CHAT = "🤖 AI Chat"
AI_TAB_FORECAST = "📈 Forecast"
AI_TAB_AUTOML = "🧠 AutoML"

AI_TABS = [AI_TAB_CHAT, AI_TAB_FORECAST, AI_TAB_AUTOML]

# ── Analytics Sub-tabs ──────────────────────────────────────
ANALYTICS_TAB_ANOMALY = "🔍 Anomaly"
ANALYTICS_TAB_PROFILING = "📊 Profiling"
ANALYTICS_TAB_WHATIF = "🎯 What-If"
ANALYTICS_TAB_PDF = "📱 PDF"
ANALYTICS_TAB_CLEANING = "🧹 Cleaning"

ANALYTICS_TABS = [ANALYTICS_TAB_ANOMALY, ANALYTICS_TAB_PROFILING, ANALYTICS_TAB_WHATIF, ANALYTICS_TAB_PDF, ANALYTICS_TAB_CLEANING]

# ── Profiler Sub-tabs ───────────────────────────────────────
PROFILER_TAB_COLUMNS = "📋 Columns"
PROFILER_TAB_DISTRIBUTIONS = "📊 Distributions"
PROFILER_TAB_CORRELATIONS = "🔗 Correlations"

PROFILER_TABS = [PROFILER_TAB_COLUMNS, PROFILER_TAB_DISTRIBUTIONS, PROFILER_TAB_CORRELATIONS]

# ── File Upload ─────────────────────────────────────────────
SUPPORTED_FILE_TYPES = ["csv", "xlsx", "xls"]
FILE_UPLOADER_LABEL = "CSV / Excel"

# ── Database Types ──────────────────────────────────────────
DB_TYPES = ["MySQL", "PostgreSQL", "SQL Server", "SQLite"]

# ── Theme ───────────────────────────────────────────────────
THEME_DARK = "dark"
THEME_LIGHT = "light"

# ── Export Formats ──────────────────────────────────────────
EXPORT_FORMAT_CSV = "CSV"
EXPORT_FORMAT_EXCEL = "Excel"

# ── AutoML Tuning Methods ───────────────────────────────────
TUNING_GRIDSEARCH = "GridSearch"
TUNING_RANDOMIZEDSEARCH = "RandomizedSearch"
TUNING_NONE = "None"

TUNING_METHODS = [TUNING_GRIDSEARCH, TUNING_RANDOMIZEDSEARCH, TUNING_NONE]

# ── AutoML Models ───────────────────────────────────────────
AUTOML_MODELS = ["Random Forest", "XGBoost", "Gradient Boosting", "Ridge", "Lasso"]

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