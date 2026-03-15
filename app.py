"""Budgeting Tool - Main Streamlit Application."""
import streamlit as st
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Personal Budgeting Tool",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main content
st.title("💰 Personal Budgeting Tool")
st.markdown("---")

# Welcome section
st.header("Welcome!")
st.markdown("""
This tool helps you understand your cash flow through a **two-tier progressive disclosure approach**:
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Phase 1: Cash Flow Analysis")
    st.markdown("""
    **Where does your money go?**

    - Import checking/savings statements (PDF)
    - See payment destinations (credit cards, bills, transfers)
    - Understand your overall cash flow
    - Get suggestions for what to import next

    *Focus: High-level money movement without transaction detail*
    """)

with col2:
    st.subheader("🔍 Phase 2: Spending Detail")
    st.markdown("""
    **What did you purchase?**

    - Import credit card statements (PDF)
    - Auto-categorize spending (groceries, dining, etc.)
    - Track budgets by category
    - See month-over-month trends

    *Focus: Detailed spending breakdown for informed decisions*
    """)

st.markdown("---")

# Quick start guide
st.header("🚀 Quick Start")
st.markdown("""
1. **Import Checking/Savings Statements** - Start with your primary checking account
2. **Review Payment Destinations** - See where your money flows
3. **Import Credit Card Statements** - Drill into spending categories (optional)
4. **Set Budgets** - Get recommendations based on your spending patterns

Navigate using the sidebar to get started!
""")

# Status section
st.markdown("---")
st.header("📈 Current Status")

# Check if database exists
db_path = Path(__file__).parent / "data" / "budgeting.db"
if db_path.exists():
    st.success("✓ Database initialized")

    # Show quick stats (placeholder for now)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Accounts", "0")
    with col2:
        st.metric("Transactions", "0")
    with col3:
        st.metric("Statements Imported", "0")
    with col4:
        st.metric("Date Range", "N/A")
else:
    st.warning("⚠️ Database not initialized. Run `python scripts/setup_db.py` first.")
    st.code("python scripts/setup_db.py", language="bash")

# Footer
st.markdown("---")
st.caption("Privacy-first • Local storage only • No cloud sync")
