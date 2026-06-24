"""
Transaction Service - Repository Layer Comprehensive Tests

Tests for all repository methods with POSITIVE | NEGATIVE | EDGE cases:
- TransactionRepository
- TransactionLogRepository
- TransferLimitRepository

Author: QA Team
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from decimal import Decimal
from datetime import datetime, timedelta
import asyncpg

from app.repositories.transaction_repository import TransactionRepository
from app.repositories.transaction_log_repository import TransactionLogRepository
from app.repositories.transfer_limit_repository import TransferLimitRepository
from app.models.enums import TransactionType, TransferMode, PrivilegeLevel
from app.exceptions.transaction_exceptions import DatabaseException


# ================================================================
# FIXTURES
# ================================================================

@pytest.fixture
def mock_database():
    """Mock database connection."""
    mock_db = AsyncMock()
    return mock_db


@pytest.fixture
def mock_connection():
    """Mock database connection."""
    mock_conn = AsyncMock()
    return mock_conn


# ================================================================
# SECTION 1: TRANSACTION REPOSITORY TESTS
# ================================================================

class TestTransactionRepository:
    """Test TransactionRepository.create_transaction method."""
    
    @pytest.mark.asyncio
    async def test_create_deposit_transaction(self, mock_database):
        """POSITIVE: Create deposit transaction (from_account=0)."""
        with patch('app.repositories.transaction_repository.database', mock_database):
            mock_conn = AsyncMock()
            mock_database.get_connection = AsyncMock(return_value=mock_conn)
            mock_conn.fetchval = AsyncMock(return_value=1)
            mock_database._pool.release = AsyncMock()
            
            repo = TransactionRepository()
            transaction_id = await repo.create_transaction(
                from_account=0,
                to_account=1000,
                amount=Decimal('5000'),
                transaction_type=TransactionType.DEPOSIT,
                description="Deposit"
            )
            
            assert transaction_id == 1
            mock_conn.fetchval.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_withdrawal_transaction(self, mock_database):
        """POSITIVE: Create withdrawal transaction (to_account=0)."""
        with patch('app.repositories.transaction_repository.database', mock_database):
            mock_conn = AsyncMock()
            mock_database.get_connection = AsyncMock(return_value=mock_conn)
            mock_conn.fetchval = AsyncMock(return_value=2)
            mock_database._pool.release = AsyncMock()
            
            repo = TransactionRepository()
            transaction_id = await repo.create_transaction(
                from_account=1000,
                to_account=0,
                amount=Decimal('3000'),
                transaction_type=TransactionType.WITHDRAWAL,
                description="Withdrawal"
            )
            
            assert transaction_id == 2
    
    @pytest.mark.asyncio
    async def test_create_transfer_transaction(self, mock_database):
        """POSITIVE: Create transfer transaction (both accounts filled)."""
        with patch('app.repositories.transaction_repository.database', mock_database):
            mock_conn = AsyncMock()
            mock_database.get_connection = AsyncMock(return_value=mock_conn)
            mock_conn.fetchval = AsyncMock(return_value=3)
            mock_database._pool.release = AsyncMock()
            
            repo = TransactionRepository()
            transaction_id = await repo.create_transaction(
                from_account=1000,
                to_account=1001,
                amount=Decimal('5000'),
                transaction_type=TransactionType.TRANSFER,
                description="Transfer"
            )
            
            assert transaction_id == 3
    
    @pytest.mark.asyncio
    async def test_create_transaction_db_error(self, mock_database):
        """NEGATIVE: Database error on create."""
        with patch('app.repositories.transaction_repository.database', mock_database):
            mock_conn = AsyncMock()
            mock_database.get_connection = AsyncMock(return_value=mock_conn)
            mock_conn.fetchval = AsyncMock(
                side_effect=asyncpg.PostgresError("DB Error")
            )
            mock_database._pool.release = AsyncMock()
            
            repo = TransactionRepository()
            with pytest.raises(Exception):
                await repo.create_transaction(
                    from_account=1000,
                    to_account=1001,
                    amount=Decimal('5000'),
                    transaction_type=TransactionType.TRANSFER
                )
    
    @pytest.mark.asyncio
    async def test_create_transaction_large_amount(self, mock_database):
        """EDGE: Create transaction with very large amount."""
        with patch('app.repositories.transaction_repository.database', mock_database):
            mock_conn = AsyncMock()
            mock_database.get_connection = AsyncMock(return_value=mock_conn)
            mock_conn.fetchval = AsyncMock(return_value=999)
            mock_database._pool.release = AsyncMock()
            
            repo = TransactionRepository()
            transaction_id = await repo.create_transaction(
                from_account=1000,
                to_account=1001,
                amount=Decimal('999999999.99'),
                transaction_type=TransactionType.TRANSFER
            )
            
            assert transaction_id == 999
    
    @pytest.mark.asyncio
    async def test_create_transaction_fractional_amount(self, mock_database):
        """EDGE: Create transaction with fractional amount."""
        with patch('app.repositories.transaction_repository.database', mock_database):
            mock_conn = AsyncMock()
            mock_database.get_connection = AsyncMock(return_value=mock_conn)
            mock_conn.fetchval = AsyncMock(return_value=100)
            mock_database._pool.release = AsyncMock()
            
            repo = TransactionRepository()
            transaction_id = await repo.create_transaction(
                from_account=1000,
                to_account=1001,
                amount=Decimal('0.01'),
                transaction_type=TransactionType.TRANSFER
            )
            
            assert transaction_id == 100


# ================================================================
# SECTION 2: TRANSACTION LOG REPOSITORY TESTS
# ================================================================

class TestTransactionLogRepository:
    """Test TransactionLogRepository methods."""
    
    @pytest.mark.asyncio
    async def test_log_to_database_success(self, mock_database):
        """POSITIVE: Successfully log to database."""
        with patch('app.repositories.transaction_log_repository.database', mock_database):
            mock_conn = AsyncMock()
            mock_database.get_connection = AsyncMock(return_value=mock_conn)
            mock_conn.fetchval = AsyncMock(return_value=123)
            mock_database._pool.release = AsyncMock()
            
            repo = TransactionLogRepository()
            result = await repo.log_to_database(
                account_number=1000,
                amount=Decimal('5000'),
                transaction_type=TransactionType.TRANSFER,
                reference_id=1,
                description="Test transfer"
            )
            
            assert result is True
            mock_conn.fetchval.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_log_to_database_db_error(self, mock_database):
        """NEGATIVE: Database error on logging."""
        with patch('app.repositories.transaction_log_repository.database', mock_database):
            mock_conn = AsyncMock()
            mock_database.get_connection = AsyncMock(return_value=mock_conn)
            mock_conn.fetchval = AsyncMock(
                side_effect=asyncpg.PostgresError("DB Error")
            )
            mock_database._pool.release = AsyncMock()
            
            repo = TransactionLogRepository()
            result = await repo.log_to_database(
                account_number=1000,
                amount=Decimal('5000'),
                transaction_type=TransactionType.TRANSFER,
                reference_id=1
            )
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_get_account_logs_with_date_filter(self, mock_database):
        """POSITIVE: Get logs with date range filter."""
        with patch('app.repositories.transaction_log_repository.database', mock_database):
            mock_conn = AsyncMock()
            mock_database.get_connection = AsyncMock(return_value=mock_conn)
            
            # Mock count query
            mock_conn.fetchrow = AsyncMock(return_value={'count': 5})
            # Mock data query
            mock_conn.fetch = AsyncMock(return_value=[
                {'id': 1, 'account_number': 1000, 'amount': 1000, 'transaction_type': 'TRANSFER', 'created_at': datetime.utcnow(), 'updated_at': datetime.utcnow()},
                {'id': 2, 'account_number': 1000, 'amount': 2000, 'transaction_type': 'DEPOSIT', 'created_at': datetime.utcnow(), 'updated_at': datetime.utcnow()}
            ])
            mock_database._pool.release = AsyncMock()
            
            repo = TransactionLogRepository()
            logs, total_count = await repo.get_account_logs(
                account_number=1000,
                skip=0,
                limit=50,
                start_date=datetime.utcnow() - timedelta(days=7),
                end_date=datetime.utcnow()
            )
            
            assert len(logs) == 2
            assert total_count == 5
    
    @pytest.mark.asyncio
    async def test_get_account_logs_no_results(self, mock_database):
        """POSITIVE: Get logs when no results found."""
        with patch('app.repositories.transaction_log_repository.database', mock_database):
            mock_conn = AsyncMock()
            mock_database.get_connection = AsyncMock(return_value=mock_conn)
            mock_conn.fetchrow = AsyncMock(return_value={'count': 0})
            mock_conn.fetch = AsyncMock(return_value=[])
            mock_database._pool.release = AsyncMock()
            
            repo = TransactionLogRepository()
            logs, total_count = await repo.get_account_logs(
                account_number=9999,
                skip=0,
                limit=50
            )
            
            assert len(logs) == 0
            assert total_count == 0
    
    @pytest.mark.asyncio
    async def test_get_account_logs_pagination(self, mock_database):
        """EDGE: Get logs with pagination."""
        with patch('app.repositories.transaction_log_repository.database', mock_database):
            mock_conn = AsyncMock()
            mock_database.get_connection = AsyncMock(return_value=mock_conn)
            mock_conn.fetchrow = AsyncMock(return_value={'count': 100})
            mock_conn.fetch = AsyncMock(return_value=[
                {'id': 51, 'account_number': 1000, 'amount': 1000, 'transaction_type': 'TRANSFER', 'created_at': datetime.utcnow(), 'updated_at': datetime.utcnow()}
            ])
            mock_database._pool.release = AsyncMock()
            
            repo = TransactionLogRepository()
            logs, total_count = await repo.get_account_logs(
                account_number=1000,
                skip=50,
                limit=1
            )
            
            assert len(logs) == 1
            assert total_count == 100


# ================================================================
# SECTION 3: TRANSFER LIMIT REPOSITORY TESTS
# ================================================================

class TestTransferLimitRepository:
    """Test TransferLimitRepository methods."""
    
    @pytest.mark.asyncio
    async def test_get_transfer_rule_premium(self, mock_database):
        """POSITIVE: Get transfer rule for PREMIUM account."""
        with patch('app.repositories.transfer_limit_repository.database', mock_database):
            mock_conn = AsyncMock()
            mock_database.get_connection = AsyncMock(return_value=mock_conn)
            
            # Mock return value
            mock_conn.fetchrow = AsyncMock(return_value={
                'daily_limit': 100000,
                'per_transaction_limit': 50,
                'created_at': datetime.utcnow()
            })
            mock_database._pool.release = AsyncMock()

            repo = TransferLimitRepository()
            rule = await repo.get_transfer_rule("PREMIUM")
            
            assert rule is not None
            assert rule["daily_limit"] == 100000
            assert rule["transaction_limit"] == 50
    
    @pytest.mark.asyncio
    async def test_get_transfer_rule_gold(self, mock_database):
        """POSITIVE: Get transfer rule for GOLD account."""
        with patch('app.repositories.transfer_limit_repository.database', mock_database):
            mock_conn = AsyncMock()
            mock_database.get_connection = AsyncMock(return_value=mock_conn)
            
            mock_conn.fetchrow = AsyncMock(return_value={
                'daily_limit': 50000,
                'per_transaction_limit': 25,
                'created_at': datetime.utcnow()
            })
            mock_database._pool.release = AsyncMock()
            
            repo = TransferLimitRepository()
            rule = await repo.get_transfer_rule("GOLD")
            
            assert rule is not None
            assert rule["daily_limit"] == 50000
            assert rule["transaction_limit"] == 25
    
    @pytest.mark.asyncio
    async def test_get_transfer_rule_silver(self, mock_database):
        """POSITIVE: Get transfer rule for SILVER account."""
        with patch('app.repositories.transfer_limit_repository.database', mock_database):
            mock_conn = AsyncMock()
            mock_database.get_connection = AsyncMock(return_value=mock_conn)
            
            mock_conn.fetchrow = AsyncMock(return_value={
                'daily_limit': 25000,
                'per_transaction_limit': 10,
                'created_at': datetime.utcnow()
            })
            mock_database._pool.release = AsyncMock()

            repo = TransferLimitRepository()
            rule = await repo.get_transfer_rule("SILVER")
            
            assert rule is not None
            assert rule["daily_limit"] == 25000
            assert rule["transaction_limit"] == 10
    
    @pytest.mark.asyncio
    async def test_get_transfer_rule_invalid_privilege(self, mock_database):
        """NEGATIVE: Get rule for invalid privilege level."""
        with patch('app.repositories.transfer_limit_repository.database', mock_database):
            mock_conn = AsyncMock()
            mock_database.get_connection = AsyncMock(return_value=mock_conn)
            
            mock_conn.fetchrow = AsyncMock(return_value=None)
            mock_database._pool.release = AsyncMock()

            repo = TransferLimitRepository()
            rule = await repo.get_transfer_rule("INVALID")
            
            assert rule is None
    
    @pytest.mark.asyncio
    async def test_get_transfer_rule_case_insensitive(self, mock_database):
        """EDGE: Test case sensitivity."""
        with patch('app.repositories.transfer_limit_repository.database', mock_database):
            mock_conn = AsyncMock()
            mock_database.get_connection = AsyncMock(return_value=mock_conn)
            
            # Using side_effect for multiple calls if needed, or just return_value
            # Assuming implementations handles case logic so DB query receives normalized values 
            # OR the query logic depends on input.
            # get_transfer_rule takes privilege arg.
            mock_conn.fetchrow = AsyncMock(return_value={
                'daily_limit': 100000,
                'per_transaction_limit': 50,
                'created_at': datetime.utcnow()
            })
            mock_database._pool.release = AsyncMock()

            repo = TransferLimitRepository()
            
            # Lowercase should work
            rule = await repo.get_transfer_rule("premium")
            assert rule is not None
            
            # Uppercase should work
            rule = await repo.get_transfer_rule("PREMIUM")
            assert rule is not None
    
    @pytest.mark.asyncio
    async def test_get_daily_used_amount(self, mock_database):
        """POSITIVE: Get daily used amount for account."""
        with patch('app.repositories.transfer_limit_repository.database', mock_database):
            mock_conn = AsyncMock()
            mock_database.get_connection = AsyncMock(return_value=mock_conn)
            mock_conn.fetchrow = AsyncMock(return_value={'total': 25000})
            mock_database._pool.release = AsyncMock()
            
            repo = TransferLimitRepository()
            amount = await repo.get_daily_used_amount(account_number=1000)
            
            assert amount == Decimal('25000')
    
    @pytest.mark.asyncio
    async def test_get_daily_used_amount_no_transactions(self, mock_database):
        """POSITIVE: Get daily used amount when no transactions."""
        with patch('app.repositories.transfer_limit_repository.database', mock_database):
            mock_conn = AsyncMock()
            mock_database.get_connection = AsyncMock(return_value=mock_conn)
            mock_conn.fetchrow = AsyncMock(return_value={'total': 0})
            mock_database._pool.release = AsyncMock()
            
            repo = TransferLimitRepository()
            amount = await repo.get_daily_used_amount(account_number=9999)
            
            assert amount == Decimal('0')
    
    @pytest.mark.asyncio
    async def test_get_daily_transaction_count(self, mock_database):
        """POSITIVE: Get daily transaction count."""
        with patch('app.repositories.transfer_limit_repository.database', mock_database):
            mock_conn = AsyncMock()
            mock_database.get_connection = AsyncMock(return_value=mock_conn)
            mock_conn.fetchrow = AsyncMock(return_value={'cnt': 15})
            mock_database._pool.release = AsyncMock()
            
            repo = TransferLimitRepository()
            count = await repo.get_daily_transaction_count(account_number=1000)
            
            assert count == 15
    
    @pytest.mark.asyncio
    async def test_get_daily_transaction_count_no_transactions(self, mock_database):
        """POSITIVE: Get transaction count when no transactions."""
        with patch('app.repositories.transfer_limit_repository.database', mock_database):
            mock_conn = AsyncMock()
            mock_database.get_connection = AsyncMock(return_value=mock_conn)
            mock_conn.fetchrow = AsyncMock(return_value={'cnt': 0})
            mock_database._pool.release = AsyncMock()
            
            repo = TransferLimitRepository()
            count = await repo.get_daily_transaction_count(account_number=9999)
            
            assert count == 0
    
    @pytest.mark.asyncio
    async def test_get_daily_amounts_db_error(self, mock_database):
        """NEGATIVE: Handle database error gracefully."""
        with patch('app.repositories.transfer_limit_repository.database', mock_database):
            mock_conn = AsyncMock()
            mock_database.get_connection = AsyncMock(return_value=mock_conn)
            mock_conn.fetchrow = AsyncMock(
                side_effect=asyncpg.PostgresError("DB Error")
            )
            mock_database._pool.release = AsyncMock()
            
            repo = TransferLimitRepository()
            amount = await repo.get_daily_used_amount(account_number=1000)
            
            # Should return 0 on error
            assert amount == Decimal('0')


# ================================================================
# TEST EXECUTION
# ================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
