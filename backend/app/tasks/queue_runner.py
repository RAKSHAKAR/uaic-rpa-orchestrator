"""Multi-Worker Automatic Queue Runner Task.

Executes queue items concurrently up to configured max_concurrent_claims (1 to 10 parallel claims)
when automatic mode is enabled, with seamless sequential fallback when concurrency is set to 1.
"""

import asyncio
import logging

import redis
from sqlalchemy import select

from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.database import TaskAsyncSessionLocal
from app.models.claim import ClaimRecord, RecordStatusEnum

logger = logging.getLogger("uaic_orchestrator.tasks.queue_runner")

AUTO_MODE_KEY = "uaic:queue:auto_mode"
ACTIVE_ITEM_KEY = "uaic:queue:active_item_id"
ACTIVE_ITEMS_SET_KEY = "uaic:queue:active_item_ids"


def get_redis_client() -> redis.Redis:
    return redis.Redis.from_url(settings.CELERY_BROKER_URL, socket_connect_timeout=1.0, socket_timeout=1.0)


def is_auto_queue_enabled() -> bool:
    try:
        r = get_redis_client()
        val = r.get(AUTO_MODE_KEY)
        if val is None:
            # Enabled by default
            r.set(AUTO_MODE_KEY, "true")
            return True
        return val == b"true" or val == b"1" or val == "true"
    except Exception as e:
        logger.warning(f"Could not read auto_queue_enabled from Redis: {e}")
        return True


def set_auto_queue_enabled(enabled: bool):
    try:
        r = get_redis_client()
        r.set(AUTO_MODE_KEY, "true" if enabled else "false")
    except Exception as e:
        logger.warning(f"Could not set auto_queue_enabled in Redis: {e}")


def get_active_queue_item_ids() -> list[str]:
    """Retrieve all actively running claim IDs from Redis set (with single-item fallback)."""
    try:
        r = get_redis_client()
        items = r.smembers(ACTIVE_ITEMS_SET_KEY)
        if items:
            return [i.decode("utf-8") if isinstance(i, bytes) else str(i) for i in items]
        single = r.get(ACTIVE_ITEM_KEY)
        if single:
            return [single.decode("utf-8") if isinstance(single, bytes) else str(single)]
        return []
    except Exception:
        return []


def add_active_queue_item_id(item_id: str):
    """Register an actively running claim ID in Redis."""
    try:
        r = get_redis_client()
        r.sadd(ACTIVE_ITEMS_SET_KEY, item_id)
        r.expire(ACTIVE_ITEMS_SET_KEY, 7200)
        # Also maintain single-item key for backward compatibility
        r.set(ACTIVE_ITEM_KEY, item_id, ex=3600)
    except Exception:
        pass


def remove_active_queue_item_id(item_id: str):
    """Deregister a claim ID from the active Redis set."""
    try:
        r = get_redis_client()
        r.srem(ACTIVE_ITEMS_SET_KEY, item_id)
        curr = r.get(ACTIVE_ITEM_KEY)
        if curr and (curr.decode("utf-8") if isinstance(curr, bytes) else str(curr)) == item_id:
            # If the single key was pointing to this item, update or delete
            remaining = r.smembers(ACTIVE_ITEMS_SET_KEY)
            if remaining:
                next_item = next(iter(remaining))
                r.set(ACTIVE_ITEM_KEY, next_item, ex=3600)
            else:
                r.delete(ACTIVE_ITEM_KEY)
    except Exception:
        pass


def clear_all_active_queue_items():
    """Clear all active running claim locks in Redis."""
    try:
        r = get_redis_client()
        r.delete(ACTIVE_ITEMS_SET_KEY)
        r.delete(ACTIVE_ITEM_KEY)
    except Exception:
        pass


def get_active_queue_item_id() -> str:
    """Backward compatibility helper returning primary active claim ID."""
    ids = get_active_queue_item_ids()
    return ids[0] if ids else ""


