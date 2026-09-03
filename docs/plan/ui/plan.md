# 🛠 UI/PLAN — Build plan chi tiết cho frontend Node.js

> **Nhánh:** `refactor` · **Trạng thái:** plan để **bắt đầu build UI**.
> Nguyên tắc làm việc: **commit nhỏ + push từng phần** lên `refactor`.
> Đọc kèm: [`brainstorm.md`](./brainstorm.md) (quyết định đã chốt), `../07-api-design.md` (API), `../implement_plan.md`.

## 🎯 Tổng quan target (đã chốt)
- **Monorepo** ngay root: folder **`frontend/`**.
- **2 UI riêng**, KHÔNG build chung: `frontend/web` (web/desktop) & `frontend/mobile` (web trên điện thoại).
- **Logic dùng chung**: `frontend/shared` (api + features + hooks + utils).
- **Framework**: React + Vite (cả `web` & `mobile`). Mobile **không phải app native** — chỉ web UI responsive tối ưu cho điện thoại.
- **Backend KHÔNG đổi**: UI chỉ gọi FastAPI `api.py` qua REST (JWT + BYOK). CORS đã mở `*` (dev).

## 🌍 Môi trường hiện tại (đã kiểm tra)
| Công cụ | Phiên bản |
|---|---|
| node | v24.19.0 ✅ |
| npm | 12.0.2 ✅ |
| pnpm | 11.21.0 ✅ |
| yarn | 1.22.22 ✅ |

→ Có thể dùng **pnpm workspaces** (khuyến nghị, nhanh + tiết kiệm disk) hoặc npm workspaces.

## 📌 Chuẩn bị docs (commit nhỏ này)
- [x] `brainstorm.md` — quyết định: monorepo `frontend/`, 2 UI riêng, shared logic, React+Vite, mobile=web.
- [~] `plan.md` (file này) — build plan chi tiết.

---

## 📁 Cấu trúc đích `frontend/`
```text
frontend/
├── package.json                  # root: workspaces + scripts (dev:web, dev:mobile, build, test)
├── pnpm-workspace.yaml           # packages: web, mobile, shared
├── tsconfig.base.json            # TS config dùng chung (strict, paths)
├── .env.example                  # VITE_API_BASE=http://localhost:8000
├── .gitignore                    # node_modules, dist, .env
├── shared/                       # logic dùng chung (KHÔNG UI riêng)
│   ├── package.json              #   name: @app/shared (private)
│   ├── src/
│   │   ├── index.ts
│   │   ├── api/                  #   client + endpoints (nhóm theo §4 brainstorm)
│   │   │   ├── client.ts         #   axios/fetch wrapper + JWT header + 401 handling
│   │   │   ├── auth.ts           #   register/login/verify/api-key/delete
│   │   │   ├── datasets.ts       #   list/create/ingest/profile/delete
│   │   │   ├── pipelines.ts      #   crud/preview/run/runs
│   │   │   ├── brief.ts          #   create/list/get
│   │   │   ├── dashboards.ts     #   crud/data/generate
│   │   │   ├── analysis.ts       #   run
│   │   │   └── system.ts         #   health/env-validate
│   │   ├── types/                #   TS types (hoặc gen từ OpenAPI)
│   │   ├── features/             #   business logic/state từng feature
│   │   │   ├── auth/             #   store auth token, user
│   │   │   ├── ingest/
│   │   │   ├── pipeline/
│   │   │   ├── brief/
│   │   │   ├── dashboard/
│   │   │   ├── lab/
│   │   │   ├── settings/
│   │   │   └── lineage/
│   │   ├── hooks/                #   dùng chung
│   │   └── utils/
│   └── tsconfig.json
├── web/                          # UI web/desktop (React+Vite, bundle riêng)
│   ├── package.json              #   name: @app/web
│   ├── vite.config.ts            #   proxy /api -> localhost:8000 (dev)
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx               #   router 7 screens
│   │   ├── components/           #   UI desktop: Sidebar, DataGrid, Chart...
│   │   ├── layout/               #   DesktopShell
│   │   ├── pages/                #   Ingest, Pipeline, Brief, Dashboard, Lab, Settings, Lineage
│   │   └── styles/               #   css vars, theme desktop
│   └── index.html
└── mobile/                       # UI mobile (web trên điện thoại, React+Vite, bundle riêng)
    ├── package.json              #   name: @app/mobile
    ├── vite.config.ts
    ├── src/
    │   ├── main.tsx
    │   ├── App.tsx               #   router + BottomNav
    │   ├── components/           #   UI mobile: BottomNav, Card, Chart (read-first)
    │   ├── layout/               #   MobileShell
    │   ├── pages/                #   Brief, Dashboard, Lab, Lineage, Login (+ Ingest/Pipeline read-only tuỳ)
    │   └── styles/               #   css vars, theme mobile
    └── index.html
```

