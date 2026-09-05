"""FastAPI Backend for Learning Analytics SaaS — JWT + bcrypt + SQLAlchemy + rate limiting"""

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from src.core.database import create_dataset as db_create_dataset
from src.core.database import (
    create_user,
)
from src.core.database import delete_dataset as db_delete_dataset
from src.core.database import (
    delete_user,
)
from src.core.database import get_dataset as db_get_dataset
from src.core.database import list_datasets as db_list_datasets
from src.core.database import (
    update_api_key,
    verify_user_password,
)
from src.utils.security import (
    get_access_token_expire_minutes,
    get_cors_origins,
    get_jwt_algorithm,
    get_jwt_secret_key,
    validate_environment,
)

logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan: replace deprecated @app.on_event('startup')."""
    try:
        from src.core.database import init_db

        init_db()
    except Exception as exc:
        logger.warning("DB init on startup failed: %s", exc)
    yield


app = FastAPI(title="Learning Analytics API", version="1.3.0", lifespan=lifespan)


# ── Configuration ──
SECRET_KEY = get_jwt_secret_key()
ALGORITHM = get_jwt_algorithm()
ACCESS_TOKEN_EXPIRE_MINUTES = get_access_token_expire_minutes()
RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "60"))

# ── Redis-based rate limiter (falls back to in-memory) ──
try:
    import redis.asyncio as aioredis

    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    _redis_available = True
    logger.info("Redis rate limiter configured: %s", REDIS_URL)
except ImportError:
    _redis = None
    _redis_available = False
    logger.warning("redis not installed; falling back to in-memory rate limiter. pip install redis")
except Exception as exc:
    _redis = None
    _redis_available = False
    logger.warning("Redis connection failed: %s; falling back to in-memory rate limiter", exc)

# ── In-memory fallback rate limiter ──
_request_counts: Dict[str, list] = {}


async def _check_rate_limit_redis(client_ip: str) -> bool:
    """Sliding-window rate limiter using Redis."""
    if not _redis_available:
        return _check_rate_limit_memory(client_ip)
    try:
        key = f"ratelimit:{client_ip}"
        now = datetime.now(timezone.utc).timestamp()
        window = 60  # seconds

        # Remove old entries and add current
        await _redis.zremrangebyscore(key, 0, now - window)
        await _redis.zadd(key, {str(now): now})
        await _redis.expire(key, window)

        count = await _redis.zcard(key)
        return count <= RATE_LIMIT_PER_MINUTE
    except Exception as exc:
        logger.error("Redis rate limit check failed: %s", exc)
        return _check_rate_limit_memory(client_ip)


def _check_rate_limit_memory(client_ip: str) -> bool:
    """Simple sliding-window rate limiter (in-memory fallback) — bounded."""
    now = datetime.now(timezone.utc)
    # Periodic cleanup to avoid unbounded dict growth
    if len(_request_counts) > 1000:
        # Remove stale IPs
        for k in list(_request_counts.keys()):
            _request_counts[k] = [t for t in _request_counts[k] if (now - t).total_seconds() < 60]
            if not _request_counts[k]:
                del _request_counts[k]
            if len(_request_counts) <= 500:
                break
    if client_ip not in _request_counts:
        _request_counts[client_ip] = []
    _request_counts[client_ip] = [t for t in _request_counts[client_ip] if (now - t).total_seconds() < 60]
    if len(_request_counts[client_ip]) >= RATE_LIMIT_PER_MINUTE:
        return False
    _request_counts[client_ip].append(now)
    return True


async def check_rate_limit(request: Request) -> None:
    """Dependency: check rate limit for the current request."""
    client_ip = request.client.host if request.client else "unknown"
    allowed = await _check_rate_limit_redis(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
        )


# ── CORS Configuration ──
cors_origins = get_cors_origins()
allow_all_cors = os.environ.get("CORS_ALLOW_ALL", "false").lower() == "true"

if allow_all_cors:
    logger.warning("CORS_ALLOW_ALL is enabled. This is insecure for production.")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # Must be False when allow_origins=["*"] per Fetch spec
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )


# ── Global exception handler ──
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception: %s | Path: %s | Detail: %s", type(exc).__name__, request.url.path, str(exc), exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error. Please try again later."},
    )


# ── Models ─────────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    expires_in: int


class RegisterRequest(BaseModel):
    username: str
    password: str


class AnalysisRequest(BaseModel):
    dataset_name: str
    analysis_type: str
    params: Dict[str, Any] = {}


class ApiKeyUpdateRequest(BaseModel):
    api_key: str


class CreateDatasetRequest(BaseModel):
    dataset_name: str
    rows: int = 0
    cols: int = 0


# ── Token utilities ────────────────────────────────────────
def create_access_token(username: str) -> tuple[str, datetime]:
    """Create a JWT access token with expiry."""
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": username,
        "iat": datetime.now(timezone.utc),
        "exp": expires_at,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, expires_at


def verify_access_token(token: str) -> Optional[str]:
    """Verify a JWT token and return the username."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as exc:
        logger.warning("Invalid token: %s", exc)
        return None


