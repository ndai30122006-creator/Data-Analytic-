"""Database models and session management using SQLAlchemy + bcrypt."""
import logging
import os
from datetime import datetime, timezone
from typing import Optional

# Load .env if present (so DEMO_MODE / DATABASE_URL from .env are respected)
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

import bcrypt

from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

# ── Configuration ──
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'users.db')}"
)

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """User account model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)  # bcrypt hash (60 chars)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    api_key_ai = Column(String(128), nullable=True)  # Optional AI API key


class Dataset(Base):
    """Dataset metadata model — stores per-user dataset info for API."""

    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), index=True, nullable=False)
    dataset_name = Column(String(128), nullable=False)
    rows = Column(Integer, nullable=True)
    cols = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_db():
    """Create all tables and optionally seed demo users."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized: %s", DATABASE_URL)
    _ensure_demo_users()


def get_user(username: str) -> Optional[User]:
    """Look up user by username."""
    session = SessionLocal()
    try:
        return session.query(User).filter(User.username == username).first()
    finally:
        session.close()


def _hash_password(password: str) -> str:
    """Hash password using bcrypt (salt included)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_user(username: str, password: str) -> User:
    """Create a new user with bcrypt-hashed password."""
    session = SessionLocal()
    try:
        user = User(
            username=username,
            password_hash=_hash_password(password),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        logger.info("User created: %s", username)
        return user
    finally:
        session.close()


def verify_user_password(username: str, password: str) -> Optional[User]:
    """Verify password and return user if valid."""
    user = get_user(username)
    if not user:
        return None
    if not _verify_password(password, user.password_hash):
        return None
    return user


def update_api_key(username: str, api_key: str) -> bool:
    """Update user's AI API key."""
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.username == username).first()
        if not user:
            return False
        user.api_key_ai = api_key
        session.commit()
        return True
    finally:
        session.close()


def delete_user(username: str) -> bool:
    """Delete a user by username. Returns True if deleted."""
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.username == username).first()
        if not user:
            return False
        session.delete(user)
        session.commit()
        logger.info("User deleted: %s", username)
        return True
    finally:
        session.close()


# ── Dataset helpers ──

def create_dataset(username: str, dataset_name: str, rows: int = 0, cols: int = 0) -> Dataset:
    """Persist dataset metadata for a user."""
    session = SessionLocal()
    try:
        ds = Dataset(username=username, dataset_name=dataset_name, rows=rows, cols=cols)
        session.add(ds)
        session.commit()
        session.refresh(ds)
        logger.info("Dataset created: %s/%s (%sx%s)", username, dataset_name, rows, cols)
        return ds
    finally:
        session.close()


def list_datasets(username: str) -> list[Dataset]:
    """Return all datasets for a user."""
    session = SessionLocal()
    try:
        return session.query(Dataset).filter(Dataset.username == username).all()
    finally:
        session.close()


def get_dataset(username: str, dataset_name: str) -> Optional[Dataset]:
    """Look up a single dataset by user + name."""
    session = SessionLocal()
    try:
        return session.query(Dataset).filter(
            Dataset.username == username, Dataset.dataset_name == dataset_name
        ).first()
    finally:
        session.close()


def delete_dataset(username: str, dataset_name: str) -> bool:
    """Delete a dataset. Returns True if deleted."""
    session = SessionLocal()
    try:
        ds = session.query(Dataset).filter(
            Dataset.username == username, Dataset.dataset_name == dataset_name
        ).first()
        if not ds:
            return False
        session.delete(ds)
        session.commit()
        return True
    finally:
        session.close()


def _ensure_demo_users():
    """Auto-create demo users when DEMO_MODE=true (env)."""
    if os.environ.get("DEMO_MODE", "false").lower() != "true":
        return
    demo_accounts = [
        (os.environ.get("DEMO_ADMIN_USERNAME", "admin"), os.environ.get("DEMO_ADMIN_PASSWORD", "admin123")),
        (os.environ.get("DEMO_USER_USERNAME", "user"), os.environ.get("DEMO_USER_PASSWORD", "user123")),
        (os.environ.get("DEMO_TEACHER_USERNAME", "teacher"), os.environ.get("DEMO_TEACHER_PASSWORD", "teacher123")),
    ]
    for uname, pwd in demo_accounts:
        if not uname or not pwd:
            continue
        try:
            existing = get_user(uname)
            if existing is None:
                create_user(uname, pwd)
                logger.info("Demo user auto-created: %s", uname)
        except Exception as exc:
            # Unique constraint race or other DB error — log and continue
            logger.warning("Failed to auto-create demo user %s: %s", uname, exc)


# Initialize on import
init_db()