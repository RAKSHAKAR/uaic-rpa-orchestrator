"""Multi-Worker Automatic Queue Runner Task.

Executes queue items concurrently up to configured max_concurrent_claims (1 to 10 parallel claims)
when automatic mode is enabled, with seamless sequential fallback when concurrency is set to 1.
"""

import asyncio
import logging
from datetime import timedelta

import redis
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.compat import utc_now
from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.database import TaskAsyncSessionLocal
from app.models.claim import BotStatusEnum, ClaimRecord, FuzzyMatchStatusEnum, RecordStatusEnum

logger = logging.getLogger("uaic_orchestrator.tasks.queue_runner")

AUTO_MODE_KEY = "uaic:queue:auto_mode"
ACTIVE_ITEM_KEY = "uaic:queue:active_item_id"
ACTIVE_ITEMS_SET_KEY = "uaic:queue:active_item_ids"
BROWSER_ACTIVE_SET_KEY = "uaic:browser:active_claims"

BOT_STATUS_ATTRS = (
    "fl_botstatus_broward",
    "fl_botstatus_hillsborough",
    "fl_botstatus_miami",
    "te_botstatus_travis",
    "te_botstatus_dallas",
    "te_botstatus_harris",
    "te_botstatus_cclerk",
    "te_botstatus_hcdistrict",
)

# Fast in-memory state fallback & bypass
_IN_MEMORY_AUTO_MODE: bool = True
_IN_MEMORY_ACTIVE_IDS: set[str] = set()


_REDIS_OFFLINE_UNTIL: float = 0.0


def _can_try_redis() -> bool:
    import time

    global _REDIS_OFFLINE_UNTIL
    if getattr(settings, "SEMAPHORE_BYPASS", False):
        return False
    return time.monotonic() > _REDIS_OFFLINE_UNTIL


def _mark_redis_failure():
    import time

    global _REDIS_OFFLINE_UNTIL
    _REDIS_OFFLINE_UNTIL = time.monotonic() + 5.0


def get_redis_client() -> redis.Redis:
    return redis.Redis.from_url(
        settings.CELERY_BROKER_URL, socket_connect_timeout=0.2, socket_timeout=0.2
    )


def is_auto_queue_enabled() -> bool:
    global _IN_MEMORY_AUTO_MODE
    if not _can_try_redis():
        return _IN_MEMORY_AUTO_MODE
    try:
        r = get_redis_client()
        val = r.get(AUTO_MODE_KEY)
        if val is None:
            # Enabled by default
            try:
                r.set(AUTO_MODE_KEY, "true")
            except Exception:
                pass
            _IN_MEMORY_AUTO_MODE = True
            return True
        enabled = val == b"true" or val == b"1" or val == "true"
        _IN_MEMORY_AUTO_MODE = enabled
        return enabled
    except Exception as e:
        _mark_redis_failure()
        logger.debug(f"Could not read auto_queue_enabled from Redis, using in-memory state: {e}")
        return _IN_MEMORY_AUTO_MODE


def set_auto_queue_enabled(enabled: bool):
    global _IN_MEMORY_AUTO_MODE
    _IN_MEMORY_AUTO_MODE = enabled
    if not _can_try_redis():
        return
    try:
        r = get_redis_client()
        r.set(AUTO_MODE_KEY, "true" if enabled else "false")
    except Exception as e:
        _mark_redis_failure()
        logger.debug(f"Could not set auto_queue_enabled in Redis: {e}")


def get_active_queue_item_ids() -> list[str]:
    """Retrieve all actively running claim IDs from Redis set (with single-item fallback and in-memory bypass)."""
    global _IN_MEMORY_ACTIVE_IDS
    if not _can_try_redis():
        return list(_IN_MEMORY_ACTIVE_IDS)
    try:
        r = get_redis_client()
        items = r.smembers(ACTIVE_ITEMS_SET_KEY)
        if items:
            res = [i.decode("utf-8") if isinstance(i, bytes) else str(i) for i in items]
            _IN_MEMORY_ACTIVE_IDS = set(res)
            return res
        single = r.get(ACTIVE_ITEM_KEY)
        if single:
            s_val = single.decode("utf-8") if isinstance(single, bytes) else str(single)
            _IN_MEMORY_ACTIVE_IDS = {s_val}
            return [s_val]
        _IN_MEMORY_ACTIVE_IDS.clear()
        return []
    except Exception:
        _mark_redis_failure()
        return list(_IN_MEMORY_ACTIVE_IDS)


