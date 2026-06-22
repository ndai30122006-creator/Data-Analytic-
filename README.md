# 📊 Data Analyst Pro v3.0

**Enterprise AI-powered data analysis platform** — Phân tích dữ liệu chuyên sâu với AI, Machine Learning, và trực quan hóa chuyên nghiệp.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29%2B-red)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Tính năng chính

### 📂 Data Input
- Upload CSV / Excel files
- Kết nối Database (MySQL, PostgreSQL, SQL Server, SQLite)
- Google Sheets integration

### 📊 Overview
- KPI dashboard (Rows, Columns, Quality, Missing)
- Sparkline trends
- Auto-generated charts (bar, histogram, box plot)
- Data preview với smart column types
- Export CSV / Excel

### 🤖 AI & ML
- **AI Chat** — Hỏi đáp dữ liệu bằng ngôn ngữ tự nhiên (Gemini AI)
- **Forecast** — Dự báo chuỗi thời gian với Prophet
- **AutoML** — Tự động chọn mô hình & hyperparameter tuning (Random Forest, XGBoost, Gradient Boosting, Ridge, Lasso)

### 🔬 Analytics
- **Anomaly Detection** — Phát hiện bất thường với Isolation Forest
- **Profiling** — Phân tích chi tiết từng cột, phân phối, tương quan
- **What-If Analysis** — Mô phỏng kịch bản thay đổi biến
- **PDF Report** — Xuất báo cáo PDF tự động

### 🧠 Deep Analysis (Advanced Analytics)
- **Thống kê nâng cao** — T-test, ANOVA, Mann-Whitney, Chi-Square, Kiểm định phân phối chuẩn
- **Chuỗi thời gian** — ADF/KPSS stationarity test, Seasonal Decompose, ACF/PACF, Dự báo
- **Phân cụm** — K-Means, DBSCAN, Hierarchical Clustering với đánh giá Silhouette/Calinski-Harabasz
- **PCA & t-SNE** — Giảm chiều dữ liệu, trực quan hóa 2D/3D
- **Feature Engineering** — Tạo đặc trưng mới, Scaling, Encoding, Feature Selection
- **So sánh mô hình** — Cross-validation, so sánh 11+ thuật toán
- **Chất lượng dữ liệu** — Data Quality Score, phát hiện trùng lặp, schema validation, drift detection

### ⚛️ Molecule (3D Visualization)
- Trực quan hóa cấu trúc phân tử 3D tương tác với dữ liệu

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

### 4. Chạy ứng dụng
```bash
streamlit run app.py
```

Mở trình duyệt tại `http://localhost:8501`

## 📋 Requirements

```
streamlit>=1.29.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.17.0
matplotlib>=3.7.0
scikit-learn>=1.3.0
scipy>=1.11.0
statsmodels>=0.14.0
openpyxl>=3.1.0
xgboost>=2.0.0
prophet>=1.1.0
fpdf2>=2.7.0
gspread>=6.0.0
google-generativeai>=0.3.0
sqlalchemy>=2.0.0
pymysql>=1.1.0
```

## 📖 Hướng dẫn sử dụng

### 1. Upload dữ liệu
- **Cách 1:** Upload file CSV/Excel từ sidebar
- **Cách 2:** Kết nối Database hoặc Google Sheets

### 2. Khám phá dữ liệu (Tab Overview)
- Xem KPI tổng quan
- Sparkline trends cho các cột numeric
- Biểu đồ tự động: phân phối, top categories
- Data preview & export

### 3. AI Chat
- Vào sidebar → **AI Setup** → nhập Gemini API Key
- Hỏi đáp bằng tiếng Việt: *"Xu hướng dữ liệu như thế nào?"*, *"Có bao nhiêu giá trị bất thường?"*

### 4. Deep Analysis
Tab **🧠 Deep Analysis** cung cấp 7 module chuyên sâu:

| Module | Mô tả |
|--------|-------|
| 📊 Thống kê nâng cao | Kiểm định giả thuyết, phân phối chuẩn, tương quan nâng cao |
| 📈 Chuỗi thời gian | ADF/KPSS, phân rã mùa vụ, ACF/PACF, dự báo |
| 🧬 Phân cụm | K-Means, DBSCAN, Hierarchical |
| 🎯 PCA & t-SNE | Giảm chiều, trực quan hóa |
| 🔧 Feature Engineering | Tạo đặc trưng, scaling, encoding, selection |
| 🏆 So sánh mô hình | 11+ thuật toán, cross-validation |
| ✅ Chất lượng dữ liệu | Data Quality Score, drift detection |

### 5. AutoML
- Tab **🤖 AI & ML** → **🧠 AutoML**
- Chọn target, features
- Chọn phương pháp tuning: GridSearch, RandomizedSearch, hoặc None
- Chọn models: Random Forest, XGBoost, Gradient Boosting, Ridge, Lasso
- Xem kết quả: R², CV scores, best params

## 🎨 Theme

Ứng dụng hỗ trợ 2 theme:
- **Dark mode** (mặc định) — Linear/Vercel/Stripe inspired
- **Light mode** — Click nút 🌓 trong sidebar để chuyển đổi

## 🔧 Troubleshooting

### Lỗi "Module not found"
```bash
pip install <module-name>
```

### Lỗi Gemini API
- Kiểm tra API key tại sidebar → AI Setup
- Lấy key miễn phí tại [aistudio.google.com](https://aistudio.google.com/apikey)

### Lỗi Prophet
```bash
pip install prophet
# hoặc
pip install pystan==2.19.1.1
```

### Lỗi XGBoost
```bash
pip install xgboost
```

## 🏗️ Cấu trúc dự án

```
project1/
├── app.py                  # Main application
├── advanced_analytics.py   # Deep analysis module (7 modules)
├── components.py           # Reusable UI components
├── config.py               # Configuration constants
├── solar_system.py         # 3D molecule visualization
├── utils.py                # Utility functions
├── requirements.txt        # Dependencies
├── .streamlit/
│   └── config.toml         # Streamlit configuration
└── README.md               # Documentation
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License — feel free to use this project for personal or commercial purposes.

## 🙏 Credits

Built with:
- [Streamlit](https://streamlit.io/) — Web framework
- [Plotly](https://plotly.com/) — Interactive charts
- [scikit-learn](https://scikit-learn.org/) — Machine Learning
- [Prophet](https://facebook.github.io/prophet/) — Time series forecasting
- [XGBoost](https://xgboost.readthedocs.io/) — Gradient boosting
- [Gemini AI](https://ai.google.dev/) — Natural language processing

---

**📊 Data Analyst Pro v2.0** — Enterprise AI Data Platform