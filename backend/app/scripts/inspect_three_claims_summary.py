import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models.claim import ClaimRecord
from app.models.error_screenshot import ErrorScreenshot

PG_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/uaic_db"
engine_pg = create_async_engine(PG_URL, echo=False)
SessionPG = async_sessionmaker(engine_pg, expire_on_commit=False)


async def summarize():
    claim_ids = [
        "842acd27-9409-4c49-9586-71da6f1b21a3",
    ]

    async with SessionPG() as session:
        for cid in claim_ids:
            q = select(ClaimRecord).where(ClaimRecord.id == cid)
            res = await session.execute(q)
            c = res.scalar_one_or_none()
            if not c:
                print(f"NOT FOUND: {cid}")
                continue

            sq = select(ErrorScreenshot).where(ErrorScreenshot.claim_id == cid).order_by(ErrorScreenshot.created_at.asc())
            sr = await session.execute(sq)
            shots = sr.scalars().all()

            print("\n" + "=" * 80)
            print(f"CLAIM ID: {c.id}")
            print(f"CLAIM NUMBER: {c.claim_number} | EXPOSURE: {c.exposure_number}")
            print(f"RECORD STATUS: {c.record_status} | RETRY COUNT: {c.retry_count}")
            print(f"POLICY STATE: {c.policy_state} | LOSS STATE: {c.loss_location_state}")
            print(f"CLAIMANT: {c.claimant_first_name} {c.claimant_last_name}")
            print(f"INSURED:  {c.insured_first_name} {c.insured_last_name}")
            print(f"DRIVER:   {c.driver_first_name} {c.driver_last_name}")
            print(f"LAST ERROR: {c.last_error}")
            print(f"UPDATED AT: {c.updated_at}")
            print("-" * 40)
            print("PORTAL STATUSES & TARGETS:")
            fl_portals = [
                ("Broward", c.fl_botstatus_broward, c.fl_website_broward),
                ("Hillsborough", c.fl_botstatus_hillsborough, c.fl_website_hillsborough),
                ("Miami", c.fl_botstatus_miami, c.fl_website_miami),
            ]
            tx_portals = [
                ("Travis", c.te_botstatus_travis, c.te_website_travis),
                ("Dallas", c.te_botstatus_dallas, c.te_website_dallas),
                ("Harris JP", c.te_botstatus_harris, c.te_website_harris),
                ("Harris CClerk", c.te_botstatus_cclerk, c.te_website_cclerk),
                ("Harris District", c.te_botstatus_hcdistrict, c.te_website_hcdistrict),
            ]
            for name, status, target in fl_portals + tx_portals:
                print(f"  {name:16}: status={str(status):16} target={target}")

            print("-" * 40)
            print(f"ERROR SCREENSHOTS / DIAGNOSTICS ({len(shots)} total):")
            for idx, sh in enumerate(shots, 1):
                print(f"  [{idx}] Portal: {sh.portal_name} (key={sh.portal_key})")
                print(f"      Time: {sh.created_at}")
                print(f"      URL:  {sh.page_url}")
                print(f"      File: {sh.file_path}")
                print(f"      Exception/Msg: {sh.exception_message}")

            # Check portal action timings status summary
            timings = c.action_timings or {}
            portals_timings = timings.get("portals", {})
            print("-" * 40)
            print("PORTALS IN ACTION TIMINGS:")
            for pkey, pval in portals_timings.items():
                print(f"  {pkey:16}: status={pval.get('status')} cases_found={pval.get('cases_found')} duration={pval.get('duration_seconds')}s error={pval.get('error')}")


if __name__ == "__main__":
    asyncio.run(summarize())
