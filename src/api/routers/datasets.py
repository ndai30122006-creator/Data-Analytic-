"""Datasets router — CRUD metadata + ingest + profile."""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from pydantic import BaseModel, Field

from src.api.deps import check_rate_limit, get_current_user
from src.core.database import create_dataset as db_create_dataset
from src.core.database import delete_dataset as db_delete_dataset
from src.core.database import get_dataset as db_get_dataset
from src.core.database import list_datasets as db_list_datasets

logger = logging.getLogger(__name__)

router = APIRouter(tags=["datasets"])


class CreateDatasetRequest(BaseModel):
    dataset_name: str
    rows: int = Field(default=0, ge=0)
    cols: int = Field(default=0, ge=0)


class IngestRequest(BaseModel):
    dataset_name: str
    rows: int = Field(default=0, ge=0)
    cols: int = Field(default=0, ge=0)
    profile: Dict[str, Any] = {}


@router.get("/datasets")
async def list_datasets(username: str = Depends(get_current_user)):
    """List all datasets owned by the authenticated user (DB-backed)."""
    try:
        datasets = db_list_datasets(username)
        items = [
            {
                "id": d.id,
                "dataset_name": d.dataset_name,
                "rows": d.rows,
                "cols": d.cols,
                "version": getattr(d, "version", 1) or 1,
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
    try:
        ds = db_create_dataset(username, request.dataset_name.strip(), request.rows, request.cols)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        if "UNIQUE constraint" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dataset already exists")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create dataset")
    return {
        "message": f"Dataset {ds.dataset_name} created",
        "dataset": {"dataset_name": ds.dataset_name, "rows": ds.rows, "cols": ds.cols, "version": 1},
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

            try:
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
            except Exception as reg_exc:
                if "UNIQUE constraint" in str(reg_exc):
                    raise HTTPException(
                        status_code=400, detail=f"Dataset '{file.filename}' already exists, doi ten file khac"
                    )
                raise
            # Update rows/cols cung transaction (session_scope tu rollback)
            from src.core.database import session_scope

            with session_scope() as s:
                obj = s.query(Dataset).filter(Dataset.id == ds.id).first()
                obj.rows = result["rows"]
                obj.cols = result["cols"]
            return {
                "message": f"Ingested {file.filename} -> {result['table']}",
                "dataset_id": ds.id,
                "version": getattr(ds, "version", 1) or 1,
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
    try:
        ds = db_create_dataset(username, req.dataset_name, req.rows, req.cols)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if "UNIQUE constraint" in str(e):
            raise HTTPException(status_code=400, detail="Dataset already exists")
        raise HTTPException(status_code=500, detail="Failed to ingest dataset")
    if req.profile:
        from src.core.database import session_scope

        with session_scope() as s:
            obj = s.query(Dataset).filter(Dataset.id == ds.id).first()
            obj.profile_json = json.dumps(req.profile, ensure_ascii=False)
    return {"message": f"Ingested {ds.dataset_name}", "dataset_id": ds.id, "profile": req.profile}


@router.post("/datasets/demo", dependencies=[Depends(check_rate_limit)])
async def ingest_demo(username: str = Depends(get_current_user)):
    """Onboarding 1-click: sinh demo data (120 SV) + ingest, khong can file."""
    import json as _json

    from src.core.database import Dataset, session_scope
    from src.warehouse import ingest as _ing
    from src.warehouse.registry import register_dataset

    name = "demo_sinhvien"
    if db_get_dataset(username, name):
        raise HTTPException(status_code=400, detail="Demo da ton tai — xoa 'demo_sinhvien' roi thu lai")
    try:
        result = _ing.ingest_df(username, _ing.demo_dataframe(), name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Ingest failed: {e}")
    with session_scope() as s:
        ds = Dataset(
            username=username,
            dataset_name=name,
            rows=0,
            cols=0,
            version=1,
            duckdb_table=result["table"],
            file_path="demo::generated",
            profile_json=_json.dumps({"profile": result["profile"]}, ensure_ascii=False),
        )
        s.add(ds)
        s.flush()
        ds.rows = result["rows"]
        ds.cols = result["cols"]
        ds_id = ds.id
    return {
        "message": f"Ingested demo -> {result['table']}",
        "dataset_id": ds_id,
        "version": 1,
        "profile": result["profile"],
        "quality": result.get("quality"),
    }


@router.get("/tables/rows", dependencies=[Depends(check_rate_limit)])
async def get_table_rows(
    table: str,
    limit: int = 20,
    offset: int = 0,
    order_by: str | None = None,
    order_dir: str = "asc",
    q: str | None = None,
    username: str = Depends(get_current_user),
):
    """Xem rows that (phan trang/sort/search) — chi bang user so huu (muc Data Table Pro)."""
    import re as _re

    from src.api.deps import _user_owns_table

    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    if not _user_owns_table(username, table):
        raise HTTPException(status_code=403, detail="Table does not belong to user")
    if not _re.match(r"^(raw|mart)\.[a-zA-Z_][a-zA-Z0-9_]{0,63}$", table):
        raise HTTPException(status_code=400, detail="Invalid table")
    schema, tname = table.split(".", 1)
    tq = f'"{schema}"."{tname}"'
    try:
        from src.warehouse.connection import get_conn

        conn = get_conn()
        try:
            cols = [r[0] for r in conn.execute(f"SELECT * FROM {tq} LIMIT 0").description]
            if order_by and order_by not in cols:
                raise HTTPException(status_code=400, detail=f"Invalid order_by column: {order_by}")
            where, params = "", []
            if q:
                like = "%" + q.replace("%", "").replace("_", "")[:50] + "%"
                conds = " OR ".join([f'CAST("{c}" AS VARCHAR) ILIKE ?' for c in cols])
                where, params = f" WHERE ({conds})", [like] * len(cols)
            total = conn.execute(f"SELECT COUNT(*) FROM {tq}{where}", params).fetchone()[0]
            order = ""
            if order_by:
                d = "DESC" if order_dir.lower() == "desc" else "ASC"
                order = f' ORDER BY "{order_by}" {d}'
            rows = conn.execute(f"SELECT * FROM {tq}{where}{order} LIMIT {limit} OFFSET {offset}", params).fetchall()

            def _cell(v):
                import datetime as _dt
                import decimal as _dec
                import math as _m

                if v is None:
                    return None
                if isinstance(v, float) and (_m.isnan(v) or _m.isinf(v)):
                    return None
                if isinstance(v, (_dt.datetime, _dt.date)):
                    return v.isoformat()
                if isinstance(v, (int, float, str, bool)):
                    return v
                if isinstance(v, _dec.Decimal):
                    return float(v)
                return str(v)

            return {
                "table": table,
                "columns": cols,
                "rows": [[_cell(v) for v in r] for r in rows],
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        finally:
            conn.close()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Cannot read table: {exc}")


@router.get("/datasets/{dataset_id}/rows", dependencies=[Depends(check_rate_limit)])
async def get_dataset_rows(
    dataset_id: int,
    limit: int = 20,
    offset: int = 0,
    order_by: str | None = None,
    order_dir: str = "asc",
    q: str | None = None,
    username: str = Depends(get_current_user),
):
    """Shortcut theo dataset id (ownership check) -> forward ve /tables/rows logic."""
    from src.core.database import Dataset, SessionLocal

    with SessionLocal() as s:
        ds = s.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not ds or ds.username != username or not ds.duckdb_table:
            raise HTTPException(status_code=404, detail="Dataset not found")
        table = ds.duckdb_table
    return await get_table_rows(table, limit, offset, order_by, order_dir, q, username)


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
        return {
            "dataset_id": ds.id,
            "dataset_name": ds.dataset_name,
            "version": getattr(ds, "version", 1) or 1,
            "profile": profile,
        }
