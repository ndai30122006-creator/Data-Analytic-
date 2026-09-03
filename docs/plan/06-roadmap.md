# 06 — Roadmap theo Phase (P0–P5)

Tổng effort ước tính: **6–9 ngày làm thật** (clone + dev + test kèm học).

## 🗺 Tổng quan phase

| Phase | Nội dung | Dependencies | Thứ tự lý do |
|---|---|---|---|
| **P0** Reposition | Gộp tab dư, Settings BYOK, README mới | — | Dọn mặt bằng, không mất engine |
| **P1** Warehouse | DuckDB + ingest + registry + profile | P0 | Mọi feature đứng trên lớp này |
| **P2** Brief | Feature 2 — quick win | P1 | Động lực + dùng được ngay |
| **P3** ETL/ELT | Feature 1 — engine + spec + ops | P1 | Phần DE đậm nhất |
| **P4** Dashboard | Feature 3 — spec + renderer | P1, P3 | Cần data sạch mới đẹp |
| **P5** Polish | Lineage, demo data, tests, README | P2–P4 | Hoàn thiện |

---
## P0 — Reposition · (~½ ngày)

**Mục tiêu:** dọn giao diện, định vị lại, sẵn sàng cho pivot.

- [ ] Thêm Settings screen: nhập AI key (BYOK), chọn provider,
      test connection.
- [ ] Gộp **Statistics + Deep Analysis** → `lab_screen.py` (giữ nguyên
      engine trong `src/core` / `src/analytics`), gộp tab dư (giảm 7 → 4-5).
- [ ] README mới định vị "AI Data Engineering Workbench".
- **✅ Acceptance:** app chạy, 5 screens skeleton hiển thị, BYOK lưu + đọc được.

---
## 1 — Warehouse foundation (~1-2 ngày)

- [ ] `src/warehouse/` (connection, ingest, registry).
- [ ] Ingest CSV/Excel → bảng `raw.<name>` trong DuckDB + schema inference +
      profiling (tái dụng `data_quality.py`).
- [ ] Alembic migration mới: mở rộng `datasets` (thêm `duckdb_table`,
      `profile_json`, `file_path`).
- [ ] UI `ingest_screen.py`: upload → preview 20 rows → confirm.
- [ ] Thêm `duckdb`, `pyyaml` vào deps + tests ingest.
- [ ] Update `.gitignore` (data/, *.duckdb, uploads/).
- **✅ Acceptance:** upload CSV → thấy trong registry; query được qua DuckDB;
  profile hiển thị.
---
## P2 — Feature: AI Brief (~1 ngày) — quick win

- [ ] `src/prompts/briefer.py` — profile JSON → narrative tiếng Việt.
- [ ] Fallback rule-based tái dụng `insights.py`.
- [ ] Alembic: bảng `briefs` (id, dataset_id, version, content, model_used).
- [ ] UI `brief_screen.py` + lưu version + export Markdown.
- **✅ Acceptance:** 1 click → brief + export Markdown; fallback khi không có key.

---
## P3 — Feature: AI ETL / ELT (~2-3 ngày) — phần DE đậm nhất

- [ ] `PipelineSpec` DSL (Pydantic) hỗ trợ DAG (`depends_on`).
- [ ] `executor.py`: topological run, checkpoint/step, dry-run mode,
      ghi `pipeline_runs` + `pipeline_steps`.
- [ ] `ops/`: `pandas_ops` (fill_missing, drop_duplicates, type_cast,
      standardize_columns, derive_column, filter, aggregate) + `sql_ops`
      (ELT mode trên DuckDB views).
- [ ] `prompts/etl_author.py`: NL tiếng Việt → spec + `validators.py`
      reject spec lỗi.
- [ ] UI `pipeline_screen.py`: chat → YAML editor → dry-run → run → history.
- [ ] Alembic: bảng `pipelines`, `pipeline_runs`, `pipeline_steps`.
- **✅ Acceptance:** mô tả yêu cầu → spec → dry-run → run → mart schema;
  rerun không tốn token.

---
## P4 — Feature: AI Dashboard Gen (~1-2 ngày)

- [ ] `dashboard/spec_schema.py` (Pydantic) + `dashboard/renderer.py`
      spec → Plotly (tái dùng theme).
- [ ] `prompts/dashboard.py`: profile + brief → DashboardSpec.
- [ ] Alembic: bảng `dashboards` (spec_json, owner).
- [ ] UI `dashboard_screen.py`: render + edit + save + export PNG/PDF/MD.
- **✅ Acceptance:** sinh dashboard hợp lý từ dataset đã transform, chỉnh &
  lưu được, export được.

---
## P5 — Polish (~1 ngày)

- [ ] Lineage view: dataset → pipelines → dashboards (đọc từ DB).
- [ ] Demo dataset generator (bộ điểm SV có "vấn đề" để demo ETL).
- [ ] Bổ sung tests (giữ coverage ≥45%), cập nhật CI, Dockerfile thêm
      volume data/.
- **✅ Acceptance:** CI xanh, demo chạy mượt, README hoàn chỉnh.

---
## 📐 Git strategy

- Làm trên nhánh chính `refactor` (hiện tại), mỗi phase 1 commit nhỏ +
  commit riêng cho docs này.
- Mỗi PR nhỏ; merge về `main` khi P2 hoàn tất (app đã dùng được Brief).

## ⚠️ Rủi ro & cách xử lý

| Rủi ro | Xử lý |
|---|---|
| AI sinh spec sai | `validators.py` + dry-run bắt buộc |
| DuckDB + Streamlit threads | 1 connection/request, chưa concurrent write |
| LLM key hết quota / lỗi | Fallback rule-based mọi feature |
| Phạm vi quá rộng | Chốt cứng 3 features, không thêm trong giai đoạn 1 |