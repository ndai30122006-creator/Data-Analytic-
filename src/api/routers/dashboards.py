"""Dashboards router — CRUD + per-chart real data + AI generate."""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.api.deps import _user_owns_table, check_rate_limit, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["dashboards"])


class DashboardCreateRequest(BaseModel):
    name: str
    spec: Dict[str, Any]


@router.post("/dashboards", dependencies=[Depends(check_rate_limit)])
async def create_dashboard(req: DashboardCreateRequest, username: str = Depends(get_current_user)):
    import json

    from src.core.database import Dashboard, SessionLocal

    try:
        with SessionLocal() as s:
            d = Dashboard(name=req.name, spec_json=json.dumps(req.spec, ensure_ascii=False), owner=username, version=1)
            s.add(d)
            s.commit()
            s.refresh(d)
            return {"dashboard_id": d.id, "name": d.name, "version": 1}
    except Exception as exc:
        logger.error("create_dashboard failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create dashboard")


@router.get("/dashboards", dependencies=[Depends(check_rate_limit)])
async def list_dashboards(username: str = Depends(get_current_user)):
    from src.core.database import Dashboard, SessionLocal

    with SessionLocal() as s:
        items = s.query(Dashboard).filter(Dashboard.owner == username).all()
        return {
            "dashboards": [
                {
                    "id": d.id,
                    "name": d.name,
                    "version": getattr(d, "version", 1) or 1,
                    "created_at": d.created_at.isoformat() if d.created_at else None,
                }
                for d in items
            ]
        }


@router.get("/dashboards/{dashboard_id}", dependencies=[Depends(check_rate_limit)])
async def get_dashboard(dashboard_id: int, username: str = Depends(get_current_user)):
    import json

    from src.core.database import Dashboard, SessionLocal

    with SessionLocal() as s:
        d = s.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
        if not d or d.owner != username:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        return {
            "id": d.id,
            "name": d.name,
            "version": getattr(d, "version", 1) or 1,
            "spec": json.loads(d.spec_json) if d.spec_json else {},
        }


@router.put("/dashboards/{dashboard_id}", dependencies=[Depends(check_rate_limit)])
async def update_dashboard(dashboard_id: int, req: DashboardCreateRequest, username: str = Depends(get_current_user)):
    import json

    from src.core.database import Dashboard, SessionLocal

    try:
        with SessionLocal() as s:
            d = s.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
            if not d or d.owner != username:
                raise HTTPException(status_code=404, detail="Dashboard not found")
            d.spec_json = json.dumps(req.spec, ensure_ascii=False)
            d.name = req.name
            d.version = (d.version or 1) + 1
            s.commit()
            return {"message": "Updated", "id": d.id, "version": d.version}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("update_dashboard failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update dashboard")


