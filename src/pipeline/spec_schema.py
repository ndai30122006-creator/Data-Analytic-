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
