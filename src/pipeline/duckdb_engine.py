"""DuckDB SQL Engine (scalability) — chay DAG truc tiep tren views, khong roundtrip pandas.

Pipeline (engine="duckdb"):
    DuckDB table -> TEMP VIEW chuoi -> SQL moi step -> CREATE OR REPLACE TABLE

- Khong fetchdf() toan bo table (chi preview LIMIT 5 + COUNT).
- Moi op pandas co ban dich SQL; op khong dich duoc (derive/filter la) ->
  fallback hybrid: materialize step do qua pandas, tiep tuc SQL sau do.
- Tra ve `fallbacks: [step_id]` de UI biet step nao khong push-down duoc.
"""

import re
from typing import Dict, List

_STEP_VIEW = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,64}$")
_BLOCKED_SQL = re.compile(
    r"\b(drop|delete|insert|update|alter|create|attach|detach|copy|pragma|vacuum|checkpoint|install|load)\b",
    re.IGNORECASE,
)


def _guard_select_only(q: str, step_id: str) -> None:
    """Chan SQL nguy hiem tren duckdb engine (mirror sql_ops.py) — fail cung, khong fallback."""
    s = (q or "").strip()
    if ";" in s:
        raise ValueError(f"Step {step_id}: multiple statements khong duoc phep")
    if not re.match(r"^(select|with)\b", s, re.IGNORECASE):
        raise ValueError(f"Step {step_id}: chi SELECT/WITH duoc phep")
    if _BLOCKED_SQL.search(s):
        raise ValueError(f"Step {step_id}: DDL/DML bi cam")


class _FallbackToPandas(Exception):
    pass


