#!/usr/bin/env python3
"""Test parsing a single PDF to debug issues."""
import sys
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers.bank_adapters import get_adapter
import pdfplumber

def test_parse(pdf_path):
    """Test parsing a single PDF and show detailed output."""
    print("=" * 60)
    print(f"TESTING: {pdf_path}")
    print("=" * 60)

    # Load config
    config_path = Path(__file__).parent.parent / "config" / "bank_parsers.yaml"
    with open(config_path, 'r') as f:
        parser_config = yaml.safe_load(f)

    print("\n1. Extracting text from PDF...")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"   Pages: {len(pdf.pages)}")

            # Extract first page text
            if pdf.pages:
                first_page_text = pdf.pages[0].extract_text()
                print(f"\n   First page text (first 500 chars):")
                print("   " + "-" * 56)
                print(first_page_text[:500] if first_page_text else "   [NO TEXT EXTRACTED]")
                print("   " + "-" * 56)

                # Full text for detection
                full_text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
                print(f"\n   Total text length: {len(full_text)} characters")

                # Check for Bank of America markers
                if "Bank of America" in full_text or "BANK OF AMERICA" in full_text:
                    print("   ✓ Bank of America detected in text")
                else:
                    print("   ✗ Bank of America NOT detected in text")

    except Exception as e:
        print(f"   ✗ Error extracting text: {e}")
        return

    print("\n2. Getting adapter...")
    try:
        adapter = get_adapter(pdf_path, parser_config['banks'])
        print(f"   ✓ Adapter: {adapter.__class__.__name__}")
    except Exception as e:
        print(f"   ✗ Error getting adapter: {e}")
        return

    print("\n3. Extracting account info...")
    try:
        account_info = adapter.extract_account_info(full_text)
        print(f"   Account Last 4: {account_info.get('account_number_last4', 'N/A')}")
        print(f"   Statement Start: {account_info.get('statement_start', 'N/A')}")
        print(f"   Statement End: {account_info.get('statement_end', 'N/A')}")
    except Exception as e:
        print(f"   ✗ Error extracting account info: {e}")
        import traceback
        traceback.print_exc()

    print("\n4. Parsing transactions...")
    try:
        transactions = adapter.parse_transactions(full_text)
        print(f"   ✓ Parsed {len(transactions)} transactions")

        if transactions:
            print("\n   First 5 transactions:")
            for i, trans in enumerate(transactions[:5], 1):
                print(f"   {i}. {trans.date} | {trans.description[:40]} | ${trans.amount}")
        else:
            print("   ✗ No transactions parsed!")
            print("\n   Searching for transaction patterns in text...")

            # Check for common patterns
            import re

            # Look for dates
            date_pattern = r'\d{1,2}/\d{1,2}/\d{4}'
            dates = re.findall(date_pattern, full_text)
            print(f"   Found {len(dates)} date patterns (MM/DD/YYYY)")
            if dates:
                print(f"   Examples: {dates[:3]}")

            # Look for amounts
            amount_pattern = r'\$[\d,]+\.\d{2}'
            amounts = re.findall(amount_pattern, full_text)
            print(f"   Found {len(amounts)} amount patterns ($X.XX)")
            if amounts:
                print(f"   Examples: {amounts[:3]}")

            # Look for transaction section markers
            if re.search(r'Deposits and other additions', full_text, re.IGNORECASE):
                print("   ✓ Found 'Deposits and other additions' section")
            else:
                print("   ✗ 'Deposits and other additions' section not found")

            if re.search(r'Withdrawals and other subtractions', full_text, re.IGNORECASE):
                print("   ✓ Found 'Withdrawals and other subtractions' section")
            else:
                print("   ✗ 'Withdrawals and other subtractions' section not found")

    except Exception as e:
        print(f"   ✗ Error parsing transactions: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_parse_single.py <path_to_pdf>")
        print("\nExample:")
        print("  python scripts/test_parse_single.py statements/BankOfAmerica-Statement/statement1.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not Path(pdf_path).exists():
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)

    test_parse(pdf_path)
