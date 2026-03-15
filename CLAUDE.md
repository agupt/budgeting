# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A two-tier personal budgeting tool designed for users who pay credit cards in full monthly. Progressive disclosure approach:
- **Phase 1**: Cash flow analysis - reveals where money goes (checking/savings → payment destinations)
- **Phase 2**: Spending detail - reveals what was purchased (credit card → spending categories)

**Key Philosophy**: Automation-first, no mandatory manual entry. Import bank/credit card statements (PDFs) → get insights.

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | Streamlit | Web UI running on localhost:8501 |
| Backend | Python 3.9+ | Data processing, PDF parsing, analysis |
| Database | SQLite | Single-file database at `data/budgeting.db` |
| ORM | SQLAlchemy | Type-safe database access |
| PDF Parsing | pdfplumber + pytesseract | Extract transactions from PDFs (text + OCR fallback) |
| Data Analysis | pandas | Transaction aggregation, time-series |
| Visualization | Plotly/Altair | Interactive charts |

## Project Structure

```
budgeting/
├── app.py                    # Streamlit homepage (main entry point)
├── requirements.txt          # Python dependencies
├── data/
│   └── budgeting.db         # SQLite database (gitignored)
├── statements/              # User's PDF statements (gitignored)
│   ├── BankOfAmerica-Statement/
│   └── TechCu-Statement/
├── config/
│   ├── bank_parsers.yaml    # Bank-specific parsing rules
│   ├── payment_patterns.yaml # Payment destination detection rules
│   └── default_categories.yaml # Category seeds (Phase 2)
├── src/
│   ├── database/            # SQLAlchemy models, connection
│   ├── parsers/             # PDF parsing, bank adapters
│   ├── categorization/      # Transaction categorization (Phase 2)
│   ├── budgets/             # Budget suggestions (Phase 2)
│   ├── analyzers/           # Payment detection, cash flow analysis
│   ├── ui/                  # Reusable UI components
│   └── utils/               # Helpers (duplicate detection, etc.)
├── pages/                   # Streamlit multi-page app
│   ├── 01_import.py         # PDF import interface
│   ├── 02_transactions.py   # View/search transactions
│   ├── 03_categorize.py     # Category management (Phase 2)
│   ├── 04_budgets.py        # Budget recommendations (Phase 2)
│   └── 05_analytics.py      # Charts and insights
├── scripts/
│   ├── setup_db.py          # Initialize database schema
│   └── import_statements.py # CLI bulk import tool
└── tests/
    ├── test_parsers/
    ├── test_categorization/
    └── fixtures/            # Sample PDFs, test data
```

## Database Architecture

**Phase 1 Core Tables**:
- `accounts`: Bank accounts (checking/savings)
- `transactions`: All financial transactions
- `payment_destinations`: Where money goes (credit cards, PayPal, bills)
- `import_logs`: Track PDF imports, detect duplicates via file hash

**Phase 2 Extensions**:
- `categories`: Spending categories (Groceries, Dining, etc.)
- `category_rules`: Auto-categorization patterns
- `budgets`: Budget definitions and tracking
- `credit_card_statements`: Credit card statement metadata

**Key Relationships**:
- `transactions.account_id` → `accounts.id`
- `transactions.payment_destination_id` → `payment_destinations.id` (Phase 1)
- `transactions.category_id` → `categories.id` (Phase 2)
- `transactions.source_file` → Links transaction to originating PDF

**Duplicate Detection**: Transactions matched by: account + date (±2 days) + amount (±$0.01) + description (fuzzy)

## Development Workflow

Development follows an **Epic-based approach**:

### Phase 1 Epics (Checking/Savings Analysis)
1. **Epic 1**: Foundation & Database Setup
2. **Epic 2**: Checking/Savings PDF Import (pdfplumber + bank adapters)
3. **Epic 3**: Payment Destination Detection (pattern matching)
4. **Epic 4**: Cash Flow Analytics (income/expenses dashboard)
5. **Epic 5**: Import Suggestions ("What to import next?" - CC accounts detected)

### Phase 2 Epics (Credit Card Detail)
6. **Epic 6**: Credit Card Import (link CC statements to checking payments)
7. **Epic 7**: Transaction Categorization (auto-categorize + manual corrections)
8. **Epic 8**: Budget Recommendations (analyze spending, suggest budgets)

**Current Status**: Planning phase - only PRD and bank statements exist.

## Common Commands

### Initial Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/setup_db.py
```

### Running the Application
```bash
# Start Streamlit app (main UI)
streamlit run app.py

# Access at: http://localhost:8501
```

### Development
```bash
# Run tests
pytest tests/

# Run specific test file
pytest tests/test_parsers/test_bank_adapters.py

