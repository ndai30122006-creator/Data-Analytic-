# 🧠 AI Data Engineering Workbench — local-first

**Workbench AI cho Data Engineering** — `Ingest → Pipeline (ETL/ELT) → Brief → Dashboard`, local-first với **DuckDB** + **BYOK** (Bring Your Own Key). Giữ **Statistics Lab** từ “Learning Analytics”.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29%2B-red)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)
![DuckDB](https://img.shields.io/badge/DuckDB-1.5%2B-yellow)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![License](https://img.shields.io/badge/License-MIT-green)

> **Pivot P0-P5 Done (`main` `eba1ed1`):** UI 7 screens `Ingest/Pipeline/Brief/Dashboard/Lab/Settings/Lineage` + `Statistics Lab` + BYOK `POST /auth/api-key`. Xem `docs/plan/README.md` & `docs/plan/implement_plan.md`.

## ✨ Tính năng chính (Workbench)

### 📥 Ingest
- Upload CSV/Excel → `raw.<name>` DuckDB (`data/warehouse.duckdb`)
- Preview 20 rows, profile JSON (KHÔNG gửi raw cho LLM), quality score
- Registry `datasets` (SQLite) + `GET /datasets/{id}/profile`

### ⚙️ Pipeline (AI ETL/ELT)
- Mô tả tiếng Việt → AI sinh `PipelineSpec` YAML (DAG `depends_on`)
- 7 ops `pandas` (`fill_missing`, `drop_duplicates`, `type_cast`, `standardize_columns`, `derive_column`, `filter`, `aggregate`) + `sql` ELT `{{prev}}`
- Dry-run 100 rows (không ghi `mart`), Run → `mart.<name>` + history `pipeline_runs/steps`

### 📋 Brief (AI)
- 1-click từ profile → narrative tiếng Việt, lưu version, export Markdown
- Fallback `core/insights.py` khi không có key, LLM chỉ nhận profile

### 📊 Dashboard (AI)
- AI đề xuất 4-6 charts `DashboardSpec` (6 types: `kpi/bar/hist/box/line/scatter`)
- Renderer Plotly 1 query/chart DuckDB, chỉnh tay, lưu `dashboards` + export JSON

### 🧪 Lab — Statistics Lab
- Gộp `Statistics` + `Deep Analysis` cũ, giữ engine `src/core/statistical_tests.py` + `src/analytics` (8 tabs: Advanced Stats, Bootstrap... Data Quality)
- Via `core` single source, fix `pooled_std`/`eta²`

### ⚙️ Settings — BYOK
- Nhập `OpenAI/Gemini` key → `POST /auth/api-key` (Fernet encrypt at-rest), Test `GET /health`, per-session cache

### 🔗 Lineage
- `Dataset → Pipeline → Dashboard` từ `warehouse/lineage.py` + `scripts/generate_demo_data.py` (300 SV missing/dup/outlier)

## 🚀 Cài đặt

### 1. Clone
```bash
git clone https://github.com/ndai30122006-creator/Data-Analytic-.git
cd Data-Analytic-
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
# base đã có duckdb>=0.10.0, pyyaml>=6.0, streamlit, fastapi, sqlalchemy, langchain
```

### 4. Chạy dev (2 terminal)
```bash
# Terminal 1 — Backend
.\.venv\Scripts\python.exe -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
# Terminal 2 — Frontend
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8501
```
Mở `http://localhost:8501` (frontend) + `http://localhost:8000/docs` (API)

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
docker compose up --build          # dev (8501+8000)
docker compose --profile production up --build -d  # + nginx 80/443
```
`data/warehouse.duckdb` + `users.db` trong volume `app_data:/app/data` → `docker compose down -v` mới mất.

## 📖 Hướng dẫn sử dụng (Workbench)

1. **Ingest:** `📥 Ingest` → Upload CSV/Excel → Preview 20 → Confirm → `raw` + profile
2. **Pipeline:** `⚙️ Pipeline` → Gõ “điền missing diem bằng median, xóa trùng ma_sv” → Generate Spec → Dry-run → Run → `mart`
3. **Brief:** `📋 Brief` → Chọn dataset → Generate Brief → history version → Export MD
4. **Dashboard:** `📊 Dashboard` → Chọn `mart` → Generate 4-6 charts → Render Plotly → Edit JSON → Save → Export
5. **Lab:** `🧪 Lab` → Advanced Stats/Bootstrap/... (t-test, ANOVA, bootstrap via `core`)
6. **Settings:** `⚙️ Settings` → Chọn provider + key → Save (session + DB encrypt) → Test Connection `GET /health`
7. **Lineage:** `🔗 Lineage` → Chọn dataset → xem `table/briefs/dashboards` count

**Frontend 2 bản (GĐ3/GĐ4):**
- `frontend/web` — React+Vite desktop (sidebar 220px, 7 routes, ECharts, proxy `/api` → 8000) — `pnpm --filter @app/web dev` (5173)
- `frontend/mobile` — React+Vite mobile web (BottomNav 44px touch, 6 routes read-first) — `pnpm --filter @app/mobile dev` (5174)
- `frontend/shared` — logic dùng chung `@app/shared` (`api` + `features` + `hooks`), `vitest` test `client.ts`

## 🏗️ Cấu trúc dự án (mới)

```
project1/
├── app.py                 # Streamlit — 7 screens (Ingest/Pipeline/Brief/Dashboard/Lab/Settings/Lineage)
├── api.py                 # FastAPI — execution layer + BYOK + rate-limit
├── src/
│   ├── warehouse/         # DuckDB local-first (connection, ingest, registry, lineage)
│   ├── pipeline/          # ETL/ELT engine (spec_schema DAG, executor, ops/pandas+sql)
│   ├── dashboard/         # DashboardSpec + renderer (1 query/chart)
│   ├── prompts/           # briefer/etl_author/dashboard_author (profile-only)
│   ├── core/              # database (users/datasets/briefs/dashboards/pipelines), ai_service BYOK encrypt, insights, statistical_tests
│   ├── analytics/         # Lab engine (8 tabs, archived 3 heavy)
│   ├── ui/screens/        # 7 screens + theme Glassmorphism (Nunito pill)
│   ├── utils/             # validators, helpers, security
│   └── services/          # report/session (legacy)
├── tests/                 # 102 tests (warehouse, pipeline, briefer, api, db, stats)
├── migrations/            # 007_* (users→datasets→warehouse→briefs→dashboards→pipelines)
├── data/                  # warehouse.duckdb (gitignored) + demo_sinhvien.csv
├── docs/plan/             # pivot plan P0-P5 + implement_plan.md
└── requirements/base.txt  # duckdb, pyyaml, streamlit, fastapi, langchain
```

## 🔌 API Endpoints (Plan 07)

**Datasets:** `POST /datasets/ingest` (file+JSON) | `GET /datasets/{id}/profile` | `GET /datasets` | `DELETE /datasets/{name}`
**Pipelines:** `POST /pipelines` | `GET /pipelines` | `GET /pipelines/{id}` | `POST /pipelines/preview` (dry-run) | `POST /pipelines/run` (BackgroundTasks) | `GET /runs/{id}` | `GET /runs`
**Brief:** `POST /brief/{dataset_id}` | `GET /brief/{id}` | `GET /brief/{id}/{version}`
**Dashboards:** `POST /dashboards` | `GET /dashboards` | `GET/PUT /dashboards/{id}` | `POST /dashboards/{id}/data` | `POST /dashboards/generate`
**Legacy:** `POST /analysis/run` | **Health:** `GET /health` `GET /env/validate` | **Docs:** `/docs` `/redoc`

## 🎨 Theme

Glassmorphism Aurora — `Bg #0A0A1A` aurora `blur(16px)`, `Nunito/Quicksand/Varela Round` pill `999px`, `radius 24px`, `Outfit` → `Nunito` tròn hơn theo yêu cầu.

## 🔧 Troubleshooting

```bash
pip install duckdb pyyaml  # warehouse
pytest -q                  # 102 passed
black --check --line-length 120 .
```

## 🤝 Contributing

PR welcome — làm trên `refactor`, mỗi phase 1 commit nhỏ, push thường xuyên, `pytest` xanh, `flake8/black` sạch.

## 📝 License

MIT

## 🙏 Credits

Built with Streamlit, FastAPI, **DuckDB**, Plotly, scikit-learn, scipy, statsmodels, pandas, Docker.

---
**🧠 AI Data Engineering Workbench** — local-first · DuckDB + BYOK · P0-P5 Done (docs/plan)
