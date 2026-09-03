"""Lineage — dataset -> pipelines -> dashboards (Plan P5)."""

from src.core.database import SessionLocal, Dataset, Brief

try:
    from src.core.database import Dashboard
except Exception:
    Dashboard = None


def get_lineage(dataset_id: int) -> dict:
    with SessionLocal() as s:
        ds = s.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not ds:
            return {}
        briefs = s.query(Brief).filter(Brief.dataset_id == dataset_id).count() if Brief else 0
        dashboards = 0
        if Dashboard:
            dashboards = s.query(Dashboard).count()
        return {
            "dataset": ds.dataset_name,
            "table": ds.duckdb_table,
            "briefs": briefs,
            "dashboards": dashboards,
        }