def _qi(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _lit(v) -> str:
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def _cols(conn, view: str) -> List[str]:
    return [r[0] for r in conn.execute(f"SELECT * FROM {view} LIMIT 0").description]


def _sql_fill_missing(view: str, params: dict, cols: List[str]) -> str:
    col = params.get("column")
    method = str(params.get("method", "mean")).lower()
    value = params.get("value")
    if not col or col not in cols:
        # Mirror pandas impl: fill toan bo df khi thieu column
        exprs = ", ".join(f"COALESCE({_qi(c)}, {_lit(value if value is not None else 0)}) AS {_qi(c)}" for c in cols)
        return f"SELECT {exprs} FROM {view}"
    if method == "mean":
        fill = f"(SELECT AVG({_qi(col)}) FROM {view})"
    elif method == "median":
        fill = f"(SELECT QUANTILE_CONT({_qi(col)}, 0.5) FROM {view})"
    elif method == "mode":
        fill = f"(SELECT MODE({_qi(col)}) FROM {view})"
    else:
        fill = _lit(value if value is not None else 0)
    others = ", ".join(_qi(c) for c in cols if c != col)
    sel = f"COALESCE({_qi(col)}, {fill}) AS {_qi(col)}"
    return f"SELECT {sel}{(', ' + others) if others else ''} FROM {view}"


def _sql_drop_duplicates(view: str, params: dict, cols: List[str]) -> str:
    subset = params.get("subset")
    if not subset:
        return f"SELECT DISTINCT * FROM {view}"
    subs = [subset] if isinstance(subset, str) else list(subset)
    if not subs or any(s not in cols for s in subs):
        raise _FallbackToPandas(f"subset {subset} khong khop schema")
    part = ", ".join(_qi(s) for s in subs)
    return (
        f"SELECT * EXCLUDE rn FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY {part}) AS rn FROM {view}) "
        f"WHERE rn = 1"
    )


_DTYPE_MAP = {
    "float": "DOUBLE",
    "float64": "DOUBLE",
    "double": "DOUBLE",
    "int": "BIGINT",
    "int64": "BIGINT",
    "integer": "BIGINT",
    "str": "VARCHAR",
    "string": "VARCHAR",
    "object": "VARCHAR",
    "bool": "BOOLEAN",
    "boolean": "BOOLEAN",
    "datetime": "TIMESTAMP",
    "datetime64": "TIMESTAMP",
    "date": "DATE",
}


def _sql_type_cast(view: str, params: dict, cols: List[str]) -> str:
    col, dtype = params.get("column"), str(params.get("dtype", "")).lower()
    if not col or col not in cols:
        return f"SELECT * FROM {view}"
    sql_type = _DTYPE_MAP.get(dtype)
    if not sql_type:
        raise _FallbackToPandas(f"dtype {dtype!r} khong map duoc sang SQL")
    others = ", ".join(_qi(c) for c in cols if c != col)
    sel = f"CAST({_qi(col)} AS {sql_type}) AS {_qi(col)}"
    return f"SELECT {sel}{(', ' + others) if others else ''} FROM {view}"


def _sanitize_col(name: str) -> str:
    import re as _re

    n = _re.sub(r"[^a-zA-Z0-9_]", "_", name.strip().lower().replace(" ", "_"))
    return n or "col"


def _sql_standardize(view: str, params: dict, cols: List[str]) -> str:
    exprs = ", ".join(f"{_qi(c)} AS {_qi(_sanitize_col(c))}" for c in cols)
    return f"SELECT {exprs} FROM {view}"


def _sql_derive(view: str, params: dict, cols: List[str]) -> str:
    name = params.get("name") or params.get("new_column")
    expr = params.get("expr") or params.get("formula")
    if not name or not expr:
        raise _FallbackToPandas("derive_column can name/expr")
    if not _STEP_VIEW.match(str(name)):
        raise _FallbackToPandas(f"ten cot {name!r} khong hop le")
    if ";" in expr or _BLOCKED_SQL.search(expr):
        raise ValueError(f"derive expr chua lenh bi cam")
    return f"SELECT *, ({expr}) AS {_qi(name)} FROM {view}"


def _sql_filter(view: str, params: dict, cols: List[str]) -> str:
    query = params.get("query")
    if not query:
        return f"SELECT * FROM {view}"
    if ";" in query or _BLOCKED_SQL.search(query):
        raise ValueError("filter query chua lenh bi cam")
    return f"SELECT * FROM {view} WHERE {query}"


def _sql_aggregate(view: str, params: dict, cols: List[str]) -> str:
    by = params.get("by") or params.get("group_by")
    agg = str(params.get("agg", "mean")).upper()
    if agg not in ("MEAN", "AVG", "SUM", "MIN", "MAX", "COUNT", "MEDIAN"):
        raise _FallbackToPandas(f"agg {agg!r} khong push-down duoc")
    if agg == "MEAN":
        agg = "AVG"
    if not by or by not in cols:
        raise _FallbackToPandas("aggregate can 'by' ton tai trong schema")
    targets = [c for c in cols if c != by]
    if not targets:
        raise _FallbackToPandas("aggregate khong co cot nao de agg")
    # Mirror pandas groupby(by).agg(): giu nguyen ten cot
    exprs = ", ".join(f"{agg}({_qi(c)}) AS {_qi(c)}" for c in targets)
    return f"SELECT {_qi(by)}, {exprs} FROM {view} GROUP BY {_qi(by)}"


def _build_step_sql(op: str, view: str, params: dict, cols: List[str]) -> str:
    builders = {
        "fill_missing": _sql_fill_missing,
        "drop_duplicates": _sql_drop_duplicates,
        "type_cast": _sql_type_cast,
        "standardize_columns": _sql_standardize,
        "derive_column": _sql_derive,
        "filter": _sql_filter,
        "aggregate": _sql_aggregate,
    }
    if op not in builders:
        raise _FallbackToPandas(f"op {op!r} chua co ban dich SQL")
    return builders[op](view, params, cols)


def execute_duckdb(spec, dag, src_q: str, tgt_q: str, conn, sample: bool = False) -> Dict:
    """Chay DAG hoan toan tren DuckDB views. Tra dict giong executor.execute + engine_used/fallbacks."""
    from src.pipeline.executor import sanitize_for_json
    from src.pipeline.ops.pandas_ops import OPS as PANDAS_OPS

    views: List[str] = []
    regs: List[str] = []  # registered df views — chi unregister CUOI cung (view SQL phu thuoc chung)

    def _track(v: str) -> str:
        views.append(v)
        return v

    try:
        base_sql = f"SELECT * FROM {src_q}"
        if sample:
            base_sql += " LIMIT 100"
        conn.execute(f"CREATE OR REPLACE TEMP VIEW wb_src AS {base_sql}")
        _track("wb_src")
        # Plan 1: Quality Gate tren bounded sample (khong fetch full table)
        from src.pipeline.contract import check_contract

        gate_df = conn.execute("SELECT * FROM wb_src LIMIT 10000").fetchdf()
        gate = check_contract(gate_df, getattr(spec, "contract", None))
        if not gate["passed"]:
            from src.pipeline.planner import spec_hash as _sh

            return {
                "status": "failed",
                "error": f"Quality gate blocked: {'; '.join(gate['violations'][:5])}",
                "gate": gate,
                "spec_hash": _sh(spec),
            }
        views_map: Dict[str, str] = {"source": "wb_src"}
        fallbacks: List[str] = []
        import time as _time

        step_timings: Dict[str, float] = {}

        for plan_step in dag.steps:
            step = plan_step.step
            op, params = step.op, step.params or {}
            _t0 = _time.perf_counter()
            deps = list(step.depends_on or [])
            if not all(_STEP_VIEW.match(d) for d in deps):
                return {"status": "failed", "error": f"Step {step.id} depends_on id khong hop le"}
            in_views = [views_map["source"]] if not deps else [views_map[d] for d in deps]
            out_view = f"wb_{step.id}"
            if not _STEP_VIEW.match(f"wb_{step.id}") or len(out_view) > 64:
                return {"status": "failed", "error": f"Step id {step.id!r} khong dung lam view name"}
            single = in_views[0] if len(in_views) == 1 else None

            try:
                if op == "sql":
                    q = params.get("query", f"SELECT * FROM {single or 'wb_src'}")
                    q = q.replace("{{prev}}", in_views[-1])
                    try:
                        _guard_select_only(q, step.id)
                    except ValueError as ve:
                        return {"status": "failed", "error": str(ve)}
                    conn.execute(f"CREATE OR REPLACE TEMP VIEW {out_view} AS {q}")
                elif op == "merge":
                    how = str(params.get("how", "concat")).lower()
                    if how == "merge":
                        on = params.get("on")
                        on_list = [on] if isinstance(on, str) else list(on or [])
                        if not on_list:
                            raise _FallbackToPandas("merge how='merge' can 'on'")
                        using = ", ".join(_qi(c) for c in on_list)
                        sql = f"SELECT * FROM {in_views[0]}"
                        for v in in_views[1:]:
                            sql += f" JOIN {v} USING ({using})"
                    else:
                        sql = " UNION ALL BY NAME ".join(f"SELECT * FROM {v}" for v in in_views)
                    conn.execute(f"CREATE OR REPLACE TEMP VIEW {out_view} AS {sql}")
                elif op in PANDAS_OPS:
                    cols = _cols(conn, single or "wb_src")
                    sql = _build_step_sql(op, single or "wb_src", params, cols)
                    try:
                        conn.execute(f"EXPLAIN {sql}")
                    except Exception as exc:
                        raise _FallbackToPandas(f"SQL khong hop le ({exc}), fallback pandas")
                    conn.execute(f"CREATE OR REPLACE TEMP VIEW {out_view} AS {sql}")
                else:
                    return {"status": "failed", "error": f"Unknown op {op}"}
            except _FallbackToPandas as fb:
                # Hybrid: materialize input ve pandas, chay op, dua lai len view
                fallbacks.append(step.id)
                if op not in PANDAS_OPS:
                    return {"status": "failed", "error": f"Step {step.id} ({op}) failed: {fb}"}
                func = PANDAS_OPS[op]
                if single is not None:
                    df = conn.execute(f"SELECT * FROM {single}").fetchdf()
                    res_df = func(df, **params)
                else:
                    frames = {d: conn.execute(f"SELECT * FROM {views_map[d]}").fetchdf() for d in deps}
                    if op != "merge":
                        return {
                            "status": "failed",
                            "error": f"Step {step.id} ({op}) has multiple inputs; use op 'merge'",
                        }
                    res_df = func(frames, **params)
                reg_name = f"wb_reg_{step.id}"
                conn.register(reg_name, res_df)
                regs.append(reg_name)
                conn.execute(f"CREATE OR REPLACE TEMP VIEW {out_view} AS SELECT * FROM {reg_name}")
            except Exception as e:
                return {"status": "failed", "error": f"Step {step.id} ({op}) failed: {e}"}

            _track(out_view)
            views_map[step.id] = out_view
            step_timings[step.id] = round((_time.perf_counter() - _t0) * 1000, 1)

        last_view = views_map[dag.sink] if dag.sink else "wb_src"
        if not sample:
            from src.warehouse.connection import warehouse_write_lock

            with warehouse_write_lock(timeout=30.0):
                conn.execute(f"CREATE OR REPLACE TABLE {tgt_q} AS SELECT * FROM {last_view}")
        cols = _cols(conn, last_view)
        total = conn.execute(f"SELECT COUNT(*) FROM {last_view}").fetchone()[0]
        preview = conn.execute(f"SELECT * FROM {last_view} LIMIT 5").fetchdf().to_dict(orient="records")
        from src.pipeline.planner import spec_hash as _sh2

        return {
            "status": "done",
            "source": spec.source,
            "target": spec.target,
            "rows": int(total),
            "cols": len(cols),
            "sink": dag.sink,
            "levels": dag.levels,
            "engine_used": "duckdb",
            "fallbacks": fallbacks,
            "spec_hash": _sh2(spec),
            "gate": gate,
            "step_timings": step_timings,
            "preview": sanitize_for_json(preview),
        }
    finally:
        for v in views:
            try:
                conn.execute(f"DROP VIEW IF EXISTS {v}")
            except Exception:
                pass
        for r in regs:
            try:
                conn.unregister(r)
            except Exception:
                pass