def set_active_queue_item_id(item_id: str):
    """Backward compatibility helper to set or clear active queue item ID."""
    if item_id:
        add_active_queue_item_id(item_id)
    else:
        clear_all_active_queue_items()


async def _async_advance_auto_queue():
    """Pick and execute eligible claim records concurrently up to configured max_concurrent_claims."""
    if not is_auto_queue_enabled():
        logger.info("Automatic queue runner is OFF. Halting queue advancement.")
        return

    from app.services.settings_service import get_system_settings_async
    runtime_settings = await get_system_settings_async()
    queue_cfg = runtime_settings.queue
    auto_cfg = runtime_settings.automation
    max_concurrency = getattr(auto_cfg, "max_concurrent_claims", None) or getattr(queue_cfg, "max_concurrent_claims", 3)
    max_concurrency = max(1, min(10, int(max_concurrency)))

    async with TaskAsyncSessionLocal() as session:
        # Check active claims currently in progress in DB
        active_q = select(ClaimRecord).where(ClaimRecord.record_status == RecordStatusEnum.SCRAPING_IN_PROGRESS)
        res_active = await session.execute(active_q)
        active_claims = list(res_active.scalars().all())
        current_active_ids = {c.id for c in active_claims}

        # Synchronize Redis active set with database reality
        redis_ids = set(get_active_queue_item_ids())
        for dead_id in (redis_ids - current_active_ids):
            remove_active_queue_item_id(dead_id)
        for live_id in current_active_ids:
            add_active_queue_item_id(live_id)

        available_slots = max_concurrency - len(active_claims)
        if available_slots <= 0:
            logger.info(f"All {max_concurrency} worker slots are active ({len(active_claims)} in progress). Waiting.")
            return

        logger.info(f"Queue runner: {len(active_claims)}/{max_concurrency} slots busy. {available_slots} slots available.")

        # Pick up to available_slots NEW claims in FIFO order
        query = (
            select(ClaimRecord)
            .where(ClaimRecord.record_status == RecordStatusEnum.NEW)
            .order_by(ClaimRecord.created_at.asc())
            .limit(available_slots)
        )
        res = await session.execute(query)
        claims_to_run = list(res.scalars().all())

        # If more slots available, check for retryable failed claims if enabled
        if len(claims_to_run) < available_slots and queue_cfg.auto_retry_failed_scrapes:
            needed = available_slots - len(claims_to_run)
            failed_q = (
                select(ClaimRecord)
                .where(
                    ClaimRecord.record_status == RecordStatusEnum.FAILED,
                    ClaimRecord.retry_count < queue_cfg.max_task_retries,
                )
                .order_by(ClaimRecord.created_at.asc())
                .limit(needed)
            )
            res_failed = await session.execute(failed_q)
            failed_claims = list(res_failed.scalars().all())
            claims_to_run.extend(failed_claims)

        if not claims_to_run:
            if len(active_claims) == 0:
                logger.info("Automatic Queue: No more claims to process. Queue completed.")
                clear_all_active_queue_items()
            return

        # Mark selected claims and dispatch Celery tasks concurrently
        for claim in claims_to_run:
            logger.info(f"Automatic Queue: Dispatching parallel worker for Claim {claim.claim_number} (ID: {claim.id})")
            claim.record_status = RecordStatusEnum.SCRAPING_IN_PROGRESS
            claim.retry_count += 1
            add_active_queue_item_id(claim.id)
            celery_app.send_task(
                "app.tasks.scraper_tasks.orchestrate_court_scrapers_task",
                args=[claim.id],
                queue="scrapers",
            )

        await session.commit()


@celery_app.task(name="app.tasks.queue_runner.advance_auto_queue_task")
def advance_auto_queue_task():
    """Celery task entrypoint for auto-queue step."""
    asyncio.run(_async_advance_auto_queue())
