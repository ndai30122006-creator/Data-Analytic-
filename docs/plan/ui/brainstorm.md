# 💡 UI/Brainstorm — Node.js UI Layer (2 nền tảng: Mobile + Web/Desktop)

> **Trạng thái:** Brainstorm — đã chốt một số quyết định cốt lõi (✅), còn mở các hướng khác.
> **Nhánh:** `refactor`.
> **Target:** thay thế dần Streamlit bằng một **bộ UI riêng trên Node.js**,
> chia **2 client riêng biệt**: web/desktop (Desktop web) + mobile (điện thoại).
>
> **✅ Đã chốt:**
> - Giữ nguyên **1 repo duy nhất** (monorepo, cấu trúc `ui/`).
> - Xây **kiến trúc modular frontend trước** — tách feature thành module độc lập,
>   dùng chung core, trước khi làm chi tiết từng screen.

---

## 1. Bối cảnh & mục tiêu

### Tại sao Node.js?
- Streamlit là framework "bảng điều khiển data-app" — tiện nhanh nhưng ràng buộc
  layout, khó làm UI theo ý muốn, khó phân tách mobile/desktop.
- Tách UI khỏi Streamlit giúp **chủ động thiết kế UI** và là bước học
  full-stack (Node + một frontend framework).

### Nguyên tắc "friendly với stack/architecture hiện tại" (bắt buộc giữ)
Kiến trúc hiện tại đã tách UI khỏi logic rõ ràng — tận dụng tối đa, không phá:

1. **FastAPI `api.py` là execution layer DUY NHẤT.** UI Node chỉ gọi qua HTTP/JSON,
   **không được** import code Python/duckdb trực tiếp. → Backend hầu như **không đổi**.
2. **Giao tiếp qua REST endpoints đã có** (28 route hiện hữu — xem §4). UI Node chỉ cần
   viết client cho các endpoint này.
3. **Auth JWT** (`/auth/login`, `/auth/register`, `/auth/api-key` BYOK) — giữ nguyên.
4. **DuckDB (warehouse) + SQLite (metadata) + AI gateway** nằm trong backend — UI vô hình.
5. **LLM authoring ≠ runtime, LLM chỉ nhận profile, BYOK, fallback rule-based** — là
   contract backend, UI không xen vào.

### 2 client riêng biệt (yêu cầu chính)
| Client | Target | Ghi chú |
|---|---|---|
| **Web/Desktop UI** | trình duyệt desktop (Mac/Win/Linux), cũng chạy trên màn hình lớn | full features, layout rộng |
| **Mobile UI** | điện thoại (PWA / responsive / native optional) | phân đoạn read-first + xem dashboard/brief |

---

## 2. Phạm vi & câu hỏi đang mở (brainstorm)

### 2.1 Cấu trúc repo — ✅ Đã chốt: monorepo 1 repo
**Quyết định:** giữ **nguyên trong 1 repo** này (monorepo), không tách repo riêng.
Lý do: dự án cá nhân, dùng chung Auth/FastAPI, deploy cùng nginx.

```
ui/                          # root của frontend Node.js (monorepo)
├── package.json
├── pnpm-workspace.yaml      # (hoặc npm workspaces)
├── packages/
│   ├── core/                # design system, hooks, theme, layout
│   ├── features/            # (tùy chọn — xem §2.5) feature modules
│   ├── web/                 # Web/Desktop app (entry)
│   └── mobile/              # Mobile app (entry, đọc-là-chính)
├── openapi.json             # gen từ FastAPI → TS types
└── tsconfig.base.json
```
> **Package manager:** chưa chốt (thảo luận §7) — npm / pnpm / yarn đều được
> monorepo workspace hỗ trợ.

### 2.2 Framework web/desktop
| Lựa chọn | Ưu nhược | Ghi chú |
|---|---|---|
| **React + Vite** | phổ biến nhất, hệ sinh thái chart lớn (Recharts/ECharts), dễ thuê/người khác đọc | mặc định nên xét |
| **Next.js** | SSR/SSG, routing mạnh, nhưng nặng cho "local-first data app" | xét nếu cần SEO/nhiều trang |
| **Vue/Nuxt** | nhẹ, dễ học | alternative |
| **SvelteKit** | cực nhẹ | ít người dùng |

**Đề xuất tạm:** React + Vite cho web; xem thêm Electron/Tauri nếu cần "desktop app" thật sự.

### 2.3 Framework mobile
| Lựa chọn | Ưu nhược |
|---|---|
| **PWA (web responsive)** | 1 codebase với web, rẻ nhất, không cần store |
| **React Native / Expo** | app native, ux tốt nhất mobile, cần build/store |
| **Capacitor (wrapper web)** | native shell + web code, trung gian |

