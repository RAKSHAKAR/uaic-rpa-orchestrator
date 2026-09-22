import asyncio
import sys
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(base_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
os.chdir(backend_dir)


from app.core.database import AsyncSessionLocal
from app.models.claim import ClaimRecord
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as session:
        claim = (await session.execute(select(ClaimRecord).where(ClaimRecord.claim_number == "FST-004"))).scalar_one_or_none()
        if not claim:
            print("FST-004 not found")
            return
        print(f"FST-004: ID={claim.id}")
        print(f"  Record Status: {claim.record_status}")
        print(f"  Policy State: {claim.policy_state} | Loss Location State: {claim.loss_location_state}")
        print(f"  Targets: Brow={claim.fl_website_broward}, Hills={claim.fl_website_hillsborough}, Miami={claim.fl_website_miami}, Trav={claim.te_website_travis}, Dal={claim.te_website_dallas}, Harr={claim.te_website_harris}, CClerk={claim.te_website_cclerk}, Dist={claim.te_website_hcdistrict}")
        print(f"  Statuses: Brow={claim.fl_botstatus_broward}, Hills={claim.fl_botstatus_hillsborough}, Miami={claim.fl_botstatus_miami}")
        print(f"  Cases in JSON: Brow={len(claim.fl_jsonbody_broward or [])}, Hills={len(claim.fl_jsonbody_hillsborough or [])}, Miami={len(claim.fl_jsonbody_miami or [])}")
        print(f"  Action Timings: {claim.action_timings}")
        from app.models.audit_log import AuditLog
        total_logs = (await session.execute(select(AuditLog))).scalars().all()
        print(f"  Total AuditLogs in DB: {len(total_logs)}")
        for l in total_logs[:5]:
            print(f"    Claim: {l.claim_number} | Action: {l.action} | Status: {l.status} | Time: {l.timestamp}")





if __name__ == "__main__":
    asyncio.run(main())
