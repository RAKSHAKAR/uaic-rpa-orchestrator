import asyncio
import json
import sys
from pathlib import Path

backend_dir = str(Path(__file__).resolve().parent.parent / "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.database import AsyncSessionLocal
from app.models.claim import ClaimRecord
from sqlalchemy import select

async def main():
    claim_nums = [
        "100285627",
        "100319958",
        "100305433",
        "100295866",
        "800221263",
        "100294077",
    ]
    async with AsyncSessionLocal() as s:
        for cnum in claim_nums:
            r = await s.execute(select(ClaimRecord).where(ClaimRecord.claim_number == cnum))
            c = r.scalar_one_or_none()
            if not c:
                print(f"Claim {cnum}: NOT FOUND")
                continue
            print(f"==================================================")
            print(f"Claim #{c.claim_number} (ID: {c.id})")
            print(f"Policy: {c.policy_state} | Loss: {c.loss_location_state}")
            print(f"Overall Status: {c.record_status}")
            print(f"Last Error: {c.last_error}")
            print(f"Updated At: {c.updated_at}")
            print(f"Florida Bots: broward={c.fl_botstatus_broward}, hillsborough={c.fl_botstatus_hillsborough}, miami={c.fl_botstatus_miami}")
            print(f"Texas Bots: travis={c.te_botstatus_travis}, dallas={c.te_botstatus_dallas}, harris={c.te_botstatus_harris}, cclerk={c.te_botstatus_cclerk}, hcdistrict={c.te_botstatus_hcdistrict}")
            at = c.action_timings or {}
            print(f"Total scraping seconds: {at.get('total_scraping_seconds')}")
            portals = at.get("portals", {})
            for pk, pv in portals.items():
                print(f"  Portal {pk}: status={pv.get('status')} cases={pv.get('cases_found')} err={pv.get('error')}")

if __name__ == "__main__":
    asyncio.run(main())
