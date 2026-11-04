"""
Tests for configurable multi-unit (seconds, minutes, hours, days, weeks, months, years)
auto-retrigger interval for failed claims & scrapers (IMP-2026-1007-003).
"""

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest

from app.core.database import TaskAsyncSessionLocal
from app.models.claim import ClaimRecord, RecordStatusEnum
from app.schemas.settings import RETRY_INTERVAL_UNIT_MULTIPLIERS, SystemSettings, TaskQueueSettings
from app.tasks.retry_tasks import _async_retrigger_failed_cases


def test_retry_interval_unit_multipliers():
    """Verify standard unit conversion multipliers to seconds."""
    assert RETRY_INTERVAL_UNIT_MULTIPLIERS["seconds"] == 1
    assert RETRY_INTERVAL_UNIT_MULTIPLIERS["minutes"] == 60
    assert RETRY_INTERVAL_UNIT_MULTIPLIERS["hours"] == 3600
    assert RETRY_INTERVAL_UNIT_MULTIPLIERS["days"] == 86400
    assert RETRY_INTERVAL_UNIT_MULTIPLIERS["weeks"] == 604800
    assert RETRY_INTERVAL_UNIT_MULTIPLIERS["months"] == 2592000
    assert RETRY_INTERVAL_UNIT_MULTIPLIERS["years"] == 31536000


def test_task_queue_settings_multi_unit_synchronization():
    """Verify TaskQueueSettings automatically derives seconds and minutes across all units."""
    # 30 seconds
    q_sec = TaskQueueSettings(
        failed_claims_retry_interval_value=30, failed_claims_retry_interval_unit="seconds"
    )
    assert q_sec.failed_claims_retry_interval_seconds == 30
    assert q_sec.failed_claims_retry_interval_value == 30
    assert q_sec.failed_claims_retry_interval_unit == "seconds"
    assert q_sec.failed_claims_retry_interval_minutes == 1

    # 15 minutes
    q_min = TaskQueueSettings(
        failed_claims_retry_interval_value=15, failed_claims_retry_interval_unit="minutes"
    )
    assert q_min.failed_claims_retry_interval_seconds == 900
    assert q_min.failed_claims_retry_interval_minutes == 15

    # 2 hours
    q_hr = TaskQueueSettings(
        failed_claims_retry_interval_value=2, failed_claims_retry_interval_unit="hours"
    )
    assert q_hr.failed_claims_retry_interval_seconds == 7200
    assert q_hr.failed_claims_retry_interval_minutes == 120

    # 1 day
    q_day = TaskQueueSettings(
        failed_claims_retry_interval_value=1, failed_claims_retry_interval_unit="days"
    )
    assert q_day.failed_claims_retry_interval_seconds == 86400
    assert q_day.failed_claims_retry_interval_minutes == 1440

    # 2 weeks
    q_wk = TaskQueueSettings(
        failed_claims_retry_interval_value=2, failed_claims_retry_interval_unit="weeks"
    )
    assert q_wk.failed_claims_retry_interval_seconds == 1209600

    # 1 month
    q_mo = TaskQueueSettings(
        failed_claims_retry_interval_value=1, failed_claims_retry_interval_unit="months"
    )
    assert q_mo.failed_claims_retry_interval_seconds == 2592000

    # 1 year
    q_yr = TaskQueueSettings(
        failed_claims_retry_interval_value=1, failed_claims_retry_interval_unit="years"
    )
    assert q_yr.failed_claims_retry_interval_seconds == 31536000
    assert q_yr.failed_claims_retry_interval_minutes == 525600


def test_task_queue_settings_legacy_minutes_backward_compatibility():
    """Verify setting legacy failed_claims_retry_interval_minutes populates value, unit, and seconds."""
    q_legacy = TaskQueueSettings(failed_claims_retry_interval_minutes=45)
    assert q_legacy.failed_claims_retry_interval_value == 45
    assert q_legacy.failed_claims_retry_interval_unit == "minutes"
    assert q_legacy.failed_claims_retry_interval_seconds == 2700
    assert q_legacy.failed_claims_retry_interval_minutes == 45


