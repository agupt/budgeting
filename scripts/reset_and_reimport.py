#!/usr/bin/env python3
"""Reset database and re-import all statements."""
import sys
from pathlib import Path
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    db_path = Path(__file__).parent.parent / "data" / "budgeting.db"

    print("=" * 60)
    print("DATABASE RESET")
    print("=" * 60)
    print()

    # Check if database exists
    if db_path.exists():
        print(f"⚠️  Database found at: {db_path}")
        response = input("Delete and recreate? (yes/no): ").strip().lower()

        if response != "yes":
            print("Aborted.")
            return

        # Delete database
        os.remove(db_path)
        print("✓ Database deleted")
    else:
        print("No existing database found")

    print()
    print("Creating new database...")

    # Create database
    from src.database import get_engine, Base
    engine = get_engine()
    Base.metadata.create_all(engine)

    print(f"✓ Database created at: {db_path}")
    print(f"✓ Tables: {', '.join(Base.metadata.tables.keys())}")
    print()

    print("=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print()
    print("1. Create an account (via UI or CLI):")
    print("   streamlit run app.py")
    print("   OR")
    print("   python -c \"from src.database import *; s = get_session(); a = Account(name='BOA Checking', institution='Bank of America', account_type='checking'); s.add(a); s.commit(); print(f'Created account ID: {a.id}')")
    print()
    print("2. Import statements:")
    print("   python scripts/import_statements.py --account-id 1 --directory statements/BankOfAmerica-Statement/")
    print()

if __name__ == "__main__":
    main()
