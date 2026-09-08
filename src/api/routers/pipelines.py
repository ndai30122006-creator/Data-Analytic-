"""Pipelines router — CRUD + preview/run/runs (persisted via DB).

Mục 10: khóa theo từng pipeline (chạy đồng thời cùng pipeline → 409),
ghi warehouse vẫn tuần tự qua warehouse_write_lock.
Mục 12: log từng run vào pipeline_steps + trả steps trong GET /runs/{id}.
Mục 8: mọi write DB bọc try/except + rollback.
"""

import logging
import threading
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel

from src.api.deps import _user_owns_table, check_rate_limit, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["pipelines"])

# Keep in-memory mirrors for backward compat (primary source = DB)
_pipelines: Dict[str, Dict[str, Any]] = {}
_runs: Dict[str, Dict[str, Any]] = {}

# Mục 10: 1 lock / pipeline_id — 2 run cùng pipeline không ghi mart đè nhau
_pipeline_locks: Dict[str, threading.Lock] = {}
_pipeline_locks_guard = threading.Lock()


def _lock_for(pipeline_id: str) -> threading.Lock:
    with _pipeline_locks_guard:
        lock = _pipeline_locks.get(pipeline_id)
        if lock is None:
            lock = threading.Lock()
            _pipeline_locks[pipeline_id] = lock
        return lock


def _write_step_logs(run_id: str, steps: list, status_map: Dict[str, str], log_text: str = "") -> None:
    """Persist per-step logs (mục 12). Best-effort, không fail run."""
    try:
        from src.core.database import PipelineStep, SessionLocal

        with SessionLocal() as s:
            for st in steps:
                sid = st.get("id") if isinstance(st, dict) else getattr(st, "id", "?")
                s.add(
                    PipelineStep(
                        run_id=run_id,
                        step_id=str(sid),
                        status=status_map.get(str(sid), "done"),
                        log=log_text[:2000] if log_text else None,
                    )
                )
            s.commit()
    except Exception as exc:
        logger.warning("Failed to write step logs for run %s: %s", run_id, exc)


class PipelineCreateRequest(BaseModel):
    name: str
    source: str
    target: str
    steps: list = []


