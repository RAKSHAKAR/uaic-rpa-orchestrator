"""Comprehensive Tests for Fleet-Aware Ingestion and Ordered Pending Queue (IMP-2026-0925-011).

Verifies that uploading claims via ingestion (or seeding) respects configured fleet concurrency:
- Fleet = 1x -> exactly 1 claim runs, remaining claims stay NEW in Ordered Pending Queue.
- Fleet = 2x -> exactly 2 claims run, remaining claims stay NEW in Ordered Pending Queue.
- Disabled auto-queue -> all claims stay NEW in Ordered Pending Queue.
- Queue advancement seamlessly picks up remaining claims in strict FIFO order as workers finish.
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, update

from app.core.celery_app import celery_app
from app.core.database import TaskAsyncSessionLocal
from app.main import app
from app.models.claim import ClaimRecord, IngestionBatch, RecordStatusEnum
from app.tasks.ingest_tasks import _async_parse_and_ingest
from app.tasks.queue_runner import (
    _async_advance_auto_queue,
    clear_all_active_queue_items,
    set_auto_queue_enabled,
)


@pytest.mark.asyncio
async def test_fleet_aware_ingest_dispatches_advance_task(tmp_path, monkeypatch):
    """Verify _async_parse_and_ingest triggers advance_auto_queue_task instead of blind-dispatching all claims."""
    mock_send = MagicMock()
    monkeypatch.setattr(celery_app, "send_task", mock_send)
    set_auto_queue_enabled(True)

    batch_id = str(uuid.uuid4())
    csv_file = tmp_path / f"{batch_id}_test_10_claims.csv"

    # Create CSV with 10 distinct claims
    rows = ["ClaimNumber,InsuredFirst,InsuredLast,DOL,LossState"]
    claim_nums = [f"FLEET-{uuid.uuid4().hex[:6]}" for _ in range(10)]
    for cn in claim_nums:
        rows.append(f"{cn},John,Doe,01/15/2024,Florida")
    csv_file.write_text("\n".join(rows), encoding="utf-8")

    async with TaskAsyncSessionLocal() as session:
        batch = IngestionBatch(
            id=batch_id,
            filename=csv_file.name,
            status="PROCESSING",
        )
        session.add(batch)
        await session.commit()

    mapping = {
        "claim_number": "ClaimNumber",
        "insured_first_name": "InsuredFirst",
        "insured_last_name": "InsuredLast",
        "dol": "DOL",
        "loss_location_state": "LossState",
    }

    await _async_parse_and_ingest(
        batch_id=batch_id,
        file_path=str(csv_file),
        column_mapping=mapping,
        duplicate_strategy="SKIP",
    )

    # Verify advance_auto_queue_task was sent to default queue
    mock_send.assert_called_with("app.tasks.queue_runner.advance_auto_queue_task", queue="default")

    # Verify that orchestrate_court_scrapers_task was NOT directly dispatched 10 times in ingest
    scrapers_calls = [
        call for call in mock_send.call_args_list
        if call[0] and call[0][0] == "app.tasks.scraper_tasks.orchestrate_court_scrapers_task"
    ]
    assert len(scrapers_calls) == 0, "Ingest task must NOT directly dispatch scraper tasks"

    # Verify all 10 claims are in the database with RecordStatusEnum.NEW
    async with TaskAsyncSessionLocal() as session:
        q = select(ClaimRecord).where(ClaimRecord.claim_number.in_(claim_nums))
        res = await session.execute(q)
        claims = list(res.scalars().all())
        assert len(claims) == 10
        assert all(c.record_status == RecordStatusEnum.NEW for c in claims)


@pytest.mark.asyncio
async def test_fleet_1x_runs_1_claim_leaves_9_new_in_pending_queue(monkeypatch):
    """Verify Fleet = 1x picks exactly 1 claim to SCRAPING_IN_PROGRESS and leaves 9 in NEW status."""
    set_auto_queue_enabled(True)
    clear_all_active_queue_items()

    # Clear any active or pending claims from test DB to ensure strict isolation
    async with TaskAsyncSessionLocal() as session:
        await session.execute(
            update(ClaimRecord)
            .where(ClaimRecord.record_status.in_([RecordStatusEnum.SCRAPING_IN_PROGRESS, RecordStatusEnum.NEW]))
            .values(record_status=RecordStatusEnum.COMPLETED)
        )
        await session.commit()

    # Create 10 NEW claims
    created_claim_ids = []
    prefix = f"F1-{uuid.uuid4().hex[:4]}"
    async with TaskAsyncSessionLocal() as session:
        for idx in range(10):
            cid = str(uuid.uuid4())
            created_claim_ids.append(cid)
            c = ClaimRecord(
                id=cid,
                claim_number=f"{prefix}-{idx:02d}",
                record_status=RecordStatusEnum.NEW,
                policy_state="FL",
                loss_location_state="FL",
            )
            session.add(c)
        await session.commit()

    # Mock settings with Fleet = 1x
    mock_settings = MagicMock()
    mock_settings.automation.max_concurrent_claims = 1
    mock_settings.queue.max_concurrent_claims = 1
    mock_settings.queue.auto_retry_failed_scrapes = False

    with patch("app.services.settings_service.get_system_settings_async", return_value=mock_settings), \
         patch("app.tasks.queue_runner.celery_app.send_task") as mock_send:
        await _async_advance_auto_queue()

        # Exactly 1 scraper task dispatched
        assert mock_send.call_count == 1
        dispatched_claim_id = mock_send.call_args[1]["kwargs"]["claim_id"]
        assert dispatched_claim_id == created_claim_ids[0]  # First in FIFO order

    # Verify DB state: exactly 1 claim is SCRAPING_IN_PROGRESS, 9 are NEW
    async with TaskAsyncSessionLocal() as session:
        q = select(ClaimRecord).where(ClaimRecord.id.in_(created_claim_ids))
        res = await session.execute(q)
        claims = list(res.scalars().all())

        running = [c for c in claims if c.record_status == RecordStatusEnum.SCRAPING_IN_PROGRESS]
        pending = [c for c in claims if c.record_status == RecordStatusEnum.NEW]

        assert len(running) == 1, f"Expected 1 running claim, got {len(running)}"
        assert len(pending) == 9, f"Expected 9 pending claims, got {len(pending)}"
        assert running[0].id == created_claim_ids[0]

    # Verify /api/v1/queue/live endpoint returns 9 pending items and 1 active
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.services.settings_service.get_system_settings_async", return_value=mock_settings):
            res = await client.get("/api/v1/queue/live")
            assert res.status_code == 200
            data = res.json()
            assert data["max_concurrency"] == 1
            assert len(data["active_items"]) == 1
            assert data["active_items"][0]["id"] == created_claim_ids[0]
            # Pending items in FIFO order
            pending_ids = [item["id"] for item in data["pending_items"]]
            for expected_id in created_claim_ids[1:]:
                assert expected_id in pending_ids

    # Cleanup
    async with TaskAsyncSessionLocal() as session:
        for cid in created_claim_ids:
            row = (await session.execute(select(ClaimRecord).where(ClaimRecord.id == cid))).scalar_one_or_none()
            if row:
                await session.delete(row)
        await session.commit()
    clear_all_active_queue_items()


@pytest.mark.asyncio
async def test_fleet_2x_runs_2_claims_leaves_8_new_in_pending_queue(monkeypatch):
    """Verify Fleet = 2x picks exactly 2 claims to SCRAPING_IN_PROGRESS and leaves 8 in NEW status."""
    set_auto_queue_enabled(True)
    clear_all_active_queue_items()

    # Clear any active or pending claims from test DB to ensure strict isolation
    async with TaskAsyncSessionLocal() as session:
        await session.execute(
            update(ClaimRecord)
            .where(ClaimRecord.record_status.in_([RecordStatusEnum.SCRAPING_IN_PROGRESS, RecordStatusEnum.NEW]))
            .values(record_status=RecordStatusEnum.COMPLETED)
        )
        await session.commit()

    created_claim_ids = []
    prefix = f"F2-{uuid.uuid4().hex[:4]}"
    async with TaskAsyncSessionLocal() as session:
        for idx in range(10):
            cid = str(uuid.uuid4())
            created_claim_ids.append(cid)
            c = ClaimRecord(
                id=cid,
                claim_number=f"{prefix}-{idx:02d}",
                record_status=RecordStatusEnum.NEW,
                policy_state="TX",
                loss_location_state="TX",
            )
            session.add(c)
        await session.commit()

    mock_settings = MagicMock()
    mock_settings.automation.max_concurrent_claims = 2
    mock_settings.queue.max_concurrent_claims = 2
    mock_settings.queue.auto_retry_failed_scrapes = False

    with patch("app.services.settings_service.get_system_settings_async", return_value=mock_settings), \
         patch("app.tasks.queue_runner.celery_app.send_task") as mock_send:
        await _async_advance_auto_queue()

        # Exactly 2 scraper tasks dispatched
        assert mock_send.call_count == 2
        dispatched_ids = [call[1]["kwargs"]["claim_id"] for call in mock_send.call_args_list]
        assert set(dispatched_ids) == {created_claim_ids[0], created_claim_ids[1]}

    # Verify DB state: exactly 2 claims are SCRAPING_IN_PROGRESS, 8 are NEW
    async with TaskAsyncSessionLocal() as session:
        q = select(ClaimRecord).where(ClaimRecord.id.in_(created_claim_ids))
        res = await session.execute(q)
        claims = list(res.scalars().all())

        running = [c for c in claims if c.record_status == RecordStatusEnum.SCRAPING_IN_PROGRESS]
        pending = [c for c in claims if c.record_status == RecordStatusEnum.NEW]

        assert len(running) == 2, f"Expected 2 running claims, got {len(running)}"
        assert len(pending) == 8, f"Expected 8 pending claims, got {len(pending)}"

    # Cleanup
    async with TaskAsyncSessionLocal() as session:
        for cid in created_claim_ids:
            row = (await session.execute(select(ClaimRecord).where(ClaimRecord.id == cid))).scalar_one_or_none()
            if row:
                await session.delete(row)
        await session.commit()
    clear_all_active_queue_items()


@pytest.mark.asyncio
async def test_sequential_queue_pickup_on_claim_completion(monkeypatch):
    """Verify that when a running claim completes, the next NEW claim in FIFO order is automatically picked up."""
    set_auto_queue_enabled(True)
    clear_all_active_queue_items()

    async with TaskAsyncSessionLocal() as session:
        await session.execute(
            update(ClaimRecord)
            .where(ClaimRecord.record_status.in_([RecordStatusEnum.SCRAPING_IN_PROGRESS, RecordStatusEnum.NEW]))
            .values(record_status=RecordStatusEnum.COMPLETED)
        )
        await session.commit()

    created_claim_ids = []
    prefix = f"SEQ-{uuid.uuid4().hex[:4]}"
    async with TaskAsyncSessionLocal() as session:
        for idx in range(3):
            cid = str(uuid.uuid4())
            created_claim_ids.append(cid)
            c = ClaimRecord(
                id=cid,
                claim_number=f"{prefix}-{idx:02d}",
                record_status=RecordStatusEnum.NEW,
                policy_state="FL",
                loss_location_state="FL",
            )
            session.add(c)
        await session.commit()

    mock_settings = MagicMock()
    mock_settings.automation.max_concurrent_claims = 1
    mock_settings.queue.max_concurrent_claims = 1
    mock_settings.queue.auto_retry_failed_scrapes = False

    # Step 1: Advance queue with Fleet = 1x -> Claim 0 should run, Claims 1 and 2 wait
    with patch("app.services.settings_service.get_system_settings_async", return_value=mock_settings), \
         patch("app.tasks.queue_runner.celery_app.send_task") as mock_send:
        await _async_advance_auto_queue()
        assert mock_send.call_count == 1
        assert mock_send.call_args[1]["kwargs"]["claim_id"] == created_claim_ids[0]

    # Step 2: Simulate Claim 0 completion (transition to COMPLETED and remove from active set)
    async with TaskAsyncSessionLocal() as session:
        c0 = (await session.execute(select(ClaimRecord).where(ClaimRecord.id == created_claim_ids[0]))).scalar_one()
        c0.record_status = RecordStatusEnum.COMPLETED
        await session.commit()
    clear_all_active_queue_items()

    # Step 3: Advance queue again -> Claim 1 should be picked up sequentially
    with patch("app.services.settings_service.get_system_settings_async", return_value=mock_settings), \
         patch("app.tasks.queue_runner.celery_app.send_task") as mock_send2:
        await _async_advance_auto_queue()
        assert mock_send2.call_count == 1
        assert mock_send2.call_args[1]["kwargs"]["claim_id"] == created_claim_ids[1]

    # Verify DB state: Claim 0 is COMPLETED, Claim 1 is SCRAPING_IN_PROGRESS, Claim 2 is NEW
    async with TaskAsyncSessionLocal() as session:
        claims = {
            c.id: c.record_status
            for c in (await session.execute(select(ClaimRecord).where(ClaimRecord.id.in_(created_claim_ids)))).scalars().all()
        }
        assert claims[created_claim_ids[0]] == RecordStatusEnum.COMPLETED
        assert claims[created_claim_ids[1]] == RecordStatusEnum.SCRAPING_IN_PROGRESS
        assert claims[created_claim_ids[2]] == RecordStatusEnum.NEW

    # Cleanup
    async with TaskAsyncSessionLocal() as session:
        for cid in created_claim_ids:
            row = (await session.execute(select(ClaimRecord).where(ClaimRecord.id == cid))).scalar_one_or_none()
            if row:
                await session.delete(row)
        await session.commit()
    clear_all_active_queue_items()

