"""FastAPI Backend for Learning Analytics SaaS"""
from fastapi import FastAPI, HTTPException, Depends, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import hashlib

app = FastAPI(title="Learning Analytics API", version="1.0.0")

# CORS middleware
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

class AnalysisRequest(BaseModel):
    dataset_name: str
    analysis_type: str
    params: Dict[str, Any] = {}

# ── Auth (simple demo) ─────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

USERS = {
    "admin": hash_password("admin123"),
    "user": hash_password("user123"),
    "teacher": hash_password("teacher123")
}

def create_token(username: str) -> str:
    """Create simple token (in production, use JWT)"""
    return hashlib.sha256(f"{username}:token".encode()).hexdigest()

def verify_token(token: str) -> Optional[str]:
    """Verify token and return username"""
    for username in USERS:
        if create_token(username) == token:
            return username
    return None

async def get_current_user(authorization: str = Header(...)) -> str:
    """Dependency that extracts and verifies the Bearer token from the Authorization header."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization[len("Bearer "):]
    username = verify_token(token)
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
    return {"message": "Learning Analytics API", "version": "1.0.0"}

@app.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login endpoint"""
    if request.username not in USERS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username",
        )

    if hash_password(request.password) != USERS[request.username]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )

    token = create_token(request.username)
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        username=request.username
    )

@app.post("/auth/register")
async def register(username: str, password: str):
    """Register new user"""
    if username in USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    if len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters",
        )

    # In production, save to database
    USERS[username] = hash_password(password)

    return {"message": f"User {username} registered successfully"}

@app.get("/auth/verify")
async def verify_auth(username: str = Depends(get_current_user)):
    """Verify token — also serves as a auth self-check via the dependency."""
    return {"username": username, "valid": True}

@app.get("/datasets")
async def list_datasets(username: str = Depends(get_current_user)):
    """List available datasets"""
    # In production, fetch from database
    return {"datasets": [], "username": username, "message": "No datasets in demo mode"}

@app.post("/analysis/run")
async def run_analysis(
    request: AnalysisRequest,
    username: str = Depends(get_current_user),
):
    """Run analysis on dataset"""
    # In production, this would trigger actual analysis
    return {
        "status": "success",
        "username": username,
        "dataset": request.dataset_name,
        "analysis_type": request.analysis_type,
        "results": {
            "message": "Analysis queued",
            "params": request.params
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)