"""
Re-export all constants from src.utils.config for backward compatibility.

New code should import directly from src.utils.config instead of this module.
This file exists only to support legacy imports like ``from config import MAIN_TABS``.
TODO: Remove this file once all imports are migrated to ``src.utils.config``.
"""
import logging
logger = logging.getLogger(__name__)

try:
    from src.utils.config import *  # noqa: F401, F403
except ImportError as exc:
    logger.error("Failed to import from src.utils.config: %s", exc)
    # ── Fallback constants ──
    MIN_ROWS_VALIDATION = 10
    MIN_COLS_VALIDATION = 1
    TOP_N_VALUES = 10
    TOP_N_CATEGORIES = 10
    TOP_N_DISTRIBUTION = 15
    SPARKLINE_SAMPLE_SIZE = 200
    DATA_PREVIEW_ROWS = 20
    MAX_DISPLAY_ROWS = 100
    TAB_OVERVIEW = "📊 Overview"
    TAB_LEARNING_ANALYTICS = "🎓 Learning Analytics"
    TAB_STATISTICS = "📈 Statistics"
    TAB_COMPARE = "⚖️ Compare"
    TAB_ANALYTICS = "🔬 Analytics"
    TAB_AI_INSIGHTS = "🤖 AI Insights"
    TAB_DEEP_ANALYSIS = "🧠 Deep Analysis"
    MAIN_TABS = [TAB_OVERVIEW, TAB_LEARNING_ANALYTICS, TAB_STATISTICS,
                  TAB_COMPARE, TAB_ANALYTICS, TAB_AI_INSIGHTS, TAB_DEEP_ANALYSIS]
    logger.warning("Using fallback constants (src.utils.config not available)")