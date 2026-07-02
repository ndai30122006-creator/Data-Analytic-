"""Data Analyst Pro v3.0 — Practical Statistics for Data Scientists Edition

Main entry point for the Streamlit application.
Handles page configuration, session state management, theme injection,
and tab rendering with comprehensive error handling and validation.
"""
import logging
import sys
from pathlib import Path

# ── Setup Logging ──
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ── Imports ──
import streamlit as st
import pandas as pd
import numpy as np

# ── UI & Core Modules (from src/) ──
try:
    from src.ui.theme import render_theme
    from src.ui.sidebar import render_sidebar
    from src.utils.exceptions import handle_error
    from src.utils.config import MAIN_TABS
    logger.info("✅ Successfully imported src modules")
except ImportError as e:
    logger.error(f"Failed to import src modules: {e}", exc_info=True)
    st.error("❌ Critical error: Cannot load UI modules")
    st.stop()

# ── Tab Components (from root - will migrate to src/ui/tabs/ in future) ──
try:
    from landing import render_landing_page
    from overview_tab import render_overview_tab
    from learning_analytics import render_learning_analytics_tab
    from statistics_tab import render_statistics_tab
    from compare_datasets import render_compare_tab
    from analytics_tab import render_analytics_tab
    from ai_insights import render_ai_insights_tab
    logger.info("✅ Successfully imported tab modules")
except ImportError as e:
    logger.error(f"Failed to import tab modules: {e}", exc_info=True)
    st.error("❌ Critical error: Cannot load tab components")
    st.stop()

# ── Optional Advanced Analytics Module ──
DEEP_ANALYSIS_AVAIL = False
try:
    from advanced_analytics import render_deep_analysis_tab
    DEEP_ANALYSIS_AVAIL = True
    logger.info("✅ Advanced analytics module loaded successfully")
except ImportError as e:
    logger.warning(f"Advanced analytics module not available (optional): {e}")
except Exception as e:
    logger.error(f"Failed to load advanced analytics: {e}", exc_info=True)

# ═══════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

SESSION_DEFAULTS = {
    "df": None,
    "filename": "",
    "cleaned_df": None,
    "file_uploader_key": 0,
    "datasets": {},
    "compare_datasets": [],
    "ai_report": None,
}

for key, default_value in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default_value
        logger.debug(f"Initialized session state: {key} = {default_value}")

# ═══════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