async def get_current_user(authorization: str = Header(...)) -> str:
    """Dependency: extract and verify Bearer JWT token."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization[len("Bearer ") :]
    username = verify_access_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username


# ── Endpoints ──────────────────────────────────────────────
@app.get("/")
async def root():
    return {"message": "Learning Analytics API", "version": "1.3.0"}


@app.post("/auth/login", response_model=LoginResponse, dependencies=[Depends(check_rate_limit)])
async def login(request: LoginRequest, req: Request):
    """Authenticate user via SQLite DB and return JWT token."""
    user = verify_user_password(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )
    token, _ = create_access_token(request.username)
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        username=request.username,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@app.post("/auth/register", dependencies=[Depends(check_rate_limit)])
async def register(request: RegisterRequest, req: Request):
    """Register a new user (persisted to SQLite)."""
    if len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters",
        )
    if not request.username or not request.username.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username cannot be empty",
        )
    try:
        user = create_user(request.username, request.password)
        return {"message": f"User {user.username} registered successfully"}
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        if "UNIQUE constraint" in str(exc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )
        logger.error("Registration failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@app.get("/auth/verify")
async def verify_auth(username: str = Depends(get_current_user)):
    return {"username": username, "valid": True}


@app.post("/auth/api-key")
async def update_ai_api_key(
    request: ApiKeyUpdateRequest,
    username: str = Depends(get_current_user),
):
    """Update user's AI API key (for OpenAI/Gemini)."""
    if not request.api_key or not request.api_key.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key cannot be empty",
        )
    ok = update_api_key(username, request.api_key)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "API key updated"}


@app.get("/datasets")
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


@app.post("/datasets")
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


@app.delete("/datasets/{dataset_name}")
async def delete_dataset_endpoint(
    dataset_name: str,
    username: str = Depends(get_current_user),
):
    """Delete a dataset owned by the authenticated user."""
    ok = db_delete_dataset(username, dataset_name)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    return {"message": f"Dataset {dataset_name} deleted"}


# ── Plan 07: Datasets ingest/profile (P1 Step 6) ──
class IngestRequest(BaseModel):
    dataset_name: str
    rows: int = 0
    cols: int = 0
    profile: Dict[str, Any] = {}


@app.post("/datasets/ingest", dependencies=[Depends(check_rate_limit)])
async def ingest_dataset(
    request: Request,
    file: Optional[UploadFile] = File(None),
    username: str = Depends(get_current_user),
):
    """Ingest dataset -> raw + profile (supports JSON or file upload, Plan 07 P1)."""
    from src.core.database import SessionLocal, Dataset
    import json

    # File upload path (multipart) — used by ingest_screen
    if file is not None and getattr(file, "filename", None):
        # Handle file upload via warehouse ingest
        try:
            from src.warehouse.ingest import ingest_file

            # Pass file-like; warehouse ingest handles CSV/Excel
            result = ingest_file(username, file)
            # Register in registry
            from src.warehouse.registry import register_dataset
            import json as _json

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
            # Update rows/cols
            with SessionLocal() as s:
                obj = s.query(Dataset).filter(Dataset.id == ds.id).first()
                obj.rows = result["rows"]
                obj.cols = result["cols"]
                s.commit()
            return {
                "message": f"Ingested {file.filename} -> {result['table']}",
                "dataset_id": ds.id,
                "profile": result["profile"],
                "quality": result.get("quality"),
            }
        except Exception as e:
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
        with SessionLocal() as s:
            obj = s.query(Dataset).filter(Dataset.id == ds.id).first()
            obj.profile_json = json.dumps(req.profile, ensure_ascii=False)
            s.commit()
    return {"message": f"Ingested {ds.dataset_name}", "dataset_id": ds.id, "profile": req.profile}


