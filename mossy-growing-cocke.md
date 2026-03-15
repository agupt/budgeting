# Personal Budgeting Tool
# Product Requirements Document (PRD) & Engineering Execution Plan

**Document Version**: 1.0
**Last Updated**: March 15, 2026
**Author**: Product & Engineering Team
**Status**: Planning Phase

---

# PART 1: PRODUCT REQUIREMENTS DOCUMENT (PRD)

## 1. Executive Summary

A two-tier budgeting tool designed for financially responsible users who pay credit cards in full monthly. The tool provides progressive financial insight disclosure: Phase 1 reveals cash flow patterns (where money goes), Phase 2 reveals spending details (what was purchased).

**Key Differentiator**: Automation-first approach with no mandatory manual entry, targeting users frustrated by overly complex budgeting tools.

---

## 2. Problem Statement

### Current Pain Points
- **Existing budgeting apps are too complex**: Force users through extensive setup, complex category hierarchies, and mandatory data entry
- **No clear cash flow visibility**: Hard to answer "Where did my money go?" without drilling into every transaction
- **Poor fit for credit card payers**: Tools designed for debt management, not for users who pay cards in full monthly
- **Real-time connectivity overhead**: Bank connection setup is complex and fragile

### User Need
Users who pay credit cards monthly want to:
1. **Understand cash flow**: "I earned $X, spent $Y, where did it go?"
2. **Identify payment destinations**: "I paid $2,500 to Chase CC, $300 to Venmo"
3. **Drill into spending details**: "What did that $2,500 Chase payment cover?"
4. **Get budget suggestions**: "Based on history, I should budget $600/month for groceries"

---

## 3. Target Users

### Primary Persona: "Financially Organized Professional"
- **Age**: 28-45
- **Income**: $60K-150K annually
- **Financial Behavior**:
  - Pays credit cards in full monthly (no revolving debt)
  - Maintains 4-7 financial accounts (checking, savings, 2-3 credit cards)
  - Wants to understand spending without micromanaging
- **Pain Point**: Current budgeting tools are overkill; spreadsheets are too manual
- **Goal**: Automate transaction tracking, understand where money goes, get actionable insights

---

## 4. Product Goals

### Phase 1 Goals (Checking/Savings Analysis)
1. **Cash Flow Transparency**: Show total income, total expenses, net savings
2. **Payment Destination Visibility**: Identify where money went (credit cards, PayPal, bills)
3. **Import Guidance**: Suggest which accounts to import next based on payment amounts

### Phase 2 Goals (Credit Card Detail)
4. **Spending Breakdown**: Categorize credit card spending (groceries, dining, gas, etc.)
5. **Budget Suggestions**: Auto-suggest budgets based on 3-6 month historical averages
6. **Trend Analysis**: Show spending trends over time per category

### Non-Goals (Out of Scope)
- ❌ Investment/stock portfolio tracking
- ❌ Bill payment scheduling or reminders
- ❌ Credit card debt management
- ❌ Multi-user/shared accounts
- ❌ Mobile app or cloud sync
- ❌ Real-time bank connectivity

---

## 5. User Stories

### Phase 1 User Stories

**US-101: Import Historical Statements**
- **As a** user
- **I want to** import my checking and savings account PDFs
- **So that** I can see my historical cash flow

**US-102: View Cash Flow Summary**
- **As a** user
- **I want to** see my monthly income vs expenses
- **So that** I understand my savings rate

**US-103: Identify Payment Destinations**
- **As a** user
- **I want to** see where my money went (credit cards, PayPal, bills)
- **So that** I know which accounts to investigate further

**US-104: Prioritize Next Imports**
- **As a** user
- **I want to** see suggested accounts to import next (ranked by payment amount)
- **So that** I can focus on the biggest spending areas first

### Phase 2 User Stories

**US-201: Import Credit Card Statements**
- **As a** user
- **I want to** import my credit card PDFs
- **So that** I can see what I bought

**US-202: Categorize Credit Card Spending**
- **As a** user
- **I want** transactions auto-categorized (groceries, dining, etc.)
- **So that** I understand spending by category

**US-203: View Spending Breakdown**
- **As a** user
- **I want to** see "$2,500 Chase payment = $600 groceries + $400 dining"
- **So that** I understand what each credit card payment covered

**US-204: Get Budget Suggestions**
- **As a** user
- **I want** the system to suggest budgets based on my history
- **So that** I can set realistic spending targets

---

## 6. Features & Requirements

### Phase 1: Checking/Savings Analysis

#### F1.1: PDF Import System
**Priority**: P0 (Must Have)

**Requirements**:
- FR-111: Support Bank of America checking/savings statement PDFs
- FR-112: Support TechCU checking/savings statement PDFs
- FR-113: Detect and skip duplicate transactions
- FR-114: Extract: transaction date, description, amount, balance
- FR-115: Support multi-page PDF statements
- FR-116: Handle mixed PDF formats (text + scanned)

**Acceptance Criteria**:
- Import BOA PDF → 100% transaction extraction accuracy
- Import TechCU PDF → 100% transaction extraction accuracy
- Re-import same PDF → 0 duplicate transactions created

#### F1.2: Payment Destination Detection
**Priority**: P0 (Must Have)

**Requirements**:
- FR-121: Detect credit card payments ("CHASE CREDIT CARD", "AMEX PAYMENT")
- FR-122: Detect payment service transfers ("PAYPAL", "VENMO", "ZELLE")
- FR-123: Detect bill payments ("PG&E", "COMCAST")
- FR-124: Aggregate monthly payment amounts per destination
- FR-125: Display payment destinations ranked by amount

**Acceptance Criteria**:
- Detect "CHASE CARD PAYMENT $2,500" → Identify Chase CC
- List: "Chase CC: $2,500/month, Venmo: $300/month, PayPal: $150/month"
- Rank by amount descending

#### F1.3: Cash Flow Dashboard
**Priority**: P0 (Must Have)

**Requirements**:
- FR-131: Calculate monthly total income
- FR-132: Calculate monthly total expenses
- FR-133: Calculate net savings (income - expenses)
- FR-134: Display savings rate as percentage
- FR-135: Show income vs expenses chart over time (6-12 months)
- FR-136: Show payment destination breakdown (bar chart)

**Acceptance Criteria**:
- Dashboard shows: "Income: $5,000, Expenses: $4,200, Savings: $800 (16%)"
- Chart displays last 6 months income/expenses trend
- Bar chart shows top 10 payment destinations

#### F1.4: Import Suggestions
**Priority**: P1 (Should Have)

**Requirements**:
- FR-141: List all detected payment destinations not yet imported
- FR-142: Show monthly average payment amount per destination
- FR-143: Sort by amount descending (highest first)
- FR-144: Display suggestion: "Import [Account] to see $X breakdown"

