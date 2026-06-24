"""
TRANSACTION SERVICE - TEST EXECUTION & MAINTENANCE GUIDE

Quick reference for running, maintaining, and extending the comprehensive test suite.
"""

# ================================================================
# QUICK START
# ================================================================

## Installation
```bash
cd transactions_service
pip install -r requirements.txt
pip install pytest pytest-cov pytest-asyncio pytest-mock
```

## Run All Tests
```bash
pytest tests/ -v --tb=short
```

## Run with Coverage
```bash
pytest tests/ --cov=app --cov-report=html
# Open htmlcov/index.html to view coverage report
```

---

# ================================================================
# TEST FILE ORGANIZATION
# ================================================================

```
tests/
├── test_comprehensive.py    # Unit tests (100+ cases)
├── test_repositories.py     # Repository tests (130+ cases)
├── test_api_endpoints.py    # API tests (150+ cases)
├── test_integration.py      # Integration tests (120+ cases)
├── conftest.py              # Shared fixtures & configuration
└── README.md                # Test documentation
```

---

# ================================================================
# RUNNING TESTS BY LAYER
# ================================================================

## Unit Tests Only
```bash
pytest tests/test_comprehensive.py -v
# Tests: Enums, Validators, Models
# Cases: 100+
# Time: ~5 seconds
```

## Repository Tests Only
```bash
pytest tests/test_repositories.py -v
# Tests: TransactionRepository, TransactionLogRepository, TransferLimitRepository
# Cases: 130+
# Time: ~10 seconds
```

## API Tests Only
```bash
pytest tests/test_api_endpoints.py -v
# Tests: Deposits, Withdrawals, Transfers, Limits, Logs endpoints
# Cases: 150+
# Time: ~15 seconds
```

## Integration Tests Only
```bash
pytest tests/test_integration.py -v
# Tests: Multi-account workflows, daily limits, concurrent transactions
# Cases: 120+
# Time: ~20 seconds
```

---

# ================================================================
# RUNNING TESTS BY FUNCTIONALITY
# ================================================================

## Test Deposit Functionality
```bash
pytest tests/ -k "deposit" -v
```

## Test Withdrawal Functionality
```bash
pytest tests/ -k "withdraw" -v
```

## Test Transfer Functionality
```bash
pytest tests/ -k "transfer" -v
```

## Test Limit Validation
```bash
pytest tests/ -k "limit" -v
```

## Test Logging
```bash
pytest tests/ -k "log" -v
```

---

# ================================================================
# RUNNING TESTS BY TEST TYPE
# ================================================================

## Positive Tests Only (Should Pass)
```bash
pytest tests/ -v | grep "POSITIVE"
# Or with marker if implemented:
pytest tests/ -m "positive" -v
```

## Negative Tests Only (Should Fail Gracefully)
```bash
pytest tests/ -v | grep "NEGATIVE"
# Or with marker:
pytest tests/ -m "negative" -v
```

## Edge Case Tests Only
```bash
pytest tests/ -v | grep "EDGE"
# Or with marker:
pytest tests/ -m "edge" -v
```

---

# ================================================================
# COVERAGE ANALYSIS
# ================================================================

## Generate HTML Coverage Report
```bash
pytest tests/ --cov=app --cov-report=html
```

## View Coverage Report
```bash
# Windows
start htmlcov/index.html

# Linux/Mac
open htmlcov/index.html
```

## Coverage by Module
```bash
pytest tests/ --cov=app --cov-report=term-missing
```

## Minimum Coverage Threshold
```bash
pytest tests/ --cov=app --cov-fail-under=90
```

---

# ================================================================
# TEST DEBUGGING
# ================================================================

## Show Print Statements
```bash
pytest tests/test_file.py -v -s
```

## Show Full Traceback
```bash
pytest tests/test_file.py -v --tb=long
```

## Stop on First Failure
```bash
pytest tests/ -v -x
```

## Show Local Variables on Failure
```bash
pytest tests/ -v -l
```

## Run with PDB on Failure
```bash
pytest tests/ -v --pdb
# Type 'h' for help, 'n' for next, 'c' for continue
```

## Detailed output with profiling
```bash
pytest tests/test_file.py -v --durations=10
```

---

# ================================================================
# RUNNING SPECIFIC TEST CLASSES
# ================================================================

## Test Specific Class
```bash
pytest tests/test_comprehensive.py::TestAmountValidator -v
pytest tests/test_repositories.py::TestTransactionRepository -v
pytest tests/test_api_endpoints.py::TestDepositEndpoint -v
pytest tests/test_integration.py::TestMultiAccountWorkflows -v
```

