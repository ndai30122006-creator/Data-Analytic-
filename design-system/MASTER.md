# Learning Analytics — Design System (Pro Max Data-Dense Dashboard)

> Generated: 2026-08-29 | Engine: ui-ux-pro-max v2.13.0 | Target: Learning Analytics Thống kê

## 1. Pattern
**Enterprise Gateway**
- Conversion: Path selection (I am a...) + trust signals, filter sidebar
- CTA: Upload Data (Primary `#1E40AF`) + Export (Secondary `#3B82F6`)
- Sections: Hero (mission) → KPI Bento → Trends → Data Quality → Preview → Export
- A11y: pause media, keyboard operable, reduced-motion static

## 2. Style
**Data-Dense Dashboard** (light + dark supported)
- Keywords: KPI cards, data tables, minimal padding `8px`, grid `12 cols`, space-efficient
- Best For: BI dashboards, financial analytics, operational dashboards
- Cost: low | Risk: low | Requires: contrast 4.5:1, keyboard, visible-focus, reduced-motion
- CSS: `display:grid; grid-template-columns:repeat(12,1fr); gap:8px; padding:12px; font-size:12-14px; sticky headers`
- Variables: `--grid-gap:8px --card-padding:12px --font-size-small:12px --table-row-height:36px --sidebar-width:240px --header-height:56px`

**Supplement:** Bento Box Grid (landing/overview) — `grid 4 cols, gap 12px, radius 16px, shadow subtle`

## 3. Colors (semantic)
| Token | Light | Dark | Var |
|-------|-------|------|-----|
| Primary | `#1E40AF` | `#60A5FA` | `--primary/--ring` |
| On Primary | `#FFFFFF` | `#0B1220` | `--text-inverse` |
| Secondary | `#3B82F6` | `#38BDF8` | `--secondary` |
| Accent/CTA | `#D97706` | `#FBBF24` | `--accent` |
| Background | `#F8FAFC` | `#0B1220` | `--bg-primary` |
| Foreground | `#1E3A8A` | `#F1F5F9` | `--text-primary` |
| Card | `#FFFFFF` | `#111D33` | `--card` |
| Muted | `#E9EEF6` | `#1E2F4A` | `--muted` |
| Border | `#DBEAFE` | `#1E3A5F` | `--border` |
| Destructive | `#DC2626` | `#F87171` | `--destructive` |
| Notes | Blue data + amber highlights (adjusted from `#F59E0B` → `#D97706` for contrast) |

Implementation: `src/ui/theme.py:21` `COLORS`, `src/utils/config.py:74` `CHART_COLORS`, `get_chart_theme()`

## 4. Typography
**Fira Code / Fira Sans** — mood: dashboard, data, technical, precise
- Google Fonts: `https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Fira+Sans:wght@300;400;500;600;700&display=swap`
- CSS: `@import url('...')` + fallback Inter (`--font: 'Fira Sans', Inter, ...`)
- Mono: `Fira Code` for KPI values, tabular-nums (`src/ui/theme.py:58` `_LIGHT_TOKENS`)

## 5. Key Effects
- Hover tooltips (`[data-tooltip]`), chart zoom on click (`transform scale 0.99`), row highlight `var(--bg-hover)`, smooth filter animations `180ms ease-out`, loading spinners `.skeleton shimmer` / `.spinner`

## 6. Avoid (Anti-patterns)
- Ornate design + No filtering + AI purple/pink gradients (`#6366F1`→ replaced by `#1E40AF`)

## 7. UX Guidelines Applied
- Table overflow `overflow-x-auto` wrapper `.dataframe-wrapper` (Web Responsive)
- Chip wrap `flex-wrap gap 6px` + `+n` disclosure, badge not color-only (prefix ●✓⚠✕)
- Cursor-pointer all clickable, transitions 150-300ms, focus-visible `2px var(--ring)`, text reflow `overflow-wrap:break-word`, prefers-reduced-motion disables animation

## 8. Pre-Delivery Checklist
- [ ] No emojis as icons (Lucide SVG via `theme.icon()` / `components._lucide()`)
- [ ] cursor-pointer, transitions 150-300ms
- [ ] contrast 4.5:1 verified (primary `#1E40AF` on `#F8FAFC` = 8.2:1)
- [ ] focus states visible
- [ ] prefers-reduced-motion respected (`@media` in `_ANIM_CSS`)
- [ ] chips/badges reflow, no clipping
- [ ] Responsive 375/768/1024/1440 (`@media` in `_BASE_CSS`)

## 9. Stack
Streamlit: HTML+T Tailwind-equivalent injected via `st.markdown(unsafe_allow_html=True)` (`src/ui/theme.py:413 render_theme()`), `st.session_state.theme_mode` drives light/dark + `set_chart_mode()`

## 10. Files
- Theme: `src/ui/theme.py`, alias `src/ui/theme_v2.py`, components `src/ui/components.py`
- Tabs: `src/ui/tabs/landing.py` (Bento), `overview.py` (Pro Max), `sidebar.py` (filter 240px)
- Config: `src/utils/config.py` (palette + chart), `migrations/002` + critical fixes `helpers.py:12`, `ai_service.py:297`, `api.py:216`
- Branch: `fix/stable-pro-max` (`e841096`), 92 tests passed, preview `http://localhost:8501`

## Hierarchical Retrieval
- Build page: read `design-system/MASTER.md` first; check `design-system/pages/<page>.md` override if exists; otherwise use MASTER.
