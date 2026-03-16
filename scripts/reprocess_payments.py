#!/usr/bin/env python3
"""Reprocess payment detection for existing transactions without re-importing.

Usage:
    python scripts/reprocess_payments.py                    # All accounts
    python scripts/reprocess_payments.py --account-id 1     # Specific account
"""
import sys
from pathlib import Path
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import get_session, Account, Transaction, PaymentDestination
from src.analyzers.payment_detector import PaymentDetector


def reprocess_payments(account_id=None):
    """
    Reprocess payment detection for existing transactions.

    Args:
        account_id: Optional account ID to filter (None = all accounts)
    """
    session = get_session()
    detector = PaymentDetector()

    # Build query
    query = session.query(Transaction)
    if account_id:
        query = query.filter(Transaction.account_id == account_id)

    transactions = query.all()

    if not transactions:
        print("No transactions found to process.")
        return

    print("=" * 60)
    print("REPROCESSING PAYMENT DETECTION")
    print("=" * 60)
    print()

    if account_id:
        account = session.query(Account).filter(Account.id == account_id).first()
        print(f"Account: {account.name} ({account.institution})")
    else:
        print("Processing: All accounts")

    print(f"Total transactions: {len(transactions)}")
    print()

    # Track statistics
    stats = {
        'already_detected': 0,
        'newly_detected': 0,
        'changed': 0,
        'still_undetected': 0
    }

    destination_changes = []

    # Process each transaction
    for idx, transaction in enumerate(transactions, 1):
        if idx % 100 == 0:
            print(f"  Processing {idx}/{len(transactions)}...", end='\r')

        old_dest_id = transaction.payment_destination_id
        old_dest_name = None
        if old_dest_id:
            old_dest = session.query(PaymentDestination).filter(
                PaymentDestination.id == old_dest_id
            ).first()
            old_dest_name = old_dest.name if old_dest else None

        # Detect with current patterns
        new_dest = detector.get_or_create_destination(session, transaction.description)

        if old_dest_id and new_dest and old_dest_id != new_dest.id:
            # Changed to different destination
            transaction.payment_destination_id = new_dest.id
            stats['changed'] += 1
            destination_changes.append({
                'date': transaction.date,
                'description': transaction.description[:60],
                'old': old_dest_name,
                'new': new_dest.name
            })
        elif old_dest_id and new_dest and old_dest_id == new_dest.id:
            # Already correct
            stats['already_detected'] += 1
        elif not old_dest_id and new_dest:
            # Newly detected
            transaction.payment_destination_id = new_dest.id
            stats['newly_detected'] += 1
        elif old_dest_id and not new_dest:
            # Was detected before, but pattern no longer matches (pattern removed?)
            # Keep the old destination
            stats['already_detected'] += 1
        else:
            # Still no detection
            stats['still_undetected'] += 1

    # Commit changes
    session.commit()

    print()
    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print()
    print(f"✓ Already correct:        {stats['already_detected']:,}")
    print(f"✓ Newly detected:         {stats['newly_detected']:,}")
    print(f"✓ Changed destination:    {stats['changed']:,}")
    print(f"⚠ Still undetected:       {stats['still_undetected']:,}")
    print()

    detection_rate = ((stats['already_detected'] + stats['newly_detected'] + stats['changed']) /
                      len(transactions) * 100)
    print(f"Detection rate: {detection_rate:.1f}%")
    print()

    # Show changed destinations
    if destination_changes:
        print("=" * 60)
        print("DESTINATION CHANGES")
        print("=" * 60)
        print()
        for change in destination_changes[:10]:  # Show first 10
            print(f"{change['date']} | {change['description']}")
            print(f"  {change['old']} → {change['new']}")
            print()

        if len(destination_changes) > 10:
            print(f"... and {len(destination_changes) - 10} more changes")
            print()

    # Show undetected samples
    if stats['still_undetected'] > 0:
        print("=" * 60)
        print("SAMPLE UNDETECTED TRANSACTIONS")
        print("=" * 60)
        print()

        undetected = [t for t in transactions if not t.payment_destination_id]
        for trans in undetected[:5]:
            print(f"{trans.date} | ${trans.amount:,.2f} | {trans.description[:70]}")

        print()
        print("💡 Consider adding patterns for these transaction types")
        print()

    session.close()


def main():
    parser = argparse.ArgumentParser(
        description="Reprocess payment detection for existing transactions"
    )
    parser.add_argument(
        "--account-id",
        type=int,
        help="Process only specific account (default: all accounts)"
    )

    args = parser.parse_args()
    reprocess_payments(args.account_id)


if __name__ == "__main__":
    main()
