# 🚀 Hướng dẫn chạy Local Dev (Backend + Frontend Web/Mobile)

> Tài liệu này cho phép **máy bất kỳ** clone repo về và chạy đủ stack: FastAPI backend (port 8000) + 2 UI React/Vite (web 5173, mobile 5174).
> Ngày tạo: 2026-09-04 · Phiên bản commit: `5994961` (fix vite alias double-src)

---

## 0. Yêu cầu môi trường

| Công cụ | Phiên bản tối thiểu | Kiểm tra |
|---|---|---|
| Python | 3.10+ (đã test 3.12) | `python3 --version` |
| Node.js | 20+ (đã test v24.19.0) | `node -v` |
| pnpm | 9+ (đã test 11.21.0) | `pnpm -v` (chưa có: `corepack enable` hoặc `npm i -g pnpm`) |

> ⚠️ Redis **không bắt buộc** cho dev: backend fallback về rate-limit in-memory. Warning `Redis rate limit check failed` trong log là **vô hại**.

---

## 1. Clone + chuẩn bị

```bash
git clone https://github.com/ndai30122006-creator/Data-Analytic-.git
cd Data-Analytic-
git checkout main          # nhánh main đã chứa UI mới + fix mới nhất
```

## 2. Backend (FastAPI) — Terminal 1

### 2.1 Tạo venv + cài deps

```bash
python3 -m venv .venv
source .venv/bin/activate              # Linux/macOS
# Windows: .\.venv\Scripts\activate

pip install -r requirements/base.txt -r requirements/dev.txt
```

> `requirements/base.txt` đã đủ (`python-multipart`, `bcrypt`, `duckdb`, `PyJWT`...). Nếu Windows không có sẵn `python3-venv`/build tool, dùng Python từ python.org (có sẵn pip/venv).

### 2.2 (Tùy chọn) file `.env` cho backend

Backend đọc biến môi trường qua `python-dotenv`. Không bắt buộc với dev cơ bản:

```bash
# .env (tùy chọn)
CORS_ALLOW_ALL=false        # true chỉ khi cần test CORS wildcard (chỉ dev)
JWT_SECRET_KEY=<chuỗi-ngẫu-nhiên>   # dev có thể bỏ qua, prod BẮT BUỘC
```

### 2.3 Chạy backend

```bash
python3 -m uvicorn api:app --reload --port 8000
```

Kiểm tra: `curl http://localhost:8000/health` → `{"status":"healthy"}`

## 3. Frontend — Terminal 2

```bash
cd frontend
pnpm install            # lần đầu, tạo node_modules + pnpm-lock.yaml
```

> Nếu pnpm hỏi approve build scripts (`esbuild`): chọn allow. Repo đã khai báo `allowBuilds.esbuild: true` trong `pnpm-workspace.yaml` nên thường không hỏi.

### 3.1 Chạy Web UI (desktop)

```bash
pnpm dev:web            # → http://localhost:5173
```

### 3.2 Chạy Mobile UI (tùy chọn, terminal 3)

```bash
pnpm dev:mobile         # → http://localhost:5174
```

### 3.3 File env frontend (tùy chọn)

```bash
# frontend/.env (đã có .env.example, mặc định đúng cho local)
VITE_API_BASE=http://localhost:8000
```

- Client HTTP gọi **thẳng** `VITE_API_BASE` (CORS đã mở sẵn 5173/5174 trong `src/utils/security.py`).
- Đồng thời Vite có **proxy `/api` → :8000** (rewrite bỏ prefix) — request từ UI dùng đường nào cũng hoạt động.

## 4. Tạo tài khoản + đăng nhập

API **không có sẵn user** — chọn 1 trong 2 cách:

**Cách A — đăng ký qua API (một lần):**
```bash
# Đăng ký (một lần)
curl -X POST http://localhost:8000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"username":"dev","password":"dev123"}'

# Đăng nhập → trả về {access_token, expires_in...}
curl -X POST http://localhost:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"dev","password":"dev123"}'
```

**Cách B — bật chế độ demo** (tự tạo `admin/admin123` + `user/user123` khi backend start):
```bash
DEMO_MODE=true python3 -m uvicorn api:app --reload --port 8000
```

Sau đó mở UI (`http://localhost:5173`) và đăng nhập bằng tài khoản vừa tạo.

| Trang | Đường dẫn web | Ghi chú |
|---|---|---|
| Login | `/login` | lấy JWT, lưu localStorage |
| Ingest | `/ingest` | upload CSV/Excel (`file` multipart) |
| Pipeline | `/pipeline` | ETL/ELT async → poll runs |
| Brief | `/brief` | AI narrative (BYOK trong Settings) |
| Dashboard | `/dashboard` | ECharts |
| Lab | `/lab` | Statistics Lab |
| Lineage | `/lineage` | dataset → pipeline → dashboard |
| Settings | `/settings` | BYOK API key (`/auth/api-key`) |

## 5. Lệnh hữu ích (trong `frontend/`)

```bash
pnpm -r typecheck                    # TypeScript toàn workspace
pnpm --filter @app/shared test       # unit test shared (vitest)
pnpm build                           # build prod cả 3 package
pnpm dev:web                         # web 5173
pnpm dev:mobile                      # mobile 5174
```

Backend tests: `pytest tests/` (đang ở venv backend).

## 6. Sự cố thường gặp (Troubleshooting)

| Triệu chứng | Nguyên nhân | Cách xử lý |
|---|---|---|
| `Failed to resolve import "@app/shared/..."` khi mở trang | alias Vite thiếu/đúp `src` | Đã fix ở `5994961` — đảm bảo đang ở commit ≥ `5994961`, restart `pnpm dev:web` |
| `ERR_PNPM_IGNORED_BUILDS esbuild` / vite không chạy | pnpm 10/11 chặn postinstall | Kiểm tra `frontend/pnpm-workspace.yaml` có `allowBuilds: esbuild: true`, chạy lại `pnpm install` |
| Browser chặn request (CORS error console) | origin 5173/5174 chưa nằm trong allowlist | Đã fix trong `src/utils/security.py` (commit `eaa4e63`); hoặc set `CORS_ALLOW_ALL=true` (dev only) |
| 401 khi đăng nhập | user chưa đăng ký | Gọi `POST /auth/register` như mục 4 |
| `ModuleNotFoundError: bcrypt`... khi start API | quên venv/deps | `source .venv/bin/activate && pip install -r requirements/base.txt` |
| Port bị chiếm (5173 bận) | đang có vite khác chạy | Vite tự chuyển `5174/5175`; hoặc `pkill -f vite` rồi chạy lại |
| `Redis rate limit check failed` trong log | không có Redis local | Bỏ qua — fallback in-memory |

## 7. Kiến trúc dev nhanh

```
[Browser] ──:5173 web / :5174 mobile (Vite dev, HMR)
    │  fetch VITE_API_BASE (CORS allowed)   hoặc   /api/* (Vite proxy → rewrite)
    ▼
[FastAPI :8000]  api.py ── src/core (SQLite), src/warehouse (DuckDB), AI gateway (BYOK)
```

- `frontend/shared` — api client + features + hooks, dùng chung web/mobile
- `frontend/web` — DesktopShell + 8 pages
- `frontend/mobile` — MobileShell (BottomNav) + 8 pages
- UI chi tiết kiến trúc: `docs/plan/ui/plan.md`, contract API: `docs/plan/ui/tasks.md`
