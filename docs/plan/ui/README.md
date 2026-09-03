# 🎨 UI Plan — Node.js UI Layer

> **Nhánh:** `refactor` · **Trạng thái:** đang ở giai đoạn **brainstorm**.

## ✅ Quyết định đã chốt
- **Giữ 1 repo** (monorepo, folder lớn `frontend/` ngay root).
- **2 folder UI riêng**: `frontend/web` (web/desktop) + `frontend/mobile` (web trên điện thoại) —
  **không build chung**, mỗi cái tối ưu giao diện riêng.
- **Không làm app mobile** — mobile chỉ là **web UI trên điện thoại** (responsive/PWA).
- **Chia sẻ logic** qua `frontend/shared` (api + features + hooks) — dùng chung giữa 2 UI.
- **Framework**: **React + Vite** cho cả `web` & `mobile`.
- **Kiến trúc modular frontend trước**: `shared/features` (mỗi feature 1 module) + 2 UI lắp ghép mỏng.

## Mục tiêu
Thay thế dần Streamlit bằng một bộ UI Node.js, chia **2 folder**:
- **`web/`** — web/desktop, full features, layout rộng (sidebar, bảng lớn).
- **`mobile/`** — web trên điện thoại, bottom-nav, card dọc, touch-first, read-first.

Cả 2 chỉ gọi FastAPI `api.py` qua REST (JWT + BYOK), **không** chạm trực tiếp
DuckDB/engine — giữ kiến trúc hiện tại không đổi.

## 📄 Tài liệu
- [`brainstorm.md`](./brainstorm.md) — hướng đã mở + quyết định đã chốt + câu hỏi còn mở.

## ✅ Việc kế tiếp
Chốt các câu hỏi còn mở trong [§7 brainstorm](./brainstorm.md#7-câu-hỏi-chốt-cần-trả-lời-trước-khi-chi-tiết-hoá)
rồi viết plan chi tiết (kiến trúc + roadmap).