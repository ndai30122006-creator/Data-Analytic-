"""Helper functions extracted from app.py"""

from __future__ import annotations

import logging
from typing import Optional

import pandas as pd

from src.utils.config import MAX_COLS_UPLOAD, MAX_FILE_SIZE_BYTES, MAX_ROWS_UPLOAD
from src.utils.exceptions import DataValidationError, handle_error
from src.utils.optional_deps import cache_data, st
from src.utils.performance import check_file_size, warn_if_large_dataset

logger = logging.getLogger(__name__)


@cache_data(
    hash_funcs={
        "streamlit.runtime.uploaded_file_manager.UploadedFile": lambda f: (
            getattr(f, "name", getattr(f, "filename", "")),
            getattr(f, "size", 0),
        ),
        "starlette.datastructures.UploadFile": lambda f: (getattr(f, "filename", ""), getattr(f, "size", 0)),
    }
)
def load_and_process_data(_file) -> Optional[pd.DataFrame]:
    """
    Load và cache dữ liệu từ file upload (CSV/Excel).

    Args:
        file: Uploaded file object từ Streamlit file_uploader

    Returns:
        pd.DataFrame nếu thành công, None nếu lỗi

    Raises:
        Không raise — tất cả exception được catch và xử lý qua handle_error()
    """
    try:
        if _file is None:
            raise DataValidationError("File không tồn tại")

        # Support both Streamlit UploadedFile (.name) and Starlette UploadFile (.filename, .file)
        fname = getattr(_file, "name", None) or getattr(_file, "filename", "") or "upload.csv"
        # Starlette UploadFile wraps .file; ensure seek/tell work
        underlying = getattr(_file, "file", _file)
        try:
            _file.seek(0, 2)
            file_size = _file.tell()
            _file.seek(0)
        except Exception:
            try:
                underlying.seek(0, 2)
                file_size = underlying.tell()
                underlying.seek(0)
                _file.seek(0)
            except Exception:
                file_size = 0
        valid_size, size_msg = check_file_size(file_size, MAX_FILE_SIZE_BYTES)
        if not valid_size:
            raise DataValidationError(size_msg)

        # Reset before read
        try:
            _file.seek(0)
        except Exception:
            pass
        if fname.endswith(".csv"):
            # For Starlette, read via underlying file if needed
            try:
                df = pd.read_csv(_file)
            except Exception:
                underlying.seek(0)
                df = pd.read_csv(underlying)
        elif fname.endswith((".xlsx", ".xls")):
            try:
                df = pd.read_excel(_file, engine="openpyxl")
            except Exception:
                underlying.seek(0)
                df = pd.read_excel(underlying, engine="openpyxl")
        else:
            raise DataValidationError(
                f"Định dạng '{fname.split('.')[-1]}' không hỗ trợ. " "Chấp nhận: .csv, .xlsx, .xls"
            )

        if df.empty:
            raise DataValidationError("File rỗng, không có dữ liệu")

        warning = warn_if_large_dataset(len(df), len(df.columns), MAX_ROWS_UPLOAD, MAX_COLS_UPLOAD)
        if warning:
            try:
                st.warning(warning)
            except Exception:
                pass

        logger.info("Loaded file '%s': %d rows x %d cols", fname, *df.shape)
        return df

    except DataValidationError as e:
        handle_error(e, "load_and_process_data")
        return None
    except pd.errors.EmptyDataError:
        handle_error(DataValidationError("File CSV rỗng"), "load_and_process_data")
        return None
    except pd.errors.ParserError as e:
        handle_error(DataValidationError(f"Lỗi parse file: {e}"), "load_and_process_data")
        return None
    except Exception as e:
        logger.error(
            "Unexpected error loading file '%s': %s",
            getattr(_file, "name", getattr(_file, "filename", "unknown")),
            e,
            exc_info=True,
        )
        try:
            st.error(f"❌ **Lỗi đọc file:** {str(e)}")
            st.caption("💡 Kiểm tra file có bị hỏng hoặc không đúng định dạng")
        except Exception:
            pass
        return None
