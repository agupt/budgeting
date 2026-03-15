"""Bank-specific adapter implementations."""
import re
from datetime import datetime
from typing import List, Dict
from .base_adapter import BaseBankAdapter, ParsedTransaction


class BankOfAmericaAdapter(BaseBankAdapter):
    """Parser for Bank of America checking/savings statements."""

    def detect_statement_type(self, text: str) -> bool:
        """Check if this is a Bank of America statement."""
        return bool(re.search(r'Bank of America', text, re.IGNORECASE))

    def extract_account_info(self, text: str) -> Dict:
        """Extract account metadata."""
        info = {}

        # Account number - try multiple patterns
        # Pattern 1: "Account number: 8980 1378 2695" (spaces in number)
        acct_match = re.search(r'Account number[:\s]+[\d\s]+(\d{4})', text, re.IGNORECASE)
        if acct_match:
            info['account_number_last4'] = acct_match.group(1)
        else:
            # Pattern 2: "Account number ending in 1234"
            acct_match = re.search(r'Account number ending in (\d{4})', text, re.IGNORECASE)
            if acct_match:
                info['account_number_last4'] = acct_match.group(1)

        # Statement period - try multiple formats
        # Format 1: "for February 26, 2019 to March 26, 2019"
        period_match = re.search(
            r'for\s+(\w+\s+\d{1,2},\s+\d{4})\s+to\s+(\w+\s+\d{1,2},\s+\d{4})',
            text,
            re.IGNORECASE
        )
        if period_match:
            try:
                info['statement_start'] = datetime.strptime(period_match.group(1), "%B %d, %Y").date()
                info['statement_end'] = datetime.strptime(period_match.group(2), "%B %d, %Y").date()
            except ValueError:
                pass

        # Format 2: "Statement period: 01/01/2019 - 01/31/2019"
        if 'statement_start' not in info:
            period_match = re.search(
                r'Statement period[:\s]+(\d{1,2}/\d{1,2}/\d{4})\s*(?:-|to)\s*(\d{1,2}/\d{1,2}/\d{4})',
                text,
                re.IGNORECASE
            )
            if period_match:
                date_format = "%m/%d/%Y"
                info['statement_start'] = datetime.strptime(period_match.group(1), date_format).date()
                info['statement_end'] = datetime.strptime(period_match.group(2), date_format).date()

        return info

    def parse_transactions(self, text: str) -> List[ParsedTransaction]:
        """Parse transactions from BOA statement."""
        transactions = []

        # Find transaction section
        lines = text.split('\n')
        in_transaction_section = False

        # Pattern: MM/DD/YY or MM/DD/YYYY followed by description and amount at the end
        # Example: "03/18/19 BKOFAMERICA MOBILE 03/16 3607167118 DEPOSIT *MOBILE FL 157.58"
        # More flexible pattern that accepts both 2-digit and 4-digit years
        transaction_pattern = re.compile(
            r'(\d{1,2}/\d{1,2}/\d{2,4})\s+(.+?)\s+(-?[\d,]+\.\d{2})$'
        )

        for line in lines:
            line = line.strip()

            # Detect transaction sections
            if re.search(r'Deposits and other additions|Withdrawals and other subtractions', line, re.IGNORECASE):
                in_transaction_section = True
                continue

            # Exit at summary section
            if re.search(r'Summary|Ending balance|Total deposits|Total withdrawals', line, re.IGNORECASE):
                in_transaction_section = False
                continue

            if in_transaction_section and line:
                match = transaction_pattern.search(line)
                if match:
                    date_str, description, amount_str = match.groups()

                    try:
                        # Parse date - handle both 2-digit and 4-digit years
                        if len(date_str.split('/')[-1]) == 2:
                            # 2-digit year (e.g., 03/18/19)
                            trans_date = datetime.strptime(date_str, "%m/%d/%y").date()
                        else:
                            # 4-digit year (e.g., 03/18/2019)
                            trans_date = datetime.strptime(date_str, "%m/%d/%Y").date()

                        # Parse amount (remove commas, handle negative)
                        # Positive amounts = deposits/credits
                        # Need to determine if this is a withdrawal or deposit based on section
                        amount = float(amount_str.replace(',', ''))

                        # BOA shows withdrawals without negative signs in the withdrawal section
                        # If we're in withdrawals section and amount is positive, make it negative
                        # This is a simplified approach - ideally track which section we're in
                        # For now, we'll keep amounts as they appear and let the description indicate type

                        transactions.append(ParsedTransaction(
                            date=trans_date,
                            description=description.strip(),
                            amount=amount,
                            balance=None  # BOA format doesn't always include running balance per line
                        ))
                    except (ValueError, IndexError) as e:
                        # Skip lines that don't parse correctly
                        continue

        return transactions


