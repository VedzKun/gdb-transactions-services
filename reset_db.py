#!/usr/bin/env python3
"""
Database Reset Script

Drops and recreates all tables in the PostgreSQL database for the Transactions Service.
This is useful for development and testing to reset the database to a clean state.

⚠️  WARNING: This will delete ALL data in the database. Use with caution!

Usage:
    python reset_db.py
"""

import asyncio
import asyncpg
import logging
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.config.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# SQL for dropping tables
DROP_TRANSACTION_LOGGING_TABLE = """
DROP TABLE IF EXISTS transaction_logging CASCADE;
"""

DROP_FUND_TRANSFERS_TABLE = """
DROP TABLE IF EXISTS fund_transfers CASCADE;
"""

# SQL Schemas for creating tables - Simplified for transaction tracking
CREATE_FUND_TRANSFERS_TABLE = """
CREATE TABLE IF NOT EXISTS fund_transfers (
    id BIGSERIAL PRIMARY KEY,
    from_account BIGINT NOT NULL,
    to_account BIGINT NOT NULL,
    transfer_amount NUMERIC(15, 2) NOT NULL,
    transfer_mode VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_transfer_amount CHECK (transfer_amount > 0),
    CONSTRAINT chk_from_not_equal_to CHECK (from_account <> to_account),
    CONSTRAINT chk_transfer_mode CHECK (
        transfer_mode IN ('NEFT', 'RTGS', 'IMPS', 'UPI')
    )
);

-- Indexes for fund_transfers
CREATE INDEX IF NOT EXISTS idx_fund_transfers_from_account ON fund_transfers(from_account);
CREATE INDEX IF NOT EXISTS idx_fund_transfers_to_account ON fund_transfers(to_account);
CREATE INDEX IF NOT EXISTS idx_fund_transfers_created_at ON fund_transfers(created_at);
"""

CREATE_TRANSACTION_LOGGING_TABLE = """
CREATE TABLE IF NOT EXISTS transaction_logging (
    id BIGSERIAL PRIMARY KEY,
    account_number BIGINT NOT NULL,
    amount NUMERIC(15, 2) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_transaction_amount CHECK (amount > 0),
    CONSTRAINT chk_transaction_type CHECK (
        transaction_type IN ('WITHDRAW', 'DEPOSIT', 'TRANSFER')
    )
);

-- Indexes for transaction_logging
CREATE INDEX IF NOT EXISTS idx_transaction_logging_account ON transaction_logging(account_number);
CREATE INDEX IF NOT EXISTS idx_transaction_logging_type ON transaction_logging(transaction_type);
CREATE INDEX IF NOT EXISTS idx_transaction_logging_created_at ON transaction_logging(created_at);
"""


async def confirm_reset():
    """Ask user for confirmation before resetting database."""
    
    print("\n" + "="*70)
    print("⚠️  WARNING: DATABASE RESET")
    print("="*70)
    print(f"\nDatabase: {settings.DB_NAME}")
    print(f"Host: {settings.DB_HOST}:{settings.DB_PORT}")
    print("\nThis operation will:")
    print("  1. DROP all existing tables (transaction_logging, fund_transfers)")
    print("  2. DELETE all data permanently")
    print("  3. Recreate empty tables with proper schema")
    print("\n⚠️  THIS CANNOT BE UNDONE!")
    print("="*70)
    
    confirmation = input("\nType 'yes' to proceed with database reset: ").strip().lower()
    
    if confirmation != 'yes':
        logger.info("❌ Reset cancelled by user")
        return False
    
    return True


async def drop_tables(connection):
    """Drop all existing tables."""
    
    logger.info("\n📋 Dropping existing tables...")
    
    try:
        # Drop in correct order (dependent tables first)
        await connection.execute(DROP_TRANSACTION_LOGGING_TABLE)
        logger.info("  ✓ Dropped transaction_logging table")
        
        await connection.execute(DROP_FUND_TRANSFERS_TABLE)
        logger.info("  ✓ Dropped fund_transfers table")
        
        logger.info("✅ All tables dropped successfully")
        return True
        
    except asyncpg.PostgresError as e:
        logger.error(f"❌ Error dropping tables: {str(e)}")
        raise


async def create_tables(connection):
    """Create all required tables."""
    
    logger.info("\n📋 Creating tables...")
    
    try:
        # Create in correct order (independent tables first)
        await connection.execute(CREATE_FUND_TRANSFERS_TABLE)
        logger.info("  ✓ Created fund_transfers table")
        
        await connection.execute(CREATE_TRANSACTION_LOGGING_TABLE)
        logger.info("  ✓ Created transaction_logging table")
        
        logger.info("✅ All tables created successfully")
        return True
        
    except asyncpg.PostgresError as e:
        logger.error(f"❌ Error creating tables: {str(e)}")
        raise


async def verify_tables(connection):
    """Verify that all tables exist and show their structure."""
    
    logger.info("\n📊 Verifying tables...")
    
    try:
        # Get list of tables
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
        """
        tables = await connection.fetch(query)
        
        if tables:
            logger.info("  Tables created:")
            for table in tables:
                table_name = table['table_name']
                # Get column count
                col_query = f"""
                SELECT COUNT(*) as cnt 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                """
                col_result = await connection.fetchrow(col_query)
                col_count = col_result['cnt']
                logger.info(f"    ✓ {table_name}: {col_count} columns, 0 rows")
        else:
            logger.warning("  No tables found!")
            return False
        
        logger.info("✅ All tables verified successfully")
        return True
        
    except asyncpg.PostgresError as e:
        logger.error(f"❌ Error verifying tables: {str(e)}")
        raise


async def reset_database():
    """Main function to reset the database."""
    
    # Connect to database
    try:
        connection = await asyncpg.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
        )
        logger.info(f"✅ Connected to database: {settings.DB_NAME}")
    except asyncpg.PostgresError as e:
        logger.error(f"❌ Failed to connect to database: {str(e)}")
        raise
    
    try:
        # Drop existing tables
        await drop_tables(connection)
        
        # Create fresh tables
        await create_tables(connection)
        
        # Verify tables
        await verify_tables(connection)
        
        logger.info("\n" + "="*70)
        logger.info("🎉 DATABASE RESET COMPLETED SUCCESSFULLY!")
        logger.info("="*70)
        logger.info(f"Database: {settings.DB_NAME}")
        logger.info(f"Host: {settings.DB_HOST}:{settings.DB_PORT}")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info("="*70)
        
    except Exception as e:
        logger.error(f"\n❌ Reset failed: {str(e)}")
        raise
    finally:
        await connection.close()
        logger.info("\n🔌 Database connection closed")


async def main():
    """Main entry point."""
    try:
        # Confirm before proceeding
        if not await confirm_reset():
            sys.exit(0)
        
        logger.info("\n🚀 Starting database reset...")
        logger.info(f"Database configuration:")
        logger.info(f"  Host: {settings.DB_HOST}")
        logger.info(f"  Port: {settings.DB_PORT}")
        logger.info(f"  Database: {settings.DB_NAME}")
        logger.info(f"  User: {settings.DB_USER}\n")
        
        # Reset database
        await reset_database()
        
    except Exception as e:
        logger.error(f"\n❌ Reset failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
