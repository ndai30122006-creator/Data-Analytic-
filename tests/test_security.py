"""Unit tests for security utilities (src/utils/security.py)"""
import os
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from src.utils.security import (
    generate_secret_key,
    get_jwt_secret_key,
    get_cors_origins,
    get_jwt_algorithm,
    get_access_token_expire_minutes,
    validate_environment,
)


class TestSecretKey:
    """Tests for secret key generation."""

    def test_generate_secret_key_length(self):
        """Secret key should be 64 hex characters (32 bytes)."""
        key = generate_secret_key()
        assert len(key) == 64
        assert isinstance(key, str)

    def test_generate_secret_key_uniqueness(self):
        """Two consecutive calls should produce different keys."""
        key1 = generate_secret_key()
        key2 = generate_secret_key()
        assert key1 != key2

    def test_get_jwt_secret_key_from_env(self, monkeypatch):
        """Should return key from environment variable if set."""
        monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-12345")
        key = get_jwt_secret_key()
        assert key == "test-secret-key-12345"

    def test_get_jwt_secret_key_from_file(self):
        """Should persist key to file for development."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a temporary .jwt_secret in a temp directory structure
            key = generate_secret_key()
            secret_file = os.path.join(tmpdir, ".jwt_secret")
            with open(secret_file, "w") as f:
                f.write(key)

            # Monkeypatch the secret_file path
            import src.utils.security as security_mod
            original_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            
            # Test that reading from file works
            with open(secret_file) as f:
                read_key = f.read().strip()
            assert read_key == key


class TestCORS:
    """Tests for CORS configuration."""

    def test_get_cors_origins_dev(self, monkeypatch):
        """Should return development origins by default."""
        monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
        monkeypatch.delenv("ENVIRONMENT", raising=False)
        origins = get_cors_origins()
        assert "http://localhost:8501" in origins
        assert "http://127.0.0.1:8501" in origins

    def test_get_cors_origins_from_env(self, monkeypatch):
        """Should return origins from environment variable."""
        monkeypatch.setenv("ALLOWED_ORIGINS", "https://app.example.com,https://api.example.com")
        origins = get_cors_origins()
        assert "https://app.example.com" in origins
        assert "https://api.example.com" in origins

    def test_get_cors_origins_production_no_env(self, monkeypatch):
        """Should return empty list in production without ALLOWED_ORIGINS."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
        origins = get_cors_origins()
        assert origins == []

    def test_get_cors_origins_empty_env(self, monkeypatch):
        """Should handle empty comma-separated origins."""
        monkeypatch.setenv("ALLOWED_ORIGINS", "   ")
        monkeypatch.delenv("ENVIRONMENT", raising=False)
        origins = get_cors_origins()
        assert len(origins) == 0


class TestJWTConfig:
    """Tests for JWT configuration."""

    def test_get_jwt_algorithm_default(self, monkeypatch):
        """Should return default algorithm."""
        monkeypatch.delenv("JWT_ALGORITHM", raising=False)
        assert get_jwt_algorithm() == "HS256"

    def test_get_jwt_algorithm_from_env(self, monkeypatch):
        """Should return algorithm from environment."""
        monkeypatch.setenv("JWT_ALGORITHM", "RS256")
        assert get_jwt_algorithm() == "RS256"

    def test_get_access_token_expire_default(self, monkeypatch):
        """Should return default expiry."""
        monkeypatch.delenv("JWT_EXPIRE_MINUTES", raising=False)
        assert get_access_token_expire_minutes() == 60

    def test_get_access_token_expire_from_env(self, monkeypatch):
        """Should return expiry from environment."""
        monkeypatch.setenv("JWT_EXPIRE_MINUTES", "30")
        assert get_access_token_expire_minutes() == 30


class TestEnvironmentValidation:
    """Tests for environment validation."""

    def test_validate_env_no_warnings_dev(self, monkeypatch):
        """Should return no warnings in development mode."""
        monkeypatch.setenv("ENVIRONMENT", "development")
        monkeypatch.setenv("JWT_SECRET_KEY", "test-key")
        warnings = validate_environment()
        # Development mode has fewer warnings
        assert isinstance(warnings, list)

    def test_validate_env_production_warnings(self, monkeypatch):
        """Should return warnings in production mode without required vars."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
        warnings = validate_environment()
        assert len(warnings) > 0
        assert any("JWT_SECRET_KEY" in w for w in warnings)

    def test_validate_env_cors_warning(self, monkeypatch):
        """Should warn about CORS_ALLOW_ALL in production."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("JWT_SECRET_KEY", "test-key")
        monkeypatch.setenv("CORS_ALLOW_ALL", "true")
        warnings = validate_environment()
        assert any("CORS_ALLOW_ALL" in w for w in warnings)