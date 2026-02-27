"""
Database session management.
Provides async database session handling with proper lifecycle management.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Use DATABASE_URL as configured.
_db_url = settings.DATABASE_URL
_is_sqlite = _db_url.startswith("sqlite")

# Create async engine
engine_kwargs = {
    "echo": settings.DEBUG,
    "pool_pre_ping": True,
}
if _is_sqlite:
    engine_kwargs["poolclass"] = NullPool  # SQLite does not support multithreaded pools well

engine = create_async_engine(_db_url, **engine_kwargs)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Alias for convenience (used in seed script and elsewhere)
AsyncSessionLocal = async_session_factory


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
    Initialize database tables when explicitly enabled.
    """
    if not settings.DB_AUTO_CREATE_TABLES:
        return

    from app.db.base import Base

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
