# 07 — Thiết kế REST API mới

FastAPI làm **execution layer**; React (web 5173 + mobile 5174) gọi qua HTTP (`frontend/shared/src/api/*`). Dưới đây là bổ sung
vào `api.py` hiện tại, tái dụng:

- Auth: `JWT + get_current_user` (đã có)
- Rate limiting: `check_rate_limit` (đã có)
- BYOK: `POST /auth/api-key` (đã có, nâng cấp lưu encrypted)
- `_dispatch_analysis` cho `POST /analysis/run` (giữ cho Statistics Lab)

## Datasets

| Method | Path | Chức năng |
|---|---|---|
| POST | `/datasets/ingest` | Upload file → DuckDB `raw` + profiling + registry |
| GET | `/datasets` | List datasets (đã có, bổ sung trường mới) |
| GET | `/datasets/{id}/profile` | Schema + stats (payload cho AI — KHÔNG lộ raw) |
| DELETE | `/datasets/{id}` | Xóa dataset (và bảng DuckDB tương ứng) |

## Pipelines (ETL/ELT)

| Method | Path | Chức năng |
|---|---|---|
| POST | `/pipelines` | Lưu PipelineSpec (YAML) |
| GET | `/pipelines` | Liệt kê specs |
| GET | `/pipelines/{id}` | Lấy spec chi tiết |
| POST | `/pipelines/preview` | **Dry-run** spec trên sample 100 rows → preview |
| POST | `/pipelines/run` | Chạy async → trả `run_id` (BackgroundTasks) |
| GET | `/runs/{id}` | Status + log + checkpoint + output schema |
| GET | `/runs` | Liệt kê run history |

## Brief

| Method | Path | Chức năng |
|---|---|---|
| POST | `/brief/{dataset_id}` | Sinh brief (gọi AI gateway) → lưu version |
| GET | `/brief/{dataset_id}` | Liệt kê brief versions |
| GET | `/brief/{dataset_id}/{version}` | Lấy brief cụ thể + export |

## Dashboards

| Method | Path | Chức năng |
|---|---|---|
| POST | `/dashboards` | Lưu DashboardSpec (JSON) |
| GET | `/dashboards` | Liệt kê |
| GET | `/dashboards/{id}` | Lấy spec |
| PUT | `/dashboards/{id}` | Cập nhật spec |
| POST | `/dashboards/{id}/data` | Trả data đã agg cho renderer (mỗi chart 1 query trên DuckDB) |
| POST | `/dashboards/generate` | AI sinh spec từ profile + brief |

## Async & execution

- `POST /pipelines/run` dùng **`BackgroundTasks`** của FastAPI → trả ngay
  `run_id`, job chạy nền; React poll `/runs/{id}` với backoff `1s→2s→4s` (`useApiCall`).
- Nếu cần scale: nối thêm queue (Redis / Dramatiq) ở phase sau — giữ interface
  `/runs/{id}` ổn định.

## DTO (Pydantic) — ví dụ

```python
class PipelineSpec(BaseModel):
    name: str
    source: str            # raw.<dataset>
    target: str            # mart.<dataset>
    steps: list[PipelineStep]

class PipelineStep(BaseModel):
    id: str
    op: str                # fill_missing | drop_duplicates | ...
    params: dict[str, Any] = {}
    depends_on: list[str] = []

class RunResponse(BaseModel):
    run_id: str
    status: str            # queued | running | done | failed
```

## ✅ Acceptance (API)

- [ ] Swagger liệt kê đủ 4 groups endpoints, auth bảo vệ.
- [ ] Dry-run `/pipelines/preview` an toàn, không ghi đè data.
- [ ] `/pipelines/run` trả `run_id` ngay; `/runs/{id}` phản ánh trạng thái
      thật qua từng step.
- [ ] Profile endpoint không lộ raw data (chỉ agg stats).
- [ ] CI chạy tests cho các endpoint mới.