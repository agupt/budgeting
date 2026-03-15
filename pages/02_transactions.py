"""View and search transactions."""
import streamlit as st
from pathlib import Path
import sys
import pandas as pd
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import get_session, Account, Transaction, PaymentDestination

st.set_page_config(page_title="Transactions", page_icon="📋", layout="wide")

st.title("📋 Transactions")

session = get_session()

# Filters
st.sidebar.header("Filters")

# Account filter
accounts = session.query(Account).all()
account_options = ["All Accounts"] + [f"{acc.name} ({acc.institution})" for acc in accounts]
selected_account = st.sidebar.selectbox("Account", account_options)

# Date range filter
date_col1, date_col2 = st.sidebar.columns(2)
with date_col1:
    start_date = st.date_input("From", value=datetime.now() - timedelta(days=90))
with date_col2:
    end_date = st.date_input("To", value=datetime.now())

# Amount range filter
st.sidebar.subheader("Amount Range")
amount_col1, amount_col2 = st.sidebar.columns(2)
with amount_col1:
    min_amount = st.number_input("Min $", value=-10000.0, step=100.0)
with amount_col2:
    max_amount = st.number_input("Max $", value=10000.0, step=100.0)

# Search
search_query = st.sidebar.text_input("Search Description", "")

# Payment destination filter
destinations = session.query(PaymentDestination).all()
dest_options = ["All"] + [dest.name for dest in destinations]
selected_dest = st.sidebar.selectbox("Payment Destination", dest_options)

# Build query
query = session.query(Transaction)

if selected_account != "All Accounts":
    account_name = selected_account.split(" (")[0]
    account = session.query(Account).filter(Account.name == account_name).first()
    if account:
        query = query.filter(Transaction.account_id == account.id)

query = query.filter(Transaction.date >= start_date, Transaction.date <= end_date)
query = query.filter(Transaction.amount >= min_amount, Transaction.amount <= max_amount)

if search_query:
    query = query.filter(Transaction.description.contains(search_query))

if selected_dest != "All":
    dest = session.query(PaymentDestination).filter(PaymentDestination.name == selected_dest).first()
    if dest:
        query = query.filter(Transaction.payment_destination_id == dest.id)

# Get transactions
transactions = query.order_by(Transaction.date.desc()).all()

# Display summary
st.header("Summary")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Transactions", len(transactions))

with col2:
    total_income = sum(t.amount for t in transactions if t.amount > 0)
    st.metric("Total Income", f"${total_income:,.2f}")

with col3:
    total_expenses = sum(t.amount for t in transactions if t.amount < 0)
    st.metric("Total Expenses", f"${abs(total_expenses):,.2f}")

with col4:
    net = total_income + total_expenses
    st.metric("Net", f"${net:,.2f}", delta=f"${net:,.2f}")

# Display transactions table
st.header("Transactions")

if transactions:
    # Convert to DataFrame
    data = []
    for t in transactions:
        data.append({
            'Date': t.date,
            'Account': t.account.name,
            'Description': t.description,
            'Amount': t.amount,
            'Payment Destination': t.payment_destination.name if t.payment_destination else 'N/A',
            'Balance': t.balance if t.balance else 'N/A'
        })

    df = pd.DataFrame(data)

    # Color code amounts
    def color_amount(val):
        if isinstance(val, (int, float)):
            color = 'green' if val > 0 else 'red' if val < 0 else 'black'
            return f'color: {color}'
        return ''

    styled_df = df.style.applymap(color_amount, subset=['Amount'])

    st.dataframe(styled_df, use_container_width=True, height=600)

    # Export button
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"transactions_{start_date}_{end_date}.csv",
        mime="text/csv"
    )
else:
    st.info("No transactions found. Try adjusting your filters or import statements first.")

session.close()
