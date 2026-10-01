import sys
import os
sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("."))

import asyncio
from app.core.database import AsyncSessionLocal
from app.models.claim import ClaimRecord, RecordStatusEnum
from sqlalchemy import select, func

async def main():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(ClaimRecord.record_status, func.count(ClaimRecord.id)).group_by(ClaimRecord.record_status))
        counts = res.all()
        print("Claim counts by status:")
        for status, cnt in counts:
            print(f"  {status}: {cnt}")

        pending = (await db.execute(
            select(ClaimRecord)
            .where(ClaimRecord.record_status.in_([RecordStatusEnum.NEW, RecordStatusEnum.PENDING]))
            .order_by(ClaimRecord.created_at.asc())
        )).scalars().all()
        print(f"\nPending claims (NEW / PENDING): {len(pending)}")
        for p in pending:
            print(f"  Claim #{p.claim_number} (ID: {p.id}, Status: {p.record_status}, Created: {p.created_at})")

if __name__ == "__main__":
    asyncio.run(main())