**Acceptance Criteria**:
- Page shows: "Chase CC: $2,500/month (not imported) → Import to see details"
- Sorted correctly by monthly amount

---

### Phase 2: Credit Card Detail Analysis

#### F2.1: Credit Card PDF Import
**Priority**: P0 (Must Have)

**Requirements**:
- FR-211: Support Chase credit card statement PDFs
- FR-212: Support Amex, Capital One, Discover credit card PDFs
- FR-213: Extract: transaction date, merchant, amount, category
- FR-214: Link CC statement to checking account payment
- FR-215: Show which checking payment covers which CC statement

**Acceptance Criteria**:
- Import Chase CC PDF → 100% transaction extraction
- Link to checking payment: "March $2,500 payment covers statement ending 2/28"

#### F2.2: Transaction Categorization
**Priority**: P0 (Must Have)

**Requirements**:
- FR-221: Auto-categorize transactions using pattern matching
- FR-222: Support categories: Groceries, Gas, Dining, Shopping, Bills, Entertainment, Travel, Other
- FR-223: Allow manual category override
- FR-224: Learn from manual overrides (suggest new rules)
- FR-225: Show categorization confidence score

**Acceptance Criteria**:
- "WHOLE FOODS" → Auto-categorized as Groceries (95% confidence)
- User changes "AMAZON" from Shopping to Groceries → System suggests rule
- 85%+ auto-categorization accuracy on first import

#### F2.3: Spending Breakdown
**Priority**: P0 (Must Have)

**Requirements**:
- FR-231: Show credit card payment breakdown by category
- FR-232: Display: "$2,500 = $600 groceries + $400 dining + $200 gas + $1,300 shopping"
- FR-233: Pie chart of category distribution
- FR-234: Month-over-month category comparison

**Acceptance Criteria**:
- Breakdown matches sum of categorized transactions
- Pie chart visually accurate
- Can compare current month vs previous month per category

#### F2.4: Budget Suggestions
**Priority**: P1 (Should Have)

**Requirements**:
- FR-241: Analyze 3-6 months of historical spending per category
- FR-242: Calculate: mean, median, standard deviation
- FR-243: Suggest budget = median + 10% buffer
- FR-244: Display confidence score based on consistency
- FR-245: Allow user to accept, adjust, or reject suggestion

**Acceptance Criteria**:
- Suggest: "Groceries: $620/month (based on 6-month avg $587, confidence: 88%)"
- Track spending vs budget: "Groceries: $450/$620 (73%)"
- Alert when 90%+ of budget used

---

## 7. Success Metrics

### Phase 1 Success Metrics
- **Adoption**: User imports all checking/savings statements (100+ PDFs)
- **Value**: User can answer "Where did my money go last month?" in < 30 seconds
- **Accuracy**: 95%+ payment destination detection accuracy
- **Engagement**: User checks dashboard at least weekly

### Phase 2 Success Metrics
- **Adoption**: User imports primary credit card statements
- **Categorization**: 85%+ auto-categorization accuracy
- **Budget Creation**: User accepts or creates budgets for top 5 categories
- **Retention**: User continues using tool for 3+ months

---

## 8. Technical Constraints

- **Local-only**: No cloud infrastructure, all data stored locally
- **Single-user**: No multi-user authentication or shared accounts
- **Desktop-only**: No mobile app support
- **Python stack**: Streamlit + SQLite + pandas ecosystem

---

# PART 2: ENGINEERING EXECUTION PLAN

## 1. Technical Architecture

### System Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Streamlit Web UI                      │
│  (localhost:8501)                                       │
└────────────────┬────────────────────────────────────────┘
                 │
     ┌───────────▼──────────────┐
     │   Application Layer      │
     │  - Analyzers             │
     │  - Parsers               │
     │  - Categorization        │
     └───────────┬──────────────┘
                 │
     ┌───────────▼──────────────┐
     │   Data Access Layer      │
     │  - SQLAlchemy ORM        │
     └───────────┬──────────────┘
                 │
     ┌───────────▼──────────────┐
     │   SQLite Database        │
     │  (data/budgeting.db)     │
     └──────────────────────────┘
```

### Technology Stack

| Layer | Technology | Justification |
|-------|------------|---------------|
| **Frontend** | Streamlit | Rapid development, built-in components, perfect for localhost dashboards |
| **Backend** | Python 3.9+ | Rich ecosystem for data processing, PDF parsing |
| **Database** | SQLite | Zero-config, portable, sufficient for single-user |
| **ORM** | SQLAlchemy | Type-safe database access, easy migrations |
| **PDF Parsing** | pdfplumber | Best for text-based PDFs, good table detection |
| **OCR Fallback** | pytesseract | Handles scanned/image PDFs |
| **Data Analysis** | pandas | Data manipulation, aggregation, time-series analysis |
| **Visualization** | Plotly/Altair | Interactive charts, Streamlit integration |

---

## 2. Database Schema Design

### Phase 1 Schema

```sql
-- Core tables for Phase 1
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,           -- "BOA Checking", "TechCU Savings"
    account_type TEXT NOT NULL,          -- "checking", "savings"
    bank_name TEXT NOT NULL,             -- "Bank of America", "TechCU"
    last_four TEXT,                      -- Last 4 digits
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    transaction_date DATE NOT NULL,
    description TEXT NOT NULL,
    amount REAL NOT NULL,                -- Negative = debit, Positive = credit
    balance_after REAL,
    transaction_type TEXT,               -- "debit", "credit", "transfer"
    source TEXT DEFAULT 'pdf_import',    -- "pdf_import", "manual"
    source_file TEXT,                    -- Reference to PDF filename
    import_batch_id TEXT,                -- Group transactions from same import
    payment_destination_id INTEGER,      -- FK to payment_destinations
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    FOREIGN KEY (payment_destination_id) REFERENCES payment_destinations(id)
);

CREATE INDEX idx_trans_account_date ON transactions(account_id, transaction_date);
CREATE INDEX idx_trans_payment_dest ON transactions(payment_destination_id);

CREATE TABLE payment_destinations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,           -- "Chase Credit Card", "PayPal", "Venmo"
    destination_type TEXT NOT NULL,      -- "credit_card", "payment_service", "bill", "other"
    pattern TEXT,                        -- Detection pattern (for reference)
    monthly_avg_amount REAL,             -- Average monthly payment
    last_detected_date DATE,
    transaction_count INTEGER DEFAULT 0,
    is_imported BOOLEAN DEFAULT 0,       -- Has user imported this account?
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE import_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id TEXT NOT NULL UNIQUE,       -- UUID for import batch
    file_path TEXT NOT NULL,
    file_hash TEXT NOT NULL,             -- SHA256 for duplicate detection
    account_id INTEGER,
    import_status TEXT NOT NULL,         -- "success", "partial", "failed"
    transactions_imported INTEGER DEFAULT 0,
    transactions_skipped INTEGER DEFAULT 0,
    error_message TEXT,
    import_method TEXT NOT NULL,         -- "pdfplumber", "tesseract", "hybrid"
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);
```

### Phase 2 Schema Extensions

```sql
-- Additional tables for Phase 2
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category_type TEXT NOT NULL,         -- "expense", "income"
    icon TEXT,                           -- For UI display
    color TEXT,                          -- Hex color for charts
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE category_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    pattern TEXT NOT NULL,               -- Regex or substring
    pattern_type TEXT DEFAULT 'substring', -- "substring", "regex", "exact"
    priority INTEGER DEFAULT 0,
    confidence_score REAL,               -- 0-1
    match_count INTEGER DEFAULT 0,       -- Usage tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Extend transactions table with category_id