@router.post("/dashboards/{dashboard_id}/data", dependencies=[Depends(check_rate_limit)])
async def dashboard_data(dashboard_id: int, username: str = Depends(get_current_user)):
    import json

    from src.core.database import Dashboard, SessionLocal

    with SessionLocal() as s:
        d = s.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
        if not d or d.owner != username:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        spec = json.loads(d.spec_json) if d.spec_json else {}
        source = spec.get("source", "") if isinstance(spec, dict) else ""
        if source and not _user_owns_table(username, source):
            raise HTTPException(status_code=403, detail="Dashboard source does not belong to user")
        # Each chart 1 query -> ApexCharts-ready JSON (keeps spec for compat)
        try:
            from src.dashboard.renderer import fetch_data
            from src.dashboard.spec_schema import ChartSpec
        except Exception:
            return {"dashboard_id": d.id, "spec": spec, "data": "1 query per chart skeleton", "charts": []}
        charts_out: list = []
        for c in spec.get("charts", []) if isinstance(spec, dict) else []:
            try:
                cs = ChartSpec(**c)
                df = fetch_data(cs, source)
                t = cs.type.lower()
                if t == "kpi":
                    col = (cs.metric or {}).get("column") if cs.metric else None
                    agg = ((cs.metric or {}).get("aggregation", "mean") if cs.metric else "mean").lower()
                    val = float(len(df))
                    if col and col in df.columns:
                        try:
                            if agg == "count":
                                val = float(len(df))
                            elif agg in ("sum", "mean", "min", "max", "median"):
                                val = float(getattr(df[col].dropna(), agg)())
                            else:
                                val = float(df[col].dropna().mean())
                        except Exception:
                            val = float(len(df))
                    charts_out.append({"id": cs.id, "type": "kpi", "title": cs.title, "value": val})
                elif t == "bar" and cs.x and cs.x in df.columns:
                    vc = df[cs.x].astype(str).value_counts().head(20)
                    charts_out.append(
                        {
                            "id": cs.id,
                            "type": "bar",
                            "title": cs.title,
                            "categories": vc.index.tolist(),
                            "series": [{"name": "count", "data": [int(v) for v in vc.values]}],
                        }
                    )
                elif t == "hist" and cs.x and cs.x in df.columns:
                    s_num = df[cs.x].dropna()
                    try:
                        import pandas as pd

                        s_num = pd.to_numeric(s_num, errors="coerce").dropna()
                    except Exception:
                        pass
                    bins = cs.bins or 20
                    try:
                        cats, edges = __import__("numpy").histogram(s_num, bins=min(bins, 20))
                        labels = [f"{edges[i]:.1f}-{edges[i+1]:.1f}" for i in range(len(cats))]
                        charts_out.append(
                            {
                                "id": cs.id,
                                "type": "hist",
                                "title": cs.title,
                                "categories": labels,
                                "series": [{"name": "freq", "data": [int(v) for v in cats]}],
                            }
                        )
                    except Exception:
                        charts_out.append(
                            {"id": cs.id, "type": "hist", "title": cs.title, "categories": [], "series": []}
                        )
                elif t == "box" and cs.x and cs.y and cs.x in df.columns and cs.y in df.columns:
                    groups = []
                    try:
                        for name, g in df.groupby(cs.x)[cs.y]:
                            q = g.dropna().quantile([0, 0.25, 0.5, 0.75, 1.0]).tolist()
                            groups.append({"x": str(name), "y": [float(v) for v in q]})
                    except Exception:
                        groups = []
                    charts_out.append(
                        {"id": cs.id, "type": "box", "title": cs.title, "series": [{"type": "boxPlot", "data": groups}]}
                    )
                elif t in ("line", "scatter") and cs.x and cs.y and cs.x in df.columns and cs.y in df.columns:
                    sub = df[[cs.x, cs.y]].dropna().head(50)
                    if t == "line":
                        try:
                            sub = sub.sort_values(cs.x)
                        except Exception:
                            pass
                        charts_out.append(
                            {
                                "id": cs.id,
                                "type": t,
                                "title": cs.title,
                                "categories": sub[cs.x].astype(str).tolist(),
                                "series": [{"name": cs.y, "data": sub[cs.y].astype(float).tolist()}],
                            }
                        )
                    else:
                        pts = list(
                            zip(sub[cs.x].astype(float, errors="ignore").tolist(), sub[cs.y].astype(float).tolist())
                        )
                        charts_out.append(
                            {"id": cs.id, "type": t, "title": cs.title, "series": [{"name": "points", "data": pts}]}
                        )
                else:
                    charts_out.append(
                        {"id": c.get("id", ""), "type": c.get("type", ""), "title": c.get("title", ""), "series": []}
                    )
            except Exception:
                charts_out.append(
                    {"id": c.get("id", ""), "type": c.get("type", ""), "title": c.get("title", ""), "series": []}
                )
        return {"dashboard_id": d.id, "spec": spec, "charts": charts_out}


@router.post("/dashboards/generate", dependencies=[Depends(check_rate_limit)])
async def generate_dashboard(dataset_id: int, username: str = Depends(get_current_user)):
    import json

    from src.core.database import Dataset, SessionLocal

    with SessionLocal() as s:
        ds = s.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not ds or ds.username != username:
            raise HTTPException(status_code=404, detail="Dataset not found")
        profile = {}
        if ds.profile_json:
            try:
                profile = json.loads(ds.profile_json)
            except Exception:
                profile = {}
        from src.prompts.dashboard_author import fallback_spec

        source = ds.duckdb_table or f"mart.{ds.dataset_name}"
        spec = fallback_spec(profile, source)
        model_used = "rule-based"
        # AI (BYOK) neu user co key — chi gui profile + brief rong
        try:
            import logging as _logging
            import os as _os

            from src.core.database import get_api_key
            from src.prompts.dashboard_author import build_prompt

            _logger = _logging.getLogger(__name__)
            user_key = get_api_key(username)
            if user_key:
                provider = _os.environ.get("AI_PROVIDER", "openai")
                try:
                    # Structured output: charts validate bang ChartSpec schema
                    from src.core.llm_client import complete_model
                    from src.prompts.schemas import DashboardLLMBody

                    body, model = complete_model(
                        user_key, provider, build_prompt(profile, "", source), DashboardLLMBody
                    )
                    allowed = {"kpi", "bar", "hist", "box", "line", "scatter"}
                    # Business validation: type ho tro + column ton tai trong profile
                    prof_cols = set((profile.get("columns") or {}).keys()) if isinstance(profile, dict) else set()
                    valid = []
                    for cs in body.charts[:6]:
                        if cs.type.lower() not in allowed:
                            continue
                        cols_used = [c for c in [cs.x, cs.y, (cs.metric or {}).get("column")] if c]
                        if prof_cols and any(c not in prof_cols for c in cols_used):
                            continue
                        valid.append(cs.model_dump())
                    if len(valid) >= 2:
                        spec = {"id": body.id, "title": body.title, "source": source, "charts": valid}
                        model_used = f"{provider}:{model}"
                except Exception as exc:
                    _logger.warning("LLM dashboard failed (%s), fallback rule-based", type(exc).__name__)
        except Exception:
            pass
        return {"spec": spec, "model_used": model_used}
