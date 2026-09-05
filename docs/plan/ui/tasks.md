# ✅ UI/TASKS — Task breakdown chi tiết để build

> **Nhánh:** `refactor` · **Trạng thái:** toàn bộ task đã **hoàn tất** (build + merge `main` + GĐ-D). Đọc kèm: 《[`plan.md`](./plan.md)》(kiến trúc + giai đoạn), 《[`brainstorm.md`](./brainstorm.md)》(quyết định, **chart dùng ApexCharts**).
> File này là danh sách task cụ thể, có contract kỹ thuật + acceptance; dùng làm reference khi mở rộng/tuỳ chỉnh frontend.

## 0. Contract cố định (đối chiếu code `api.py` thực tế)

### 0.1 Auth (JWT)
- `POST /auth/login` body `{username, password}` → **LoginResponse**:
  `{access_token, token_type("bearer"), username, expires_in(giây)}`.
- `POST /auth/register` body `{username, password}` → `{message}`; password ≥ 6 chữ, username không rỗng.
- `GET /auth/verify` (Bearer) → `{username, valid:true}`; dùng để validate token khi app bật.
- `POST /auth/api-key` (Bearer) body `{api_key}` → `{message}` (BYOK); key không rỗng.
- `DELETE /auth/user` (Bearer) → xoá user.

### 0.2 Header bắt buộc
- Ngoài `/auth/login` & `/auth/register`, **mọi endpoint** cần `Authorization: Bearer <token>` (`get_current_user`).
- Lỗi 401 trả `detail` "Invalid or expired token" → client phải logout & đưa về /login.

### 0.3 Datasets
- `GET /datasets` (Bearer) → `{datasets:[{dataset_name, rows, cols, created_at}], username, count}`.
- `POST /datasets` body `{dataset_name, rows?, cols?}` → `{message, dataset}`; lỗi nếu trùng tên.
- `POST /datasets/ingest` **multipart** field `file` (hoặc JSON `{dataset_name}`) → `{message, dataset_id, profile, quality?}`.
  Đây là đường UI upload file.
- `GET /datasets/{id}/profile` (Bearer) → `{dataset_id, dataset_name, profile}` (KHÔNG raw data).
- `DELETE /datasets/{dataset_name}` (Bearer) → `{message}`.

### 0.4 Pipelines & Runs
- `POST /pipelines` body là **PipelineSpec** → tạo.
- `GET /pipelines`, `GET /pipelines/{id}` (Bearer) → danh sách/chi tiết.
- `POST /pipelines/preview` → dry-run (không ghi).
- `POST /pipelines/run` → `{run_id, status:"queued"}` (async BackgroundTasks); poll `GET /runs/{id}`.
- `GET /runs`, `GET /runs/{id}` → `{run_id, pipeline_id, status, result, created_at}`.

### 0.5 Brief & Dashboards
- `POST /brief/{dataset_id}` → sinh brief; `GET /brief/{dataset_id}`, `GET /brief/{id}/{version}`.
- `POST /dashboards` body `DashboardSpec`; `GET/PUT /dashboards/{id}`; `POST /dashboards/{id}/data` → data agg cho renderer; `POST /dashboards/generate`.
- `POST /analysis/run` body `AnalysisRequest{dataset_name, analysis_type, params}` → `{status, username, dataset, analysis_type, results}`.

### 0.6 CORS & security (lưu ý từ fix mới `be498fe`/`8f60a6d`)
- **`CORS_ALLOW_ALL=true`** (dev): backend dùng `allow_origins=["*"]` nhưng **`allow_credentials=False`**.
  → Client KHÔNG dùng `credentials: include` (không cần cookie; dùng **Bearer header** là đủ).
- Không CORS_ALLOW_ALL (prod/deploy): dùng `cors_origins` từ env; client gọi từ origin chính xác được cấu hình.
- Rate limit: giới hạn request/phút; UI nên tránh spam poll (backoff).

### 0.7 Quy tắc dùng chung
- `shared` = logic; `web`/`mobile` chỉ = UI. KHÔNG import backend trực tiếp từ UI.
- Lỗi API trả dạng `{detail: string}` → client hiển thị `detail`.
- KIỂU TypeScript khai báo trong `shared/src/types/index.ts` (contract dưới đây).

---

