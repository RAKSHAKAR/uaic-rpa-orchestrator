import asyncio
import sys
from pathlib import Path

backend_dir = str(Path(__file__).resolve().parent.parent / "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.database import AsyncSessionLocal
from app.models.claim import ClaimRecord, RecordStatusEnum, BotStatusEnum
from sqlalchemy import select, update

async def reset_claims():
    async with AsyncSessionLocal() as s:
        # Reset claims currently in FAILED or SCRAPING_IN_PROGRESS
        r = await s.execute(
            select(ClaimRecord).where(
                ClaimRecord.record_status.in_([RecordStatusEnum.FAILED, RecordStatusEnum.SCRAPING_IN_PROGRESS])
            )
        )
        claims = r.scalars().all()
        print(f"Found {len(claims)} claims to reset.")
        
        bot_status_attrs = [
            "fl_botstatus_broward", "fl_botstatus_hillsborough", "fl_botstatus_miami",
            "te_botstatus_travis", "te_botstatus_dallas", "te_botstatus_harris",
            "te_botstatus_cclerk", "te_botstatus_hcdistrict"
        ]
        
        for c in claims:
            c.record_status = RecordStatusEnum.NEW
            c.last_error = None
            c.retry_count = 0
            for attr in bot_status_attrs:
                setattr(c, attr, BotStatusEnum.NOT_TRIGGERED)
        
        await s.commit()
        print(f"Successfully reset {len(claims)} claims to NEW with NOT_TRIGGERED bot statuses!")

if __name__ == "__main__":
    asyncio.run(reset_claims())