> Quy tắc: `web` & `mobile` chứa **UI layer + composition**, không nhét logic feature/API.
> `shared/features` chứa logic; `web`/`mobile` import qua `@app/shared`.

---

## 🧭 Các bước build — mỗi bước = 1 commit nhỏ, push lên `refactor`

### GIAI ĐOẠN 0 — Khởi tạo monorepo `frontend/` (commit 1–2)
Mục tiêu: dựng khung `frontend/` + workspaces để mọi package hoạt động.

**Commit 1 — scaffold root `frontend/`:**
- Tạo `frontend/package.json` (root, private, scripts): `dev:web`, `dev:mobile`, `build`, `typecheck`.
- `frontend/pnpm-workspace.yaml`: `packages: ['shared', 'web', 'mobile']` (hoặc npm workspaces).
- `frontend/tsconfig.base.json`: strict, `moduleResolution: bundler`, `jsx: react-jsx`.
- `frontend/.gitignore`: `node_modules/`, `dist/`, `.env*`.
- `frontend/.env.example`: `VITE_API_BASE=http://localhost:8000`.

**Commit 2 — scaffold `shared` package (rỗng, có thể build):**
- `frontend/shared/package.json`: `name: @app/shared`, `private: true`, `type: module`.
- `frontend/shared/src/index.ts` + `tsconfig.json`.
- `frontend/shared/src/api/client.ts` — wrapper chuẩn (xem §bên dưới).

> ✅ Sau commit này: `cd frontend && pnpm install` chạy được, không lỗi import.

### GIAI ĐOẠN 1 — `shared/api` + types (commit 3–4)
Mục tiêu: client gọi đủ 28 endpoint của FastAPI, kiểu TS rõ ràng.

**Commit 3 — `shared` API client nền:**
- `client.ts`: fetch wrapper, gắn `Authorization: Bearer <token>`, parse `Content-Type: application/json`,
  xử lý HTTPException `detail`, cảnh báo khi `401` (logout). BASE = `VITE_API_BASE`.
- `types/index.ts`: TS types cho `Dataset`, `Profile`, `PipelineSpec`, `RunStatus`,
  `Brief`, `DashboardSpec`, `ChartSpec`, `LoginResponse`, `AuthVerify`.

**Commit 4 — `shared/api/*.ts`:** implement các hàm gọi endpoint, nhóm theo §4 brainstorm:
- `auth.ts`: register/login/verify/apiKey(BYOK)/deleteUser.
- `datasets.ts`: list/create/ingestFile(FormData)/profile/delete.
- `pipelines.ts`: create/list/get/preview/run/listRuns/getRun.
- `brief.ts`: create/list/get.
- `dashboards.ts`: create/list/get/update/data/generate.
- `analysis.ts`: run(params). · `system.ts`: health/envValidate.
- Export tổng từ `index.ts`.

> ✅ Test: gọi `GET /health` qua `api` khi backend chạy `uvicorn`.

### GIAI ĐOẠN 2 — `shared/features` + hooks (commit 5–6)
Mục tiêu: business logic/state dùng chung, trước khi làm UI.