## 1. TypeScript types contract (`shared/src/types/index.ts`)
```ts
// Auth
export interface LoginResponse { access_token: string; token_type: string; username: string; expires_in: number }
export interface RegisterRequest { username: string; password: string }
export interface LoginRequest { username: string; password: string }

// Datasets
export interface DatasetMeta { dataset_name: string; rows: number; cols: number; created_at: string | null }
export interface DatasetListResponse { datasets: DatasetMeta[]; username: string; count: number }
export interface ProfileResponse { dataset_id: number; dataset_name: string; profile: Record<string, unknown> }
export interface IngestResponse { message: string; dataset_id?: number; profile?: Record<string, unknown>; quality?: unknown }

// Pipelines
export interface PipelineSpec { name: string; source: string; target: string; steps: PipelineStep[] }
export interface PipelineStep { id: string; op: string; params?: Record<string, unknown>; depends_on?: string[] }
export interface RunStarted { run_id: string; status: string }
export interface RunInfo { run_id: string; pipeline_id: string; status: string; result: Record<string, unknown>; created_at: string | null }

// Brief
export interface BriefItem { id: string | number; version?: number; content?: string; created_at?: string }

// Dashboards
export interface ChartSpec { type: 'kpi'|'bar'|'hist'|'box'|'line'|'scatter'; title?: string; x?: string; y?: string; metric?: { column?: string; aggregation?: string }; bins?: number }
export interface DashboardSpec { name: string; source: string; charts: ChartSpec[] }

// Analysis
export interface AnalysisRequest { dataset_name: string; analysis_type: string; params?: Record<string, unknown> }
export interface AnalysisResponse { status: string; username: string; dataset: string; analysis_type: string; results: unknown }

// System
export interface HealthResponse { status: string }
export interface EnvValidateResponse { status: string; warnings: string[]; cors_origins?: string[]; rate_limiter?: string }
```

---

## 2. Scaffold root `frontend/` — checklist cụ thể (Commit 1 & 2)

### Commit 1 — root monorepo
- [ ] `frontend/package.json` (root, private):
  ```json
  { "name": "app-frontend", "private": true, "scripts": {
      "dev:web": "pnpm --filter @app/web dev",
      "dev:mobile": "pnpm --filter @app/mobile dev",
      "build": "pnpm -r build",
      "typecheck": "pnpm -r typecheck",
      "test": "pnpm -r test"
  }}
  ```
- [ ] `frontend/pnpm-workspace.yaml`: `packages: ['shared', 'web', 'mobile']`.
- [ ] `frontend/tsconfig.base.json`: strict, `moduleResolution: bundler`, `module: ESNext`, `target: ES2022`, `jsx: react-jsx`, `paths: { "@app/shared": ["./shared/src"] }`.
- [ ] `frontend/.gitignore`: `node_modules/`, `dist/`, `*.local`, `.env` (giữ `!.env.example`).
- [ ] `frontend/.env.example`: `VITE_API_BASE=http://localhost:8000`.

### Commit 2 — package `shared` (rỗng, build được)
- [ ] `frontend/shared/package.json`: `{ "name": "@app/shared", "version":"0.0.0", "private": true, "type":"module", "main":"src/index.ts", "types":"src/index.ts", "exports": { ".": "./src/index.ts" } }`.
- [ ] `frontend/shared/tsconfig.json` extends base.
- [ ] `frontend/shared/src/index.ts` — export thử (rỗng, verify build).
- [ ] `cd frontend && pnpm install` → chạy không lỗi.

> ✅ Acceptance GĐ0: `cd frontend && pnpm install` xong; `pnpm --filter @app/shared typecheck` pass.

---

## 3. `shared/api` — client + module (Commit 3 & 4)

### `client.ts`
```ts
import { ApiError } from './errors'
const BASE = (import.meta as any).env?.VITE_API_BASE ?? 'http://localhost:8000'
let _token: string | null = null
export function setToken(t: string | null) { _token = t }
export function getToken() { return _token }
export async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = { ...(init.headers as Record<string,string> || {}) }
  if (_token) headers['Authorization'] = `Bearer ${_token}`
  if (init.body && !(init.body instanceof FormData)) headers['Content-Type'] = 'application/json'
  const res = await fetch(`${BASE}${path}`, { ...init, headers })
  if (res.status === 401) { window.dispatchEvent(new Event('app:unauthorized')) }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new ApiError(body?.detail ?? `HTTP ${res.status}`, res.status)
  }
  return res.json() as Promise<T>
}
// helpers
export const api = {
  get:  <T>(p: string) => request<T>(p),
  post: <T>(p: string, body?: unknown) => request<T>(p, { method:'POST', body: body===undefined?undefined: JSON.stringify(body) }),
  put:  <T>(p: string, body: unknown) => request<T>(p, { method:'PUT', body: JSON.stringify(body) }),
  del:  <T>(p: string) => request<T>(p, { method:'DELETE' }),
  upload: <T>(p: string, file: File) => { const fd = new FormData(); fd.append('file', file); return request<T>(p, { method:'POST', body: fd }) },
}
```
> **Lưu ý CORS**: KHÔNG set `credentials:'include'` — thì mới hoạt động khi `CORS_ALLOW_ALL=true` (backend gửi `allow_credentials=False`).

