"""Lineage — dataset -> pipelines -> dashboards (Plan P5)."""

from src.core.database import Brief, Dataset, SessionLocal

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
        pipelines_count = 0
        if Dashboard:
            dashboards = s.query(Dashboard).count()
        try:
            from src.core.database import Pipeline

            # Count pipelines whose source matches dataset's duckdb_table or name
            if ds.duckdb_table:
                pipelines_count = s.query(Pipeline).filter(Pipeline.source == ds.duckdb_table).count()
                if pipelines_count == 0 and ds.dataset_name:
                    pipelines_count = s.query(Pipeline).filter(Pipeline.source.contains(ds.dataset_name)).count()
            elif ds.dataset_name:
                pipelines_count = s.query(Pipeline).filter(Pipeline.source.contains(ds.dataset_name)).count()
        except Exception:
            pipelines_count = 0
        return {
            "dataset": ds.dataset_name,
            "table": ds.duckdb_table,
            "briefs": briefs,
            "dashboards": dashboards,
            "pipelines_count": pipelines_count,
            "pipelines": pipelines_count,
        }
