"""SQLAlchemy database models for Phase 1."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Account(Base):
    """Bank accounts (checking/savings)."""
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)  # e.g., "Chase Checking"
    account_type = Column(String(50), nullable=False)  # 'checking', 'savings', 'credit_card'
    institution = Column(String(255), nullable=False)  # e.g., "Bank of America"
    account_number_last4 = Column(String(4), nullable=True)  # Last 4 digits for identification
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    transactions = relationship("Transaction", back_populates="account")

    def __repr__(self):
        return f"<Account(name='{self.name}', type='{self.account_type}')>"


class PaymentDestination(Base):
    """Payment destinations (credit cards, bills, transfers)."""
    __tablename__ = 'payment_destinations'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)  # e.g., "Chase Credit Card"
    destination_type = Column(String(50), nullable=False)  # 'credit_card', 'bill', 'transfer', 'other'
    institution = Column(String(255), nullable=True)  # e.g., "Chase"
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    transactions = relationship("Transaction", back_populates="payment_destination")

    def __repr__(self):
        return f"<PaymentDestination(name='{self.name}', type='{self.destination_type}')>"


class Transaction(Base):
    """Financial transactions from bank statements."""
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    date = Column(Date, nullable=False)
    description = Column(Text, nullable=False)
    amount = Column(Float, nullable=False)  # Negative for expenses, positive for income
    balance = Column(Float, nullable=True)  # Account balance after transaction (if available)

    # Phase 1: Payment destination tracking
    payment_destination_id = Column(Integer, ForeignKey('payment_destinations.id'), nullable=True)

    # Import tracking
    source_file = Column(String(500), nullable=True)  # Original PDF filename
    import_log_id = Column(Integer, ForeignKey('import_logs.id'), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    account = relationship("Account", back_populates="transactions")
    payment_destination = relationship("PaymentDestination", back_populates="transactions")
    import_log = relationship("ImportLog", back_populates="transactions")

    # Indexes for common queries
    __table_args__ = (
        Index('idx_account_date', 'account_id', 'date'),
        Index('idx_payment_destination', 'payment_destination_id'),
    )

    def __repr__(self):
        return f"<Transaction(date='{self.date}', amount={self.amount}, desc='{self.description[:30]}...')>"


class ImportLog(Base):
    """Track PDF imports to prevent duplicates."""
    __tablename__ = 'import_logs'

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    filename = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False, unique=True)  # SHA256 hash of file
    import_date = Column(DateTime, default=datetime.utcnow)
    transactions_count = Column(Integer, default=0)
    statement_start_date = Column(Date, nullable=True)
    statement_end_date = Column(Date, nullable=True)
    status = Column(String(50), default='success')  # 'success', 'partial', 'failed'
    error_message = Column(Text, nullable=True)

    # Relationships
    transactions = relationship("Transaction", back_populates="import_log")

    def __repr__(self):
        return f"<ImportLog(filename='{self.filename}', status='{self.status}')>"
