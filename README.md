# 🎓 Learning Analytics Thống kê

**Nền tảng phân tích dữ liệu học tập** — Phân tích điểm số, nhóm rủi ro, kiểm định thống kê và học máy cho sinh viên ngành Thống kê.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29%2B-red)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Tính năng chính

### 📂 Data Input
- Upload nhiều CSV / Excel files cùng lúc
- Quản lý datasets: chọn, xóa, thay đổi dataset active
- Xử lý tự động: parse dates, normalize columns
- Data validation & quality checks

### 📊 Overview
- KPI dashboard (Rows, Columns, Quality, Missing)
- Sparkline trends cho các cột numeric
- Auto-generated charts (bar, histogram, box plot)
- Data dictionary & column profiler
- Export CSV / Excel

### ⚖️ Compare Datasets
- So sánh cấu trúc: rows, columns, memory usage
- So sánh columns: common, only in dataset 1, only in dataset 2
- So sánh thống kê: mean, std của các cột numeric chung
- Trực quan hóa: box plot so sánh

### 🤖 AI Auto Insights
- Phân tích tự động bằng AI
- Tạo báo cáo insights tự động
- Phát hiện chất lượng dữ liệu, xu hướng, correlation
- Khuyến nghị hành động
- Export báo cáo Markdown

### 🎓 Learning Analytics
- Phân tích điểm số, tỷ lệ đạt, nhóm rủi ro
- Phân loại kết quả: Cần hỗ trợ / Cần theo dõi / Đạt
- So sánh theo nhóm (lớp, môn học, giới tính...)
- Gợi ý đọc kết quả tự động

### 📈 Statistics (Practical Statistics for Data Scientists)
- **Hypothesis Testing** — T-test, ANOVA, Mann-Whitney, Kruskal-Wallis, Chi-Square
- **Bootstrap** — Confidence intervals, resampling (Book Ch.2)
- **A/B Testing** — Two-proportion Z-test, Sample Size Calculator, Power Analysis (Book Ch.3)
- **Regression** — Linear Regression với diagnostics (Book Ch.4)
- **Logistic Regression** — Binary classification, ROC/AUC, Confusion Matrix (Book Ch.5)
- **Naive Bayes** — Gaussian & Categorical NB
- **Diagnostics** — VIF, Heteroskedasticity, Durbin-Watson

### 🔬 Analytics
- **Anomaly Detection** — Phát hiện bất thường với Isolation Forest
- **Profiling** — Phân tích chi tiết từng cột, phân phối, tương quan
- **Data Cleaning** — Missing values, duplicates, outliers, encoding
- **AutoML** — Tự động chọn mô hình & hyperparameter tuning (5 thuật toán)

### 🧠 Deep Analysis (Advanced Analytics)
- **Bootstrap & CI** — Resampling, confidence intervals
- **A/B Testing** — Thiết kế thử nghiệm, power analysis
- **Logistic Regression** — Phân loại nhị phân, SHAP explainability
- **Naive Bayes** — Gaussian & Categorical classification
- **Time Series** — ADF/KPSS stationarity, Seasonal Decompose, ACF/PACF
- **Clustering** — K-Means, DBSCAN, Hierarchical với đánh giá Silhouette/Calinski-Harabasz
- **PCA & t-SNE** — Giảm chiều dữ liệu, trực quan hóa 2D/3D
- **Feature Engineering** — Scaling, Encoding, Feature Selection
- **Model Comparison** — Cross-validation, so sánh 11+ thuật toán
- **Regression Diagnostics** — VIF, Heteroskedasticity, Durbin-Watson, Residuals

## 🚀 Cài đặt

### 1. Clone repository
```bash
git clone <repo-url>
cd project1
```

### 2. Tạo virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 4. Chạy ứng dụng (Development)
```bash
streamlit run app.py
```

Mở trình duyệt tại `http://localhost:8501`

### Đăng nhập
> ⚠️ **Cảnh báo:** Các tài khoản dưới đây chỉ dành cho **mục đích demo / phát triển**.  
> **Không sử dụng trong môi trường production.** Thay đổi mật khẩu hoặc tích hợp xác thực thực tế trước khi triển khai công khai.

Credentials được cấu hình qua biến môi trường (xem `.env.example`):

