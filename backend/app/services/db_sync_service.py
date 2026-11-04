"""Database synchronization service between SQLite (orchestrator.db) and PostgreSQL.

Ensures that whenever the solution is deployed or redeployed using Docker Compose,
all historical claims, scraping results, match evaluations, and system configurations
from orchestrator.db are automatically seeded into PostgreSQL if the database is clean.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, engine

logger = logging.getLogger("uaic_orchestrator.db_sync")

TABLES_IN_ORDER = [
    "ingestion_batches",
    "claim_records",
    "scraped_court_cases",
    "match_pairs",
    "filtered_out_cases",
    "guidewire_activities",
    "error_screenshots",
    "automation_settings",
    "settings_audit_logs",
    "notification_templates",
    "notification_rules",
    "notifications",
    "audit_logs",
]

JSON_COLUMNS: dict[str, list[str]] = {
    "ingestion_batches": ["mapping_config", "failed_rows_data"],
    "claim_records": ["action_timings", "guidewire_payload"],
    "scraped_court_cases": ["raw_payload"],
    "error_screenshots": [],
    "automation_settings": ["value"],
    "settings_audit_logs": ["old_value", "new_value"],
    "notification_templates": [],
    "notification_rules": ["channels", "recipients"],
    "notifications": ["recipient_emails", "error_details", "delivery_receipt"],
    "audit_logs": ["payload"],
}


def find_sqlite_db_path() -> Path | None:
    """Locate the authoritative orchestrator.db file across environments."""
    candidates = [
        Path("/app/orchestrator.db"),
        Path("/app/backend/orchestrator.db"),
        Path(__file__).resolve().parent.parent.parent / "orchestrator.db",
        Path(__file__).resolve().parent.parent.parent.parent / "backend" / "orchestrator.db",
        Path("backend/orchestrator.db"),
        Path("orchestrator.db"),
    ]
    for p in candidates:
        if p.is_file() and p.stat().st_size > 0:
            return p
    return None


async def auto_seed_from_sqlite_if_empty() -> None:
    """Automatically seeds PostgreSQL from orchestrator.db if claim_records is empty.

    Triggered on FastAPI lifespan startup to ensure redeploying with docker-compose
    always retains and displays all historical claims and settings.
    """
    if engine.dialect.name == "sqlite":
        # Already running directly on SQLite, no sync needed
        return

    sqlite_path = find_sqlite_db_path()
    if not sqlite_path:
        logger.info("Auto-seed check: No SQLite orchestrator.db found to seed from.")
        return

    async with AsyncSessionLocal() as session:
        try:
            res = await session.execute(text("SELECT count(*) FROM claim_records;"))
            pg_claim_count = res.scalar() or 0
        except Exception as e:
            logger.warning(f"Could not verify existing claim_records count: {e}")
            return

        if pg_claim_count > 0:
            logger.info(f"Database already contains {pg_claim_count} claims. Skipping auto-seed.")
            return

        logger.info(f"Clean database detected (0 claims). Auto-seeding from {sqlite_path}...")
        try:
            total_synced = await sync_sqlite_to_postgres(sqlite_path, session)
            logger.info(
                f"Auto-seed successfully restored {total_synced} total entities from {sqlite_path.name}."
            )
        except Exception as e:
            logger.error(
                f"Auto-seed encountered an error during data restoration: {e}", exc_info=True
            )


async def sync_sqlite_to_postgres(sqlite_path: Path, session: AsyncSession) -> int:
    """Streams and copies all tables from SQLite into PostgreSQL with idempotent conflict handling."""
    if not sqlite_path.exists():
        raise FileNotFoundError(f"SQLite file not found at {sqlite_path}")

    sqlite_conn = sqlite3.connect(str(sqlite_path))
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    total_entities_synced = 0

    try:
        for table_name in TABLES_IN_ORDER:
            # Check row count in SQLite
            try:
                sqlite_cur.execute(f"SELECT count(*) FROM {table_name}")
                sq_count = sqlite_cur.fetchone()[0]
            except sqlite3.OperationalError:
                continue

            if sq_count == 0:
                continue

            # Fetch SQLite columns
            sqlite_cur.execute(f"PRAGMA table_info({table_name})")
            sq_cols = [r["name"] for r in sqlite_cur.fetchall()]

            # Fetch PostgreSQL columns
            res = await session.execute(
                text(
                    "SELECT column_name, data_type FROM information_schema.columns "
                    f"WHERE table_name = '{table_name}' AND table_schema = 'public'"
                )
            )
            pg_col_types = {r[0]: r[1] for r in res.fetchall()}
            common_cols = [c for c in sq_cols if c in pg_col_types]

            if not common_cols:
                continue

            # Fetch rows from SQLite (filter orphan foreign keys where applicable)
            where_clause = ""
            if table_name == "match_pairs":
                where_clause = " WHERE court_case_id IN (SELECT id FROM scraped_court_cases)"

            sqlite_cur.execute(f"SELECT {', '.join(common_cols)} FROM {table_name}{where_clause}")
            rows = sqlite_cur.fetchall()

            batch_data: list[dict] = []
            json_cols = set(JSON_COLUMNS.get(table_name, []))

            for row in rows:
                row_dict = {}
                for col in common_cols:
                    val = row[col]
                    col_type = pg_col_types[col]

                    if col in json_cols and val is not None:
                        if isinstance(val, (dict, list)):
                            row_dict[col] = json.dumps(val)
                        elif isinstance(val, str):
                            try:
                                json.loads(val)
                                row_dict[col] = val
                            except Exception:
                                row_dict[col] = json.dumps(val)
                        else:
                            row_dict[col] = json.dumps(val)
                    elif col_type in (
                        "timestamp without time zone",
                        "timestamp with time zone",
                    ) and isinstance(val, str):
                        try:
                            row_dict[col] = datetime.fromisoformat(val)
                        except Exception:
                            row_dict[col] = val
                    elif col_type == "boolean" and val is not None and isinstance(val, int):
                        row_dict[col] = bool(val)
                    else:
                        row_dict[col] = val
                batch_data.append(row_dict)

            chunk_size = 500
            table_inserted = 0
            for i in range(0, len(batch_data), chunk_size):
                chunk = batch_data[i : i + chunk_size]
                col_names = ", ".join(common_cols)
                param_names = ", ".join([f":{c}" for c in common_cols])

                pk = "key" if table_name == "automation_settings" else "id"
                if pk in common_cols:
                    stmt = text(
                        f"INSERT INTO {table_name} ({col_names}) VALUES ({param_names}) ON CONFLICT ({pk}) DO NOTHING"
                    )
                else:
                    stmt = text(f"INSERT INTO {table_name} ({col_names}) VALUES ({param_names})")

                await session.execute(stmt, chunk)
                table_inserted += len(chunk)

            await session.commit()
            total_entities_synced += table_inserted
            logger.info(f"[{table_name}] Restored {table_inserted} rows from SQLite.")

    finally:
        sqlite_conn.close()

    return total_entities_synced
