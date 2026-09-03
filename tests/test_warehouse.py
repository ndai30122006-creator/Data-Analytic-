"""Tests for warehouse ingest (P1 Step 7)."""

import pandas as pd


def test_ingest_small_csv(tmp_path):
    from src.warehouse.connection import get_conn

    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    conn = get_conn()
    try:
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
        conn.execute("DROP TABLE IF EXISTS raw.test_small")
        conn.register("df_tmp", df)
        conn.execute("CREATE TABLE raw.test_small AS SELECT * FROM df_tmp")
        conn.unregister("df_tmp")
        cnt = conn.execute("SELECT COUNT(*) FROM raw.test_small").fetchone()[0]
        assert cnt == 3
        conn.execute("DROP TABLE IF EXISTS raw.test_small")
    finally:
        conn.close()


def test_warehouse_connection():
    from src.warehouse.connection import get_conn, get_db_path

    conn = get_conn()
    assert conn is not None
    conn.close()
    assert get_db_path().name == "warehouse.duckdb"