# Run tests with coverage
pytest --cov=src tests/

# Bulk import statements (CLI)
python scripts/import_statements.py --account-id 1 --directory statements/BankOfAmerica-Statement/
```

### Database Management
```bash
# Recreate database (WARNING: deletes all data)
rm data/budgeting.db
python scripts/setup_db.py

# Access database directly
sqlite3 data/budgeting.db
```

## Key Architectural Patterns

### Bank Adapter Pattern
Each bank has a specific parser adapter inheriting from `BaseBankAdapter`:
- **Responsibility**: Parse bank-specific PDF formats
- **Location**: `src/parsers/bank_adapters/`
- **Example**: `bank_of_america.py`, `techcu.py`
- **Methods**: `parse_transactions()`, `detect_statement_type()`, `extract_account_info()`

### Payment Destination Detection
Pattern-based matching to identify where money flows:
- **Config**: `config/payment_patterns.yaml` - regex patterns for credit cards, payment services, bills
- **Logic**: `src/analyzers/payment_detector.py`
- **Goal**: Answer "Where did my checking account money go?" (e.g., Chase CC, Venmo, utilities)

### Progressive Disclosure (Phase 1 → Phase 2)
- **Phase 1**: Focus on cash flow without drilling into transactions
  - Import checking/savings → see payment destinations → identify what accounts to import next
  - Example: "You paid $2,500/month to Chase CC" → prompt to import Chase CC statements
- **Phase 2**: Drill into spending categories
  - Import CC statements → auto-categorize → see "Chase $2,500 = $600 groceries + $400 dining + ..."
  - Link CC statement to checking payment via date + amount matching

### Duplicate Detection Strategy
- **File-level**: SHA256 hash in `import_logs.file_hash` - skip re-importing same PDF
- **Transaction-level**: Fuzzy match on account + date + amount + description
- **Purpose**: Allow re-imports without creating duplicates (e.g., overlapping statement periods)

## Phase 1 vs Phase 2 Distinctions

**Phase 1 (Checking/Savings)**:
- Transaction source: `account_type = 'checking' OR 'savings'`
- Key analysis: Payment destinations (credit cards, bills, transfers)
- No categorization - focus is "where did money go?" not "what was purchased?"
- Dashboard: Income vs Expenses, Payment Destination Breakdown

**Phase 2 (Credit Card)**:
- Transaction source: `account_type = 'credit_card'`
- Key analysis: Spending categories (Groceries, Dining, Entertainment)
- Links to Phase 1: Match CC statement to checking payment (date + amount)
- Dashboard: Category spending, Budget vs Actual, Month-over-month trends

## Testing Strategy

### Epic-by-Epic Validation
Each epic has explicit acceptance criteria tested against **real PDFs** in `statements/`:
- **Epic 2**: Import BOA checking statement → verify 100% transaction extraction, test duplicate detection
- **Epic 3**: Run payment detector → verify detects "CHASE CREDIT CARD", "PAYPAL", etc.
- **Epic 6**: Import Chase CC statement → verify links to checking account payment

### Test Data
- **Real PDFs**: Use existing statements in `statements/BankOfAmerica-Statement/` and `statements/TechCu-Statement/`
- **Fixtures**: Anonymized/synthetic statements in `tests/fixtures/` for CI/CD

### Testing Commands
```bash
# Run all tests
pytest

# Test specific epic
pytest tests/test_parsers/  # Epic 2 tests
pytest tests/test_categorization/  # Epic 7 tests

# Integration test (end-to-end)
pytest tests/test_integration/test_phase1_workflow.py
```

## Important Constraints

1. **Single-user application**: No authentication, localhost-only, one SQLite database
2. **PDF-only import**: No live bank connections (Plaid/Yodlee) - all data from PDF uploads
3. **Automation-first**: Minimize manual data entry - everything derived from statements
4. **Privacy-first**: All data stored locally in `data/budgeting.db`, no cloud sync
5. **Progressive disclosure**: Phase 1 must work independently - don't build Phase 2 dependencies into Phase 1

## Development Priorities

**P0 (Must Have)**:
- Epics 1-5 (Phase 1 core functionality)
- Epics 6-7 (Phase 2 core functionality)

**P1 (Should Have)**:
- Epic 8 (Budget recommendations)
- Improved categorization (learning from corrections)

**P2 (Nice to Have)**:
- Multi-account reconciliation
- Email import automation
- Export reports (CSV, PDF)

## Reference Documents

- **Complete PRD**: See `mossy-growing-cocke.md` for full requirements, user stories, and implementation plan
- **Database Schema**: Full schema definitions in PRD under "Database Schema Design"
- **Epic Details**: Detailed task breakdowns in PRD under "Phase 1/2 Implementation"
