import logging

import redis
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.database import get_db
from app.models.claim import ClaimRecord, RecordStatusEnum
from app.schemas.queue import (
    ConcurrencyUpdateRequest,
    LiveQueueItemResponse,
    LiveQueueStateResponse,
    QueueStatusResponse,
    RetriggerRequest,
    RunSelectedQueueRequest,
    SeedDemoClaimsRequest,
)
from app.services.audit_service import extract_client_context, record_audit_event_background
from app.services.settings_service import get_system_settings_async

logger = logging.getLogger("uaic_orchestrator.queue")
router = APIRouter()

async def _validate_anticaptcha():
    settings_obj = await get_system_settings_async()
    if not settings_obj.automation.anticaptcha_api_key or not settings_obj.automation.anticaptcha_api_key.strip():
        raise HTTPException(
            status_code=422,
            detail="Anti-Captcha API key is not configured in Automation Settings. Cannot start scrapers."
        )


def _format_live_queue_item(claim: ClaimRecord, position: int | None = None) -> LiveQueueItemResponse:
    """Format ClaimRecord into a structured LiveQueueItemResponse with portal coverage."""
    policy_st = (claim.policy_state or "").upper()
    loss_st = (claim.loss_location_state or "").upper()
    is_fl = "FL" in policy_st or "FLORIDA" in policy_st
    is_tx = "TX" in policy_st or "TEXAS" in policy_st
    loss_fl = "FL" in loss_st or "FLORIDA" in loss_st
    loss_tx = "TX" in loss_st or "TEXAS" in loss_st

    if is_fl and loss_fl:
        portals = ["Broward", "Hillsborough", "Miami-Dade"]
    elif is_tx and loss_tx:
        portals = ["Harris County Clerk", "Dallas", "Harris JP", "Harris District", "Travis"]
    else:
        portals = [
            "Broward", "Hillsborough", "Miami-Dade",
            "Harris County Clerk", "Dallas", "Harris JP", "Harris District", "Travis"
        ]

    bot_statuses = {
        "fl_broward": str(claim.fl_botstatus_broward.value if hasattr(claim.fl_botstatus_broward, "value") else claim.fl_botstatus_broward),
        "fl_hillsborough": str(claim.fl_botstatus_hillsborough.value if hasattr(claim.fl_botstatus_hillsborough, "value") else claim.fl_botstatus_hillsborough),
        "fl_miami": str(claim.fl_botstatus_miami.value if hasattr(claim.fl_botstatus_miami, "value") else claim.fl_botstatus_miami),
        "te_travis": str(claim.te_botstatus_travis.value if hasattr(claim.te_botstatus_travis, "value") else claim.te_botstatus_travis),
        "te_dallas": str(claim.te_botstatus_dallas.value if hasattr(claim.te_botstatus_dallas, "value") else claim.te_botstatus_dallas),
        "te_harris": str(claim.te_botstatus_harris.value if hasattr(claim.te_botstatus_harris, "value") else claim.te_botstatus_harris),
        "te_cclerk": str(claim.te_botstatus_cclerk.value if hasattr(claim.te_botstatus_cclerk, "value") else claim.te_botstatus_cclerk),
    }

    insured = f"{claim.insured_first_name or ''} {claim.insured_last_name or ''}".strip() or None
    claimant = f"{claim.claimant_first_name or ''} {claim.claimant_last_name or ''}".strip() or None
    driver = f"{claim.driver_first_name or ''} {claim.driver_last_name or ''}".strip() or None

    return LiveQueueItemResponse(
        id=claim.id,
        claim_number=claim.claim_number,
        exposure_number=claim.exposure_number,
        insured_name=insured,
        claimant_name=claimant,
        driver_name=driver,
        dol=claim.dol,
        policy_state=claim.policy_state,
        loss_location_state=claim.loss_location_state,
        record_status=str(claim.record_status.value if hasattr(claim.record_status, "value") else claim.record_status),
        fuzzy_match_status=str(claim.fuzzy_match_status.value if hasattr(claim.fuzzy_match_status, "value") else claim.fuzzy_match_status),
        queue_position=position,
        portals_to_run=portals,
        bot_statuses=bot_statuses,
        total_duration_seconds=claim.total_duration_seconds,
        current_portal=None,
        created_at=claim.created_at,
        updated_at=claim.updated_at,
    )


