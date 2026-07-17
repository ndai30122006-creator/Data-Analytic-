"""Unit tests for API endpoints (api.py)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone, timedelta

from fastapi.testclient import TestClient

# Mock database before importing api
with patch('src.core.database.init_db'):
    from api import app


client = TestClient(app)


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_check(self):
        """Test health check endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


class TestAuthEndpoints:
    """Tests for authentication endpoints."""

    @patch('api.create_user')
    def test_register_success(self, mock_create_user):
        """Test successful user registration."""
        mock_user = MagicMock()
        mock_user.username = "newuser"
        mock_create_user.return_value = mock_user

        response = client.post("/auth/register", json={
            "username": "newuser",
            "password": "securepass123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "registered successfully" in data["message"]

    def test_register_short_password(self):
        """Test registration with short password."""
        response = client.post("/auth/register", json={
            "username": "testuser",
            "password": "12345"  # Less than 6 characters
        })
        assert response.status_code == 400
        data = response.json()
        assert "Password must be at least 6 characters" in data["detail"]

    def test_register_empty_username(self):
        """Test registration with empty username."""
        response = client.post("/auth/register", json={
            "username": "",
            "password": "securepass123"
        })
        assert response.status_code == 400

    @patch('api.verify_user_password')
    def test_login_success(self, mock_verify):
        """Test successful login."""
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_user.is_active = True
        mock_verify.return_value = mock_user

        response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "correctpass"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["username"] == "testuser"

    @patch('api.verify_user_password')
    def test_login_invalid_credentials(self, mock_verify):
        """Test login with invalid credentials."""
        mock_verify.return_value = None

        response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "wrongpass"
        })
        assert response.status_code == 401

    @patch('api.verify_user_password')
    def test_login_disabled_account(self, mock_verify):
        """Test login with disabled account."""
        mock_user = MagicMock()
        mock_user.is_active = False
        mock_verify.return_value = mock_user

        response = client.post("/auth/login", json={
            "username": "disabled_user",
            "password": "pass123"
        })
        assert response.status_code == 403

    def test_verify_without_token(self):
        """Test verify endpoint without token (422 due to missing required header)."""
        response = client.get("/auth/verify")
        # FastAPI returns 422 for missing required header
        assert response.status_code in (401, 422)

    def test_verify_with_invalid_token(self):
        """Test verify endpoint with invalid token."""
        response = client.get(
            "/auth/verify",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        assert response.status_code == 401


class TestApiKeyEndpoint:
    """Tests for API key management endpoint."""

    def test_update_api_key_without_auth(self):
        """Test updating API key without authentication."""
        response = client.post("/auth/api-key", json={"api_key": "sk-test"})
        # FastAPI returns 422 for missing required header
        assert response.status_code in (401, 422)

    def test_update_api_key_empty(self):
        """Test updating with empty API key."""
        # First get a valid token
        with patch('api.verify_user_password') as mock_verify:
            mock_user = MagicMock()
            mock_user.username = "testuser"
            mock_user.is_active = True
            mock_verify.return_value = mock_user

            login_resp = client.post("/auth/login", json={
                "username": "testuser",
                "password": "pass123"
            })
            token = login_resp.json()["access_token"]

            # Try with empty API key
            response = client.post(
                "/auth/api-key",
                json={"api_key": ""},
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 400


class TestAnalysisEndpoint:
    """Tests for analysis endpoints."""

    def test_run_analysis_without_auth(self):
        """Test running analysis without authentication."""
        response = client.post("/analysis/run", json={
            "dataset_name": "test",
            "analysis_type": "overview"
        })
        # FastAPI returns 422 for missing required header
        assert response.status_code in (401, 422)

    def test_run_analysis_missing_fields(self):
        """Test running analysis with missing required fields."""
        with patch('api.verify_user_password') as mock_verify:
            mock_user = MagicMock()
            mock_user.username = "testuser"
            mock_user.is_active = True
            mock_verify.return_value = mock_user

            login_resp = client.post("/auth/login", json={
                "username": "testuser",
                "password": "pass123"
            })
            token = login_resp.json()["access_token"]

            # Missing dataset_name (FastAPI validates via Pydantic - returns 422)
            response = client.post(
                "/analysis/run",
                json={"analysis_type": "overview"},
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code in (400, 422)

            # Missing analysis_type
            response = client.post(
                "/analysis/run",
                json={"dataset_name": "test"},
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code in (400, 422)


class TestEnvValidation:
    """Tests for environment validation endpoint."""

    def test_env_validate(self):
        """Test environment validation endpoint."""
        response = client.get("/env/validate")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "warnings" in data
        assert "cors_origins" in data
        assert "rate_limiter" in data