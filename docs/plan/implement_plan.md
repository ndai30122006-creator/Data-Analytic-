# 🛠 IMPLEMENTATION PLAN — Hướng dẫn triển khai

> **Lưu ý 09/2026:** P0-P5 ban đầu cho Streamlit (`app.py` + `src/ui/screens`), đã hoàn tất và **đã thay bằng React** `frontend/web+mobile` (`87337f5` xóa Streamlit). Các bước dưới giữ lại để tham khảo lịch sử; dev mới xem `docs/plan/ui/plan.md` (React 20 commits) + `docs/plan/ui/local-dev.md`.
>
> Đây là bản **cầm tay chỉ việc** (implementation guide) để thực thi các kế
> hoạch trong `docs/plan/`. Đọc theo thứ tự: bắt đầu từ đây, tham chiếu các
> file `0X-*.md` khi cần chi tiết lý thuyết.
>
> 🔗 Bạn đọc song song: `02-architecture.md` (kiến trúc), `06-roadmap.md`
> (phase & acceptance), `03/04/05-feature-*.md` (từng feature),
> `07-api-design.md` (API).

---

## 🧭 Nguyên tắc làm việc

1. **Commit nhỏ & push thường xuyên** — mỗi thay đổi có nghĩa = 1 commit,
   push lên `refactor` ngay.
2. **Tận dụng code có sẵn** — đừng viết lại: kiểm tra `src/core`,
   `src/analytics`, `src/utils` trước khi xây cái mới.
3. **Test theo từng bước** — `pytest` chạy sau mỗi phần, giữ coverage ≥45%.
4. **LLM = authoring, không runtime** — AI sinh spec; mọi lần chạy sau
   deterministic, không tốn token.
5. **LLM chỉ nhận profile** — không bao giờ gửi raw data cho LLM.

---

## Tổng quan không gian làm việc

- **Nhánh:** `refactor` (đang ở đây).
- **Môi trường:** venv riêng, cài deps:
  ```bash
  python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements/base.txt -r requirements/dev.txt
  ```
- **Chạy dev:**
  ```bash
  uvicorn api:app --reload --port 8000   # backend
  cd frontend && pnpm install && pnpm dev:web   # frontend React 5173 (mobile: pnpm dev:mobile 5174)
  ```
- **Kiểm tra:** `pytest -q` · **lint:** `flake8` · **format:** `black .` (đã bỏ Streamlit `app.py` `87337f5`)

---

## ✅ PHASE 0 — Reposition (≈½ ngày)

Mục tiêu: dọn giao diện, định vị lại, thêm Settings BYOK. Chi tiết: `06-roadmap.md`.

### Việc cần làm (chia commit nhỏ)

1. **Commit 1 — cấu trúc UI screens**
   - Tạo `src/ui/screens/__init__.py`.
   - Tạo `src/ui/screens/ingest_screen.py`, `pipeline_screen.py`,
     `brief_screen.py`, `dashboard_screen.py` với hàm `render_xxx(*args)`
     trả "skeleton" (tiêu đề + placeholder) để app không crash.
   - Tạo `src/ui/screens/lab_screen.py` — **gộp Statistics + Deep Analysis**:
     import lại từ `src/core/analytics_engine` và `src/ui/tabs/statistics`.

2. **Commit 2 — cập nhật app.py routing**
   - Thay `MAIN_TABS` cũ (7 tabs) bằng 5 screens: Ingest, Pipeline, Brief,
     Dashboard, Lab.
   - Giữ `render_theme`, `render_sidebar`, command palette Ctrl+K.

3. **Commit 3 — Settings BYOK**
   - Dùng endpoint có sẵn `POST /auth/api-key` → lưu key.
   - Settings screen: nhập key, chọn provider (openai/gemini), nút
     "Test connection" gọi `GET /health` hoặc `/env/validate`.
   - Server-side: `UPDATE users SET api_key_ai = ?` — thêm encrypt trước
     khi lưu (nếu muốn, phase sau).

4. **Commit 4 — README reposition**
   - Cập nhật README định vị "AI Data Engineering Workbench", giữ phần
     Statistics engine làm "Statistics Lab".

---

## ✅ PHASE 1 — Warehouse foundation (1–2 ngày)

Mục tiêu: DuckDB + ingestion + registry + profiling. Chi tiết:
`02-architecture.md`, `04-feature-elt.md` (nguồn profile).

### Bước 1 — dependency & gitignore (commit)

- Thêm vào `requirements/base.txt`: `duckdb>=0.10.0`, `pyyaml>=6.0`.
- Thêm vào `.gitignore`:
  ```
  data/
  *.duckdb
  data/uploads/
  ```
- `pip install duckdb pyyaml` + commit.

### Bước 2 — `src/warehouse/connection.py` (commit)

