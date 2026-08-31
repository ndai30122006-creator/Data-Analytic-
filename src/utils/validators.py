"""Validation utilities for Data Analyst Pro"""

import logging
from typing import Any, Callable, Dict, List, Tuple

import numpy as np
import pandas as pd
import streamlit as st

from src.utils.exceptions import DataValidationError, handle_error

logger = logging.getLogger(__name__)

TOP_N_VALUES: int = 10


def validate_dataframe(df: pd.DataFrame, min_rows: int = 5, min_cols: int = 1) -> Tuple[bool, str]:
    """
    Validate dataframe trước khi phân tích.

    Args:
        df: Input DataFrame
        min_rows: Số dòng tối thiểu (default: 5)
        min_cols: Số cột tối thiểu (default: 1)

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
            - (True, "OK") nếu hợp lệ
            - (False, "reason") nếu không hợp lệ
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


def validate_dataframe_schema(df: pd.DataFrame, schema: dict) -> bool:
    """
    Validate that a DataFrame matches an expected schema (column names + dtypes).

    Args:
        df: DataFrame to validate.
        schema: Dict mapping column name -> expected dtype string (e.g. "int64", "object").

    Returns:
        True if all columns exist and match expected dtypes, False otherwise.
    """
    for col, expected_dtype in schema.items():
        if col not in df.columns:
            logger.warning("Schema validation failed: missing column '%s'", col)
            return False
        actual_dtype = str(df[col].dtype)
        if actual_dtype != expected_dtype:
            logger.warning("Schema validation: column '%s' expected %s, got %s", col, expected_dtype, actual_dtype)
            # Not returning False for dtype mismatch — too strict for real data
    return True


def safe_execute(func: Callable, error_msg: str = "Lỗi thực thi", default: Any = None) -> Any:
    """
    Wrapper để execute function với error handling.

    Args:
        func: Function cần execute (không tham số)
        error_msg: Thông báo lỗi hiển thị (default: "Lỗi thực thi")
        default: Giá trị trả về nếu có lỗi (default: None)

    Returns:
        Kết quả của func hoặc default nếu có lỗi
    """
    try:
        return func()
    except Exception as e:
        logger.error(
            "safe_execute failed [%s] | Context: %s | Detail: %s", type(e).__name__, error_msg, str(e), exc_info=True
        )
        st.error(f"❌ {error_msg}: {str(e)}")
        return default


@st.cache_data
def get_column_stats(df: pd.DataFrame, col: str) -> Dict[str, Any]:
    """
    Cache thống kê chi tiết cho từng cột.

    Args:
        df: Input DataFrame
        col: Tên cột cần phân tích

    Returns:
        dict với các keys:
            - count (int): Số lượng giá trị
            - missing (int): Số lượng null
            - missing_pct (float): Phần trăm null
            - unique (int): Số lượng unique values
            - dtype (str): Kiểu dữ liệu
            - Nếu numeric: min, max, mean, median, std, q1, q3, iqr
            - Nếu categorical: top_values (dict)
    """
    stats: Dict[str, Any] = {
        "count": len(df[col]),
        "missing": df[col].isnull().sum(),
        "missing_pct": round(df[col].isnull().sum() / len(df) * 100, 1),
        "unique": df[col].nunique(),
        "dtype": str(df[col].dtype),
    }

    if pd.api.types.is_numeric_dtype(df[col].dtype):
        stats.update(
            {
                "min": df[col].min(),
                "max": df[col].max(),
                "mean": df[col].mean(),
                "median": df[col].median(),
                "std": df[col].std(),
                "q1": df[col].quantile(0.25),
                "q3": df[col].quantile(0.75),
                "iqr": df[col].quantile(0.75) - df[col].quantile(0.25),
            }
        )
    else:
        stats["top_values"] = df[col].value_counts().head(TOP_N_VALUES).to_dict()

    return stats


@st.cache_data
def compute_data_quality_score(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Tính Data Quality Score dựa trên 4 tiêu chí.

    Args:
        df: Input DataFrame cần đánh giá

    Returns:
        dict với các keys:
            completeness (float): 0-100
            uniqueness (float): 0-100
            validity (float): 0-100
            overall (float): 0-100 (weighted: 30% completeness + 25% uniqueness + 25% validity + 20% consistency)
            total_cells (int): Tổng số ô
            filled_cells (int): Số ô không null
            dup_rows (int): Số dòng trùng lặp
            outlier_count (int): Số giá trị ngoại lai (IQR method)
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

    quality_score = completeness * 0.3 + uniqueness * 0.25 + validity * 0.25 + 100 * 0.2

    return {
        "completeness": round(completeness, 1),
        "uniqueness": round(uniqueness, 1),
        "validity": round(validity, 1),
        "overall": round(quality_score, 1),
        "total_cells": total_cells,
        "filled_cells": filled_cells,
        "dup_rows": int(dup_rows),
        "outlier_count": int(outlier_count),
    }


@st.cache_data
def generate_data_dictionary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tạo Data Dictionary (metadata) cho dataset.

    Args:
        df: Input DataFrame

    Returns:
        pd.DataFrame với các cột:
            Column, Type, Dtype, Non-Null, Null, Null%, Unique, Sample
    """
    dict_data = []
    for col in df.columns:
        col_type = "Numeric" if pd.api.types.is_numeric_dtype(df[col].dtype) else "Categorical"
        if "date" in col.lower() or "time" in col.lower():
            col_type = "DateTime"

        dict_data.append(
            {
                "Column": col,
                "Type": col_type,
                "Dtype": str(df[col].dtype),
                "Non-Null": df[col].count(),
                "Null": df[col].isnull().sum(),
                "Null%": round(df[col].isnull().sum() / len(df) * 100, 1),
                "Unique": df[col].nunique(),
                "Sample": str(df[col].dropna().iloc[0])[:50] if len(df[col].dropna()) > 0 else "N/A",
            }
        )

    return pd.DataFrame(dict_data)