ALTER TABLE transactions ADD COLUMN category_id INTEGER REFERENCES categories(id);

CREATE TABLE budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    amount REAL NOT NULL,
    source TEXT DEFAULT 'manual',        -- "manual", "suggested"
    confidence_score REAL,               -- For suggested budgets
    historical_avg REAL,
    historical_median REAL,
    historical_stddev REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

---

## 3. Epic Breakdown & Detailed Tasks

### Phase 1: Checking/Savings Analysis (6-9 sessions, 13-20 hours)

#### **EPIC 1: Foundation & Database Setup**
**Duration**: 1 session (2-3 hours)
**Priority**: P0 (Blocker for all other epics)

**Objectives**:
- Establish project structure
- Create database schema
- Set up development environment

**Tasks**:
1. **E1-T1: Project Setup** (30 min)
   - Create Python virtual environment
   - Install dependencies: streamlit, sqlalchemy, pdfplumber, pandas, plotly
   - Create `requirements.txt`
   - Set up `.gitignore` (exclude `data/`, `.env`, `*.db`)

2. **E1-T2: Directory Structure** (15 min)
   - Create folder structure:
     ```
     budgeting/
     ├── app.py
     ├── requirements.txt
     ├── data/
     ├── src/
     │   ├── database/
     │   ├── parsers/
     │   ├── analyzers/
     │   └── ui/
     ├── pages/
     ├── config/
     └── scripts/
     ```

3. **E1-T3: Database Schema** (1 hour)
   - Create `src/database/schema.py` with SQLAlchemy models:
     - `Account` model
     - `Transaction` model
     - `PaymentDestination` model
     - `ImportLog` model
   - Define relationships and indexes

4. **E1-T4: Database Connection** (30 min)
   - Create `src/database/connection.py`
   - Implement: `get_db_session()`, `init_database()`
   - Create `scripts/setup_db.py` to initialize database

5. **E1-T5: Verification** (30 min)
   - Run `scripts/setup_db.py`
   - Verify `data/budgeting.db` created
   - Test: Insert test account, query successfully

**Acceptance Criteria**:
- ✅ Database file created at `data/budgeting.db`
- ✅ All tables exist (accounts, transactions, payment_destinations, import_logs)
- ✅ Can insert and query test data
- ✅ No errors in setup script

**Dependencies**: None

---

#### **EPIC 2: Checking/Savings PDF Import**
**Duration**: 2-3 sessions (4-6 hours)
**Priority**: P0 (Must Have)

**Objectives**:
- Extract transactions from BOA and TechCU PDFs
- Handle duplicate detection
- Provide import UI

**Tasks**:
1. **E2-T1: Statement Detector** (1 hour)
   - Create `src/parsers/statement_detector.py`
   - Implement `detect_bank(pdf_path)`:
     - Extract first page text
     - Pattern match: "Bank of America", "Technology Credit Union"
     - Return: bank identifier, confidence score
   - Test with sample PDFs

2. **E2-T2: PDFPlumber Parser** (1.5 hours)
   - Create `src/parsers/pdfplumber_parser.py`
   - Implement `extract_transactions(pdf_path, bank_adapter)`:
     - Extract table data from PDF
     - Handle multi-page statements
     - Return: List[Transaction]
   - Test with BOA and TechCU samples

3. **E2-T3: Bank Adapters** (2 hours)
   - Create `src/parsers/bank_adapters/base.py` (abstract base class)
   - Create `src/parsers/bank_adapters/bank_of_america.py`:
     - Parse BOA-specific table format
     - Extract: date, description, amount, balance
     - Handle debit/credit distinction
   - Create `src/parsers/bank_adapters/techcu.py`:
     - Parse TechCU-specific format
     - Same extraction requirements
   - Test with 3 sample statements each

4. **E2-T4: Duplicate Detection** (1 hour)
   - Create `src/utils/duplicate_detector.py`
   - Implement `is_duplicate(transaction, existing_transactions)`:
     - Match on: date + amount + description (fuzzy)
     - Date window: ±2 days
     - Amount tolerance: ±$0.01
   - Test with re-imported PDFs

5. **E2-T5: Import UI** (1.5 hours)
   - Create `pages/01_import.py`
   - UI components:
     - File uploader (accept .pdf)
     - Account selector dropdown
     - Preview table (show extracted transactions)
     - Import button with progress bar
     - Summary: "45 imported, 3 duplicates skipped"

6. **E2-T6: Integration & Testing** (1 hour)
   - End-to-end test: Upload BOA PDF → View transactions
   - Verify: All transactions match statement
   - Verify: Re-import skips duplicates
   - Test error handling (invalid PDF, corrupted file)

**Acceptance Criteria**:
- ✅ Import BOA checking statement → 100% transaction extraction
- ✅ Import TechCU statement → 100% transaction extraction
- ✅ Re-import same PDF → 0 new transactions (all marked duplicate)
- ✅ UI shows preview before import
- ✅ Import logs saved to database

**Dependencies**: Epic 1 (Database must exist)

---

#### **EPIC 3: Payment Destination Detection**
**Duration**: 1-2 sessions (2-4 hours)
**Priority**: P0 (Must Have)

**Objectives**:
- Detect where money went from transaction descriptions
- Aggregate payment amounts per destination

**Tasks**:
1. **E3-T1: Payment Pattern Configuration** (30 min)
   - Create `config/payment_patterns.yaml`
   - Define regex patterns for:
     - Credit cards: `".*CHASE.*CREDIT CARD.*"`, `".*AMEX.*PAYMENT.*"`
     - Payment services: `".*PAYPAL.*"`, `".*VENMO.*"`, `".*ZELLE.*"`
     - Bills: `".*PG&E.*"`, `".*COMCAST.*"`

2. **E3-T2: Payment Detector** (2 hours)
   - Create `src/analyzers/payment_detector.py`
   - Implement `detect_payment_destination(description)`:
     - Load patterns from YAML
     - Match description against patterns
     - Extract destination name (e.g., "Chase Credit Card")
     - Return: destination name, type, confidence
   - Implement `analyze_all_transactions(account_id)`:
     - Run detector on all transactions
     - Create/update payment_destinations records
     - Link transactions to destinations