## Test Specific Method
```bash
pytest tests/test_comprehensive.py::TestAmountValidator::test_valid_withdrawal_amount -v
pytest tests/test_repositories.py::TestTransactionLogRepository::test_log_to_database_success -v
pytest tests/test_api_endpoints.py::TestDepositEndpoint::test_deposit_success -v
```

---

# ================================================================
# PARALLEL TEST EXECUTION
# ================================================================

## Install pytest-xdist
```bash
pip install pytest-xdist
```

## Run Tests in Parallel
```bash
# Use 4 CPU cores
pytest tests/ -n 4 -v

# Auto-detect CPU count
pytest tests/ -n auto -v
```

---

# ================================================================
# CONTINUOUS TESTING
# ================================================================

## Watch Tests (Re-run on File Change)
```bash
pip install pytest-watch
ptw tests/ -- -v
```

## Repeat Failed Tests
```bash
pytest tests/ -v --lf    # Run last failed
pytest tests/ -v --ff    # Run failed first, then others
```

## Run N Times (For Flaky Test Detection)
```bash
pip install pytest-repeat
pytest tests/ --count=10 -v
```

---

# ================================================================
# TEST MAINTENANCE CHECKLIST
# ================================================================

### Weekly:
- [ ] Run full test suite
- [ ] Review test coverage report
- [ ] Check for any flaky tests
- [ ] Update any failing tests due to code changes

### Monthly:
- [ ] Review test organization
- [ ] Consolidate duplicate tests
- [ ] Add tests for new features
- [ ] Update test documentation

### Quarterly:
- [ ] Performance analysis
- [ ] Coverage gap analysis
- [ ] Refactor slow tests
- [ ] Update mock configurations

---

# ================================================================
# ADDING NEW TESTS
# ================================================================

## Test Template - Unit Test
```python
@pytest.mark.asyncio
async def test_new_validator_success(self):
    """POSITIVE: Test validator with valid input."""
    # Arrange
    validator = SomeValidator()
    test_input = "valid_value"
    
    # Act
    result = await validator.validate(test_input)
    
    # Assert
    assert result is True

@pytest.mark.asyncio
async def test_new_validator_invalid(self):
    """NEGATIVE: Test validator with invalid input."""
    # Arrange
    validator = SomeValidator()
    test_input = "invalid_value"
    
    # Act & Assert
    with pytest.raises(ValidationError):
        await validator.validate(test_input)

@pytest.mark.asyncio
async def test_new_validator_boundary(self):
    """EDGE: Test validator at boundary condition."""
    # Arrange
    validator = SomeValidator()
    boundary_value = 999999999.99
    
    # Act
    result = await validator.validate(boundary_value)
    
    # Assert
    assert result is True
```

## Test Template - Repository Test
```python
@pytest.mark.asyncio
async def test_new_repository_method_success(self, mock_database):
    """POSITIVE: Repository method succeeds."""
    with patch('app.repositories.module.database', mock_database):
        # Setup mocks
        mock_conn = AsyncMock()
        mock_database.get_connection = AsyncMock(return_value=mock_conn)
        mock_conn.fetchval = AsyncMock(return_value=expected_value)
        mock_database._pool.release = AsyncMock()
        
        # Execute
        repo = SomeRepository()
        result = await repo.some_method(param1, param2)
        
        # Assert
        assert result == expected_value
```

## Test Template - API Test
```python
@pytest.mark.asyncio
async def test_endpoint_success(self, client, mock_service):
    """POSITIVE: Endpoint returns success."""
    # Setup
    mock_service.some_method = AsyncMock(return_value=123)
    
    # Request
    response = client.post("/api/v1/endpoint", json={
        "param1": "value1",
        "param2": 100
    })
    
    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "success"
```

---

# ================================================================
# COMMON ISSUES & SOLUTIONS
# ================================================================

### Issue: "ModuleNotFoundError" in tests
**Solution**: 
```bash
# Ensure working directory is correct
cd transactions_service

# Install package in development mode
pip install -e .
```

### Issue: Async tests not running
**Solution**:
```bash
# Install pytest-asyncio
pip install pytest-asyncio

# Add marker to async tests
@pytest.mark.asyncio
async def test_async_function():
    ...
```

### Issue: Mock not working
**Solution**:
```python
# Use full path to patch
with patch('app.full.path.to.module.function') as mock:
    # correct path is crucial
```

