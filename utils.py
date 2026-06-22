"""Utility functions for Data Analyst Pro"""
import pandas as pd
import numpy as np
import streamlit as st
from typing import Tuple, Optional

TOP_N_VALUES = 10

@st.cache_data
def load_and_process_data(file) -> Optional[pd.DataFrame]:
    """
    Load và cache dữ liệu từ file upload (CSV/Excel).

    Args:
        file: Uploaded file object từ Streamlit file_uploader

    Returns:
        pd.DataFrame nếu thành công, None nếu lỗi
    """
    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        elif file.name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file, engine="openpyxl")
        else:
            st.error("❌ Định dạng file không hỗ trợ")
            return None
        
        if df.empty:
            st.error("❌ File rỗng")
            return None
            
        return df
    except Exception as e:
        st.error(f"❌ Lỗi đọc file: {str(e)}")
        return None

@st.cache_data
def get_column_stats(df: pd.DataFrame, col: str) -> dict:
    """
    Cache thống kê chi tiết cho từng cột.

    Args:
        df: Input DataFrame
        col: Tên cột cần phân tích

    Returns:
        dict: Thống kê bao gồm count, missing, unique, dtype
              và các stats numeric (min, max, mean, median, std, q1, q3, iqr)
              hoặc top_values cho categorical
    """
    stats = {
        "count": len(df[col]),
        "missing": df[col].isnull().sum(),
        "missing_pct": round(df[col].isnull().sum() / len(df) * 100, 1),
        "unique": df[col].nunique(),
        "dtype": str(df[col].dtype)
    }
    
    if df[col].dtype in [np.float64, np.int64]:
        stats.update({
            "min": df[col].min(),
            "max": df[col].max(),
            "mean": df[col].mean(),
            "median": df[col].median(),
            "std": df[col].std(),
            "q1": df[col].quantile(0.25),
            "q3": df[col].quantile(0.75),
            "iqr": df[col].quantile(0.75) - df[col].quantile(0.25)
        })
    else:
        stats["top_values"] = df[col].value_counts().head(TOP_N_VALUES).to_dict()
    
    return stats

@st.cache_data
def compute_data_quality_score(df: pd.DataFrame) -> dict:
    """
    Tính Data Quality Score dựa trên 4 tiêu chí.

    Args:
        df: Input DataFrame cần đánh giá

    Returns:
        dict: Score breakdown {
            'completeness': float (0-100),
            'uniqueness': float (0-100),
            'validity': float (0-100),
            'overall': float (0-100),
            'total_cells': int,
            'filled_cells': int,
            'dup_rows': int,
            'outlier_count': int
        }
    """
    total_cells = df.shape[0] * df.shape[1]
    filled_cells = total_cells - df.isnull().sum().sum()
    completeness = filled_cells / total_cells * 100 if total_cells > 0 else 0
    
    dup_rows = df.duplicated().sum()
    uniqueness = (1 - dup_rows / len(df)) * 100 if len(df) > 0 else 0
    
    num_cols = df.select_dtypes(include=[np.number]).columns
    outlier_count = 0
    for c in num_cols:
        q1, q3 = df[c].quantile(0.25), df[c].quantile(0.75)
        iqr = q3 - q1
        outliers = ((df[c] < q1 - 1.5 * iqr) | (df[c] > q3 + 1.5 * iqr)).sum()
        outlier_count += outliers
    
    validity = max(0, 100 - (outlier_count / total_cells * 100)) if total_cells > 0 else 0
    
    quality_score = (
        completeness * 0.3 + 
        uniqueness * 0.25 + 
        validity * 0.25 + 
        100 * 0.2  # consistency (simplified)
    )
    
    return {
        "completeness": round(completeness, 1),
        "uniqueness": round(uniqueness, 1),
        "validity": round(validity, 1),
        "overall": round(quality_score, 1),
        "total_cells": total_cells,
        "filled_cells": filled_cells,
        "dup_rows": int(dup_rows),
        "outlier_count": int(outlier_count)
    }

@st.cache_data
def generate_data_dictionary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tạo Data Dictionary (metadata) cho dataset.

    Args:
        df: Input DataFrame

    Returns:
        pd.DataFrame: Data Dictionary với các cột:
            Column, Type, Dtype, Non-Null, Null, Null%, Unique, Sample
    """
    dict_data = []
    for col in df.columns:
        col_type = "Numeric" if df[col].dtype in [np.float64, np.int64] else "Categorical"
        if "date" in col.lower() or "time" in col.lower():
            col_type = "DateTime"
        
        dict_data.append({
            "Column": col,
            "Type": col_type,
            "Dtype": str(df[col].dtype),
            "Non-Null": df[col].count(),
            "Null": df[col].isnull().sum(),
            "Null%": round(df[col].isnull().sum() / len(df) * 100, 1),
            "Unique": df[col].nunique(),
            "Sample": str(df[col].dropna().iloc[0])[:50] if len(df[col].dropna()) > 0 else "N/A"
        })
    
    return pd.DataFrame(dict_data)

def validate_dataframe(df: pd.DataFrame, min_rows: int = 5, min_cols: int = 1) -> Tuple[bool, str]:
    """
    Validate dataframe trước khi phân tích.

    Args:
        df: Input DataFrame
        min_rows: Số dòng tối thiểu (default: 5)
        min_cols: Số cột tối thiểu (default: 1)

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if df is None:
        return False, "Dataset is None"
    if df.empty:
        return False, "Dataset rỗng"
    if len(df) < min_rows:
        return False, f"Cần ít nhất {min_rows} dòng (hiện có {len(df)})"
    if len(df.columns) < min_cols:
        return False, f"Cần ít nhất {min_cols} cột (hiện có {len(df.columns)})"
    return True, "OK"

def safe_execute(func, error_msg: str = "Lỗi thực thi", default=None):
    """
    Wrapper để execute function với error handling.

    Args:
        func: Function cần execute
        error_msg: Thông báo lỗi hiển thị (default: "Lỗi thực thi")
        default: Giá trị trả về nếu có lỗi (default: None)

    Returns:
        Kết quả của func hoặc default nếu có lỗi
    """
    try:
        return func()
    except Exception as e:
        st.error(f"❌ {error_msg}: {str(e)}")
        return default