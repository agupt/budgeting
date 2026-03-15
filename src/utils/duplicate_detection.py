"""Transaction duplicate detection utilities."""
import hashlib
from datetime import timedelta
from typing import Optional
from sqlalchemy.orm import Session
from src.database.models import Transaction, ImportLog


def calculate_file_hash(file_path: str) -> str:
    """
    Calculate SHA256 hash of a file.

    Args:
        file_path: Path to file

    Returns:
        Hex string of file hash
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def check_file_already_imported(session: Session, file_hash: str) -> Optional[ImportLog]:
    """
    Check if a file has already been imported.

    Args:
        session: Database session
        file_hash: SHA256 hash of file

    Returns:
        ImportLog if file was previously imported, None otherwise
    """
    return session.query(ImportLog).filter(ImportLog.file_hash == file_hash).first()


def find_duplicate_transaction(
    session: Session,
    account_id: int,
    date,
    amount: float,
    description: str,
    current_import_log_id: int,
    date_tolerance_days: int = 2,
    amount_tolerance: float = 0.01
) -> Optional[Transaction]:
    """
    Find potential duplicate transaction using fuzzy matching.

    IMPORTANT: Only checks for duplicates from OTHER import sessions (different import_log_id).
    Multiple identical transactions within the SAME import are allowed.

    Args:
        session: Database session
        account_id: Account ID
        date: Transaction date
        amount: Transaction amount
        description: Transaction description
        current_import_log_id: ImportLog ID for current import (to exclude transactions from same import)
        date_tolerance_days: Allow date difference up to N days
        amount_tolerance: Allow amount difference up to $N

    Returns:
        Existing Transaction if duplicate found, None otherwise
    """
    # Query transactions in date range
    date_start = date - timedelta(days=date_tolerance_days)
    date_end = date + timedelta(days=date_tolerance_days)

    amount_min = amount - amount_tolerance
    amount_max = amount + amount_tolerance

    # CRITICAL FIX: Exclude transactions from the same import session
    # This allows multiple identical transactions within one statement/import
    # Even if the same statement is re-imported with a different filename,
    # it will be caught as a duplicate (by import session, not filename)
    candidates = session.query(Transaction).filter(
        Transaction.account_id == account_id,
        Transaction.date >= date_start,
        Transaction.date <= date_end,
        Transaction.amount >= amount_min,
        Transaction.amount <= amount_max,
        Transaction.import_log_id != current_import_log_id  # Only check OTHER imports
    ).all()

    # Check description similarity
    for candidate in candidates:
        if _descriptions_similar(candidate.description, description):
            return candidate

    return None


def _descriptions_similar(desc1: str, desc2: str, threshold: float = 0.8) -> bool:
    """
    Check if two transaction descriptions are similar enough to be duplicates.

    Args:
        desc1: First description
        desc2: Second description
        threshold: Similarity threshold (0-1)

    Returns:
        True if descriptions are similar
    """
    # Simple approach: normalize and check for substring match
    # For production, consider using fuzzy string matching (e.g., difflib, fuzzywuzzy)
    desc1_norm = desc1.lower().strip()
    desc2_norm = desc2.lower().strip()

    # Exact match
    if desc1_norm == desc2_norm:
        return True

    # Substring match (one contains the other with significant overlap)
    if len(desc1_norm) > 10 and len(desc2_norm) > 10:
        if desc1_norm in desc2_norm or desc2_norm in desc1_norm:
            return True

    # Basic token overlap check
    tokens1 = set(desc1_norm.split())
    tokens2 = set(desc2_norm.split())

    if len(tokens1) > 0 and len(tokens2) > 0:
        overlap = len(tokens1 & tokens2) / max(len(tokens1), len(tokens2))
        return overlap >= threshold

    return False
