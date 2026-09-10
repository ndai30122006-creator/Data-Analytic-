"""DAG Planner (P0/P1) — PipelineSpec -> executable Plan.

Plan = topo order + execution levels (steps cung level khong phu thuoc nhau,
co the chay song song trong tuong lai). Hien executor van chay tuan tu theo
topo order de giu deterministic.
"""

from dataclasses import dataclass, field
from typing import List

from src.pipeline.spec_schema import PipelineSpec, PipelineStep


@dataclass
class PlanStep:
    """1 step kem level thuc thi (longest-path tu source)."""

    step: PipelineStep
    level: int = 0


@dataclass
class Plan:
    """Ke hoach thuc thi: topo order + levels + sink."""

    steps: List[PlanStep] = field(default_factory=list)
    levels: List[List[str]] = field(default_factory=list)
    sink: str = ""  # id step cuoi (output ghi ra target)

    @property
    def order(self) -> List[PipelineStep]:
        return [p.step for p in self.steps]


def plan(spec: PipelineSpec) -> Plan:
    """Validate DAG + tra Plan (raise ValueError neu DAG sai)."""
    spec.validate_dag()
    order = spec.topo_order()
    # Level = 1 + max(level of deps), source-level 0
    level_of: dict[str, int] = {}
    for s in order:
        deps = s.depends_on or []
        level_of[s.id] = (max((level_of[d] for d in deps), default=-1) + 1) if deps else 0
    max_level = max(level_of.values(), default=0)
    levels: List[List[str]] = [[] for _ in range(max_level + 1)]
    for s in order:
        levels[level_of[s.id]].append(s.id)
    return Plan(
        steps=[PlanStep(step=s, level=level_of[s.id]) for s in order],
        levels=levels,
        sink=order[-1].id if order else "",
    )
