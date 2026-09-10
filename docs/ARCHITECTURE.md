# Architecture — AI Data Engineering Workbench

Repo/project: `dataworkbench`. Local-first workbench:
`Ingest → Pipeline (ETL/ELT) → Brief → Dashboard`, plus Statistics Lab and visual lineage.
Detail history: `docs/plan/02-architecture.md`, `docs/plan/implement_plan.md`.

## 1. System overview

```mermaid
flowchart LR
  subgraph UI["React + Vite (pwa-ready web)"]
    WEB["frontend/web :5173\nDesktop 240px shell"]
    MOB["frontend/mobile :5174\nBottomNav"]
    SH["frontend/shared\napi + hooks + ui + ApexCharts theme"]
  end
  WEB --> SH
  MOB --> SH
  SH -->|HTTP JSON, JWT Bearer| API
  subgraph API["FastAPI :8000 (api.py = thin composition root)"]
    AUTH["routers/auth"]
    DS["routers/datasets"]
    PIPE["routers/pipelines"]
    BR["routers/brief"]
    DASH["routers/dashboards"]
    AN["routers/analysis+lineage"]
    SYS["routers/system"]
  end
  API --> DDB[("DuckDB\nraw.* / mart.*")]
  API --> MDB[("SQLite\nusers/datasets/pipelines/\nruns/steps/briefs/dashboards")]
  API --> LLM["LLM via LangChain\nBYOK per-user key\nretry + timeout, rule fallback"]
```

## 2. Data flow

```mermaid
flowchart TD
  UP["CSV/Excel upload\n(<=50MB, validated)"] --> ING["warehouse/ingest.py\nsanitize table name"]
```

### 2b. Execution engines (scalability)

```mermaid
flowchart TD
  SPEC["PipelineSpec\n(engine: pandas | duckdb)"] --> PLAN["planner.plan()\nvalidate + topo + levels + sink"]
  PLAN --> CTX["ExecutionContext\nnamed frames, explicit inputs"]
  CTX -->|engine=pandas| PE["Pandas Engine\nsmall data, full op catalog"]
  CTX -->|engine=duckdb| DE["DuckDB SQL Engine\nviews chuoi, SQL push-down"]
  DE --> FB{"op dich duoc?"}
  FB -->|co| SQL["SQL view"]
  FB -->|khong| HYB["hybrid fallback\nmaterialize step do"]
```

- Pandas: `fetchdf()` toàn bộ source — ok tới ~100K rows.
- DuckDB: không fetch toàn bộ (chỉ preview LIMIT 5 + COUNT); mỗi op có bản dịch SQL
  (`fill_missing`→COALESCE, `drop_duplicates`→DISTINCT, `aggregate`→GROUP BY...);
  op không dịch được (`derive`/`filter` lạ) fallback hybrid từng step, liệt kê trong `fallbacks`.
- Kết quả trả `engine_used` + `sink` + `levels`.
  ING --> RAW[("raw.table\nDuckDB")]
  RAW --> PROF["profile JSON\n(never raw rows to LLM)"]
  PROF --> SPEC["PipelineSpec\n(DAG validate, 7 pandas ops + sql)"]
  SPEC -->|dry-run 100 rows| PREV["preview"]
  SPEC -->|BackgroundTasks| MART[("mart.table\natomic CREATE OR REPLACE\nwarehouse_write_lock")]
  MART --> BRIEF["brief (versioned)"]
  MART --> DBOARD["dashboard spec\n1 query/chart → ApexCharts JSON"]
  RAW --> PIPE["pipelines"]
  PIPE --> MART
  MART --> DBOARD
```

LLM only ever receives **profile JSON + brief text** (never raw rows).

### 2c. AI production-grade — LLM proposes. Engine validates. Human approves. Executor executes.

```mermaid
flowchart LR
  NL["mo ta tieng Viet"] --> LLM["LLM + structured output\n(Pydantic schema)"]
  LLM --> V1["schema validation"]
  V1 --> V2["semantic validation\n(cot ton tai, engine compat)"]
  V2 --> V3["safety validation\n(mart.* only, SELECT-only)"]
  V3 --> COST["cost estimation\n(rows, engine goi y)"]
  COST --> DRY["auto dry-run 100 rows"]
  DRY --> PROP["ai_proposals\nstatus=proposed"]
  PROP --> HUMAN{"human approve?"}
  HUMAN -->|approve| EXEC["create pipeline\n-> executor"]
  HUMAN -->|reject| END["rejected"]
