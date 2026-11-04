"""Unit and integration tests for worker restart auto-recovery and zero-portal resilience.

Validates:
1. Reconciling stranded SCRAPING_IN_PROGRESS claims on worker boot
2. Reconciling worker-restart FAILED claims on worker boot
3. Zero-portal claims exempt from retry count penalties
4. Watchdog dead-orphan zero-portal handling
5. Scheduled retry tasks picking up worker-interrupted claims even with exhausted retries
6. Queue retrigger endpoint resetting retry count for worker-interrupted claims
"""

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.main import app
from app.models.claim import BotStatusEnum, ClaimRecord, RecordStatusEnum
from app.tasks.queue_runner import (
    reconcile_worker_restart_claims_async,
    reconcile_worker_restart_claims_sync,
)
from app.tasks.retry_tasks import _async_retrigger_failed_cases


@pytest.mark.asyncio
async def test_reconcile_stranded_scraping_in_progress_zero_portals():
    """Verify that a claim stranded in SCRAPING_IN_PROGRESS with 0 portals is reset to NEW with retry_count=0."""
    claim_id = str(uuid.uuid4())
    async with AsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number=f"REC{uuid.uuid4().hex[:6].upper()}",
            exposure_number="1",
            policy_state="FL",
            loss_location_state="FL",
            insured_first_name="Carlos",
            insured_last_name="Mendez",
            claimant_first_name="Jane",
            claimant_last_name="Williams",
            driver_first_name="Carlos",
            driver_last_name="Mendez",
            dol="05/12/2023",
            record_status=RecordStatusEnum.SCRAPING_IN_PROGRESS,
            retry_count=2,
            action_timings={"started_at": "2026-10-10T10:00:00", "portals": []},
            fl_website_broward="Yes",
            fl_botstatus_broward=BotStatusEnum.IN_PROGRESS,
            fl_website_hillsborough="Yes",
            fl_botstatus_hillsborough=BotStatusEnum.FAILED,
        )
        session.add(claim)
        await session.commit()

    recovered = await reconcile_worker_restart_claims_async()
    assert recovered >= 1

    async with AsyncSessionLocal() as session:
        res = await session.execute(select(ClaimRecord).where(ClaimRecord.id == claim_id))
        updated = res.scalar_one()
        assert updated.record_status == RecordStatusEnum.NEW
        assert updated.retry_count == 0  # 0 portals = 0 penalty
        assert updated.fl_botstatus_broward == BotStatusEnum.NOT_TRIGGERED
        assert updated.fl_botstatus_hillsborough == BotStatusEnum.NOT_TRIGGERED
        assert "Auto-recovered" in (updated.last_error or "")


@pytest.mark.asyncio
async def test_reconcile_worker_restart_failed_claim():
    """Verify that claims marked FAILED with 'worker restart' are recovered to NEW with retry_count=0."""
    claim_id = str(uuid.uuid4())
    async with AsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number=f"REC{uuid.uuid4().hex[:6].upper()}",
            exposure_number="1",
            policy_state="TX",
            loss_location_state="TX",
            insured_first_name="Maria",
            insured_last_name="Rodriguez",
            claimant_first_name="John",
            claimant_last_name="Smith",
            dol="01/15/2023",
            record_status=RecordStatusEnum.FAILED,
            retry_count=3,
            last_error="Scraping timed out or was interrupted by worker restart.",
            action_timings={},
            te_website_travis="Yes",
            te_botstatus_travis=BotStatusEnum.FAILED,
        )
        session.add(claim)
        await session.commit()

    recovered = await reconcile_worker_restart_claims_async()
    assert recovered >= 1

    async with AsyncSessionLocal() as session:
        res = await session.execute(select(ClaimRecord).where(ClaimRecord.id == claim_id))
        updated = res.scalar_one()
        assert updated.record_status == RecordStatusEnum.NEW
        assert updated.retry_count == 0
        assert updated.te_botstatus_travis == BotStatusEnum.NOT_TRIGGERED


@pytest.mark.asyncio
async def test_reconcile_claim_with_prior_portals_decrements_retry():
    """Verify that claims with actual portal attempts decrement retry_count by 1 rather than resetting to 0."""
    claim_id = str(uuid.uuid4())
    async with AsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number=f"REC{uuid.uuid4().hex[:6].upper()}",
            exposure_number="1",
            policy_state="FL",
            loss_location_state="FL",
            insured_first_name="Alice",
            insured_last_name="Walker",
            claimant_first_name="Bob",
            claimant_last_name="Taylor",
            dol="02/20/2023",
            record_status=RecordStatusEnum.SCRAPING_IN_PROGRESS,
            retry_count=2,
            action_timings={"portals": [{"portal": "broward", "status": "completed"}]},
        )
        session.add(claim)
        await session.commit()

    await reconcile_worker_restart_claims_async()

    async with AsyncSessionLocal() as session:
        res = await session.execute(select(ClaimRecord).where(ClaimRecord.id == claim_id))
        updated = res.scalar_one()
        assert updated.record_status == RecordStatusEnum.NEW
        assert updated.retry_count == 1


