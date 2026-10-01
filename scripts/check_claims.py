import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.database import AsyncSessionLocal
from app.models.claim import ClaimRecord
from sqlalchemy import select

async def main():
    fl_numbers = [
        "100290914", "100303098", "100309189", "100298095", "800229161",
        "100301036", "800219248", "100317408", "800227314", "100285580"
    ]
    async with AsyncSessionLocal() as s:
        r = await s.execute(select(ClaimRecord).where(ClaimRecord.claim_number.in_(fl_numbers)))
        cs = r.scalars().all()
        print(f"Matching Florida claims in DB: {len(cs)} of {len(fl_numbers)}")
        for c in cs:
            print(f"Claim #{c.claim_number} | Status: {c.record_status} | Error: {c.last_error}")

if __name__ == "__main__":
    asyncio.run(main())
