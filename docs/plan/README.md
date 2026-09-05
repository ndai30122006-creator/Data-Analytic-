# 📘 AI Data Engineering Workbench — Kế hoạch Pivot

Trang này là **index** cho toàn bộ kế hoạch chuyển đổi (pivot) dự án
`workbench-ai` (trước là `Data-Analytic-`) từ "Learning Analytics / Data Analyst Pro" sang một
**local-first AI Data Engineering Workbench**.

## 📁 Danh mục kế hoạch

| File | Nội dung |
|------|----------|
| [`01-vision.md`](./01-vision.md) | Tầm nhìn, mục tiêu cá nhân, định nghĩa phạm vi |
| [`02-architecture.md`](./02-architecture.md) | Kiến trúc mục tiêu, cấu trúc thư mục, data layout |
| [`03-feature-brief.md`](./03-feature-brief.md) | Feature 1 — AI Brief dữ liệu |
| [`04-feature-elt.md`](./04-feature-elt.md) | Feature 2 — AI ETL / ELT pipeline |
| [`05-feature-dashboard.md`](./05-feature-dashboard.md) | Feature 3 — AI sinh Dashboard |
| [`06-roadmap.md`](./06-roadmap.md) | Kế hoạch theo phase (P0–P5) & acceptance |
| [`07-api-design.md`](./07-api-design.md) | Thiết kế REST API mới |
| [`ui/`](./ui/README.md) | Plan UI mới — Node.js (`frontend/`): web + mobile + shared, build plan sẵn sàng |

## 🎯 Bối cảnh

- Đây là dự án cá nhân, mục tiêu là **học data engineering + AI** thực tế.
- **Tận dụng tối đa repo có sẵn** (statistical engine, AI service, FastAPI
  backend, UI Streamlit, tests, CI/CD) thay vì viết lại từ đầu.
- **Input giữ nguyên**: upload CSV / Excel như hiện tại.
- **BYOK (Bring Your Own Key)**: người dùng tự cung cấp key AI riêng
  (OpenAI / Gemini) — cấu hình đã có sẵn trong dự án.
- **3 feature trọng tâm**: AI cho quy trình ETL/ELT, AI brief dữ liệu,
  AI sinh dashboard.

## 🔢 Nguyên tắc chỉ đạo

1. **LLM chỉ "authoring", không "runtime"** — AI sinh spec (YAML/JSON),
   tất cả các lần chạy sau là deterministic và không tốn token.
2. **LLM nhận profile/schema, KHÔNG nhận raw data** — tiết kiệm token,
   riêng tư, và buộc phải xây hệ profiling pipeline đúng chuẩn.
3. **FastAPI làm execution layer** — Streamlit gọi qua API; backend điều phối
   job, lưu history, kiểm soát truy cập.
4. **Local-first** — DuckDB làm warehouse nhúng, không cần infra bên ngoài.