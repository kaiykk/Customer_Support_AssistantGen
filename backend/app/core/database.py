"""
Database Configuration and Session Management

This module provides database connectivity and session management for the application.
It uses SQLAlchemy's async engine for non-blocking database operations and implements
connection pooling for optimal performance.

Key Features:
- Async database engine with connection pooling
- Automatic connection health checks (pool_pre_ping)
- Transaction management with automatic rollback on errors
- Configurable pool size and overflow limits
- Declarative base for ORM models

Connection Pool Configuration:
- pool_size: 5 (number of persistent connections)
- max_overflow: 10 (additional connections when pool is exhausted)
- Total capacity: 15 concurrent database operations

Usage:
    from app.core.database import get_db, Base
    
    # In FastAPI endpoint
    @app.get("/items")
    async def get_items(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(Item))
        return result.scalars().all()
"""

import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Suppress SQLAlchemy INFO-level SQL query logs to reduce noise
# Only WARNING and above will be logged
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# Create async database engine with connection pooling
# This engine manages all database connections and provides async operations
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Disable SQL query echo to console (use logger instead)
    pool_pre_ping=True,  # Test connections before using them (detect stale connections)
    pool_size=5,  # Maintain 5 persistent connections in the pool
    max_overflow=10,  # Allow up to 10 additional connections when pool is exhausted
    pool_recycle=3600,  # Recycle connections after 1 hour to prevent stale connections
    pool_timeout=30,  # Wait up to 30 seconds for an available connection
)

# Create async session factory
# This factory produces database sessions for each request
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Keep objects usable after commit
    autocommit=False,  # Require explicit commit
    autoflush=False,  # Require explicit flush
)

# Create declarative base class for ORM models
# All database models should inherit from this base
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Database session dependency for FastAPI endpoints.
    
    This function provides a database session for each request and ensures
    proper transaction management with automatic commit/rollback.
    
    Transaction Behavior:
    - Automatically commits on successful completion
    - Automatically rolls back on any exception
    - Always closes the session to return connection to pool
    
    Yields:
        AsyncSession: Database session for the current request
        
    Raises:
        Exception: Re-raises any exception after rolling back the transaction
        
    Example:
        @app.get("/users/{user_id}")
        async def get_user(
            user_id: int,
            db: AsyncSession = Depends(get_db)
        ):
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # Commit transaction if no exceptions occurred
            await session.commit()
        except Exception:
            # Rollback transaction on any error
            await session.rollback()
            raise
        finally:
            # Always close session to return connection to pool
            await session.close()


async def init_db() -> None:
    """
    Initialize database by creating all tables.
    
    This function should be called during application startup to ensure
    all database tables exist. It creates tables based on all models
    that inherit from Base.
    
    Note:
        This is a simple initialization suitable for development.
        For production, use Alembic migrations instead.
        
    Example:
        @app.on_event("startup")
        async def startup():
            await init_db()
    """
    async with engine.begin() as conn:
        # Create all tables defined in models
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database engine and dispose of connection pool.
    
    This function should be called during application shutdown to ensure
    all database connections are properly closed and resources are released.
    
    Example:
        @app.on_event("shutdown")
        async def shutdown():
            await close_db()
    """
    await engine.dispose()


async def check_db_connection() -> bool:
    """
    Check if database connection is healthy.
    
    This function attempts to execute a simple query to verify that
    the database is accessible and responding.
    
    Returns:
        bool: True if connection is healthy, False otherwise
        
    Example:
        @app.get("/health")
        async def health_check():
            db_healthy = await check_db_connection()
            return {"database": "healthy" if db_healthy else "unhealthy"}
    """
    try:
        async with AsyncSessionLocal() as session:
            # Execute simple query to test connection
            await session.execute("SELECT 1")
            return True
    except Exception as e:
        logging.error(f"Database connection check failed: {e}")
        return False