```bash
# Mặc định (DEMO_MODE=true) — chỉ dùng cho development
DEMO_ADMIN_USERNAME=admin
DEMO_ADMIN_PASSWORD=admin123
DEMO_USER_USERNAME=user
DEMO_USER_PASSWORD=user123
DEMO_TEACHER_USERNAME=teacher
DEMO_TEACHER_PASSWORD=teacher123
```

> **Cho production:** Set `DEMO_MODE=false` và tạo user qua API `/auth/register`.  
> **Luôn** thay đổi mật khẩu và JWT_SECRET_KEY trước khi deploy thật.

## 🐳 Deploy với Docker (Production)

### Prerequisites
- Docker >= 20.10
- Docker Compose >= 2.0

### 1. Build và Start
```bash
# Development mode (không có Nginx)
docker-compose up --build

# Production mode (với Nginx reverse proxy)
docker-compose --profile production up --build -d
```

### 2. Truy cập
- **Frontend:** http://localhost:8501
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### 3. Dừng services
```bash
docker-compose down
```

### 4. Xem logs
```bash
docker-compose logs -f
docker-compose logs -f frontend
docker-compose logs -f backend
```

## 📋 Requirements

```
streamlit>=1.29.0
pandas>=2.1.0
numpy>=1.24.0
matplotlib>=3.7.0
plotly>=5.17.0
scipy>=1.10.0
scikit-learn>=1.3.0
statsmodels>=0.14.0
fpdf2>=2.5.0
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0.0
python-multipart>=0.0.6
```

> 🧩 **Build notes:** `scipy`, `scikit-learn`, and `statsmodels` include C extensions. If pip fails to build them, install a pre-compiled wheel or use **conda**:
> ```bash
> conda install scipy scikit-learn statsmodels
> ```
> These packages are **optional** unless you use the Deep Analysis / Statistics tabs — the core app runs without them.

## 📖 Hướng dẫn sử dụng

### 1. Upload dữ liệu
- Upload nhiều file CSV/Excel cùng lúc từ sidebar
- Chọn dataset từ dropdown để active
- Xóa dataset không cần thiết
- Hệ thống tự động parse dates và validate data

### 3. Overview
- Xem KPI tổng quan (Rows, Columns, Quality, Missing)
- Sparkline trends cho các cột numeric
- Biểu đồ tự động: phân phối, top categories
- Data dictionary & column profiler
- Export CSV / Excel

### 4. Compare Datasets
- Tab **⚖️ Compare Datasets** cho phép so sánh 2 datasets
- So sánh cấu trúc: rows, columns, memory
- So sánh columns: common, only in each dataset
- So sánh thống kê: mean, std của các cột numeric chung
- Trực quan hóa: box plot so sánh

### 5. AI Insights
- Tab **🤖 AI Insights** phân tích tự động bằng AI
- Chọn loại phân tích: Tổng quan hoặc Học tập
- Tự động phát hiện chất lượng dữ liệu, insights, khuyến nghị
- Export báo cáo Markdown

### 6. Learning Analytics
- Chọn cột điểm/kết quả và cột phân nhóm (lớp, môn...)
- Xem phân phối điểm, tỷ lệ đạt, nhóm rủi ro
- So sánh giữa các nhóm với box plot
- Gợi ý đọc kết quả tự động

### 7. Statistics
Tab **📈 Statistics** cung cấp 7 module:

| Module | Mô tả |
|--------|-------|
| 🔬 Hypothesis Testing | T-test, ANOVA, Mann-Whitney, Chi-Square |
| 🎲 Bootstrap | Confidence intervals, resampling |
| ⚗️ A/B Testing | Two-proportion test, power analysis |
| 📈 Regression | Linear regression, diagnostics |
| 🔴 Logistic | Binary classification, ROC/AUC |
| 🧮 Naive Bayes | Gaussian & Categorical NB |
| 🔧 Diagnostics | VIF, heteroskedasticity, Durbin-Watson |

### 8. Analytics
Tab **🔬 Analytics** cung cấp 4 module:

| Module | Mô tả |
|--------|-------|
| 🔍 Anomaly | Phát hiện bất thường với Isolation Forest |
| 📊 Profiling | Phân tích chi tiết cột, correlation matrix |
| 🧹 Cleaning | Xử lý missing, duplicates, outliers, encoding |
| 🚀 AutoML | Tự động chọn mô hình, hyperparameter tuning |

### 9. Deep Analysis
Tab **🧠 Deep Analysis** cung cấp 10 module chuyên sâu:

