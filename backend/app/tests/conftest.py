"""
Pytest configuration and fixtures for testing.
"""
import os
import sys

# Ensure backend/ is on sys.path so "app" imports work when running pytest from repo root
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator

from app.db.base import Base
from app.core.config import settings


# Override database URL for testing
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/hireus_test"


@pytest.fixture(scope="session")
def test_database_url():
    """Provide test database URL."""
    return TEST_DATABASE_URL


@pytest_asyncio.fixture(scope="function")
async def test_engine(test_database_url):
    """Create a test database engine."""
    engine = create_async_engine(
        test_database_url,
        echo=False,
        future=True,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session.
    
    Each test gets a fresh session that is rolled back after the test completes.
    """
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async with async_session_maker() as session:
        yield session
        await session.rollback()