@router.get("/status", response_model=QueueStatusResponse)
async def get_queue_status():
    """Inspect active Celery workers, registered tasks, and real Redis queue lengths."""
    queues = {
        "ingest": 0,
        "scrapers": 0,
        "matcher": 0,
        "notifications": 0,
        "default": 0,
    }
    
    # 1. Fetch real pending queue depths from Redis
    try:
        r = redis.Redis.from_url(settings.CELERY_BROKER_URL, socket_connect_timeout=0.5, socket_timeout=0.5)
        for q_name in queues:
            queues[q_name] = r.llen(q_name) or 0
    except Exception as e:
        logger.warning(f"Could not read Redis queue lengths: {e}")

    # 2. Inspect active workers and tasks
    total_active = 0
    workers_online = 0
    
    try:
        ping_res = celery_app.control.ping(timeout=0.5) or []
        workers_online = len(ping_res)
    except Exception:
        workers_online = 0

    return QueueStatusResponse(
        active_tasks=total_active,
        pending_tasks=sum(queues.values()),
        failed_tasks=0,
        completed_tasks=0,
        queues=queues,
        workers_online=workers_online,
    )


@router.post("/retrigger")
async def retrigger_failed_claims(
    request: Request = None,
    payload: RetriggerRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Manually retrigger failed or stuck claims for RPA scraping and fuzzy matching."""
    await _validate_anticaptcha()
    
    query = select(ClaimRecord)
    
    if payload and payload.claim_ids:
        query = query.where(ClaimRecord.id.in_(payload.claim_ids))
    else:
        # Retrigger failed or stuck claims
        query = query.where(
            or_(
                ClaimRecord.record_status == RecordStatusEnum.FAILED,
                ClaimRecord.record_status == RecordStatusEnum.SCRAPING_IN_PROGRESS,
            )
        ).limit(50)

    res = await db.execute(query)
    claims_to_retrigger = res.scalars().all()
    
    if not claims_to_retrigger:
        return {"message": "No matching claims found to retrigger", "count": 0}

    retriggered_ids = []
    for claim in claims_to_retrigger:
        claim.record_status = RecordStatusEnum.NEW
        claim.retry_count += 1
        retriggered_ids.append(claim.id)
        
        # Dispatch Celery scraping orchestrator task
        celery_app.send_task(
            "app.tasks.scraper_tasks.orchestrate_court_scrapers_task",
            args=[claim.id],
            queue="scrapers",
        )

    await db.commit()

    ctx = extract_client_context(request)
    record_audit_event_background(
        action="QUEUE_RETRIGGERED",
        entity_type="QUEUE",
        description=f"Operator manually retriggered {len(retriggered_ids)} failed/stuck claims",
        user_id=ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="SUCCESS",
        details={"retriggered_count": len(retriggered_ids), "claim_ids": [str(cid) for cid in retriggered_ids]},
    )

    return {
        "message": f"Successfully retriggered {len(retriggered_ids)} claims",
        "count": len(retriggered_ids),
        "claim_ids": retriggered_ids,
    }


@router.get("/auto-mode")
async def get_auto_queue_mode():
    """Get status of the sequential automatic queue runner."""
    from app.tasks.queue_runner import get_active_queue_item_id, is_auto_queue_enabled
    enabled = is_auto_queue_enabled()
    active_id = get_active_queue_item_id()
    return {
        "auto_queue_enabled": enabled,
        "is_running": bool(active_id),
        "current_claim_id": active_id or None,
    }


@router.post("/auto-mode")
async def toggle_auto_queue_mode(payload: dict, request: Request = None):
    """Enable or disable sequential automatic queue runner."""
    enabled = bool(payload.get("enabled", False))
    if enabled:
        await _validate_anticaptcha()

    from app.tasks.queue_runner import is_auto_queue_enabled, set_auto_queue_enabled
    set_auto_queue_enabled(enabled)
    if enabled:
        celery_app.send_task("app.tasks.queue_runner.advance_auto_queue_task", queue="default")

    ctx = extract_client_context(request)
    record_audit_event_background(
        action="AUTO_QUEUE_TOGGLED",
        entity_type="QUEUE",
        description=f"Operator set automatic sequential queue runner to {'ENABLED' if enabled else 'DISABLED'}",
        user_id=ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="SUCCESS",
        details={"enabled": enabled},
    )

    return {
        "auto_queue_enabled": is_auto_queue_enabled(),
        "message": f"Automatic queue runner {'ENABLED' if enabled else 'DISABLED'}.",
    }


@router.post("/pause")
async def pause_queue(request: Request = None):
    """Pause automatic queue execution."""
    from app.tasks.queue_runner import set_auto_queue_enabled
    set_auto_queue_enabled(False)

    ctx = extract_client_context(request)
    record_audit_event_background(
        action="QUEUE_PAUSED",
        entity_type="QUEUE",
        description="Operator paused automatic sequential queue runner",
        user_id=ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="SUCCESS",
    )

    return {"status": "paused", "message": "Automatic queue runner paused."}


@router.post("/start-all")
async def start_all_queue(request: Request = None, db: AsyncSession = Depends(get_db)):
    """Start automatic sequential execution of all NEW queue items and recover any stuck claims."""
    await _validate_anticaptcha()
    
    from app.tasks.queue_runner import set_active_queue_item_id, set_auto_queue_enabled

    # Reset any orphaned SCRAPING_IN_PROGRESS claims to NEW
    stuck_res = await db.execute(
        select(ClaimRecord).where(ClaimRecord.record_status == RecordStatusEnum.SCRAPING_IN_PROGRESS)
    )
    stuck_claims = stuck_res.scalars().all()
    for c in stuck_claims:
        c.record_status = RecordStatusEnum.NEW
    if stuck_claims:
        await db.commit()
        logger.info(f"Reset {len(stuck_claims)} stuck SCRAPING_IN_PROGRESS claims to NEW for start-all.")

    set_active_queue_item_id("")
    set_auto_queue_enabled(True)
    celery_app.send_task("app.tasks.queue_runner.advance_auto_queue_task", queue="default")

    ctx = extract_client_context(request)
    record_audit_event_background(
        action="QUEUE_STARTED_ALL",
        entity_type="QUEUE",
        description=f"Operator triggered Start All queue processing ({len(stuck_claims)} stuck claims reset to NEW)",
        user_id=ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="SUCCESS",
        details={"reset_claims_count": len(stuck_claims)},
    )

    return {"status": "started", "message": f"Automatic sequential queue processing started ({len(stuck_claims)} claims queued)."}


@router.get("/live", response_model=LiveQueueStateResponse)
async def get_live_queue_state(db: AsyncSession = Depends(get_db)):
    """Fetch real-time queue execution state, including all active running claims across parallel workers and pending items in FIFO order."""
    from app.services.settings_service import get_system_settings_async
    from app.tasks.queue_runner import get_active_queue_item_ids, is_auto_queue_enabled

    enabled = is_auto_queue_enabled()
    settings_obj = await get_system_settings_async()
    max_concurrency = getattr(settings_obj.automation, "max_concurrent_claims", None) or getattr(settings_obj.queue, "max_concurrent_claims", 3)
    max_concurrency = max(1, min(10, int(max_concurrency)))

    # Fetch all claims currently scraping (parallel worker fleet)
    active_res = await db.execute(
        select(ClaimRecord)
        .where(ClaimRecord.record_status == RecordStatusEnum.SCRAPING_IN_PROGRESS)
        .order_by(ClaimRecord.updated_at.desc())
        .limit(max_concurrency)
    )
    active_claims = list(active_res.scalars().all())
    active_items = [_format_live_queue_item(c, position=0) for c in active_claims]
    active_ids = {c.id for c in active_claims}

    # If DB has no active claims, check Redis active IDs as fallback
    if not active_items:
        redis_ids = get_active_queue_item_ids()
        if redis_ids:
            redis_claims_res = await db.execute(
                select(ClaimRecord).where(ClaimRecord.id.in_(redis_ids))
            )
            fallback_claims = list(redis_claims_res.scalars().all())
            active_items = [_format_live_queue_item(c, position=0) for c in fallback_claims]
            active_ids = {c.id for c in fallback_claims}

    primary_active_item = active_items[0] if active_items else None
    available_slots = max(0, max_concurrency - len(active_items))

    # Pending items in strict FIFO queue order (created_at ASC)
    pending_query = (
        select(ClaimRecord)
        .where(ClaimRecord.record_status == RecordStatusEnum.NEW)
        .order_by(ClaimRecord.created_at.asc())
        .limit(30)
    )
    if active_ids:
        pending_query = pending_query.where(ClaimRecord.id.not_in(active_ids))

    pending_res = await db.execute(pending_query)
    pending_claims = pending_res.scalars().all()

    pending_items = [
        _format_live_queue_item(c, position=idx + 1)
        for idx, c in enumerate(pending_claims)
    ]

    # Total counts
    pending_count_res = await db.execute(
        select(func.count(ClaimRecord.id)).where(ClaimRecord.record_status == RecordStatusEnum.NEW)
    )
    total_pending = pending_count_res.scalar_one() or 0

    in_progress_count_res = await db.execute(
        select(func.count(ClaimRecord.id)).where(ClaimRecord.record_status == RecordStatusEnum.SCRAPING_IN_PROGRESS)
    )
    total_in_progress = in_progress_count_res.scalar_one() or 0

    # Recently completed claims (last 10)
    recent_query = (
        select(ClaimRecord)
        .where(
            ClaimRecord.record_status.in_([
                RecordStatusEnum.SCRAPING_COMPLETED,
                RecordStatusEnum.MATCH_FOUND,
                RecordStatusEnum.NO_MATCH_FOUND,
                RecordStatusEnum.MANUAL_REVIEW,
                RecordStatusEnum.COMPLETED,
                RecordStatusEnum.FAILED,
            ])
        )
        .order_by(ClaimRecord.updated_at.desc())
        .limit(10)
    )
    recent_res = await db.execute(recent_query)
    recent_claims = recent_res.scalars().all()
    recently_completed = [_format_live_queue_item(c) for c in recent_claims]

    # Celery workers ping
    workers_online = 0
    try:
        ping_res = celery_app.control.ping(timeout=0.3) or []
        workers_online = len(ping_res)
    except Exception:
        workers_online = 0

    return LiveQueueStateResponse(
        auto_queue_enabled=enabled,
        is_running=len(active_items) > 0,
        current_claim_id=primary_active_item.id if primary_active_item else None,
        max_concurrency=max_concurrency,
        available_slots=available_slots,
        active_items=active_items,
        active_item=primary_active_item,
        pending_items=pending_items,
        recently_completed=recently_completed,
        total_pending_count=total_pending,
        total_in_progress_count=total_in_progress,
        workers_online=workers_online,
    )


@router.post("/run-next")
async def run_next_queue_item(request: Request = None):
    """Trigger the queue runner to pick and process the next pending claim immediately."""
    await _validate_anticaptcha()
    
    from app.tasks.queue_runner import set_auto_queue_enabled
    set_auto_queue_enabled(True)
    celery_app.send_task("app.tasks.queue_runner.advance_auto_queue_task", queue="default")

    ctx = extract_client_context(request)
    record_audit_event_background(
        action="QUEUE_ADVANCED_MANUAL",
        entity_type="QUEUE",
        description="Operator triggered immediate advancement to next pending queue item",
        user_id=ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="SUCCESS",
    )

    return {"status": "advancing", "message": "Triggered advancement to next pending claim."}


@router.post("/concurrency")
async def update_queue_concurrency(payload: ConcurrencyUpdateRequest, request: Request = None):
    """Set the number of parallel concurrent claim executions (1 to 10 parallel claims)."""
    concurrency = max(1, min(10, payload.concurrency))
    from app.services.settings_service import get_system_settings_async, save_system_settings_async
    curr_settings = await get_system_settings_async()
    curr_settings.automation.max_concurrent_claims = concurrency
    curr_settings.queue.max_concurrent_claims = concurrency
    await save_system_settings_async(curr_settings)

    from app.tasks.queue_runner import is_auto_queue_enabled
    if is_auto_queue_enabled():
        celery_app.send_task("app.tasks.queue_runner.advance_auto_queue_task", queue="default")

    ctx = extract_client_context(request)
    record_audit_event_background(
        action="QUEUE_CONCURRENCY_CHANGED",
        entity_type="QUEUE",
        description=f"Operator changed RPA execution concurrency to {concurrency} parallel workers",
        user_id=ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="SUCCESS",
        details={"concurrency": concurrency},
    )

    return {"concurrency": concurrency, "message": f"Execution concurrency updated to {concurrency} parallel workers."}


@router.post("/seed-demo")
async def seed_demo_claims(
    payload: SeedDemoClaimsRequest | None = None,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Seed authentic Florida and Texas test claims for immediate parallel multi-worker RPA testing."""
    import random
    import uuid

    count = min(25, max(1, payload.count if payload else 10))
    sample_pool = [
        {"insured_first": "James", "insured_last": "Rodriguez", "claimant_first": "Carlos", "claimant_last": "Gomez", "state": "FL", "city": "Miami", "county": "Miami-Dade"},
        {"insured_first": "Maria", "insured_last": "Gonzalez", "claimant_first": "Elena", "claimant_last": "Hernandez", "state": "FL", "city": "Fort Lauderdale", "county": "Broward"},
        {"insured_first": "David", "insured_last": "Williams", "claimant_first": "Ashley", "claimant_last": "Miller", "state": "FL", "city": "Tampa", "county": "Hillsborough"},
        {"insured_first": "Michael", "insured_last": "Smith", "claimant_first": "Brenda", "claimant_last": "Johnson", "state": "TX", "city": "Houston", "county": "Harris"},
        {"insured_first": "Robert", "insured_last": "Davis", "claimant_first": "Marcus", "claimant_last": "Jackson", "state": "TX", "city": "Dallas", "county": "Dallas"},
        {"insured_first": "Sarah", "insured_last": "Jenkins", "claimant_first": "Kevin", "claimant_last": "Taylor", "state": "TX", "city": "Austin", "county": "Travis"},
        {"insured_first": "Daniel", "insured_last": "Martinez", "claimant_first": "Sofia", "claimant_last": "Alvarez", "state": "FL", "city": "Hollywood", "county": "Broward"},
        {"insured_first": "Jennifer", "insured_last": "Brown", "claimant_first": "Brian", "claimant_last": "Wilson", "state": "FL", "city": "Miami Beach", "county": "Miami-Dade"},
        {"insured_first": "Christopher", "insured_last": "Garcia", "claimant_first": "Lucas", "claimant_last": "Perez", "state": "TX", "city": "Pasadena", "county": "Harris"},
        {"insured_first": "Amanda", "insured_last": "Clark", "claimant_first": "Jason", "claimant_last": "White", "state": "TX", "city": "Richardson", "county": "Dallas"},
        {"insured_first": "Thomas", "insured_last": "Hall", "claimant_first": "Diana", "claimant_last": "Allen", "state": "FL", "city": "Brandon", "county": "Hillsborough"},
        {"insured_first": "Patricia", "insured_last": "Young", "claimant_first": "Eric", "claimant_last": "King", "state": "TX", "city": "Round Rock", "county": "Travis"},
    ]

    created_ids = []

    for i in range(count):
        tmpl = sample_pool[i % len(sample_pool)]
        claim_num = f"0{random.randint(10000000, 99999999)}"  # 9-digit gets '0' prefix
        exp_num = f"{random.randint(1, 3):03d}"
        dol_month = random.randint(1, 12)
        dol_day = random.randint(1, 28)
        dol_year = random.randint(2021, 2024)
        dol_str = f"{dol_month:02d}/{dol_day:02d}/{dol_year}"

        rec = ClaimRecord(
            id=str(uuid.uuid4()),
            claim_number=claim_num,
            exposure_number=exp_num,
            insured_first_name=tmpl["insured_first"],
            insured_last_name=tmpl["insured_last"],
            claimant_first_name=tmpl["claimant_first"],
            claimant_last_name=tmpl["claimant_last"],
            driver_first_name=tmpl["insured_first"],
            driver_last_name=tmpl["insured_last"],
            dol=dol_str,
            policy_state=tmpl["state"],
            loss_location_state=tmpl["state"],
            record_status=RecordStatusEnum.NEW,
            retry_count=0,
        )
        db.add(rec)
        created_ids.append(rec.id)

    await db.commit()

    # Trigger queue advancement if enabled
    from app.tasks.queue_runner import is_auto_queue_enabled
    if is_auto_queue_enabled():
        celery_app.send_task("app.tasks.queue_runner.advance_auto_queue_task", queue="default")

    ctx = extract_client_context(request)
    record_audit_event_background(
        action="DEMO_CLAIMS_SEEDED",
        entity_type="QUEUE",
        description=f"Operator seeded {len(created_ids)} demo claims for parallel execution",
        user_id=ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="SUCCESS",
        details={"seeded_count": len(created_ids), "claim_ids": created_ids},
    )

    return {
        "message": f"Successfully seeded {len(created_ids)} authentic sample claims.",
        "count": len(created_ids),
        "claim_ids": created_ids,
    }


@router.post("/run-selected")
async def run_selected_claims(
    payload: RunSelectedQueueRequest,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Run a specific batch of selected claims in parallel."""
    await _validate_anticaptcha()
    
    if not payload.claim_ids:
        return {"message": "No claim IDs provided", "count": 0}

    res = await db.execute(
        select(ClaimRecord).where(ClaimRecord.id.in_(payload.claim_ids))
    )
    claims = list(res.scalars().all())
    from app.tasks.queue_runner import add_active_queue_item_id

    dispatched = []
    for c in claims:
        c.record_status = RecordStatusEnum.SCRAPING_IN_PROGRESS
        c.retry_count += 1
        add_active_queue_item_id(c.id)
        celery_app.send_task(
            "app.tasks.scraper_tasks.orchestrate_court_scrapers_task",
            args=[c.id],
            queue="scrapers",
        )
        dispatched.append(c.id)

    await db.commit()

    ctx = extract_client_context(request)
    record_audit_event_background(
        action="QUEUE_SELECTED_DISPATCHED",
        entity_type="QUEUE",
        description=f"Operator launched {len(dispatched)} selected claims concurrently",
        user_id=ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="SUCCESS",
        details={"claim_ids": dispatched},
    )

    return {"message": f"Dispatched {len(dispatched)} claims for parallel execution.", "count": len(dispatched), "claim_ids": dispatched}



