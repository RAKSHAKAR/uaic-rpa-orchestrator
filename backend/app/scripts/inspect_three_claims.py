import asyncio
import json
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models.claim import ClaimRecord
from app.models.error_screenshot import ErrorScreenshot

PG_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/uaic_db"
engine_pg = create_async_engine(PG_URL, echo=False)
SessionPG = async_sessionmaker(engine_pg, expire_on_commit=False)


async def inspect_claims():
    claim_ids = [
        "842acd27-9409-4c49-9586-71da6f1b21a3",
        "2b41c35b-9d6b-4caa-84b9-a250e2b3ada2",
        "9a79524c-7462-47e8-9f76-a99a802fcead",
    ]

    async with SessionPG() as session:
        for cid in claim_ids:
            q = select(ClaimRecord).where(ClaimRecord.id == cid)
            res = await session.execute(q)
            c = res.scalar_one_or_none()
            if not c:
                print(f"CLAIM NOT FOUND IN DB: {cid}")
                continue

            sq = select(ErrorScreenshot).where(ErrorScreenshot.claim_id == cid).order_by(ErrorScreenshot.created_at.desc())
            sr = await session.execute(sq)
            shots = sr.scalars().all()

            print("=" * 60)
            print(f"CLAIM ID: {c.id}")
            print(f"CLAIM NUMBER: {c.claim_number} | EXPOSURE: {c.exposure_number}")
            print(f"RECORD STATUS: {c.record_status} | RETRY COUNT: {c.retry_count}")
            print(f"POLICY STATE: {c.policy_state} | LOSS LOCATION: {c.loss_location_state}")
            print(f"CLAIMANT: {c.claimant_first_name} {c.claimant_last_name}")
            print(f"INSURED: {c.insured_first_name} {c.insured_last_name}")
            print(f"DRIVER: {c.driver_first_name} {c.driver_last_name}")
            print(f"LAST ERROR: {c.last_error}")
            print(f"UPDATED AT: {c.updated_at} | CREATED AT: {c.created_at}")
            print("PORTAL STATUSES:")
            print(f"  FL Broward: {c.fl_botstatus_broward} (target: {c.fl_website_broward})")
            print(f"  FL Hillsborough: {c.fl_botstatus_hillsborough} (target: {c.fl_website_hillsborough})")
            print(f"  FL Miami: {c.fl_botstatus_miami} (target: {c.fl_website_miami})")
            print(f"  TX Travis: {c.te_botstatus_travis} (target: {c.te_website_travis})")
            print(f"  TX Dallas: {c.te_botstatus_dallas} (target: {c.te_website_dallas})")
            print(f"  TX Harris JP: {c.te_botstatus_harris} (target: {c.te_website_harris})")
            print(f"  TX Harris CClerk: {c.te_botstatus_cclerk} (target: {c.te_website_cclerk})")
            print(f"  TX Harris District: {c.te_botstatus_hcdistrict} (target: {c.te_website_hcdistrict})")
            print("ACTION TIMINGS:")
            print(json.dumps(c.action_timings, indent=2))
            print(f"ERROR SCREENSHOTS COUNT: {len(shots)}")
            for sh in shots:
                print(f"  - [{sh.portal_name}] attempt={sh.attempt_number} error={sh.exception_message}")
                print(f"    file_path={sh.file_path}")
            print("=" * 60)


if __name__ == "__main__":
    asyncio.run(inspect_claims())
