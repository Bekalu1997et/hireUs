"""
Database session management.
Provides async database session handling with proper lifecycle management.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.db.base import Base

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.
    Ensures proper cleanup after request completion.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.
    Creates all tables defined in models.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections.
    Call this on application shutdown.
    """
    await engine.dispose()


async def get_sync_db():
    """
    Get a synchronous database session.
    Useful for migrations and initial setup.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    sync_engine = create_engine(
        settings.SYNC_DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )
    
    sync_session_factory = sessionmaker(
        sync_engine,
        autocommit=False,
        autoflush=False,
    )
    
    return sync_session_factory()