| Module | Mô tả |
|--------|-------|
| 🎲 Bootstrap | Resampling, confidence intervals |
| ⚗️ A/B Testing | Thiết kế thử nghiệm, power analysis |
| 🔴 Logistic | Phân loại, SHAP explainability |
| 🧮 Naive Bayes | Gaussian & Categorical NB |
| 📈 Time Series | Stationarity, decompose, ACF/PACF |
| 🧬 Clustering | K-Means, DBSCAN, Hierarchical |
| 🎯 PCA & t-SNE | Giảm chiều, trực quan hóa |
| 🔧 Feature Engineering | Scaling, encoding, selection |
| 🏆 Model Comparison | 11+ thuật toán, cross-validation |
| ✅ Diagnostics | VIF, heteroskedasticity, residuals |

## 🎨 Theme

Ứng dụng hỗ trợ dark mode mặc định với theme hiện đại:
- **Dark mode** — Linear/Vercel/Stripe inspired
- Font Inter, màu sắc chuyên nghiệp
- Responsive design

## 🔧 Troubleshooting

### Lỗi "Module not found"
```bash
pip install <module-name>
```

### Lỗi scipy / scikit-learn
```bash
pip install scipy scikit-learn
```

### Lỗi statsmodels
```bash
pip install statsmodels
```

### Lỗi xgboost
```bash
pip install xgboost
```

### Docker issues
```bash
# Rebuild images
docker-compose build --no-cache

# Check logs
docker-compose logs

# Restart services
docker-compose restart
```

## 🏗️ Cấu trúc dự án

> ⚠️ **Legacy layout:** Mã nguồn hiện tại tồn tại song song ở 2 nơi — root và `src/`.  
> **Khuyến nghị:** Các module mới nên đặt trong `src/` package. Dịch chuyển dần code cũ ra khỏi root khi có thời gian.

```
project1/
├── app.py                  # Main Streamlit application (entry point)
├── sidebar.py              # Sidebar component (to migrate → src/ui/)
├── components.py           # Reusable UI components (to migrate → src/ui/)
├── config.py               # Configuration constants (to migrate → src/utils/)
├── utils.py                # Utility functions (to migrate → src/utils/)
├── report_utils.py         # PDF report generation
├── landing.py              # Landing page (to migrate → src/ui/tabs/)
├── overview_tab.py         # Overview tab (to migrate → src/ui/tabs/)
├── statistics_tab.py       # Statistics tab (to migrate → src/ui/tabs/)
├── analytics_tab.py        # Analytics tab (to migrate → src/ui/tabs/)
├── learn_analytics.py      # Learning analytics tab
├── compare_datasets.py     # Compare datasets tab
├── ai_insights.py          # AI-powered insights & reporting
├── advanced_analytics/     # Deep analysis package (advanced modules)
├── api.py                  # FastAPI backend
├── report_utils.py         # PDF report generation
│
├── src/                    # 📦 New package structure (recommended)
│   ├── ui/
│   │   ├── sidebar.py      # Refactored sidebar
│   │   ├── theme.py        # Theme configuration
│   │   └── tabs/           # Tab components
│   ├── utils/
│   │   ├── exceptions.py   # Error handling
│   │   ├── helpers.py      # Helper functions
│   │   ├── config.py       # Configuration
│   │   └── validators.py   # Data validation
│   ├── core/
│   │   └── analytics_engine.py
│   └── api/
│
├── .streamlit/
│   └── config.toml         # Streamlit configuration
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # Docker Compose configuration
├── nginx.conf              # Nginx reverse proxy config
└── README.md               # Documentation
```

## 🔌 API Endpoints

### Analysis
- `GET /datasets` - List datasets
- `POST /analysis/run` - Run analysis

### Health
- `GET /health` - Health check

### Interactive Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License — feel free to use this project for personal or commercial purposes.

## 🙏 Credits

Built with:
- [Streamlit](https://streamlit.io/) — Web framework
- [FastAPI](https://fastapi.tiangolo.com/) — API backend
- [Plotly](https://plotly.com/) — Interactive charts
- [scikit-learn](https://scikit-learn.org/) — Machine Learning
- [scipy](https://scipy.org/) — Scientific computing
- [statsmodels](https://www.statsmodels.org/) — Statistical models
- [pandas](https://pandas.pydata.org/) — Data manipulation
- [Docker](https://www.docker.com/) — Containerization

---

**🎓 Learning Analytics Thống kê** — Practical Statistics for Data Scientists Edition