@router.post("/pipelines", dependencies=[Depends(check_rate_limit)])
async def create_pipeline(req: PipelineCreateRequest, username: str = Depends(get_current_user)):
    import json
    import uuid

    from src.core.database import Pipeline, SessionLocal

    # Validate PipelineSpec (schema + DAG + identifiers) before persisting
    try:
        from src.pipeline.executor import _validate_identifier
        from src.pipeline.spec_schema import PipelineSpec

        spec = PipelineSpec(**req.model_dump())
        spec.validate_dag()
        _validate_identifier(spec.source)
        _validate_identifier(spec.target)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid PipelineSpec: {e}")
    if not _user_owns_table(username, req.source):
        raise HTTPException(status_code=403, detail="Source table does not belong to user")
    pid = str(uuid.uuid4())[:8]
    spec_json = json.dumps(req.model_dump(), ensure_ascii=False)
    try:
        with SessionLocal() as s:
            p = Pipeline(
                id=pid,
                owner=username,
                name=req.name,
                source=req.source,
                target=req.target,
                spec_json=spec_json,
                version=1,
            )
            s.add(p)
            s.commit()
    except Exception as exc:
        logger.error("create_pipeline DB failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create pipeline")
    # Keep in-memory for preview/run backward compat
    _pipelines[pid] = {
        "id": pid,
        "owner": username,
        **req.model_dump(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return {"pipeline_id": pid, "spec": _pipelines[pid]}


@router.get("/pipelines", dependencies=[Depends(check_rate_limit)])
async def list_pipelines(username: str = Depends(get_current_user)):
    from src.core.database import Pipeline, SessionLocal

    with SessionLocal() as s:
        rows = s.query(Pipeline).filter(Pipeline.owner == username).all()
        items = [
            {
                "id": r.id,
                "owner": r.owner,
                "name": r.name,
                "source": r.source,
                "target": r.target,
                "version": getattr(r, "version", 1) or 1,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]
        # Fallback in-memory if DB empty (for tests without DB)
        if not items:
            items = [v for v in _pipelines.values() if v["owner"] == username]
        return {"pipelines": items, "count": len(items)}


@router.get("/pipelines/{pipeline_id}", dependencies=[Depends(check_rate_limit)])
async def get_pipeline(pipeline_id: str, username: str = Depends(get_current_user)):
    import json

    from src.core.database import Pipeline, SessionLocal

    with SessionLocal() as s:
        p = s.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
        if p and p.owner == username:
            spec = json.loads(p.spec_json) if p.spec_json else {}
            return {
                "id": p.id,
                "owner": p.owner,
                **spec,
                "version": getattr(p, "version", 1) or 1,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
    # Fallback in-memory
    p = _pipelines.get(pipeline_id)
    if not p or p["owner"] != username:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return p


@router.put("/pipelines/{pipeline_id}", dependencies=[Depends(check_rate_limit)])
async def update_pipeline(pipeline_id: str, req: PipelineCreateRequest, username: str = Depends(get_current_user)):
    """Cap nhat spec pipeline — validate DAG + ownership, tang version (muc 15)."""
    import json

    from src.core.database import Pipeline, SessionLocal

    try:
        from src.pipeline.executor import _validate_identifier
        from src.pipeline.spec_schema import PipelineSpec

        spec = PipelineSpec(**req.model_dump())
        spec.validate_dag()
        _validate_identifier(spec.source)
        _validate_identifier(spec.target)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid PipelineSpec: {e}")
    if not _user_owns_table(username, req.source):
        raise HTTPException(status_code=403, detail="Source table does not belong to user")
    try:
        with SessionLocal() as s:
            p = s.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
            if not p or p.owner != username:
                raise HTTPException(status_code=404, detail="Pipeline not found")
            p.name = req.name
            p.source = req.source
            p.target = req.target
            p.spec_json = json.dumps(req.model_dump(), ensure_ascii=False)
            p.version = (p.version or 1) + 1
            s.commit()
            return {"pipeline_id": p.id, "version": p.version}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("update_pipeline failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update pipeline")


class PipelineGenerateRequest(BaseModel):
    source: str
    target: str
    description: str


@router.post("/pipelines/generate", dependencies=[Depends(check_rate_limit)])
async def generate_pipeline(req: PipelineGenerateRequest, username: str = Depends(get_current_user)):
    """AI sinh PipelineSpec tu mo ta tieng Viet (BYOK) — validate DAG + schema, khong persist (muc AI)."""
    import logging as _logging
    import os as _os

    _logger = _logging.getLogger(__name__)
    if not req.description or not req.description.strip():
        raise HTTPException(status_code=400, detail="description is required")
    if not _user_owns_table(username, req.source):
        raise HTTPException(status_code=403, detail="Source table does not belong to user")
    try:
        from src.pipeline.executor import _validate_identifier
        from src.pipeline.spec_schema import PipelineSpec

        _validate_identifier(req.source)
        _validate_identifier(req.target)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid identifiers: {e}")
    # Lay schema cot (LIMIT 1, khong doc raw rows cho LLM)
    try:
        from src.warehouse.connection import get_conn

        conn = get_conn()
        try:
            schema, table = req.source.split(".", 1)
            cols = conn.execute(f'SELECT * FROM "{schema}"."{table}" LIMIT 1').fetchdf().columns.tolist()
        finally:
            conn.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot read source schema: {e}")
    model_used = "rule-based"
    warnings: list = []
    # Spec mac dinh an toan (fallback khi khong co key / LLM fail)
    spec = {
        "name": "ai-pipeline",
        "source": req.source,
        "target": req.target,
        "steps": [{"id": "s1", "op": "drop_duplicates", "params": {}, "depends_on": []}],
    }
    try:
        from src.core.database import get_api_key
        from src.core.llm_client import complete_json
        from src.prompts.etl_author import build_prompt, validate_spec

        user_key = get_api_key(username)
        if user_key:
            provider = _os.environ.get("AI_PROVIDER", "openai")
            try:
                data, model = complete_json(
                    user_key, provider, build_prompt(req.description, cols, req.source, req.target)
                )
                candidate = {
                    "name": data.get("name", "ai-pipeline"),
                    "source": req.source,
                    "target": req.target,
                    "steps": data.get("steps", []),
                }
                PipelineSpec(**candidate).validate_dag()
                warnings = validate_spec(candidate, cols)
                spec, model_used = candidate, f"{provider}:{model}"
            except Exception as exc:
                _logger.warning("LLM pipeline generate failed, fallback default: %s", exc)
                warnings = [f"LLM unavailable, dung spec mac dinh: {exc}"]
        else:
            warnings = ["Chua co BYOK key (Settings) — dung spec mac dinh, hay sua tay."]
    except Exception as exc:
        _logger.warning("Pipeline generate AI path error: %s", exc)
    return {"spec": spec, "warnings": warnings, "model_used": model_used, "columns": cols}


@router.post("/pipelines/preview", dependencies=[Depends(check_rate_limit)])
async def preview_pipeline(req: PipelineCreateRequest, username: str = Depends(get_current_user)):
    """Dry-run on sample 100 rows (Plan 07)."""
    if not _user_owns_table(username, req.source):
        raise HTTPException(status_code=403, detail="Source table does not belong to user")
    try:
        from src.pipeline.executor import execute
        from src.pipeline.spec_schema import PipelineSpec

        spec = PipelineSpec(**req.model_dump())
        res = execute(spec, sample=True)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def _run_pipeline_task(pipeline_id: str, run_id: str):
    import json

    from src.core.database import Pipeline, PipelineRun, SessionLocal

    run_log = logging.getLogger(f"pipeline.run.{run_id}")
    steps_spec: list = []
    try:
        from src.pipeline.executor import execute
        from src.pipeline.spec_schema import PipelineSpec

        # Fetch spec from DB or in-memory fallback
        spec_dict = None
        with SessionLocal() as s:
            p = s.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
            if p:
                spec_dict = json.loads(p.spec_json) if p.spec_json else {}
                spec_dict["name"] = p.name
                spec_dict["source"] = p.source
                spec_dict["target"] = p.target
        if spec_dict is None:
            spec_dict = _pipelines.get(pipeline_id, {})
        steps_spec = spec_dict.get("steps", [])
        spec = PipelineSpec(
            name=spec_dict.get("name", "pipeline"),
            source=spec_dict.get("source", "raw.t"),
            target=spec_dict.get("target", "mart.t"),
            steps=spec_dict.get("steps", []),
        )
        run_log.info(
            "Run %s started: pipeline=%s target=%s steps=%d", run_id, pipeline_id, spec.target, len(steps_spec)
        )
        from src.pipeline.executor import sanitize_for_json

        res = sanitize_for_json(execute(spec, sample=False))
        status = "done" if res.get("status") == "done" else "failed"
        run_log.info("Run %s finished: status=%s rows=%s", run_id, status, res.get("rows"))
        # Update DB (rollback-safe)
        try:
            with SessionLocal() as s:
                r = s.query(PipelineRun).filter(PipelineRun.id == run_id).first()
                if r:
                    r.status = status
                    r.result_json = json.dumps(res, ensure_ascii=False)
                    s.commit()
        except Exception as exc:
            run_log.error("Run %s DB update failed: %s", run_id, exc, exc_info=True)
        # Per-step logs (mục 12): parse failed step từ error "Step {id} (...)"
        status_map: Dict[str, str] = {}
        log_text = "" if status == "done" else str(res.get("error", ""))
        if status == "done":
            for st in steps_spec:
                sid = st.get("id") if isinstance(st, dict) else "?"
                status_map[str(sid)] = "done"
        else:
            import re as _re

            m = _re.search(r"Step (\S+)", log_text)
            failed_sid = m.group(1).strip("()") if m else None
            seen_failed = False
            for st in steps_spec:
                sid = str(st.get("id") if isinstance(st, dict) else "?")
                if failed_sid and sid == failed_sid:
                    status_map[sid] = "failed"
                    seen_failed = True
                elif seen_failed:
                    status_map[sid] = "skipped"
                else:
                    status_map[sid] = "done" if failed_sid else "failed"
        _write_step_logs(run_id, steps_spec, status_map, log_text)
        # Also update in-memory for backward compat
        if run_id in _runs:
            _runs[run_id]["status"] = status
            _runs[run_id]["result"] = res
    except TimeoutError as e:
        # Mục 10: warehouse lock timeout → failed rõ ràng
        import json as _json

        run_log.error("Run %s lock timeout: %s", run_id, e)
        try:
            with SessionLocal() as s:
                r = s.query(PipelineRun).filter(PipelineRun.id == run_id).first()
                if r:
                    r.status = "failed"
                    r.result_json = _json.dumps({"error": f"Warehouse busy, thử lại sau: {e}"}, ensure_ascii=False)
                    s.commit()
        except Exception:
            pass
        if run_id in _runs:
            _runs[run_id]["status"] = "failed"
            _runs[run_id]["error"] = str(e)
        _write_step_logs(run_id, steps_spec, {}, f"lock timeout: {e}")
    except Exception as e:
        import json as _json

        run_log.error("Run %s crashed: %s", run_id, e, exc_info=True)
        try:
            with SessionLocal() as s:
                r = s.query(PipelineRun).filter(PipelineRun.id == run_id).first()
                if r:
                    r.status = "failed"
                    r.result_json = _json.dumps({"error": str(e)}, ensure_ascii=False)
                    s.commit()
        except Exception:
            pass
        if run_id in _runs:
            _runs[run_id]["status"] = "failed"
            _runs[run_id]["error"] = str(e)
        _write_step_logs(run_id, steps_spec, {}, str(e))


@router.post("/pipelines/run", dependencies=[Depends(check_rate_limit)])
async def run_pipeline(pipeline_id: str, background_tasks: BackgroundTasks, username: str = Depends(get_current_user)):
    import uuid

    from src.core.database import Pipeline, PipelineRun, SessionLocal

    # Check existence via DB or in-memory
    exists = False
    with SessionLocal() as s:
        p = s.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
        if p and p.owner == username:
            exists = True
    if not exists and (pipeline_id not in _pipelines or _pipelines[pipeline_id]["owner"] != username):
        raise HTTPException(status_code=404, detail="Pipeline not found")
    # Mục 10: cùng pipeline đang chạy → 409 (tránh 2 run ghi cùng mart.target)
    lock = _lock_for(pipeline_id)
    if lock.locked():
        raise HTTPException(status_code=409, detail="Pipeline is already running, thử lại sau")

    def _guarded_task(pid: str, rid: str):
        with lock:
            _run_pipeline_task(pid, rid)

    run_id = str(uuid.uuid4())[:8]
    # Persist run in DB (rollback-safe)
    try:
        with SessionLocal() as s:
            r = PipelineRun(id=run_id, pipeline_id=pipeline_id, status="queued")
            s.add(r)
            s.commit()
    except Exception as exc:
        logger.error("run_pipeline persist failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create run")
    _runs[run_id] = {
        "run_id": run_id,
        "pipeline_id": pipeline_id,
        "owner": username,
        "status": "queued",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    background_tasks.add_task(_guarded_task, pipeline_id, run_id)
    _runs[run_id]["status"] = "running"
    # Update DB to running
    try:
        with SessionLocal() as s:
            r = s.query(PipelineRun).filter(PipelineRun.id == run_id).first()
            if r:
                r.status = "running"
                s.commit()
    except Exception:
        pass
    return {"run_id": run_id, "status": "queued"}


@router.get("/runs/{run_id}", dependencies=[Depends(check_rate_limit)])
async def get_run(run_id: str, username: str = Depends(get_current_user)):
    import json

    from src.core.database import Pipeline, PipelineRun, PipelineStep, SessionLocal

    with SessionLocal() as s:
        r = s.query(PipelineRun).filter(PipelineRun.id == run_id).first()
        if r:
            # Check owner via pipeline
            p = s.query(Pipeline).filter(Pipeline.id == r.pipeline_id).first()
            if p and p.owner == username:
                result = {}
                if r.result_json:
                    try:
                        result = json.loads(r.result_json)
                    except Exception:
                        result = {"raw": r.result_json}
                steps = [
                    {"step_id": st.step_id, "status": st.status, "log": st.log}
                    for st in s.query(PipelineStep).filter(PipelineStep.run_id == run_id).all()
                ]
                return {
                    "run_id": r.id,
                    "pipeline_id": r.pipeline_id,
                    "status": r.status,
                    "result": result,
                    "steps": steps,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
    # Fallback in-memory
    r = _runs.get(run_id)
    if not r or r["owner"] != username:
        raise HTTPException(status_code=404, detail="Run not found")
    return r


@router.get("/runs", dependencies=[Depends(check_rate_limit)])
async def list_runs(username: str = Depends(get_current_user)):
    from src.core.database import Pipeline, PipelineRun, SessionLocal

    with SessionLocal() as s:
        # Join to filter by owner
        rows = (
            s.query(PipelineRun)
            .join(Pipeline, Pipeline.id == PipelineRun.pipeline_id)
            .filter(Pipeline.owner == username)
            .all()
        )
        if rows:
            items = [
                {
                    "run_id": r.id,
                    "pipeline_id": r.pipeline_id,
                    "status": r.status,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in rows
            ]
            return {"runs": items, "count": len(items)}
    # Fallback
    items = [v for v in _runs.values() if v["owner"] == username]
    return {"runs": items, "count": len(items)}
