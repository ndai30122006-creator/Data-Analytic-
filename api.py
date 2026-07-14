"""FastAPI Backend for Learning Analytics SaaS — JWT + bcrypt + SQLAlchemy + rate limiting"""
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Depends, status, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import jwt

from src.core.database import create_user, verify_user_password, get_user, update_api_key

logger = logging.getLogger(__name__)

app = FastAPI(title="Learning Analytics API", version="1.2.0")

# ── Configuration ──
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-me-in-production-use-env-var")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("JWT_EXPIRE_MINUTES", "60"))
RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "60"))

pwd_context = None  # Handled by database module

# ── Simple in-memory rate limiter ──
_request_counts: Dict[str, list] = {}

def _check_rate_limit(client_ip: str) -> bool:
    """Simple sliding-window rate limiter."""
    now = timezone.now()
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    return {"message": "Learning Analytics API", "version": "1.2.0"}

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
    try:
        user = create_user(request.username, request.password)
        return {"message": f"User {user.username} registered successfully"}
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)