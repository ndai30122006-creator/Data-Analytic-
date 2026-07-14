"""Unit tests for utility modules — Data Analyst Pro v3.0"""
import os
import sys
import tempfile
import pytest
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.performance import safe_n_jobs, check_file_size, warn_if_large_dataset
from src.utils.exceptions import DataValidationError, handle_error
from src.utils.validators import validate_dataframe_schema


class TestPerformanceUtils:
    """Tests for src.utils.performance"""

    def test_safe_n_jobs_default(self):
        """safe_n_jobs should clamp -1 to min(cpu_count, 4)."""
        result = safe_n_jobs(-1, max_jobs=4)
        assert 1 <= result <= 4

    def test_safe_n_jobs_capped(self):
        """safe_n_jobs should never exceed max_jobs."""
        result = safe_n_jobs(100, max_jobs=4)
        assert result <= 4

    def test_safe_n_jobs_min_one(self):
        """safe_n_jobs should return at least 1."""
        result = safe_n_jobs(0, max_jobs=4)
        assert result >= 1

    def test_check_file_size_ok(self):
        """check_file_size returns True for small files."""
        valid, msg = check_file_size(1000, max_bytes=10_000_000)
        assert valid is True
        assert msg == ""

    def test_check_file_size_exceeded(self):
        """check_file_size returns False for oversized files."""
        valid, msg = check_file_size(100_000_000, max_bytes=1_000_000)
        assert valid is False
        assert "exceeds" in msg.lower()

    def test_warn_if_large_dataset_ok(self):
        """warn_if_large_dataset returns None for small datasets."""
        result = warn_if_large_dataset(100, 10, max_rows=500_000, max_cols=200)
        assert result is None

    def test_warn_if_large_dataset_warning(self):
        """warn_if_large_dataset returns warning for large datasets."""
        result = warn_if_large_dataset(600_000, 250, max_rows=500_000, max_cols=200)
        assert result is not None
        assert "rows" in result
        assert "columns" in result


class TestDataValidation:
    """Tests for data validation utilities."""

    def test_data_validation_error(self):
        """DataValidationError should be catchable as Exception."""
        with pytest.raises(DataValidationError):
            raise DataValidationError("Test error")

    def test_handle_error_no_crash(self, caplog):
        """handle_error should log and not crash."""
        try:
            handle_error(ValueError("test"), "test_context", "user_msg")
        except Exception:
            pytest.fail("handle_error should not raise")

    def test_validate_dataframe_schema_valid(self):
        """validate_dataframe_schema passes on correct schema."""
        df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
        schema = {"a": "int64", "b": "object"}
        # This should not raise
        result = validate_dataframe_schema(df, schema)
        assert result is True

    def test_validate_dataframe_schema_invalid(self):
        """validate_dataframe_schema fails on missing column."""
        df = pd.DataFrame({"a": [1, 2]})
        schema = {"a": "int64", "c": "object"}
        result = validate_dataframe_schema(df, schema)
        assert result is False


class TestConfigConstants:
    """Tests for configuration constants."""

    def test_config_imports(self):
        """Core config constants should be accessible."""
        from src.utils.config import (
            MIN_ROWS_VALIDATION, MAX_FILE_SIZE_MB,
            MAIN_TABS, STATISTICS_TABS,
            N_JOBS_MAX, FEATURE_FLAGS
        )
        assert MIN_ROWS_VALIDATION >= 1
        assert MAX_FILE_SIZE_MB >= 1
        assert len(MAIN_TABS) >= 5
        assert len(STATISTICS_TABS) >= 4
        assert N_JOBS_MAX >= 1
        assert "show_landing_page" in FEATURE_FLAGS

    def test_feature_flags(self):
        """FEATURE_FLAGS should have all expected keys."""
        from src.utils.config import FEATURE_FLAGS
        expected_keys = [
            "show_landing_page", "show_smart_search",
            "show_deep_analysis", "show_compare_tab",
            "show_ai_insights"
        ]
        for key in expected_keys:
            assert key in FEATURE_FLAGS, f"Missing feature flag: {key}"