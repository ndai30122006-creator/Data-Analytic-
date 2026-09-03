# 🎨 UI Plan — Node.js UI Layer

> **Nhánh:** `refactor` · **Trạng thái:** plan đã sẵn sàng để **bắt đầu build** (Giai đoạn 0).

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
- [`plan.md`](./plan.md) — **Build plan chi tiết** (cấu trúc `frontend/` + 20 commit nhỏ theo giai đoạn).
- [`brainstorm.md`](./brainstorm.md) — quyết định đã chốt + câu hỏi còn mở.

## ✅ Việc kế tiếp
Bắt đầu **Giai đoạn 0** theo [`plan.md`](./plan.md): scaffold `frontend/` monorepo
(package.json, workspaces, `.gitignore`, `.env.example`) — commit nhỏ + push lên `refactor`.