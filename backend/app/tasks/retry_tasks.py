"""Celery Retry Tasks (Replacing legacy RetriggerFailedCases cloud flow)."""

import asyncio
import logging
from datetime import timedelta

from sqlalchemy import and_, or_, select

from app.core.celery_app import celery_app
from app.core.database import TaskAsyncSessionLocal
from app.models.claim import BotStatusEnum, ClaimRecord, RecordStatusEnum
from app.services.cooldown_service import is_portal_in_cooldown
from app.services.settings_service import get_system_settings_async

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
    queue_cfg = (await get_system_settings_async()).queue
    if not queue_cfg.auto_retry_failed_scrapes or queue_cfg.max_task_retries == 0:
        logger.info("Scheduled retry is disabled in Settings.")
        return

    from app.compat import utc_now
    from app.tasks.queue_runner import (
        add_active_queue_item_id,
        get_active_queue_item_ids,
        remove_active_queue_item_id,
    )

    max_concurrency = max(1, getattr(queue_cfg, "max_concurrent_claims", 10) or 10)
    active_ids = get_active_queue_item_ids()
    available_slots = max(0, max_concurrency - len(active_ids))
    if available_slots <= 0:
        logger.info(
            f"Scheduled retry: All {max_concurrency} worker slots are busy ({len(active_ids)} active). Deferring retry."
        )
        return

    interval_seconds = getattr(queue_cfg, "failed_claims_retry_interval_seconds", None)
    if not interval_seconds or interval_seconds <= 0:
        interval_minutes = getattr(queue_cfg, "failed_claims_retry_interval_minutes", 0) or 0
        if interval_minutes > 0:
            interval_seconds = interval_minutes * 60
        else:
            interval_seconds = getattr(queue_cfg, "task_retry_delay_seconds", 30) or 30
    retry_threshold = utc_now() - timedelta(seconds=interval_seconds)
    async with TaskAsyncSessionLocal() as session:
        is_worker_restart_clause = ClaimRecord.last_error.ilike("%worker restart%")
        has_blocked_or_failed_portal = or_(
            ClaimRecord.fl_botstatus_broward.in_([BotStatusEnum.FAILED, BotStatusEnum.BLOCKED]),
            ClaimRecord.fl_botstatus_hillsborough.in_(
                [BotStatusEnum.FAILED, BotStatusEnum.BLOCKED]
            ),
            ClaimRecord.fl_botstatus_miami.in_([BotStatusEnum.FAILED, BotStatusEnum.BLOCKED]),
            ClaimRecord.te_botstatus_travis.in_([BotStatusEnum.FAILED, BotStatusEnum.BLOCKED]),
            ClaimRecord.te_botstatus_dallas.in_([BotStatusEnum.FAILED, BotStatusEnum.BLOCKED]),
            ClaimRecord.te_botstatus_harris.in_([BotStatusEnum.FAILED, BotStatusEnum.BLOCKED]),
            ClaimRecord.te_botstatus_cclerk.in_([BotStatusEnum.FAILED, BotStatusEnum.BLOCKED]),
            ClaimRecord.te_botstatus_hcdistrict.in_([BotStatusEnum.FAILED, BotStatusEnum.BLOCKED]),
        )
        claim_qualification_clause = or_(
            ClaimRecord.record_status == RecordStatusEnum.FAILED,
            and_(
                ClaimRecord.record_status.in_(
                    [
                        RecordStatusEnum.SCRAPING_COMPLETED,
                        RecordStatusEnum.NO_MATCH_FOUND,
                    ]
                ),
                has_blocked_or_failed_portal,
            ),
        )
        query = (
            select(ClaimRecord)
            .where(
                claim_qualification_clause,
                or_(
                    ClaimRecord.retry_count < queue_cfg.max_task_retries,
                    is_worker_restart_clause,
                ),
                ClaimRecord.updated_at <= retry_threshold,
            )
            .order_by(ClaimRecord.created_at.asc())
            .limit(available_slots)
            .with_for_update(skip_locked=True)
        )
        res = await session.execute(query)
        failed_claims = res.scalars().all()

        if not failed_claims:
            logger.info("Scheduled retry: No failed claims found.")
            return

        logger.info(
            f"Scheduled retry: Found {len(failed_claims)} candidate claims with failed/blocked portals to inspect (slots available: {available_slots})."
        )
        retriggered_count = 0
        for claim in failed_claims:
            # Check if all failed/blocked portals for this claim are currently in cooldown
            failed_portal_keys = [
                portal_key
                for portal_key, status_field in PORTAL_STATUS_FIELDS
                if getattr(claim, status_field, None)
                in (
                    BotStatusEnum.FAILED,
                    BotStatusEnum.BLOCKED,
                    "FAILED",
                    "BLOCKED",
                )
            ]
            if failed_portal_keys:
                all_in_cooldown = all(is_portal_in_cooldown(pk)[0] for pk in failed_portal_keys)
                if all_in_cooldown:
                    logger.info(
                        f"Claim {claim.claim_number}: All failed portals ({failed_portal_keys}) "
                        "are actively in security cooldown. Deferring retry to next cycle."
                    )
                    continue

            # Mark active before dispatch so the auto-queue cannot pick the
            # same claim as a separate NEW item.
            is_worker_restart = bool(
                claim.last_error and "worker restart" in claim.last_error.lower()
            )
            timings = claim.action_timings if isinstance(claim.action_timings, dict) else {}
            has_zero_portals = not timings.get("portals")

            claim.record_status = RecordStatusEnum.SCRAPING_IN_PROGRESS
            if is_worker_restart and has_zero_portals:
                claim.retry_count = 0
                for _pk, status_field in PORTAL_STATUS_FIELDS:
                    if getattr(claim, status_field, None) in (
                        BotStatusEnum.FAILED,
                        BotStatusEnum.BLOCKED,
                        "FAILED",
                        "BLOCKED",
                    ):
                        setattr(claim, status_field, BotStatusEnum.NOT_TRIGGERED)
            else:
                claim.retry_count = (claim.retry_count or 0) + 1
            claim.last_error = None

            # Preserve status flags for normal retries so retry_failed_only correctly isolates target portals.
            retriggered_count += 1
        await session.commit()
        dispatches = [
            claim
            for claim in failed_claims
            if claim.record_status == RecordStatusEnum.SCRAPING_IN_PROGRESS
        ]
        for dispatch_index, claim in enumerate(dispatches):
            try:
                add_active_queue_item_id(claim.id)
                celery_app.send_task(
                    "app.tasks.scraper_tasks.orchestrate_court_scrapers_task",
                    args=[claim.id, None, True],
                    queue="scrapers",
                )
            except Exception:
                remove_active_queue_item_id(claim.id)
                for unsent_claim in dispatches[dispatch_index:]:
                    unsent_claim.record_status = RecordStatusEnum.FAILED
                    unsent_claim.retry_count -= 1
                    remove_active_queue_item_id(unsent_claim.id)
                await session.commit()
                raise
        logger.info(
            f"Scheduled retry: Successfully retriggered {retriggered_count}/{len(failed_claims)} claims (failed portals only)."
        )


@celery_app.task(name="app.tasks.retry_tasks.retrigger_failed_cases_task")
def retrigger_failed_cases_task():
    """Periodic Celery Beat task to reprocess failed cases automatically."""
    logger.info("Running periodic failed case retrigger task...")
    asyncio.run(_async_retrigger_failed_cases())
