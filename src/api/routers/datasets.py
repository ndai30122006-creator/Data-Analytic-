"""Datasets router — CRUD metadata + ingest + profile."""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from pydantic import BaseModel

from src.api.deps import check_rate_limit, get_current_user
from src.core.database import (
    create_dataset as db_create_dataset,
)
from src.core.database import (
    delete_dataset as db_delete_dataset,
)
from src.core.database import (
    get_dataset as db_get_dataset,
)
from src.core.database import (
    list_datasets as db_list_datasets,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["datasets"])


class CreateDatasetRequest(BaseModel):
    dataset_name: str
    rows: int = 0
    cols: int = 0


class IngestRequest(BaseModel):
    dataset_name: str
    rows: int = 0
    cols: int = 0
    profile: Dict[str, Any] = {}


@router.get("/datasets")
async def list_datasets(username: str = Depends(get_current_user)):
    """List all datasets owned by the authenticated user (DB-backed)."""
    try:
        datasets = db_list_datasets(username)
        items = [
            {
                "dataset_name": d.dataset_name,
                "rows": d.rows,
                "cols": d.cols,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
            for d in datasets
        ]
        return {"datasets": items, "username": username, "count": len(items)}
    except Exception as exc:
        logger.error("list_datasets failed for %s: %s", username, exc, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list datasets")


@router.post("/datasets")
async def create_dataset_endpoint(
    request: CreateDatasetRequest,
    username: str = Depends(get_current_user),
):
    """Create dataset metadata for the authenticated user."""
    if not request.dataset_name or not request.dataset_name.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="dataset_name is required")
    if db_get_dataset(username, request.dataset_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dataset already exists")
    ds = db_create_dataset(username, request.dataset_name.strip(), request.rows, request.cols)
    return {
        "message": f"Dataset {ds.dataset_name} created",
        "dataset": {"dataset_name": ds.dataset_name, "rows": ds.rows, "cols": ds.cols},
    }


@router.delete("/datasets/{dataset_name}")
async def delete_dataset_endpoint(
    dataset_name: str,
    username: str = Depends(get_current_user),
):
    """Delete a dataset owned by the authenticated user."""
    ok = db_delete_dataset(username, dataset_name)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    return {"message": f"Dataset {dataset_name} deleted"}


@router.post("/datasets/ingest", dependencies=[Depends(check_rate_limit)])
async def ingest_dataset(
    request: Request,
    file: Optional[UploadFile] = File(None),
    username: str = Depends(get_current_user),
):
    """Ingest dataset -> raw + profile (supports JSON or file upload, Plan 07 P1)."""
    import json

    from src.core.database import Dataset, SessionLocal

    # File upload path (multipart) — used by ingest_screen
    if file is not None and getattr(file, "filename", None):
        # Handle file upload via warehouse ingest
        try:
            from src.warehouse.ingest import ingest_file

            # Pass file-like; warehouse ingest handles CSV/Excel
            result = ingest_file(username, file)
            # Register in registry (rollback-safe: single transaction)
            import json as _json

            from src.warehouse.registry import register_dataset

            ds = register_dataset(
                username,
                file.filename,
                result["table"],
                file_path=file.filename,
                profile_json=(
                    _json.dumps(result["profile"], ensure_ascii=False)
                    if isinstance(result["profile"], str)
                    else _json.dumps({"profile": result["profile"]}, ensure_ascii=False)
                ),
            )
            # Update rows/cols (mục 8: rollback nếu fail)
            try:
                with SessionLocal() as s:
                    obj = s.query(Dataset).filter(Dataset.id == ds.id).first()
                    obj.rows = result["rows"]
                    obj.cols = result["cols"]
                    s.commit()
            except Exception:
                with SessionLocal() as s:
                    s.rollback()
                raise
            return {
                "message": f"Ingested {file.filename} -> {result['table']}",
                "dataset_id": ds.id,
                "profile": result["profile"],
                "quality": result.get("quality"),
            }
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Ingest failed: {e}")
        except Exception as e:
            logger.error("Ingest failed for %s: %s", username, e, exc_info=True)
            raise HTTPException(status_code=400, detail=f"Ingest failed: {e}")

    # JSON path (for tests / programmatic)
    try:
        body = await request.json()
        req = IngestRequest(**body)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ingest request: need JSON {dataset_name} or file upload")
    ds = db_get_dataset(username, req.dataset_name)
    if ds:
        raise HTTPException(status_code=400, detail="Dataset already exists")
    ds = db_create_dataset(username, req.dataset_name, req.rows, req.cols)
    if req.profile:
        try:
            with SessionLocal() as s:
                obj = s.query(Dataset).filter(Dataset.id == ds.id).first()
                obj.profile_json = json.dumps(req.profile, ensure_ascii=False)
                s.commit()
        except Exception:
            with SessionLocal() as s:
                s.rollback()
            raise
    return {"message": f"Ingested {ds.dataset_name}", "dataset_id": ds.id, "profile": req.profile}


@router.get("/datasets/{dataset_id}/profile", dependencies=[Depends(check_rate_limit)])
async def get_dataset_profile(dataset_id: int, username: str = Depends(get_current_user)):
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
                profile = {"raw": ds.profile_json}
        # No raw data, only profile (Plan 03/07)
        return {"dataset_id": ds.id, "dataset_name": ds.dataset_name, "profile": profile}
