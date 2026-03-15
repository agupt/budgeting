"""PDF Import Interface with Multi-File Support."""
import streamlit as st
from pathlib import Path
import sys
import yaml
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import get_session, Account, Transaction, ImportLog
from src.parsers.bank_adapters import get_adapter
from src.utils.duplicate_detection import calculate_file_hash, check_file_already_imported, find_duplicate_transaction
from src.analyzers.payment_detector import PaymentDetector

st.set_page_config(page_title="Import Statements", page_icon="📄", layout="wide")

st.title("📄 Import Bank Statements")
st.markdown("Upload one or multiple checking/savings account PDF statements to begin analysis.")

# Initialize session state
if 'import_results' not in st.session_state:
    st.session_state.import_results = None

# Load config
config_path = Path(__file__).parent.parent / "config" / "bank_parsers.yaml"
with open(config_path, 'r') as f:
    parser_config = yaml.safe_load(f)

# Account selection/creation
st.header("1. Select or Create Account")

session = get_session()
accounts = session.query(Account).filter(Account.account_type.in_(['checking', 'savings'])).all()

col1, col2 = st.columns([2, 1])

with col1:
    if accounts:
        account_options = {f"{acc.name} ({acc.institution})": acc.id for acc in accounts}
        selected_account = st.selectbox(
            "Select existing account",
            options=list(account_options.keys()),
            key="existing_account"
        )
        selected_account_id = account_options[selected_account] if selected_account else None
    else:
        st.info("No accounts found. Create one below.")
        selected_account_id = None

with col2:
    if st.button("+ New Account"):
        st.session_state.show_new_account = True

# New account form
if st.session_state.get('show_new_account', False) or not accounts:
    with st.form("new_account_form"):
        st.subheader("Create New Account")

        new_name = st.text_input("Account Name", placeholder="e.g., Chase Checking")
        new_institution = st.text_input("Institution", placeholder="e.g., Bank of America")
        new_type = st.selectbox("Account Type", ["checking", "savings"])
        new_last4 = st.text_input("Last 4 Digits (optional)", max_chars=4)

        submitted = st.form_submit_button("Create Account")

        if submitted and new_name and new_institution:
            new_account = Account(
                name=new_name,
                institution=new_institution,
                account_type=new_type,
                account_number_last4=new_last4 if new_last4 else None
            )
            session.add(new_account)
            session.commit()
            st.success(f"✓ Created account: {new_name}")
            st.session_state.show_new_account = False
            st.rerun()

# PDF Upload - MULTI-FILE SUPPORT
st.header("2. Upload Statement PDFs")

