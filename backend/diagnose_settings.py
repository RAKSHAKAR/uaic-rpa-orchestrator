"""Diagnostic script to check system settings and claim failure causes."""
import asyncio
import sys
sys.path.insert(0, '.')

async def main():
    from app.services.settings_service import get_system_settings_async
    from app.core.database import TaskAsyncSessionLocal
    from app.models.claim import ClaimRecord, RecordStatusEnum
    from sqlalchemy import select, func

    settings = await get_system_settings_async()
    auto_cfg = settings.automation
    queue_cfg = settings.queue
    portals_cfg = settings.portals

    print("=== AUTOMATION SETTINGS ===")
    print(f"  max_concurrent_claims: {auto_cfg.max_concurrent_claims}")
    print(f"  headless_mode: {auto_cfg.headless_mode}")
    print(f"  use_chrome_browser: {auto_cfg.use_chrome_browser}")
    engine = getattr(auto_cfg, "browser_engine", "N/A")
    print(f"  browser_engine: {engine}")

    print()
    print("=== QUEUE SETTINGS ===")
    print(f"  auto_retry_failed_scrapes: {queue_cfg.auto_retry_failed_scrapes}")
    retries = getattr(queue_cfg, "max_task_retries", "N/A")
    print(f"  max_task_retries: {retries}")
    interval = getattr(queue_cfg, "failed_claims_retry_interval_minutes", "N/A")
    print(f"  failed_claims_retry_interval_minutes: {interval}")

    print()
    print("=== PORTAL SETTINGS ===")
    print(f"  broward_enabled: {portals_cfg.broward_enabled}")
    print(f"  hillsborough_enabled: {portals_cfg.hillsborough_enabled}")
    print(f"  miami_enabled: {portals_cfg.miami_enabled}")
    print(f"  harris_jp_enabled: {portals_cfg.harris_jp_enabled}")
    print(f"  harris_cclerk_enabled: {portals_cfg.harris_cclerk_enabled}")
    print(f"  harris_district_enabled: {portals_cfg.harris_district_enabled}")
    print(f"  dallas_enabled: {portals_cfg.dallas_enabled}")
    print(f"  travis_enabled: {portals_cfg.travis_enabled}")

    print()
    print("=== CLAIM STATUS COUNTS ===")
    async with TaskAsyncSessionLocal() as session:
        q = select(ClaimRecord.record_status, func.count()).group_by(ClaimRecord.record_status)
        res = await session.execute(q)
        for row in res.all():
            status = row[0].value if hasattr(row[0], "value") else row[0]
            print(f"  {status}: {row[1]}")

        print()
        print("=== SAMPLE NEW CLAIMS (check bot targets) ===")
        q2 = select(ClaimRecord).where(ClaimRecord.record_status == RecordStatusEnum.NEW).limit(5)
        res2 = await session.execute(q2)
        for c in res2.scalars().all():
            print(f"  Claim: {c.claim_number}")
            print(f"    PolicyState={c.policy_state}, LossState={c.loss_location_state}")
            print(f"    fl_broward={c.fl_website_broward}, fl_hills={c.fl_website_hillsborough}, fl_miami={c.fl_website_miami}")
            print(f"    te_travis={c.te_website_travis}, te_dallas={c.te_website_dallas}")
            print(f"    te_harris={c.te_website_harris}, te_cclerk={c.te_website_cclerk}, te_hcdistrict={c.te_website_hcdistrict}")
            print(f"    insured={c.insured_first_name} {c.insured_last_name}")
            print(f"    driver={c.driver_first_name} {c.driver_last_name}")
            print(f"    claimant={c.claimant_first_name} {c.claimant_last_name}")
            print()

asyncio.run(main())
