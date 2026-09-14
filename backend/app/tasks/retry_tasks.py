"""Celery Retry Tasks (Replacing legacy RetriggerFailedCases cloud flow)."""

import asyncio
import logging

from sqlalchemy import select

from app.core.celery_app import celery_app
from app.core.database import TaskAsyncSessionLocal
from app.models.claim import BotStatusEnum, ClaimRecord, RecordStatusEnum
from app.services.cooldown_service import is_portal_in_cooldown

logger = logging.getLogger("uaic_orchestrator.tasks.retry")

PORTAL_STATUS_FIELDS = [
    ("broward", "fl_botstatus_broward"),
    ("hillsborough", "fl_botstatus_hillsborough"),
    ("miami", "fl_botstatus_miami"),
    ("travis", "te_botstatus_travis"),
    ("dallas", "te_botstatus_dallas"),
    ("harris_jp", "te_botstatus_harris"),
    ("harris_cclerk", "te_botstatus_cclerk"),
    ("harris_district", "te_botstatus_hcdistrict"),
]


async def _async_retrigger_failed_cases():
    """Async helper to find and retrigger failed claims honoring portal cooldowns."""
    async with TaskAsyncSessionLocal() as session:
        query = select(ClaimRecord).where(ClaimRecord.record_status == RecordStatusEnum.FAILED)
        res = await session.execute(query)
        failed_claims = res.scalars().all()

        if not failed_claims:
            logger.info("Scheduled retry: No failed claims found.")
            return

        logger.info(f"Scheduled retry: Found {len(failed_claims)} failed claims to inspect.")
        retriggered_count = 0
        for claim in failed_claims:
            # Check if all failed/blocked portals for this claim are currently in cooldown
            failed_portal_keys = [
                portal_key for portal_key, status_field in PORTAL_STATUS_FIELDS
                if getattr(claim, status_field, None) in (
                    BotStatusEnum.FAILED,
                    BotStatusEnum.BLOCKED,
                    "FAILED",
                    "BLOCKED",
                )
            ]
            if failed_portal_keys:
                all_in_cooldown = all(
                    is_portal_in_cooldown(pk)[0] for pk in failed_portal_keys
                )
                if all_in_cooldown:
                    logger.info(
                        f"Claim {claim.claim_number}: All failed portals ({failed_portal_keys}) "
                        "are actively in security cooldown. Deferring retry to next cycle."
                    )
                    continue

            claim.record_status = RecordStatusEnum.NEW
            claim.retry_count += 1
            retriggered_count += 1
            celery_app.send_task(
                "app.tasks.scraper_tasks.orchestrate_court_scrapers_task",
                args=[claim.id, None, True],
                queue="scrapers",
            )

        await session.commit()
        logger.info(f"Scheduled retry: Successfully retriggered {retriggered_count}/{len(failed_claims)} claims (failed portals only).")


@celery_app.task(name="app.tasks.retry_tasks.retrigger_failed_cases_task")
def retrigger_failed_cases_task():
    """Periodic Celery Beat task to reprocess failed cases automatically."""
    logger.info("Running periodic failed case retrigger task...")
    asyncio.run(_async_retrigger_failed_cases())
