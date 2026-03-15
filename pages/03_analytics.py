"""Cash flow analytics and visualizations."""
import streamlit as st
from pathlib import Path
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sqlalchemy import func

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import get_session, Account, Transaction, PaymentDestination

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")

st.title("📊 Cash Flow Analytics")

session = get_session()

# Date range selector
st.sidebar.header("Analysis Period")
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("From", value=datetime.now() - timedelta(days=90))
with col2:
    end_date = st.date_input("To", value=datetime.now())

# Account filter
accounts = session.query(Account).filter(Account.account_type.in_(['checking', 'savings'])).all()
account_options = ["All Accounts"] + [f"{acc.name}" for acc in accounts]
selected_account_name = st.sidebar.selectbox("Account", account_options)

# Build base query
query = session.query(Transaction).filter(
    Transaction.date >= start_date,
    Transaction.date <= end_date
)

if selected_account_name != "All Accounts":
    account = session.query(Account).filter(Account.name == selected_account_name).first()
    if account:
        query = query.filter(Transaction.account_id == account.id)

transactions = query.all()

if not transactions:
    st.warning("No transactions found for the selected period. Import statements first.")
    st.stop()

# Overview metrics
st.header("Overview")
col1, col2, col3, col4 = st.columns(4)

total_income = sum(t.amount for t in transactions if t.amount > 0)
total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
net_cash_flow = total_income - total_expenses
avg_daily_spending = total_expenses / ((end_date - start_date).days + 1) if (end_date - start_date).days > 0 else 0

with col1:
    st.metric("Total Income", f"${total_income:,.2f}")
with col2:
    st.metric("Total Expenses", f"${total_expenses:,.2f}")
with col3:
    st.metric("Net Cash Flow", f"${net_cash_flow:,.2f}")
with col4:
    st.metric("Avg Daily Spending", f"${avg_daily_spending:,.2f}")

st.markdown("---")

# Income vs Expenses Over Time
st.header("Income vs Expenses Over Time")

# Aggregate by month
df = pd.DataFrame([{
    'date': t.date,
    'amount': t.amount,
    'type': 'Income' if t.amount > 0 else 'Expense'
} for t in transactions])

df['month'] = pd.to_datetime(df['date']).dt.to_period('M').astype(str)
df['abs_amount'] = df['amount'].abs()

monthly_data = df.groupby(['month', 'type'])['abs_amount'].sum().reset_index()

fig_income_expense = px.bar(
    monthly_data,
    x='month',
    y='abs_amount',
    color='type',
    barmode='group',
    labels={'abs_amount': 'Amount ($)', 'month': 'Month'},
    color_discrete_map={'Income': 'green', 'Expense': 'red'}
)
st.plotly_chart(fig_income_expense, use_container_width=True)

st.markdown("---")

# Payment Destinations Breakdown
st.header("Payment Destinations Breakdown")

# Get transactions with payment destinations
dest_transactions = [t for t in transactions if t.payment_destination_id and t.amount < 0]

if dest_transactions:
    dest_data = {}
    for t in dest_transactions:
        dest_name = t.payment_destination.name
        dest_data[dest_name] = dest_data.get(dest_name, 0) + abs(t.amount)

    dest_df = pd.DataFrame([
        {'Destination': name, 'Amount': amount}
        for name, amount in sorted(dest_data.items(), key=lambda x: x[1], reverse=True)
    ])

    # Pie chart
    col1, col2 = st.columns([2, 1])

    with col1:
        fig_pie = px.pie(
            dest_df,
            values='Amount',
            names='Destination',
            title='Expense Distribution by Payment Destination'
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.subheader("Top Destinations")
        for idx, row in dest_df.head(10).iterrows():
            pct = (row['Amount'] / total_expenses) * 100
            st.write(f"**{row['Destination']}**")
            st.write(f"${row['Amount']:,.2f} ({pct:.1f}%)")
            st.progress(pct / 100)
            st.write("")

    # Detailed table
    st.subheader("All Payment Destinations")
    dest_df['Percentage'] = (dest_df['Amount'] / total_expenses * 100).round(2)
    dest_df['Amount'] = dest_df['Amount'].apply(lambda x: f"${x:,.2f}")
    dest_df['Percentage'] = dest_df['Percentage'].apply(lambda x: f"{x}%")
    st.dataframe(dest_df, use_container_width=True)

else:
    st.info("No payment destinations detected yet. Import more statements or check payment detection patterns.")

st.markdown("---")

# Daily Balance Trend (if balance data available)
st.header("Account Balance Trend")

balance_transactions = [t for t in transactions if t.balance is not None]

if balance_transactions:
    balance_df = pd.DataFrame([
        {'Date': t.date, 'Balance': t.balance, 'Account': t.account.name}
        for t in sorted(balance_transactions, key=lambda x: x.date)
    ])

    fig_balance = px.line(
        balance_df,
        x='Date',
        y='Balance',
        color='Account',
        labels={'Balance': 'Balance ($)'},
        title='Account Balance Over Time'
    )
    st.plotly_chart(fig_balance, use_container_width=True)
else:
    st.info("No balance data available. Some statements may not include running balance information.")

session.close()
