"""Executor — topological DAG run with checkpoint (Plan 04)."""

from typing import Dict

import pandas as pd

import re

from src.pipeline.spec_schema import PipelineSpec
from src.warehouse.connection import get_conn

_VALID_ID = re.compile(r"^(raw|mart)\.[a-zA-Z_][a-zA-Z0-9_]{0,63}$")


def _validate_identifier(name: str) -> str:
    if not _VALID_ID.match(name):
        raise ValueError(f"Invalid identifier {name!r} (must be raw/mart + alphanum/_)")
    # Quote safely
    schema, table = name.split(".", 1)
    return f'"{schema}"."{table}"'


def execute(spec: PipelineSpec, sample: bool = False) -> Dict:
    """Execute spec DAG; sample=True limits 100 rows, no overwrite mart."""
    spec.validate_dag()
    order = spec.topo_order()

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

        # Track intermediate results per step id
        results = {"source": df}
        current = df

        # Import ops
        from src.pipeline.ops.pandas_ops import OPS as PANDAS_OPS
        from src.pipeline.ops.sql_ops import run_sql

        for step in order:
            op = step.op
            params = step.params or {}
            # Resolve prev: if depends_on, use last dependency's result, else current
            if step.depends_on:
                # For simplicity, use most recent dependency's df
                prev_id = step.depends_on[-1]
                prev_df = results.get(prev_id, current)
            else:
                prev_df = current

            try:
                if op in PANDAS_OPS:
                    # Call pandas op
                    # Pass df as first arg
                    func = PANDAS_OPS[op]
                    # Handle special case where op expects column param
                    res_df = func(prev_df.copy(), **params)
                    if isinstance(res_df, pd.DataFrame):
                        current = res_df
                    else:
                        current = prev_df
                elif op == "sql":
                    # ELT mode: run SQL on DuckDB view of prev_df
                    conn.register("prev_view", prev_df)
                    q = params.get("query", f"SELECT * FROM prev_view")
                    # Replace {{prev}} with prev_view
                    res_df = run_sql(conn, q, "prev_view")
                    conn.unregister("prev_view")
                    current = res_df
                else:
                    return {"status": "failed", "error": f"Unknown op {op}"}
                results[step.id] = current.copy()
            except Exception as e:
                return {"status": "failed", "error": f"Step {step.id} ({op}) failed: {e}"}

        # Write to target if not sample
        if not sample:
            conn.register("final_df", current)
            conn.execute(f"DROP TABLE IF EXISTS {tgt_q}")
            conn.execute(f"CREATE TABLE {tgt_q} AS SELECT * FROM final_df")
            conn.unregister("final_df")

        return {
            "status": "done",
            "source": spec.source,
            "target": spec.target,
            "rows": len(current),
            "cols": len(current.columns),
            "preview": current.head(5).to_dict(orient="records"),
        }
    finally:
        conn.close()
