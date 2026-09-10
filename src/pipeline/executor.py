"""Executor — DAG run with checkpoint (Plan 04, P0/P1 real DAG semantics).

PipelineSpec -> planner.plan() -> ExecutionContext (named frames) -> ops.
Moi step doc inputs tuong minh theo depends_on (xem context.ExecutionContext);
target = output cua sink (step cuoi topo order).
"""

import re
from typing import Dict

import pandas as pd

from src.pipeline.context import ExecutionContext
from src.pipeline.planner import plan as plan_dag
from src.pipeline.spec_schema import PipelineSpec
from src.warehouse.connection import get_conn, warehouse_write_lock

_VALID_ID = re.compile(r"^(raw|mart)\.[a-zA-Z_][a-zA-Z0-9_]{0,63}$")


def _validate_identifier(name: str) -> str:
    if not _VALID_ID.match(name):
        raise ValueError(f"Invalid identifier {name!r} (must be raw/mart + alphanum/_)")
    # Quote safely
    schema, table = name.split(".", 1)
    return f'"{schema}"."{table}"'


def sanitize_for_json(obj):
    """Chuyen NaN/Inf -> None de JSONResponse khong 500 (muc smoke-fix)."""
    import math

    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize_for_json(v) for v in obj]
    # pandas/numpy scalar co NaN
    try:
        import math as _m

        if obj is not None and not isinstance(obj, (str, bool, int)) and hasattr(obj, "item"):
            v = obj.item()
            if isinstance(v, float) and (_m.isnan(v) or _m.isinf(v)):
                return None
            return v
    except Exception:
        pass
    return obj


def execute(spec: PipelineSpec, sample: bool = False) -> Dict:
    """Execute spec DAG; sample=True limits 100 rows, no overwrite mart."""
    dag = plan_dag(spec)
    order = dag.order

    # Validate identifiers before any SQL
    try:
        src_q = _validate_identifier(spec.source)
        tgt_q = _validate_identifier(spec.target)
    except ValueError as e:
        return {"status": "failed", "error": str(e)}

    conn = get_conn()
    try:
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
        conn.execute("CREATE SCHEMA IF NOT EXISTS mart")
        # Load source
        try:
            df = conn.execute(f"SELECT * FROM {src_q}").fetchdf()
        except Exception as e:
            return {"status": "failed", "error": f"source {spec.source} not found: {e}"}

        if sample:
            df = df.head(100)

        # Execution context: named frames + explicit inputs (P0/P1)
        ctx = ExecutionContext(df)
        results = {"source": df}
        current = df

        # Import ops
        from src.pipeline.ops.pandas_ops import OPS as PANDAS_OPS
        from src.pipeline.ops.sql_ops import run_sql

        for step in order:
            op = step.op
            params = step.params or {}
            try:
                inputs = ctx.resolve(step)
            except ValueError as e:
                return {"status": "failed", "error": str(e)}

            try:
                if op in PANDAS_OPS:
                    func = PANDAS_OPS[op]
                    if isinstance(inputs, dict):
                        # Multi-input chi op 'merge' duoc nhan dict tuong minh
                        if op != "merge":
                            return {
                                "status": "failed",
                                "error": f"Step {step.id} ({op}) has multiple inputs {list(inputs)}; use op 'merge' (or single depends_on)",
                            }
                        res_df = func(inputs, **params)
                    else:
                        res_df = func(inputs.copy(), **params)
                    if isinstance(res_df, pd.DataFrame):
                        current = res_df
                    else:
                        current = inputs if isinstance(inputs, pd.DataFrame) else current
                elif op == "sql":
                    # ELT mode: dict inputs -> moi dep la 1 view theo ten step;
                    # single input -> prev_view nhu cu ({{prev}} tuong thich nguoc)
                    registered = []
                    try:
                        if isinstance(inputs, dict):
                            for dep_id, dep_df in inputs.items():
                                conn.register(dep_id, dep_df)
                                registered.append(dep_id)
                            default_view = (step.depends_on or ["prev_view"])[-1]
                        else:
                            conn.register("prev_view", inputs)
                            registered.append("prev_view")
                            default_view = "prev_view"
                        q = params.get("query", f"SELECT * FROM {default_view}")
                        q = q.replace("{{prev}}", default_view)
                        res_df = run_sql(conn, q, default_view)
                        current = res_df
                    finally:
                        for v in registered:
                            try:
                                conn.unregister(v)
                            except Exception:
                                pass
                else:
                    return {"status": "failed", "error": f"Unknown op {op}"}
                ctx.put(step.id, current.copy())
                results[step.id] = current.copy()
            except Exception as e:
                return {"status": "failed", "error": f"Step {step.id} ({op}) failed: {e}"}

        # Write to target if not sample — Medium fix: atomic + serialized
        if not sample:
            conn.register("final_df", current)
            try:
                with warehouse_write_lock(timeout=30.0):
                    # CREATE OR REPLACE là 1 statement atomic, tránh race DROP+CREATE
                    conn.execute(f"CREATE OR REPLACE TABLE {tgt_q} AS SELECT * FROM final_df")
            finally:
                try:
                    conn.unregister("final_df")
                except Exception:
                    pass

        return {
            "status": "done",
            "source": spec.source,
            "target": spec.target,
            "rows": len(current),
            "cols": len(current.columns),
            "sink": dag.sink,
            "levels": dag.levels,
            "preview": sanitize_for_json(current.head(5).to_dict(orient="records")),
        }
    finally:
        conn.close()
