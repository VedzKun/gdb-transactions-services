"""
Database Connection Module

Manages PostgreSQL connection pool using asyncpg.
Handles initialization, cleanup, and connection operations.
"""

import asyncpg
from typing import Optional
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """PostgreSQL connection pool manager."""

    _pool: Optional[asyncpg.Pool] = None

    @classmethod
    async def initialize(cls) -> asyncpg.Pool:
        """
        Initialize and return PostgreSQL connection pool.
        Also handles automatic database creation, schema execution, and seeding.
        
        Returns:
            asyncpg.Pool: Connection pool instance
            
        Raises:
            ConnectionError: If connection fails
        """
        if cls._pool is not None:
            return cls._pool

        # 1. Connect to postgres DB to verify/create target DB
        try:
            logger.info(f"Checking if database {settings.DB_NAME} exists...")
            temp_conn = await asyncpg.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                database="postgres"
            )
            db_exists = await temp_conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1",
                settings.DB_NAME
            )
            if not db_exists:
                logger.info(f"📦 Creating database: {settings.DB_NAME}")
                await temp_conn.execute(f"CREATE DATABASE {settings.DB_NAME}")
                logger.info(f"✅ Database created: {settings.DB_NAME}")
            else:
                logger.info(f"✅ Database already exists: {settings.DB_NAME}")
            await temp_conn.close()
        except Exception as e:
            logger.error(f"⚠️ Error verifying/creating database {settings.DB_NAME}: {e}")

        # 2. Connect pool
        try:
            cls._pool = await asyncpg.create_pool(init=set_schema_search_path, 
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                database=settings.DB_NAME,
                min_size=settings.DB_POOL_MIN_SIZE,
                max_size=settings.DB_POOL_MAX_SIZE,
                command_timeout=settings.DB_TIMEOUT,
            )
            logger.info("✅ Database connection pool initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize database pool: {str(e)}")
            raise ConnectionError(f"Database connection failed: {str(e)}")

        # 3. Check if tables exist, run schema, and seed
        try:
            from pathlib import Path
            async with cls._pool.acquire() as conn:
                limits_exists = await conn.fetchval(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = current_schema() AND table_name = 'transfer_limits')"
                )
                if not limits_exists:
                    logger.info("📋 Core table 'transfer_limits' does not exist. Running transactions_schema.sql...")
                    schema_path = Path(__file__).parent / "transactions_schema.sql"
                    if schema_path.exists():
                        with open(schema_path, "r", encoding="utf-8") as f:
                            schema_sql = f.read()
                        await conn.execute(schema_sql)
                        logger.info("✅ Schema executed successfully")
                    else:
                        logger.error(f"❌ Schema file not found at {schema_path}")
                
                # Check limits count and seed transfer limits
                limits_count = await conn.fetchval("SELECT COUNT(*) FROM transfer_limits")
                if limits_count == 0:
                    logger.info("🌱 Seeding transfer limits...")
                    await conn.execute(
                        """
                        INSERT INTO transfer_limits (privilege, daily_limit, per_transaction_limit)
                        VALUES 
                            ('PREMIUM', 100000.00, 50000.00),
                            ('GOLD', 50000.00, 25000.00),
                            ('SILVER', 25000.00, 12500.00)
                        """
                    )
                    logger.info("✅ Seeded transfer limits")

                # Check transaction logs count and seed dummy logs
                logs_count = await conn.fetchval("SELECT COUNT(*) FROM transaction_logging")
                if logs_count == 0:
                    logger.info("🌱 Seeding dummy transaction logs...")
                    
                    # Deposit to 1001 (John Doe)
                    await conn.execute(
                        """
                        INSERT INTO transaction_logging (account_number, amount, transaction_type, reference_id, description, mode, status)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        """,
                        1001, 60000.00, "DEPOSIT", None, "Initial deposit", "CASH", "SUCCESS"
                    )
                    
                    # Transfer from 1002 (Admin) to 1001 (John Doe)
                    await conn.execute(
                        """
                        INSERT INTO fund_transfers (from_account, to_account, transfer_amount, transfer_mode)
                        VALUES ($1, $2, $3, $4)
                        """,
                        1002, 1001, 10000.00, "IMPS"
                    )
                    
                    # Debit log for 1002
                    await conn.execute(
                        """
                        INSERT INTO transaction_logging (account_number, amount, transaction_type, reference_id, description, mode, status)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        """,
                        1002, 10000.00, "TRANSFER", 1, "Fund Transfer to 1001", "IMPS", "SUCCESS"
                    )
                    
                    # Credit log for 1001
                    await conn.execute(
                        """
                        INSERT INTO transaction_logging (account_number, amount, transaction_type, reference_id, description, mode, status)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        """,
                        1001, 10000.00, "TRANSFER", 1, "Fund Transfer from 1002", "IMPS", "SUCCESS"
                    )
                    logger.info("✅ Seeded dummy transaction logs")
        except Exception as e:
            logger.error(f"❌ Error during transactions schema verification/seeding: {e}")
            raise

        return cls._pool

    @classmethod
    async def close(cls) -> None:
        """
        Close database connection pool.
        """
        if cls._pool is not None:
            await cls._pool.close()
            cls._pool = None
            logger.info("✅ Database connection pool closed")

    @classmethod
    async def get_connection(cls) -> asyncpg.Connection:
        """
        Get a connection from the pool.
        
        Returns:
            asyncpg.Connection: A database connection
        """
        if cls._pool is None:
            await cls.initialize()
        return await cls._pool.acquire()

    @classmethod
    async def execute(
        cls,
        query: str,
        *args,
        fetch: bool = False,
        fetch_one: bool = False
    ) -> any:
        """
        Execute a query.
        
        Args:
            query: SQL query string
            args: Query parameters
            fetch: Return all rows
            fetch_one: Return single row
            
        Returns:
            Query result (list of dicts or single dict)
        """
        conn = await cls.get_connection()
        try:
            if fetch:
                return await conn.fetch(query, *args)
            elif fetch_one:
                return await conn.fetchrow(query, *args)
            else:
                # TODO: [M10-Bug-01] BUG: The application freezes after several transaction searches. We might be exhausting our resources here.
                return await conn.execute(query, *args)
        finally:
            # Bug (M10-Bug-01): Missing connection release in pool for specific queries.
            # If the query counts logs or queries logs, we skip the release call, leaking connection.
            await cls._pool.release(conn)

    @classmethod
    async def transaction(cls):
        """
        Get transaction context manager.
        
        Usage:
            async with database.transaction():
                # Transaction operations
        """
        conn = await cls.get_connection()
        return conn.transaction()


# CR (M10-CR-01): Batch Update Query Execution
# TODO: Implement a classmethod `execute_batch(cls, query, args_list)` to run batch queries.
# The method should:
# - Obtain a database connection from the pool using `cls.get_connection()`.
# - Use the connection's `executemany(query, args_list)` method to execute batch writes.
# - Ensure that the connection is released back to the pool inside a finally block.

    @classmethod
    async def execute_batch(cls, query: str, args_list: list) -> None:
        """
        Execute a batch update query using executemany.
        """
        conn = await cls.get_connection()
        try:
            await conn.executemany(query, args_list)
        finally:
            await cls._pool.release(conn)


# Singleton instance
database = DatabaseConnection()

# Schema configuration for multi-tenant database
SCHEMA_NAME = "transactions_service"

# Update search_path for PostgreSQL
async def set_schema_search_path(connection):
    """Set the search path to use the correct schema."""
    await connection.execute(f"SET search_path TO transactions_service, public")
