# 🧠 Dataworkbench — local-first AI Data Engineering Workbench

**Dataworkbench** — `Ingest → Pipeline (ETL/ELT) → Brief → Dashboard`, local-first với **DuckDB** + **BYOK** (Bring Your Own Key), kèm **Statistics Lab**.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)
![React](https://img.shields.io/badge/React-Vite-61DAFB)
![DuckDB](https://img.shields.io/badge/DuckDB-1.5%2B-yellow)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![License](https://img.shields.io/badge/License-MIT-green)

> **Hiện tại (`main`):** UI 8 screens `Overview/Ingest/Pipeline/Brief/Dashboard/Lab/Settings/Lineage` + `Statistics Lab` + BYOK `POST /auth/api-key` + AI proposals (approve gate) + DAG engine 2 chế độ (pandas/duckdb). Xem `docs/ARCHITECTURE.md` (tổng quan) & `docs/plan/README.md`.
> **Kiến trúc tổng quan + sơ đồ dữ liệu:** xem [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## ✨ Tính năng chính (Workbench)

### 📥 Ingest
- Upload CSV/Excel (≤50MB, validate) → `raw.<name>` DuckDB (`data/warehouse.duckdb`), atomic + lock
- Data Table Pro: xem rows thật (phân trang/sort/search), profile JSON (KHÔNG gửi raw cho LLM), quality score
- Registry `datasets` (SQLite) + `GET /datasets/{id}/profile` + demo 1-click `POST /datasets/demo`

### ⚙️ Pipeline (AI ETL/ELT)
- Mô tả tiếng Việt → AI sinh `PipelineSpec` JSON (DAG `depends_on`) → proposal (schema/semantic/safety + cost + dry-run) → human Approve → Create → Run
- 8 ops (`fill_missing`, `drop_duplicates`, `type_cast`, `standardize_columns`, `derive_column`, `filter`, `aggregate`, `merge`) + `sql` ELT `{{prev}}`, DAG editor kéo-thả trên UI
- 2 engines: `pandas` (small data) / `duckdb` (SQL push-down, large data) + DataContract gate + versioning + reproduce hash
- Dry-run 100 rows (không ghi `mart`), Run → `mart.<name>` + history `pipeline_runs/steps` + stats quan sát được

### 📋 Brief (AI)
- 1-click từ profile → narrative tiếng Việt, lưu version, export Markdown
- Fallback `core/insights.py` khi không có key, LLM chỉ nhận profile

### 📊 Dashboard (AI)
- AI đề xuất 4-6 charts `DashboardSpec` (6 types: `kpi/bar/hist/box/line/scatter`)
- Renderer ApexCharts real-data 1 query/chart DuckDB, sắp xếp/ẩn-hiện + save layout, export PNG/SVG/CSV, auto-refresh, versioning

### 🧪 Lab — Statistics Lab
- Chạy qua `POST /analysis/run` → engine `src/core/statistical_tests.py` (t-test, ANOVA, bootstrap, Mann-Whitney, Kruskal, AB-test)
- JSON-serializable (NaN-safe), kiểm tra dataset thuộc user trước khi chạy

### ⚙️ Settings — BYOK
- Chọn provider (`OpenAI/Gemini`) + key → `POST /auth/api-key` (Fernet encrypt at-rest), nút **Test connection** gọi LLM siêu nhẹ báo latency
- Retry typed theo loại lỗi, structured output Pydantic, fallback rule-based khi không key

### 🔗 Lineage
- Graph `dataset → brief/pipeline → mart → dashboard` (`nodes/edges`) từ `warehouse/lineage.py`, vẽ trực quan trên UI
- Demo: `POST /datasets/demo` sinh 120 SV (missing/dup) 1-click, hoặc `scripts/generate_demo_data.py` (300 SV)

## 🚀 Cài đặt

### 1. Clone
```bash
git clone https://github.com/ndai30122006-creator/dataworkbench.git
cd dataworkbench
git checkout main
```

### 2. Venv
```bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows
# source .venv/bin/activate
```

### 3. Deps
```bash
pip install -r requirements/base.txt -r requirements/dev.txt
# base đã có duckdb>=0.10.0, pyyaml>=6.0, fastapi, sqlalchemy, langchain
```

### 4. Chạy dev (2 terminal)
```bash
# Terminal 1 — Backend
.\.venv\Scripts\python.exe -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
# Terminal 2 — Frontend
cd frontend && pnpm install && pnpm dev:web        # → http://localhost:5173
#    Mobile UI: pnpm dev:mobile                    # → http://localhost:5174
```
Mở `http://localhost:5173` (web) / `http://localhost:5174` (mobile) + `http://localhost:8000/docs` (API)

> 📘 **Hướng dẫn đầy đủ chạy local dev UI mới** (cài Node/pnpm, tạo tài khoản đăng nhập, troubleshooting):
> xem [`docs/plan/ui/local-dev.md`](docs/plan/ui/local-dev.md).

### Đăng nhập (demo)
> Chỉ dev. Production `DEMO_MODE=false` + `JWT_SECRET_KEY` mạnh.
```bash
DEMO_ADMIN_USERNAME=admin DEMO_ADMIN_PASSWORD=admin123
DEMO_USER_USERNAME=user DEMO_USER_PASSWORD=user123
```

## 🐳 Docker

```bash
copy .env.example .env
# JWT_SECRET_KEY=python -c "import secrets; print(secrets.token_hex(32))"
docker compose up --build          # dev (web+api)
docker compose --profile production up --build -d  # + nginx 80/443
```
`data/warehouse.duckdb` + `users.db` trong volume `app_data:/app/data` → `docker compose down -v` mới mất.

## 📖 Hướng dẫn sử dụng (Workbench)

1. **Ingest:** `📥 Ingest` → Upload CSV/Excel → Preview 20 → Confirm → `raw` + profile
2. **Pipeline:** `⚙️ Pipeline` → Gõ “điền missing diem bằng median, xóa trùng ma_sv” → Generate Spec → Dry-run → Run → `mart`
3. **Brief:** `📋 Brief` → Chọn dataset → Generate Brief → history version → Export MD
4. **Dashboard:** `📊 Dashboard` → Chọn `mart` → Generate 4-6 charts → Render ApexCharts real-data → Edit JSON → Save → Export
5. **Lab:** `🧪 Lab` → Advanced Stats/Bootstrap/... (t-test, ANOVA, bootstrap via `core`)
6. **Settings:** `⚙️ Settings` → Chọn provider + key → Save (DB encrypt) → Test connection (báo latency)
7. **Lineage:** `🔗 Lineage` → Chọn dataset → xem graph nodes/edges (hover xem quan hệ)

**Frontend 2 bản:**
- `frontend/web` — React+Vite desktop (top navbar pill, 8 routes + Overview, ApexCharts, command palette `Ctrl+K`) — `pnpm --filter @app/web dev` (5173)
- `frontend/mobile` — React+Vite mobile web (BottomNav touch, 8 routes) — `pnpm --filter @app/mobile dev` (5174)
- `frontend/shared` — logic dùng chung `@app/shared` (`api` + `features` + `hooks` + `components`), `vitest` test `client.ts`

## 🏗️ Cấu trúc dự án (mới)

```
dataworkbench/
├── api.py                 # FastAPI — execution layer + BYOK + rate-limit
├── src/
│   ├── warehouse/         # DuckDB local-first (connection, ingest, registry, lineage)
│   ├── pipeline/          # ETL/ELT engine (spec_schema DAG, executor, ops/pandas+sql)
│   ├── dashboard/         # DashboardSpec + renderer (1 query/chart)
│   ├── prompts/           # briefer/etl_author/dashboard_author (profile-only)
│   ├── core/              # database (+session_scope), ai_service/llm_client/llm_errors BYOK, insights, statistical_tests
│   ├── api/               # deps + routers/{auth,datasets,pipelines,brief,dashboards,analysis,system}
│   ├── utils/             # validators, helpers, security, optional_deps
│   └── prompts/           # + schemas.py (structured output), briefer/etl_author/dashboard_author
├── tests/                 # 146 tests (e2e, stability, dag-engine, scale, proposals, review-fixes...)
├── migrations/            # 011 (users→...→ai_proposals→observability→provider)
├── data/                  # warehouse.duckdb (gitignored) + demo_sinhvien.csv
├── docs/plan/             # pivot plan P0-P5 + implement_plan.md
└── requirements/base.txt  # duckdb, pyyaml, fastapi, langchain
```

## 🔌 API Endpoints (Plan 07)

**Datasets:** `POST /datasets/ingest` (file+JSON) | `GET /datasets/{id}/profile` | `GET /datasets` | `DELETE /datasets/{name}`
**Pipelines:** `POST /pipelines` | `GET /pipelines` | `GET /pipelines/{id}` | `POST /pipelines/preview` (dry-run) | `POST /pipelines/run` (BackgroundTasks) | `GET /runs/{id}` | `GET /runs`
**Brief:** `POST /brief/{dataset_id}` | `GET /brief/{id}` | `GET /brief/{id}/{version}`
**Dashboards:** `POST /dashboards` | `GET /dashboards` | `GET/PUT /dashboards/{id}` | `POST /dashboards/{id}/data` | `POST /dashboards/generate`
**Legacy:** `POST /analysis/run` | **Health:** `GET /health` `GET /env/validate` | **Docs:** `/docs` `/redoc`

## 🎨 Theme

Modern dark SaaS — nền `#0A0C10`, accent teal `#2DD4BF` + cyan, Inter + JetBrains Mono, card kính mờ bo 16px, motion (page-enter, stagger, shimmer, hover lift), tôn trọng `prefers-reduced-motion`.

## 🔧 Troubleshooting

```bash
pip install duckdb pyyaml  # warehouse
pytest -q                  # 146 collected
black --check --line-length 120 src/ api.py tests/
```

## 🤝 Contributing

PR welcome — làm trên `main`, mỗi phase 1 commit nhỏ, push thường xuyên, `pytest` xanh, `flake8/black` sạch.

## 📝 License

MIT

## 🙏 Credits

Built with FastAPI, **DuckDB**, React+Vite, ApexCharts, scikit-learn, scipy, statsmodels, pandas, Docker.

---
**🧠 Dataworkbench** — local-first · DuckDB + BYOK · P0-P5 Done (docs/plan)