```

- Loi provider co kieu (`llm_errors.py`): retry `RateLimit/Timeout/Server`, fallback ngay `Auth/InvalidRequest` — khong string-matching.
- Output validate 2 lop: Pydantic schema (`prompts/schemas.py`) + business validation (column ton tai, type ho tro).
- AI khong bao gio execute truc tiep: `POST /pipelines` voi `proposal_id` doi hoi status `approved` (403 neu chua).
- Rate limit: Redis share giua workers (`redis` service trong compose); in-memory chi fallback dev single-worker.

### 2d. Data Contract + reproducibility + observability

- **Contract gate** (`pipeline/contract.py`): spec mang `contract` (min_rows, missing/dup %, kieu/mien gia tri tung cot).
  Gate chay tren bounded sample (10k rows, ke ca engine duckdb) truoc execute — rot la failed kem report.
- **Reproducibility**: `spec_hash` (sha256 canonical) tren proposal + run; pipeline luu `proposal_id`;
  `GET /pipelines/{id}/reproduce` tra snapshot tao + hash + engine; `GET /runs/{id}` tra hash/engine/duration.
- **Observability**: run ghi `started_at/finished_at/rows_out/engine`; `GET /pipelines/{id}/stats`
  (success rate, avg/last duration, engine breakdown, step status); executor tra `step_timings` moi step.

## 3. Backend layout

```
api.py                      # thin root: app, CORS, error handlers, include_router x7
src/api/deps.py             # JWT, Redis/in-memory rate limit, _user_owns_table
src/api/routers/            # auth/datasets/pipelines/brief/dashboards/analysis/system
src/core/database.py        # SQLAlchemy models + session_scope() (commit/rollback)
src/warehouse/              # DuckDB connection (+write lock), ingest, registry, lineage graph
src/pipeline/               # spec_schema (DAG validate), executor, ops (pandas + hardened sql)
src/dashboard/              # spec_schema + renderer (fetch_data 1 query/chart)
src/prompts/                # briefer/etl_author/dashboard_author (profile-only, fallbacks)
src/core/ai_service.py      # LangChain LLM, timeout/retry/backoff, keyed cache, rule fallback
src/utils/                  # security (JWT/CORS), exceptions ({code,message,detail,trace_id}),
                            # validators, logging_config (rotating files)
```

## 4. Metadata schema (SQLite)

```mermaid
erDiagram
  users ||--o{ datasets : owns
  datasets ||--o{ briefs : has
  datasets ||--o{ pipelines : sources
  pipelines ||--o{ pipeline_runs : runs
  pipeline_runs ||--o{ pipeline_steps : logs
  users ||--o{ dashboards : owns
  users ||--o{ pipelines : owns
  users {
    string username PK
    string password_hash
    string api_key_ai_encrypted
  }
  datasets {
    int id PK
    string dataset_name
    string duckdb_table
    text profile_json
    int version
  }
  pipelines {
    string id PK
    string source_target
    text spec_json
    int version
  }
  pipeline_runs {
    string id PK
    string status
    text result_json
  }
  dashboards {
    int id PK
    text spec_json
    int version
  }
```

Versioning: `briefs` version per dataset; `pipelines`/`dashboards` bump `version` on PUT;
`datasets` are immutable per name (`version=1`, foundation for re-ingest versioning).

## 5. Pipeline run lifecycle + concurrency

```mermaid
stateDiagram-v2
  [*] --> queued: POST /pipelines/run
  queued --> running: BackgroundTasks start
  running --> done: execute ok
  running --> failed: step error / lock timeout
  running --> failed: exception
  done --> [*]
  failed --> [*]
```

- One `threading.Lock` per `pipeline_id`: a second run of the **same** pipeline → `409`.
- DuckDB writes serialized by `warehouse_write_lock` (thread RLock + file lock, 30s timeout).
- `api.py` runs single uvicorn worker; multi-worker needs Redis + external queue (documented in Dockerfile).
- Every run writes `pipeline_steps` rows (`done/failed/skipped` + log excerpt); `GET /runs/{id}` returns them.

## 6. Security model

- JWT Bearer (`HS256`, auto dev key in `.jwt_secret` 0600, **required** in production).
- Ownership enforced per row: datasets/pipelines/runs/briefs/dashboards/lineage (`403/404`).
- Table identifiers validated `^(raw|mart)\.[A-Za-z_][A-Za-z0-9_]{0,63}$` + quoted; `sql` op allows only single `SELECT/WITH`, blocks DDL/DML keywords.
- Uploads: extension allowlist, 0-byte reject, 50MB cap, empty-frame reject.
- BYOK keys Fernet-encrypted at rest; per-(provider,key) service cache (no cross-user leak).

## 7. Lineage graph

`GET /lineage/{dataset_id}` returns `{nodes, edges}`:

```mermaid
flowchart LR
  DS[("dataset\nraw.table")] --> B["brief v1..n"]
  DS --> P["pipeline"]
  P --> M[("mart.table")]
  M --> D["dashboard"]
  DS --> D2["dashboard\n(direct source)"]
```

UI (`Lineage.tsx` web+mobile) renders kind-grouped columns with hover edge tooltips.

## 8. Deploy

- Dev: `uvicorn api:app --port 8000` + `pnpm dev:web (:5173)` / `dev:mobile (:5174)`.
- Prod: `docker compose --profile production up --build -d` → `backend :8000` (non-root `appuser`, healthcheck) + `frontend :80` (nginx: web `/`, mobile `/app/mobile/`, `/api/` proxy + rate limits).
- CI (`.github/workflows/ci.yml`): flake8/black/isort + full pytest + frontend typecheck (enforced) + compose validate + backend/frontend image builds with GHA cache.

## 9. Test map

| Suite | Covers |
|---|---|
| `test_e2e.py` | register → ingest → pipeline → dashboard → lineage |
| `test_e2e_stability.py` | error shape, api-key, upload, spec validation, 403s, SQLi, steps, 409, dashboard ownership, versioning, lineage graph |
| `test_api.py` | auth/analysis endpoints (mocked DB fns) |
| `test_llm_retry.py` | LLM retry/success, non-retryable, fallback, keyed cache |
| `test_pipeline/warehouse/security/...` | engine, validators, DB, stats |
