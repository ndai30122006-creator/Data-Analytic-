"""PipelineSpec DSL (Plan 02/04)."""

import re
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

_STEP_ID = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,64}$")


def _build_graph(steps: List["PipelineStep"]) -> Tuple[Dict[str, int], Dict[str, List[str]]]:
    """Dung chung cho validate_dag + topo_order (Kahn)."""
    indeg = {s.id: len(s.depends_on) for s in steps}
    adj: Dict[str, List[str]] = {s.id: [] for s in steps}
    for s in steps:
        for dep in s.depends_on:
            adj[dep].append(s.id)
    return indeg, adj


class PipelineStep(BaseModel):
    id: str
    op: str
    params: dict[str, Any] = Field(default_factory=dict)
    depends_on: List[str] = Field(default_factory=list)


class PipelineSpec(BaseModel):
    name: str
    source: str  # raw.<dataset>
    target: str  # mart.<dataset>
    steps: List[PipelineStep]
    engine: str = "pandas"  # pandas (small data) | duckdb (large data, SQL push-down)
    contract: Optional[dict] = None  # plan 1: DataContract gate truoc execute

    def validate_dag(self) -> None:
        """Validate DAG: engine, step ids, no cycle, depends_on exists, op in catalog."""
        if self.engine not in ("pandas", "duckdb"):
            raise ValueError(f"Unknown engine {self.engine!r} (allowed: pandas, duckdb)")
        seen: set = set()
        for s in self.steps:
            if not s.id or not _STEP_ID.match(s.id):
                raise ValueError(f"Invalid step id {s.id!r} (phai [A-Za-z_][A-Za-z0-9_]{{0,64}})")
            if s.id in seen:
                raise ValueError(f"Duplicate step id {s.id!r}")
            seen.add(s.id)
        ids = {s.id for s in self.steps}
        # Check depends_on exists
        for s in self.steps:
            for dep in s.depends_on:
                if dep not in ids:
                    raise ValueError(f"Step {s.id} depends_on unknown {dep}")
        # Check op in catalog
        try:
            from src.pipeline.ops.pandas_ops import OPS as PANDAS_OPS
            from src.pipeline.ops.sql_ops import OPS_SQL  # type: ignore

            catalog = set(PANDAS_OPS.keys()) | set(OPS_SQL.keys()) if "OPS_SQL" in locals() else set(PANDAS_OPS.keys())
        except Exception:
            catalog = set()
        # Allow any op if catalog empty (skeleton), else validate
        if catalog:
            for s in self.steps:
                if s.op not in catalog and s.op != "sql":
                    raise ValueError(f"Unknown op {s.op} (allowed: {catalog})")
        # Cycle detection via Kahn
        indeg, adj = _build_graph(self.steps)
        q = [k for k, v in indeg.items() if v == 0]
        visited = 0
        while q:
            n = q.pop()
            visited += 1
            for nb in adj[n]:
                indeg[nb] -= 1
                if indeg[nb] == 0:
                    q.append(nb)
        if visited != len(self.steps):
            raise ValueError("Cycle detected in DAG")

    def topo_order(self) -> List[PipelineStep]:
        self.validate_dag()
        # Kahn order
        ids = {s.id: s for s in self.steps}
        indeg, adj = _build_graph(self.steps)
        q = [k for k, v in indeg.items() if v == 0]
        order = []
        while q:
            n = q.pop(0)
            order.append(ids[n])
            for nb in adj[n]:
                indeg[nb] -= 1
                if indeg[nb] == 0:
                    q.append(nb)
        return order
