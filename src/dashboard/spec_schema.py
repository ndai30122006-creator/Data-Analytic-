"""DashboardSpec (Plan 02/05)."""

from typing import Any, List, Optional

from pydantic import BaseModel


class ChartSpec(BaseModel):
    id: str
    type: str  # kpi|bar|hist|box|line|scatter
    title: str
    x: Optional[str] = None
    y: Optional[str] = None
    aggregation: Optional[str] = None


class DashboardSpec(BaseModel):
    id: str
    title: str
    source: str
    charts: List[ChartSpec]