### Module files (mỗi cái export hàm typed)
- `auth.ts`: `register(u,p)`, `login(u,p): LoginResponse`, `verify(): AuthView`, `saveApiKey(key)`, `deleteUser()`.
- `datasets.ts`: `list()`, `create(name)`, `ingestFile(file): IngestResponse`, `getProfile(id)`, `remove(name)`.
- `pipelines.ts`: `create(spec)`, `list()`, `get(id)`, `preview(spec)`, `run(id)`, `listRuns()`, `getRun(id)`.
- `brief.ts`: `create(datasetId)`, `list(datasetId)`, `get(datasetId, version)`.
- `dashboards.ts`: `create(spec)`, `list()`, `get(id)`, `update(id, spec)`, `data(id)`, `generate(payload)`.
- `analysis.ts`: `run(req: AnalysisRequest): AnalysisResponse`.
- `system.ts`: `health()`, `envValidate()`.
- `errors.ts`: `export class ApiError extends Error { constructor(msg:string,public status:number){super(msg)} }`.

### Acceptance (Commit 4)
- [ ] `pnpm --filter @app/shared typecheck` pass.
- [ ] Test nhanh: gọi `system.health()` khi backend `uvicorn` chạy → `{status:"healthy"}`.
- [ ] login → `setToken` → `list()` datasets trả mảng.

---

## 4. `shared/features` + hooks (Commit 5 & 6)

### Commit 5 — auth + settings
- `features/auth/store.ts`: lưu token + username (localStorage key `app_token`), `setToken` global, `logout()`.
- `features/auth/useAuth.ts`: hook `{user, token, login(), register(), logout(), loading}`; tự gọi `verify()` khi mount.
- `features/settings/useSettings.ts`: `{apiKey, saveApiKey()}` gọi `auth.saveApiKey`.
- `features/settings/providers.ts`: `const PROVIDERS = ['openai','gemini']`.

### Commit 6 — feature còn lại + hooks chung
- `features/ingest/`, `pipeline/`, `brief/`, `dashboard/`, `lab/`, `lineage/` mỗi cái `index.ts` + `state.ts` + `actions.ts` gọi qua `shared/api`.
- `hooks/useAsync.ts`, `hooks/useDebounce.ts` (dùng chung).

### Acceptance
- [ ] Logic feature gọi đúng endpoint; không `window` trong shared (trừ hook client).
- [ ] `typecheck` pass.

---

## 5. `web/` UI desktop — pages chi tiết (Commit 7–13)

**Routing (react-router):**
```text
/          → redirect /login (nếu chưa auth) else /ingest
/login     → Login page
/ingest    → Ingest page (datasets)
/pipeline  → Pipeline page
/brief     → Brief page
/dashboard → Dashboard page
/lab       → Lab page
/settings  → Settings page (BYOK)
/lineage   → Lineage page
```

### Commit 7 — scaffold web
- [ ] `web/package.json` (`@app/web`), add: `react`, `react-dom`, `react-router-dom`, `apexcharts` (ApexCharts — đã switch từ ECharts).
- [ ] `vite.config.ts`: proxy `/api` → `http://localhost:8000` (để giảm lệ thuộc CORS khi dev cùng origin).
- [ ] `index.html` + `src/main.tsx` + `src/App.tsx` (router).
- [ ] `src/styles/theme.css`: CSS vars (dark, desktop: sidebar, max-width container).
- [ ] `dependencies`: `@app/shared` (workspace: `"@app/shared": "workspace:*"`).

### Commit 8 — shell + auth
- [ ] `layout/DesktopShell`: sidebar trái (7 nav), header (user, logout).
- [ ] `pages/Login.tsx`: login/register form → `features/auth`.
- [ ] `pages/Settings.tsx`: BYOK (provider select + api key input + save) → `features/settings`.

