"""Advanced analytics engine — canonical re-export for deep analysis (P0).

App should import via src.core.analytics_engine, not src.analytics directly.
"""

import logging

logger = logging.getLogger(__name__)

try:
    from src.analytics.analytics_main import render_deep_analysis_tab

    __all__ = ["render_deep_analysis_tab"]
except Exception as exc:  # broader than ImportError to catch scipy errors
    logger.warning("src.analytics module not available: %s", exc)

    def render_deep_analysis_tab(df, num, cat, dat) -> None:  # type: ignore[no-redef]
        """Placeholder when src.analytics is unavailable."""
        import streamlit as st

        st.error(
            "Advanced Analytics module unavailable. Install: pip install scipy scikit-learn statsmodels matplotlib seaborn"
        )

    __all__ = ["render_deep_analysis_tab"]
