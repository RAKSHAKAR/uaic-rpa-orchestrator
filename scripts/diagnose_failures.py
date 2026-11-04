import asyncio
import sys
from collections import Counter
from pathlib import Path

# Add backend to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.database import TaskAsyncSessionLocal
from app.models.claim import ClaimRecord, RecordStatusEnum
from app.models.error_screenshot import ErrorScreenshot
from sqlalchemy import select


async def main():
    async with TaskAsyncSessionLocal() as session:
        claims = (await session.execute(select(ClaimRecord))).scalars().all()
        print(f"TOTAL CLAIMS IN DATABASE: {len(claims)}")
        
        status_counts = Counter(c.record_status.value if hasattr(c.record_status, 'value') else str(c.record_status) for c in claims)
        print("\n=== RECORD STATUS DISTRIBUTION ===")
        for status, count in status_counts.most_common():
            print(f"  {status}: {count}")

        failed_claims = [c for c in claims if c.record_status == RecordStatusEnum.FAILED]
        in_progress = [c for c in claims if c.record_status == RecordStatusEnum.SCRAPING_IN_PROGRESS]
        print(f"\nExplicit FAILED Claims: {len(failed_claims)}")
        print(f"Stuck SCRAPING_IN_PROGRESS Claims: {len(in_progress)}")

        # Check portal failure distribution across all claims
        portal_fields = [
            ("broward", "fl_botstatus_broward"),
            ("hillsborough", "fl_botstatus_hillsborough"),
            ("miami", "fl_botstatus_miami"),
            ("travis", "te_botstatus_travis"),
            ("dallas", "te_botstatus_dallas"),
            ("harris_jp", "te_botstatus_harris"),
            ("harris_cclerk", "te_botstatus_cclerk"),
            ("harris_district", "te_botstatus_hcdistrict"),
        ]

        print("\n=== PORTAL BOT STATUS COUNTERS ACROSS ALL CLAIMS ===")
        for portal_key, attr in portal_fields:
            vals = Counter(str(getattr(c, attr)) for c in claims)
            print(f"  {portal_key:16}: {dict(vals)}")

        # Inspect failure reasons in detail for the most recent 15 claims
        print("\n=== RECENT 15 CLAIMS DETAILED DIAGNOSTICS ===")
        for c in claims[-15:]:
            print("-" * 70)
            print(f"Claim #{c.claim_number} (ID: {c.id})")
            print(f"  Status: {c.record_status.value if hasattr(c.record_status, 'value') else c.record_status} | RetryCount: {c.retry_count}")
            print(f"  Routing: Policy={c.policy_state}, Loss={c.loss_location_state}, DOL={c.dol}")
            portal_summary = []
            for portal_key, attr in portal_fields:
                val = getattr(c, attr)
                if val:
                    val_str = val.value if hasattr(val, 'value') else str(val)
                    portal_summary.append(f"{portal_key}={val_str}")
            print(f"  Portals: {', '.join(portal_summary)}")
            
            if c.action_timings:
                portals_timings = c.action_timings.get("portals", {})
                errors = []
                for p_name, p_data in portals_timings.items():
                    err = p_data.get("error")
                    st = p_data.get("status")
                    if err or st in ("FAILED", "BLOCKED", "ERROR"):
                        errors.append(f"[{p_name}: status={st}, err={err}]")
                if errors:
                    print(f"  Portal Errors in Timings: {' '.join(errors)}")
            
        screenshots = (await session.execute(select(ErrorScreenshot))).scalars().all()
        print(f"\n=== TOTAL ERROR SCREENSHOTS: {len(screenshots)} ===")
        err_msg_counts = Counter(s.exception_message for s in screenshots)
        for msg, cnt in err_msg_counts.most_common(15):
            print(f"  [{cnt}x] {msg}")

        print("\n=== LAST 10 ERROR SCREENSHOTS ===")
        for s in screenshots[-10:]:
            print(f"  Claim {s.claim_id} | Portal: {s.portal_name} | Error: {s.exception_message}")

if __name__ == "__main__":
    asyncio.run(main())
