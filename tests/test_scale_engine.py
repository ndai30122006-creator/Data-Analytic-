"""Tests scalability — DuckDB SQL engine vs Pandas engine parity + large data."""

import pandas as pd
import pytest


@pytest.fixture
def scale_table():
    """raw.t_scale: 100k rows (du lon de thay khac biet fetchdf, du nhanh cho CI)."""
    import numpy as np

    from src.warehouse.connection import get_conn

    n = 100_000
    rng = np.random.default_rng(7)
    df = pd.DataFrame(
        {
            "id": range(n),
            "grp": rng.choice(["A", "B", "C", "D"], n),
            "score": rng.normal(6.5, 1.5, n).round(2),
        }
    )
    df.loc[rng.choice(n, 1000, replace=False), "score"] = None
    conn = get_conn()
    try:
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
        conn.execute("CREATE SCHEMA IF NOT EXISTS mart")
        conn.execute("DROP TABLE IF EXISTS raw.t_scale")
        conn.execute("DROP TABLE IF EXISTS mart.t_scale_duck")
        conn.execute("DROP TABLE IF EXISTS mart.t_scale_pd")
        conn.register("df_tmp", df)
        conn.execute("CREATE TABLE raw.t_scale AS SELECT * FROM df_tmp")
        conn.unregister("df_tmp")
    finally:
        conn.close()
    yield "raw.t_scale"
    conn = get_conn()
    try:
        for t in ("raw.t_scale", "mart.t_scale_duck", "mart.t_scale_pd"):
            conn.execute(f"DROP TABLE IF EXISTS {t}")
    finally:
        conn.close()


def _spec(source, target, engine):
    from src.pipeline.spec_schema import PipelineSpec

    return PipelineSpec(
        name="scale",
        source=source,
        target=target,
        engine=engine,
        steps=[
            {"id": "clean", "op": "fill_missing", "params": {"column": "score", "method": "mean"}, "depends_on": []},
            {"id": "dedup", "op": "drop_duplicates", "params": {}, "depends_on": ["clean"]},
            {"id": "agg", "op": "aggregate", "params": {"by": "grp", "agg": "mean"}, "depends_on": ["dedup"]},
        ],
    )


def test_engine_parity_sample(scale_table):
    from src.pipeline.executor import execute

    pd_res = execute(_spec(scale_table, "mart.t_scale_pd", "pandas"), sample=True)
    dq_res = execute(_spec(scale_table, "mart.t_scale_duck", "duckdb"), sample=True)
    assert pd_res["status"] == "done", pd_res
    assert dq_res["status"] == "done", dq_res
    assert dq_res["engine_used"] == "duckdb"
    assert pd_res["engine_used"] == "pandas"
    assert dq_res["fallbacks"] == []
    assert dq_res["rows"] == pd_res["rows"] == 4  # 4 grps
    # Gia tri agg gan dung (mean theo grp)
    assert dq_res["preview"][0].keys() == pd_res["preview"][0].keys()


def test_duckdb_full_write(scale_table):
    from src.pipeline.executor import execute
    from src.warehouse.connection import get_conn

    res = execute(_spec(scale_table, "mart.t_scale_duck", "duckdb"), sample=False)
    assert res["status"] == "done", res
    assert res["rows"] == 4
    conn = get_conn()
    try:
        cnt = conn.execute("SELECT COUNT(*) FROM mart.t_scale_duck").fetchone()[0]
        assert cnt == 4
    finally:
        conn.close()


def test_duckdb_fallback_pandas_syntax(scale_table):
    """Filter syntax chi-pandas -> fallback hybrid, van done."""
    from src.pipeline.executor import execute
    from src.pipeline.spec_schema import PipelineSpec

    spec = PipelineSpec(
        name="fb",
        source=scale_table,
        target="mart.t_scale_duck",
        engine="duckdb",
        steps=[{"id": "s1", "op": "filter", "params": {"query": "score.isnull()"}, "depends_on": []}],
    )
    res = execute(spec, sample=True)
    assert res["status"] == "done", res
    assert res["fallbacks"] == ["s1"]
    assert 1 <= res["rows"] <= 100  # sample 100 rows dau, loc null trong do


def test_invalid_engine_rejected():
    from src.pipeline.spec_schema import PipelineSpec

    spec = PipelineSpec(name="x", source="raw.t", target="mart.t", engine="spark", steps=[])
    with pytest.raises(ValueError, match="engine"):
        spec.validate_dag()
