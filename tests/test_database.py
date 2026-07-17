"""Unit tests for src/core/database.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from sqlalchemy.exc import IntegrityError

from src.core.database import (
    User,
    SessionLocal,
    create_user,
    get_user,
    verify_user_password,
    update_api_key,
    _hash_password,
    _verify_password,
)


class TestPasswordHashing:
    """Tests for password hashing utilities."""

    def test_hash_and_verify(self):
        """Test that a hashed password can be verified."""
        password = "test_password_123!"
        hashed = _hash_password(password)
        assert hashed != password
        assert _verify_password(password, hashed)

    def test_wrong_password(self):
        """Test that wrong password fails verification."""
        password = "correct_password"
        wrong = "wrong_password"
        hashed = _hash_password(password)
        assert not _verify_password(wrong, hashed)

    def test_hash_uniqueness(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "same_password"
        hash1 = _hash_password(password)
        hash2 = _hash_password(password)
        assert hash1 != hash2


class TestUserCreation:
    """Tests for user creation and retrieval."""

    def test_create_user(self):
        """Test creating a new user."""
        username = "test_user_create"
        password = "secure_pass_123"
        try:
            user = create_user(username, password)
            assert user.username == username
            assert user.is_active is True
            assert user.id is not None
        finally:
            # Cleanup
            session = SessionLocal()
            try:
                session.query(User).filter(User.username == username).delete()
                session.commit()
            finally:
                session.close()

    def test_create_duplicate_user(self):
        """Test that creating duplicate username raises exception."""
        username = "test_dup_user"
        password = "pass123"
        try:
            create_user(username, password)
            with pytest.raises(IntegrityError):
                create_user(username, "other_pass")
        finally:
            session = SessionLocal()
            try:
                session.query(User).filter(User.username == username).delete()
                session.commit()
            finally:
                session.close()

    def test_get_nonexistent_user(self):
        """Test getting a user that doesn't exist."""
        result = get_user("nonexistent_user_xyz")
        assert result is None


class TestUserVerification:
    """Tests for user password verification."""

    def test_verify_valid_user(self):
        """Test verifying a valid user's password."""
        username = "test_verify_user"
        password = "verify_pass_123"
        try:
            create_user(username, password)
            result = verify_user_password(username, password)
            assert result is not None
            assert result.username == username
        finally:
            session = SessionLocal()
            try:
                session.query(User).filter(User.username == username).delete()
                session.commit()
            finally:
                session.close()

    def test_verify_wrong_password(self):
        """Test verifying with wrong password."""
        username = "test_wrong_pass"
        password = "correct_pass"
        try:
            create_user(username, password)
            result = verify_user_password(username, "wrong_pass")
            assert result is None
        finally:
            session = SessionLocal()
            try:
                session.query(User).filter(User.username == username).delete()
                session.commit()
            finally:
                session.close()

    def test_verify_nonexistent_user(self):
        """Test verifying a non-existent user."""
        result = verify_user_password("nonexistent_user", "any_pass")
        assert result is None


class TestApiKey:
    """Tests for API key management."""

    def test_update_api_key(self):
        """Test updating a user's API key."""
        username = "test_apikey_user"
        password = "pass123"
        api_key = "sk-test-key-12345"
        try:
            create_user(username, password)
            result = update_api_key(username, api_key)
            assert result is True

            # Verify the key was stored
            updated_user = get_user(username)
            assert updated_user.api_key_ai == api_key
        finally:
            session = SessionLocal()
            try:
                session.query(User).filter(User.username == username).delete()
                session.commit()
            finally:
                session.close()

    def test_update_api_key_nonexistent_user(self):
        """Test updating API key for non-existent user."""
        result = update_api_key("nonexistent_user", "some_key")
        assert result is False