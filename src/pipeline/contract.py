"""Data Contract + Quality Gate (plan 1).

Contract khai bao ky vong ve source truoc khi chay:
    contract:
      min_rows: 1
      max_missing_pct: 20
      max_dup_pct: 5
      columns:
        diem: {dtype: float, nullable: false, min: 0, max: 10}
        lop:  {dtype: str, nullable: true}

Gate chay truoc moi execute (ke ca dry-run): dat -> chay, rot -> failed
kem gate report chi tiet tung rule.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ColumnRule(BaseModel):
    dtype: Optional[str] = None  # float|int|str|bool (+ bien the pandas)
    nullable: bool = True
    min: Optional[float] = None
    max: Optional[float] = None
    allowed: Optional[List[Any]] = None


class DataContract(BaseModel):
    min_rows: int = 1
    max_missing_pct: float = 100.0
    max_dup_pct: float = 100.0
    columns: Dict[str, ColumnRule] = Field(default_factory=dict)


_DTYPE_FAMILIES = {
    "float": {"float64", "float32", "float", "double"},
    "int": {"int64", "int32", "int", "bigint"},
    "str": {"object", "string", "str", "varchar"},
    "bool": {"bool", "boolean"},
}


def _dtype_match(actual: str, expected: str) -> bool:
    actual, expected = actual.lower(), expected.lower()
    if actual == expected:
        return True
    return actual in _DTYPE_FAMILIES.get(expected, set())


def check_contract(df, contract: Optional[dict]) -> Dict[str, Any]:
    """Kiem tra df theo contract. Tra ve {passed, violations[], checked}."""
    violations: List[str] = []
    if not contract:
        return {"passed": True, "violations": [], "checked": False}
    try:
        rule = DataContract(**contract)
    except Exception as e:
        return {"passed": False, "violations": [f"contract sai schema: {e}"], "checked": True}

    n = len(df)
    if n < rule.min_rows:
        violations.append(f"rows {n} < min_rows {rule.min_rows}")
    if n > 0:
        miss_pct = float(df.isnull().sum().sum() / (n * len(df.columns)) * 100) if len(df.columns) else 0.0
        if miss_pct > rule.max_missing_pct:
            violations.append(f"missing {miss_pct:.1f}% > max {rule.max_missing_pct}%")
        dup_pct = float(df.duplicated().sum() / n * 100)
        if dup_pct > rule.max_dup_pct:
            violations.append(f"duplicate {dup_pct:.1f}% > max {rule.max_dup_pct}%")
    for col, cr in rule.columns.items():
        if col not in df.columns:
            violations.append(f"thieu cot '{col}'")
            continue
        s = df[col]
        if not cr.nullable and s.isnull().any():
            violations.append(f"cot '{col}' co null nhung nullable=false")
        if cr.dtype and not _dtype_match(str(s.dtype), cr.dtype):
            violations.append(f"cot '{col}' dtype {s.dtype} khac {cr.dtype}")
        num = None
        try:
            import pandas as pd

            num = pd.to_numeric(s, errors="coerce").dropna()
        except Exception:
            num = None
        if num is not None and len(num):
            if cr.min is not None and float(num.min()) < cr.min:
                violations.append(f"cot '{col}' min {float(num.min())} < {cr.min}")
            if cr.max is not None and float(num.max()) > cr.max:
                violations.append(f"cot '{col}' max {float(num.max())} > {cr.max}")
        if cr.allowed is not None:
            bad = set(s.dropna().unique().tolist()) - set(cr.allowed)
            if bad:
                violations.append(f"cot '{col}' gia tri la {sorted(bad)[:5]}")
    return {"passed": not violations, "violations": violations, "checked": True}
