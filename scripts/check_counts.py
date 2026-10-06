import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath("backend"))

from app.core.database import AsyncSessionLocal
from sqlalchemy import select, func
from app.models.claim import ClaimRecord

async def main():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(ClaimRecord.record_status, func.count(ClaimRecord.id)).group_by(ClaimRecord.record_status))
        print("RECORD_STATUS:", [(str(r[0].value if hasattr(r[0], 'value') else r[0]), r[1]) for r in res.all()])
        res2 = await db.execute(select(ClaimRecord.fuzzy_match_status, func.count(ClaimRecord.id)).group_by(ClaimRecord.fuzzy_match_status))
        print("FUZZY_STATUS:", [(str(r[0].value if hasattr(r[0], 'value') else r[0]), r[1]) for r in res2.all()])

if __name__ == "__main__":
    asyncio.run(main())
