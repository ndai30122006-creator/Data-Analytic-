"""Database models and session management using SQLAlchemy."""
import logging
import os
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# ── Configuration ──
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'users.db')}"
)

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """User account model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    api_key_ai = Column(String(128), nullable=True)  # Optional AI API key


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized: %s", DATABASE_URL)


def get_user(username: str) -> Optional[User]:
    """Look up user by username."""
    session = SessionLocal()
    try:
        return session.query(User).filter(User.username == username).first()
    finally:
        session.close()


def create_user(username: str, password: str) -> User:
    """Create a new user with hashed password."""
    session = SessionLocal()
    try:
        user = User(
            username=username,
            password_hash=pwd_context.hash(password),
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
    if not pwd_context.verify(password, user.password_hash):
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


# Initialize on import
init_db()