"""Sync exact claim completion statuses from backend/orchestrator.db.bak into PostgreSQL."""

import asyncio
import sqlite3

import asyncpg


async def sync_bak():
    conn_sq = sqlite3.connect("backend/orchestrator.db.bak")
    conn_sq.row_factory = sqlite3.Row
    c_sq = conn_sq.cursor()
    rows = c_sq.execute(
        "SELECT id, record_status, fuzzy_match_status, last_error, retry_count FROM claim_records"
    ).fetchall()

    conn_pg = await asyncpg.connect("postgresql://postgres:postgres@localhost:5432/uaic_db")

    print(f"Syncing exact status for {len(rows)} claims from orchestrator.db.bak...")
    for r in rows:
        await conn_pg.execute(
            """
            UPDATE claim_records
            SET record_status = $2, fuzzy_match_status = $3, last_error = $4, retry_count = $5
            WHERE id = $1
            """,
            r["id"],
            r["record_status"],
            r["fuzzy_match_status"],
            r["last_error"],
            r["retry_count"],
        )

    counts = await conn_pg.fetch(
        "SELECT record_status, count(*) as cnt FROM claim_records GROUP BY record_status"
    )
    print("\nUpdated PostgreSQL Record Statuses:")
    for c in counts:
        print(f"  {c['record_status']}: {c['cnt']}")

    await conn_pg.close()
    conn_sq.close()


if __name__ == "__main__":
    asyncio.run(sync_bak())
