# Transactions Service - Global Digital Bank (GDB)

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Requirements](#requirements)
4. [Features](#features)
5. [Installation & Setup](#installation--setup)
6. [Configuration](#configuration)
7. [API Endpoints](#api-endpoints)
8. [Database Schema](#database-schema)
9. [Data Models](#data-models)
10. [Error Handling](#error-handling)
11. [Testing](#testing)
12. [Deployment](#deployment)

---

## 📌 Overview

The **Transactions Service** is a core microservice within the Global Digital Bank (GDB) ecosystem, responsible for processing all financial transactions. It provides comprehensive transaction management including:

- **Withdrawals**: Withdraw funds from accounts with PIN verification
- **Deposits**: Deposit funds to accounts
- **Transfers**: Transfer funds between accounts with privilege-based limits
- **Transfer Limits**: Manage and track daily transfer limits by privilege level
- **Transaction Logging**: Comprehensive audit trail of all transactions
- **Account Integration**: Seamless integration with Accounts Service

**Service Port**: `8002`
**API Prefix**: `/api/v1`
**Key Dependencies**: Accounts Service (8001), PostgreSQL

---

## 🏗️ Architecture

### System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT / API GATEWAY                     │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────▼────┐  ┌────▼────┐  ┌───▼──────┐
   │ Accounts │  │  Trx    │  │  Users   │
   │ Service  │  │ Service │  │ Service  │
   │ (8001)   │  │ (8002)  │  │ (8003)   │
   └────┬────┘  └────┬────┘  └───┬──────┘
        │            │            │
   ┌────▼────────────▼────────────▼────┐
   │      PostgreSQL Database           │
   │  ┌─────────────────────────────┐   │
   │  │  accounts_db                │   │
   │  │  transactions_db            │   │
   │  │  users_db                   │   │
   │  └─────────────────────────────┘   │
   └────────────────────────────────────┘
```

### Microservice Architecture - Transactions Service

```
┌──────────────────────────────────────────────────────────────────┐
│                   TRANSACTIONS SERVICE (8002)                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ 🌐 API Layer (FastAPI)                                      │  │
│  │  ├─ POST   /api/v1/withdrawals              (Withdraw)      │  │
│  │  ├─ POST   /api/v1/deposits                 (Deposit)       │  │
│  │  ├─ POST   /api/v1/transfers                (Transfer)      │  │
│  │  ├─ GET    /api/v1/transfer-limits          (Get Limits)    │  │
│  │  └─ GET    /api/v1/transaction-logs         (Get Logs)      │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              │                                     │
│  ┌───────────────────────────▼────────────────────────────────┐  │
│  │ 🔧 Service Layer (Business Logic)                           │  │
│  │  ├─ WithdrawService (withdraw_service.py)                  │  │
│  │  │  └─ process_withdraw()                                  │  │
│  │  │                                                          │  │
│  │  ├─ DepositService (deposit_service.py)                    │  │
│  │  │  └─ process_deposit()                                   │  │
│  │  │                                                          │  │
│  │  ├─ TransferService (transfer_service.py)                  │  │
│  │  │  └─ process_transfer()                                  │  │
│  │  │                                                          │  │
│  │  ├─ TransferLimitService (transfer_limit_service.py)       │  │
│  │  │  ├─ get_transfer_limit()                                │  │
│  │  │  └─ get_transfer_rules()                                │  │
│  │  │                                                          │  │
│  │  └─ TransactionLogService (transaction_log_service.py)     │  │
│  │     ├─ log_transaction()                                   │  │
│  │     └─ get_transaction_logs()                              │  │
│  └───────────────────────────▲────────────────────────────────┘  │
│                              │                                     │
│  ┌───────────────────────────┼────────────────────────────────┐  │
│  │ 📦 Repository Layer (Data Access)                           │  │
│  │  ├─ TransactionRepository                                  │  │
│  │  │  ├─ create_transaction()                                │  │
│  │  │  └─ get_transaction()                                   │  │
│  │  │                                                          │  │
│  │  ├─ TransferLimitRepository                                │  │
│  │  │  ├─ get_transfer_rule()                                 │  │
│  │  │  ├─ get_daily_used_amount()                             │  │
│  │  │  └─ get_daily_transaction_count()                       │  │
│  │  │                                                          │  │
│  │  └─ TransactionLogRepository                               │  │
│  │     ├─ log_to_database()                                   │  │
│  │     └─ log_to_file()                                       │  │
│  └───────────────────────────▲────────────────────────────────┘  │
│                              │                                     │
│  ┌───────────────────────────┼────────────────────────────────┐  │
│  │ 🔗 Integration Layer                                        │  │
│  │  └─ AccountServiceClient (account_service_client.py)       │  │
│  │     ├─ validate_account()                                  │  │
│  │     ├─ debit_account()                                     │  │
│  │     ├─ credit_account()                                    │  │
│  │     └─ verify_pin()                                        │  │
│  └───────────────────────────▲────────────────────────────────┘  │
│                              │                                     │
│  ┌───────────────────────────┼────────────────────────────────┐  │
│  │ ✔️ Validation Layer                                         │  │
│  │  ├─ AmountValidator                                        │  │
│  │  ├─ BalanceValidator                                       │  │
│  │  ├─ PINValidator                                           │  │
│  │  ├─ TransferValidator                                      │  │
│  │  └─ TransferLimitValidator                                 │  │
│  └───────────────────────────▲────────────────────────────────┘  │
│                              │                                     │
│  ┌───────────────────────────┼────────────────────────────────┐  │
│  │ 💾 Database Layer (asyncpg)                                 │  │
│  │  ├─ Connection Pooling                                      │  │
│  │  ├─ Transaction Management                                  │  │
│  │  └─ Query Execution                                         │  │
│  └───────────────────────────▲────────────────────────────────┘  │
│                              │                                     │
└──────────────────────────────┼──────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   PostgreSQL DB    │
                    │ (transactions_db)  │
                    └────────────────────┘
```

### Layered Architecture Details

#### 1. **API Layer** (`app/api/`)
- **Withdraw Routes** (`withdraw_routes.py`): Withdrawal endpoints
- **Deposit Routes** (`deposit_routes.py`): Deposit endpoints
- **Transfer Routes** (`transfer_routes.py`): Fund transfer endpoints
- **Transfer Limit Routes** (`transfer_limit_routes.py`): Limit management
- **Transaction Log Routes** (`transaction_log_routes.py`): Transaction history
- Framework: FastAPI with dependency injection
- CORS middleware for inter-service communication

#### 2. **Service Layer** (`app/services/`)
- **WithdrawService**: Withdrawal business logic
  - Account validation
  - PIN verification
  - Balance checks
  - Account debit
  
- **DepositService**: Deposit business logic
  - Account validation
  - Amount validation
  - Account credit
  
- **TransferService**: Transfer business logic
  - Source and destination validation
  - PIN verification
  - Limit checking
  - Debit source, credit destination
  
- **TransferLimitService**: Limit management
  - Get privilege-based limits
  - Track daily usage
  - Count daily transactions
  
- **TransactionLogService**: Logging and audit trail
  - Log to database
  - Log to file
  - Query transaction history

#### 3. **Repository Layer** (`app/repositories/`)
- **TransactionRepository**: Fund transfer records
- **TransferLimitRepository**: Limit rules and daily usage
- **TransactionLogRepository**: Transaction audit logs
- Raw SQL with asyncpg
- Type-safe database interactions

#### 4. **Integration Layer** (`app/integration/`)
- **AccountServiceClient**: HTTP client for Accounts Service
  - Validate account existence
  - Verify PIN
  - Debit/credit operations
  - Error handling and retries

#### 5. **Validation Layer** (`app/validation/`)
- **AmountValidator**: Transaction amount validation
- **BalanceValidator**: Sufficient balance checks
- **PINValidator**: PIN format validation
- **TransferValidator**: Transfer-specific validations
- **TransferLimitValidator**: Limit compliance checks

#### 6. **Models** (`app/models/`)
- **Enums**: TransactionType, TransferMode, PrivilegeLevel
- **Pydantic Models**: Request/Response validation
- Type safety with Field descriptors

#### 7. **Exception Handling** (`app/exceptions/`)
- Custom exception hierarchy
- HTTP status code mapping
- Error codes for external communication

#### 8. **Database** (`app/database/`)
- asyncpg connection pool management
- Lifecycle management (init/close)
- Query execution helpers

#### 9. **Configuration** (`app/config/`)
- **settings.py**: Environment-based configuration

---

## 📦 Requirements

### System Requirements
- **Python**: 3.9+
- **PostgreSQL**: 12.0+
- **asyncpg**: For async PostgreSQL driver
- **FastAPI**: 0.104.1+
- **uvicorn**: ASGI server
- **Accounts Service**: Must be running on port 8001

### Python Dependencies

```
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.4.2
pydantic-settings==2.0.3

# Database
asyncpg==0.29.0
sqlalchemy==2.0.23

# Security & Encryption
bcrypt==4.1.1
python-jose[cryptography]==3.3.0
cryptography==41.0.7

# HTTP Client (Inter-service communication)
httpx==0.25.1
aiohttp==3.9.1

# Utilities
python-dateutil==2.8.2
pytz==2023.3

# Logging & Monitoring
python-json-logger==2.0.7

# Development & Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.12.1
flake8==6.1.0
isort==5.13.2
mypy==1.7.1

# API Documentation
openapi-spec-validator==0.6.0

# Environment Management
python-dotenv==1.0.0
```

### Database Requirements
- PostgreSQL database with the following tables:
  - `fund_transfers`: Track transfers between accounts
  - `transaction_logging`: Audit trail of all transactions
  - `transfer_limits`: Privilege-based transfer limits
  - `daily_transfer_usage`: Track daily usage per account

---

## ✨ Features

### 1. Withdrawal Operations (FE010)
- **PIN Verification**: Secure withdrawal with PIN
- **Account Validation**: Ensure account exists and is active
- **Balance Checks**: Verify sufficient funds
- **Amount Validation**: Support amounts up to ₹10,00,000
- **Audit Trail**: Log all withdrawals
- **Real-time Response**: Immediate confirmation

### 2. Deposit Operations (FE011)
- **Account Validation**: Ensure account exists and is active
- **Amount Validation**: Support amounts up to ₹99,99,99,999.99
- **Balance Updates**: Instant credit to account
- **Transaction Recording**: Permanent transaction record
- **No PIN Required**: Deposits are allowed without authentication

### 3. Transfer Operations (FE012)
- **Dual Account Validation**: Verify both accounts
- **PIN Authentication**: Require PIN for authorization
- **Balance Verification**: Check source account balance
- **Limit Checking**: Enforce privilege-based daily limits
- **Multiple Modes**: NEFT, RTGS, IMPS, UPI, CHEQUE
- **Atomic Operations**: All-or-nothing transfers

### 4. Transfer Limits (FE013, FE014)
- **Privilege-Based Limits**: Different limits for SILVER/GOLD/PREMIUM
- **Daily Tracking**: Track daily usage and remaining limit
- **Transaction Count**: Limit transactions per day
- **Real-Time Calculation**: Show remaining limits instantly
- **Privilege Levels**:
  - **SILVER**: ₹50,000/day, 10 transactions/day
  - **GOLD**: ₹50,000/day, 50 transactions/day
  - **PREMIUM**: ₹1,00,000/day, 100 transactions/day

### 5. Transaction Logging (FE015)
- **Comprehensive Logging**: All transaction details
- **File-Based Audit**: Separate log files per day
- **Database Records**: Permanent transaction records
- **Query Support**: Retrieve transaction history by account
- **Timestamps**: Accurate transaction timing

### 6. Account Integration
- **Seamless Communication**: HTTP integration with Accounts Service
- **Retry Logic**: Automatic retries for transient failures
- **Error Propagation**: Clear error messages from both services
- **Real-Time Balance**: Always fetch current balance

---

## 🚀 Installation & Setup

### 1. Prerequisites
```bash
# Verify Python version
python --version  # Should be 3.9+

# Verify PostgreSQL
psql --version  # Should be 12+

# Ensure Accounts Service is running
curl http://localhost:8001/health
```

### 2. Clone & Navigate
```bash
cd transactions_service
```

### 3. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Setup Database
```bash
# Initialize database
python setup_db.py

# Or manually:
# 1. Create PostgreSQL database: gdb_transactions_db
# 2. Run: database_schemas/transactions_schema.sql
```

### 6. Configure Environment
```bash
# Create .env file
cp .env.example .env

# Edit .env with your settings:
DATABASE_URL=postgresql://user:password@localhost:5432/gdb_transactions_db
ACCOUNT_SERVICE_URL=http://localhost:8001
LOG_LEVEL=INFO
```

### 7. Run Application
```bash
# Development
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# Production
gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8002 app.main:app
```

### 8. Verify Service
```bash
# Health check
curl http://localhost:8002/health

# API docs
open http://localhost:8002/api/v1/docs
```

---

## ⚙️ Configuration

### Environment Variables

```env
# Application
APP_NAME=GDB-Transactions-Service
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=production

# Server
HOST=0.0.0.0
PORT=8002

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/gdb_transactions_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gdb_transactions_db
DB_USER=postgres
DB_PASSWORD=postgres

# Account Service
ACCOUNT_SERVICE_URL=http://localhost:8001

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/transactions_service.log

# API
API_PREFIX=/api/v1
```

---

## 📡 API Endpoints

### Withdrawal Operations

#### Withdraw Funds
```http
POST /api/v1/withdrawals
Content-Type: application/json

{
  "account_number": 1001,
  "amount": 5000.00,
  "pin": "1234",
  "description": "ATM Withdrawal"
}
```

**Response (201 Created)**:
```json
{
  "status": "SUCCESS",
  "transaction_id": 101,
  "account_number": 1001,
  "amount": 5000.00,
  "transaction_type": "WITHDRAWAL",
  "description": "ATM Withdrawal",
  "new_balance": 140000.00,
  "transaction_date": "2024-12-24T10:30:00"
}
```

### Deposit Operations

#### Deposit Funds
```http
POST /api/v1/deposits
Content-Type: application/json

{
  "account_number": 1001,
  "amount": 10000.00,
  "description": "Salary Credit"
}
```

**Response (201 Created)**:
```json
{
  "status": "SUCCESS",
  "transaction_id": 102,
  "account_number": 1001,
  "amount": 10000.00,
  "transaction_type": "DEPOSIT",
  "description": "Salary Credit",
  "new_balance": 150000.00,
  "transaction_date": "2024-12-24T10:35:00"
}
```

### Transfer Operations

#### Transfer Funds
```http
POST /api/v1/transfers
Content-Type: application/json

{
  "from_account": 1001,
  "to_account": 1002,
  "amount": 5000.00,
  "pin": "1234",
  "transfer_mode": "NEFT",
  "description": "Payment for services"
}
```

**Response (201 Created)**:
```json
{
  "status": "SUCCESS",
  "transaction_id": 103,
  "from_account": 1001,
  "to_account": 1002,
  "amount": 5000.00,
  "transfer_mode": "NEFT",
  "description": "Payment for services",
  "from_account_new_balance": 135000.00,
  "to_account_new_balance": 55000.00,
  "transaction_date": "2024-12-24T10:40:00"
}
```

### Transfer Limits

#### Get Transfer Limits
```http
GET /api/v1/transfer-limits?account_number=1001
```

**Response**:
```json
{
  "account_number": 1001,
  "privilege": "GOLD",
  "daily_limit": 50000.00,
  "daily_used": 5000.00,
  "daily_remaining": 45000.00,
  "transaction_limit": 50,
  "transactions_today": 1,
  "transactions_remaining": 49
}
```

### Transaction Logs

#### Get Transaction History
```http
GET /api/v1/transaction-logs?account_number=1001
```

**Response**:
```json
{
  "account_number": 1001,
  "transactions": [
    {
      "id": 101,
      "account_number": 1001,
      "amount": 5000.00,
      "transaction_type": "WITHDRAWAL",
      "reference_id": 101,
      "description": "ATM Withdrawal",
      "created_at": "2024-12-24T10:30:00"
    },
    {
      "id": 102,
      "account_number": 1001,
      "amount": 10000.00,
      "transaction_type": "DEPOSIT",
      "reference_id": 102,
      "description": "Salary Credit",
      "created_at": "2024-12-24T10:35:00"
    }
  ]
}
```

---

## 💾 Database Schema

### Fund Transfers Table
```sql
CREATE TABLE fund_transfers (
  id SERIAL PRIMARY KEY,
  from_account INT NOT NULL,
  to_account INT NOT NULL,
  amount NUMERIC(15, 2) NOT NULL,
  transfer_mode VARCHAR(20) NOT NULL,
  status VARCHAR(20) DEFAULT 'COMPLETED',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Transaction Logging Table
```sql
CREATE TABLE transaction_logging (
  id SERIAL PRIMARY KEY,
  account_number INT NOT NULL,
  amount NUMERIC(15, 2) NOT NULL,
  transaction_type VARCHAR(20) NOT NULL,
  reference_id INT,
  description VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Transfer Limits Table
```sql
CREATE TABLE transfer_limits (
  id SERIAL PRIMARY KEY,
  privilege_level VARCHAR(20) NOT NULL,
  daily_limit NUMERIC(15, 2) NOT NULL,
  transaction_limit INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Daily Transfer Usage Table
```sql
CREATE TABLE daily_transfer_usage (
  id SERIAL PRIMARY KEY,
  account_number INT NOT NULL,
  usage_date DATE NOT NULL,
  amount_used NUMERIC(15, 2) DEFAULT 0,
  transaction_count INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(account_number, usage_date)
);
```

---

## 🔍 Data Models

### Request Models

#### WithdrawRequest
```python
{
  "account_number": int,
  "amount": float (1-1000000),
  "pin": str (4-6 digits),
  "description": str (optional)
}
```

#### DepositRequest
```python
{
  "account_number": int,
  "amount": float,
  "description": str (optional)
}
```

#### TransferRequest
```python
{
  "from_account": int,
  "to_account": int,
  "amount": float,
  "pin": str (4-6 digits),
  "transfer_mode": "NEFT|RTGS|IMPS|UPI|CHEQUE",
  "description": str (optional)
}
```

### Response Models

#### TransactionResponse
```python
{
  "status": "SUCCESS|FAILED",
  "transaction_id": int,
  "account_number": int,
  "amount": float,
  "transaction_type": "WITHDRAWAL|DEPOSIT|TRANSFER",
  "new_balance": float,
  "transaction_date": datetime
}
```

---

## ⚠️ Error Handling

### Error Response Format
```json
{
  "error_code": "ERROR_CODE",
  "message": "Human-readable error message"
}
```

### Common Error Codes

| Error Code | Status | Meaning |
|---|---|---|
| `ACCOUNT_NOT_FOUND` | 404 | Account does not exist |
| `ACCOUNT_NOT_ACTIVE` | 400 | Account is not active |
| `INSUFFICIENT_FUNDS` | 400 | Balance insufficient for transaction |
| `INVALID_PIN` | 401 | PIN is invalid or incorrect |
| `INVALID_AMOUNT` | 400 | Amount is invalid |
| `TRANSFER_LIMIT_EXCEEDED` | 400 | Daily transfer limit exceeded |
| `DAILY_TRANSACTION_COUNT_EXCEEDED` | 400 | Daily transaction count exceeded |
| `SAME_ACCOUNT_TRANSFER` | 400 | Cannot transfer to same account |
| `SERVICE_UNAVAILABLE` | 503 | Accounts Service is down |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_api_endpoints.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

### Test Files
- **test_api_endpoints.py**: API endpoint tests
- **test_comprehensive.py**: Comprehensive feature tests
- **test_integration.py**: End-to-end integration tests
- **test_models_and_validators.py**: Model validation tests
- **test_repositories.py**: Data access layer tests
- **test_helpers_and_utilities.py**: Utility function tests

### Test Coverage
- ✅ 220+ automated tests
- ✅ Unit tests for all layers
- ✅ Integration tests
- ✅ Error scenario testing
- ✅ Edge case coverage

---

## 📦 Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: transactions-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: transactions-service
  template:
    metadata:
      labels:
        app: transactions-service
    spec:
      containers:
      - name: transactions-service
        image: gdb/transactions-service:latest
        ports:
        - containerPort: 8002
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: transactions-db-url
        - name: ACCOUNT_SERVICE_URL
          value: http://accounts-service:8001
        livenessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 30
          periodSeconds: 10
```

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8002/api/v1/docs
- **ReDoc**: http://localhost:8002/api/v1/redoc
- **Health Check**: http://localhost:8002/health
- **Database Schema**: `database_schemas/transactions_schema.sql`
- **Configuration Template**: `.env.example`

---

## 🤝 Contributing

### Code Style
- Use Black for formatting: `black app/`
- Use isort for imports: `isort app/`
- Run linting: `flake8 app/`

### Before Committing
```bash
black app/
isort app/
flake8 app/
pytest tests/
```

---

## 📝 License

Copyright © 2024 Global Digital Bank (GDB). All rights reserved.

---

## 📞 Support

For issues, questions, or support:
- Create an issue in the repository
- Contact: support@gdb.local
- Documentation: Check docs/ folder

---

**Last Updated**: December 24, 2024
**Version**: 1.0.0
**Maintainer**: GDB Architecture Team
