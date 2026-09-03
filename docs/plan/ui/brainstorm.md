# 💡 UI/Brainstorm — Node.js UI Layer (2 nền tảng: Mobile + Web/Desktop)

> **Trạng thái:** Brainstorm — chưa chốt kiến trúc, đang mở các hướng.
> **Nhánh:** `refactor`.
> **Target:** thay thế dần Streamlit bằng một **bộ UI riêng trên Node.js**,
> chia **2 client riêng biệt**: web/desktop (Desktop web) + mobile (điện thoại).

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

### 2.1 Thư mục — monorepo hay tách riêng?
Monorepo trong repo này (khuyến nghị cho dự án cá nhân và shared Auth/FastAPI):
```
ui/
├── package.json / pnpm-workspace.yaml
├── packages/
│   ├── shared/          # API client, types (generated từ OpenAPI), utils
│   ├── web/             # Web/Desktop UI
│   └── mobile/          # Mobile UI
└── ...
```
**Câu hỏi:** dùng pnpm workspace, npm workspaces, hay Turborepo?

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

1. **Giai đoạn A — Nền móng:** monorepo + `shared` package + OpenAPI→TS types +
   auth (login/register/BYOK) trên web. Backend chỉ thêm CORS origin.
2. **Giai đoạn B — Web/Desktop skeleton:** routing đủ 7 screens, mỗi screen gọi API thật
   (datasets list, profile) → thay thế Streamlit Ingest.
3. **Giai đoạn C — Web Dashboard + Lab:** dashboard render chart (ECharts), Lab → `/analysis/run`.
4. **Giai đoạn D — Pipeline + Brief web:** toàn bộ workflow.
5. **Giai đoạn E — Mobile (PWA):** clone web codebase, responsive mobile, read-first
   (Brief + Dashboard + Lineage), login.
6. **Giai đoạn F — Polish:** loại Streamlit, demo, deploy (nginx trỏ backend + static UI).

---

## 7. Câu hỏi chốt cần trả lời trước khi chi tiết hoá

- [ ] **Monorepo** hay tách repo? (đề xuất: monorepo `ui/` trong repo này)
- [ ] **Web framework**: React+Vite (đề xuất) hay Next/Vue/Svelte?
- [ ] **Mobile**: PWA responsive (đề xuất bắt đầu) hay React Native/Expo ngay?
- [ ] **Package manager**: npm / pnpm / yarn workspaces?
- [ ] **Data viz**: ECharts / Recharts / khác?
- [ ] **Database mới**: có cần migration backend, hay backend đã đủ?
- [ ] **Thứ tự feature**: bắt đầu bằng screen nào để "dùng được" sớm nhất?
- [ ] **Giữ Streamlit song song** bao lâu trước khi xoá?