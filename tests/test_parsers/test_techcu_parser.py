"""Tests for Technology Credit Union multi-account parser."""
import pytest
from datetime import date
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.parsers.bank_adapters import TechCUAdapter


# Sample TechCU statement text with BOTH checking and savings
SAMPLE_TECHCU_STATEMENT = """
Technology Credit Union
Statement Period: 02/01/2024 - 02/28/2024

PRIMARY CHECKING

02/01 Starting Balance $1,234.56

Date Transaction Description Amount Balance
02/05 Direct Deposit - COMPANY INC $2,500.00 $3,734.56
02/06 ACH Debit - APPLE CARD GSBANK -$150.00 $3,584.56
02/10 Debit Card Purchase - SAFEWAY #123 -$87.45 $3,497.11
02/15 Online Transfer to Savings -$1,000.00 $2,497.11
02/20 ATM Withdrawal - #12345 -$100.00 $2,397.11

2/28 Ending Balance for PRIMARY CHECKING
$2,397.11

Summary: 1 Deposit : $2,500.00 4 Withdrawals : $-1,337.45


PRIMARY SAVINGS

02/01 Starting Balance $25,000.00

Date Transaction Description Amount Balance
02/03 Interest Credit $12.50 $25,012.50
02/15 Online Transfer from Checking $1,000.00 $26,012.50
02/28 Interest Credit $13.31 $26,025.81

2/28 Ending Balance for PRIMARY SAVINGS
$26,025.81

Summary: 3 Deposits : $1,025.81 YTD Dividends Paid : $25.81
"""


def test_detect_techcu_statement():
    """Test TechCU statement detection."""
    adapter = TechCUAdapter({})
    assert adapter.detect_statement_type(SAMPLE_TECHCU_STATEMENT)


def test_extract_account_info():
    """Test extraction of statement period."""
    adapter = TechCUAdapter({})
    info = adapter.extract_account_info(SAMPLE_TECHCU_STATEMENT)

    assert info['statement_start'] == date(2024, 2, 1)
    assert info['statement_end'] == date(2024, 2, 28)


def test_parse_multi_account_statement():
    """
    Test parsing statement with BOTH checking and savings accounts.

    Acceptance Criteria:
    - Should detect 2 account sections (checking + savings)
    - Should return transactions grouped by account type
    - Transaction counts should match summary
    - Deposit/withdrawal totals should match summary
    """
    adapter = TechCUAdapter({})

    # Parse with account separation
    accounts_data = adapter.parse_multi_account_statement(SAMPLE_TECHCU_STATEMENT)

    assert len(accounts_data) == 2  # Checking + Savings

    # Verify checking account
    checking = next(a for a in accounts_data if a['account_type'] == 'checking')
    assert checking['account_name'] == 'PRIMARY CHECKING'
    assert len(checking['transactions']) == 5
    assert checking['starting_balance'] == 1234.56
    assert checking['ending_balance'] == 2397.11

    # Verify summary matches
    assert checking['summary']['deposits_count'] == 1
    assert checking['summary']['deposits_total'] == 2500.00
    assert checking['summary']['withdrawals_count'] == 4
    assert abs(checking['summary']['withdrawals_total']) == 1337.45

    # Verify savings account
    savings = next(a for a in accounts_data if a['account_type'] == 'savings')
    assert savings['account_name'] == 'PRIMARY SAVINGS'
    assert len(savings['transactions']) == 3
    assert savings['starting_balance'] == 25000.00
    assert savings['ending_balance'] == 26025.81

    # Verify summary matches
    assert savings['summary']['deposits_count'] == 3
    assert savings['summary']['deposits_total'] == 1025.81


def test_transaction_amounts_match_summary():
    """Verify parsed transaction amounts match the summary line."""
    adapter = TechCUAdapter({})
    accounts_data = adapter.parse_multi_account_statement(SAMPLE_TECHCU_STATEMENT)

    for account in accounts_data:
        transactions = account['transactions']
        summary = account['summary']

        # Calculate from transactions
        deposits = [t for t in transactions if t.amount > 0]
        withdrawals = [t for t in transactions if t.amount < 0]

        deposits_total = sum(t.amount for t in deposits)
        withdrawals_total = sum(t.amount for t in withdrawals)

        # Compare with summary
        assert len(deposits) == summary['deposits_count'], \
            f"{account['account_name']}: Deposit count mismatch"
        assert abs(deposits_total - summary['deposits_total']) < 0.01, \
            f"{account['account_name']}: Deposit total mismatch"

        if summary['withdrawals_count'] > 0:
            assert len(withdrawals) == summary['withdrawals_count'], \
                f"{account['account_name']}: Withdrawal count mismatch"
            assert abs(abs(withdrawals_total) - abs(summary['withdrawals_total'])) < 0.01, \
                f"{account['account_name']}: Withdrawal total mismatch"


def test_parse_transactions_legacy():
    """Test backward compatibility with old parse_transactions method."""
    adapter = TechCUAdapter({})

    # Old method should still work for single-account statements
    # (returns flat list of transactions from all accounts)
    transactions = adapter.parse_transactions(SAMPLE_TECHCU_STATEMENT)

    # Should get all transactions from both accounts
    assert len(transactions) == 8  # 5 checking + 3 savings


def test_account_name_extraction():
    """Test extraction of account names from section headers."""
    adapter = TechCUAdapter({})
    accounts_data = adapter.parse_multi_account_statement(SAMPLE_TECHCU_STATEMENT)

    account_names = [a['account_name'] for a in accounts_data]
    assert 'PRIMARY CHECKING' in account_names
    assert 'PRIMARY SAVINGS' in account_names
