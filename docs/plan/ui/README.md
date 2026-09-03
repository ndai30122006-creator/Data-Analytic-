# 🎨 UI Plan — Node.js UI Layer

> **Nhánh:** `refactor` · **Trạng thái:** docs đã **đầy đủ, sẵn sàng bắt đầu build** (Giai đoạn 0).

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

## 📄 Tài liệu (đầy đủ để bắt đầu build)
| File | Nội dung |
|---|---|
| [`brainstorm.md`](./brainstorm.md) | Quyết định đã chốt (monorepo, 2 UI, React+Vite, ECharts, pnpm...) |
| [`plan.md`](./plan.md) | Kiến trúc `frontend/` + 20 commit nhỏ theo 6 giai đoạn |
| [`tasks.md`](./tasks.md) | **Task breakdown chi tiết**: contract API, TS types, routing, acceptance từng commit |

## ✅ Việc kế tiếp
Bắt đầu **Giai đoạn 0 — Commit 1** theo [`tasks.md`](./tasks.md): scaffold root `frontend/`
(package.json, `pnpm-workspace.yaml`, `tsconfig.base.json`, `.gitignore`, `.env.example`) —
commit nhỏ + push lên `refactor`.