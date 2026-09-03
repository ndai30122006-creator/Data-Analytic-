"""Executor — topological DAG run (Plan 02). Skeleton."""

from typing import Dict

from src.pipeline.spec_schema import PipelineSpec


def execute(spec: PipelineSpec, sample: bool = False) -> Dict:
    """Skeleton executor — validates DAG, returns preview."""
    # TODO: topo sort, checkpoint, DuckDB, history (P3)
    return {"spec": spec.model_dump(), "sample": sample, "status": "skeleton"}
