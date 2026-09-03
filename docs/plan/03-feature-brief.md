# 03 — Feature: AI Brief dữ liệu

> Đây là feature **làm trước (P2)** vì đơn giản, tận dụng tối đa code có sẵn,
> và vừa làm vừa có thể dùng được ngay.

## 🎯 Mục đích

1-click tổng kết một dataset đã upload: **dataset này là gì**, **chất lượng
ra sao**, **có vấn đề gì**, **nên làm pipeline gì tiếp theo**.

## ✨ User flow

1. Chọn dataset trong đã ingest (registry).
2. Bấm "Sinh Brief".
3. Hệ thống lấy **profile** (không phải raw data) → gọi AI gateway → trả về
   narrative tiếng Việt.
4. Brief được **lưu theo version** (mỗi lần chạy +1).
5. Export Markdown.

## 🔁 Tận dụng từ repo

| Thành phần | Dùng như thế nào |
|---|---|
| `src/core/insights.py` | Hàm `generate_data_summary()` — nền của profiling → brief |
| `src/core/ai_service.py` | LLM client (OpenAI/Gemini), fallback rule-based |
| Bảng `users.api_key_ai` | BYOK — lấy key riêng của user |
| `src/services/report_service.py` | Export brief dạng Markdown / PDF |

## 🧱 Cần xây mới

- `src/prompts/briefer.py` — prompt xây dựng từ profile JSON.
- `src/warehouse/registry.py` — lưu `profile_json` cho mỗi dataset.
- Migration Alembic: bảng `briefs` (id, dataset_id, version, content,
  model_used, created_at).
- `src/ui/screens/brief_screen.py`.

## 🧾 Ví dụ input (profile) — LLM KHÔNG thấy raw data

```json
{
  "table": "raw.sinhvien_diem",
  "rows": 1200,
  "cols": 8,
  "columns": {
    "ma_sv": {"type": "int", "missing": 0},
    "diem": {"type": "float", "mean": 6.1, "std": 1.9, "min": 1.5, "max": 10.0, "missing": 14},
    "lop": {"type": "string", "categories": 5, "missing": 3}
  },
  "quality_score": 0.87,
  "issues": {"high_missing": ["diem"], "low_cardinality": ["lop"]}
}
```

## ✅ Acceptance criteria

- [ ] Upload dataset → click "Sinh Brief" → hiển thị narrative hợp lý.
- [ ] Không có key AI → fallback rule-based (tái dụng `insights.py`) vẫn chạy.
- [ ] Brief lưu được nhiều version, export Markdown được.
- [ ] LLM chỉ nhận profile, không nhận raw data (verify log).