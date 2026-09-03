"""Briefer prompt (Plan 02)."""

SYSTEM = "Bạn là trợ lý phân tích dữ liệu. Dựa vào profile JSON, viết brief tiếng Việt ngắn gọn."


def build_prompt(profile: dict) -> list[dict]:
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": f"profile:\n{profile}\n→ brief:"}]
