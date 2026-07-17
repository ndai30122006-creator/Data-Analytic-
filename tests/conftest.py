"""Pytest fixtures and configuration for Data Analyst Pro tests."""
import os
import sys
import tempfile
from pathlib import Path
from typing import Generator

import pytest
import pandas as pd
import numpy as np

# Ensure src is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Use a temporary database for all tests to avoid polluting the real users.db
_temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_temp_db_path = _temp_db.name
_temp_db.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_temp_db_path}"


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Create a sample DataFrame for testing."""
    np.random.seed(42)
    return pd.DataFrame({
        "student_id": [f"S{i:03d}" for i in range(1, 101)],
        "score": np.random.normal(6.5, 1.5, 100).clip(0, 10),
        "attendance": np.random.uniform(60, 100, 100),
        "study_hours": np.random.exponential(3, 100).clip(0, 15),
        "grade": np.random.choice(["A", "B", "C", "D", "F"], 100, p=[0.2, 0.3, 0.3, 0.1, 0.1]),
        "department": np.random.choice(["Math", "Science", "Arts", "Engineering"], 100),
        "gender": np.random.choice(["M", "F"], 100),
    })


@pytest.fixture
def sample_df_with_missing() -> pd.DataFrame:
    """Create a sample DataFrame with missing values."""
    np.random.seed(42)
    df = pd.DataFrame({
        "x": np.random.normal(0, 1, 100),
        "y": np.random.normal(0, 1, 100),
        "z": np.random.normal(0, 1, 100),
        "category": np.random.choice(["A", "B", "C"], 100),
    })
    # Introduce missing values
    mask = np.random.random(100) < 0.15
    df.loc[mask, "x"] = np.nan
    mask = np.random.random(100) < 0.10
    df.loc[mask, "y"] = np.nan
    return df


@pytest.fixture
def sample_df_no_categorical() -> pd.DataFrame:
    """Create a DataFrame with only numeric columns."""
    np.random.seed(42)
    return pd.DataFrame({
        "a": np.random.normal(0, 1, 50),
        "b": np.random.normal(0, 1, 50),
        "c": np.random.normal(0, 1, 50),
    })


@pytest.fixture
def sample_df_no_numeric() -> pd.DataFrame:
    """Create a DataFrame with only categorical columns."""
    return pd.DataFrame({
        "name": [f"Person_{i}" for i in range(20)],
        "city": np.random.choice(["HN", "HCM", "DN"], 20),
        "status": np.random.choice(["active", "inactive"], 20),
    })


@pytest.fixture
def temp_db_path() -> Generator[str, None, None]:
    """Create a temporary SQLite database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    yield db_path
    # Cleanup
    try:
        os.unlink(db_path)
    except OSError:
        pass