```python
import duckdb, os
from pathlib import Path

DATA_DIR = Path("data"); DATA_DIR.mkdir(exist_ok=True)
_DB_PATH = DATA_DIR / "warehouse.duckdb"

def get_conn() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(_DB_PATH))
```

### Bước 3 — `src/warehouse/registry.py` (commit)

- Khai báo `Dataset` metadata mở rộng: `duckdb_table`, `profile_json`,
  `file_path` (thêm cột qua Alembic migration mới `003_*`).
- Helper: `register_dataset(user, name, table)`, `list_datasets(user)`,
  `get_profile(dataset_id)`.

### Bước 4 — Alembic migration 003 (commit)

- Copy `migrations/versions/002_datasets.py` → `003_warehouse.py`, thêm 3 cột
  mới vào bảng `datasets`.
- Chạy `alembic upgrade head` kiểm tra.

### Bước 5 — `src/warehouse/ingest.py` (commit)

- `ingest_file(user, file)`: đọc CSV/Excel → `raw.<name>` trong DuckDB.
- Schema inference + profiling: tái dụng **`src/analytics/data_quality.py`**
  và `src/core/insights.generate_data_summary` để tạo `profile_json`.
- Lưu metadata vào SQLite qua registry.

### Bước 6 — API /datasets/ingest (commit)

- Thêm endpoint `POST /datasets/ingest` (auth + rate-limit) gọi ingest.
- `GET /datasets/{id}/profile` trả profile (KHÔNG lộ raw data).

### Bước 7 — `ingest_screen.py` hoàn thiện + tests (commit)

- Upload → preview 20 rows → confirm ingest.
- Tests: `tests/test_warehouse.py` (ingest 1 CSV nhỏ, đọc lại qua DuckDB).

**✅ Checkpoint:** upload CSV → thấy trong registry; `SELECT * FROM raw.x`
qua DuckDB; profile hiển thị; `pytest` xanh.

---

## ✅ PHASE 2 — Feature: AI Brief (≈1 ngày) — quick win

Chi tiết: `03-feature-brief.md`.

### Bước 1 — `src/prompts/__init__.py` + `briefer.py` (commit)

```python
# src/prompts/briefer.py
SYSTEM = "Bạn là trợ lý phân tích dữ liệu. Dựa vào profile JSON, viết brief tiếng Việt ngắn gọn."

def build_prompt(profile: dict) -> list[dict]:
    return [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"profile:\n{profile}\n→ brief:..."}]
```

### Bước 2 — AI gateway reuse + fallback (commit)

- Tái dụng `src/core/ai_service.AIService` (đã hỗ trợ openai/gemini +
  rule-based fallback).
- `briefer.generate_brief(dataset_id)`:
  1. Lấy profile từ registry.
  2. Nếu có key (BYOK từ `users.api_key_ai`) → gọi LLM với prompt briefer.
  3. Không có key → dùng `src/core/insights.generate_data_summary`.

### Bước 3 — Alembic 004 + API /brief (commit)

- Bảng `briefs`: id, dataset_id, version, content, model_used, created_at.
- API: `POST /brief/{id}`, `GET /brief/{id}`, `GET /brief/{id}/{version}`.

### Bước 4 — `brief_screen.py` hoàn thiện + export (commit)

- 1-click → brief; lưu version; export Markdown (tái dụng `report_service`).
- Tests cho briefer (mock AI + fallback).

**✅ Checkpoint:** click → brief hiển thị; không key vẫn chạy (rule-based);
export MD được.
---

## ✅ PHASE 3 — Feature: AI ETL / ELT (2–3 ngày) — phần DE đậm nhất

Chi tiết: `04-feature-elt.md`, `07-api-design.md`.

### Bước 1 — `src/pipeline/spec_schema.py` (commit)

- Pydantic `PipelineSpec`, `PipelineStep` (id, op, params, depends_on).
- Validate DAG: không chu kỳ, đủ dependent, op nằm trong registry ops.

### Bước 2 — `src/pipeline/ops/` (commit)

- `pandas_ops.py`: `fill_missing`, `drop_duplicates`, `type_cast`,
  `standardize_columns`, `derive_column`, `filter`, `aggregate`.
- `sql_ops.py`: op `sql` chạy query trên DuckDB (dùng `{{prev}}` placeholder).
- `registry.py` trong pipeline: `OPS = {"fill_missing": ..., ...}` để LLM biết.

### Bước 3 — `src/pipeline/executor.py` (commit)

- `execute(spec, sample=False)`:
  - Topological sort theo `depends_on`.
  - Từng step: chạy op → ghi checkpoint (parquet tạm hoặc DuckDB stage).
  - `sample=True` → giới hạn 100 rows (dry-run), không ghi đè mart.
- Ghi `pipeline_runs` (status, error, timestamps) + `pipeline_steps` log.

### Bước 4 — `src/prompts/etl_author.py` + `validators.py` (commit)

