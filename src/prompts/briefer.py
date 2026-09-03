"""Briefer prompt — profile JSON -> narrative (Plan 03)."""

SYSTEM = (
    "Bạn là trợ lý phân tích dữ liệu. Dựa vào profile JSON (KHÔNG có raw data), "
    "viết brief tiếng Việt ngắn gọn: 1) dataset là gì, 2) chất lượng & vấn đề, 3) đề xuất pipeline tiếp theo."
)


def build_prompt(profile: dict) -> list[dict]:
    import json

    pj = json.dumps(profile, ensure_ascii=False, indent=2)[:8000]  # guard token
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"profile:\n{pj}\n→ brief (Markdown, tiếng Việt):"},
    ]


def generate_brief_fallback(profile: dict) -> str:
    """Rule-based fallback dùng core/insights (không tốn token)."""
    from src.core.insights import generate_data_summary

    # profile may contain summary already; fallback to simple narrative
    try:
        # If profile has rows/cols, craft brief
        rows = profile.get("rows", "?")
        cols = profile.get("cols", "?")
        return f"Dataset {rows} dòng, {cols} cột. Chất lượng: {profile.get('quality_score', 'N/A')}. Vấn đề: {profile.get('issues', {})}. Đề xuất: kiểm tra missing/duplicate trước khi pipeline."
    except Exception:
        return "Brief rule-based: dataset cần làm sạch missing/duplicate, kiểm tra phân phối trước ETL."