3. **E3-T3: Payment Destinations UI** (1.5 hours)
   - Create `pages/02_payment_destinations.py`
   - Display table:
     - Destination name
     - Type (credit card, payment service, bill)
     - Monthly average amount
     - Transaction count
     - Last seen date
   - Sort by monthly amount (descending)
   - Add "Not Yet Imported" badge for unimported accounts

4. **E3-T4: Testing** (1 hour)
   - Test with real imported transactions
   - Verify: "CHASE CREDIT CARD PAYMENT" → Detected as Chase CC
   - Verify: Monthly amounts calculated correctly
   - Verify: UI displays all destinations

**Acceptance Criteria**:
- ✅ Detect credit card payments with 95%+ accuracy
- ✅ Detect payment service transfers with 90%+ accuracy
- ✅ UI lists all destinations sorted by amount
- ✅ Monthly average calculation is correct

**Dependencies**: Epic 2 (Needs imported transactions)

---

#### **EPIC 4: Basic Cash Flow Analytics**
**Duration**: 1-2 sessions (3-4 hours)
**Priority**: P0 (Must Have)

**Objectives**:
- Calculate and display cash flow metrics
- Visualize income vs expenses over time

**Tasks**:
1. **E3-T1: Cash Flow Analyzer** (1.5 hours)
   - Create `src/analyzers/cash_flow.py`
   - Implement `calculate_monthly_cashflow(account_ids, month, year)`:
     - Sum all positive transactions (income)
     - Sum all negative transactions (expenses)
     - Calculate net savings
     - Calculate savings rate percentage
     - Return: CashFlowSummary dataclass
   - Implement `get_cashflow_trend(account_ids, months=6)`:
     - Calculate cash flow for last N months
     - Return: List[CashFlowSummary] sorted by date

2. **E4-T2: Dashboard UI** (2 hours)
   - Create `app.py` (Streamlit homepage)
   - Display metrics cards:
     - Monthly Income (large green number)
     - Monthly Expenses (large red number)
     - Net Savings (large blue number)
     - Savings Rate (percentage with progress bar)
   - Line chart: Income vs Expenses over time (6 months)
   - Bar chart: Top 10 payment destinations by amount

3. **E4-T3: Transaction List** (1 hour)
   - Create `pages/03_transactions.py`
   - Display filterable transaction table:
     - Columns: Date, Description, Amount, Account, Payment Destination
     - Filters: Date range, Account dropdown, Search box
     - Pagination (100 per page)
   - Export CSV button

4. **E4-T4: Testing** (30 min)
   - Import 3 months of statements
   - Verify: Dashboard shows correct totals
   - Verify: Charts render properly
   - Verify: Transaction list filters work

**Acceptance Criteria**:
- ✅ Dashboard shows: Income, Expenses, Savings, Savings Rate
- ✅ Line chart displays last 6 months trend
- ✅ Bar chart shows top payment destinations
- ✅ Transaction list is filterable and paginated

**Dependencies**: Epic 2 & 3 (Needs transactions and payment destinations)

---

#### **EPIC 5: Import Suggestions**
**Duration**: 1 session (2-3 hours)
**Priority**: P1 (Should Have)

**Objectives**:
- Suggest which accounts to import next
- Prioritize by payment amount

**Tasks**:
1. **E5-T1: Import Recommender** (1 hour)
   - Create `src/analyzers/import_recommender.py`
   - Implement `get_import_suggestions()`:
     - Query payment_destinations where is_imported = False
     - Calculate priority score (monthly_avg_amount * transaction_count)
     - Sort by priority descending
     - Return: List[ImportSuggestion]

2. **E5-T2: Suggestions UI** (1.5 hours)
   - Create `pages/04_import_suggestions.py`
   - Display cards for each suggestion:
     - Destination name
     - "Not Yet Imported" badge
     - Monthly average: "$2,500/month"
     - Transaction count: "12 payments"
     - Suggestion text: "Import Chase CC to see $2,500 spending breakdown"
   - Sort by monthly amount (highest first)
   - "Mark as Imported" button (manual override)

3. **E5-T3: Testing** (30 min)
   - Verify: Suggestions show all unimported destinations
   - Verify: Sorted correctly by amount
   - Verify: Amounts are accurate

**Acceptance Criteria**:
- ✅ Lists all detected payment destinations not yet imported
- ✅ Sorted by monthly amount descending
- ✅ Shows clear call-to-action for each suggestion

**Dependencies**: Epic 3 (Needs payment destinations)

---

### Phase 2: Credit Card Detail Analysis (5-7 sessions, 11-15 hours)

#### **EPIC 6: Credit Card PDF Import**
**Duration**: 2-3 sessions (4-6 hours)
**Priority**: P0 (Must Have for Phase 2)

**Objectives**:
- Extend parser to support credit card statements
- Link CC transactions to checking payments

**Tasks**:
1. **E6-T1: Credit Card Adapters** (2 hours)
   - Create `src/parsers/bank_adapters/chase_cc.py`
   - Create `src/parsers/bank_adapters/amex_cc.py`
   - Parse CC-specific fields:
     - Transaction date
     - Post date
     - Merchant name
     - Category (if provided by bank)
     - Amount
   - Test with sample CC statements

2. **E6-T2: Payment Linker** (2 hours)
   - Create `src/analyzers/payment_linker.py`
   - Implement `link_cc_to_checking_payment(cc_statement_id)`:
     - Find checking payment matching CC statement total
     - Match by: amount (±$1), date window (±7 days)
     - Create link in database
   - Display in UI: "March payment $2,500 covers statement ending 2/28"

3. **E6-T3: UI Updates** (1 hour)
   - Extend `pages/01_import.py` to support CC imports
   - Add CC account type selector
   - Show linked checking payment after import

4. **E6-T4: Testing** (1 hour)
   - Import Chase CC statement
   - Verify: All transactions extracted
   - Verify: Linked to correct checking payment

**Acceptance Criteria**:
- ✅ Import Chase CC PDF → 100% transaction extraction
- ✅ CC transactions linked to checking payment
- ✅ UI shows linkage clearly

**Dependencies**: Epic 1-2 (Database and parser infrastructure)

---

#### **EPIC 7: Category-Level Spending Analysis**
**Duration**: 2 sessions (4-5 hours)
**Priority**: P0 (Must Have for Phase 2)

**Objectives**:
- Categorize CC transactions automatically
- Display spending breakdown by category

**Tasks**:
1. **E7-T1: Category Setup** (30 min)
   - Create `config/default_categories.yaml`
   - Define categories: Groceries, Gas, Dining, Shopping, Bills, Entertainment, Travel, Other
   - Seed categories table via `scripts/seed_categories.py`