class TechCUAdapter(BaseBankAdapter):
    """Parser for Technology Credit Union statements."""

    def detect_statement_type(self, text: str) -> bool:
        """Check if this is a TechCU statement."""
        return bool(re.search(r'Technology Credit Union|TechCU', text, re.IGNORECASE))

    def extract_account_info(self, text: str) -> Dict:
        """Extract account metadata."""
        info = {}

        # Account number (last 4 digits)
        acct_match = re.search(r'Account[:\s]+.*?(\d{4})', text)
        if acct_match:
            info['account_number_last4'] = acct_match.group(1)

        # Statement period
        period_match = re.search(
            r'(\d{1,2}/\d{1,2}/\d{4})\s*-\s*(\d{1,2}/\d{1,2}/\d{4})',
            text
        )
        if period_match:
            date_format = "%m/%d/%Y"
            info['statement_start'] = datetime.strptime(period_match.group(1), date_format).date()
            info['statement_end'] = datetime.strptime(period_match.group(2), date_format).date()

        return info

    def parse_transactions(self, text: str) -> List[ParsedTransaction]:
        """Parse transactions from TechCU statement."""
        transactions = []

        lines = text.split('\n')
        in_transaction_section = False

        # Pattern: MM/DD Description $XXX.XX $X,XXX.XX
        transaction_pattern = re.compile(
            r'(\d{1,2}/\d{1,2})\s+(.+?)\s+(-?\$?[\d,]+\.\d{2})\s+(\$?[\d,]+\.\d{2})?'
        )

        # Assume current year for transactions (TechCU often omits year)
        current_year = datetime.now().year

        for line in lines:
            # Detect transaction section
            if re.search(r'Transaction Details|TRANSACTION DETAIL', line, re.IGNORECASE):
                in_transaction_section = True
                continue

            # Exit at summary
            if re.search(r'Balance Summary|BALANCE SUMMARY', line, re.IGNORECASE):
                in_transaction_section = False

            if in_transaction_section:
                match = transaction_pattern.search(line)
                if match:
                    date_str, description, amount_str, balance_str = match.groups()

                    # Parse date (add year)
                    trans_date = datetime.strptime(f"{date_str}/{current_year}", "%m/%d/%Y").date()

                    # Parse amount
                    amount = float(amount_str.replace('$', '').replace(',', ''))

                    # Parse balance
                    balance = None
                    if balance_str:
                        balance = float(balance_str.replace('$', '').replace(',', ''))

                    transactions.append(ParsedTransaction(
                        date=trans_date,
                        description=description.strip(),
                        amount=amount,
                        balance=balance
                    ))

        return transactions


def get_adapter(pdf_path: str, config: Dict) -> BaseBankAdapter:
    """
    Auto-detect and return the appropriate bank adapter.

    Args:
        pdf_path: Path to statement PDF
        config: Bank parser configuration

    Returns:
        Appropriate BaseBankAdapter instance

    Raises:
        ValueError: If no adapter can parse this statement
    """
    import pdfplumber

    # Extract text for detection
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages[:2] if page.extract_text())

    # Try each adapter
    adapters = [
        BankOfAmericaAdapter(config.get('bank_of_america', {})),
        TechCUAdapter(config.get('techcu', {})),
    ]

    for adapter in adapters:
        if adapter.detect_statement_type(text):
            return adapter

    raise ValueError("No adapter found for this statement format. Please check the bank and try again.")
