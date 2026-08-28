"""FastAPI Backend for Learning Analytics SaaS — JWT + bcrypt + SQLAlchemy + rate limiting"""
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, Depends, status, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import jwt

from src.core.database import (
    create_user,
    verify_user_password,
    get_user,
    update_api_key,
    delete_user,
    list_datasets as db_list_datasets,
    create_dataset as db_create_dataset,
    get_dataset as db_get_dataset,
    delete_dataset as db_delete_dataset,
)
from src.utils.security import (
    get_jwt_secret_key,
    get_jwt_algorithm,
    get_access_token_expire_minutes,
    get_cors_origins,
    validate_environment,
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Learning Analytics API", version="1.3.0")

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
    """Simple sliding-window rate limiter (in-memory fallback)."""
    now = datetime.now(timezone.utc)
    if client_ip not in _request_counts:
        _request_counts[client_ip] = []
    _request_counts[client_ip] = [
        t for t in _request_counts[client_ip]
        if (now - t).total_seconds() < 60
    ]
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
        allow_credentials=True,
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
        "Unhandled exception: %s | Path: %s | Detail: %s",
        type(exc).__name__, request.url.path, str(exc), exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error. Please try again later."}
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
    token = authorization[len("Bearer "):]
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

@app.post("/auth/login", response_model=LoginResponse)
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

@app.post("/auth/register")
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
        run_ttest_independent,
        run_ttest_onesample,
        run_ttest_paired,
        run_anova,
        run_mannwhitney,
        run_kruskal,
        run_bootstrap,
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
        result["boot_stats"] = result["boot_stats"].tolist() if hasattr(result["boot_stats"], "tolist") else result["boot_stats"]
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


@app.post("/analysis/run")
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