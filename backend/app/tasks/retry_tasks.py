"""Celery Retry Tasks (Replacing legacy RetriggerFailedCases cloud flow)."""

import asyncio
import logging

from sqlalchemy import select

from app.core.celery_app import celery_app
from app.core.database import TaskAsyncSessionLocal
from app.models.claim import ClaimRecord, RecordStatusEnum

logger = logging.getLogger("uaic_orchestrator.tasks.retry")


async def _async_retrigger_failed_cases():
    """Async helper to find and retrigger failed claims."""
    async with TaskAsyncSessionLocal() as session:
        query = select(ClaimRecord).where(ClaimRecord.record_status == RecordStatusEnum.FAILED)
        res = await session.execute(query)
        failed_claims = res.scalars().all()
        
        if not failed_claims:
            logger.info("Scheduled retry: No failed claims found.")
            return

        logger.info(f"Scheduled retry: Found {len(failed_claims)} failed claims to reprocess.")
        for claim in failed_claims:
            claim.record_status = RecordStatusEnum.NEW
            claim.retry_count += 1
            celery_app.send_task(
                "app.tasks.scraper_tasks.orchestrate_court_scrapers_task",
                args=[claim.id, None, True],
                queue="scrapers",
            )

        await session.commit()
        logger.info(f"Scheduled retry: Successfully retriggered {len(failed_claims)} claims (failed portals only).")


@celery_app.task(name="app.tasks.retry_tasks.retrigger_failed_cases_task")
def retrigger_failed_cases_task():
    """Periodic Celery Beat task to reprocess failed cases automatically."""
    logger.info("Running periodic failed case retrigger task...")
    asyncio.run(_async_retrigger_failed_cases())
