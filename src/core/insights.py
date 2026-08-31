"""Core insights helpers — extracted from UI to break core->ui cycle (P0)."""

import numpy as np
import pandas as pd


def generate_data_summary(df: pd.DataFrame) -> str:
    """Generate comprehensive data summary for AI analysis (moved from ui.tabs.ai_insights)."""
    summary = []
    summary.append(f"Dataset có {len(df):,} dòng và {len(df.columns)} cột.")
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    date_cols = df.select_dtypes(include=["datetime64", "datetime64[ns]"]).columns.tolist()
    summary.append(f"- {len(num_cols)} cột numeric: {', '.join(num_cols[:5])}{'...' if len(num_cols) > 5 else ''}")
    summary.append(f"- {len(cat_cols)} cột categorical: {', '.join(cat_cols[:5])}{'...' if len(cat_cols) > 5 else ''}")
    if date_cols:
        summary.append(f"- {len(date_cols)} cột datetime: {', '.join(date_cols[:3])}")
    missing = df.isnull().sum().sum()
    # Guard empty df
    total_cells = len(df) * len(df.columns) if len(df.columns) else 0
    missing_pct = (missing / total_cells * 100) if total_cells else 0
    summary.append(f"- {missing:,} giá trị thiếu ({missing_pct:.1f}%)")
    dupes = df.duplicated().sum()
    summary.append(f"- {dupes:,} dòng trùng lặp")
    if num_cols:
        summary.append("\nThống kê các cột numeric:")
        for col in num_cols[:5]:
            stats = df[col].describe()
            summary.append(
                f"- {col}: mean={stats['mean']:.2f}, std={stats['std']:.2f}, min={stats['min']:.2f}, max={stats['max']:.2f}"
            )
    if cat_cols:
        summary.append("\nPhân phối các cột categorical (top 3):")
        for col in cat_cols[:3]:
            top_vals = df[col].value_counts().head(3)
            summary.append(f"- {col}: {', '.join([f'{idx} ({cnt})' for idx, cnt in top_vals.items()])}")
    return "\n".join(summary)


def generate_learning_insights(df: pd.DataFrame, score_col: str, group_col: str = None) -> str:
    """Generate insights specific to learning analytics (moved from ui)."""
    insights = []
    if score_col in df.columns:
        scores = pd.to_numeric(df[score_col], errors="coerce").dropna()
        if len(scores) > 0:
            insights.append(f"Phân tích cột '{score_col}':")
            insights.append(f"- Điểm trung bình: {scores.mean():.2f}")
            insights.append(f"- Điểm cao nhất: {scores.max():.2f}")
            insights.append(f"- Điểm thấp nhất: {scores.min():.2f}")
            insights.append(f"- Độ lệch chuẩn: {scores.std():.2f}")
            pass_rate = (scores >= 5.0).mean() * 100
            insights.append(f"- Tỷ lệ đạt (>=5.0): {pass_rate:.1f}%")
            risk_rate = (scores < 4.0).mean() * 100
            insights.append(f"- Tỷ lệ rủi ro (<4.0): {risk_rate:.1f}%")
            insights.append(
                f"- Phân phối: 25%={scores.quantile(0.25):.2f}, 50%={scores.median():.2f}, 75%={scores.quantile(0.75):.2f}"
            )
    if group_col and group_col in df.columns:
        insights.append(f"\nPhân tích theo nhóm '{group_col}':")
        try:
            groups = df.groupby(group_col)[score_col].agg(["count", "mean", "std"]).round(2)
            insights.append(f"Số nhóm: {len(groups)}")
            insights.append(f"Nhóm có điểm cao nhất: {groups['mean'].idxmax()} ({groups['mean'].max():.2f})")
            insights.append(f"Nhóm có điểm thấp nhất: {groups['mean'].idxmin()} ({groups['mean'].min():.2f})")
        except Exception:
            insights.append("(không thể nhóm)")
    return "\n".join(insights)
