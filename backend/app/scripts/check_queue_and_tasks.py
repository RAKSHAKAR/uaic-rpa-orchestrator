import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models.claim import ClaimRecord
from app.tasks.queue_runner import get_active_queue_item_ids, is_auto_queue_enabled

PG_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/uaic_db"
engine_pg = create_async_engine(PG_URL, echo=False)
SessionPG = async_sessionmaker(engine_pg, expire_on_commit=False)


async def check():
    auto_mode = is_auto_queue_enabled()
    active_ids = get_active_queue_item_ids()
    print(f"Auto-queue enabled: {auto_mode}")
    print(f"Active queue item IDs ({len(active_ids)}): {active_ids}")

    async with SessionPG() as s:
        status_counts = await s.execute(select(ClaimRecord.record_status, func.count()).group_by(ClaimRecord.record_status))
        print("Record status counts:")
        for st, cnt in status_counts.all():
            print(f"  {st}: {cnt}")

        new_claims = await s.execute(select(ClaimRecord.id, ClaimRecord.claim_number).where(ClaimRecord.record_status == 'NEW').limit(10))
        print("Sample NEW claims:")
        for cid, cnum in new_claims.all():
            print(f"  {cid}: {cnum}")


if __name__ == "__main__":
    asyncio.run(check())
