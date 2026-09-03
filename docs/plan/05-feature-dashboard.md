# 05 — Feature: AI sinh Dashboard

## 🎯 Mục đích

Từ dataset (đã transform) và brief, **AI đề xuất một bộ biểu đồ dưới dạng
`DashboardSpec` (JSON)** → renderer vẽ bằng Plotly → user chỉnh tay → lưu /
export.

## ✨ User flow

1. Chọn dataset `mart.<name>`.
2. Bấm "Sinh dashboard" (có thể kèm yêu cầu: *"so sánh điểm giữa các lớp"*).
3. AI sinh `DashboardSpec`: 4–6 charts hợp lý (KPI, bar, hist, box, line...).
4. Renderer vẽ; user sửa layout / thêm-bớt chart / đổi type.
5. Lưu layout (JSON) → có thể load lại; export PNG / PDF / Markdown báo cáo.

## 🧱 DashboardSpec (JSON)

```json
{
  "id": "dash_x1",
  "title": "Phân tích kết quả học tập",
  "source": "mart.sinhvien_diem",
  "charts": [
    {
      "id": "c1",
      "type": "kpi",
      "title": "Trung bình điểm",
      "metric": {"aggregation": "mean", "column": "diem"}
    },
    {
      "id": "c2",
      "type": "hist",
      "title": "Phân phối điểm",
      "x": "diem", "bins": 20
    },
    {
      "id": "c3",
      "type": "box",
      "title": "Điểm theo lớp",
      "x": "lop", "y": "diem", "orientation": "v"
    },
    {
      "id": "c4",
      "type": "bar",
      "title": "Số SV theo xếp loại",
      "x": "xep_loai", "aggregation": "count"
    }
  ]
}
```

## 🔁 Tận dụng từ repo

| Thành phần | Dùng như thế nào |
|---|---|
| Plotly (khắp các tabs hiện có) | Nguồn chart types & styling |
| `src/ui/theme.py` | Tái dùng theme, metric_card, gradient_text |
| `src/services/report_service.py` | Export PDF / Markdown |
| `compare.py` | Hữu ích làm QA sau transform |
| DuckDB | Nguồn data cho mỗi chart (mỗi chart 1 query) |

## 🧱 Cần xây mới

- `src/dashboard/spec_schema.py` — ChartSpec / DashboardSpec (Pydantic).
- `src/dashboard/renderer.py` — spec → plotly figure.
- `src/prompts/dashboard_author.py` — profile + brief → DashboardSpec.
- Migration: bảng `dashboards` (id, name, spec_json, owner, created_at).
- `src/ui/screens/dashboard_screen.py`.

## ✅ Acceptance criteria

- [ ] Từ dataset đã transform → sinh dashboard hợp lý (4–6 charts).
- [ ] Renderer vẽ đúng từng chart type; sửa layout/lưu được.
- [ ] Mỗi chart đọc data qua query riêng trên DuckDB.
- [ ] Export PNG/PDF/Markdown hoạt động.