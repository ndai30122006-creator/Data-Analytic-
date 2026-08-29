"""
🎨 Theme V2 — Deprecated alias (Pro Max Data-Dense)
Keeps API compatibility; delegates to src.ui.theme (Pro Max).
"""
from src.ui.theme import (
    COLORS,
    get_light_mode_css,
    get_dark_mode_css,
    metric_card,
    status_badge,
    gradient_text,
    render_theme,
    get_theme_colors,
    render_theme_switcher,
    debug_theme_config,
    icon,
)

__all__ = [
    "COLORS", "get_light_mode_css", "get_dark_mode_css",
    "metric_card", "status_badge", "gradient_text",
    "render_theme", "get_theme_colors", "render_theme_switcher",
    "debug_theme_config", "icon",
]
