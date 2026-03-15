"""Base adapter for bank statement parsing."""
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional
from datetime import date


class ParsedTransaction:
    """Structured transaction data."""
    def __init__(
        self,
        date: date,
        description: str,
        amount: float,
        balance: Optional[float] = None
    ):
        self.date = date
        self.description = description
        self.amount = amount
        self.balance = balance

    def to_dict(self) -> Dict:
        return {
            'date': self.date,
            'description': self.description,
            'amount': self.amount,
            'balance': self.balance
        }


class BaseBankAdapter(ABC):
    """Abstract base class for bank-specific PDF parsers."""

    def __init__(self, config: Dict):
        """Initialize with bank-specific configuration."""
        self.config = config

    @abstractmethod
    def detect_statement_type(self, text: str) -> bool:
        """
        Detect if this PDF is from this bank.

        Args:
            text: Full text extracted from PDF

        Returns:
            True if this adapter can parse this statement
        """
        pass

    @abstractmethod
    def extract_account_info(self, text: str) -> Dict:
        """
        Extract account metadata from statement.

        Args:
            text: Full text extracted from PDF

        Returns:
            Dict with keys: account_number_last4, statement_start, statement_end
        """
        pass

    @abstractmethod
    def parse_transactions(self, text: str) -> List[ParsedTransaction]:
        """
        Parse transactions from statement text.

        Args:
            text: Full text extracted from PDF

        Returns:
            List of ParsedTransaction objects
        """
        pass

    def parse_statement(self, pdf_path: str) -> Tuple[Dict, List[ParsedTransaction]]:
        """
        Full parsing pipeline for a statement PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Tuple of (account_info, transactions)
        """
        import pdfplumber

        # Extract text from PDF
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

        # Verify this is the right bank
        if not self.detect_statement_type(text):
            raise ValueError(f"PDF does not match {self.__class__.__name__} format")

        # Extract metadata and transactions
        account_info = self.extract_account_info(text)
        transactions = self.parse_transactions(text)

        return account_info, transactions
