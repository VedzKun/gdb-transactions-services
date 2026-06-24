# Transactions Service - Requirements Document

**Project**: Global Digital Bank (GDB) Microservices Architecture
**Service**: Transactions Service
**Version**: 1.0.0
**Last Updated**: December 24, 2024
**Status**: Active

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Functional Requirements](#functional-requirements)
3. [Non-Functional Requirements](#non-functional-requirements)
4. [API Requirements](#api-requirements)
5. [Database Requirements](#database-requirements)
6. [Security Requirements](#security-requirements)
7. [Performance Requirements](#performance-requirements)
8. [Availability & Reliability Requirements](#availability--reliability-requirements)
9. [Integration Requirements](#integration-requirements)
10. [Deployment Requirements](#deployment-requirements)

---

## 🎯 Executive Summary

The **Transactions Service** is a core microservice in the Global Digital Bank (GDB) ecosystem responsible for processing all financial transactions. It handles withdrawals, deposits, transfers, and comprehensive transaction logging while enforcing privilege-based transfer limits. This service acts as a transaction orchestrator, delegating account operations to the Accounts Service.

**Key Responsibilities**: 
- Process financial transactions (withdrawal, deposit, transfer)
- Enforce daily transfer limits based on account privilege
- Maintain comprehensive audit trail
- Integrate seamlessly with Accounts Service for account operations

**Service Port**: 8002
**API Version**: v1
**Technology Stack**: FastAPI, PostgreSQL, asyncpg
**Depends On**: Accounts Service (Port 8001)

---

## ✅ Functional Requirements

### FR1: Withdrawal Operations (FE010)

#### FR1.1: Process Withdrawal
**ID**: FR1.1  
**Priority**: CRITICAL  
**Status**: ACTIVE  

**Requirement**:
The system SHALL allow account holders to withdraw cash with PIN verification and proper validations.

**Input Parameters**:
- `account_number`: Account to withdraw from (integer)
- `amount`: Withdrawal amount (decimal, 2 decimal places)
- `pin`: 4-6 digit PIN for authorization
- `description`: Optional transaction description

**Validation Rules**:
1. Account must exist (verify via Accounts Service)
2. Account must be ACTIVE
3. PIN must be valid (verify via Accounts Service)
4. Amount must be positive (> 0)
5. Amount must have maximum 2 decimal places
6. Amount must not exceed ₹10,00,000
7. Amount must not exceed account balance (sufficient funds)
8. Account must not be CLOSED

**Processing Steps**:
1. Validate account existence and status via Accounts Service
2. Validate PIN format
3. Verify PIN via Accounts Service
4. Validate withdrawal amount
5. Check sufficient balance
6. Create fund_transfers record (from_account, to_account=0)
7. Debit account via Accounts Service
8. Log to transaction_logging table
9. Log to file with timestamp
10. Return transaction confirmation

**Output**:
```json
{
  "status": "SUCCESS",
  "transaction_id": <integer>,
  "account_number": <integer>,
  "amount": <float>,
  "transaction_type": "WITHDRAWAL",
  "description": "<string>",
  "new_balance": <float>,
  "transaction_date": "<ISO-8601 timestamp>"
}
```

**Error Handling**:
- Account not found → Return 404 with error code `ACCOUNT_NOT_FOUND`
- Account inactive → Return 400 with error code `ACCOUNT_NOT_ACTIVE`
- Invalid PIN → Return 401 with error code `INVALID_PIN`
- Insufficient funds → Return 400 with error code `INSUFFICIENT_FUNDS`
- Invalid amount → Return 400 with error code `INVALID_AMOUNT`
- Account Service down → Return 503 with error code `SERVICE_UNAVAILABLE`
- Database error → Return 500 with error code `WITHDRAWAL_FAILED`

**HTTP Endpoint**:
```
POST /api/v1/withdrawals
Content-Type: application/json
```

**Query Parameters**:
```
?account_number=<int>&amount=<float>&pin=<string>&description=<string>
```

---

### FR2: Deposit Operations (FE011)

#### FR2.1: Process Deposit
**ID**: FR2.1  
**Priority**: CRITICAL  
**Status**: ACTIVE  

**Requirement**:
The system SHALL allow deposits to accounts without PIN verification.

**Input Parameters**:
- `account_number`: Account to deposit to (integer)
- `amount`: Deposit amount (decimal, 2 decimal places)
- `description`: Optional transaction description

**Validation Rules**:
1. Account must exist (verify via Accounts Service)
2. Account must be ACTIVE
3. Amount must be positive (> 0)
4. Amount must have maximum 2 decimal places
5. Amount must not exceed ₹99,99,99,999.99
6. Resulting balance must not exceed ₹99,99,99,999.99
7. Account must not be CLOSED

**Processing Steps**:
1. Validate account existence and status via Accounts Service
2. Validate deposit amount
3. Create fund_transfers record (from_account=0, to_account)
4. Credit account via Accounts Service
5. Log to transaction_logging table
6. Log to file with timestamp
7. Return transaction confirmation

**Output**:
```json
{
  "status": "SUCCESS",
  "transaction_id": <integer>,
  "account_number": <integer>,
  "amount": <float>,
  "transaction_type": "DEPOSIT",
  "description": "<string>",
  "new_balance": <float>,
  "transaction_date": "<ISO-8601 timestamp>"
}
```

**Error Handling**:
- Account not found → Return 404 with error code `ACCOUNT_NOT_FOUND`
- Account inactive → Return 400 with error code `ACCOUNT_NOT_ACTIVE`
- Invalid amount → Return 400 with error code `INVALID_AMOUNT`
- Balance overflow → Return 400 with error code `BALANCE_OVERFLOW`
- Account Service down → Return 503 with error code `SERVICE_UNAVAILABLE`
- Database error → Return 500 with error code `DEPOSIT_FAILED`

**HTTP Endpoint**:
```
POST /api/v1/deposits
Content-Type: application/json
```

**Query Parameters**:
```
?account_number=<int>&amount=<float>&description=<string>
```

---

### FR3: Transfer Operations (FE012)

#### FR3.1: Process Fund Transfer
**ID**: FR3.1  
**Priority**: CRITICAL  
**Status**: ACTIVE  

**Requirement**:
The system SHALL transfer funds between accounts with comprehensive validations and privilege-based limits.

**Input Parameters**:
- `from_account`: Source account (integer)
- `to_account`: Destination account (integer)
- `amount`: Transfer amount (decimal, 2 decimal places)
- `pin`: 4-6 digit PIN for authorization
- `transfer_mode`: NEFT, RTGS, IMPS, UPI, CHEQUE (string)
- `description`: Optional transaction description

**Validation Rules**:
1. Both accounts must exist and be ACTIVE
2. Accounts must be different (from_account ≠ to_account)
3. PIN must be valid for source account
4. Amount must be positive and > 0
5. Amount must have maximum 2 decimal places
6. Amount must not exceed source account balance
7. Amount must not exceed daily transfer limit based on privilege
8. Daily transaction count must not be exceeded

**Transfer Modes**:
- **NEFT**: National Electronic Funds Transfer
- **RTGS**: Real Time Gross Settlement
- **IMPS**: Immediate Payment Service
- **UPI**: Unified Payments Interface
- **CHEQUE**: Cheque-based transfer

**Processing Steps**:
1. Validate both accounts exist and are ACTIVE
2. Ensure accounts are different
3. Verify PIN for source account
4. Validate transfer amount
5. Check source account balance
6. Check privilege-based daily limits
7. Check daily transaction count limit
8. Create fund_transfers record
9. Debit source account via Accounts Service
10. Credit destination account via Accounts Service
11. Log to transaction_logging (both accounts)
12. Log to file with timestamp
13. Return transfer confirmation

**Output**:
```json
{
  "status": "SUCCESS",
  "transaction_id": <integer>,
  "from_account": <integer>,
  "to_account": <integer>,
  "amount": <float>,
  "transfer_mode": "<NEFT|RTGS|IMPS|UPI|CHEQUE>",
  "description": "<string>",
  "from_account_new_balance": <float>,
  "to_account_new_balance": <float>,
  "transaction_date": "<ISO-8601 timestamp>"
}
```

**Error Handling**:
- Account not found → Return 404 with error code `ACCOUNT_NOT_FOUND`
- Account inactive → Return 400 with error code `ACCOUNT_NOT_ACTIVE`
- Same account transfer → Return 400 with error code `SAME_ACCOUNT_TRANSFER`
- Invalid PIN → Return 401 with error code `INVALID_PIN`
- Insufficient funds → Return 400 with error code `INSUFFICIENT_FUNDS`
- Limit exceeded → Return 400 with error code `TRANSFER_LIMIT_EXCEEDED`
- Transaction count exceeded → Return 400 with error code `DAILY_TRANSACTION_COUNT_EXCEEDED`
- Invalid amount → Return 400 with error code `INVALID_AMOUNT`
- Service down → Return 503 with error code `SERVICE_UNAVAILABLE`
- Database error → Return 500 with error code `TRANSFER_FAILED`

**HTTP Endpoint**:
```
POST /api/v1/transfers
Content-Type: application/json
```

**Query Parameters**:
```
?from_account=<int>&to_account=<int>&amount=<float>&pin=<string>&transfer_mode=<string>&description=<string>
```

---

### FR4: Transfer Limits Management (FE013, FE014)

#### FR4.1: Get Transfer Limits
**ID**: FR4.1  
**Priority**: HIGH  
**Status**: ACTIVE  

**Requirement**:
The system SHALL retrieve transfer limit information for an account based on privilege level.

**Input Parameters**:
- `account_number`: Account number (query parameter)

**Processing**:
1. Validate account exists via Accounts Service
2. Get account privilege level
3. Fetch transfer limit rule for privilege
4. Calculate daily used amount
5. Calculate daily remaining amount
6. Calculate daily transaction count
7. Calculate transactions remaining
8. Return limit details

**Output**:
```json
{
  "account_number": <integer>,
  "privilege": "<SILVER|GOLD|PREMIUM>",
  "daily_limit": <float>,
  "daily_used": <float>,
  "daily_remaining": <float>,
  "transaction_limit": <integer>,
  "transactions_today": <integer>,
  "transactions_remaining": <integer>
}
```

**Transfer Limit Rules**:
| Privilege | Daily Limit | Daily Txn Limit |
|---|---|---|
| SILVER | ₹50,000 | 10 |
| GOLD | ₹50,000 | 50 |
| PREMIUM | ₹1,00,000 | 100 |

**Error Handling**:
- Account not found → Return 404 with error code `ACCOUNT_NOT_FOUND`
- No limit rule for privilege → Return 400 with error code `TRANSFER_LIMIT_NOT_FOUND`
- Database error → Return 500 with error code `INTERNAL_ERROR`

**HTTP Endpoint**:
```
GET /api/v1/transfer-limits?account_number=<integer>
```

---

#### FR4.2: Get All Transfer Rules
**ID**: FR4.2  
**Priority**: MEDIUM  
**Status**: ACTIVE  

**Requirement**:
The system SHALL provide endpoint to retrieve all transfer limit rules (admin use).

**Output**:
```json
{
  "rules": [
    {
      "privilege": "SILVER",
      "daily_limit": 50000.00,
      "transaction_limit": 10
    },
    {
      "privilege": "GOLD",
      "daily_limit": 50000.00,
      "transaction_limit": 50
    },
    {
      "privilege": "PREMIUM",
      "daily_limit": 100000.00,
      "transaction_limit": 100
    }
  ]
}
```

**HTTP Endpoint**:
```
GET /api/v1/transfer-limits/rules
```

---

### FR5: Transaction Logging (FE015)

#### FR5.1: Get Transaction History
**ID**: FR5.1  
**Priority**: HIGH  
**Status**: ACTIVE  

**Requirement**:
The system SHALL provide transaction history for an account.

**Input Parameters**:
- `account_number`: Account number (query parameter)
- `limit`: Maximum records to return (default 100, optional)
- `offset`: Pagination offset (default 0, optional)

**Processing**:
1. Validate account exists
2. Query transaction_logging table for account
3. Order by creation date descending
4. Apply limit and offset for pagination
5. Return transaction details

**Output**:
```json
{
  "account_number": <integer>,
  "total_transactions": <integer>,
  "transactions": [
    {
      "id": <integer>,
      "account_number": <integer>,
      "amount": <float>,
      "transaction_type": "<WITHDRAWAL|DEPOSIT|TRANSFER>",
      "reference_id": <integer>,
      "description": "<string>",
      "created_at": "<ISO-8601 timestamp>"
    }
  ]
}
```

**Error Handling**:
- Account not found → Return 404 with error code `ACCOUNT_NOT_FOUND`
- Invalid parameters → Return 422 with validation error
- Database error → Return 500 with error code `INTERNAL_ERROR`

**HTTP Endpoint**:
```
GET /api/v1/transaction-logs?account_number=<integer>&limit=100&offset=0
```

---

#### FR5.2: Get Transaction by ID
**ID**: FR5.2  
**Priority**: MEDIUM  
**Status**: ACTIVE  

**Requirement**:
The system SHALL retrieve a specific transaction by ID.

**Input Parameters**:
- `transaction_id`: Transaction ID (path parameter)

**Output**:
```json
{
  "id": <integer>,
  "account_number": <integer>,
  "amount": <float>,
  "transaction_type": "<WITHDRAWAL|DEPOSIT|TRANSFER>",
  "reference_id": <integer>,
  "description": "<string>",
  "created_at": "<ISO-8601 timestamp>"
}
```

**Error Handling**:
- Transaction not found → Return 404 with error code `TRANSACTION_NOT_FOUND`
- Database error → Return 500 with error code `INTERNAL_ERROR`

**HTTP Endpoint**:
```
GET /api/v1/transaction-logs/{transaction_id}
```

---

## 🔧 Non-Functional Requirements

### NFR1: Performance Requirements

**NFR1.1: Response Time**
- Withdrawal processing: < 500ms (95th percentile)
- Deposit processing: < 300ms (95th percentile)
- Transfer processing: < 800ms (95th percentile)
- Transfer limit query: < 100ms (95th percentile)
- Transaction log query: < 200ms (95th percentile)

**NFR1.2: Throughput**
- Minimum 500 requests per second (RPS)
- Minimum 250 concurrent users
- Support for 100 simultaneous transfers

**NFR1.3: Database Performance**
- Database queries must complete in < 50ms
- Connection pool must handle 20 concurrent connections
- Query optimization required for daily usage calculations

---

### NFR2: Scalability Requirements

**NFR2.1: Horizontal Scalability**
- Service must support running multiple instances (min 3, max 10)
- Stateless design for instance independence
- Load balancing support

**NFR2.2: Data Scalability**
- Support for 1 million+ transactions
- Support for 1 million+ daily transfer usage records
- Efficient indexing on frequently queried columns
- Archive old transactions after 1 year

---

### NFR3: Reliability Requirements

**NFR3.1: Availability**
- Service availability: 99.9% (four nines)
- Maximum planned downtime: 43 minutes/month
- Zero-downtime deployments support

**NFR3.2: Data Consistency**
- ACID compliance for all transaction operations
- Transaction support for multi-step operations
- Atomic debit/credit operations
- No partial transactions (all-or-nothing semantics)
- Consistent balance reporting across all queries

**NFR3.3: Error Recovery**
- Automatic retry logic for transient failures
- Exponential backoff for retries
- Circuit breaker for Accounts Service integration
- Graceful degradation for service dependencies

---

### NFR4: Maintainability Requirements

**NFR4.1: Code Quality**
- Code coverage: minimum 85%
- All public methods documented with docstrings
- Type hints for all function parameters and returns

**NFR4.2: Logging**
- Structured JSON logging for all operations
- Log levels: DEBUG, INFO, WARNING, ERROR
- Transaction audit log per day
- Separate log files for different log levels

**NFR4.3: Monitoring**
- Health check endpoint: `/health`
- Readiness check: `/ready`
- Metrics endpoint for Prometheus integration
- Request/response logging with request IDs

---

### NFR5: Security Requirements

**NFR5.1: PIN Handling**
- PIN never stored locally
- PIN verification delegated to Accounts Service
- PIN validation via secure channel (HTTPS)
- No PIN in logs or error messages

**NFR5.2: Data Protection**
- Encryption in transit (HTTPS/TLS 1.2+)
- Amount fields as NUMERIC(15,2) in DB
- Transaction immutability (no updates, only inserts)
- PII (Personally Identifiable Information) protection

**NFR5.3: Access Control**
- Service-to-service authentication (optional)
- Rate limiting on API endpoints
- Account ownership validation (implicit via Accounts Service)
- Audit trail of all operations

---

## 📡 API Requirements

### API Specification

**Base URL**: `http://<host>:8002/api/v1`

**Content Type**: `application/json`

**API Version**: v1

**Versioning Strategy**: URL-based versioning

**Response Format**: JSON with consistent error structure

---

## 💾 Database Requirements

### Database Platform
- **DBMS**: PostgreSQL 12+
- **Driver**: asyncpg
- **Connection Pooling**: Min 5, Max 20 connections

### Schema Requirements

**fund_transfers table**:
- Primary key: id (SERIAL)
- Columns: from_account, to_account, amount (NUMERIC 15,2), transfer_mode, status
- Timestamps: created_at, updated_at
- Indexes: (from_account, created_at), (to_account, created_at)

**transaction_logging table**:
- Primary key: id (SERIAL)
- Columns: account_number, amount, transaction_type, reference_id, description
- Timestamps: created_at, updated_at
- Indexes: (account_number, created_at), created_at (for archival)

**transfer_limits table**:
- Primary key: id (SERIAL)
- Unique constraint: privilege_level
- Columns: privilege_level, daily_limit (NUMERIC 15,2), transaction_limit
- Timestamps: created_at, updated_at

**daily_transfer_usage table**:
- Primary key: id (SERIAL)
- Unique constraint: (account_number, usage_date)
- Columns: account_number, usage_date (DATE), amount_used, transaction_count
- Timestamps: created_at, updated_at
- Indexes: (account_number, usage_date)

---

## 🔐 Security Requirements

### SEC1: Transaction Integrity
- All transactions are immutable (append-only audit trail)
- No updates to transaction records (only INSERT)
- Transaction amounts must be positive
- Atomic operations for debit/credit pairs

### SEC2: API Security
- CORS: Allow only known origins
- Rate limiting: 1000 requests/minute per IP
- Request validation: All inputs validated
- Response sanitization: No sensitive data in errors

### SEC3: Data Protection
- Balance calculations always use NUMERIC(15,2)
- No string concatenation for balance calculations
- Type-safe conversions throughout
- Audit trail immutability

---

## ⚡ Performance Requirements

### Latency SLAs
| Operation | Target (p95) | Limit (p99) |
|---|---|---|
| Withdrawal | 500ms | 1000ms |
| Deposit | 300ms | 600ms |
| Transfer | 800ms | 1500ms |
| Get Limits | 100ms | 200ms |
| Get History | 200ms | 400ms |

### Throughput SLAs
| Metric | Requirement |
|---|---|
| Minimum RPS | 500 |
| Concurrent Users | 250+ |
| Transfer Operations | 100 simultaneous |

---

## 📈 Availability & Reliability Requirements

### Uptime Requirements
- Target Availability: 99.9%
- Acceptable Downtime: 43 minutes/month
- RTO (Recovery Time Objective): < 5 minutes
- RPO (Recovery Point Objective): < 1 minute

### Failover Requirements
- Database replication: PostgreSQL streaming replication
- Load balancer: Active-active configuration
- Health checks: Every 10 seconds
- Circuit breaker for Accounts Service

---

## 🔗 Integration Requirements

### INT1: Accounts Service Integration (Port 8001)

**Critical Integration Points**:
- `/internal/accounts/validate`: Verify account existence and status
- `/internal/accounts/debit`: Debit account for withdrawal/transfer
- `/internal/accounts/credit`: Credit account for deposit/transfer
- `/internal/accounts/verify-pin`: Verify PIN for authorization

**Retry Logic**:
- Max 3 retries with exponential backoff
- Initial backoff: 100ms, exponential multiplier: 2
- Circuit breaker: 5 failures in 60 seconds

**Error Handling**:
- Service timeout (> 5s): Return 503
- Invalid response: Log and return 500
- Network error: Retry with backoff

### INT2: Message Format

**Request Headers**:
```
Content-Type: application/json
X-Request-ID: <uuid>
```

**Response Headers**:
```
Content-Type: application/json
X-Request-ID: <uuid>
X-RateLimit-Limit: <integer>
X-RateLimit-Remaining: <integer>
```

---

## 🚀 Deployment Requirements

### DEP1: Containerization
- Docker image: `gdb/transactions-service:latest`
- Base image: `python:3.9-slim`
- Multi-stage build: Separate build and runtime stages
- Health check: Built-in health endpoint

### DEP2: Orchestration
- Kubernetes: Deployment with 3+ replicas
- Auto-scaling: HPA with min 3, max 10 replicas
- Rolling updates: Zero-downtime deployment
- Service discovery: Kubernetes DNS

### DEP3: Infrastructure
- Persistent storage: PostgreSQL database
- Logging: ELK stack or CloudWatch
- Monitoring: Prometheus + Grafana
- CI/CD: GitHub Actions or Jenkins

### DEP4: Configuration Management
- Environment variables for configuration
- .env file support for local development
- Secrets management: Kubernetes Secrets or Vault
- Feature flags: Optional for gradual rollout

---

## 📋 Testing Requirements

### TEST1: Unit Tests
- Minimum coverage: 85%
- Test framework: pytest
- Async support: pytest-asyncio
- Mock external dependencies (Accounts Service)

### TEST2: Integration Tests
- Database integration tests
- Accounts Service API tests
- End-to-end transaction scenarios
- Error path testing
- Limit enforcement testing

### TEST3: Performance Tests
- Load testing: k6 or JMeter (500 RPS)
- Stress testing: 2x peak load
- Endurance testing: 24-hour run
- Spike testing: Sudden traffic increase

### TEST4: Data Integrity Tests
- Balance correctness: No string concatenation
- Transaction atomicity: Debit and credit both succeed or both fail
- Daily limit reset: Verify reset at midnight UTC
- Transaction immutability: No updates to transaction records

---

## 🔍 Monitoring & Observability Requirements

### MON1: Logging
- Structured JSON logging
- Log levels: DEBUG, INFO, WARNING, ERROR
- Transaction ID in all logs
- Request/response logging

### MON2: Metrics
- Prometheus metrics:
  - Request count by endpoint
  - Request duration histogram
  - Error count by type
  - Daily limit usage by privilege
  - Transaction count by type
- Grafana dashboards for visualization

### MON3: Tracing
- Distributed tracing: OpenTelemetry (optional)
- Trace IDs: X-Trace-ID header
- Trace sampling: Configurable (10% default)

### MON4: Alerting
- Alert on service down
- Alert on high error rate (> 1%)
- Alert on slow responses (p95 > 500ms)
- Alert on database connection pool exhaustion
- Alert on Accounts Service unavailability

---

## 📝 Documentation Requirements

### DOC1: API Documentation
- OpenAPI/Swagger specification
- Interactive API explorer: Swagger UI
- Auto-generated from code comments
- Updated with each release

### DOC2: Developer Documentation
- Setup guide
- Architecture diagrams
- Code examples
- Troubleshooting guide

### DOC3: Operational Documentation
- Deployment guide
- Configuration reference
- Monitoring setup
- Incident response procedures

---

## ✨ Additional Requirements

### REQ1: Audit Trail
- Log all withdrawal events
- Log all deposit events
- Log all transfer events
- Log all limit queries
- Retain audit logs for 7 years

### REQ2: Compliance
- GDPR compliance for EU users
- PII data protection
- Transaction audit trail
- Data retention policies
- Regulatory reporting support

### REQ3: Backward Compatibility
- Maintain API v1 compatibility
- Database schema versioning
- Migration scripts for updates
- Non-breaking changes in new versions

### REQ4: Daily Limit Reset
- Reset daily usage at midnight UTC
- Support for regional time zones
- Batch cleanup of old usage records
- Scheduled maintenance windows

---

## 📅 Acceptance Criteria

### Definition of Done
- ✅ All unit tests passing (coverage >= 85%)
- ✅ All integration tests passing
- ✅ API documentation complete
- ✅ Code review approved
- ✅ Performance benchmarks met
- ✅ Security audit passed
- ✅ Deployed to staging environment
- ✅ Load testing passed (500 RPS)
- ✅ Monitoring configured
- ✅ Daily limit reset working correctly
- ✅ Balance calculations verified (no string concatenation)

---

## 🎯 Success Metrics

| Metric | Target | Status |
|---|---|---|
| Service Availability | 99.9% | Active |
| API Response Time (p95) | < 500ms | Active |
| Error Rate | < 0.1% | Active |
| Code Coverage | >= 85% | Active |
| Deployment Frequency | Daily | Active |
| Mean Time to Recovery | < 5 min | Active |
| Transfer Limit Accuracy | 100% | Active |
| Transaction Atomicity | 100% | Active |

---

**Document Version**: 1.0.0  
**Last Updated**: December 24, 2024  
**Next Review**: June 24, 2025  
**Owner**: GDB Architecture Team  
**Status**: APPROVED ✅

---

## 📝 Service-Specific Notes

**Scope**: This document focuses exclusively on **Transactions Service** requirements.

**Account Service Requirements**: Separate requirements document covers Accounts Service, including:
- Account creation and management
- PIN hashing and idempotency key handling
- Account activation and status management
- These are NOT duplicated here

**Integration Points**: 
- Account operations (debit/credit) delegated to Accounts Service
- Transactions Service handles orchestration and limit enforcement
- No idempotency keys in Transactions Service (handled upstream at Accounts Service)

**Key Differentiators from Accounts Service**:
- Focus on transaction processing and orchestration
- Daily transfer limit enforcement based on privilege levels
- Transfer mode support (NEFT, RTGS, IMPS, UPI, CHEQUE)
- Transaction logging and audit trail
- Daily usage tracking and cleanup

