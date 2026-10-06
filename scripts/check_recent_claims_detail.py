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

async def check():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ClaimRecord).order_by(desc(ClaimRecord.updated_at)).limit(15)
        )
        claims = result.scalars().all()
        for c in claims:
            print(f"Claim: {c.claim_number} | ID: {c.id} | Status: {c.record_status} | Error: {c.last_error}")
            at = c.action_timings or {}
            portals = at.get("portals", {})
            for p_k, p_v in portals.items():
                print(f"   {p_k}: status={p_v.get('status')} duration={p_v.get('duration_seconds')} error={p_v.get('error')}")

if __name__ == "__main__":
    asyncio.run(check())
