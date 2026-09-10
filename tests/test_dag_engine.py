"""Tests P0/P1 — real DAG semantics: planner, context, explicit inputs, merge."""

import pandas as pd
import pytest


@pytest.fixture
def dag_table():
    """raw.t_dag: 6 rows, 2 grps, 1 dup, 1 missing."""
    from src.warehouse.connection import get_conn

    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 5],
            "grp": ["A", "A", "B", "B", "A", "A"],
            "score": [5.0, None, 7.0, 8.0, 6.0, 6.0],
        }
    )
    conn = get_conn()
    try:
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
        conn.execute("CREATE SCHEMA IF NOT EXISTS mart")
        conn.execute("DROP TABLE IF EXISTS raw.t_dag")
        conn.execute("DROP TABLE IF EXISTS mart.t_dag")
        conn.register("df_tmp", df)
        conn.execute("CREATE TABLE raw.t_dag AS SELECT * FROM df_tmp")
        conn.unregister("df_tmp")
    finally:
        conn.close()
    yield "raw.t_dag"
    conn = get_conn()
    try:
        conn.execute("DROP TABLE IF EXISTS raw.t_dag")
        conn.execute("DROP TABLE IF EXISTS mart.t_dag")
    finally:
        conn.close()


def _spec(source, target, steps):
    from src.pipeline.spec_schema import PipelineSpec

    return PipelineSpec(name="dag", source=source, target=target, steps=steps)


def test_planner_levels_diamond():
    from src.pipeline.planner import plan

    spec = _spec(
        "raw.t",
        "mart.t",
        [
            {"id": "clean", "op": "drop_duplicates", "params": {}, "depends_on": []},
            {"id": "aggregate", "op": "aggregate", "params": {"by": "grp", "agg": "mean"}, "depends_on": ["clean"]},
            {"id": "filter", "op": "filter", "params": {"query": "score >= 6"}, "depends_on": ["clean"]},
            {"id": "final", "op": "merge", "params": {"how": "concat"}, "depends_on": ["aggregate", "filter"]},
        ],
    )
    p = plan(spec)
    assert p.levels == [["clean"], ["aggregate", "filter"], ["final"]]
    assert p.sink == "final"
    assert [s.id for s in p.order] == ["clean", "aggregate", "filter", "final"]


def test_diamond_merge_concat(dag_table):
    from src.pipeline.executor import execute

    spec = _spec(
        dag_table,
        "mart.t_dag",
        [
            {"id": "clean", "op": "drop_duplicates", "params": {}, "depends_on": []},
            {"id": "aggregate", "op": "aggregate", "params": {"by": "grp", "agg": "mean"}, "depends_on": ["clean"]},
            {"id": "filter", "op": "filter", "params": {"query": "score >= 6"}, "depends_on": ["clean"]},
            {"id": "final", "op": "merge", "params": {"how": "concat"}, "depends_on": ["aggregate", "filter"]},
        ],
    )
    res = execute(spec, sample=True)
    assert res["status"] == "done", res
    # clean: 6 rows - 1 dup = 5; aggregate -> 2 rows (A,B); filter score>=6 -> 3 rows; concat = 5
    assert res["rows"] == 5, res
    assert res["sink"] == "final"
    assert res["levels"] == [["clean"], ["aggregate", "filter"], ["final"]]


def test_merge_join_on_key(dag_table):
    from src.pipeline.executor import execute

    spec = _spec(
        dag_table,
        "mart.t_dag",
        [
            {"id": "a", "op": "filter", "params": {"query": "grp == 'A'"}, "depends_on": []},
            {"id": "b", "op": "filter", "params": {"query": "score >= 6"}, "depends_on": []},
            {"id": "final", "op": "merge", "params": {"how": "merge", "on": "id"}, "depends_on": ["a", "b"]},
        ],
    )
    res = execute(spec, sample=True)
    assert res["status"] == "done", res
    # A rows ids {1,2,5} ∩ score>=6 ids {3,4,5,6(dup)} = {5} (dup removed? no dedup here: A has 5 twice)
    assert res["rows"] >= 1, res


def test_multi_dep_non_merge_rejected(dag_table):
    from src.pipeline.executor import execute

    spec = _spec(
        dag_table,
        "mart.t_dag",
        [
            {"id": "a", "op": "drop_duplicates", "params": {}, "depends_on": []},
            {"id": "b", "op": "drop_duplicates", "params": {}, "depends_on": []},
            {"id": "c", "op": "drop_duplicates", "params": {}, "depends_on": ["a", "b"]},
        ],
    )
    res = execute(spec, sample=True)
    assert res["status"] == "failed"
    assert "merge" in res["error"]


def test_no_dep_step_uses_source(dag_table):
    """Step khong depends_on doc source (khong phai output step truoc)."""
    from src.pipeline.executor import execute

    spec = _spec(
        dag_table,
        "mart.t_dag",
        [
            {"id": "s1", "op": "filter", "params": {"query": "score > 100"}, "depends_on": []},
            {"id": "s2", "op": "drop_duplicates", "params": {}, "depends_on": []},
        ],
    )
    res = execute(spec, sample=True)
    assert res["status"] == "done", res
    # s2 la sink, doc source (6 rows - 1 dup = 5) chu khong phai output rong cua s1
    assert res["rows"] == 5, res


def test_context_resolve_unit():
    from src.pipeline.context import ExecutionContext

    df = pd.DataFrame({"a": [1]})
    ctx = ExecutionContext(df)
    assert ctx.resolve(type("S", (), {"id": "x", "depends_on": []})()).equals(df)
    ctx.put("s1", pd.DataFrame({"a": [2]}))
    out = ctx.resolve(type("S", (), {"id": "y", "depends_on": ["s1"]})())
    assert isinstance(out, pd.DataFrame) and out["a"].iloc[0] == 2
    ctx.put("s2", pd.DataFrame({"a": [3]}))
    out = ctx.resolve(type("S", (), {"id": "z", "depends_on": ["s1", "s2"]})())
    assert isinstance(out, dict) and set(out) == {"s1", "s2"}
