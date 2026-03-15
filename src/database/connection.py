"""Database connection management."""
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Database path
DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_PATH = DB_DIR / "budgeting.db"


def get_engine():
    """Create and return SQLAlchemy engine."""
    # Ensure data directory exists
    DB_DIR.mkdir(parents=True, exist_ok=True)

    # Create engine with SQLite
    engine = create_engine(
        f"sqlite:///{DB_PATH}",
        echo=False,  # Set to True for SQL query logging
        connect_args={"check_same_thread": False}  # Allow multi-threading
    )
    return engine


def get_session() -> Session:
    """Create and return a database session."""
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()
