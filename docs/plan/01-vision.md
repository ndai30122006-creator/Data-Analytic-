# 01 — Tầm nhìn, Mục tiêu & Phạm vi

## 🧭 Tầm nhìn

Biến một "Learning Analytics app" hiện có thành **AI Data Engineering
Workbench** — một công cụ local chạy trên máy cá nhân, nơi:

- Người dùng upload dữ liệu (CSV / Excel).
- **AI hỗ trợ toàn bộ vòng đời**: làm sạch / chuyển đổi (ETL/ELT),
  tóm tắt & hiểu dữ liệu (Brief), và trực quan hóa (Dashboard).
- Mọi bước dùng **key AI của chính người dùng** (BYOK), không cần dịch vụ
  ngoài.

## 🎯 Mục tiêu cá nhân (vì sao làm dự án này)

1. **Học data engineering thực hành**: ingestion, warehouse modeling,
   DAG orchestration, data quality gates, lineage, spec-driven pipeline.
2. **Học AI integration thực tế**: LLM orchestration, prompting, guardrails,
   BYOK gateway, fallback rule-based.
3. **Học API / backend design**: FastAPI làm execution layer, async jobs,
   streaming, REST API grouping.
4. **Có một sản phẩm demo đầy đủ** để giới thiệu, không phải toy demo.

## ✂️ Phạm vi (in scope)

### 3 Feature trọng tâm

1. **Feature 2 — AI Brief dữ liệu** (làm trước, quick win):
   - 1-click tổng kết dataset: nó là gì, chất lượng, vấn đề, đề xuất.
   - Lưu brief theo version, export Markdown.
   - Fallback rule-based khi không có key AI.

2. **Feature 1 — AI ETL / ELT** (phần data engineering đậm nhất):
   - Mô tả bằng tiếng Việt tự nhiên → AI sinh **PipelineSpec (YAML/JSON)**.
   - Review spec (dry-run trên sample) → chạy → xem history & lineage.
   - Hai mode: **ETL** (pandas ops) và **ELT** (SQL trên DuckDB views).

3. **Feature 3 — AI Dashboard Gen**:
   - AI đề xuất bộ chart dưới dạng **DashboardSpec (JSON)**.
   - Renderer spec → Plotly, sửa tay được, lưu / export layout.

### Ngoài phạm vi (out of scope — giai đoạn một)

- Multi-tenant production deployment.
- Xử lý dữ liệu khổng lồ (Big Data / distributed).
- Thay thế hoàn toàn database hiện có; SQLite/SQLAlchemy/Alembic giữ cho
  metadata.
- ~~Giao diện thuần HTML/JS bên ngoài Streamlit~~ → **Đã làm 09/2026: React Vite `frontend/web (5173)` + `mobile (5174)` thay Streamlit (xóa `app.py` `87337f5`).**

## 🔁 Mối quan hệ với code hiện tại

| Code hiện có | Vai trò mới |
|---|---|
| `src/analytics/*` (statistical engine) | Trở thành **Statistics Lab** (giữ nguyên, gộp UI) |
| `src/core/database.py` + Alembic | Metadata store (users, datasets, pipelines, runs, briefs, dashboards) |
| `src/core/ai_service.py` | Nâng cấp → **AI Gateway** hỗ trợ BYOK |
| FastAPI `api.py` | **Execution layer** (job runner + API) |
| Streamlit UI (cũ, đã xóa `87337f5`) | **Đã thay bằng React** `frontend/web` + `mobile` (7 routes) + Statistics Lab (`Lab` page `POST /analysis/run`) |