### Commit 9 — Ingest
- [ ] `features/ingest/IngestPage`: chọn dataset → upload file → `datasets.ingestFile` → hiện profile preview → confirm.

### Commit 10 — Brief + Lineage
- [ ] `features/brief/BriefPage`: chọn dataset → `brief.create` → hiện brief + danh sách version.
- [ ] `features/lineage/LineagePage`: danh sách dataset → lineage (dataset→briefs/dashboards/pipelines) (đọc).

### Commit 11 — Dashboard
- [ ] `features/dashboard/DashboardPage`: chọn dataset → `dashboards.generate` or manual spec → ApexCharts render từ `dashboards.data`.

### Commit 12 — Pipeline
- [ ] `features/pipeline/PipelinePage`: NL mô tả → nhận spec (YAML editor) → `pipelines.preview` → `pipelines.run` → poll `getRun` → history.

### Commit 13 — Lab
- [ ] `features/lab/LabPage`: chọn `analysis_type` + params → `analysis.run` → hiện results (bảng/chart).

> ✅ **Acceptance web**: `pnpm dev:web` chạy; login + 7 screens hoạt động với backend chạy.

---

## 6. `mobile/` UI mobile — pages chi tiết (Commit 14–18)

**Routing (react-router):**
```text
/          → redirect → /login or /brief
/login     → Login (form mobile)
/brief     → Brief (read-first)
/dashboard → Dashboard (ApexCharts responsive)
/lineage   → Lineage
/lab       → Lab (chọn nhanh)
/settings  → Settings (BYOK)
/ingest    → Ingest (tuỳ, upload đơn giản)
/pipeline  → Pipeline (tuỳ, theo dõi đơn giản)
```

### Đặc thù mobile
- `BottomNav` (4–5 mục chính: Brief, Dashboard, Lineage, Lab, Settings).
- `Card` xếp dọc, touch target ≥ 44px, tối ưu đọc (read-first).
- Chart: ApexCharts responsive; KPI nhỏ render bằng CSS (không cần chart lib).

### Commit 14–18
- [ ] 14: scaffold `mobile` (Vite) + theme mobile (`.env.example`, proxy). 
- [ ] 15: `MobileShell` + `BottomNav` + Login.
- [ ] 16: Brief + Dashboard + Lineage (read-first).
- [ ] 17: Lab + Settings.
- [ ] 18: Ingest + Pipeline (đơn giản, nếu cần).

> ✅ **Acceptance mobile**: `pnpm dev:mobile` chạy; dùng chung `shared`; layout/touch chuẩn mobile.

---

## 7. Test & deploy (Commit 19–20)
- [ ] `shared`: `vitest` test `client.ts` (mock fetch), `types` không parse lỗi.
- [ ] `web`/`mobile`: ví dụ component test (Login, Ingest) bằng Vitest + Testing Library.
- [ ] CI: `frontend/` test + build trong GitHub Actions (kèm bước install pnpm).
- [ ] Deploy: nginx `location /app/web` → `web/dist`; `location /app/mobile` → `mobile/dist`;
      `location /` → api `:8000`; cấu hình `cors_origins` chứa domain web/mobile (không `*` + credentials).

---

## 8. Rủi ro & cách xử lý
| Rủi ro | Xử lý |
|---|---|
| CORS khi dev (web gọi `:8000` khác origin) | dùng Vite proxy `/api` hoặc bật `CORS_ALLOW_ALL=true` (không credentials) |
| 401 timeout JWT | client lắng nghe `app:unauthorized` → logout → redirect /login |
| Poll `/runs` spam (rate limit) | backoff: poll 2s → 4s → 8s, dừng khi status khác running |
| Chart bundle (ApexCharts) quá to trên mobile | import `react-apexcharts`/dynamic import để giảm bundle (tree-shake) |
| Xung đột backend CORS mới (`be498fe`) | không dùng credentials; chỉnh `cors_origins` khi deploy |
| OpenAI/Gemini key thiếu | BYOK fallback rule-based (đã có backend); UI chỉ thông báo |

---

## ✅ Definition of Done (trước khi merge mỗi giai đoạn)
- [ ] `pnpm -r typecheck` pass.
- [ ] `pnpm -r build` pass (web & mobile).
- [ ] Test (nếu có) pass.
- [ ] Feature module không import nhau; UI không nhét logic.
- [ ] Chạy được với backend `uvicorn` (login + screen tương ứng).
- [ ] Commit nhỏ có message rõ; đã push `refactor`.