- Author: gửi cho LLM **OPERATIONS CATALOG** + schema columns → NL → spec.
- Validators: reject op lạ, params sai, column không tồn tại → trả lỗi rõ.

### Bước 5 — Alembic 005 + API pipelines (commit)

- Bảng `pipelines`, `pipeline_runs`, `pipeline_steps`.
- API: `POST /pipelines`, `GET /pipelines`, `GET /pipelines/{id}`,
  `POST /pipelines/preview`, `POST /pipelines/run`, `GET /runs/{id}`, `GET /runs`.
- `run` dùng **BackgroundTasks** → trả `run_id` ngay; Streamlit poll `/runs/{id}`.

### Bước 6 — `pipeline_screen.py` hoàn thiện (commit)

- Chat (nhập NL) → hiện spec YAML editor → dry-run button → run → history
  (status + từng step log).

### Bước 7 — tests (commit)

- `tests/test_pipeline.py`: DAG topo, fill_missing/dedup hoạt động,
  dry-run không ghi đè, validators bắt lỗi.

**✅ Checkpoint:** gõ tiếng Việt → spec → dry-run → run → mart schema;
rerun deterministic không tốn token; history + lineage hiển thị.

---

## ✅ PHASE 4 — Feature: AI Dashboard Gen (1–2 ngày)

Chi tiết: `05-feature-dashboard.md`.

### Bước 1 — `src/dashboard/spec_schema.py` (commit)

- Pydantic `ChartSpec`, `DashboardSpec` (type, source, x, y, agg, filters...).

### Bước 2 — `src/dashboard/renderer.py` (commit)

- `render(spec) -> fig`: map chart type → plotly (kpi, bar, line, scatter,
  hist, box). Tái dụng `src/ui/theme.py` cho styling.
- `fetch_data(chart, conn)`: 1 query trên DuckDB cho mỗi chart.

### Bước 3 — `src/prompts/dashboard_author.py` (commit)

- Input: profile + brief → đề xuất 4–6 charts hợp lý dưới dạng
  `DashboardSpec`.
- Validator: chỉ cho phép type đã hỗ trợ, column tồn tại.

### Bước 4 — Alembic 006 + API dashboards (commit)

- Bảng `dashboards` (spec_json, owner).
- API: `POST/GET /dashboards`, `GET/PUT /dashboards/{id}`,
  `POST /dashboards/{id}/data`, `POST /dashboards/generate`.

### Bước 5 — `dashboard_screen.py` + export (commit)

- Render spec, chỉnh tay (thêm/bớt/đổi type), lưu layout.
- Export: PNG/PDF/Markdown (tái dụng `report_service`).

**✅ Checkpoint:** sinh dashboard từ dataset đã transform; chỉnh & lưu được;
export được.
---

## ✅ PHASE 5 — Polish (≈1 ngày)

- **Commit 1 — lineage:** view dataset → pipelines → dashboards (query DB).
- **Commit 2 — demo data:** generator bộ điểm SV có "vấn đề" (missing,
  duplicate, outlier) → `scripts/generate_demo_data.py`.
- **Commit 3 — tests & CI:** thêm tests mới, giữ coverage ≥45%; cập nhật
  CI workflow nếu cần install duckdb; Dockerfile thêm volume `data/`.
- **Commit 4 — README hoàn chỉnh** + hướng dẫn từng feature.

---

## 📦 Checklist tổng trước khi merge về `main`

- [ ] 5 screens hoạt động; app chạy bằng `uvicorn` + `streamlit`.
- [ ] BYOK: nhập key OpenAI/Gemini → dùng được; không key → fallback rule.
- [ ] 3 features đúng theo `03/04/05-feature-*.md` acceptance.
- [ ] `pytest -q` xanh, coverage ≥45%.
- [ ] `flake8` + `black` sạch.
- [ ] DuckDB data nằm trong `data/` (gitignored).
- [ ] Docs `docs/plan/` cập nhật đúng với implement thực tế.
- [ ] Commit & push từng bước lên `refactor`, tạo PR → `main`.

---

## 🧯 Xử lý lỗi thường gặp

- **DuckDB + Streamlit cạnh tranh thread:** mở connection mới trong mỗi
  request/step (`get_conn()` mỗi lần), không giữ global conn dài.
- **AI sinh spec sai:** luôn chạy `validators` + bắt buộc dry-run trước run.
- **LLM key hết quota:** fallback rule-based; log `model_used` để biết.
- **Coverage giảm:** thêm test cho module mới trước khi qua phase khác.
- **Import cycle core↔ui:** logic nằm `src/core`/`src/pipeline`/`src/dashboard`;
  `src/ui` CHỈ gọi qua API, không import core trực tiếp cho execution.
**✅ Checkpoint:** app chạy được 5 screens; nhập key lưu + đọc lại được.