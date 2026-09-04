# 🎨 UI Plan — Node.js UI Layer

> **Trạng thái:** build UI **hoàn tất GĐ0–GĐ5** (đã merge vào `main`) — web + mobile chạy được, xem [`local-dev.md`](./local-dev.md) để chạy ngay.

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
| File | Nội dung |
|---|---|
| [`local-dev.md`](./local-dev.md) | **🚀 Hướng dẫn chạy local dev** (backend + web + mobile, troubleshooting) — bắt đầu từ đây |
| [`brainstorm.md`](./brainstorm.md) | Quyết định đã chốt (monorepo, 2 UI, React+Vite, ECharts, pnpm...) |
| [`plan.md`](./plan.md) | Kiến trúc `frontend/` + 20 commit nhỏ theo 6 giai đoạn |
| [`tasks.md`](./tasks.md) | **Task breakdown chi tiết**: contract API, TS types, routing, acceptance từng commit |

## 🚀 Chạy nhanh
```bash
# Terminal 1 — Backend
python3 -m uvicorn api:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend && pnpm install
pnpm dev:web        # http://localhost:5173
# pnpm dev:mobile   # http://localhost:5174 (tùy chọn)
```
Chi tiết đầy đủ (cài đặt deps, tạo tài khoản, troubleshooting): [`local-dev.md`](./local-dev.md).