**Commit 5 — feature `auth` + `settings` (BYOK):**
- `features/auth/`: quản lý token (setToken, currentUser), login/register flow, `useAuth` hook.
- `features/settings/`: đọc/lưu API key (gọi `auth.apiKey`), danh sách provider.

**Commit 6 — feature còn lại (skeleton logic + hook):**
- `features/ingest`, `pipeline`, `brief`, `dashboard`, `lab`, `lineage` — mỗi feature:
  `index.ts` + `state/actions` gọi qua `shared/api` (chưa vẽ UI).
- `hooks/useAsync`, `useDebounce`.

> ✅ Sau commit này: logic feature hoàn chỉnh, vẫn chưa có UI cụ thể.

### GIAI ĐOẠN 3 — `web/` UI desktop (commit 7–13)
Mục tiêu: thay Streamlit ở bản desktop.

**Commit 7 — scaffold `web` (React+Vite):**
- `web/package.json` (`@app/web`), `vite.config.ts` (proxy `/api` → `:8000`),
  `index.html`, `src/main.tsx`, `styles/` (theme desktop: css vars, layout rộng).

**Commit 8 — shell desktop + auth UI:** `layout/DesktopShell` (sidebar trái, header),
  routing (react-router) 7 routes, `pages/Login` + `pages/Settings` (BYOK) gắn `features/auth`+`settings`.

**Commit 9 — Ingest page (datasets):** upload → preview → confirm (dùng `features/ingest`).

**Commit 10 — Brief + Lineage pages:** 1-click brief + version; lineage (read-only).

**Commit 11 — Dashboard page:** `features/dashboard` → render chart. Chọn lib §2.4
  (ECharts hoặc Recharts).

**Commit 12 — Pipeline page:** NL → spec (YAML) → dry-run → run → history (`features/pipeline`).

**Commit 13 — Lab page:** chọn phân tích → `analysis.run` → hiện kết quả (bảng/chart).

> ✅ Checkpoint: `pnpm dev:web` chạy, login + 7 screens hoạt động với backend.

### GIAI ĐOẠN 4 — `mobile/` UI mobile (commit 14–18)
Mục tiêu: web UI tối ưu điện thoại, tái dùng `shared`.

**Commit 14 — scaffold `mobile` (React+Vite):** tương tự web nhưng theme mobile
  (bottom-nav, card dọc, touch). `vite.config.ts` proxy `:8000`.

**Commit 15 — shell mobile + login:** `MobileShell` + `BottomNav`; login dùng `features/auth`.

**Commit 16 — read-first pages:** Brief, Dashboard, Lineage (tối ưu xem trên điện thoại).

**Commit 17 — Lab pintasan + Settings:** Lab (chọn nhanh kiểu phân tích), Settings BYOK.

**Commit 18 — Ingest/Pipeline mobile (nếu cần):** upload file + theo dõi pipeline đơn giản.

> ✅ Checkpoint: `pnpm dev:mobile` chạy, dùng chung logic, layout/touch mobile đúng.

### GIAI ĐOẠN 5 — Polish & tích hợp deploy (commit 19–20)
**Commit 19 — docs + test:** test cho `shared` (api client), ví dụ component test web/mobile,
  cài vitest + testing-library, giữ coverage logic.
**Commit 20 — deploy/CI:** nginx `location /app/web` + `location /app/mobile` → static build;
  Dockerfile phục vụ build web/mobile; cập nhật README hướng dẫn chạy 2 bản.

---

## ✋ Chuẩn lỗi & môi trường khi build
- Backend phải chạy: `uvicorn api:app --reload --port 8000`.
- CORS dev đã mở `*`. Khi deploy: đặt `allow_origins` theo domain web/mobile.
- JWT: lưu token ở client (localStorage/memory) — quyết định an toàn khi deploy.
- `pytest` (Python) vẫn giữ; thêm test Node trong `frontend/**/*.test.*`.