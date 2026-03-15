"""Tests for duplicate detection."""
import pytest
from datetime import date, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database import get_engine, Base, Account, Transaction, ImportLog
from src.utils.duplicate_detection import find_duplicate_transaction
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def session():
    """Create test database session."""
    engine = get_engine()
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def test_account(session):
    """Create test account."""
    account = Account(
        name="Test Checking",
        institution="Test Bank",
        account_type="checking"
    )
    session.add(account)
    session.commit()
    return account


@pytest.fixture
def import_log_1(session, test_account):
    """Create first import log."""
    log = ImportLog(
        account_id=test_account.id,
        filename="statement1.pdf",
        file_hash="hash1"
    )
    session.add(log)
    session.commit()
    return log


@pytest.fixture
def import_log_2(session, test_account):
    """Create second import log."""
    log = ImportLog(
        account_id=test_account.id,
        filename="statement2.pdf",
        file_hash="hash2"
    )
    session.add(log)
    session.commit()
    return log


def test_exact_duplicate_detection(session, test_account, import_log_1, import_log_2):
    """Test detection of exact duplicate transaction from DIFFERENT import."""
    # Create original transaction from import 1
    original = Transaction(
        account_id=test_account.id,
        date=date(2024, 1, 15),
        description="STARBUCKS COFFEE #123",
        amount=-5.50,
        source_file="statement1.pdf",
        import_log_id=import_log_1.id
    )
    session.add(original)
    session.commit()

    # Try to find duplicate from import 2 (should find it)
    duplicate = find_duplicate_transaction(
        session,
        test_account.id,
        date(2024, 1, 15),
        -5.50,
        "STARBUCKS COFFEE #123",
        import_log_2.id  # Different import
    )

    assert duplicate is not None
    assert duplicate.id == original.id


def test_same_import_not_duplicate(session, test_account, import_log_1):
    """Test that identical transactions in SAME import are NOT marked as duplicates."""
    # Create original transaction from import 1
    original = Transaction(
        account_id=test_account.id,
        date=date(2024, 1, 15),
        description="STARBUCKS COFFEE #123",
        amount=-5.50,
        source_file="statement1.pdf",
        import_log_id=import_log_1.id
    )
    session.add(original)
    session.commit()

    # Try to find duplicate from SAME import (should NOT find it)
    duplicate = find_duplicate_transaction(
        session,
        test_account.id,
        date(2024, 1, 15),
        -5.50,
        "STARBUCKS COFFEE #123",
        import_log_1.id  # Same import
    )

    assert duplicate is None  # Should not find duplicate from same import


def test_fuzzy_date_matching(session, test_account, import_log_1, import_log_2):
    """Test duplicate detection with date tolerance."""
    # Create original transaction
    original = Transaction(
        account_id=test_account.id,
        date=date(2024, 1, 15),
        description="GROCERY STORE",
        amount=-100.00,
        source_file="statement1.pdf",
        import_log_id=import_log_1.id
    )
    session.add(original)
    session.commit()

    # Try to find with date 1 day off (should match)
    duplicate = find_duplicate_transaction(
        session,
        test_account.id,
        date(2024, 1, 16),
        -100.00,
        "GROCERY STORE",
        import_log_2.id
    )

    assert duplicate is not None
    assert duplicate.id == original.id


def test_fuzzy_amount_matching(session, test_account, import_log_1, import_log_2):
    """Test duplicate detection with amount tolerance."""
    # Create original transaction
    original = Transaction(
        account_id=test_account.id,
        date=date(2024, 1, 15),
        description="RESTAURANT",
        amount=-50.00,
        source_file="statement1.pdf",
        import_log_id=import_log_1.id
    )
    session.add(original)
    session.commit()

    # Try to find with slightly different amount (should match)
    duplicate = find_duplicate_transaction(
        session,
        test_account.id,
        date(2024, 1, 15),
        -50.005,  # Within $0.01
        "RESTAURANT",
        import_log_2.id
    )

    assert duplicate is not None
    assert duplicate.id == original.id


