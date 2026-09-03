# 🎨 UI Plan — Node.js UI Layer

> **Nhánh:** `refactor` · **Trạng thái:** đang ở giai đoạn **brainstorm**.

## ✅ Quyết định đã chốt
- **Giữ 1 repo** (monorepo, cấu trúc `ui/`).
- **Kiến trúc modular frontend trước**: `core` (dùng chung) + `features`
  (mỗi feature 1 module độc lập) + `web`/`mobile` (lớp lắp ghép mỏng). Chi tiết §2.5 brainstorm.

## Mục tiêu
Thay thế dần Streamlit bằng một bộ UI riêng trên **Node.js**, chia **2 client**:
- **Web/Desktop** — full features, layout rộng.
- **Mobile** — read-first (Brief + Dashboard + Lineage).

UI Node chỉ gọi FastAPI `api.py` qua REST (JWT + BYOK), **không** chạm trực tiếp
DuckDB/engine — giữ kiến trúc hiện tại không đổi.

## 📄 Tài liệu
- [`brainstorm.md`](./brainstorm.md) — hướng đã mở + quyết định đã chốt + câu hỏi còn mở.

## ✅ Việc kế tiếp
Chốt các câu hỏi còn mở trong [§7 brainstorm](./brainstorm.md#7-câu-hỏi-chốt-cần-trả-lời-trước-khi-chi-tiết-hoá)
rồi viết plan chi tiết (kiến trúc + roadmap).