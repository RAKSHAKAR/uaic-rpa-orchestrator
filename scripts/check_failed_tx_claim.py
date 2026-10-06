import asyncio
import json
import sys
from pathlib import Path

backend_dir = str(Path(__file__).resolve().parent.parent / "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.database import AsyncSessionLocal
from app.models.claim import ClaimRecord, RecordStatusEnum
from sqlalchemy import select, desc

async def inspect():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ClaimRecord).where(ClaimRecord.record_status == RecordStatusEnum.FAILED).order_by(desc(ClaimRecord.updated_at)).limit(5)
        )
        claims = result.scalars().all()
        for c in claims:
            print(f"=== Claim {c.id} ({c.claim_number}) State: {c.policy_state}/{c.loss_location_state} ===")
            print(f"Status: {c.record_status}")
            print(f"Last Error: {c.last_error}")
            print(f"Action Timings: {json.dumps(c.action_timings, indent=2)}")
            print(f"te_botstatus_cclerk: {c.te_botstatus_cclerk}")
            print(f"te_botstatus_dallas: {c.te_botstatus_dallas}")
            print(f"te_botstatus_harris: {c.te_botstatus_harris}")
            print(f"te_botstatus_hcdistrict: {c.te_botstatus_hcdistrict}")
            print(f"te_botstatus_travis: {c.te_botstatus_travis}")
            print()

if __name__ == "__main__":
    asyncio.run(inspect())
