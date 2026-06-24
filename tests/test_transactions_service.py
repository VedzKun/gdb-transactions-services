"""
Transactions Service API Tests
Tests endpoints using FastAPI app and mocked dependencies.
"""

import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from decimal import Decimal
from datetime import datetime, timedelta
from jose import jwt
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models.enums import TransactionType

from app.config.settings import settings

# Must match settings because lifespan overwrites any manual set_jwt_config
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM

def create_test_token(role: str = "MANAGER", login_id: str = "TEST_USER", sub: str = "1000"):
    """Create a valid JWT token for testing with specific role."""
    payload = {
        "sub": sub,
        "login_id": login_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@pytest.fixture
def mock_db():
    """Robust mock for database across all repositories."""
    mock_db_obj = MagicMock()
    mock_conn = AsyncMock()
    
    # Default success behaviors
    mock_conn.fetchval.return_value = 123
    mock_conn.fetchrow.return_value = None
    mock_conn.execute.return_value = "DONE"
    mock_conn.fetch.return_value = []
    
    # Return the SAME connection mock by default for each test
    mock_db_obj.get_connection = AsyncMock(return_value=mock_conn)
    
    mock_pool = MagicMock()
    mock_pool.release = AsyncMock()
    mock_db_obj._pool = mock_pool

    targets = [
        "app.repositories.transaction_log_repository.database",
        "app.repositories.transfer_limit_repository.database",
        "app.repositories.transaction_repository.database"
    ]
    
    with patch(targets[0], mock_db_obj), \
         patch(targets[1], mock_db_obj), \
         patch(targets[2], mock_db_obj):
        yield mock_db_obj, mock_conn

@pytest.fixture(autouse=True)
def mock_auth():
    """Bypass JWT signature verification for tests."""
    with patch("security.jwt_validation.JWTValidator.validate_token") as mock:
        yield mock

@pytest.fixture
def manager_headers():
    token = create_test_token(role="MANAGER")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_headers():
    token = create_test_token(role="ADMIN")
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
class TestTransactionsService:
    """Test suite for Transactions Service API"""

    BASE_URL = "/api/v1"

    async def test_positive_deposit(self, mock_db, manager_headers, mock_auth):
        """POSITIVE: Deposit with valid amount"""
        db_obj, mock_conn = mock_db
        mock_auth.return_value = {"role": "MANAGER", "login_id": "TEST", "sub": "1000"}
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with patch("app.services.deposit_service.account_service_client") as mock_client:
                mock_client.validate_account = AsyncMock(return_value={"id": 1003, "balance": 5000, "status": "ACTIVE", "name": "John Doe"})
                mock_client.credit_account = AsyncMock(return_value={"new_balance": 6000})
                
                response = await client.post(
                    f"{self.BASE_URL}/deposits",
                    headers=manager_headers,
                    params={"account_number": 1003, "amount": 1000}
                )
                
                assert response.status_code == 201
                data = response.json()
                assert data["status"] == "SUCCESS"
                assert data["new_balance"] == 6000.0

    async def test_negative_deposit_no_auth(self):
        """NEGATIVE: Deposit without auth token"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"{self.BASE_URL}/deposits",
                params={"account_number": 1003, "amount": 1000}
            )
            assert response.status_code == 401

    async def test_negative_deposit_nonexistent_account(self, mock_db, manager_headers, mock_auth):
        """NEGATIVE: Deposit to non-existent account"""
        db_obj, mock_conn = mock_db
        mock_auth.return_value = {"role": "MANAGER", "login_id": "TEST", "sub": "1000"}
        from app.exceptions.transaction_exceptions import AccountNotFoundException
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with patch("app.services.deposit_service.account_service_client") as mock_client:
                mock_client.validate_account = AsyncMock(side_effect=AccountNotFoundException("Account not found"))
                
                response = await client.post(
                    f"{self.BASE_URL}/deposits",
                    headers=manager_headers,
                    params={"account_number": 9999, "amount": 1000}
                )
                assert response.status_code == 404

    async def test_negative_deposit_invalid_amount(self, mock_db, manager_headers, mock_auth):
        """NEGATIVE: Deposit with invalid amount"""
        db_obj, mock_conn = mock_db
        mock_auth.return_value = {"role": "MANAGER", "login_id": "TEST", "sub": "1000"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with patch("app.services.deposit_service.account_service_client") as mock_client:
                mock_client.validate_account = AsyncMock(return_value={"id": 1003, "balance": 5000, "status": "ACTIVE"})
                
                response = await client.post(
                    f"{self.BASE_URL}/deposits",
                    headers=manager_headers,
                    params={"account_number": 1003, "amount": -1000}
                )
                assert response.status_code == 400

    async def test_positive_withdraw_correct_pin(self, mock_db, manager_headers, mock_auth):
        """POSITIVE: Withdraw with correct PIN"""
        db_obj, mock_conn = mock_db
        mock_auth.return_value = {"role": "MANAGER", "login_id": "TEST", "sub": "1000"}
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with patch("app.services.withdraw_service.account_service_client") as mock_client:
                mock_client.validate_account = AsyncMock(return_value={"id": 1003, "balance": 5000, "status": "ACTIVE"})
                mock_client.verify_pin = AsyncMock(return_value=True)
                mock_client.debit_account = AsyncMock(return_value={"new_balance": 4500})
                
                response = await client.post(
                    f"{self.BASE_URL}/withdrawals",
                    headers=manager_headers,
                    params={"account_number": 1003, "amount": 500, "pin": "9640"}
                )
                assert response.status_code == 201
                assert response.json()["new_balance"] == 4500.0

    async def test_negative_withdraw_wrong_pin(self, mock_db, manager_headers, mock_auth):
        """NEGATIVE: Withdraw with wrong PIN"""
        db_obj, mock_conn = mock_db
        mock_auth.return_value = {"role": "MANAGER", "login_id": "TEST", "sub": "1000"}
        from app.exceptions.transaction_exceptions import InvalidPINException
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with patch("app.services.withdraw_service.account_service_client") as mock_client:
                mock_client.validate_account = AsyncMock(return_value={"id": 1003, "balance": 5000, "status": "ACTIVE"})
                mock_client.verify_pin = AsyncMock(side_effect=InvalidPINException("Invalid PIN"))

                response = await client.post(
                    f"{self.BASE_URL}/withdrawals",
                    headers=manager_headers,
                    params={"account_number": 1003, "amount": 500, "pin": "0000"}
                )
                assert response.status_code == 401

    async def test_positive_transfer_valid(self, mock_db, manager_headers, mock_auth):
        """POSITIVE: Transfer between valid accounts"""
        db_obj, mock_conn = mock_db
        mock_auth.return_value = {"role": "MANAGER", "login_id": "TEST", "sub": "1000"}
        
        # Sequentially mocked responses for limits and count
        mock_conn.fetchrow.side_effect = [
            {"total": 0}, # get_daily_used_amount (Decimal(0))
            {"cnt": 0},   # get_daily_transaction_count (0)
            {             # get_transfer_rule
                'daily_limit': 100000.0,
                'per_transaction_limit': 50000.0,
                'created_at': datetime.utcnow()
            }
        ]
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with patch("app.services.transfer_service.account_service_client") as mock_client:
                mock_client.validate_account = AsyncMock(side_effect=[
                    {"id": 1003, "balance": 5000, "status": "ACTIVE", "privilege": "GOLD"},
                    {"id": 1004, "balance": 1000, "status": "ACTIVE", "privilege": "SILVER"}
                ])
                mock_client.verify_pin = AsyncMock(return_value=True)
                mock_client.debit_account = AsyncMock(return_value={"new_balance": 4500})
                mock_client.credit_account = AsyncMock(return_value={"new_balance": 1500})
                
                # Comprehensive Payment Gateway mock
                with patch("app.services.transfer_service.payment_gateway_client") as mock_gw:
                    mock_gw.validate_payment = AsyncMock(return_value=True)
                    mock_gw.process_payment = AsyncMock(return_value={"status": "SUCCESS", "gateway_id": "GW123"})
                    
                    response = await client.post(
                        f"{self.BASE_URL}/transfers",
                        headers=manager_headers,
                        params={
                            "from_account": 1003,
                            "to_account": 1004,
                            "amount": 500,
                            "pin": "9640"
                        }
                    )
                    assert response.status_code == 201

    async def test_positive_get_transaction_logs(self, mock_db, admin_headers, mock_auth):
        """POSITIVE: Get transaction logs"""
        db_obj, mock_conn = mock_db
        mock_auth.return_value = {"role": "ADMIN", "login_id": "TEST", "sub": "1000"}
        
        mock_conn.fetchrow.return_value = {'count': 2}
        mock_conn.fetch.return_value = [
            {'id': 1, 'account_number': 1003, 'amount': 1000, 'transaction_type': 'DEPOSIT', 'created_at': datetime.utcnow()},
            {'id': 2, 'account_number': 1003, 'amount': 200, 'transaction_type': 'WITHDRAWAL', 'created_at': datetime.utcnow()}
        ]
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with patch("app.services.transaction_log_service.account_service_client") as mock_client:
                mock_client.validate_account = AsyncMock(return_value={"id": 1003, "status": "ACTIVE"})
                
                response = await client.get(
                    f"{self.BASE_URL}/transaction-logs/1003",
                    headers=admin_headers
                )
                assert response.status_code == 200
                data = response.json()
                assert "logs" in data
                assert len(data["logs"]) == 2

    async def test_positive_get_transfer_limits(self, mock_db, admin_headers, mock_auth):
        """POSITIVE: Get transfer limits"""
        db_obj, mock_conn = mock_db
        mock_auth.return_value = {"role": "ADMIN", "login_id": "TEST", "sub": "1000"}
        
        mock_conn.fetchrow.return_value = {
            'daily_limit': 50000.0, 
            'per_transaction_limit': 25000.0,
            'created_at': datetime.utcnow()
        }
        mock_conn.fetchval.return_value = 0 # used today
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with patch("app.services.transfer_limit_service.account_service_client") as mock_client:
                mock_client.validate_account = AsyncMock(return_value={"id": 1003, "balance": 5000, "privilege": "GOLD"})
                mock_client.get_account_privilege = AsyncMock(return_value="GOLD")
                
                response = await client.get(
                    f"{self.BASE_URL}/transfer-limits/1003",
                    headers=admin_headers
                )
                assert response.status_code == 200
                data = response.json()
                assert data["privilege"] == "GOLD"
                assert data["daily_limit"] == 50000.0