try:
    st.set_page_config(
        page_title="Learning Analytics Thống kê",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    logger.info("✅ Page configuration set successfully")
except Exception as e:
    logger.error(f"Page config failed (non-critical): {e}", exc_info=True)
    st.warning("⚠️ Some UI features may not display correctly. Please refresh the page.")

# ═══════════════════════════════════════════════════════════════════════════
# THEME & SIDEBAR INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

try:
    render_theme()
    logger.debug("✅ Theme rendered successfully")
except Exception as e:
    logger.error(f"Theme rendering failed: {e}", exc_info=True)
    st.warning("⚠️ Theme styling may not load correctly")

try:
    render_sidebar()
    logger.debug("✅ Sidebar rendered successfully")
except Exception as e:
    logger.error(f"Sidebar rendering failed: {e}", exc_info=True)
    handle_error(e, "render_sidebar", "Failed to render sidebar components")

# ═══════════════════════════════════════════════════════════════════════════
# MAIN CONTENT RENDERING
# ═══════════════════════════════════════════════════════════════════════════

def extract_column_types(df: pd.DataFrame) -> tuple:
    """
    Safely extract numeric, categorical, and datetime columns from DataFrame.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Tuple of (numeric_cols, categorical_cols, datetime_cols)
        
    Raises:
        ValueError: If df is None or empty
        TypeError: If df is not a DataFrame
    """
    if df is None:
        raise ValueError("DataFrame is None")
    
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected DataFrame, got {type(df).__name__}")
    
    if df.empty:
        logger.warning("DataFrame is empty - column extraction skipped")
        return [], [], []
    
    num = df.select_dtypes(include=[np.number]).columns.tolist()
    cat = df.select_dtypes(include=["object", "category"]).columns.tolist()
    dat = df.select_dtypes(include=["datetime64", "datetime64[ns]"]).columns.tolist()
    
    logger.info(f"Column extraction complete: {len(num)} numeric, {len(cat)} categorical, {len(dat)} datetime")
    return num, cat, dat


def validate_config() -> bool:
    """
    Validate MAIN_TABS configuration.
    
    Returns:
        True if valid, False otherwise
    """
    if not MAIN_TABS:
        logger.error("MAIN_TABS is empty or None")
        return False
    
    if len(MAIN_TABS) < 7:
        logger.error(f"MAIN_TABS has only {len(MAIN_TABS)} tabs, expected at least 7")
        return False
    
    logger.info(f"✅ MAIN_TABS configuration valid: {len(MAIN_TABS)} tabs")
    return True


def render_tabs(df: pd.DataFrame, num: list, cat: list, dat: list) -> None:
    """
    Render all main tabs with error handling for each tab.
    
    Args:
        df: Working DataFrame
        num: List of numeric column names
        cat: List of categorical column names
        dat: List of datetime column names
    """
    if not validate_config():
        st.error("❌ Tab configuration is invalid. Please check src/utils/config.py")
        logger.error("Tab validation failed")
        return
    
    try:
        main_tabs = st.tabs(MAIN_TABS)
        logger.info(f"Created {len(main_tabs)} tabs successfully")
    except Exception as e:
        logger.error(f"Failed to create tabs: {e}", exc_info=True)
        st.error("❌ Failed to create tabs")
        return
    
    # ── Tab 0: Overview ──
    try:
        with main_tabs[0]:
            render_overview_tab(df, num, cat)
            logger.debug("✅ Overview tab rendered")
    except Exception as e:
        logger.error(f"Overview tab error: {e}", exc_info=True)
        with main_tabs[0]:
            handle_error(e, "render_overview_tab", "Failed to render Overview tab")
    
    # ── Tab 1: Learning Analytics ──
    try:
        with main_tabs[1]:
            render_learning_analytics_tab(df, num, cat)
            logger.debug("✅ Learning Analytics tab rendered")
    except Exception as e:
        logger.error(f"Learning Analytics tab error: {e}", exc_info=True)
        with main_tabs[1]:
            handle_error(e, "render_learning_analytics_tab", "Failed to render Learning Analytics tab")
    
    # ── Tab 2: Statistics ──
    try:
        with main_tabs[2]:
            render_statistics_tab(df, num, cat)
            logger.debug("✅ Statistics tab rendered")
    except Exception as e:
        logger.error(f"Statistics tab error: {e}", exc_info=True)
        with main_tabs[2]:
            handle_error(e, "render_statistics_tab", "Failed to render Statistics tab")
    
    # ── Tab 3: Compare ──
    try:
        with main_tabs[3]:
            render_compare_tab()
            logger.debug("✅ Compare tab rendered")
    except Exception as e:
        logger.error(f"Compare tab error: {e}", exc_info=True)
        with main_tabs[3]:
            handle_error(e, "render_compare_tab", "Failed to render Compare tab")
    
    # ── Tab 4: Analytics ──
    try:
        with main_tabs[4]:
            render_analytics_tab(df, num, cat)
            logger.debug("✅ Analytics tab rendered")
    except Exception as e:
        logger.error(f"Analytics tab error: {e}", exc_info=True)
        with main_tabs[4]:
            handle_error(e, "render_analytics_tab", "Failed to render Analytics tab")
    
    # ── Tab 5: AI Insights ──
    try:
        with main_tabs[5]:
            render_ai_insights_tab(df, num, cat)
            logger.debug("✅ AI Insights tab rendered")
    except Exception as e:
        logger.error(f"AI Insights tab error: {e}", exc_info=True)
        with main_tabs[5]:
            handle_error(e, "render_ai_insights_tab", "Failed to render AI Insights tab")
    
    # ── Tab 6: Deep Analysis ──
    try:
        with main_tabs[6]:
            if DEEP_ANALYSIS_AVAIL:
                render_deep_analysis_tab(df, num, cat, dat)
                logger.debug("✅ Deep Analysis tab rendered")
            else:
                st.info("📦 Advanced Analytics module not installed")
                with st.expander("🔧 Install dependencies", expanded=True):
                    st.write("To enable advanced analytics, install:")
                    st.code("pip install scipy scikit-learn statsmodels matplotlib seaborn")
                    if st.button("🔄 Refresh after installation", key="da_refresh"):
                        logger.info("User clicked refresh after installing dependencies")
                        st.rerun()
    except Exception as e:
        logger.error(f"Deep Analysis tab error: {e}", exc_info=True)
        with main_tabs[6]:
            handle_error(e, "render_deep_analysis_tab", "Failed to render Deep Analysis tab")


# ── Main Content Logic ──
if st.session_state.df is None:
    logger.debug("No data loaded - rendering landing page")
    render_landing_page()

elif st.session_state.df.empty:
    logger.warning("DataFrame is empty")
    st.error("❌ DataFrame is empty. Please upload data from the sidebar.")
    st.stop()

else:
    try:
        logger.info("Starting main content rendering...")
        raw = st.session_state.df
        
        # ── Extract Column Types ──
        try:
            num, cat, dat = extract_column_types(raw)
        except (ValueError, TypeError) as e:
            logger.error(f"Column extraction failed: {e}")
            handle_error(e, "extract_column_types", "Failed to analyze column types")
            st.stop()
        
        # ── Warn if insufficient columns ──
        if not num and not cat:
            logger.warning("No analyzable columns (numeric or categorical) found")
            st.warning("⚠️ No numeric or categorical columns found. Some features may be limited.")
        
        # ── Select working DataFrame ──
        df = st.session_state.cleaned_df if st.session_state.cleaned_df is not None else raw
        logger.debug(f"Working DataFrame shape: {df.shape}")
        
        # ── Render All Tabs ──
        render_tabs(df, num, cat, dat)
        logger.info("✅ All tabs rendered successfully")
    
    except Exception as e:
        logger.error(f"Unexpected error in main content: {e}", exc_info=True)
        handle_error(e, "render_main_content", "An unexpected error occurred while rendering content")
        st.error("💡 Please try refreshing the page or uploading data again")

# ═══════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════

st.divider()
st.caption("📊 Data Analyst Pro v3.0 — Practical Statistics for Data Scientists, 2nd Ed")
