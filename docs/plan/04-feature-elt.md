# 04 — Feature: AI ETL / ELT Pipeline

> Đây là feature **quan trọng nhất** vì chứa phần lớn kỹ năng data engineering.

## 🎯 Mục đích

Người dùng mô tả bằng tiếng Việt tự nhiên cách muốn làm sạch / chuyển đổi
dữ liệu → AI sinh một **PipelineSpec (YAML/JSON)** → user review (dry-run)
→ chạy → xem history & lineage.

## ✨ User flow

1. Chọn dataset đã ingest.
2. Gõ yêu cầu: *"điền missing cột điểm bằng median, xóa dòng trùng, tách
   cột họ_tên thành ho và ten"*.
3. AI sinh `PipelineSpec` → hiển thị trong editor YAML để **review**.
4. **Dry-run** trên sample 100 rows → xem ví dụ kết quả trước khi chạy thật.
5. Chạy → pipeline đưa dữ liệu vào `mart.<dataset>` trong DuckDB.
6. Xem run history, log từng step, lineage.

## 🔁 Hai mode

| Mode | Cách xử lý | Khi nào dùng | Skill học |
|---|---|---|---|
| **ETL** | `pandas_ops` chạy trong Python | logic phức tạp khó viết SQL | pandas transforms, df ops |
| **ELT** | SQL trên DuckDB views | transform tuyên bố, đơn giản | SQL analytics, warehouse modeling |

Toggle chọn mode cho từng step.

## 🧱 PipelineSpec DSL (YAML)

```yaml
name: clean-score
source: raw.sinhvien_diem
target: mart.sinhvien_diem
steps:
  - id: s1
    op: fill_missing
    params: {column: diem, method: median}
  - id: s2
    op: drop_duplicates
    params: {subset: [ma_sv]}
    depends_on: [s1]
  - id: s3
    op: derive_column
    params: {name: xep_loai,
             expr: "CASE WHEN diem>=8 THEN 'gioi' WHEN diem>=5 THEN 'dat' ELSE 'can_hotro' END"}
    depends_on: [s2]
  - id: s4
    op: sql
    params: {query: "SELECT *, ROW_NUMBER() OVER (PARTITION BY ma_sv ORDER BY diem DESC) AS rn FROM {{prev}}"}
    depends_on: [s3]
```

- Mỗi step có `id`, `op`, `params`, `depends_on` → tạo thành **DAG**.
- Executor chạy theo thứ tự topo, **checkpoint** sau mỗi step (dừng được,
  resume được).
- Mode `sql` chạy trên DuckDB views (ELT).

## 📚 Ops library (bản P1 — có thể mở rộng)

| op | loại | mô tả |
|---|---|---|
| `fill_missing` | pandas | điền missing (mean/median/mode/const) |
| `drop_duplicates` | pandas | bỏ dòng trùng |
| `type_cast` | pandas | ép kiểu cột |
| `standardize_columns` | pandas | chuẩn hóa tên cột (snake_case) |
| `derive_column` | pandas/sql | tạo cột mới |
| `filter` | pandas/sql | lọc theo điều kiện |
| `aggregate` | pandas/sql | groupby + agg |
| `sql` | sql | chạy SQL trên DuckDB |

## 🔁 Tận dụng từ repo

| Thành phần | Dùng như thế nào |
|---|---|
| `src/analytics/data_quality.py` | Logic cleaning ops (missing, dupes, outliers) |
| `src/utils/validators.py` | Validate input |
| Dataset model + Alembic | Thêm bảng `pipelines`, `pipeline_runs`, `pipeline_steps` |
| `auth` | Bảo vệ endpoints pipeline |

## 🛡 Guardrails chống hallucination spec

- `src/prompts/etl_author.py` cung cấp **danh mục ops + schema** cho LLM.
- `validators.py` kiểm tra spec trước khi chạy: reject op lạ, params sai,
  column không tồn tại → dừng và báo lỗi rõ.

## ✅ Acceptance criteria

- [ ] Gõ yêu cầu tiếng Việt → spec hợp lệ hiển thị trong YAML editor.
- [ ] Dry-run an toàn (sample 100 rows), preview kết quả.
- [ ] Chạy đúng DAG, checkpoint từng step, rerun không tốn token.
- [ ] ELT mode chạy SQL trên DuckDB views hoạt động.
- [ ] Run history + lineage (dataset → pipeline → runs) hiển thị.