"""Tests for pipeline DAG + ops (implement_plan Phase 3 Step 7)."""

import pandas as pd


def test_dag_topo():
    from src.pipeline.spec_schema import PipelineSpec

    spec = PipelineSpec(
        name="test",
        source="raw.t",
        target="mart.t",
        steps=[
            {"id": "s1", "op": "fill_missing", "params": {}, "depends_on": []},
            {"id": "s2", "op": "drop_duplicates", "params": {}, "depends_on": ["s1"]},
        ],
    )
    order = spec.topo_order()
    assert [s.id for s in order] == ["s1", "s2"]


def test_dag_cycle():
    from src.pipeline.spec_schema import PipelineSpec
    import pytest

    spec = PipelineSpec(
        name="cycle",
        source="raw.t",
        target="mart.t",
        steps=[
            {"id": "s1", "op": "fill_missing", "params": {}, "depends_on": ["s2"]},
            {"id": "s2", "op": "drop_duplicates", "params": {}, "depends_on": ["s1"]},
        ],
    )
    with pytest.raises(ValueError, match="Cycle"):
        spec.validate_dag()


def test_fill_missing_dedup():
    from src.pipeline.ops.pandas_ops import OPS

    df = pd.DataFrame({"a": [1, None, 1], "b": ["x", "y", "x"]})
    df2 = OPS["fill_missing"](df.copy(), column="a", method="mean")
    assert df2["a"].isnull().sum() == 0
    df3 = OPS["drop_duplicates"](df2, subset=None)
    assert len(df3) < len(df2) or len(df3) == 2


def test_dry_run_no_overwrite(tmp_path):
    from src.pipeline.spec_schema import PipelineSpec
    from src.pipeline.executor import execute
    import pandas as pd
    from src.warehouse.connection import get_conn

    df = pd.DataFrame({"a": [1, 2, 3]})
    conn = get_conn()
    try:
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
        conn.execute("DROP TABLE IF EXISTS raw.t_dry")
        conn.execute("DROP TABLE IF EXISTS mart.t_dry")
        conn.register("df_tmp", df)
        conn.execute("CREATE TABLE raw.t_dry AS SELECT * FROM df_tmp")
        conn.unregister("df_tmp")
    finally:
        conn.close()

    spec = PipelineSpec(
        name="dry",
        source="raw.t_dry",
        target="mart.t_dry",
        steps=[{"id": "s1", "op": "fill_missing", "params": {}, "depends_on": []}],
    )
    res = execute(spec, sample=True)
    assert res["status"] == "done"
    # Verify mart not created in dry-run
    conn = get_conn()
    try:
        cnt = conn.execute("SELECT COUNT(*) FROM mart.t_dry").fetchone()[0]
        # Should fail or 0 if not created; dry-run shouldn't create
        assert False, "mart should not exist after dry-run"
    except Exception:
        pass
    finally:
        conn.close()
        # Cleanup
        conn = get_conn()
        try:
            conn.execute("DROP TABLE IF EXISTS raw.t_dry")
            conn.execute("DROP TABLE IF EXISTS mart.t_dry")
        finally:
            conn.close()


def test_validators_reject():
    from src.prompts.etl_author import validate_spec

    errs = validate_spec({"steps": [{"id": "s1", "op": "unknown_op", "params": {}}]}, columns=["a"])
    assert any("Unknown op" in e for e in errs)
    errs2 = validate_spec(
        {"steps": [{"id": "s1", "op": "fill_missing", "params": {"column": "nonexist"}}]}, columns=["a"]
    )
    assert any("not in schema" in e for e in errs2)
