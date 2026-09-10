"""SQLAlchemy Async Database Configuration and Session Management."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Configure engine arguments based on DB dialect for FastAPI server
engine_kwargs = {"echo": False, "future": True}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_size"] = 20
    engine_kwargs["max_overflow"] = 10

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Dedicated engine with NullPool for Celery background tasks (prevents event loop connection conflicts)
task_engine_kwargs = {"echo": False, "future": True, "poolclass": NullPool}
if settings.DATABASE_URL.startswith("sqlite"):
    task_engine_kwargs["connect_args"] = {"check_same_thread": False}

task_engine = create_async_engine(settings.DATABASE_URL, **task_engine_kwargs)

TaskAsyncSessionLocal = async_sessionmaker(
    bind=task_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base model for all SQLAlchemy entities."""


async def get_db() -> AsyncGenerator[AsyncSession]:
    """FastAPI Dependency for obtaining an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables on application startup."""
    # Import all models to ensure metadata registration
    from sqlalchemy import text

    import app.models  # noqa: F401
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Ensure new telemetry columns exist in SQLite
        try:
            await conn.execute(text("ALTER TABLE claim_records ADD COLUMN action_timings JSON"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE claim_records ADD COLUMN total_duration_seconds REAL"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE error_screenshots ADD COLUMN storage_provider VARCHAR(50) DEFAULT 'local'"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE ingestion_batches ADD COLUMN duplicate_records INTEGER DEFAULT 0"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE ingestion_batches ADD COLUMN invalid_records INTEGER DEFAULT 0"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE ingestion_batches ADD COLUMN mapping_config JSON"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE ingestion_batches ADD COLUMN failed_rows_data JSON"))
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE notifications ADD COLUMN delivery_receipt JSON"))
        except Exception:
            pass


