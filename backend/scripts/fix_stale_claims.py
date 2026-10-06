"""
Fix Stale Claims Script — IMP-2026-1002-001

Repairs two DB issues:
1. Resets claims stuck in SCRAPING_IN_PROGRESS > 10 minutes back to NEW
2. Runs resolve_county_bot_targets() on claims with all bot targets = 'No'
3. Resets Redis semaphore and queue keys if Redis is available
"""

import asyncio
import sys
from datetime import datetime, timedelta

sys.path.insert(0, ".")

from app.core.database import TaskAsyncSessionLocal
from app.models.claim import ClaimRecord, RecordStatusEnum
from app.services.excel_parser import resolve_county_bot_targets
from sqlalchemy import select


async def fix_stale_in_progress(session) -> int:
    """Reset stale SCRAPING_IN_PROGRESS claims (> 10 min) back to NEW."""
    threshold = datetime.utcnow() - timedelta(minutes=10)
    q = select(ClaimRecord).where(ClaimRecord.record_status == RecordStatusEnum.SCRAPING_IN_PROGRESS)
    res = await session.execute(q)
    claims = res.scalars().all()

    reset_count = 0
    for c in claims:
        claim_time = c.updated_at or c.created_at
        if claim_time:
            claim_time_naive = claim_time.replace(tzinfo=None) if getattr(claim_time, "tzinfo", None) else claim_time
            age_min = (datetime.utcnow() - claim_time_naive).total_seconds() / 60
            if age_min > 10:
                print(f"  [RESET] Claim {c.claim_number} (ID={c.id}, age={age_min:.0f}min) -> NEW")
                c.record_status = RecordStatusEnum.NEW
                c.last_error = f"Reset from stale SCRAPING_IN_PROGRESS ({age_min:.0f} min) by fix_stale_claims.py"
                c.retry_count = 0
                reset_count += 1
            else:
                print(f"  [SKIP]  Claim {c.claim_number} only {age_min:.0f}min old — keeping IN_PROGRESS")
        else:
            # No timestamp — reset anyway
            print(f"  [RESET] Claim {c.claim_number} (no timestamp) -> NEW")
            c.record_status = RecordStatusEnum.NEW
            c.last_error = "Reset from stale SCRAPING_IN_PROGRESS (no timestamp) by fix_stale_claims.py"
            c.retry_count = 0
            reset_count += 1

    if reset_count > 0:
        await session.commit()
    return reset_count


async def fix_all_no_targets(session) -> int:
    """Assign correct bot targets to NEW claims where all targets are 'No'."""
    q = select(ClaimRecord).where(
        ClaimRecord.record_status == RecordStatusEnum.NEW,
        ClaimRecord.fl_website_broward == "No",
        ClaimRecord.fl_website_hillsborough == "No",
        ClaimRecord.fl_website_miami == "No",
        ClaimRecord.te_website_travis == "No",
        ClaimRecord.te_website_dallas == "No",
        ClaimRecord.te_website_harris == "No",
        ClaimRecord.te_website_cclerk == "No",
        ClaimRecord.te_website_hcdistrict == "No",
    )
    res = await session.execute(q)
    claims = res.scalars().all()

    fixed_count = 0
    for c in claims:
        targets = resolve_county_bot_targets(c.policy_state, c.loss_location_state)
        # Check if any target is Yes (non-trivial resolution)
        if any(v == "Yes" for v in targets.values()):
            print(
                f"  [FIX]   Claim {c.claim_number} (Policy={c.policy_state}, Loss={c.loss_location_state}) "
                f"-> targets: { {k: v for k, v in targets.items() if v == 'Yes'} }"
            )
            c.fl_website_broward = targets.get("fl_broward", "No")
            c.fl_website_hillsborough = targets.get("fl_hillsborough", "No")
            c.fl_website_miami = targets.get("fl_miami", "No")
            c.te_website_travis = targets.get("te_travis", "No")
            c.te_website_dallas = targets.get("te_dallas", "No")
            c.te_website_harris = targets.get("te_harris", "No")
            c.te_website_cclerk = targets.get("te_cclerk", "No")
            c.te_website_hcdistrict = targets.get("te_hcdistrict", "No")
            fixed_count += 1
        else:
            print(
                f"  [WARN]  Claim {c.claim_number}: resolve_county_bot_targets returned all-No "
                f"for Policy={c.policy_state}, Loss={c.loss_location_state}. Enabling all portals."
            )
            # Enable all 8 as fallback (cross-state / unknown)
            for attr, key in [
                ("fl_website_broward", "fl_broward"),
                ("fl_website_hillsborough", "fl_hillsborough"),
                ("fl_website_miami", "fl_miami"),
                ("te_website_travis", "te_travis"),
                ("te_website_dallas", "te_dallas"),
                ("te_website_harris", "te_harris"),
                ("te_website_cclerk", "te_cclerk"),
                ("te_website_hcdistrict", "te_hcdistrict"),
            ]:
                setattr(c, attr, "Yes")
            fixed_count += 1

    if fixed_count > 0:
        await session.commit()
    return fixed_count


def reset_redis_keys():
    """Reset Redis browser semaphore and queue active-item keys."""
    try:
        import redis
        from app.core.config import settings
        r = redis.Redis.from_url(settings.CELERY_BROKER_URL, socket_connect_timeout=3.0, socket_timeout=3.0)
        r.ping()  # quick check
        deleted = []
        for key in ["uaic:browser:active_count", "uaic:queue:active_item_ids", "uaic:queue:active_item_id"]:
            if r.exists(key):
                r.delete(key)
                deleted.append(key)
        if deleted:
            print(f"  [REDIS] Deleted stale keys: {deleted}")
        else:
            print("  [REDIS] No stale keys found (already clean).")
        return True
    except Exception as e:
        print(f"  [REDIS] Redis not available ({e}) — skipping key reset. This is OK if SEMAPHORE_BYPASS=true.")
        return False


async def main():
    print("=" * 60)
    print("  UAIC Fix Stale Claims — IMP-2026-1002-001")
    print("=" * 60)
    print()

    async with TaskAsyncSessionLocal() as session:
        print("PHASE 1: Reset stale SCRAPING_IN_PROGRESS claims...")
        reset_count = await fix_stale_in_progress(session)
        print(f"  -> Reset {reset_count} stale in-progress claim(s) to NEW.")
        print()

        print("PHASE 2: Fix claims with all bot targets = No...")
        fixed_count = await fix_all_no_targets(session)
        print(f"  → Fixed {fixed_count} claim(s) with all-No bot targets.")
        print()

    print("PHASE 3: Reset Redis stale semaphore/queue keys...")
    reset_redis_keys()
    print()

    print("=" * 60)
    print(f"  DONE: {reset_count} stale claims reset, {fixed_count} bot-target fixes applied.")
    print("  Next: Restart backend workers to begin processing NEW claims.")
    print("=" * 60)


asyncio.run(main())
