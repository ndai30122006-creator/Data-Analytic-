"""PipelineSpec DSL (Plan 02/04)."""

from typing import Any, List, Optional

from pydantic import BaseModel, Field


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

    def validate_dag(self) -> None:
        """Validate DAG: no cycle, depends_on exists, op in catalog."""
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
        indeg = {s.id: len(s.depends_on) for s in self.steps}
        adj = {s.id: [] for s in self.steps}
        for s in self.steps:
            for dep in s.depends_on:
                adj[dep].append(s.id)
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
        indeg = {s.id: len(s.depends_on) for s in self.steps}
        adj = {s.id: [] for s in self.steps}
        for s in self.steps:
            for dep in s.depends_on:
                adj[dep].append(s.id)
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