def add_active_queue_item_id(item_id: str):
    """Register an actively running claim ID in Redis and in-memory set."""
    global _IN_MEMORY_ACTIVE_IDS
    _IN_MEMORY_ACTIVE_IDS.add(item_id)
    if not _can_try_redis():
        return
    try:
        r = get_redis_client()
        r.sadd(ACTIVE_ITEMS_SET_KEY, item_id)
        r.expire(ACTIVE_ITEMS_SET_KEY, 7200)
        # Also maintain single-item key for backward compatibility
        r.set(ACTIVE_ITEM_KEY, item_id, ex=3600)
    except Exception:
        _mark_redis_failure()


def remove_active_queue_item_id(item_id: str):
    """Deregister a claim ID from the active Redis set, browser slot set, and in-memory tracking."""
    global _IN_MEMORY_ACTIVE_IDS
    _IN_MEMORY_ACTIVE_IDS.discard(item_id)
    if not _can_try_redis():
        return
    try:
        r = get_redis_client()
        r.srem(ACTIVE_ITEMS_SET_KEY, item_id)
        r.srem(BROWSER_ACTIVE_SET_KEY, item_id)
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
        _mark_redis_failure()


def clear_all_active_queue_items():
    """Clear all active running claim locks and browser slot sets in Redis and in-memory."""
    global _IN_MEMORY_ACTIVE_IDS
    _IN_MEMORY_ACTIVE_IDS.clear()
    if not _can_try_redis():
        return
    try:
        r = get_redis_client()
        r.delete(ACTIVE_ITEMS_SET_KEY)
        r.delete(ACTIVE_ITEM_KEY)
        r.delete(BROWSER_ACTIVE_SET_KEY)
        r.delete("uaic:browser:active_count")
    except Exception:
        _mark_redis_failure()


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


async def reconcile_stale_active_claims_async(
    session: AsyncSession,
    claim_id: str | None = None,
    force: bool = False,
) -> int:
    """Detect and auto-evict zombie/stale claims stuck in SCRAPING_IN_PROGRESS.

    Cross-references Celery worker active tasks. If a claim has no active Celery task
    and has not been updated for > 120s, or if > 300s (5m timeout), or if force=True,
    it is automatically evicted, re-queued as NEW (or FAILED if retries exhausted),
    and removed from active concurrency sets.
    """
    from app.services.settings_service import get_system_settings_async

    runtime_settings = await get_system_settings_async()
    queue_cfg = runtime_settings.queue
    max_retries = getattr(queue_cfg, "max_task_retries", 3)

    query = select(ClaimRecord).where(
        ClaimRecord.record_status == RecordStatusEnum.SCRAPING_IN_PROGRESS
    )
    if claim_id:
        query = query.where(ClaimRecord.id == claim_id)

    res = await session.execute(query)
    candidates = list(res.scalars().all())
    if not candidates:
        return 0

    live_celery_task_claim_ids = set()
    celery_probe_ok = False
    if not force:
        try:

            def _probe():
                insp = celery_app.control.inspect(timeout=0.4)
                active_map = insp.active() if insp else None
                if active_map is not None:
                    c_ids = set()
                    for _w, tasks in active_map.items():
                        for t in tasks or []:
                            if t.get("args") and len(t["args"]) > 0:
                                c_ids.add(str(t["args"][0]))
                            if t.get("kwargs"):
                                c_id = t["kwargs"].get("claim_id")
                                if c_id:
                                    c_ids.add(str(c_id))
                    return True, c_ids
                return False, set()

            celery_probe_ok, live_celery_task_claim_ids = await asyncio.to_thread(_probe)
        except Exception as e_probe:
            logger.debug(f"Celery live inspector probe note: {e_probe}")

    now = utc_now()
    evicted_count = 0

    for c in candidates:
        claim_time = c.updated_at or c.created_at
        claim_time_naive = (
            claim_time.replace(tzinfo=None)
            if (claim_time and getattr(claim_time, "tzinfo", None))
            else claim_time
        )
        age_seconds = (now - claim_time_naive).total_seconds() if claim_time_naive else 0

        # Eviction conditions:
        # 1. Explicit force eviction by operator
        # 2. Confirmed dead orphan: Celery replied, this claim is NOT active, and age > 120s
        # 3. Maximum hard timeout exceeded: age > 720s (12 minutes) regardless of Celery probe
        is_dead_orphan = (
            celery_probe_ok
            and (str(c.id) not in live_celery_task_claim_ids)
            and (age_seconds > 120)
        )
        is_hard_timeout = age_seconds > 720
        should_evict = force or is_dead_orphan or is_hard_timeout

        if should_evict:
            timings = c.action_timings if isinstance(c.action_timings, dict) else {}
            portals_done = timings.get("portals", [])
            has_portals = bool(portals_done)

            if not has_portals or force:
                c.record_status = RecordStatusEnum.NEW
                c.last_error = (
                    "Manually evicted by operator; re-queued as NEW."
                    if force
                    else "Auto-recovered orphaned in-progress worker; re-queued as NEW without penalty."
                )
            elif (c.retry_count or 0) < max_retries:
                c.retry_count = (c.retry_count or 0) + 1
                c.record_status = RecordStatusEnum.NEW
                c.last_error = f"Automation session timed out (>12m); automatically re-queuing as NEW (attempt {c.retry_count}/{max_retries})."
            else:
                c.record_status = RecordStatusEnum.FAILED
                c.last_error = (
                    f"Automation session timed out (>12m); max retries ({max_retries}) exhausted."
                )

            for bot_attr in BOT_STATUS_ATTRS:
                if getattr(c, bot_attr) == BotStatusEnum.IN_PROGRESS:
                    setattr(c, bot_attr, BotStatusEnum.NOT_TRIGGERED)

            remove_active_queue_item_id(str(c.id))
            evicted_count += 1
            logger.info(
                f"Evicted stale in-progress claim {c.claim_number} ({c.id}) -> {c.record_status} (age={age_seconds:.1f}s)"
            )

    if evicted_count > 0:
        await session.commit()

    return evicted_count