**Đề xuất tạm:** bắt đầu bằng **PWA responsive** (dùng chung codebase web với layout mobile cắt),
tách React Native/Expo thành phase sau nếu cần store.

### 2.4 Data-visualization (chart)
- Streamlit hiện dùng **Plotly** (backend render JSON figure).
- UI Node không kéo Plotly JS → chọn: **ECharts** (mạnh, tree-shake), **Recharts** (React-native),
  cho dashboard; **ag-grid** cho bảng lớn.
- Backend trả **data aggregated** (JSON) từ `/dashboards/{id}/data` → frontend vẽ, tương tự renderer hiện tại.

---

### 2.5 Kiến trúc modular frontend — ✅ Đã chốt hướng: modular trước
**Quyết định:** xây **frontend modular trước** — tách thành các module độc lập,
dùng chung core, trước khi làm chi tiết từng screen.

**Vì sao modular:**
- **Tái dùng giữa Web/Desktop & Mobile** — cùng feature module (Ingest, Pipeline, Brief,
  Dashboard, Lab, Settings, Lineage) chạy được cả 2 nền tảng; chỉ khác ở `shell` (layout/nav).
- **Dễ bảo trì & mở rộng** — thêm feature mới = thêm 1 module, không đụng app chính.
- **Khớp backend** — mỗi feature module map 1 nhóm endpoints (Ingest→datasets,
  Pipeline→pipelines/runs, ...).
- **Dead-code elimination & bundle nhỏ** — mobile chỉ tải module nó cần.

**Mô hình modular đề xuất (feature-first):**
```
packages/
├── core/                # KHÔNG feature — dùng chung
│   ├── api/             #   axios/fetch client + generated types + auth token
│   ├── ui/              #   design system: Button, Card, DataGrid, Chart...
│   ├── theme/           #   tokens (dark/light), glassmorphism
│   ├── hooks/           #   useAuth, useDataset, useDebounce...
│   └── layout/          #   shell của từng nền tảng
├── features/            # mỗi feature = 1 module (độc lập, tự quản state)
│   ├── ingest/          #   upload→preview→confirm (datasets)
│   ├── pipeline/        #   NL→spec→dry-run→run→history
│   ├── brief/           #   1-click brief + version
│   ├── dashboard/       #   spec→render chart + edit
│   ├── lab/             #   statistics / analysis/run
│   ├── settings/        #   BYOK key + provider
│   └── lineage/         #   dataset→brief→dashboard
├── web/                 # LÁT MỎNG: import feature modules + core, bố layout
└── mobile/              # LÁT MỎNG: chỉ tải feature read-first
```

**Ràng buộc modular (để "friendly" và sạch):**
- Feature module **không import nhau** (chỉ core). Giao tiếp qua props/events.
- Feature module **không import backend trực tiếp** — chỉ qua `core/api`.
- `web`/`mobile` = "app composition root" — ghép feature, không chứa logic feature.
- Mỗi feature module có `index.ts` export rõ ràng + test riêng.

---

## 3. Cách "friendly" với stack hiện tại — chi tiết

### 3.1 Dùng OpenAPI spec của FastAPI
- FastAPI tự sinh `openapi.json`. → Dùng tool (openapi-typescript) để **generate TypeScript types**
  tự động từ `/openapi.json`, đảm bảo client đồng bộ backend.
- Backend thêm CORS allow cho origin của UI Node (đã có `CORSMiddleware`).

### 3.2 Shared API client
- Package `shared` chứa: base URL config, axios/fetch wrapper, auth token lưu trữ,
  error handling theo format backend (HTTPException detail), typing từ OpenAPI.

### 3.3 Giữ nguyên logic / không duplicata
- Không viết lại duckdb/analysis/pipeline → chỉ gọi `/analysis/run`, `/pipelines/run`,
  `/dashboards/generate` (AI authoring vẫn ở backend).
- Lab/Statistics: dùng `/analysis/run` (dispatch nhiều loại) — UI Node chỉ present kết quả.

### 3.4 Migration từ Streamlit
- Streamlit hiện tại (`app.py`) có thể giữ song song lúc đầu (fallback), sau đó loại bỏ.
- Định nghĩa rõ: feature nào chuyển sang Node trước (thứ tự ưu tiên).

---

## 4. Bản đồ endpoints hiện tại (UI Node sẽ gọi)

> Nguồn: `api.py` (28 route). UI Node chỉ viết client cho các endpoint này.

