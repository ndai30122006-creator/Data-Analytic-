"""FastAPI Backend for Learning Analytics SaaS — Secure auth with JWT + bcrypt"""
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Depends, status, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import jwt
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

app = FastAPI(title="Learning Analytics API", version="1.1.0")

# ── Configuration ──────────────────────────────────────────
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-me-in-production-use-env-var")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("JWT_EXPIRE_MINUTES", "60"))
MAX_USERS = 100  # Prevent unbounded dict growth

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

# ── In-memory user store (replace with DB in production) ──
USERS: Dict[str, str] = {}  # username -> bcrypt hash

def _seed_demo_users():
    """Seed demo users if the store is empty."""
    if not USERS:
        USERS["admin"] = pwd_context.hash("admin123")
        USERS["user"] = pwd_context.hash("user123")
        USERS["teacher"] = pwd_context.hash("teacher123")

_seed_demo_users()

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
    """Verify a JWT token and return the username (sub claim)."""
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
    return {"message": "Learning Analytics API", "version": "1.1.0"}

@app.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate user and return JWT token."""
    if request.username not in USERS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    if not pwd_context.verify(request.password, USERS[request.username]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token, _ = create_access_token(request.username)
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        username=request.username,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

@app.post("/auth/register")
async def register(request: RegisterRequest):
    """Register a new user."""
    if request.username in USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    if len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters",
        )
    if len(USERS) >= MAX_USERS:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Maximum user limit reached",
        )

    USERS[request.username] = pwd_context.hash(request.password)
    return {"message": f"User {request.username} registered successfully"}

@app.get("/auth/verify")
async def verify_auth(username: str = Depends(get_current_user)):
    """Verify token validity."""
    return {"username": username, "valid": True}

@app.get("/datasets")
async def list_datasets(username: str = Depends(get_current_user)):
    """List available datasets for the authenticated user."""
    return {"datasets": [], "username": username, "message": "No datasets in demo mode"}

@app.post("/analysis/run")
async def run_analysis(
    request: AnalysisRequest,
    username: str = Depends(get_current_user),
):
    """Queue an analysis job on a dataset."""
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