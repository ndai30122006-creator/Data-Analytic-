"""Auth router — register/login/verify/api-key/delete_user."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from src.api.deps import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    check_rate_limit,
    create_access_token,
    get_current_user,
)
from src.core.database import create_user, delete_user, get_api_provider, update_api_key, verify_user_password

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])


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


class ApiKeyUpdateRequest(BaseModel):
    api_key: str
    provider: str | None = None  # openai|gemini (luu that, het fake UI)


@router.post("/auth/login", response_model=LoginResponse, dependencies=[Depends(check_rate_limit)])
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


@router.post("/auth/register", dependencies=[Depends(check_rate_limit)])
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


@router.get("/auth/verify")
async def verify_auth(username: str = Depends(get_current_user)):
    return {"username": username, "valid": True}


@router.post("/auth/api-key")
async def update_ai_api_key(
    request: ApiKeyUpdateRequest,
    username: str = Depends(get_current_user),
):
    """Update user's AI API key (for OpenAI/Gemini)."""
    key = (request.api_key or "").strip()
    if not key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key cannot be empty",
        )
    if len(key) < 8 or len(key) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key length must be 8-1000 characters",
        )
    provider = (request.provider or "").strip().lower() or None
    if provider is not None and provider not in ("openai", "gemini"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="provider must be openai|gemini",
        )
    ok = update_api_key(username, key, provider)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "API key updated", "provider": provider or get_api_provider(username)}


@router.delete("/auth/user")
async def delete_user_endpoint(username: str = Depends(get_current_user)):
    """Delete the authenticated user's own account."""
    ok = delete_user(username)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": f"User {username} deleted"}