async def reconcile_worker_restart_claims_async() -> int:
    """Auto-recover claims interrupted by Celery worker restarts, crashes, or redeployments.

    Identifies any claims stranded in SCRAPING_IN_PROGRESS or marked FAILED due to worker restart interruption.
    Clears stale Redis active queue and browser locks, resets in-flight bot status flags back to NOT_TRIGGERED,
    and reverts claim status to NEW. If zero portals were attempted, retry_count is reset to 0 to avoid penalizing
    claims for infrastructure restarts.
    """
    clear_all_active_queue_items()
    if _can_try_redis():
        try:
            r = get_redis_client()
            r.delete(BROWSER_ACTIVE_SET_KEY)
            r.delete("uaic:browser:active_count")
        except Exception as e:
            logger.debug(f"Could not clear browser active keys in Redis: {e}")

    recovered_count = 0
    async with TaskAsyncSessionLocal() as session:
        query = select(ClaimRecord).where(
            or_(
                ClaimRecord.record_status == RecordStatusEnum.SCRAPING_IN_PROGRESS,
                and_(
                    ClaimRecord.record_status == RecordStatusEnum.FAILED,
                    ClaimRecord.last_error.ilike("%worker restart%"),
                ),
            )
        )
        res = await session.execute(query)
        stranded_claims = res.scalars().all()

        if not stranded_claims:
            logger.info("Worker boot auto-recovery: No interrupted claims to reconcile.")
            return 0

        logger.info(
            f"Worker boot auto-recovery: Found {len(stranded_claims)} interrupted claims. Reconciling..."
        )
        for claim in stranded_claims:
            timings = claim.action_timings if isinstance(claim.action_timings, dict) else {}
            portals = timings.get("portals", [])
            has_zero_portals = not portals or len(portals) == 0

            # If interrupted before any portal even began, reset retry_count to 0
            if has_zero_portals:
                claim.retry_count = 0
            else:
                claim.retry_count = max(0, (claim.retry_count or 0) - 1)

            claim.record_status = RecordStatusEnum.NEW
            claim.last_error = (
                "Auto-recovered on worker startup; queued as NEW for fresh execution."
            )

            for attr in BOT_STATUS_ATTRS:
                curr_status = getattr(claim, attr, None)
                if curr_status in (
                    BotStatusEnum.IN_PROGRESS,
                    BotStatusEnum.FAILED,
                    BotStatusEnum.BLOCKED,
                    "IN_PROGRESS",
                    "FAILED",
                    "BLOCKED",
                ):
                    setattr(claim, attr, BotStatusEnum.NOT_TRIGGERED)

            recovered_count += 1
            logger.info(
                f"Auto-recovered claim {claim.claim_number} ({claim.id}) -> NEW "
                f"(zero_portals={has_zero_portals}, retry_count={claim.retry_count})"
            )

        await session.commit()

    logger.info(
        f"Worker boot auto-recovery complete: Successfully reconciled {recovered_count} claims."
    )
    return recovered_count