2. **E7-T2: Categorization Rules** (1 hour)
   - Create `config/categorization_rules.yaml`
   - Define initial rules:
     - "WHOLE FOODS", "SAFEWAY" → Groceries
     - "CHEVRON", "SHELL" → Gas
     - "UBER EATS", "DOORDASH" → Dining
     - "AMAZON", "TARGET" → Shopping
   - Load into category_rules table

3. **E7-T3: Rule Engine** (2 hours)
   - Create `src/categorization/rule_engine.py`
   - Implement `categorize_transaction(description)`:
     - Match against rules (exact → substring → regex)
     - Return: category_id, confidence_score
   - Implement `categorize_all_transactions(account_id)`:
     - Run on all uncategorized transactions
     - Update transaction.category_id

4. **E7-T4: Category Breakdown UI** (1.5 hours)
   - Create `pages/05_category_breakdown.py`
   - Show for selected CC statement:
     - Total amount
     - Pie chart: category distribution
     - Table: Category, Amount, % of Total, Transaction Count
   - Example: "$2,500 = $600 Groceries (24%) + $400 Dining (16%) + ..."

5. **E7-T5: Manual Override & Learning** (1 hour)
   - Add "Edit Category" button on transaction list
   - On manual override: Suggest new rule creation
   - Display: "Create rule: 'AMAZON' → Groceries?"

6. **E7-T6: Testing** (1 hour)
   - Import CC statement with diverse transactions
   - Verify: 85%+ auto-categorization accuracy
   - Verify: Manual override works
   - Verify: Pie chart displays correctly

**Acceptance Criteria**:
- ✅ 85%+ auto-categorization accuracy on first import
- ✅ Pie chart shows category distribution
- ✅ Manual category override works
- ✅ System suggests new rules from overrides

**Dependencies**: Epic 6 (Needs CC transactions)

---

#### **EPIC 8: Budget Suggestions**
**Duration**: 1-2 sessions (3-4 hours)
**Priority**: P1 (Should Have for Phase 2)

**Objectives**:
- Analyze historical spending per category
- Suggest realistic budgets

**Tasks**:
1. **E8-T1: Budget Analyzer** (2 hours)
   - Create `src/budgets/analyzer.py`
   - Implement `analyze_category_spending(category_id, months=6)`:
     - Fetch last N months of transactions for category
     - Calculate: mean, median, std_dev, min, max
     - Detect trend: increasing/decreasing/stable
     - Return: SpendingAnalysis dataclass
   - Implement `suggest_budget(category_id)`:
     - Base = median spending
     - Buffer = +10% for variability
     - Adjust for trend
     - Calculate confidence score
     - Return: BudgetSuggestion

2. **E8-T2: Budget UI** (1.5 hours)
   - Create `pages/06_budgets.py`
   - Display suggestions for each category:
     - Category name
     - Historical analysis: "Avg: $587/month, Median: $565"
     - Suggested budget: "$620/month (confidence: 88%)"
     - Buttons: "Accept", "Adjust", "Reject"
   - For accepted budgets, show progress:
     - "$450 / $620 used (73%)"
     - Progress bar (green if < 90%, yellow if 90-99%, red if 100%+)

3. **E8-T3: Testing** (30 min)
   - Import 6 months of CC statements
   - View budget suggestions
   - Verify: Amounts are reasonable
   - Accept budget, verify tracking works

**Acceptance Criteria**:
- ✅ Suggestions based on 3-6 month history
- ✅ Confidence score displayed
- ✅ Budget tracking shows progress
- ✅ Alert when 90%+ of budget used

**Dependencies**: Epic 7 (Needs categorized transactions)

---

## 4. Dependencies & Critical Path

```
PHASE 1:
Epic 1 (Foundation)
    └─→ Epic 2 (PDF Import)
            └─→ Epic 3 (Payment Detection)
                    └─→ Epic 4 (Cash Flow Dashboard)
                    └─→ Epic 5 (Import Suggestions)

PHASE 2:
Epic 6 (CC Import) [depends on Epic 1-2]
    └─→ Epic 7 (Categorization) [depends on Epic 6]
            └─→ Epic 8 (Budgets) [depends on Epic 7]
```

**Critical Path**: Epic 1 → Epic 2 → Epic 3 → Epic 4
**Estimated Duration**: 6-9 sessions for Phase 1, 5-7 sessions for Phase 2

---

## 5. Risk Assessment & Mitigation

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| PDF parsing fails for certain banks | Medium | High | Implement hybrid parser with OCR fallback; add bank-specific adapters as needed |
| Duplicate detection misses transactions | Low | Medium | Implement fuzzy matching with date window and amount tolerance; allow manual merge |
| Payment destination detection inaccurate | Medium | Medium | Use configurable regex patterns; allow manual override and pattern learning |
| Performance issues with large datasets | Low | Low | Add database indexes; implement pagination; use pandas for aggregations |
| Categorization accuracy < 85% | Medium | Medium | Start with robust rule set; implement confidence scoring; allow easy manual override |

### Scope Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Phase 1 takes longer than estimated | Medium | Low | Phase 1 delivers immediate value; Phase 2 can be delayed without blocking usage |
| User requests additional bank support | High | Low | Modular adapter design makes adding banks straightforward |
| Feature creep (e.g., investment tracking) | Medium | Medium | Strict adherence to non-goals; defer out-of-scope requests to backlog |

---

## 6. Testing Strategy

### Unit Testing
- **Parser Tests**: Test each bank adapter with sample PDFs
- **Detection Tests**: Test payment destination and category detection with known descriptions
- **Calculation Tests**: Test cash flow calculations with known transaction sets
- **Duplicate Tests**: Test duplicate detection with edge cases (same amount different days, etc.)

### Integration Testing
- **Import Flow**: Upload PDF → Extract → Store → Display
- **Analysis Flow**: Transactions → Detect Destinations → Calculate Cash Flow
- **Category Flow**: CC Import → Categorize → Calculate Budgets

### End-to-End Testing
- **Phase 1 E2E**: Import all BOA + TechCU statements → View dashboard → See payment destinations → Check suggestions
- **Phase 2 E2E**: Import CC statement → View categorization → Accept budget → Track progress

### Performance Testing
- Import 100 PDFs (2+ years of statements) → Verify < 5 min total time
- Dashboard load with 10,000+ transactions → Verify < 2 sec render time

---

## 7. Deployment & Operations

