"""
Unit tests for database session management.

Tests database connection, session lifecycle, and transaction rollback.
Requirements: 10.3
"""
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.unit
async def test_database_connection(db_session: AsyncSession):
    """Test that database connection is established successfully."""
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


@pytest.mark.unit
async def test_session_lifecycle(db_session: AsyncSession):
    """Test that database session can be created and closed properly."""
    # Session should be active
    assert db_session.is_active
    
    # Execute a simple query
    result = await db_session.execute(text("SELECT 'test' as value"))
    row = result.first()
    assert row[0] == "test"
    
    # Session should still be active after query
    assert db_session.is_active


@pytest.mark.unit
async def test_transaction_rollback_on_error(db_session: AsyncSession):
    """
    Test that transactions are rolled back when errors occur.
    
    This test verifies that database operations are properly rolled back
    when an exception is raised, ensuring data consistency.
    """
    # Create a temporary table for testing
    await db_session.execute(text("""
        CREATE TEMP TABLE test_rollback (
            id SERIAL PRIMARY KEY,
            value TEXT NOT NULL
        )
    """))
    await db_session.commit()
    
    # Insert a value
    await db_session.execute(text("""
        INSERT INTO test_rollback (value) VALUES ('initial')
    """))
    await db_session.commit()
    
    # Verify the value exists
    result = await db_session.execute(text("SELECT COUNT(*) FROM test_rollback"))
    assert result.scalar() == 1
    
    # Try to insert another value but rollback
    try:
        await db_session.execute(text("""
            INSERT INTO test_rollback (value) VALUES ('should_rollback')
        """))
        # Simulate an error
        raise Exception("Simulated error")
    except Exception:
        await db_session.rollback()
    
    # Verify the second value was not persisted
    result = await db_session.execute(text("SELECT COUNT(*) FROM test_rollback"))
    assert result.scalar() == 1
    
    # Verify only the initial value exists
    result = await db_session.execute(text("SELECT value FROM test_rollback"))
    row = result.first()
    assert row[0] == "initial"


@pytest.mark.unit
async def test_session_commit(db_session: AsyncSession):
    """Test that session commit persists changes."""
    # Create a temporary table
    await db_session.execute(text("""
        CREATE TEMP TABLE test_commit (
            id SERIAL PRIMARY KEY,
            value TEXT NOT NULL
        )
    """))
    await db_session.commit()
    
    # Insert and commit
    await db_session.execute(text("""
        INSERT INTO test_commit (value) VALUES ('committed')
    """))
    await db_session.commit()
    
    # Verify the value persists
    result = await db_session.execute(text("SELECT value FROM test_commit"))
    row = result.first()
    assert row[0] == "committed"


@pytest.mark.unit
async def test_multiple_queries_in_session(db_session: AsyncSession):
    """Test that multiple queries can be executed in the same session."""
    # Execute multiple queries
    result1 = await db_session.execute(text("SELECT 1 as num"))
    result2 = await db_session.execute(text("SELECT 2 as num"))
    result3 = await db_session.execute(text("SELECT 3 as num"))
    
    assert result1.scalar() == 1
    assert result2.scalar() == 2
    assert result3.scalar() == 3
