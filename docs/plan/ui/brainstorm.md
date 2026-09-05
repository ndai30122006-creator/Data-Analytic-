# 💡 UI/Brainstorm — Node.js UI Layer (2 nền tảng: Mobile + Web/Desktop)

> **Trạng thái:** **ĐÃ HOÀN TẤT** — UI Node.js (web + mobile) đã build xong, merge `main`,
> Streamlit đã xoá. Repo đổi tên **workbench-ai**.
> **Nhánh:** `refactor` (= `main`). 
> **Target (đã đạt):** thay thế Streamlit bằng một bộ UI riêng trên Node.js,
> chia **2 client riêng biệt**: web/desktop (Desktop web) + mobile (điện thoại).
>
> **✅ Đã chốt:**
> - Giữ nguyên **1 repo duy nhất** (monorepo, cấu trúc `frontend/`).
> - Xây **kiến trúc modular frontend trước** — tách feature thành module độc lập
>   dùng chung trong `shared/`, web & mobile chỉ là 2 UI riêng lắp ghép.

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

### 2.1 Cấu trúc repo — ✅ Đã chốt: monorepo 1 repo + `frontend/` ở root
**Quyết định:** giữ **nguyên trong 1 repo** này (monorepo); folder lớn **`frontend/`**
ngay root, **2 folder con riêng** — bản web/desktop và bản web trên điện thoại.
Lý do: dự án cá nhân, dùng chung Auth/FastAPI, deploy cùng nginx.

```text
frontend/                    # root frontend Node.js (monorepo)
├── package.json
├── pnpm-workspace.yaml      # (hoặc npm workspaces)
├── web/                     # UI riêng — web/desktop (React+Vite, bundle riêng)
├── mobile/                  # UI riêng — web trên điện thoại (React+Vite, bundle riêng)
├── shared/                  # DÙNG CHUNG — logic, API, types, hooks, components trừu tượng
│   ├── api/                 #   client + TS types (gen từ FastAPI OpenAPI)
│   ├── features/            #   business logic/state của từng feature
│   ├── hooks/
│   └── utils/
├── openapi.json             # gen từ FastAPI → TS types
└── tsconfig.base.json
```
> **Nguyên tắc:** `web` & `mobile` = 2 app UI riêng (tối ưu giao diện riêng),
> **KHÔNG** build chung bundle; nhưng cùng dùng logic trong `shared/`.
> **Package manager:** chưa chốt (thảo luận §7) — npm / pnpm / yarn đều hỗ trợ.

### 2.2 Framework web/desktop — ✅ Đã chốt: React + Vite
**Quyết định:** bản web/desktop dùng **React + Vite**.
Lý do: phổ biến nhất, hệ sinh thái chart lớn (Recharts/ECharts), routing nhẹ, build nhanh —
đủ tốt cho "local-first data app" (không cần SSR/SEO như Next).

### 2.3 Mobile — ✅ Đã chốt: KHÔNG app, là **web UI trên điện thoại**
**Quyết định:** mobile **không phải app native** (không React Native / Expo / Capacitor).
Mà là **UI web tối ưu cho điện thoại** (responsive/PWA), nằm folder riêng `frontend/mobile`.

| Lựa chọn | Quyết định |
|---|---|
| ❌ React Native / Expo | không (đây là app native, cần build/store) |
| ❌ Capacitor (native shell) | không |
| ✅ **Web UI responsive tối ưu mobile** | dùng (folder `mobile/`, React+Vite, bundle riêng) |

**Điểm khác với web/desktop:** `mobile/` tối ưu giao diện cho màn hình nhỏ + touch:
bottom-nav, card xếp dọc, layout đọc-là-chính (Brief/Dashboard/Lineage dễ xem trước),
nhưng **cùng logic** trong `shared/`.

### 2.4 Data-visualization (chart) — ✅ Đã chốt: ApexCharts cho dashboard
- Streamlit (đã xoá) trước dùng **Plotly** (backend render JSON figure).
- UI Node **không kéo Plotly JS**.
- **Quyết định (đã chốt, GĐ-D đã switch):**
  - Dashboard chart → **Apache ECharts** (mạnh, tree-shake) — *ban đầu chốt*, sau đó **switch sang ApexCharts** (lighter bundle, khoẻ cho cả web & mobile).
  - Bảng dữ liệu lớn → **ag-Grid** (cộng đồng, free) cho web/desktop *(hiện chưa bắt buộc)*.
  - Mobile chart → dùng ApexCharts (responsive) hoặc bản đơn giản CSS-based cho KPI nhỏ.
- Backend trả **data aggregated** (JSON) từ `/dashboards/{id}/data` → frontend vẽ, tương tự renderer hiện tại.

---

### 2.5 Kiến trúc modular frontend — ✅ Đã chốt hướng: modular trước
**Quyết định:** xây **frontend modular trước** — tách logic dùng chung ra `shared/`,
web & mobile chỉ là **2 UI riêng** lắp ghép cùng logic. Cấu trúc thực tế nằm trong
`frontend/` (§2.1).

**Vì sao modular:**
- **Tái dùng logic giữa web/desktop & mobile** — cùng business logic/state/API call
  trong `shared/features`; chỉ khác **UI layer** ở `web/` vs `mobile/` (layout/nav/component).
- **Dễ bảo trì & mở rộng** — thêm feature mới = thêm 1 module trong `shared/features`.
- **Khớp backend** — mỗi feature module map 1 nhóm endpoints (Ingest→datasets,
  Pipeline→pipelines/runs, ...).
- **2 bundle UI riêng**, tối ưu riêng cho PC và điện thoại — không build chung.