### Local Deployment
1. Clone repository
2. Create virtual environment: `python -m venv venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Initialize database: `python scripts/setup_db.py`
5. Run app: `streamlit run app.py`
6. Access: http://localhost:8501

### Data Backup Strategy
- **Automatic**: SQLite database backed up weekly to `data/backups/`
- **Manual**: Export transactions to CSV via UI
- **Recovery**: Copy backup DB to `data/budgeting.db`

### Monitoring
- **Error Logging**: Log import errors to `logs/import_errors.log`
- **Usage Metrics**: Track: PDFs imported, transactions processed, categorization accuracy

---

## 8. Future Enhancements (Post-Phase 2)

**Epic 9: Email Monitoring**
- IMAP client to monitor dedicated email address
- Parse transaction alert emails
- Auto-import e-statement PDF attachments
- Deduplicate email alerts vs PDF transactions

**Epic 10: Advanced Analytics**
- Spending trends with seasonal adjustment
- Anomaly detection (unusual spending)
- Forecasting future expenses
- Net worth tracking (if savings/investment data available)

**Epic 11: Multi-User Support**
- Shared budgets for households
- Per-user transaction assignments
- Shared expense reconciliation

---

## 9. Success Criteria & Launch Readiness

### Phase 1 Launch Criteria
- ✅ All epic acceptance criteria met
- ✅ Successfully import 10+ BOA statements
- ✅ Successfully import 5+ TechCU statements
- ✅ Dashboard displays accurate cash flow
- ✅ Payment destinations detected with 95%+ accuracy
- ✅ No critical bugs in import or analysis flows

### Phase 2 Launch Criteria
- ✅ All Phase 2 epic acceptance criteria met
- ✅ Successfully import 5+ credit card statements
- ✅ 85%+ auto-categorization accuracy
- ✅ Budget suggestions for top 5 categories
- ✅ Budget tracking functional

### User Acceptance Criteria
- ✅ User can answer "Where did my money go?" in < 30 seconds
- ✅ User can identify top spending categories
- ✅ User finds tool simpler than alternatives tried
- ✅ User commits to using tool for 3+ months

---

## 10. Next Steps & Kick-Off

### Pre-Development Tasks
1. **Confirm requirements** with user (this document)
2. **Set up development environment** (Python, IDE, Git)
3. **Review sample PDFs** to validate parsing approach
4. **Clarify account names** and structure with user

### Kick-Off Questions for User
1. **Account naming**: What should we call your accounts? (e.g., "BOA Checking", "TechCU Savings")
2. **Historical import scope**: Import all history (2019-2026) or just recent (last 12 months)?
3. **Phase 1 completion definition**: What does success look like after Phase 1?
4. **Credit card priority**: Which CC to support first in Phase 2? (Chase, Amex, etc.)

### First Sprint (Epic 1)
**Goal**: Working database and project structure
**Duration**: 1 session (2-3 hours)
**Deliverables**:
- Database initialized
- Can manually add accounts
- Can manually insert test transactions
- Project structure in place

**Ready to Start**: Awaiting user confirmation and answers to kick-off questions.

---

**END OF DOCUMENT**
- `scripts/setup_db.py` - Initialize database with schema
- `requirements.txt` - Python dependencies

**Success Criteria:**
- Database created with accounts, transactions, payment_destinations tables
- Can add/query checking and savings accounts
- Simple enough to get started quickly

---

#### Epic 2: Checking/Savings PDF Import
**Deliverables:**
- Statement detector (identify Bank of America vs TechCU)
- PDF extraction for checking/savings statements ONLY
- Bank-specific adapters (Bank of America, TechCU)
- Duplicate transaction detection
- Import UI page

**Key Files to Create:**
- `src/parsers/statement_detector.py` - Identify bank from PDF
- `src/parsers/hybrid_parser.py` - Orchestrate pdfplumber + OCR extraction
- `src/parsers/pdfplumber_parser.py` - Primary text-based extraction
- `src/parsers/bank_adapters/bank_of_america.py` - BOA checking/savings parser
- `src/parsers/bank_adapters/techcu.py` - TechCU checking/savings parser
- `src/utils/duplicate_detector.py` - Detect duplicate transactions
- `pages/01_import.py` - Streamlit UI for PDF upload

**Success Criteria:**
- Import BOA checking statement → extract all transactions
- Import TechCU checking/savings statement → extract all transactions
- Detect and skip duplicate transactions on re-import
- View all imported transactions in UI

**Note**: Credit card statements are explicitly OUT OF SCOPE for Phase 1.

---

#### Epic 3: Payment Destination Detection
**Deliverables:**
- Auto-detect payment destinations from transaction descriptions
- Pattern recognition for credit cards (Chase, Amex, Discover, Capital One, etc.)
- Pattern recognition for payment services (PayPal, Venmo, Zelle)
- Payment destinations database table
- UI to view where money is going

**Key Files to Create:**
- `src/analyzers/payment_detector.py` - Identify payment destinations from descriptions
- `src/database/payment_destinations.py` - Track identified payment accounts
- `config/payment_patterns.yaml` - Regex patterns for common payment types
- `pages/02_payment_destinations.py` - UI showing where money went

**Success Criteria:**
- Detect "CHASE CREDIT CARD PAYMENT" → Identify Chase CC as destination
- Detect "PAYPAL TRANSFER" → Identify PayPal as destination
- List all payment destinations with total amounts paid per month
- Example output: "Chase CC: $2,500/month, Venmo: $300/month, PayPal: $150/month"

---

#### Epic 4: Basic Cash Flow Analytics
**Deliverables:**
- Homepage dashboard showing income vs expenses
- Monthly cash flow summary (how much came in, how much went out)
- Trend visualization (last 6-12 months)
- Breakdown by payment destination
- Simple transaction list with filtering

**Key Files to Create:**
- `app.py` - Streamlit homepage with cash flow dashboard
- `src/analyzers/cash_flow.py` - Calculate income, expenses, net savings
- `pages/03_transactions.py` - Transaction list with basic filters
- `src/ui/components/charts.py` - Chart components for visualizations

**Success Criteria:**
- Dashboard shows: "Income: $5,000/month, Expenses: $4,200/month, Savings: $800 (16%)"
- Chart showing income vs expenses over time
- Bar chart: payment destinations ranked by amount
- Filter transactions by date, account, payment destination

---

#### Epic 5: Import Suggestions
**Deliverables:**
- "What to Import Next" page
- List all detected payment destinations
- Show monthly amounts and transaction counts
- Suggest priority order (highest amounts first)
- Placeholder for "Not yet imported" credit card accounts

**Key Files to Create:**
- `pages/04_import_suggestions.py` - Suggest what to import next
- `src/analyzers/import_recommender.py` - Rank payment destinations by priority

**Success Criteria:**
- Page shows: "You paid $2,500/month to Chase CC (not imported)"
- Shows: "You paid $300/month to Venmo (not imported)"
- Suggests: "Import Chase CC next to see $2,500 breakdown"
- List is sorted by amount (highest first)

---

### Phase 2: Credit Card Detail Analysis
*Goal: Import credit card statements and link them to checking account payments*

#### Epic 6: Credit Card PDF Import
**Deliverables:**
- Extend PDF parser to handle credit card statements
- Credit card-specific adapters (Chase, Amex, Capital One, etc.)
- Import credit card transactions
- Link CC transactions to checking account payments

**Key Files to Create:**
- `src/parsers/bank_adapters/chase_cc.py` - Chase credit card parser
- `src/parsers/bank_adapters/amex_cc.py` - Amex credit card parser
- `src/analyzers/payment_linker.py` - Link CC bill to checking payment

**Success Criteria:**
- Import Chase CC statement → extract all transactions
- Link to checking account payment: "March payment: $2,500"
- Show which checking payment covers which CC statement

---

#### Epic 7: Category-Level Spending Analysis
**Deliverables:**
- Category assignment for credit card transactions
- Auto-categorization engine (now operating on CC transactions)
- Category hierarchy (Groceries, Gas, Dining, Shopping, etc.)
- Breakdown view: "$2,500 Chase payment split across categories"

**Key Files to Create:**
- `src/categorization/rule_engine.py` - Pattern matching for categories
- `src/categorization/category_manager.py` - CRUD for categories/rules
- `pages/05_category_breakdown.py` - Show category spending details
- `config/default_categories.yaml` - Full category hierarchy

**Success Criteria:**
- Categorize CC transactions: "WHOLE FOODS" → Groceries
- Show: "Chase CC $2,500: Groceries $600, Gas $200, Dining $400, Shopping $1,300"
- User can edit categories and system learns

---

#### Epic 8: Budget Suggestions (Phase 2)
**Deliverables:**
- Historical spending analyzer (now with category detail from CC statements)
- Budget suggestion algorithm per category
- Budget tracking and progress visualization

**Key Files to Create:**
- `src/budgets/analyzer.py` - Analyze historical spending by category
- `src/budgets/suggester.py` - Suggest budgets based on 3-6 month averages
- `pages/06_budgets.py` - Budget setup and tracking UI

**Success Criteria:**
- Suggest: "Groceries: $620/month (based on 6-month avg of $587)"
- Track progress: "Groceries: $450/$620 used (73%)"
- Alert when approaching limit

---

#### Epic 9: Email Monitoring (Future Enhancement)
**Deliverables:**
- Email monitoring for transaction alerts and e-statements
- Auto-import when new statements arrive
- Real-time balance tracking

**Key Files to Create:**
- `src/email/imap_client.py` - Email monitoring
- `src/email/parsers.py` - Parse emails for transactions

**Success Criteria:**
- Monitor email for statement PDFs
- Auto-import new statements
- Parse transaction alerts

---

## Epic Sequencing & Dependencies

```
PHASE 1: Checking/Savings Analysis
Epic 1 (Foundation)
    ↓
