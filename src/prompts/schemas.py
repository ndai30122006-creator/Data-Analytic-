"""Structured LLM outputs (Pydantic) — LLM -> schema -> validation -> business validation."""

from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from src.dashboard.spec_schema import ChartSpec


class BriefDoc(BaseModel):
    """Brief narrative tieng Viet do LLM sinh."""

    brief: str = Field(min_length=20, max_length=12000)


class DashboardLLMBody(BaseModel):
    """Phan LLM duoc phep sinh cho dashboard (source do engine dien)."""

    id: str = "dash_ai"
    title: str = "Dashboard AI"
    charts: List[ChartSpec] = Field(min_length=2, max_length=6)


class PipelineLLMStep(BaseModel):
    id: str
    op: str
    params: dict[str, Any] = Field(default_factory=dict)
    depends_on: List[str] = Field(default_factory=list)


class PipelineLLMBody(BaseModel):
    """Phan LLM duoc phep sinh cho pipeline (source/target do engine dien)."""

    name: str = "ai-pipeline"
    steps: List[PipelineLLMStep] = Field(min_length=1, max_length=20)

    @field_validator("steps")
    @classmethod
    def unique_ids(cls, steps):
        ids = [s.id for s in steps]
        if len(ids) != len(set(ids)):
            raise ValueError("trung step id")
        return steps


class ProposalValidations(BaseModel):
    """Ket qua 4 lop validation cho AI proposal."""

    schema_ok: bool = True
    schema_errors: List[str] = Field(default_factory=list)
    semantic_ok: bool = True
    semantic_errors: List[str] = Field(default_factory=list)
    safety_ok: bool = True
    safety_errors: List[str] = Field(default_factory=list)
    dry_run_ok: bool = False
    dry_run_error: Optional[str] = None

    @property
    def all_ok(self) -> bool:
        return self.schema_ok and self.semantic_ok and self.safety_ok and self.dry_run_ok


class ProposalCost(BaseModel):
    """Cost estimation truoc execute."""

    source_rows: Optional[int] = None
    steps: int = 0
    recommended_engine: Literal["pandas", "duckdb"] = "pandas"
    reason: str = ""
