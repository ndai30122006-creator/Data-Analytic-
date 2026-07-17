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

from src.core.database import create_user, verify_user_password, get_user, update_api_key
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
    return {"datasets": [], "username": username, "message": "No datasets in demo mode"}

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
    return {
        "status": "success",
        "username": username,
        "dataset": request.dataset_name,
        "analysis_type": request.analysis_type,
        "results": {"message": "Analysis queued", "params": request.params},
    }

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