| Nhóm | Method/Path | UI dùng |
|---|---|---|
| Auth | `POST /auth/register`, `/auth/login`, `/auth/api-key`, `GET /auth/verify`, `DELETE /auth/user` | Web + Mobile (login, BYOK settings) |
| Datasets | `GET /datasets`, `POST /datasets`, `POST /datasets/ingest`, `GET /datasets/{id}/profile`, `DELETE /datasets/{name}` | Ingest screen, profile |
| Pipelines | `POST/GET /pipelines`, `GET /pipelines/{id}`, `POST /pipelines/preview`, `POST /pipelines/run`, `GET /runs/{id}`, `GET /runs` | Pipeline screen |
| Brief | `POST /brief/{id}`, `GET /brief/{id}`, `GET /brief/{id}/{version}` | Brief screen |
| Dashboards | `POST/GET /dashboards`, `GET/PUT /dashboards/{id}`, `POST /dashboards/{id}/data`, `POST /dashboards/generate` | Dashboard screen |
| Analysis | `POST /analysis/run` | Lab/Statistics |
| System | `GET /health`, `GET /env/validate` | Health/Setup |

---
## 5. Sơ đồ kiến trúc target (Node UI thay Streamlit)

```
┌──────────────────────────── 2 clients ────────────────────────────┐
│   Web/Desktop UI (React+Vite)      Mobile UI (PWA / React Native) │
│   ───────────────────────────      ─────────────────────────────   │
│   screens: Ingest·Pipeline·Brief·  screens: Brief·Dashboard·Lab   │
│   Dashboard·Lab·Settings·Lineage   (read-first, cắt theo mobile)  │
└──────────────┬──────────────────────────────┬─────────────────────┘
               │        HTTP/JSON (JWT)       │
               └──────────────┬───────────────┘
                             ▼
         ┌─── FastAPI `api.py` (execution layer, KHÔNG đổi) ───┐
         │ /datasets /pipelines /runs /brief /dashboards       │
         │ /analysis /auth /health /env  + AI Gateway (BYOK)   │
         └──────────┬──────────────┬──────────────┬────────────┘
                    ▼              ▼              ▼
               DuckDB          Pipeline        SQLite metadata
               (raw+mart)      engine (DAG)
```

---

## 6. Đề xuất thứ tự triển khai (brainstorm giai đoạn)

> Điều chỉnh theo quyết định: **xây kiến trúc modular cho frontend TRƯỚC**.
> Thay vì làm screen trước, ta dựng `core` + các feature module độc lập trước,
> rồi `web`/`mobile` chỉ là lớp lắp ghép mỏng.

1. **Giai đoạn A — Nền móng mono/modular:** `ui/` monorepo + `packages/core`
   (api client + OpenAPI→TS types, design system, theme, hooks) + auth
   (login/register/BYOK). Backend chỉ thêm CORS origin.
   **Sản phẩm:** `core` dùng được, chạy auth trên web shell.
2. **Giai đoạn B — Feature modules (trước khi làm screen):** tách từng feature
   thành module độc lập (ingest, pipeline, brief, dashboard, lab, settings,
   lineage) — mỗi module: state + API call + UI riêng, **không import nhau**,
   chỉ dùng `core`.
3. **Giai đoạn C — Web/Desktop composition:** `packages/web` = lớp lắp ghép,
   routing 7 screens, mỗi screen = 1 feature module. Bắt đầu thay Streamlit Ingest.
4. **Giai đoạn D — Web workflow đầy đủ:** Dashboard (render chart ECharts) +
   Lab (`/analysis/run`) + Pipeline/Brief — toàn bộ workflow trên web.
5. **Giai đoạn E — Mobile composition:** `packages/mobile` tái dùng feature module,
   bố layout mobile, read-first (Brief + Dashboard + Lineage), login.
6. **Giai đoạn F — Polish:** loại Streamlit, demo, deploy (nginx trỏ backend +
   static UI từ `web`/`mobile`).

---

## 7. Câu hỏi chốt cần trả lời trước khi chi tiết hoá

- [x] **Monorepo** hay tách repo? → **Giữ 1 repo** (monorepo `ui/` trong repo này) ✅
- [x] **Kiến trúc modular frontend?** → **Đã chốt hướng: modular trước** (feature-first, xem §2.5) ✅
- [ ] **Web framework**: React+Vite (đề xuất) hay Next/Vue/Svelte?
- [ ] **Mobile**: PWA responsive (đề xuất bắt đầu) hay React Native/Expo ngay?
- [ ] **Package manager**: npm / pnpm / yarn workspaces?
- [ ] **Data viz**: ECharts / Recharts / khác?
- [ ] **Database mới**: có cần migration backend, hay backend đã đủ?
- [ ] **Thứ tự feature**: bắt đầu bằng screen nào để "dùng được" sớm nhất?
- [ ] **Giữ Streamlit song song** bao lâu trước khi xoá?