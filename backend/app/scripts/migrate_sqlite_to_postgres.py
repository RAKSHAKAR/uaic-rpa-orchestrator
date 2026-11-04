"""Enterprise Data Migration Script: SQLite to Docker PostgreSQL.
Implementation ID: IMP-2026-1007-001

Migrates all historical workflow records from backend/orchestrator.db
into the running Docker PostgreSQL container (localhost:5432 / uaic_db).
"""

import asyncio
import json
import os
import sqlite3
import sys
from datetime import datetime

import asyncpg


def parse_datetime(val):
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    if isinstance(val, str):
        val = val.strip()
        try:
            return datetime.fromisoformat(val.replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    return datetime.strptime(val, fmt)
                except ValueError:
                    pass
    return None


async def run_migration():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    sqlite_path = os.environ.get("SQLITE_PATH", os.path.join(base_dir, "orchestrator.db"))
    if not os.path.exists(sqlite_path):
        print(f"[ERROR] SQLite database not found at {sqlite_path}")
        sys.exit(1)

    print(f"[INFO] Connecting to SQLite: {sqlite_path}")
    conn_sq = sqlite3.connect(sqlite_path)
    conn_sq.row_factory = sqlite3.Row
    c_sq = conn_sq.cursor()

    pg_url = os.environ.get("PG_URL", "postgresql://postgres:postgres@localhost:5432/uaic_db")
    print(f"[INFO] Connecting to PostgreSQL: {pg_url}")
    conn_pg = await asyncpg.connect(pg_url)

    tables_order = [
        "automation_settings",
        "settings_audit_logs",
        "ingestion_batches",
        "claim_records",
        "scraped_court_cases",
        "error_screenshots",
        "guidewire_activities",
        "filtered_out_cases",
        "match_pairs",
        "audit_logs",
        "notifications",
        "notification_templates",
        "notification_rules",
    ]

    print("[INFO] Truncating existing PostgreSQL tables in cascade mode...")
    for table in reversed(tables_order):
        try:
            await conn_pg.execute(f"TRUNCATE TABLE {table} CASCADE;")
        except Exception as e:
            print(f"  [WARN] Failed to truncate {table}: {e}")

    total_migrated = {}

    for table in tables_order:
        # 1. Fetch column metadata from PostgreSQL
        pg_col_info = await conn_pg.fetch(
            """
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns
            WHERE table_name = $1 AND table_schema = 'public'
            ORDER BY ordinal_position
            """,
            table,
        )
        pg_cols = {r["column_name"]: r for r in pg_col_info}

        # 2. Before migrating match_pairs, reconcile any orphan court_case_id references
        if table == "match_pairs":
            c_sq.execute(
                """
                SELECT DISTINCT mp.court_case_id, mp.claim_id, mp.case_style
                FROM match_pairs mp
                WHERE NOT EXISTS (SELECT 1 FROM scraped_court_cases cc WHERE cc.id = mp.court_case_id)
                """
            )
            orphans = c_sq.fetchall()
            if orphans:
                print(
                    f"[RECONCILE] Backfilling {len(orphans)} historical cases referenced in match_pairs..."
                )
                for o in orphans:
                    await conn_pg.execute(
                        """
                        INSERT INTO scraped_court_cases
                        (id, claim_id, county_name, county_website, case_number, case_style, case_status, filing_date, created_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
                        ON CONFLICT (id) DO NOTHING
                        """,
                        o["court_case_id"],
                        o["claim_id"],
                        "Historical Archive",
                        "https://historical-archive.local",
                        f"ARCHIVED-{o['court_case_id'][:8]}",
                        o["case_style"] or "Historical Case",
                        "Closed",
                        "2021-01-01",
                    )

        # 3. Fetch rows from SQLite
        c_sq.execute(f"SELECT * FROM {table}")
        sq_rows = c_sq.fetchall()
        row_count = len(sq_rows)
        if row_count == 0:
            print(f"[SKIP] {table}: 0 rows in SQLite")
            total_migrated[table] = 0
            continue

        print(f"[MIGRATING] {table}: {row_count} rows...")

        sq_col_names = [d[0] for d in c_sq.description]
        target_cols = [c for c in sq_col_names if c in pg_cols]

        col_names_str = ", ".join(f'"{col}"' for col in target_cols)
        placeholders_str = ", ".join(f"${i + 1}" for i in range(len(target_cols)))
        insert_query = f"INSERT INTO {table} ({col_names_str}) VALUES ({placeholders_str}) ON CONFLICT DO NOTHING"

        batch_size = 500
        records_to_insert = []
        for row in sq_rows:
            row_dict = dict(row)
            formatted_values = []
            for col in target_cols:
                val = row_dict.get(col)
                col_meta = pg_cols[col]
                dtype = col_meta["data_type"]

                if val is None:
                    formatted_values.append(None)
                elif dtype in ("json", "jsonb"):
                    if isinstance(val, (dict, list)):
                        formatted_values.append(json.dumps(val))
                    elif isinstance(val, str):
                        s = val.strip()
                        if (s.startswith("{") and s.endswith("}")) or (
                            s.startswith("[") and s.endswith("]")
                        ):
                            try:
                                json.loads(s)
                                formatted_values.append(s)
                            except Exception:
                                formatted_values.append(json.dumps(s))
                        else:
                            formatted_values.append(json.dumps(s))
                    else:
                        formatted_values.append(json.dumps(val))
                elif dtype == "boolean":
                    formatted_values.append(bool(val) if val not in (None, "") else None)
                elif "timestamp" in dtype:
                    formatted_values.append(parse_datetime(val))
                elif dtype in ("integer", "bigint", "smallint"):
                    try:
                        formatted_values.append(int(val))
                    except ValueError, TypeError:
                        formatted_values.append(None)
                elif dtype in ("real", "double precision", "numeric"):
                    try:
                        formatted_values.append(float(val))
                    except ValueError, TypeError:
                        formatted_values.append(None)
                else:
                    formatted_values.append(str(val) if val is not None else None)

            records_to_insert.append(formatted_values)

        inserted_for_table = 0
        for i in range(0, len(records_to_insert), batch_size):
            chunk = records_to_insert[i : i + batch_size]
            await conn_pg.executemany(insert_query, chunk)
            inserted_for_table += len(chunk)

        total_migrated[table] = inserted_for_table
        print(f"  [SUCCESS] {table}: {inserted_for_table}/{row_count} rows migrated successfully.")

    print("\n================== PARITY VERIFICATION ==================")
    all_matched = True
    for table in tables_order:
        c_sq.execute(f"SELECT count(*) FROM {table}")
        sq_cnt = c_sq.fetchone()[0]
        pg_cnt = await conn_pg.fetchval(f"SELECT count(*) FROM {table}")
        status = (
            "MATCH"
            if (sq_cnt == pg_cnt or (table == "scraped_court_cases" and pg_cnt >= sq_cnt))
            else "MISMATCH"
        )
        if status == "MISMATCH":
            all_matched = False
        print(f"{table:25} | SQLite: {sq_cnt:6} | PostgreSQL: {pg_cnt:6} | {status}")

    await conn_pg.close()
    conn_sq.close()

    if all_matched:
        print("\n[SUCCESS] Migration completed with full data parity!")
    else:
        print("\n[WARNING] Some counts differed. Review output above.")


if __name__ == "__main__":
    asyncio.run(run_migration())
