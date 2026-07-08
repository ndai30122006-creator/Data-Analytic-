"""Data Analyst Pro v3.0 — Practical Statistics for Data Scientists Edition"""
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import streamlit as st

# ═══════════════════════════════════
# MUST be the very first st.* call
# ═══════════════════════════════════
try:
    st.set_page_config(
        page_title="Learning Analytics Thống kê", page_icon="🎓",
        layout="wide", initial_sidebar_state="expanded"
    )
except Exception as e:
    logging.error("Page config failed: %s", e, exc_info=True)

import pandas as pd
import numpy as np


# ── Safe module loading helpers ──

def _make_fallback(name: str):
    """Return a no-op callable that logs + shows st.error on invocation."""
    def _fallback(*args, **kwargs):
        st.error(f"⚠️ Module **{name}** failed to load. "
                 f"Check the app logs for details.")
        logger.error("Attempted to use unavailable module: %s", name)
    return _fallback


def _safe_import(module_name: str, attr: str, *,
                 fallback: bool = True):
    """Safely import *attr* from *module_name*.

    Returns (callable, True) on success, or (fallback_callable, False)
    on failure when *fallback* is True.  If *fallback* is False, returns
    (None, False) so the caller can handle the absence explicitly.
    """
    try:
        mod = __import__(module_name, fromlist=[attr])
        fn = getattr(mod, attr)
        logger.info("Loaded %s from %s", attr, module_name)
        return fn, True
    except Exception as exc:
        logger.error("Failed to import %s from %s: %s", attr, module_name, exc,
                      exc_info=True)
        if fallback:
            return _make_fallback(f"{module_name}.{attr}"), False
        return None, False


# ── Safe imports for every render_* function ──
render_theme, _ = _safe_import("theme_config", "render_theme")
render_sidebar, _ = _safe_import("sidebar", "render_sidebar")
render_landing_page, _ = _safe_import("landing", "render_landing_page")
render_overview_tab, _ = _safe_import("overview_tab", "render_overview_tab")
render_learning_analytics_tab, _ = _safe_import(
    "learning_analytics", "render_learning_analytics_tab")
render_statistics_tab, _ = _safe_import(
    "statistics_tab", "render_statistics_tab")
render_compare_tab, _ = _safe_import(
    "compare_datasets", "render_compare_tab")
render_analytics_tab, _ = _safe_import(
    "analytics_tab", "render_analytics_tab")
render_ai_insights_tab, _ = _safe_import(
    "ai_insights", "render_ai_insights_tab")

# Deep analysis – no fallback because we show a different UI in that case
render_deep_analysis_tab, DEEP_ANALYSIS_AVAIL = _safe_import(
    "advanced_analytics", "render_deep_analysis_tab", fallback=False)
if not DEEP_ANALYSIS_AVAIL:
    logger.warning("Advanced analytics module not available")

# ── Safe import for error handler (no automatic fallback) ──
_handle_error, _handle_error_ok = _safe_import(
    "src.utils.exceptions", "handle_error", fallback=False)
if _handle_error_ok:
    handle_error = _handle_error
else:
    # Local fallback so the app never crashes on a missing handler
    def handle_error(exc: Exception, context: str = "",
                     user_message: str = "") -> None:
        """Fallback error handler when src.utils.exceptions.handle_error
        failed to load."""
        logger.error("[%s] %s | Context: %s",
                     type(exc).__name__, exc, context, exc_info=True)
        try:
            import streamlit as st
            st.error(f"❌ {user_message or str(exc)}")
        except Exception:
            pass
    logger.warning("Using local fallback for handle_error")


