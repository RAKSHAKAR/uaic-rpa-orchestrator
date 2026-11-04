"""Enterprise Synchronization Utility: SQLite (orchestrator.db) -> PostgreSQL (Docker).

Usage:
    python scripts/sync_sqlite_to_postgres.py [--sqlite-path PATH] [--pg-url URL] [--force]

Options:
    --sqlite-path: Path to SQLite database (default: backend/orchestrator.db)
    --pg-url: PostgreSQL connection URL (default: postgresql+asyncpg://postgres:postgres@localhost:5432/uaic_db)
    --force: Overwrite existing records if needed
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add backend to sys.path so app imports work cleanly
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.db_sync_service import find_sqlite_db_path, sync_sqlite_to_postgres
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("sync_sqlite_to_postgres")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Sync SQLite claims to PostgreSQL")
    parser.add_argument("--sqlite-path", type=str, default="", help="Path to SQLite DB")
    parser.add_argument(
        "--pg-url",
        type=str,
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/uaic_db",
        help="PostgreSQL connection string",
    )
    args = parser.parse_args()

    sqlite_path = Path(args.sqlite_path) if args.sqlite_path else find_sqlite_db_path()
    if not sqlite_path or not sqlite_path.is_file():
        logger.error(f"Could not locate SQLite database at {sqlite_path}")
        sys.exit(1)

    logger.info(f"Target SQLite database: {sqlite_path} ({sqlite_path.stat().st_size / 1024 / 1024:.2f} MB)")
    logger.info(f"Target PostgreSQL URL: {args.pg_url}")

    engine = create_async_engine(args.pg_url, echo=False)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        try:
            total_synced = await sync_sqlite_to_postgres(sqlite_path, session)
            logger.info(f"Synchronization complete! Restored {total_synced} entities.")
        except Exception as e:
            logger.error(f"Sync failed: {e}", exc_info=True)
            sys.exit(1)
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