**Mô hình modular (feature-first) trong `frontend/`:**
```
frontend/
├── shared/                # KHÔNG UI riêng — logic dùng chung (2 app cùng dùng)
│   ├── api/               #   axios/fetch client + generated TS types + auth token
│   ├── features/          #   mỗi feature = 1 module (state + API + logic)
│   │   ├── ingest/        #   upload→preview→confirm (datasets)
│   │   ├── pipeline/      #   NL→spec→dry-run→run→history
│   │   ├── brief/         #   1-click brief + version
│   │   ├── dashboard/     #   spec→data→render chart + edit
│   │   ├── lab/           #   statistics / analysis/run
│   │   ├── settings/      #   BYOK key + provider
│   │   └── lineage/       #   dataset→brief→dashboard
│   ├── hooks/             #   useAuth, useDataset, useDebounce...
│   └── utils/
├── web/                   # UI web/desktop — components + layout + pages RIÊNG
│   ├── components/        #   UI thì desktop (sidebar to, bảng rộng)
│   ├── layout/            #   shell desktop
│   └── pages/
└── mobile/                # UI mobile — components + layout + pages RIÊNG
    ├── components/        #   bottom-nav, card dọc, touch-first
    ├── layout/            #   shell mobile
    └── pages/
```

> Hợp nhất: `shared/features` = `core + features` các cách gọi trước — logic dùng chung.

**Ràng buộc modular (để "friendly" và sạch):**
- Feature module **không import nhau** (chỉ qua `shared`).
- Feature module **không import backend trực tiếp** — chỉ qua `shared/api`.
- `web`/`mobile` chứa **UI layer và composition** — không nhét logic feature/API.
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
┌────────────────────────── frontend/ (Node) ───────────────────────────┐
│   web/ (UI web/desktop)   mobile/ (UI web trên điện thoại)             │
│   ─────────── components·     ─────────── components·layout·pages      │
│   layout·pages (PC, rộng)     (bottom-nav, card dọc, touch, read-first)│
│                                                                        │
│            ┌────────────────── shared/ (logic dùng chung) ─────┐        │
│            │ api client + types ▪ features (7 module) ▪ hooks  │        │
│            └───────────────────────────────────────────────────┘        │
└─────────────────────────────────┬──────────────────────────────────────┘
                                    │ HTTP/JSON (JWT)
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
> Thay vì làm screen trước, ta dựng `frontend/shared` (logic dùng chung) trước,
> rồi `web`/`mobile` (2 UI riêng) chỉ là lớp lắp ghép mỏng.

1. **Giai đoạn A — Nền móng `frontend/`:** monorepo `frontend/` (package manager +
   workspaces) + `shared` (api client + OpenAPI→TS types, hooks, utils) + auth
   (login/register/BYOK). Backend chỉ thêm CORS origin.
   **Sản phẩm:** `shared` dùng được, chạy auth trên web shell.
2. **Giai đoạn B — Feature modules (trước khi làm screen):** tách từng feature
   thành module độc lập trong `shared/features` (ingest, pipeline, brief, dashboard,
   lab, settings, lineage) — mỗi module: state + API call + logic, **không import nhau**,
   chỉ dùng `shared`.
3. **Giai đoạn C — Web/Desktop UI:** `frontend/web` = UI riêng cho PC (layout,
   components, pages) lắp ghép logic từ `shared`. Bắt đầu thay Streamlit Ingest.
4. **Giai đoạn D — Web workflow đầy đủ:** Dashboard (render chart — ECharts rồi switch ApexCharts) +
   Lab (`/analysis/run`) + Pipeline/Brief — toàn bộ workflow trên web/desktop.
5. **Giai đoạn E — Mobile UI:** `frontend/mobile` = UI riêng cho điện thoại
   (bottom-nav, card dọc, touch-first, read-first) dùng lại logic `shared`.
6. **Giai đoạn F — Polish:** loại Streamlit, demo, deploy (nginx trỏ backend +
   static UI từ `web` & `mobile`).

---

## 7. Quyết định đã chốt (câu hỏi trước khi chi tiết hoá)

- [x] **Monorepo** hay tách repo? → **Giữ 1 repo** (monorepo `frontend/` trong repo này) ✅
- [x] **Kiến trúc modular frontend?** → **Đã chốt hướng: modular trước** (feature-first, xem §2.5) ✅
- [x] **Web framework** → **React + Vite** (xem §2.2) ✅
- [x] **Mobile** → **Không app**, là **web UI trên điện thoại** (folder `mobile/`, xem §2.3) ✅
- [x] **Data viz** → **Apache ECharts** (chốt đầu) → **đã switch sang ApexCharts** (dashboard). Bảng lớn tuỳ dùng ag-Grid. Xem §2.4 ✅
- [x] **Package manager** → **pnpm workspaces** (đã cài pnpm 11. sẵn). Xem `plan.md` ✅
- [x] **Database/backend** → **không thay đổi backend cho giai đoạn building UI**;
      backend `api.py` đã đủ endpoint. Chỉ cần CORS config khi deploy. ✅
- [x] **Thứ tự feature web** → làm **Ingest trước** (để có data từ đầu), rồi Brief/Lineage,
      Dashboard, Pipeline, Lab. Xem `plan.md` GĐ3. ✅
- [x] **Giữ Streamlit song song?** → **đã giữ trong lúc build Node**, và **đã loại bỏ hoàn toàn** (app.py, .streamlit, src/ui/ xoá; Node UI là frontend duy nhất). ✅

> Tất cả quyết định đã chốt → build theo `plan.md` (kế hoạch triển khai) +
> `tasks.md` (task breakdown chi tiết).