Epic 2 (Checking/Savings Import) ← Must complete before Epic 3
    ↓
Epic 3 (Payment Detection) ← Analyzes transactions from Epic 2
    ↓
Epic 4 (Cash Flow Analytics) ← Visualizes data from Epic 2-3
    ↓
Epic 5 (Import Suggestions) ← Suggests next imports based on Epic 3

PHASE 2: Credit Card Detail
Epic 6 (CC Import) ← Extends Epic 2 parser
    ↓
Epic 7 (Category Analysis) ← Deep categorization of CC transactions
    ↓
Epic 8 (Budget Suggestions) ← Needs category data from Epic 7

PHASE 2 FUTURE:
Epic 9 (Email Monitoring) ← Independent, adds automation
```

---

## Implementation Strategy

### Incremental Development Approach
We will work through each epic together, **one at a time**, with the following workflow per epic:

1. **Review Requirements**: Discuss what the epic should accomplish
2. **Design Components**: Break down into files/modules to create
3. **Implement Core Logic**: Write the main functionality
4. **Build UI (if applicable)**: Create Streamlit pages/components
5. **Test & Validate**: Import real PDFs, verify outputs
6. **Demo & Iterate**: Review together, make adjustments

### What We'll Build Together

**Phase 1 (Epics 1-5): Checking/Savings Focus**
- **Epic 1**: Simple database for accounts, transactions, payment destinations
- **Epic 2**: Import Bank of America + TechCU checking/savings statements
- **Epic 3**: Detect WHERE money went (credit cards, PayPal, Venmo, etc.)
- **Epic 4**: Show basic cash flow: income in, money out, net savings
- **Epic 5**: Suggest which accounts to import next (ranked by amount)

**Phase 2 (Epics 6-8): Credit Card Detail**
- **Epic 6**: Import credit card statements (Chase, Amex, etc.)
- **Epic 7**: Categorize CC spending (Groceries, Gas, Dining, etc.)
- **Epic 8**: Suggest budgets per category based on history

**Two-Tier Value Proposition:**
- After Phase 1: "I see I paid $2,500 to Chase CC last month"
- After Phase 2: "That $2,500 was $600 groceries, $400 dining, $200 gas, $1,300 shopping"

### What We Won't Build (Simplicity Principles)
- ❌ Investment/stock tracking
- ❌ Bill payment scheduling or reminders
- ❌ Credit card debt tracking (assumes paid in full monthly)
- ❌ Forced manual data entry (automation first)
- ❌ Multi-user authentication (single-user localhost app)
- ❌ Cloud sync or mobile apps (desktop-focused)

---

## File Structure Overview

```
budgeting/
├── app.py                          # Streamlit homepage
├── requirements.txt                # Python dependencies
├── .env                            # Configuration
├── README.md
│
├── data/
│   ├── budgeting.db               # SQLite database
│   └── backups/
│
├── statements/                    # Your existing PDFs
│   ├── BankOfAmerica-Statement/
│   └── TechCu-Statement/
│
├── config/
│   ├── bank_parsers.yaml          # Bank-specific parsing config
│   ├── default_categories.yaml    # Seed categories
│   └── categorization_rules.yaml  # Initial auto-cat rules
│
├── src/
│   ├── database/                  # Epic 1
│   ├── parsers/                   # Epic 2
│   ├── categorization/            # Epic 3
│   ├── budgets/                   # Epic 4
│   ├── reconciliation/            # Epic 5
│   ├── ui/                        # Epic 6
│   ├── utils/
│   └── email/                     # Epic 7 (Phase 2)
│
├── pages/                         # Streamlit multi-page app
│   ├── 01_import.py               # Epic 2
│   ├── 02_transactions.py         # Epic 3
│   ├── 03_categorize.py           # Epic 3
│   ├── 04_budgets.py              # Epic 4
│   ├── 05_reconcile.py            # Epic 5
│   └── 06_analytics.py            # Epic 6
│
├── scripts/
│   ├── setup_db.py                # Epic 1
│   ├── seed_categories.py         # Epic 1
│   └── import_statements.py       # CLI bulk import (Epic 2)
│
└── tests/
    ├── test_parsers/
    ├── test_categorization/
    └── fixtures/
