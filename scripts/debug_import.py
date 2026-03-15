#!/usr/bin/env python3
"""Debug import issues - check what happened."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import get_session, ImportLog, Transaction, Account

session = get_session()

print("=" * 60)
print("IMPORT LOGS SUMMARY")
print("=" * 60)

# Get all import logs
import_logs = session.query(ImportLog).order_by(ImportLog.import_date.desc()).all()

print(f"\nTotal import logs: {len(import_logs)}")
print()

for log in import_logs:
    account = session.query(Account).filter(Account.id == log.account_id).first()
    print(f"File: {log.filename}")
    print(f"  Account: {account.name if account else 'Unknown'}")
    print(f"  Date: {log.import_date}")
    print(f"  Status: {log.status}")
    print(f"  Transactions: {log.transactions_count}")
    print(f"  Statement Period: {log.statement_start_date} to {log.statement_end_date}")
    if log.error_message:
        print(f"  Error: {log.error_message}")
    print()

print("=" * 60)
print("TRANSACTION COUNT BY ACCOUNT")
print("=" * 60)

accounts = session.query(Account).all()
for account in accounts:
    trans_count = session.query(Transaction).filter(Transaction.account_id == account.id).count()
    print(f"{account.name} ({account.institution}): {trans_count} transactions")

session.close()
