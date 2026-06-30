"""Centralized error handling for Data Analyst Pro"""
import logging
import streamlit as st
from typing import Callable, Any, Optional, Dict, Type, Union
from loguru import logger

# Keep standard logger for FastAPI compatibility (api.py)
_std_logger = logging.getLogger(__name__)


class DataValidationError(Exception):
    """Lỗi validation dữ liệu đầu vào"""
    pass


class DataProcessingError(Exception):
    """Lỗi xử lý dữ liệu"""
    pass


class ModelTrainingError(Exception):
    """Lỗi training model"""
    pass


class ImportError(Exception):
    """Lỗi thiếu thư viện"""
    pass


ERROR_MESSAGES: Dict[Type[Exception], Dict[str, str]] = {
    DataValidationError: {
        "title": "❌ Dữ liệu không hợp lệ",
        "icon": "❌",
        "default": "Kiểm tra lại dữ liệu đầu vào",
    },
    DataProcessingError: {
        "title": "⚙️ Lỗi xử lý dữ liệu",
        "icon": "⚙️",
        "default": "Có lỗi trong quá trình xử lý",
    },
    ModelTrainingError: {
        "title": "🧠 Lỗi training model",
        "icon": "🧠",
        "default": "Model training thất bại",
    },
    ImportError: {
        "title": "📦 Thiếu thư viện",
        "icon": "📦",
        "default": "Cài đặt thư viện: pip install <package>",
    },
    ValueError: {
        "title": "❌ Giá trị không hợp lệ",
        "icon": "❌",
        "default": "Kiểm tra lại giá trị nhập vào",
    },
    MemoryError: {
        "title": "🧠 Dataset quá lớn",
        "icon": "🧠",
        "default": "Giảm kích thước dataset hoặc tăng RAM",
    },
    KeyError: {
        "title": "🔑 Không tìm thấy cột",
        "icon": "🔑",
        "default": "Cột không tồn tại trong dữ liệu",
    },
    IndexError: {
        "title": "📏 Chỉ số ngoài phạm vi",
        "icon": "📏",
        "default": "Kiểm tra lại chỉ số truy cập",
    },
    ZeroDivisionError: {
        "title": "➗ Lỗi chia cho 0",
        "icon": "➗",
        "default": "Dữ liệu không đủ biến động",
    },
    TypeError: {
        "title": "🔤 Sai kiểu dữ liệu",
        "icon": "🔤",
        "default": "Kiểm tra lại kiểu dữ liệu đầu vào",
    },
}


def handle_error(error: Exception, context: str = "", fallback_message: str = "") -> None:
    """
    Xử lý lỗi tập trung: log chi tiết + hiển thị user-friendly message.

    Sử dụng ERROR_MESSAGES mapping để tra cứu thông báo phù hợp theo loại exception.
    Nếu loại lỗi không có trong mapping, hiển thị fallback_message hoặc str(error).

    Args:
        error: Exception object cần xử lý
        context: Ngữ cảnh xảy ra lỗi (tên function, operation). Ví dụ: "load_and_process_data"
        fallback_message: Message mặc định nếu loại lỗi không có trong ERROR_MESSAGES

    Returns:
        None — hiển thị trực tiếp lên Streamlit UI

    Example:
        >>> try:
        ...     df = pd.read_csv("invalid.csv")
        ... except Exception as e:
        ...     handle_error(e, "load_csv", "Không thể đọc file CSV")
    """
    error_type = type(error)
    error_info: Dict[str, str] = ERROR_MESSAGES.get(error_type, {
        "title": "🚨 Lỗi không xác định",
        "icon": "🚨",
        "default": fallback_message or str(error),
    })

    # Log chi tiết cho developer
    logger.error(
        "[{}] {} | Context: {} | Detail: {}",
        error_type.__name__,
        error_info["title"],
        context,
        str(error),
        exc_info=True,
    )

    # Hiển thị user-friendly message
    st.error(f"{error_info['icon']} **{error_info['title']}**")
    if context:
        st.caption(f"📍 {context}")
    st.caption(f"💡 {error_info['default']}")


def safe_run(
    func: Callable[..., Any],
    context: str = "",
    fallback: Any = None,
    **kwargs: Any
) -> Any:
    """
    Execute function với error handling tự động.

    Wrapper an toàn để thực thi function. Tự động bắt các exception phổ biến
    (DataValidationError, ValueError, KeyError, ...) và xử lý qua handle_error().
    Các exception không xác định được log chi tiết + hiển thị message hệ thống.

    Args:
        func: Function cần execute
        context: Ngữ cảnh (tên operation) để log và hiển thị
        fallback: Giá trị trả về nếu có lỗi (default: None)
        **kwargs: Keyword arguments truyền vào func

    Returns:
        Kết quả của func, hoặc fallback nếu có lỗi

    Raises:
        Không raise exception — tất cả đều được catch và xử lý

    Example:
        >>> result = safe_run(
        ...     func=pd.read_csv,
        ...     context="load_csv",
        ...     fallback=pd.DataFrame(),
        ...     filepath_or_buffer="data.csv"
        ... )
    """
    try:
        return func(**kwargs)
    except (DataValidationError, ValueError, KeyError, IndexError, TypeError, ZeroDivisionError) as e:
        handle_error(e, context)
        return fallback
    except MemoryError as e:
        handle_error(e, context)
        return fallback
    except Exception as e:
        logger.error(
            "Unexpected error [{}] | Context: {} | Detail: {}",
            type(e).__name__, context, str(e), exc_info=True
        )
        st.error(f"🚨 **Lỗi hệ thống:** {str(e)}")
        st.caption(f"📍 {context}" if context else "")
        st.caption("💡 Vui lòng thử lại hoặc liên hệ admin")
        return fallback