```

---

## Testing & Validation Strategy

### Phase 1 Testing (Epics 1-5)
Each epic will be tested with real BOA + TechCU checking/savings data:

**Epic 1 (Foundation)**:
- Create database
- Add BOA checking account manually
- Insert test transaction
- Verify schema created correctly

**Epic 2 (Checking/Savings Import)**:
- Import 1 BOA checking statement → verify transaction count matches
- Import 1 TechCU checking statement → verify all fields parsed
- Import duplicate statement → verify duplicates skipped

**Epic 3 (Payment Detection)**:
- Run payment detector on imported transactions
- Verify detects: "CHASE CREDIT CARD" as Chase CC payment
- Verify detects: "PAYPAL" as PayPal transfer
- List all payment destinations with monthly totals

**Epic 4 (Cash Flow Analytics)**:
- Import 3 months of checking statements
- Dashboard shows: total income, total expenses, net savings
- Verify chart renders income vs expenses over time
- Verify payment destination breakdown (bar chart)

**Epic 5 (Import Suggestions)**:
- View "What to Import Next" page
- Verify lists: Chase CC ($2,500/month), Venmo ($300/month), PayPal ($150/month)
- Verify sorted by amount (highest first)

### Phase 2 Testing (Epics 6-8)
**Epic 6 (CC Import)**:
- Import 1 Chase CC statement → verify all transactions extracted
- Link CC statement to checking account payment
- Verify: "$2,500 payment on 3/15 covers statement ending 2/28"

**Epic 7 (Category Analysis)**:
- Auto-categorize CC transactions: "WHOLE FOODS" → Groceries
- Manually fix miscategorized transactions
- Verify system learns from corrections
- View breakdown: "$2,500 = $600 groceries + $400 dining + ..."

**Epic 8 (Budgets)**:
- Analyze 6 months of categorized spending
- Suggest budget: "Groceries: $620/month (avg $587)"
- Track progress against budget

---

## Next Steps

### Immediate Action Items (Epic 1)
1. Set up Python virtual environment
2. Install initial dependencies (SQLAlchemy, Streamlit, pandas, pdfplumber)
3. Create project file structure
4. Design simplified database schema for Phase 1:
   - `accounts` table (name, account_type, bank, last_four)
   - `transactions` table (account_id, date, description, amount, type)
   - `payment_destinations` table (name, detected_from, monthly_amount)
5. Initialize SQLite database
6. Create simple import UI

### Questions Before Starting Epic 1
1. **Account names**: What should we call your accounts in the database?
   - Example: "BOA Checking", "BOA Savings", "TechCU Checking"
2. **Starting date**: How far back should we import?
   - All history (2019-2026) or just recent (e.g., last 12 months)?
3. **Phase 1 completion goal**: What do you want to see after Phase 1?
   - Example: "I want to see exactly where my checking account money goes each month"

---

## Verification Plan

### Phase 1 Verification (After Epic 5)
We will verify the checking/savings analysis is working:

1. **Import All Checking/Savings Statements**:
   - Bulk import all BOA checking statements (90 PDFs)
   - Bulk import all TechCU checking/savings statements (11 PDFs)
   - Verify: 2+ years of deposit account data loaded

2. **Payment Detection Works**:
   - View payment destinations page
   - Verify lists all credit cards (Chase, Amex, etc.)
   - Verify lists payment services (PayPal, Venmo, Zelle)
   - Verify monthly amounts are accurate

3. **Cash Flow Dashboard Shows Insights**:
   - Homepage shows: monthly income, expenses, savings rate
   - Chart shows income vs expenses trend over time
   - Can answer: "How much do I pay to credit cards each month?"

4. **Import Suggestions Are Useful**:
   - "What to Import Next" page lists credit cards by amount
   - Shows: "Chase CC: $2,500/month → Import to see details"
   - Prioritized correctly (highest payments first)

### Phase 2 Verification (After Epic 8)
We will verify the credit card detail analysis:

1. **Import Credit Card Statements**:
   - Import Chase CC statement
   - Verify links to checking account payment
   - All CC transactions extracted

2. **Category Analysis Works**:
   - CC transactions auto-categorized
   - View breakdown: "$2,500 = $600 groceries + $400 dining + ..."
   - Can answer: "How much do I spend on groceries?"

3. **Budget Suggestions Make Sense**:
   - Suggest budgets for top 5-10 categories
   - Budgets based on historical averages
   - Can track spending vs budget

---

## Success Metrics

**Phase 1 Completion (Epics 1-5):**
- ✅ All checking/savings statements imported (100+ PDFs)
- ✅ Payment destinations detected (credit cards, PayPal, Venmo)
- ✅ Dashboard shows where money goes each month
- ✅ Can answer: "How much do I pay to Chase CC monthly?"
- ✅ Suggestions list what to import next

**Phase 2 Completion (Epics 6-8):**
- ✅ Credit card statements imported
- ✅ CC transactions categorized (Groceries, Dining, etc.)
- ✅ Can answer: "What do I spend on groceries?"
- ✅ Budget suggestions for major categories
- ✅ Track spending vs budget

**User Satisfaction:**
- ✅ Simpler than existing budgeting apps
- ✅ Two-tier approach makes sense (cash flow first, then detail)
- ✅ Answers key questions without overwhelming detail
- ✅ Automation works well (minimal manual work)
- ✅ Provides actionable insights

---

## Timeline Estimate

Based on working together incrementally:

### Phase 1: Checking/Savings Analysis
- **Epic 1** (Foundation): 1 session (2-3 hours)
- **Epic 2** (Checking/Savings Import): 2-3 sessions (4-6 hours)
- **Epic 3** (Payment Detection): 1-2 sessions (2-4 hours)
- **Epic 4** (Cash Flow Analytics): 1-2 sessions (3-4 hours)
- **Epic 5** (Import Suggestions): 1 session (2-3 hours)

**Total Phase 1**: 6-9 sessions, 13-20 hours of collaborative work

### Phase 2: Credit Card Detail
- **Epic 6** (CC Import): 2-3 sessions (4-6 hours)
- **Epic 7** (Category Analysis): 2 sessions (4-5 hours)
- **Epic 8** (Budget Suggestions): 1-2 sessions (3-4 hours)

**Total Phase 2**: 5-7 sessions, 11-15 hours of collaborative work

### Future Enhancement
- **Epic 9** (Email Monitoring): 2-3 sessions (5-7 hours)

---

**Key Benefits of Two-Tier Approach:**
- After Phase 1, you'll have immediate value: see where money goes from checking account
- Phase 1 is simpler and faster (fewer epics, clearer scope)
- Phase 2 builds naturally on Phase 1 (adds detail where you need it)
- Can pause after Phase 1 if cash flow view is sufficient
- Each phase delivers working, useful functionality

This plan focuses on incremental delivery. After Phase 1, you'll have a working tool that shows where your money goes. Phase 2 adds the detail of what you bought.
