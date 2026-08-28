"""Session state management service"""
import logging
import os
import pickle
from datetime import datetime
from typing import Optional, Dict, Any
import pandas as pd

import streamlit as st

logger = logging.getLogger(__name__)

SESSION_FILE = "saved_session.pkl"

def save_session_state() -> tuple[bool, str]:
    """Save current session state to pickle file"""
    try:
        session_data = {
            "df": st.session_state.get("df"),
            "cleaned_df": st.session_state.get("cleaned_df"),
            "filename": st.session_state.get("filename", ""),
            "saved_at": datetime.now().isoformat(),
        }
        with open(SESSION_FILE, "wb") as f:
            pickle.dump(session_data, f)
        return True, f"✅ Session saved at {datetime.now():%H:%M:%S}"
    except (IOError, pickle.PickleError) as e:
        logger.error("Session save failed: %s", e, exc_info=True)
        return False, f"❌ Save failed: {str(e)}"
    except Exception as e:
        logger.error("Unexpected session save error: %s", e, exc_info=True)
        return False, f"❌ Save failed: unexpected error"

def load_session_state() -> tuple[bool, str]:
    """Load session state from pickle file"""
    try:
        if not os.path.exists(SESSION_FILE):
            return False, "❌ No saved session found"
        with open(SESSION_FILE, "rb") as f:
            session_data = pickle.load(f)

        if session_data.get("df") is not None:
            st.session_state.df = session_data["df"]
        if session_data.get("cleaned_df") is not None:
            st.session_state.cleaned_df = session_data["cleaned_df"]
        if session_data.get("filename"):
            st.session_state.filename = session_data["filename"]

        saved_at = session_data.get("saved_at", "unknown")
        return True, f"✅ Session loaded (saved: {saved_at})"
    except (IOError, pickle.PickleError) as e:
        logger.error("Session load failed: %s", e, exc_info=True)
        return False, f"❌ Load failed: {str(e)}"
    except Exception as e:
        logger.error("Unexpected session load error: %s", e, exc_info=True)
        return False, f"❌ Load failed: unexpected error"

def has_saved_session() -> bool:
    """Check if a saved session exists"""
    return os.path.exists(SESSION_FILE)

def get_session_info() -> Optional[Dict[str, Any]]:
    """Get info about saved session"""
    if not has_saved_session():
        return None
    try:
        with open(SESSION_FILE, "rb") as f:
            data = pickle.load(f)
        return {
            "saved_at": data.get("saved_at", "unknown"),
            "filename": data.get("filename", "unknown"),
            "rows": len(data.get("df", [])),
            "cols": len(data.get("df", pd.DataFrame()).columns) if data.get("df") is not None else 0,
        }
    except (IOError, pickle.PickleError, KeyError) as e:
        logger.warning("Session info read failed: %s", e)
        return None
    except Exception as e:
        logger.error("Unexpected session info error: %s", e, exc_info=True)
        return None
