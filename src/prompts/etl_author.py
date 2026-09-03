"""ETL author — NL -> PipelineSpec (Plan 04)."""

from src.pipeline.ops.pandas_ops import OPS as PANDAS_OPS
from src.pipeline.ops.sql_ops import OPS as SQL_OPS

CATALOG = list(PANDAS_OPS.keys()) + list(SQL_OPS.keys())

SYSTEM = (
    "Bạn là trợ lý ETL. Dựa vào yêu cầu tiếng Việt và schema cột, "
    f"sinh PipelineSpec YAML/JSON chỉ dùng ops: {CATALOG}. "
    "Trả về JSON với name, source, target, steps (id, op, params, depends_on). "
    "Không dùng op ngoài catalog, params phải có column tồn tại."
)


def build_prompt(nl: str, columns: list, source: str = "raw.dataset", target: str = "mart.dataset") -> list[dict]:
    cols = ", ".join(columns[:20])
    return [
        {"role": "system", "content": SYSTEM},
        {
            "role": "user",
            "content": f"columns: {cols}\nsource: {source}\ntarget: {target}\nyêu cầu: {nl}\n→ spec JSON:",
        },
    ]


def validate_spec(spec: dict, columns: list) -> list[str]:
    """Validate spec params, return list errors."""
    errs = []
    for step in spec.get("steps", []):
        op = step.get("op")
        if op not in CATALOG:
            errs.append(f"Unknown op {op}")
        # Check column exists if params has column
        col = step.get("params", {}).get("column")
        if col and col not in columns:
            errs.append(f"Step {step.get('id')} column {col} not in schema")
    return errs