def reconcile_worker_restart_claims_sync() -> int:
    """Synchronous wrapper for reconcile_worker_restart_claims_async, suitable for Celery startup signals."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(asyncio.run, reconcile_worker_restart_claims_async())
                return future.result()
        else:
            return loop.run_until_complete(reconcile_worker_restart_claims_async())
    except RuntimeError:
        return asyncio.run(reconcile_worker_restart_claims_async())
    except Exception as e:
        logger.error(f"Error during worker startup claim reconciliation: {e}", exc_info=True)
        return 0


async def _async_advance_auto_queue():
    """Pick and execute eligible claim records concurrently up to configured max_concurrent_claims."""
    if not is_auto_queue_enabled():
        logger.info("Automatic queue runner is OFF. Halting queue advancement.")
        return

    from app.services.settings_service import get_system_settings_async

    runtime_settings = await get_system_settings_async()
    queue_cfg = runtime_settings.queue
    auto_cfg = runtime_settings.automation
    # Browser Automation & RPA Execution Fleet is the single operator-facing
    # concurrency control. The legacy queue copy is kept only for migration.
    max_concurrency = auto_cfg.max_concurrent_claims
    max_concurrency = max(1, min(10, int(max_concurrency)))

    async with TaskAsyncSessionLocal() as session:
        # Auto-reconcile and evict any stale/orphaned claims stuck in SCRAPING_IN_PROGRESS
        await reconcile_stale_active_claims_async(session)

        # Check genuine active claims currently in progress in DB
        active_q = select(ClaimRecord).where(
            ClaimRecord.record_status == RecordStatusEnum.SCRAPING_IN_PROGRESS
        )
        res_active = await session.execute(active_q)
        active_claims = list(res_active.scalars().all())

        current_active_ids = {c.id for c in active_claims}

        # Synchronize Redis active set with database reality
        redis_ids = set(get_active_queue_item_ids())
        for dead_id in redis_ids - current_active_ids:
            remove_active_queue_item_id(dead_id)
        for live_id in current_active_ids:
            add_active_queue_item_id(live_id)

        # Synchronize browser active slots set with database reality
        if _can_try_redis():
            try:
                r = get_redis_client()
                raw_b_ids = r.smembers(BROWSER_ACTIVE_SET_KEY) or set()
                for b_id in raw_b_ids:
                    bid_str = b_id.decode("utf-8") if isinstance(b_id, bytes) else str(b_id)
                    if bid_str not in current_active_ids:
                        r.srem(BROWSER_ACTIVE_SET_KEY, bid_str)
                r.delete("uaic:browser:active_count")
            except Exception:
                pass

        available_slots = max_concurrency - len(active_claims)
        if available_slots <= 0:
            logger.info(
                f"All {max_concurrency} worker slots are active ({len(active_claims)} in progress). Waiting."
            )
            return

        logger.info(
            f"Queue runner: {len(active_claims)}/{max_concurrency} slots busy. {available_slots} slots available."
        )

        # Auto-recover claims where scraping completed but fuzzy matching has not yet run
        pending_fuzzy_q = (
            select(ClaimRecord)
            .where(
                ClaimRecord.record_status == RecordStatusEnum.SCRAPING_COMPLETED,
                ClaimRecord.fuzzy_match_status.in_([FuzzyMatchStatusEnum.NEW, None]),
            )
            .limit(5)
        )
        res_fuzzy = await session.execute(pending_fuzzy_q)
        stranded_claims = res_fuzzy.scalars().all()
        for stranded in stranded_claims:
            logger.info(
                f"Auto-queue: dispatching fuzzy matching for claim {stranded.claim_number} ({stranded.id})"
            )
            try:
                celery_app.send_task(
                    "app.tasks.fuzzy_tasks.evaluate_fuzzy_matches_task",
                    args=[stranded.id],
                    queue="matcher",
                )
            except Exception:
                pass
            try:
                from app.tasks.fuzzy_tasks import _async_evaluate_fuzzy_matches

                asyncio.create_task(_async_evaluate_fuzzy_matches(stranded.id))
            except Exception:
                pass

        # Pick up to available_slots NEW claims in FIFO order
        query = (
            select(ClaimRecord)
            .where(ClaimRecord.record_status == RecordStatusEnum.NEW)
            .order_by(ClaimRecord.created_at.asc())
            .limit(available_slots)
            .with_for_update(skip_locked=True)
        )
        res = await session.execute(query)
        claims_to_run = list(res.scalars().all())

        # If more slots available, check for retryable failed claims if enabled
        if len(claims_to_run) < available_slots and queue_cfg.auto_retry_failed_scrapes:
            needed = available_slots - len(claims_to_run)
            interval_seconds = getattr(queue_cfg, "failed_claims_retry_interval_seconds", None)
            if not interval_seconds or interval_seconds <= 0:
                interval_minutes = (
                    getattr(queue_cfg, "failed_claims_retry_interval_minutes", 0) or 0
                )
                if interval_minutes > 0:
                    interval_seconds = interval_minutes * 60
                else:
                    interval_seconds = getattr(queue_cfg, "task_retry_delay_seconds", 30) or 30
            retry_threshold = utc_now() - timedelta(seconds=interval_seconds)
            failed_q = (
                select(ClaimRecord)
                .where(
                    ClaimRecord.record_status == RecordStatusEnum.FAILED,
                    ClaimRecord.retry_count < getattr(queue_cfg, "max_task_retries", 3),
                    ClaimRecord.updated_at <= retry_threshold,
                )
                .order_by(ClaimRecord.created_at.asc())
                .limit(needed)
                .with_for_update(skip_locked=True)
            )
            res_failed = await session.execute(failed_q)
            failed_claims = list(res_failed.scalars().all())
            claims_to_run.extend(failed_claims)

        if not claims_to_run:
            if len(active_claims) == 0:
                logger.info("Automatic Queue: No more claims to process. Queue completed.")
                clear_all_active_queue_items()
            return

        # Claim rows are committed before dispatch so a second queue runner
        # cannot select them while a broker publish is in flight.
        dispatches: list[tuple[str, bool]] = []
        for claim in claims_to_run:
            logger.info(
                f"Automatic Queue: Dispatching parallel worker for Claim {claim.claim_number} (ID: {claim.id})"
            )
            is_retry = claim.record_status == RecordStatusEnum.FAILED
            claim.record_status = RecordStatusEnum.SCRAPING_IN_PROGRESS
            if is_retry:
                claim.retry_count += 1
            add_active_queue_item_id(claim.id)
            dispatches.append((claim.id, is_retry))

        await session.commit()
        for dispatch_index, (claim_id, is_retry) in enumerate(dispatches):
            try:
                celery_app.send_task(
                    "app.tasks.scraper_tasks.orchestrate_court_scrapers_task",
                    kwargs={"claim_id": claim_id, "retry_failed_only": is_retry},
                    queue="scrapers",
                )
            except Exception:
                for unsent_id, unsent_is_retry in dispatches[dispatch_index:]:
                    claim = next(item for item in claims_to_run if item.id == unsent_id)
                    claim.record_status = (
                        RecordStatusEnum.FAILED if unsent_is_retry else RecordStatusEnum.NEW
                    )
                    if unsent_is_retry:
                        claim.retry_count -= 1
                    remove_active_queue_item_id(unsent_id)
                await session.commit()
                raise


@celery_app.task(name="app.tasks.queue_runner.advance_auto_queue_task")
def advance_auto_queue_task():
    """Celery task entrypoint for auto-queue step."""
    asyncio.run(_async_advance_auto_queue())
