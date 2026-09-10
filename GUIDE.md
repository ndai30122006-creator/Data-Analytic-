# GUIDE — Chạy local dev đúng cách (Dataworkbench-ai)

## 1. Yêu cầu

| Thứ | Bản tối thiểu | Kiểm tra |
|---|---|---|
| Python | 3.10+ | `python --version` |
| Node.js | 20+ | `node -v` |
| pnpm | 9+ (`corepack enable` để có lệnh `pnpm`) | `pnpm -v` |
| Docker Desktop | chỉ khi build prod | `docker --version` |

## 2. Cài đặt (lần đầu)

```powershell
# Backend deps
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements/base.txt -r requirements/dev.txt

# Frontend deps
corepack enable
cd frontend
pnpm install
cd ..
```

## 3. Chạy dev (2 terminal riêng)

```powershell
# Terminal 1 — Backend :8000
.\.venv\Scripts\python.exe -m uvicorn api:app --host 127.0.0.1 --port 8000
```

```powershell
# Terminal 2 — Web :5173
cd frontend\web
..\..\frontend\web\node_modules\.bin\vite.CMD --host 127.0.0.1 --port 5173
# (nếu đã có pnpm global: cd frontend; pnpm dev:web)
```

```powershell
# (Tùy chọn) Mobile :5174
cd frontend\mobile
..\..\frontend\mobile\node_modules\.bin\vite.CMD --host 127.0.0.1 --port 5174
```

Mở: web `http://localhost:5173/`, mobile `http://localhost:5174/`, API docs `http://localhost:8000/docs`.

## 4. Tài khoản

- Đăng ký mới ở `/login`, hoặc dùng sẵn `dev / dev123`.
- Chưa login vào trang nào cũng tự đá về `/login`.

## 5. Danh sách port (đừng nhầm)

| Port | Cái gì | Khi nào dùng |
|---|---|---|
| 5173 | Web dev (Vite, code mới nhất) | dùng hàng ngày |
| 5174 | Mobile dev | test giao diện điện thoại |
| 8000 | Backend API | luôn cần |
| 4173 | Bản build cũ (vite preview) | **đừng dùng** — cũ từ 08/09 |
| 8080 / 80 | Docker prod | chỉ khi build Docker |

## 6. Sự cố thường gặp

- **Thấy giao diện cũ**: `Ctrl+F5` hard refresh. Vẫn cũ → mở tab ẩn danh `Ctrl+Shift+N` vào lại. Vẫn cũ nữa → kiểm tra port (mục 5), có thể đang mở nhầm tab cũ.
- **Trắng tab**: backend chưa chạy (mở `/health` kiểm tra) hoặc JS crash — mở `F12 → Console` copy dòng đỏ.
- **401/đá về login**: token hết hạn — login lại.
- **Port bận** (`EADDRINUSE`): kill process node/python cũ đang giữ port rồi chạy lại.
- **DB loạn**: xóa `users.db` + `data/warehouse.duckdb` để reset dev (mất data local).

## 7. Build prod (cần Docker Desktop + engine running)

```powershell
copy .env.example .env
# đặt JWT_SECRET_KEY mạnh trong .env
docker compose --profile production up --build -d
```

Mở `http://localhost` (nginx) — build prod với `--build-arg VITE_API_BASE=/api`.

## 8. Kiểm tra nhanh sau khi chạy

```powershell
Invoke-WebRequest http://127.0.0.1:8000/health   # {"status":"healthy"}
Invoke-WebRequest http://127.0.0.1:5173/          # 200
```
