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
        """Parse transactions from TechCU statement (legacy method - returns flat list)."""
        # Use new multi-account parser and flatten results for backward compatibility
        accounts_data = self.parse_multi_account_statement(text)

        all_transactions = []
        for account_data in accounts_data:
            all_transactions.extend(account_data['transactions'])

        return all_transactions

    def parse_multi_account_statement(self, text: str) -> List[Dict]:
        """
        Parse TechCU statement with multiple account sections (checking + savings).

        Returns:
            List of account data dicts, each containing:
            - account_type: 'checking' or 'savings'
            - account_name: e.g., 'PRIMARY CHECKING'
            - starting_balance: float
            - ending_balance: float
            - transactions: List[ParsedTransaction]
            - summary: dict with deposits_count, deposits_total, withdrawals_count, withdrawals_total
        """
        accounts_data = []
        lines = text.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Detect account section header (e.g., "PRIMARY CHECKING", "PRIMARY SAVINGS")
            account_type_match = re.search(r'(PRIMARY\s+)?(CHECKING|SAVINGS)$', line, re.IGNORECASE)
            if account_type_match:
                account_name = line.strip()
                account_type = account_type_match.group(2).lower()

                # Look for starting balance
                i += 1
                starting_balance = None
                while i < len(lines):
                    line = lines[i].strip()
                    start_match = re.search(r'(\d{1,2}/\d{1,2})\s+Starting Balance\s+\$?([\d,]+\.\d{2})', line, re.IGNORECASE)
                    if start_match:
                        starting_balance = float(start_match.group(2).replace(',', ''))
                        i += 1
                        break
                    i += 1

                # Parse transactions until ending balance
                transactions = []
                ending_balance = None
                year_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', text)
                current_year = int(year_match.group(3)) if year_match else datetime.now().year

                # Skip header line ("Date Transaction Description Amount Balance")
                while i < len(lines):
                    line = lines[i].strip()
                    if re.match(r'^Date\s+Transaction', line, re.IGNORECASE):
                        i += 1
                        break
                    i += 1

                # Transaction pattern: MM/DD Description Amount Balance
                transaction_pattern = re.compile(
                    r'^(\d{1,2}/\d{1,2})\s+(.+?)\s+(-?\$?[\d,]+\.\d{2})(?:\s+\$?([\d,]+\.\d{2}))?$'
                )

                while i < len(lines):
                    line = lines[i].strip()

                    # Check for ending balance (can be split across two lines)
                    # Line 1: "2/28 Ending Balance for PRIMARY CHECKING"
                    # Line 2: "$2,397.11"
                    if re.search(r'(\d{1,2}/\d{1,2})\s+Ending Balance', line, re.IGNORECASE):
                        # Check if amount is on the same line
                        amount_match = re.search(r'\$?([\d,]+\.\d{2})', line)
                        if amount_match:
                            ending_balance = float(amount_match.group(1).replace(',', ''))
                        else:
                            # Amount is on the next line
                            i += 1
                            if i < len(lines):
                                next_line = lines[i].strip()
                                amount_match = re.search(r'^\$?([\d,]+\.\d{2})$', next_line)
                                if amount_match:
                                    ending_balance = float(amount_match.group(1).replace(',', ''))
                        i += 1
                        break

                    # Check if we've reached the summary (end of account section)
                    if re.search(r'^Summary:', line, re.IGNORECASE):
                        break

                    # Try to match transaction
                    trans_match = transaction_pattern.match(line)
                    if trans_match:
                        date_str, description, amount_str, balance_str = trans_match.groups()

                        try:
                            # Parse date
                            trans_date = datetime.strptime(f"{date_str}/{current_year}", "%m/%d/%Y").date()

                            # Parse amount
                            amount = float(amount_str.replace('$', '').replace(',', ''))

                            # Parse balance if present
                            balance = None
                            if balance_str:
                                balance = float(balance_str.replace(',', ''))

                            transactions.append(ParsedTransaction(
                                date=trans_date,
                                description=description.strip(),
                                amount=amount,
                                balance=balance
                            ))
                        except (ValueError, AttributeError):
                            pass

                    i += 1

                # Parse summary line
                summary = {
                    'deposits_count': 0,
                    'deposits_total': 0.0,
                    'withdrawals_count': 0,
                    'withdrawals_total': 0.0
                }

                # Look for summary within next few lines
                for j in range(i, min(i + 10, len(lines))):
                    summary_line = lines[j].strip()
                    # Pattern: "Summary: 1 Deposit : $2,500.00 4 Withdrawals : $-1,337.45"
                    # Or: "Summary: 3 Deposits : $1,025.81 YTD Dividends Paid : $25.81"
                    if re.search(r'^Summary:', summary_line, re.IGNORECASE):
                        # Extract deposits
                        deposits_match = re.search(r'(\d+)\s+Deposits?\s*:\s*\$?([\d,]+\.\d{2})', summary_line, re.IGNORECASE)
                        if deposits_match:
                            summary['deposits_count'] = int(deposits_match.group(1))
                            summary['deposits_total'] = float(deposits_match.group(2).replace(',', ''))

                        # Extract withdrawals
                        withdrawals_match = re.search(r'(\d+)\s+Withdrawals?\s*:\s*\$?(-?[\d,]+\.\d{2})', summary_line, re.IGNORECASE)
                        if withdrawals_match:
                            summary['withdrawals_count'] = int(withdrawals_match.group(1))
                            summary['withdrawals_total'] = float(withdrawals_match.group(2).replace(',', ''))

                        i = j + 1
                        break

                # Add account data
                accounts_data.append({
                    'account_type': account_type,
                    'account_name': account_name,
                    'starting_balance': starting_balance,
                    'ending_balance': ending_balance,
                    'transactions': transactions,
                    'summary': summary
                })

                continue

            i += 1

        return accounts_data


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
