"""Shared API dependencies — auth (JWT), rate limiting, ownership checks.

Tách từ api.py monolith (mục 7) để các routers dùng chung, tránh circular import.
"""

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import jwt
from fastapi import Header, HTTPException, Request, status

from src.utils.security import (
    get_access_token_expire_minutes,
    get_jwt_algorithm,
    get_jwt_secret_key,
)

logger = logging.getLogger(__name__)

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
    # Tests tat rate limit de tranh 429 rac giua cac test (DISABLE_RATE_LIMIT=1).
    # Production mac dinh bat (khong dat env nay).
    if os.environ.get("DISABLE_RATE_LIMIT", "").lower() in ("1", "true", "yes"):
        return
    client_ip = request.client.host if request.client else "unknown"
    allowed = await _check_rate_limit_redis(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
        )


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


async def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """Dependency: extract and verify Bearer JWT token (thieu header -> 401, khong 422)."""
    if not authorization or not authorization.startswith("Bearer "):
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


def _user_owns_table(username: str, table: str) -> bool:
    """Check whether raw./mart. table belongs to user (via datasets registry)."""
    import re as _re

    if not table or not isinstance(table, str):
        return False
    if not _re.match(r"^(raw|mart)\.[a-zA-Z_][a-zA-Z0-9_]{0,63}$", table):
        return False
    try:
        from src.core.database import Dataset, SessionLocal

        suffix = table.split(".", 1)[1].lower()
        with SessionLocal() as s:
            rows = s.query(Dataset).filter(Dataset.username == username).all()
            allowed: set = set()
            for d in rows:
                if getattr(d, "duckdb_table", None):
                    allowed.add(d.duckdb_table.lower())
                base = _re.sub(r"[^a-z0-9_]", "_", (d.dataset_name or "").lower())
                if base:
                    if base[0].isdigit():
                        base = f"t_{base}"
                    allowed.add(f"raw.{base[:64]}")
                    allowed.add(f"mart.{base[:64]}")
            return suffix and (table.lower() in allowed or f"raw.{suffix}" in allowed or f"mart.{suffix}" in allowed)
    except Exception:
        return False
