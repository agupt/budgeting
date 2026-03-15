#!/usr/bin/env python3
"""Bulk import statements from a directory."""
import sys
from pathlib import Path
import argparse
import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import get_session, Account, Transaction, ImportLog
from src.parsers.bank_adapters import get_adapter
from src.utils.duplicate_detection import calculate_file_hash, check_file_already_imported, find_duplicate_transaction
from src.analyzers.payment_detector import PaymentDetector


def import_directory(account_id: int, directory: str, skip_duplicates: bool = True):
    """
    Import all PDF statements from a directory.

    Args:
        account_id: Database ID of account to import into
        directory: Path to directory containing PDF files
        skip_duplicates: If True, skip files already imported
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        print(f"Error: Directory not found: {directory}")
        return

    # Load config
    config_path = Path(__file__).parent.parent / "config" / "bank_parsers.yaml"
    with open(config_path, 'r') as f:
        parser_config = yaml.safe_load(f)

    session = get_session()

    # Verify account exists
    account = session.query(Account).filter(Account.id == account_id).first()
    if not account:
        print(f"Error: Account ID {account_id} not found")
        return

    print(f"Importing statements for account: {account.name} ({account.institution})")
    print(f"From directory: {directory}")
    print()

    # Find all PDFs
    pdf_files = list(dir_path.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in directory")
        return

    print(f"Found {len(pdf_files)} PDF files")
    print()

    # Initialize payment detector
    detector = PaymentDetector()

    # Process each file
    total_imported = 0
    total_skipped = 0
    files_processed = 0
    files_skipped = 0

    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file.name}")

        try:
            # Check for duplicate file
            file_hash = calculate_file_hash(str(pdf_file))
            existing_import = check_file_already_imported(session, file_hash)

            if existing_import and skip_duplicates:
                print(f"  ⏭️  Skipped (already imported on {existing_import.import_date.strftime('%Y-%m-%d')})")
                files_skipped += 1
                print()
                continue

            # Parse statement
            adapter = get_adapter(str(pdf_file), parser_config['banks'])
            account_info, parsed_transactions = adapter.parse_statement(str(pdf_file))

            print(f"  📄 Parsed {len(parsed_transactions)} transactions")

            # Create import log
            import_log = ImportLog(
                account_id=account_id,
                filename=pdf_file.name,
                file_hash=file_hash,
                statement_start_date=account_info.get('statement_start'),
                statement_end_date=account_info.get('statement_end')
            )
            session.add(import_log)
            session.flush()

            # Import transactions
            imported = 0
            skipped = 0

            for parsed_trans in parsed_transactions:
                # Check for duplicates (only against OTHER import sessions)
                duplicate = find_duplicate_transaction(
                    session,
                    account_id,
                    parsed_trans.date,
                    parsed_trans.amount,
                    parsed_trans.description,
                    import_log.id  # Exclude duplicates from same import session
                )

                if duplicate:
                    skipped += 1
                    continue

                # Detect payment destination
                payment_dest = detector.get_or_create_destination(
                    session,
                    parsed_trans.description
                )

                # Create transaction
                transaction = Transaction(
                    account_id=account_id,
                    date=parsed_trans.date,
                    description=parsed_trans.description,
                    amount=parsed_trans.amount,
                    balance=parsed_trans.balance,
                    source_file=pdf_file.name,
                    import_log_id=import_log.id,
                    payment_destination_id=payment_dest.id if payment_dest else None
                )
                session.add(transaction)
                imported += 1

            # Update import log
            import_log.transactions_count = imported
            import_log.status = 'success'

            session.commit()

            print(f"  ✓ Imported {imported} transactions")
            if skipped > 0:
                print(f"  ⏭️  Skipped {skipped} duplicate transactions")

            total_imported += imported
            total_skipped += skipped
            files_processed += 1

        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            session.rollback()

        print()

    # Summary
    print("=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)
    print(f"Files processed: {files_processed}")
    print(f"Files skipped: {files_skipped}")
    print(f"Total transactions imported: {total_imported}")
    print(f"Total transactions skipped: {total_skipped}")
    print()

    session.close()


def main():
    parser = argparse.ArgumentParser(description="Bulk import bank statement PDFs")
    parser.add_argument("--account-id", type=int, required=True, help="Database ID of account")
    parser.add_argument("--directory", required=True, help="Directory containing PDF files")
    parser.add_argument("--force", action="store_true", help="Re-import files even if already imported")

    args = parser.parse_args()

    import_directory(args.account_id, args.directory, skip_duplicates=not args.force)


if __name__ == "__main__":
    main()
