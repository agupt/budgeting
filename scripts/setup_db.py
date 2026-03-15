#!/usr/bin/env python3
"""Initialize the budgeting database."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import Base, get_engine


def setup_database():
    """Create all database tables."""
    print("Initializing budgeting database...")

    engine = get_engine()

    # Create all tables
    Base.metadata.create_all(engine)

    print(f"✓ Database created successfully at: {engine.url}")
    print(f"✓ Tables created: {', '.join(Base.metadata.tables.keys())}")


if __name__ == "__main__":
    setup_database()
