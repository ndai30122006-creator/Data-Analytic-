# 🎨 UI Plan — Node.js UI Layer

> **Nhánh:** `refactor` · **Trạng thái:** đang ở giai đoạn **brainstorm**.

## Mục tiêu
Thay thế dần Streamlit bằng một bộ UI riêng trên **Node.js**, chia **2 client**:
- **Web/Desktop** — React + Vite, full features, layout rộng.
- **Mobile** — PWA responsive (đề xuất bắt đầu), read-first.

UI Node chỉ gọi FastAPI `api.py` qua REST (JWT + BYOK), **không** chạm trực tiếp
DuckDB/engine — giữ kiến trúc hiện tại không đổi.

## 📄 Tài liệu
- [`brainstorm.md`](./brainstorm.md) — đang mở hướng, câu hỏi chờ chốt.

## ✅ Việc kế tiếp
Chốt các câu hỏi trong [§7 brainstorm](./brainstorm.md#7-câu-hỏi-chốt-cần-trả-lời-trước-khi-chi-tiết-hoá)
rồi viết plan chi tiết (kiến trúc + roadmap).