# 02 — Kiến trúc mục tiêu

## 🏗 Sơ đồ kiến trúc

```
┌──────────────── React UI (web 5173 + mobile 5174) ─────────────────┐
│  📥 Ingest   ⚙️ Pipeline   📋 Brief   📊 Dashboard   🧪 Lab          │
│  (frontend/web + mobile via shared/api)                             │
└────────────────────────┬────────────────────────────────────────────┘
                         │ HTTP (JSON) JWT + BYOK
                         ▼
┌──────────────────────── FastAPI (execution layer) ─────────────────┐
│  /datasets/*   /pipelines/*   /runs/*   /brief/*           │
│  /dashboards/*  /settings/api-key      + AI Gateway (BYOK) │
└──────┬───────────────────┬──────────────────┬──────────────┘
       ▼                   ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────────────┐
│  DuckDB       │   │ Pipeline     │   │ AI / prompts /       │
│  warehouse    │   │ engine       │   │ validators           │
│  (raw + mart) │   │ (spec→DAG)   │   │ (LLM authoring)      │
└──────────────┘   └──────┬───────┘   └──────────────────────┘
                          ▼
              SQLite/SQLAlchemy/Alembic (metadata)
              users, datasets, pipelines, runs, briefs, dashboards
```

## 📁 Cấu trúc thư mục mới (thêm vào `src/` hiện tại)

```
src/
├── warehouse/                # P1 — DuckDB layer
│   ├── connection.py         #   quản lý DuckDB con, path config
│   ├── ingest.py             #   CSV/Excel → raw schema, profiling
│   └── registry.py           #   datasets catalog (SQLite meta + DuckDB data)
├── pipeline/                 # P3 — ETL/ELT engine
│   ├── spec_schema.py        #   Pydantic models cho PipelineSpec (YAML)
│   ├── executor.py           #   chạy DAG: load → steps → checkpoints
│   ├── ops/
│   │   ├── pandas_ops.py     #   fill_missing, dedupe, type_cast, derive...
│   │   └── sql_ops.py        #   ELT mode: SQL trên DuckDB views
│   └── history.py            #   run history + lineage (đọc từ SQLite)
├── dashboard/                # P4 — chart spec renderer
│   ├── spec_schema.py        #   ChartSpec / DashboardSpec (Pydantic)
│   └── renderer.py           #   spec → plotly figure (tái dùng theme)
├── prompts/                  # nâng cấp từ core/ai_service.py
│   ├── briefer.py            #   profile → narrative brief
│   ├── etl_author.py         #   NL → PipelineSpec
│   └── dashboard_author.py   #   NL → DashboardSpec
└── frontend/                 # 09/2026 React Vite (thay src/ui cũ đã xóa)
    ├── shared/               #   api + features + hooks + ui (Button/Card)
    ├── web/                  #   7 routes Ingest/Pipeline/Brief/Dashboard/Lab/Settings/Lineage (5173)
    └── mobile/               #   BottomNav read-first (5174)
```

## 💾 Data layout (local, gitignored)

```
data/
├── warehouse.duckdb         # DuckDB raw + mart schemas
├── uploads/                 # file gốc người dùng (gitignored)
└── specs/                   # pipeline & dashboard YAML/JSON
```

Thêm `data/` và `*.duckdb` vào `.gitignore`.

## 🔑 Nguyên tắc kiến trúc

1. **LLM authoring ≠ runtime**: AI sinh spec một lần; mọi lần chạy sau là
   deterministic, reproducible, không tốn token.
2. **FastAPI là execution layer duy nhất**: React (web/mobile) không gọi trực tiếp
   DuckDB/executor; mọi thứ qua API `shared/api` → tách UI khỏi logic, học API design.
3. **LLM chỉ nhận profile, không nhận raw data**.
4. **BYOK gateway**: key AI lấy từ `users.api_key_ai`, lưu encrypted trong
   `.env` / DB; fallback rule-based nếu không có key.
5. **Metadata trong SQLite, dữ liệu lớn trong DuckDB**: hai vai trò rõ ràng,
   tận dụng Alembic cho schema metadata.

## 🐺 Dependencies mới cần thêm vào `requirements/base.txt`

- `duckdb>=0.10.0` — warehouse nhúng, đọc CSV/Parquet, SQL analytics
- `pyyaml>=6.0` — serialization PipelineSpec / DashboardSpec
- `pydantic>=2.0` — đã có, dùng cho spec schemas
- (giữ) `langchain`, `langchain-openai`, `langchain-google-genai` — AI gateway