if selected_account_id:
    uploaded_files = st.file_uploader(
        "Choose PDF statements (can select multiple)",
        type="pdf",
        accept_multiple_files=True,
        help="Upload one or more checking/savings account statement PDFs"
    )

    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} file(s) selected")

        # Option to skip already-imported files
        skip_duplicates = st.checkbox("Skip files already imported", value=True)

        # Import button
        if st.button("Import All Statements", type="primary"):
            # Initialize payment detector once
            detector = PaymentDetector()

            # Track overall results
            overall_results = {
                'files_processed': 0,
                'files_skipped': 0,
                'files_failed': 0,
                'total_transactions': 0,
                'total_imported': 0,
                'total_skipped': 0,
                'file_details': []
            }

            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Process each file
            for idx, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")

                try:
                    # Save uploaded file temporarily
                    temp_path = Path("/tmp") / uploaded_file.name
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getvalue())

                    # Check for duplicate file
                    file_hash = calculate_file_hash(str(temp_path))
                    existing_import = check_file_already_imported(session, file_hash)

                    if existing_import and skip_duplicates:
                        overall_results['files_skipped'] += 1
                        overall_results['file_details'].append({
                            'filename': uploaded_file.name,
                            'status': 'skipped',
                            'reason': f"Already imported on {existing_import.import_date.strftime('%Y-%m-%d')}",
                            'transactions': 0
                        })
                        progress_bar.progress((idx + 1) / len(uploaded_files))
                        continue

                    # Parse statement
                    adapter = get_adapter(str(temp_path), parser_config['banks'])
                    account_info, parsed_transactions = adapter.parse_statement(str(temp_path))

                    overall_results['total_transactions'] += len(parsed_transactions)

                    # Create import log
                    import_log = ImportLog(
                        account_id=selected_account_id,
                        filename=uploaded_file.name,
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
                            selected_account_id,
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
                            account_id=selected_account_id,
                            date=parsed_trans.date,
                            description=parsed_trans.description,
                            amount=parsed_trans.amount,
                            balance=parsed_trans.balance,
                            source_file=uploaded_file.name,
                            import_log_id=import_log.id,
                            payment_destination_id=payment_dest.id if payment_dest else None
                        )
                        session.add(transaction)
                        imported += 1

                    # Update import log
                    import_log.transactions_count = imported
                    import_log.status = 'success'

                    session.commit()

                    overall_results['files_processed'] += 1
                    overall_results['total_imported'] += imported
                    overall_results['total_skipped'] += skipped
                    overall_results['file_details'].append({
                        'filename': uploaded_file.name,
                        'status': 'success',
                        'imported': imported,
                        'skipped': skipped,
                        'total': len(parsed_transactions),
                        'period': f"{account_info.get('statement_start')} to {account_info.get('statement_end')}"
                    })

                except Exception as e:
                    overall_results['files_failed'] += 1
                    overall_results['file_details'].append({
                        'filename': uploaded_file.name,
                        'status': 'failed',
                        'error': str(e)
                    })
                    session.rollback()

                progress_bar.progress((idx + 1) / len(uploaded_files))

            # Complete
            progress_bar.progress(1.0)
            status_text.text("✓ Import complete!")

            # Store results in session state
            st.session_state.import_results = overall_results

            # Display summary
            st.markdown("---")
            st.header("📊 Import Summary")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Files Processed", overall_results['files_processed'])
            col2.metric("Files Skipped", overall_results['files_skipped'])
            col3.metric("Files Failed", overall_results['files_failed'])
            col4.metric("Total Files", len(uploaded_files))

            st.markdown("---")

            col1, col2, col3 = st.columns(3)
            col1.metric("Transactions Found", overall_results['total_transactions'])
            col2.metric("Imported", overall_results['total_imported'],
                       delta=f"+{overall_results['total_imported']}")
            col3.metric("Skipped (Duplicates)", overall_results['total_skipped'])

            # Detailed results per file
            st.markdown("---")
            st.subheader("📄 Detailed Results")

            for file_detail in overall_results['file_details']:
                with st.expander(f"📄 {file_detail['filename']} - {file_detail['status'].upper()}"):
                    if file_detail['status'] == 'success':
                        st.write(f"**Statement Period:** {file_detail.get('period', 'N/A')}")
                        st.write(f"**Total Transactions:** {file_detail['total']}")
                        st.write(f"**Imported:** {file_detail['imported']}")
                        st.write(f"**Skipped (Duplicates):** {file_detail['skipped']}")
                    elif file_detail['status'] == 'skipped':
                        st.info(f"⏭️ {file_detail['reason']}")
                    elif file_detail['status'] == 'failed':
                        st.error(f"❌ Error: {file_detail['error']}")

else:
    st.info("Please select or create an account first.")

# Show previous import results if available (from session state)
if st.session_state.import_results and not uploaded_files:
    st.markdown("---")
    st.header("📊 Last Import Summary")
    results = st.session_state.import_results

    col1, col2, col3 = st.columns(3)
    col1.metric("Files Processed", results.get('files_processed', results.get('total', 0)))
    col2.metric("Transactions Imported", results.get('total_imported', results.get('imported', 0)))
    col3.metric("Skipped (Duplicates)", results.get('total_skipped', results.get('skipped', 0)))

session.close()