### Issue: Tests timeout
**Solution**:
```bash
# Increase timeout
pytest tests/ -v --timeout=10

# Check for hanging mocks/connections
```

### Issue: Flaky tests (intermittent failures)
**Solution**:
```bash
# Run test multiple times
pytest tests/test_file.py::test_name -v --count=20

# Look for race conditions or timing issues
# Add await/async properly
# Check mock sequential return values
```

---

# ================================================================
# CI/CD INTEGRATION
# ================================================================

## GitHub Actions Example
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, "3.10", 3.11]
    
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -r requirements.txt pytest pytest-cov pytest-asyncio
      - run: pytest tests/ --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v2
        with:
          files: ./coverage.xml
```

## GitLab CI Example
```yaml
test:
  image: python:3.10
  script:
    - pip install -r requirements.txt pytest pytest-cov pytest-asyncio
    - pytest tests/ --cov=app --cov-report=term --junitxml=report.xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      junit: report.xml
```

---

# ================================================================
# PERFORMANCE OPTIMIZATION
# ================================================================

## Identify Slow Tests
```bash
pytest tests/ -v --durations=10
# Shows 10 slowest tests
```

## Profile Test Execution
```bash
pip install pytest-profiling
pytest tests/ --profile
```

## Cache Test Results
```bash
pytest tests/ --cache-show
pytest tests/ --cache-clear
```

## Reduce Mock Setup Time
```python
# Use parametrize for multiple similar tests
@pytest.mark.parametrize("input,expected", [
    ("value1", result1),
    ("value2", result2),
    ("value3", result3),
])
async def test_validator(input, expected):
    ...
```

---

# ================================================================
# TEST REPORTING
# ================================================================

## Generate JUnit XML Report
```bash
pytest tests/ --junitxml=report.xml
```

## Generate HTML Report
```bash
pip install pytest-html
pytest tests/ --html=report.html
```

## Generate Coverage Badge
```bash
pip install coverage-badge
coverage run -m pytest tests/
coverage-badge -o coverage.svg
```

## Combine Reports
```bash
pytest tests/ \
  --junitxml=report.xml \
  --html=report.html \
  --cov=app \
  --cov-report=html \
  --cov-report=xml
```

---

# ================================================================
# MAINTAINING TEST QUALITY
# ================================================================

### Best Practices:
1. ✅ One assertion per test (or closely related)
2. ✅ Clear, descriptive test names
3. ✅ Proper test organization (Arrange-Act-Assert)
4. ✅ Independent tests (no interdependencies)
5. ✅ Fast execution (< 1 second per test)
6. ✅ Comprehensive error messages
7. ✅ Don't test implementation details
8. ✅ Mock external dependencies

### Anti-Patterns to Avoid:
1. ❌ Tests that depend on execution order
2. ❌ Hidden test dependencies in fixtures
3. ❌ Over-mocking (mocking too much)
4. ❌ Under-mocking (not isolating units)
5. ❌ Flaky/timing-dependent tests
6. ❌ Tests that modify global state
7. ❌ Overly complex test logic
8. ❌ Missing edge cases

---

# ================================================================
# TEST METRICS TRACKING
# ================================================================

## Key Metrics to Monitor:
- **Test Count**: Total tests (target: 500+)
- **Pass Rate**: % of passing tests (target: 100%)
- **Code Coverage**: % of lines covered (target: >90%)
- **Execution Time**: Total test duration (target: <60 seconds)
- **Flake Rate**: % of flaky tests (target: 0%)

## Tracking Commands:
```bash
# Count tests
pytest --collect-only | grep "test session starts" -A 1

# Summary statistics
pytest tests/ -v --tb=no | tail -5

# Coverage summary
pytest tests/ --cov=app --cov-report=term-missing | grep "TOTAL"
```

---

# ================================================================
# RESOURCES
# ================================================================

## Documentation:
- pytest: https://docs.pytest.org/
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/
- unittest.mock: https://docs.python.org/3/library/unittest.mock.html
- FastAPI Testing: https://fastapi.tiangolo.com/advanced/testing-dependencies/

## Tools:
- pytest plugins: https://docs.pytest.org/en/latest/plugins.html
- coverage: https://coverage.readthedocs.io/
- hypothesis (property-based testing): https://hypothesis.readthedocs.io/

---

**Last Updated**: 2024
**Status**: Complete and Ready for Use
**Maintenance**: Quarterly review recommended

