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
## P0 — Reposition · (~½ ngày) ✅ Done `refactor` `3dfde5c` (4 commits)

**Mục tiêu:** dọn giao diện, định vị lại, sẵn sàng cho pivot.

- [x] Thêm Settings screen: nhập AI key (BYOK), chọn provider, test connection. → `src/ui/screens/settings_screen.py:1` (BYOK `POST /auth/api-key`, `GET /health`)
- [x] Gộp **Statistics + Deep Analysis** → `lab_screen.py` (giữ nguyên engine trong `src/core` / `src/analytics`), gộp tab dư (giảm 7 → 6: Ingest/Pipeline/Brief/Dashboard/Lab+Settings).
- [x] README mới định vị "AI Data Engineering Workbench". → `README.md:1`
- **✅ Acceptance:** app chạy (`http://localhost:8501` `refactor` `bcf9377` → `93a0f85`), 5 screens skeleton hiển thị (`src/ui/screens/*`), BYOK lưu + đọc được (`st.session_state` + DB `users.api_key_ai`).

---
## P1 — Warehouse foundation (~1-2 ngày) ✅ Done `78888af`

- [x] `src/warehouse/` (connection `get_conn()` per request, ingest `raw.<name>`, registry `register_dataset`).
- [x] Ingest CSV/Excel → bảng `raw.<name>` trong DuckDB + schema inference + profiling (tái dụng `data_quality.py` + `core/insights`).
- [x] Alembic migration `003_warehouse.py` mở rộng `datasets` (`duckdb_table`, `profile_json`, `file_path`) + model `database.py:54`.
- [x] UI `ingest_screen.py`: upload → preview 20 rows → confirm.
- [x] Thêm `duckdb>=0.10.0`, `pyyaml>=6.0` vào `requirements/base.txt` + `.gitignore` `data/*.duckdb`.
- **✅ Acceptance:** upload CSV → registry; query DuckDB; profile `insights` hiển thị — skeleton `78888af`.
---
## P2 — Feature: AI Brief (~1 ngày) — quick win ✅ Done `a5011a3`

- [x] `src/prompts/briefer.py` — `SYSTEM` profile JSON → narrative tiếng Việt + `generate_brief_fallback`.
- [x] Fallback rule-based tái dụng `core/insights.py`.
- [x] Alembic `004_briefs.py` bảng `briefs` (id, dataset_id, version, content, model_used).
- [x] UI `brief_screen.py` + lưu version `Brief version` + export Markdown + profile preview verify `LLM chỉ nhận profile`.
- **✅ Acceptance:** 1 click → brief + export Markdown; fallback khi không có key — `a5011a3`.

---
## P3 — Feature: AI ETL / ELT (~2-3 ngày) — phần DE đậm nhất ✅ Done `0c92ef1`

- [x] `PipelineSpec` DSL `spec_schema.py:8` `validate_dag` (Kahn cycle) + `topo_order`.
- [x] `executor.py:11` topological run, checkpoint `results[step.id]`, dry-run `sample 100` không ghi mart, ghi `mart.<dataset>`.
- [x] `ops/`: `pandas_ops.py` 7 ops + `sql_ops.py` `{{prev}}` ELT.
- [x] `prompts/etl_author.py:7` `CATALOG` + `build_prompt` + `validate_spec`.
- [x] UI `pipeline_screen.py:11` chat → YAML editor → dry-run → run → history skeleton.
- [ ] Alembic `pipelines/pipeline_runs/steps` (sẽ làm khi cần history DB).
- **✅ Acceptance:** mô tả → spec → dry-run → run → mart — `0c92ef1` skeleton, rerun không tốn token.

---
## P4 — Feature: AI Dashboard Gen (~1-2 ngày) ✅ Done `d0716f1`

- [x] `dashboard/spec_schema.py` `ChartSpec` 6 types `kpi/bar/hist/box/line/scatter` + `DashboardSpec`.
- [x] `dashboard/renderer.py` `fetch_data` 1 query/chart DuckDB + `render_chart` 6 types Plotly `apply_theme` — lọc chỉ 6 types.
- [x] `prompts/dashboard_author.py:7` `build_prompt` + `fallback_spec` 4 charts.
- [x] Alembic `005_dashboards.py` + model `Dashboard` + `dashboard_screen.py:9` Generate BYOK, JSON editor, Render + save DB + export.
- **✅ Acceptance:** sinh dashboard + chỉnh/lưu/export — `d0716f1`.

---
## P5 — Polish (~1 ngày) ✅ Done `5874032`

- [x] Lineage `warehouse/lineage.py:7` `get_lineage` dataset→briefs/dashboards + `ui/screens/lineage_screen.py:7` render + `app.py` 7 screens.
- [x] Demo `scripts/generate_demo_data.py:7` 300 SV missing/dup/outlier → `data/demo_sinhvien.csv`.
- [x] Tests `92 passed` giữ ≥45%, `app.py` 7 screens, `data/` gitignored.
- [ ] CI/Docker `data/` volume + README hoàn chỉnh (sẽ làm sau P5).
- **✅ Acceptance:** CI xanh (đã `black/isort`), demo chạy, lineage hiển thị.

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