@pytest.mark.asyncio
async def test_functional_retrigger_sub_minute_seconds_precision():
    """
    Functional Test: An operator sets retry interval to 30 seconds.
    - Claim A (failed 45s ago) MUST be retriggered.
    - Claim B (failed 15s ago) MUST NOT be retriggered yet.
    """
    claim_a_id = str(uuid.uuid4())
    claim_b_id = str(uuid.uuid4())

    async with TaskAsyncSessionLocal() as session:
        claim_a = ClaimRecord(
            id=claim_a_id,
            claim_number=f"FAIL-30S-A-{claim_a_id[:6]}",
            record_status=RecordStatusEnum.FAILED,
            retry_count=0,
            updated_at=datetime.now(UTC) - timedelta(seconds=45),
        )
        claim_b = ClaimRecord(
            id=claim_b_id,
            claim_number=f"FAIL-30S-B-{claim_b_id[:6]}",
            record_status=RecordStatusEnum.FAILED,
            retry_count=0,
            updated_at=datetime.now(UTC) - timedelta(seconds=15),
        )
        session.add_all([claim_a, claim_b])
        await session.commit()

    # Configure system settings with 30 seconds retry interval
    test_settings = SystemSettings()
    test_settings.queue.failed_claims_retry_interval_value = 30
    test_settings.queue.failed_claims_retry_interval_unit = "seconds"
    test_settings.queue.failed_claims_retry_interval_seconds = 30
    test_settings.queue.auto_retry_failed_scrapes = True

    with (
        patch(
            "app.tasks.retry_tasks.get_system_settings_async", AsyncMock(return_value=test_settings)
        ),
        patch("app.tasks.retry_tasks.is_portal_in_cooldown", return_value=(False, 0, "")),
        patch("app.core.celery_app.celery_app.send_task") as mock_retry_task,
    ):
        await _async_retrigger_failed_cases()

        retriggered_ids = [
            c_args.kwargs["args"][0]
            for c_args in mock_retry_task.call_args_list
            if "args" in c_args.kwargs and c_args.kwargs["args"]
        ]

        # Claim A (45s elapsed > 30s threshold) was dispatched
        assert claim_a_id in retriggered_ids
        # Claim B (15s elapsed < 30s threshold) was NOT dispatched
        assert claim_b_id not in retriggered_ids

    # Cleanup test claims
    async with TaskAsyncSessionLocal() as session:
        for cid in [claim_a_id, claim_b_id]:
            row = await session.get(ClaimRecord, cid)
            if row:
                await session.delete(row)
        await session.commit()


@pytest.mark.asyncio
async def test_functional_retrigger_extended_horizon_hours_and_days():
    """
    Functional Test: An operator sets retry interval to 2 hours.
    - Claim C (failed 3 hours ago) MUST be retriggered.
    - Claim D (failed 30 minutes ago) MUST NOT be retriggered yet.
    """
    claim_c_id = str(uuid.uuid4())
    claim_d_id = str(uuid.uuid4())

    async with TaskAsyncSessionLocal() as session:
        claim_c = ClaimRecord(
            id=claim_c_id,
            claim_number=f"FAIL-2HR-C-{claim_c_id[:6]}",
            record_status=RecordStatusEnum.FAILED,
            retry_count=0,
            updated_at=datetime.now(UTC) - timedelta(hours=3),
        )
        claim_d = ClaimRecord(
            id=claim_d_id,
            claim_number=f"FAIL-2HR-D-{claim_d_id[:6]}",
            record_status=RecordStatusEnum.FAILED,
            retry_count=0,
            updated_at=datetime.now(UTC) - timedelta(minutes=30),
        )
        session.add_all([claim_c, claim_d])
        await session.commit()

    test_settings = SystemSettings()
    test_settings.queue.failed_claims_retry_interval_value = 2
    test_settings.queue.failed_claims_retry_interval_unit = "hours"
    test_settings.queue.failed_claims_retry_interval_seconds = 7200
    test_settings.queue.auto_retry_failed_scrapes = True

    with (
        patch(
            "app.tasks.retry_tasks.get_system_settings_async", AsyncMock(return_value=test_settings)
        ),
        patch("app.tasks.retry_tasks.is_portal_in_cooldown", return_value=(False, 0, "")),
        patch("app.core.celery_app.celery_app.send_task") as mock_retry_task,
    ):
        await _async_retrigger_failed_cases()

        retriggered_ids = [
            c_args.kwargs["args"][0]
            for c_args in mock_retry_task.call_args_list
            if "args" in c_args.kwargs and c_args.kwargs["args"]
        ]

        # Claim C (3 hours > 2 hours) was retriggered
        assert claim_c_id in retriggered_ids
        # Claim D (30 mins < 2 hours) was NOT retriggered
        assert claim_d_id not in retriggered_ids

    # Cleanup test claims
    async with TaskAsyncSessionLocal() as session:
        for cid in [claim_c_id, claim_d_id]:
            row = await session.get(ClaimRecord, cid)
            if row:
                await session.delete(row)
        await session.commit()
