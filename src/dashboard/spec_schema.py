"""DashboardSpec (Plan 02/05)."""

from typing import Any, List, Optional

from pydantic import BaseModel


class ChartSpec(BaseModel):
    id: str
    type: str  # kpi|bar|hist|box|line|scatter|kpi
    title: str
    x: Optional[str] = None
    y: Optional[str] = None
    aggregation: Optional[str] = None
    metric: Optional[dict[str, Any]] = None  # for kpi: {"aggregation":"mean","column":"diem"}
    bins: Optional[int] = None  # for hist
    orientation: Optional[str] = None


class DashboardSpec(BaseModel):
    id: str
    title: str
    source: str
    charts: List[ChartSpec]
