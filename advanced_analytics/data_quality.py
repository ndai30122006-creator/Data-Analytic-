"""Advanced Data Quality (Book Ch.1)"""
import streamlit as st
import pandas as pd
import numpy as np

from .base import insight_card

try:
    from scipy import stats as scipy_stats
    SCIPY_AVAIL = True
except Exception:
    SCIPY_AVAIL = False


def render_data_quality_tab(df, num, cat):
    st.markdown("### ✅ Data Quality (Book Ch.1)")
    st.caption("Chất lượng dữ liệu, trùng lặp, schema validation, drift")

    tabs = st.tabs(["📋 Overview", "🔍 Duplicates", "📐 Schema", "📊 Drift"])

    with tabs[0]:
        _render_quality_overview(df, num)

    with tabs[1]:
        _render_duplicates(df)

    with tabs[2]:
        _render_schema(df)

    with tabs[3]:
        _render_drift(df, num)


def _render_quality_overview(df, num):
    total_cells = df.shape[0] * df.shape[1]
    filled_cells = total_cells - df.isnull().sum().sum()
    completeness = filled_cells / total_cells * 100 if total_cells > 0 else 0
    dup_rows = df.duplicated().sum()
    uniqueness = (1 - dup_rows / len(df)) * 100 if len(df) > 0 else 0

    outlier_count = 0
    for c in num:
        q1, q3 = df[c].quantile(0.25), df[c].quantile(0.75)
        iqr = q3 - q1
        outliers = ((df[c] < q1 - 1.5 * iqr) | (df[c] > q3 + 1.5 * iqr)).sum()
        outlier_count += outliers

    validity = max(0, 100 - (outlier_count / total_cells * 100) if total_cells > 0 else 0)
    quality_score = completeness * 0.3 + uniqueness * 0.25 + validity * 0.25 + 100 * 0.2

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Completeness", f"{completeness:.1f}%")
    c2.metric("Uniqueness", f"{uniqueness:.1f}%")
    c3.metric("Validity", f"{validity:.1f}%")
    c4.metric("Quality Score", f"{quality_score:.1f}%")

    issues = []
    if df.isnull().sum().sum() > 0:
        issues.append(f"⚠️ {df.isnull().sum().sum():,} missing values")
    if dup_rows > 0:
        issues.append(f"⚠️ {dup_rows:,} duplicate rows")
    if outlier_count > 0:
        issues.append(f"⚠️ {outlier_count:,} outliers")
    if not issues:
        issues.append("✅ Data is clean!")
    for issue in issues:
        insight_card("📊", "", issue, "good" if "✅" in issue else "warning")


def _render_duplicates(df):
    exact_dups = df.duplicated(keep=False)
    n_exact = exact_dups.sum()
    st.metric("Exact Duplicates", f"{n_exact:,} ({n_exact/len(df)*100:.1f}%)")
    if n_exact > 0:
        st.dataframe(df[exact_dups].head(20), width='stretch')


def _render_schema(df):
    schema = pd.DataFrame({
        "Column": df.columns,
        "Type": df.dtypes.astype(str),
        "Non-Null": df.count().values,
        "Null%": (df.isnull().sum().values / len(df) * 100).round(1).astype(str) + "%",
        "Unique": df.nunique().values
    })
    st.dataframe(schema, width="stretch")


def _render_drift(df, num):
    if not num:
        return
    split_point = st.slider("Split point (%):", 10, 90, 50, 5, key="dq_split")
    split_idx = int(len(df) * split_point / 100)
    if split_idx <= 0 or split_idx >= len(df):
        return
    df_a = df.iloc[:split_idx]
    df_b = df.iloc[split_idx:]

    drift_results = []
    for c in num:
        a = df_a[c].dropna()
        b = df_b[c].dropna()
        if len(a) > 1 and len(b) > 1 and SCIPY_AVAIL:
            try:
                stat, p = scipy_stats.ks_2samp(a, b)
                drift_results.append({
                    "Column": c, "KS Stat": round(stat, 4),
                    "p-value": round(p, 6),
                    "Drift": "⚠️ Yes" if p < 0.05 else "✅ No"
                })
            except:
                pass

    if drift_results:
        st.dataframe(pd.DataFrame(drift_results), width='stretch')
        n_drift = sum(1 for r in drift_results if r["Drift"] == "⚠️ Yes")
        if n_drift > 0:
            insight_card("⚠️", f"{n_drift} drifted columns",
                        f"{n_drift}/{len(drift_results)} columns have different distributions",
                        "warning" if n_drift <= len(drift_results)/2 else "danger")
        else:
            insight_card("✅", "No drift detected", "Data is stable", "good")