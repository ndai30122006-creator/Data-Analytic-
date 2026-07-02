"""Validation utilities for Data Analyst Pro"""
from typing import Tuple, Callable, Any
import pandas as pd
import logging
import streamlit as st

from src.utils.exceptions import DataValidationError, handle_error

logger = logging.getLogger(__name__)


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
        logger.error("safe_execute failed [%s] | Context: %s | Detail: %s", type(e).__name__, error_msg, str(e), exc_info=True)
        st.error(f"❌ {error_msg}: {str(e)}")
        return default