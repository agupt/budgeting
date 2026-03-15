"""Import suggestions - what to import next."""
import streamlit as st
from pathlib import Path
import sys
from collections import defaultdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import get_session, Account, Transaction, PaymentDestination

st.set_page_config(page_title="Import Suggestions", page_icon="💡", layout="wide")

st.title("💡 Import Suggestions")
st.markdown("Based on your cash flow, here's what to import next for deeper insights.")

session = get_session()

# Get all checking/savings accounts
checking_accounts = session.query(Account).filter(
    Account.account_type.in_(['checking', 'savings'])
).all()

if not checking_accounts:
    st.warning("No checking/savings accounts found. Import statements first.")
    st.stop()

# Get payment destinations with significant spending
payment_destinations = session.query(
    PaymentDestination,
    func.count(Transaction.id).label('transaction_count'),
    func.sum(func.abs(Transaction.amount)).label('total_amount')
).join(Transaction).group_by(PaymentDestination.id).order_by(
    func.sum(func.abs(Transaction.amount)).desc()
).all()

from sqlalchemy import func

st.header("🎯 Recommended Imports")

if not payment_destinations:
    st.info("No payment destinations detected yet. Import more checking/savings statements to see suggestions.")
    st.stop()

# Categorize suggestions
credit_card_dests = []
other_dests = []

for dest, count, total in payment_destinations:
    if dest.destination_type == 'credit_card':
        credit_card_dests.append((dest, count, total))
    elif dest.destination_type in ['payment_service', 'bill']:
        other_dests.append((dest, count, total))

# Credit Card Suggestions
if credit_card_dests:
    st.subheader("💳 Credit Card Statements")
    st.markdown("Import these credit card statements to see **what you purchased** (Phase 2):")

    for dest, count, total in credit_card_dests:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.write(f"**{dest.name}**")
                if dest.institution:
                    st.caption(f"Institution: {dest.institution}")

            with col2:
                st.metric("Total Paid", f"${total:,.2f}")

            with col3:
                st.metric("Transactions", count)

            # Check if already imported
            cc_account = session.query(Account).filter(
                Account.account_type == 'credit_card',
                Account.name.contains(dest.institution) if dest.institution else False
            ).first()

            if cc_account:
                st.success(f"✓ Already imported: {cc_account.name}")
            else:
                st.info("⏳ Not yet imported - import this credit card statement to see spending categories")

            st.markdown("---")
else:
    st.info("No credit card payments detected. If you use credit cards, import more checking statements.")

# Other payment services
if other_dests:
    st.subheader("🔍 Other Payment Destinations")
    st.markdown("Consider tracking these for complete cash flow visibility:")

    for dest, count, total in other_dests[:5]:  # Top 5
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

            with col1:
                st.write(f"**{dest.name}**")

            with col2:
                st.write(f"Type: {dest.destination_type.replace('_', ' ').title()}")

            with col3:
                st.metric("Total", f"${total:,.2f}")

            with col4:
                st.metric("Count", count)

st.markdown("---")

# Import status summary
st.header("📋 Import Status")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Checking/Savings Accounts")
    for account in checking_accounts:
        trans_count = session.query(Transaction).filter(Transaction.account_id == account.id).count()
        st.write(f"✓ **{account.name}** - {trans_count} transactions")

with col2:
    st.subheader("Credit Card Accounts")
    cc_accounts = session.query(Account).filter(Account.account_type == 'credit_card').all()

    if cc_accounts:
        for account in cc_accounts:
            trans_count = session.query(Transaction).filter(Transaction.account_id == account.id).count()
            st.write(f"✓ **{account.name}** - {trans_count} transactions")
    else:
        st.write("❌ No credit card accounts imported yet")
        st.caption("Import credit card statements to see spending categories (Phase 2)")

st.markdown("---")

# Next steps
st.header("🚀 Next Steps")

st.markdown("""
1. **Import Credit Card Statements** - Focus on cards with highest spending first
2. **Categorize Spending** - Once imported, categorize transactions to see spending patterns
3. **Set Budgets** - Use spending insights to create realistic budgets
""")

session.close()