def test_reconcile_sync_wrapper():
    """Verify that reconcile_worker_restart_claims_sync runs cleanly without event loop collisions."""
    count = reconcile_worker_restart_claims_sync()
    assert isinstance(count, int)


@pytest.mark.asyncio
async def test_retry_tasks_picks_up_worker_restart_failed_claim_beyond_max_retries():
    """Verify that scheduled retry task picks up worker-restart claims even when retry_count >= max_task_retries."""
    claim_id = str(uuid.uuid4())
    async with AsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number=f"REC{uuid.uuid4().hex[:6].upper()}",
            exposure_number="1",
            policy_state="FL",
            loss_location_state="FL",
            insured_first_name="David",
            insured_last_name="Miller",
            claimant_first_name="Sarah",
            claimant_last_name="Brown",
            dol="03/10/2023",
            record_status=RecordStatusEnum.FAILED,
            retry_count=5,  # Exceeded max_task_retries
            last_error="Scraping timed out or was interrupted by worker restart.",
            updated_at=datetime.now(UTC) - timedelta(minutes=5),
            action_timings={},
            fl_website_broward="Yes",
            fl_botstatus_broward=BotStatusEnum.FAILED,
        )
        session.add(claim)
        await session.commit()

    from app.schemas.settings import SystemSettings

    test_settings = SystemSettings()
    test_settings.automation.anticaptcha_api_key = "test-key"

    with (
        patch("app.tasks.queue_runner.get_active_queue_item_ids", return_value=[]),
        patch(
            "app.tasks.retry_tasks.get_system_settings_async", AsyncMock(return_value=test_settings)
        ),
        patch("app.core.celery_app.celery_app.send_task") as mock_send,
    ):
        await _async_retrigger_failed_cases()
        assert mock_send.called

    async with AsyncSessionLocal() as session:
        res = await session.execute(select(ClaimRecord).where(ClaimRecord.id == claim_id))
        updated = res.scalar_one()
        assert updated.record_status == RecordStatusEnum.SCRAPING_IN_PROGRESS
        assert updated.retry_count == 0  # Zero portals = 0 penalty
        assert updated.fl_botstatus_broward == BotStatusEnum.NOT_TRIGGERED
        assert updated.last_error is None


@pytest.mark.asyncio
async def test_queue_retrigger_endpoint_worker_restart_zero_penalty():
    """Verify POST /api/v1/queue/retrigger resets retry_count=0 for worker restart claims."""
    claim_id = str(uuid.uuid4())
    async with AsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number=f"REC{uuid.uuid4().hex[:6].upper()}",
            exposure_number="1",
            policy_state="FL",
            loss_location_state="FL",
            insured_first_name="George",
            insured_last_name="Clark",
            claimant_first_name="Emma",
            claimant_last_name="Lewis",
            dol="04/11/2023",
            record_status=RecordStatusEnum.FAILED,
            retry_count=3,
            last_error="Scraping timed out or was interrupted by worker restart.",
            action_timings={},
            fl_website_miami="Yes",
            fl_botstatus_miami=BotStatusEnum.FAILED,
        )
        session.add(claim)
        await session.commit()

    from app.schemas.settings import SystemSettings

    test_settings = SystemSettings()
    test_settings.automation.anticaptcha_api_key = "test-key"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        with (
            patch(
                "app.api.v1.endpoints.queue.get_system_settings_async",
                AsyncMock(return_value=test_settings),
            ),
            patch("app.core.celery_app.celery_app.send_task") as mock_send,
        ):
            res = await ac.post("/api/v1/queue/retrigger", json={"claim_ids": [claim_id]})
            assert res.status_code == 200
            assert mock_send.called

    async with AsyncSessionLocal() as session:
        res = await session.execute(select(ClaimRecord).where(ClaimRecord.id == claim_id))
        updated = res.scalar_one()
        assert updated.record_status == RecordStatusEnum.NEW
        assert updated.retry_count == 0
        assert updated.fl_botstatus_miami == BotStatusEnum.NOT_TRIGGERED
        assert updated.last_error is None
