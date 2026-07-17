"""
Security utilities — auto-generated SECRET_KEY, CORS configuration, environment validation.
"""
import os
import logging
import secrets
from typing import List, Optional

logger = logging.getLogger(__name__)


def generate_secret_key() -> str:
    """Generate a cryptographically secure random secret key."""
    return secrets.token_hex(32)


def get_jwt_secret_key() -> str:
    """
    Get JWT secret key from environment or generate a persistent one.
    
    In production, ALWAYS set JWT_SECRET_KEY environment variable.
    For development, a key is auto-generated and stored in .jwt_secret file.
    """
    env_key = os.environ.get("JWT_SECRET_KEY")
    if env_key:
        return env_key
    
    # Development fallback: persist key to file so restarts don't invalidate tokens
    secret_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".jwt_secret")
    try:
        if os.path.exists(secret_file):
            with open(secret_file, "r") as f:
                key = f.read().strip()
                if key:
                    return key
        key = generate_secret_key()
        with open(secret_file, "w") as f:
            f.write(key)
        logger.warning(
            "JWT_SECRET_KEY not set in environment. "
            "Generated development key saved to %s. "
            "For production, set JWT_SECRET_KEY environment variable.",
            secret_file,
        )
        return key
    except (IOError, OSError) as exc:
        logger.error("Failed to persist JWT secret: %s", exc)
        # Last resort: generate key in-memory (will invalidate on restart)
        return generate_secret_key()


ALLOWED_ORIGINS_DEV: List[str] = [
    "http://localhost:8501",
    "http://127.0.0.1:8501",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

ALLOWED_ORIGINS_PROD: List[str] = []


def get_cors_origins() -> List[str]:
    """
    Get allowed CORS origins based on environment.
    
    In production, set ALLOWED_ORIGINS env var as comma-separated list.
    Falls back to DEVELOPMENT origins.
    """
    env_origins = os.environ.get("ALLOWED_ORIGINS")
    if env_origins:
        return [o.strip() for o in env_origins.split(",") if o.strip()]
    
    is_production = os.environ.get("ENVIRONMENT", "").lower() in ("production", "prod")
    if is_production:
        logger.warning(
            "ALLOWED_ORIGINS not configured in production. "
            "Set ALLOWED_ORIGINS environment variable with comma-separated origins."
        )
        return ALLOWED_ORIGINS_PROD
    
    return ALLOWED_ORIGINS_DEV


def get_jwt_algorithm() -> str:
    """Get JWT signing algorithm."""
    return os.environ.get("JWT_ALGORITHM", "HS256")


def get_access_token_expire_minutes() -> int:
    """Get access token expiry in minutes."""
    return int(os.environ.get("JWT_EXPIRE_MINUTES", "60"))


def validate_environment() -> List[str]:
    """Validate required environment variables and return warnings."""
    warnings: List[str] = []
    
    if not os.environ.get("JWT_SECRET_KEY"):
        warnings.append(
            "JWT_SECRET_KEY not set. Using auto-generated key (not suitable for production with multiple instances)."
        )
    
    if os.environ.get("ENVIRONMENT", "").lower() in ("production", "prod"):
        if not os.environ.get("DATABASE_URL"):
            warnings.append("DATABASE_URL not set. Using default SQLite (not suitable for production).")
        if not os.environ.get("ALLOWED_ORIGINS"):
            warnings.append("ALLOWED_ORIGINS not set. CORS will be restrictive.")
        if os.environ.get("CORS_ALLOW_ALL", "false").lower() == "true":
            warnings.append("CORS_ALLOW_ALL is set to true. This is insecure for production.")
    
    return warnings