def test_description_similarity(session, test_account, import_log_1, import_log_2):
    """Test duplicate detection with similar descriptions."""
    # Create original transaction
    original = Transaction(
        account_id=test_account.id,
        date=date(2024, 1, 15),
        description="AMAZON.COM PAYMENT",
        amount=-75.00,
        source_file="statement1.pdf",
        import_log_id=import_log_1.id
    )
    session.add(original)
    session.commit()

    # Try to find with slightly different description (should match)
    duplicate = find_duplicate_transaction(
        session,
        test_account.id,
        date(2024, 1, 15),
        -75.00,
        "AMAZON.COM PAYMENT #123456",  # Contains original
        import_log_2.id
    )

    assert duplicate is not None
    assert duplicate.id == original.id


def test_no_false_positive(session, test_account, import_log_1, import_log_2):
    """Test that truly different transactions are not marked as duplicates."""
    # Create original transaction
    original = Transaction(
        account_id=test_account.id,
        date=date(2024, 1, 15),
        description="STORE A",
        amount=-50.00,
        source_file="statement1.pdf",
        import_log_id=import_log_1.id
    )
    session.add(original)
    session.commit()

    # Try to find completely different transaction (should NOT match)
    duplicate = find_duplicate_transaction(
        session,
        test_account.id,
        date(2024, 1, 15),
        -50.00,
        "STORE B",  # Different description
        import_log_2.id
    )

    assert duplicate is None


def test_different_account_no_match(session, test_account, import_log_1):
    """Test that transactions from different accounts don't match."""
    # Create another account
    other_account = Account(
        name="Other Account",
        institution="Other Bank",
        account_type="checking"
    )
    session.add(other_account)
    session.commit()

    # Create import log for other account
    other_import_log = ImportLog(
        account_id=other_account.id,
        filename="other_statement.pdf",
        file_hash="hash_other"
    )
    session.add(other_import_log)
    session.commit()

    # Create transaction in first account
    original = Transaction(
        account_id=test_account.id,
        date=date(2024, 1, 15),
        description="PAYMENT",
        amount=-100.00,
        source_file="statement1.pdf",
        import_log_id=import_log_1.id
    )
    session.add(original)
    session.commit()

    # Try to find in other account (should NOT match)
    duplicate = find_duplicate_transaction(
        session,
        other_account.id,
        date(2024, 1, 15),
        -100.00,
        "PAYMENT",
        other_import_log.id
    )

    assert duplicate is None


def test_multiple_identical_transactions_same_import(session, test_account, import_log_1):
    """Test that multiple identical transactions in the SAME import are all imported."""
    # Simulate importing two identical Starbucks transactions from same statement
    trans1 = Transaction(
        account_id=test_account.id,
        date=date(2024, 1, 15),
        description="STARBUCKS #123",
        amount=-5.50,
        source_file="statement1.pdf",
        import_log_id=import_log_1.id
    )
    session.add(trans1)
    session.commit()

    # Second identical transaction from SAME import should not be flagged as duplicate
    duplicate = find_duplicate_transaction(
        session,
        test_account.id,
        date(2024, 1, 15),
        -5.50,
        "STARBUCKS #123",
        import_log_1.id  # Same import
    )

    assert duplicate is None  # Should allow import

    # Now add the second transaction
    trans2 = Transaction(
        account_id=test_account.id,
        date=date(2024, 1, 15),
        description="STARBUCKS #123",
        amount=-5.50,
        source_file="statement1.pdf",
        import_log_id=import_log_1.id
    )
    session.add(trans2)
    session.commit()

    # Verify both exist
    all_trans = session.query(Transaction).filter(
        Transaction.account_id == test_account.id,
        Transaction.description == "STARBUCKS #123"
    ).all()

    assert len(all_trans) == 2  # Both transactions imported
