# Personal Budgeting Tool

A two-tier personal budgeting tool for users who pay credit cards in full monthly. Progressive disclosure approach reveals cash flow first, then spending detail.

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/setup_db.py
```

### 2. Run Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Features

### Phase 1: Cash Flow Analysis ✅
- **Import checking/savings statements** (PDF) with auto-parsing
- **Payment destination detection** (credit cards, bills, transfers)
- **Cash flow analytics** (income vs expenses, trends)
- **Import suggestions** (what to import next)

### Phase 2: Spending Detail (Coming Soon)
- Import credit card statements
- Auto-categorize spending
- Track budgets by category
- Month-over-month trends

## Usage

### Import Statements

**Via Web UI:**
1. Navigate to "Import Statements" page
2. Create or select an account
3. Upload PDF statement
4. Review preview and import

**Via CLI (Bulk Import):**
```bash
# Import all PDFs from a directory
python scripts/import_statements.py \
  --account-id 1 \
  --directory statements/BankOfAmerica-Statement/
```

### View Analytics

Navigate through the sidebar:
- **Transactions**: Search and filter all transactions
- **Analytics**: Charts and insights on cash flow
- **Suggestions**: Recommendations for what to import next

## Supported Banks

Currently supported:
- Bank of America
- Technology Credit Union
- Chase (basic support)

More banks can be added via `config/bank_parsers.yaml`

## Project Structure

```
budgeting/
├── app.py                    # Main Streamlit app
├── requirements.txt          # Python dependencies
├── data/
│   └── budgeting.db         # SQLite database (auto-created)
├── config/
│   ├── bank_parsers.yaml    # Bank-specific parsing rules
│   └── payment_patterns.yaml # Payment destination patterns
├── src/
│   ├── database/            # SQLAlchemy models
│   ├── parsers/             # PDF parsing, bank adapters
│   ├── analyzers/           # Payment detection
│   └── utils/               # Duplicate detection, etc.
├── pages/                   # Streamlit pages
│   ├── 01_import.py
│   ├── 02_transactions.py
│   ├── 03_analytics.py
│   └── 04_suggestions.py
└── scripts/
    ├── setup_db.py          # Database initialization
    └── import_statements.py # Bulk import CLI
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_parsers/test_duplicate_detection.py
```

## Privacy & Security

- **All data stored locally** in SQLite database
- **No cloud sync** or external connections
- **PDF-only import** - no live bank connections
- Your financial data never leaves your computer

## Development

See `CLAUDE.md` for detailed development guidelines and epic breakdown.

## License

MIT License - See LICENSE file for details
