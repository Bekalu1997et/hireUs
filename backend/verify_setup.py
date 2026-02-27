"""
Quick verification script to check if the infrastructure is set up correctly.
"""
import asyncio
from sqlalchemy import text

from app.db.session import AsyncSessionLocal
from app.core.config import settings


async def verify_database_connection():
    """Verify database connection works."""
    print("Testing database connection...")
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            value = result.scalar()
            if value == 1:
                print("✓ Database connection successful")
                return True
            else:
                print("✗ Database connection failed: unexpected result")
                return False
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


async def verify_configuration():
    """Verify configuration is loaded."""
    print("\nVerifying configuration...")
    print(f"  App Name: {settings.app_name}")
    print(f"  Database URL: {settings.database_url[:50]}...")
    print(f"  JWT Algorithm: {settings.jwt_algorithm}")
    print(f"  OpenAI Model: {settings.openai_model}")
    print(f"  Debug Mode: {settings.debug}")
    print("✓ Configuration loaded successfully")
    return True


async def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Infrastructure Setup Verification")
    print("=" * 60)
    
    config_ok = await verify_configuration()
    db_ok = await verify_database_connection()
    
    print("\n" + "=" * 60)
    if config_ok and db_ok:
        print("✓ All checks passed! Infrastructure is ready.")
    else:
        print("✗ Some checks failed. Please review the errors above.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
