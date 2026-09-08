"""Lineage — dataset -> pipelines -> dashboards (Plan P5 + muc 13: graph nodes/edges)."""

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
        table = ds.duckdb_table or ""
        # Brief versions
        brief_rows = []
        if Brief:
            brief_rows = [
                {"version": b.version, "model": b.model_used}
                for b in s.query(Brief).filter(Brief.dataset_id == dataset_id).order_by(Brief.version.asc()).all()
            ]
        # Pipelines whose source matches this dataset
        pipe_rows = []
        try:
            from src.core.database import Pipeline

            q = s.query(Pipeline).filter(Pipeline.owner == ds.username)
            if table:
                pipe_rows = q.filter(Pipeline.source == table).all()
                if not pipe_rows and ds.dataset_name:
                    pipe_rows = q.filter(Pipeline.source.contains(ds.dataset_name)).all()
            elif ds.dataset_name:
                pipe_rows = q.filter(Pipeline.source.contains(ds.dataset_name)).all()
        except Exception:
            pipe_rows = []
        targets = {p.target for p in pipe_rows if getattr(p, "target", None)}
        # Dashboards whose spec.source matches dataset table HOAC pipeline target
        dash_rows = []
        if Dashboard:
            import json as _json

            for d in s.query(Dashboard).filter(Dashboard.owner == ds.username).all():
                try:
                    src = (_json.loads(d.spec_json) if d.spec_json else {}).get("source", "")
                except Exception:
                    src = ""
                if src == table or src in targets:
                    dash_rows.append(d)
        # Graph truc quan cho UI (nodes/edges) — giu cac key cu de tuong thich
        nodes = [{"id": f"dataset:{dataset_id}", "kind": "dataset", "label": ds.dataset_name, "meta": table}]
        edges = []
        for b in brief_rows:
            nid = f"brief:v{b['version']}"
            nodes.append({"id": nid, "kind": "brief", "label": f"Brief v{b['version']}", "meta": b["model"]})
            edges.append({"from": f"dataset:{dataset_id}", "to": nid, "label": "generates"})
        for p in pipe_rows:
            nid = f"pipeline:{p.id}"
            nodes.append({"id": nid, "kind": "pipeline", "label": p.name, "meta": f"{p.source} → {p.target}"})
            edges.append({"from": f"dataset:{dataset_id}", "to": nid, "label": "feeds"})
            if p.target:
                tid = f"table:{p.target}"
                if not any(n["id"] == tid for n in nodes):
                    nodes.append({"id": tid, "kind": "mart", "label": p.target, "meta": "mart table"})
                edges.append({"from": nid, "to": tid, "label": "writes"})
        for d in dash_rows:
            nid = f"dashboard:{d.id}"
            nodes.append({"id": nid, "kind": "dashboard", "label": d.name, "meta": ""})
            # Noi dashboard ve table nguon cua no (dataset hoac mart target)
            try:
                import json as _json

                src = (_json.loads(d.spec_json) if d.spec_json else {}).get("source", "")
            except Exception:
                src = ""
            parent = f"table:{src}" if src in targets else f"dataset:{dataset_id}"
            edges.append({"from": parent, "to": nid, "label": "visualizes"})
        return {
            "dataset": ds.dataset_name,
            "table": table,
            "briefs": len(brief_rows),
            "brief_versions": brief_rows,
            "dashboards": len(dash_rows),
            "dashboard_list": [{"id": d.id, "name": d.name} for d in dash_rows],
            "pipelines_count": len(pipe_rows),
            "pipelines": len(pipe_rows),
            "pipeline_list": [{"id": p.id, "name": p.name, "source": p.source, "target": p.target} for p in pipe_rows],
            "nodes": nodes,
            "edges": edges,
        }