def main() -> None:
    """Main entry point — initialises session state and renders the UI."""
    # ── Session State Init ──
    SESSION_DEFAULTS = [
        ("df", None), ("filename", ""), ("cleaned_df", None),
        ("file_uploader_key", 0),
        ("datasets", {}), ("compare_datasets", []),
        ("ai_report", None),
    ]
    for key, default in SESSION_DEFAULTS:
        if key not in st.session_state:
            st.session_state[key] = default

    # ── Inject Theme ──
    try:
        render_theme()
    except Exception as exc:
        handle_error(exc, "render_theme()", "Failed to apply theme.")

    # ── Sidebar ──
    try:
        render_sidebar()
    except Exception as exc:
        handle_error(exc, "render_sidebar()", "Sidebar failed to load.")

    # ═══════════════════════════════════
    # MAIN CONTENT
    # ═══════════════════════════════════
    if st.session_state.df is None:
        try:
            render_landing_page()
        except Exception as exc:
            handle_error(exc, "render_landing_page()", "Landing page failed to load.")
    else:
        raw = st.session_state.df
        num = raw.select_dtypes(include=[np.number]).columns.tolist()
        cat = raw.select_dtypes(include=["object", "category"]).columns.tolist()
        dat = raw.select_dtypes(include=["datetime"]).columns.tolist()
        df = st.session_state.cleaned_df if st.session_state.cleaned_df is not None else raw

        try:
            from config import MAIN_TABS, TAB_DEEP_ANALYSIS
        except Exception as exc:
            logger.error("Failed to import MAIN_TABS from config: %s", exc,
                          exc_info=True)
            st.error("⚠️ Configuration error: tab definitions could not be loaded.")
            st.stop()

        # ── Header section before tabs ──
        st.markdown(f"""
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        ">
            <div>
                <h2 style="margin:0;font-size:1.5rem;font-weight:700;">
                    📊 {st.session_state.filename}
                </h2>
                <span style="font-size:0.82rem;color:var(--text-secondary);">
                    {len(df):,} rows · {len(num)} numeric · {len(cat)} categorical
                </span>
            </div>
            <div style="
                background: var(--bg-secondary);
                border: 1px solid var(--border-light);
                border-radius: var(--radius-md);
                padding: 0.4rem 0.8rem;
                font-size:0.82rem;
                color:var(--text-secondary);
            ">
                🎯 {len(MAIN_TABS)} analysis tabs
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Dynamic tab dispatch ──
        # Map each tab name to its renderer (with pre-bound args).
        # If a tab has no entry, a warning is shown instead.
        TAB_RENDERERS = {
            "📊 Overview": lambda: render_overview_tab(df, num, cat),
            "🎓 Learning Analytics": lambda: render_learning_analytics_tab(df, num, cat),
            "📈 Statistics": lambda: render_statistics_tab(df, num, cat),
            "⚖️ Compare": lambda: render_compare_tab(),
            "🔬 Analytics": lambda: render_analytics_tab(df, num, cat),
            "🤖 AI Insights": lambda: render_ai_insights_tab(df, num, cat),
        }

        main_tabs = st.tabs(MAIN_TABS)

        for tab_idx, tab_name in enumerate(MAIN_TABS):
            with main_tabs[tab_idx]:
                try:
                    if tab_name == TAB_DEEP_ANALYSIS:
                        if DEEP_ANALYSIS_AVAIL:
                            render_deep_analysis_tab(df, num, cat, dat)
                        else:
                            st.error("Advanced Analytics module unavailable.")
                            with st.expander("🔧 Install dependencies", expanded=True):
                                st.code("pip install scipy scikit-learn statsmodels matplotlib seaborn")
                                if st.button("🔄 Refresh", key="da_refresh"):
                                    st.rerun()
                    elif tab_name in TAB_RENDERERS:
                        TAB_RENDERERS[tab_name]()
                    else:
                        st.warning(f"⚠️ No renderer registered for tab **{tab_name}**.")
                        logger.warning("Missing renderer for tab: %s", tab_name)
                except Exception as exc:
                    st.error(f"⚠️ An error occurred in the **{tab_name}** tab. "
                             f"Check the logs for details.")
                    logger.error("Renderer for tab %s failed: %s",
                                 tab_name, exc, exc_info=True)

    st.caption("📊 Data Analyst Pro v3.0 — Practical Statistics for Data Scientists, 2nd Ed")


if __name__ == "__main__":
    main()