@app.get("/datasets/{dataset_id}/profile", dependencies=[Depends(check_rate_limit)])
async def get_dataset_profile(dataset_id: int, username: str = Depends(get_current_user)):
    from src.core.database import SessionLocal, Dataset
    import json

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


# ── Plan 07: Pipelines (persisted via DB, P0 fix) ──
from fastapi import BackgroundTasks

# Keep in-memory for backward compat during transition, but primary is DB
_pipelines: Dict[str, Dict[str, Any]] = {}
_runs: Dict[str, Dict[str, Any]] = {}


class PipelineCreateRequest(BaseModel):
    name: str
    source: str
    target: str
    steps: list = []


@app.post("/pipelines", dependencies=[Depends(check_rate_limit)])
async def create_pipeline(req: PipelineCreateRequest, username: str = Depends(get_current_user)):
    import json
    import uuid

    from src.core.database import Pipeline, SessionLocal

    pid = str(uuid.uuid4())[:8]
    spec_json = json.dumps(req.model_dump(), ensure_ascii=False)
    with SessionLocal() as s:
        p = Pipeline(id=pid, owner=username, name=req.name, source=req.source, target=req.target, spec_json=spec_json)
        s.add(p)
        s.commit()
    # Keep in-memory for preview/run backward compat
    _pipelines[pid] = {
        "id": pid,
        "owner": username,
        **req.model_dump(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return {"pipeline_id": pid, "spec": _pipelines[pid]}


@app.get("/pipelines", dependencies=[Depends(check_rate_limit)])
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
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]
        # Fallback in-memory if DB empty (for tests without DB)
        if not items:
            items = [v for v in _pipelines.values() if v["owner"] == username]
        return {"pipelines": items, "count": len(items)}


@app.get("/pipelines/{pipeline_id}", dependencies=[Depends(check_rate_limit)])
async def get_pipeline(pipeline_id: str, username: str = Depends(get_current_user)):
    from src.core.database import Pipeline, SessionLocal
    import json

    with SessionLocal() as s:
        p = s.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
        if p and p.owner == username:
            spec = json.loads(p.spec_json) if p.spec_json else {}
            return {
                "id": p.id,
                "owner": p.owner,
                **spec,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
    # Fallback in-memory
    p = _pipelines.get(pipeline_id)
    if not p or p["owner"] != username:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return p


@app.post("/pipelines/preview", dependencies=[Depends(check_rate_limit)])
async def preview_pipeline(req: PipelineCreateRequest, username: str = Depends(get_current_user)):
    """Dry-run on sample 100 rows (Plan 07)."""
    try:
        from src.pipeline.spec_schema import PipelineSpec
        from src.pipeline.executor import execute

        spec = PipelineSpec(**req.model_dump())
        res = execute(spec, sample=True)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def _run_pipeline_task(pipeline_id: str, run_id: str):
    import json

    from src.core.database import Pipeline, PipelineRun, SessionLocal

    try:
        from src.pipeline.spec_schema import PipelineSpec
        from src.pipeline.executor import execute

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
        spec = PipelineSpec(
            name=spec_dict.get("name", "pipeline"),
            source=spec_dict.get("source", "raw.t"),
            target=spec_dict.get("target", "mart.t"),
            steps=spec_dict.get("steps", []),
        )
        res = execute(spec, sample=False)
        status = "done" if res.get("status") == "done" else "failed"
        # Update DB
        with SessionLocal() as s:
            r = s.query(PipelineRun).filter(PipelineRun.id == run_id).first()
            if r:
                r.status = status
                r.result_json = json.dumps(res, ensure_ascii=False)
                s.commit()
        # Also update in-memory for backward compat
        if run_id in _runs:
            _runs[run_id]["status"] = status
            _runs[run_id]["result"] = res
    except Exception as e:
        import json as _json

        with SessionLocal() as s:
            r = s.query(PipelineRun).filter(PipelineRun.id == run_id).first()
            if r:
                r.status = "failed"
                r.result_json = _json.dumps({"error": str(e)}, ensure_ascii=False)
                s.commit()
        if run_id in _runs:
            _runs[run_id]["status"] = "failed"
            _runs[run_id]["error"] = str(e)


@app.post("/pipelines/run", dependencies=[Depends(check_rate_limit)])
async def run_pipeline(pipeline_id: str, background_tasks: BackgroundTasks, username: str = Depends(get_current_user)):
    import json
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
    run_id = str(uuid.uuid4())[:8]
    # Persist run in DB
    with SessionLocal() as s:
        r = PipelineRun(id=run_id, pipeline_id=pipeline_id, status="queued")
        s.add(r)
        s.commit()
    _runs[run_id] = {
        "run_id": run_id,
        "pipeline_id": pipeline_id,
        "owner": username,
        "status": "queued",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    background_tasks.add_task(_run_pipeline_task, pipeline_id, run_id)
    _runs[run_id]["status"] = "running"
    # Update DB to running
    with SessionLocal() as s:
        r = s.query(PipelineRun).filter(PipelineRun.id == run_id).first()
        if r:
            r.status = "running"
            s.commit()
    return {"run_id": run_id, "status": "queued"}


@app.get("/runs/{run_id}", dependencies=[Depends(check_rate_limit)])
async def get_run(run_id: str, username: str = Depends(get_current_user)):
    from src.core.database import PipelineRun, SessionLocal
    import json

    with SessionLocal() as s:
        r = s.query(PipelineRun).filter(PipelineRun.id == run_id).first()
        if r:
            # Check owner via pipeline
            from src.core.database import Pipeline

            p = s.query(Pipeline).filter(Pipeline.id == r.pipeline_id).first()
            if p and p.owner == username:
                result = {}
                if r.result_json:
                    try:
                        result = json.loads(r.result_json)
                    except Exception:
                        result = {"raw": r.result_json}
                return {
                    "run_id": r.id,
                    "pipeline_id": r.pipeline_id,
                    "status": r.status,
                    "result": result,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
    # Fallback in-memory
    r = _runs.get(run_id)
    if not r or r["owner"] != username:
        raise HTTPException(status_code=404, detail="Run not found")
    return r


@app.get("/runs", dependencies=[Depends(check_rate_limit)])
async def list_runs(username: str = Depends(get_current_user)):
    from src.core.database import PipelineRun, Pipeline, SessionLocal

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


# ── Plan 07: Brief ──
class BriefCreateRequest(BaseModel):
    dataset_id: int


@app.post("/brief/{dataset_id}", dependencies=[Depends(check_rate_limit)])
async def create_brief(dataset_id: int, username: str = Depends(get_current_user)):
    from src.core.database import SessionLocal, Dataset, Brief
    import json

    with SessionLocal() as s:
        ds = s.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not ds or ds.username != username:
            raise HTTPException(status_code=404, detail="Dataset not found")
        # Get profile
        profile = {}
        if ds.profile_json:
            try:
                profile = json.loads(ds.profile_json)
            except Exception:
                profile = {}
        # Generate via briefer fallback (no LLM raw)
        from src.prompts.briefer import generate_brief_fallback

        content = generate_brief_fallback(profile)
        max_v = s.query(Brief).filter(Brief.dataset_id == dataset_id).count()
        b = Brief(dataset_id=dataset_id, version=max_v + 1, content=content, model_used="rule-based")
        s.add(b)
        s.commit()
        s.refresh(b)
        return {"brief_id": b.id, "version": b.version, "content": content, "model_used": "rule-based"}


@app.get("/brief/{dataset_id}", dependencies=[Depends(check_rate_limit)])
async def list_briefs(dataset_id: int, username: str = Depends(get_current_user)):
    from src.core.database import SessionLocal, Dataset, Brief

    with SessionLocal() as s:
        ds = s.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not ds or ds.username != username:
            raise HTTPException(status_code=404, detail="Dataset not found")
        briefs = s.query(Brief).filter(Brief.dataset_id == dataset_id).order_by(Brief.version.desc()).all()
        return {
            "briefs": [
                {
                    "version": b.version,
                    "content": b.content[:200],
                    "model_used": b.model_used,
                    "created_at": b.created_at.isoformat() if b.created_at else None,
                }
                for b in briefs
            ]
        }


@app.get("/brief/{dataset_id}/{version}", dependencies=[Depends(check_rate_limit)])
async def get_brief_version(dataset_id: int, version: int, username: str = Depends(get_current_user)):
    from src.core.database import SessionLocal, Dataset, Brief

    with SessionLocal() as s:
        ds = s.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not ds or ds.username != username:
            raise HTTPException(status_code=404, detail="Dataset not found")
        b = s.query(Brief).filter(Brief.dataset_id == dataset_id, Brief.version == version).first()
        if not b:
            raise HTTPException(status_code=404, detail="Brief version not found")
        return {"version": b.version, "content": b.content, "model_used": b.model_used}


# ── Plan 07: Dashboards ──
class DashboardCreateRequest(BaseModel):
    name: str
    spec: Dict[str, Any]


@app.post("/dashboards", dependencies=[Depends(check_rate_limit)])
async def create_dashboard(req: DashboardCreateRequest, username: str = Depends(get_current_user)):
    from src.core.database import SessionLocal, Dashboard
    import json

    with SessionLocal() as s:
        d = Dashboard(name=req.name, spec_json=json.dumps(req.spec, ensure_ascii=False), owner=username)
        s.add(d)
        s.commit()
        s.refresh(d)
        return {"dashboard_id": d.id, "name": d.name}


@app.get("/dashboards", dependencies=[Depends(check_rate_limit)])
async def list_dashboards(username: str = Depends(get_current_user)):
    from src.core.database import SessionLocal, Dashboard

    with SessionLocal() as s:
        items = s.query(Dashboard).filter(Dashboard.owner == username).all()
        return {
            "dashboards": [
                {"id": d.id, "name": d.name, "created_at": d.created_at.isoformat() if d.created_at else None}
                for d in items
            ]
        }


@app.get("/dashboards/{dashboard_id}", dependencies=[Depends(check_rate_limit)])
async def get_dashboard(dashboard_id: int, username: str = Depends(get_current_user)):
    from src.core.database import SessionLocal, Dashboard
    import json

    with SessionLocal() as s:
        d = s.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
        if not d or d.owner != username:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        return {"id": d.id, "name": d.name, "spec": json.loads(d.spec_json) if d.spec_json else {}}


@app.put("/dashboards/{dashboard_id}", dependencies=[Depends(check_rate_limit)])
async def update_dashboard(dashboard_id: int, req: DashboardCreateRequest, username: str = Depends(get_current_user)):
    from src.core.database import SessionLocal, Dashboard
    import json

    with SessionLocal() as s:
        d = s.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
        if not d or d.owner != username:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        d.spec_json = json.dumps(req.spec, ensure_ascii=False)
        d.name = req.name
        s.commit()
        return {"message": "Updated", "id": d.id}


@app.post("/dashboards/{dashboard_id}/data", dependencies=[Depends(check_rate_limit)])
async def dashboard_data(dashboard_id: int, username: str = Depends(get_current_user)):
    from src.core.database import SessionLocal, Dashboard
    import json

    with SessionLocal() as s:
        d = s.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
        if not d or d.owner != username:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        spec = json.loads(d.spec_json) if d.spec_json else {}
        # Each chart 1 query (skeleton)
        return {"dashboard_id": d.id, "spec": spec, "data": "1 query per chart skeleton"}


@app.post("/dashboards/generate", dependencies=[Depends(check_rate_limit)])
async def generate_dashboard(dataset_id: int, username: str = Depends(get_current_user)):
    from src.core.database import SessionLocal, Dataset
    import json

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

        spec = fallback_spec(profile, ds.duckdb_table or f"mart.{ds.dataset_name}")
        return {"spec": spec}


@app.delete("/auth/user")
async def delete_user_endpoint(username: str = Depends(get_current_user)):
    """Delete the authenticated user's own account."""
    ok = delete_user(username)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": f"User {username} deleted"}


def _dispatch_analysis(analysis_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Map analysis_type to real computation via src/core/statistical_tests."""
    import numpy as np

    from src.core.statistical_tests import (
        run_anova,
        run_bootstrap,
        run_kruskal,
        run_mannwhitney,
        run_ttest_independent,
        run_ttest_onesample,
        run_ttest_paired,
        run_two_proportion_ztest,
    )

    at = analysis_type.strip().lower()

    if at in ("ttest_independent", "ttest", "independent_ttest"):
        a = np.asarray(params.get("group_a") or params.get("data_a") or params.get("s1"), dtype=float)
        b = np.asarray(params.get("group_b") or params.get("data_b") or params.get("s2"), dtype=float)
        if a.size == 0 or b.size == 0:
            raise ValueError("group_a and group_b are required (non-empty arrays)")
        return run_ttest_independent(a, b)

    if at in ("ttest_onesample", "one_sample_ttest"):
        data = np.asarray(params.get("data") or params.get("group_a") or [], dtype=float)
        mu0 = float(params.get("mu0", params.get("mu", 0)))
        if data.size == 0:
            raise ValueError("data is required")
        return run_ttest_onesample(data, mu0)

    if at in ("ttest_paired", "paired_ttest"):
        before = np.asarray(params.get("before") or params.get("group_a") or [], dtype=float)
        after = np.asarray(params.get("after") or params.get("group_b") or [], dtype=float)
        if before.size == 0 or after.size == 0:
            raise ValueError("before and after are required")
        return run_ttest_paired(before, after)

    if at == "anova":
        groups_raw = params.get("groups")
        if not groups_raw or not isinstance(groups_raw, list):
            raise ValueError("groups (list of arrays) is required for ANOVA")
        groups = [np.asarray(g, dtype=float) for g in groups_raw]
        return run_anova(*groups)

    if at in ("mannwhitney", "mann_whitney", "mannwhitney_u"):
        a = np.asarray(params.get("group_a") or [], dtype=float)
        b = np.asarray(params.get("group_b") or [], dtype=float)
        if a.size == 0 or b.size == 0:
            raise ValueError("group_a and group_b are required")
        return run_mannwhitney(a, b)

    if at in ("kruskal", "kruskal_wallis"):
        groups_raw = params.get("groups")
        if not groups_raw or not isinstance(groups_raw, list):
            raise ValueError("groups is required for Kruskal-Wallis")
        groups = [np.asarray(g, dtype=float) for g in groups_raw]
        return run_kruskal(*groups)

    if at == "bootstrap":
        data = np.asarray(params.get("data") or params.get("group_a") or [], dtype=float)
        if data.size == 0:
            raise ValueError("data is required for bootstrap")
        n_iter = int(params.get("n_iter", 1000))
        conf_level = int(params.get("conf_level", 95))
        result = run_bootstrap(data, n_iter=n_iter, conf_level=conf_level)
        # Convert ndarray to list for JSON serialization
        result["boot_stats"] = (
            result["boot_stats"].tolist() if hasattr(result["boot_stats"], "tolist") else result["boot_stats"]
        )
        return result

    if at in ("ab_test", "two_proportion", "two_proportion_ztest", "abtest"):
        sa = int(params["successes_a"])
        ta = int(params["total_a"])
        sb = int(params["successes_b"])
        tb = int(params["total_b"])
        return run_two_proportion_ztest(sa, ta, sb, tb)

    if at in ("overview", "summary", "descriptive"):
        # Generic descriptive fallback — expects data array
        data = params.get("data")
        if data is not None:
            arr = np.asarray(data, dtype=float)
            return {
                "count": int(arr.size),
                "mean": float(np.mean(arr)) if arr.size else 0,
                "std": float(np.std(arr)) if arr.size else 0,
                "min": float(np.min(arr)) if arr.size else 0,
                "max": float(np.max(arr)) if arr.size else 0,
            }
        return {"message": "No data provided for overview", "params": params}

    raise ValueError(f"Unknown analysis_type: {analysis_type}")


@app.post("/analysis/run", dependencies=[Depends(check_rate_limit)])
async def run_analysis(
    request: AnalysisRequest,
    username: str = Depends(get_current_user),
):
    if not request.dataset_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="dataset_name is required",
        )
    if not request.analysis_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="analysis_type is required",
        )
    # If dataset_name is not "inline" and not "demo", verify it exists for this user
    if request.dataset_name not in ("inline", "demo", "__inline__"):
        ds = db_get_dataset(username, request.dataset_name)
        if ds is None:
            # Allow inline computation even when dataset not found — require data in params
            has_inline_data = any(k in request.params for k in ("data", "group_a", "groups", "successes_a"))
            if not has_inline_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Dataset '{request.dataset_name}' not found. Create it via POST /datasets or use dataset_name='inline' with data in params.",
                )
    try:
        results = _dispatch_analysis(request.analysis_type, request.params)
        # Ensure JSON serializable (convert numpy types)
        import numpy as np

        def _to_python(obj):
            if isinstance(obj, np.generic):
                return obj.item()
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, dict):
                return {k: _to_python(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_to_python(v) for v in obj]
            return obj

        results = _to_python(results)
        return {
            "status": "success",
            "username": username,
            "dataset": request.dataset_name,
            "analysis_type": request.analysis_type,
            "results": results,
        }
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.error("Analysis failed (%s): %s", request.analysis_type, exc, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Analysis failed")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/env/validate")
async def validate_env():
    """Validate environment configuration and return warnings."""
    warnings = validate_environment()
    return {
        "status": "warning" if warnings else "ok",
        "warnings": warnings,
        "cors_origins": cors_origins if not allow_all_cors else ["*"],
        "rate_limiter": "redis" if _redis_available else "in-memory",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
