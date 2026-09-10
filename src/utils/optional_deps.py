"""Optional UI deps (streamlit/plotly) — guarded import.

Backend (FastAPI + React) khong can streamlit/plotly; cac module legacy
(src/analytics/*, helpers, validators) van import de tai su dung logic.
De nghiem ngat: import that bai -> None + decorator no-op, chi fail khi
duong legacy UI that su duoc goi (khong xay ra o backend).
"""

try:
    import streamlit as st
except Exception:
    st = None  # type: ignore[assignment]

try:
    import plotly.express as px
except Exception:
    px = None  # type: ignore[assignment]

try:
    import plotly.graph_objects as go
except Exception:
    go = None  # type: ignore[assignment]

try:
    from plotly.subplots import make_subplots
except Exception:

    def make_subplots(*args, **kwargs):  # type: ignore[no-redef]
        raise ImportError("plotly is not installed")


def cache_data(*dargs, **dkwargs):
    """Thay @st.cache_data — ho tro ca dang bare (@cache_data) va goi (@cache_data(...))."""
    if st is not None and hasattr(st, "cache_data"):
        if dargs and callable(dargs[0]) and len(dargs) == 1 and not dkwargs:
            return st.cache_data(dargs[0])
        return st.cache_data(*dargs, **dkwargs)

    def _deco(fn):
        return fn

    if dargs and callable(dargs[0]) and len(dargs) == 1 and not dkwargs:
        return dargs[0]
    return _deco
