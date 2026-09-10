"""Comprehensive automated test suite for the Enterprise Data Cleanup & Retention Engine."""

import uuid
from datetime import datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.database import TaskAsyncSessionLocal
from app.main import app
from app.models.audit_log import AuditLog
from app.models.claim import ClaimRecord, RecordStatusEnum
from app.models.court_case import ScrapedCourtCase
from app.models.error_screenshot import ErrorScreenshot
from app.models.match_result import MatchPair
from app.models.notification import Notification
from app.services.cleanup_service import (
    calculate_cleanup_preview,
    execute_enterprise_cleanup,
    expand_categories,
    resolve_time_window,
)


@pytest.mark.asyncio
async def test_time_window_resolution():
    """Verify that all time scope calculators produce correct normalized date boundaries."""
    ref_time = datetime(2026, 9, 5, 14, 30, 0)

    # 1. Current Month
    start_dt, end_dt, desc = resolve_time_window("current_month", reference_now=ref_time)
    assert start_dt == datetime(2026, 9, 1, 0, 0, 0)
    assert end_dt == ref_time
    assert "Current Month" in desc

    # 2. Previous Month (August 2026 has 31 days)
    start_dt, end_dt, desc = resolve_time_window("previous_month", reference_now=ref_time)
    assert start_dt == datetime(2026, 8, 1, 0, 0, 0)
    assert end_dt == datetime(2026, 8, 31, 23, 59, 59, 999999)
    assert "Previous Month" in desc

    # January rollover check (January -> December previous year)
    jan_time = datetime(2026, 1, 15, 10, 0, 0)
    start_dt, end_dt, _ = resolve_time_window("previous_month", reference_now=jan_time)
    assert start_dt == datetime(2025, 12, 1, 0, 0, 0)
    assert end_dt == datetime(2025, 12, 31, 23, 59, 59, 999999)

    # 3. Last N Days
    start_dt, end_dt, _ = resolve_time_window("last_n_days", n_units=10, reference_now=ref_time)
    assert start_dt == ref_time - timedelta(days=10)
    assert end_dt == ref_time

    # 4. Custom Range
    start_dt, end_dt, _ = resolve_time_window(
        "custom_range",
        start_date="2026-06-01",
        end_date="2026-06-30",
        reference_now=ref_time,
    )
    assert start_dt.year == 2026 and start_dt.month == 6 and start_dt.day == 1
    assert end_dt.year == 2026 and end_dt.month == 6 and end_dt.day == 30

    # 5. All Time
    start_dt, end_dt, desc = resolve_time_window("all_time")
    assert start_dt is None
    assert end_dt is None
    assert "All Time" in desc


def test_categories_expansion():
    """Verify category list expansion logic."""
    # All operational expands to full set
    all_cats = expand_categories(["all_operational"])
    assert "claims" in all_cats
    assert "court_cases" in all_cats
    assert "notifications" in all_cats
    assert "telemetry" in all_cats
    assert len(all_cats) >= 10

    # Comma-separated categories
    multi = expand_categories(["claims,notifications,telemetry"])
    assert set(multi) == {"claims", "notifications", "telemetry"}


@pytest.mark.asyncio
async def test_calculate_cleanup_preview_no_mutations():
    """Verify that calculate_cleanup_preview calculates accurate counts without modifying any data."""
    test_id = str(uuid.uuid4())
    async with TaskAsyncSessionLocal() as session:
        # Create test claim
        claim = ClaimRecord(
            id=test_id,
            claim_number=f"TEST-PREVIEW-{test_id[:6]}",
            dol="09/01/2026",
            insured_first_name="Preview",
            insured_last_name="Test",
            policy_state="FL",
            loss_location_state="FL",
            record_status=RecordStatusEnum.NEW,
            created_at=datetime.now(),
        )
        session.add(claim)
        
        # Create test notification
        notif = Notification(
            id=str(uuid.uuid4()),
            claim_id=test_id,
            claim_number=f"TEST-PREVIEW-{test_id[:6]}",
            event_type="test_email",
            recipient="operator@test.com",
            subject="Preview Notification",
            body_html="<p>Preview Notification</p>",
            body_text="Preview Notification",
            status="SENT",
            created_at=datetime.now(),
        )
        session.add(notif)
        await session.commit()

    # Calculate preview
    preview = await calculate_cleanup_preview(
        categories=["claims", "notifications"],
        time_scope="all_time",
    )
    assert preview.total_database_records >= 2
    assert preview.record_counts.get("claims", 0) >= 1
    assert preview.record_counts.get("notifications", 0) >= 1

    # Verify that data still exists in DB
    async with TaskAsyncSessionLocal() as session:
        claim_check = (await session.execute(select(ClaimRecord).where(ClaimRecord.id == test_id))).scalar_one_or_none()
        assert claim_check is not None
        notif_check = (await session.execute(select(Notification).where(Notification.id == notif.id))).scalar_one_or_none()
        assert notif_check is not None

        # Clean up seeded records
        await session.delete(notif_check)
        await session.delete(claim_check)
        await session.commit()


@pytest.mark.asyncio
async def test_execute_cleanup_single_category_isolation():
    """Verify that deleting one category (e.g. notifications) leaves other categories (e.g. claims) completely intact."""
    test_id = str(uuid.uuid4())
    async with TaskAsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=test_id,
            claim_number=f"TEST-ISOLATION-{test_id[:6]}",
            dol="09/01/2026",
            insured_first_name="Isolation",
            insured_last_name="User",
            policy_state="FL",
            loss_location_state="FL",
            record_status=RecordStatusEnum.NEW,
            created_at=datetime.now(),
        )
        session.add(claim)

        notif = Notification(
            id=str(uuid.uuid4()),
            claim_id=test_id,
            claim_number=claim.claim_number,
            event_type="test_email",
            recipient="operator@test.com",
            subject="Isolation Notification",
            body_html="<p>Isolation Notification</p>",
            body_text="Isolation Notification",
            status="SENT",
            created_at=datetime.now(),
        )
        session.add(notif)
        await session.commit()

    # Execute cleanup ONLY for notifications
    res = await execute_enterprise_cleanup(
        categories=["notifications"],
        time_scope="all_time",
        operator="TEST_RUNNER",
        dry_run=False,
    )
    assert res.success is True
    assert res.records_deleted.get("notifications", 0) >= 1

    # Verify: notification is gone, but claim STILL exists!
    async with TaskAsyncSessionLocal() as session:
        notif_check = (await session.execute(select(Notification).where(Notification.id == notif.id))).scalar_one_or_none()
        assert notif_check is None

        claim_check = (await session.execute(select(ClaimRecord).where(ClaimRecord.id == test_id))).scalar_one_or_none()
        assert claim_check is not None

        # Clean up seeded claim
        await session.delete(claim_check)
        await session.commit()


@pytest.mark.asyncio
async def test_execute_cleanup_claim_cascades():
    """Verify that deleting a claim properly cascades to child court cases, match pairs, and error screenshots."""
    claim_id = str(uuid.uuid4())
    case_id = str(uuid.uuid4())
    match_id = str(uuid.uuid4())
    screenshot_id = str(uuid.uuid4())

    async with TaskAsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number=f"TEST-CASCADE-{claim_id[:6]}",
            dol="09/01/2026",
            insured_first_name="Cascade",
            insured_last_name="Owner",
            policy_state="FL",
            loss_location_state="FL",
            record_status=RecordStatusEnum.NEW,
            created_at=datetime.now(),
        )
        session.add(claim)

        court_case = ScrapedCourtCase(
            id=case_id,
            claim_id=claim_id,
            case_number="CASE-CASCADE-001",
            case_style="Cascade v. Defendant",
            county_name="Broward",
            county_website="https://www.browardclerk.org/Web2",
            created_at=datetime.now(),
        )
        session.add(court_case)

        match_pair = MatchPair(
            id=match_id,
            claim_id=claim_id,
            court_case_id=case_id,
            party_type="INSURED",
            party_name="Cascade Owner",
            case_style="Cascade v. Defendant",
            similarity_score=0.95,
            threshold_applied=0.6,
            is_match=True,
            created_at=datetime.now(),
        )
        session.add(match_pair)

        screenshot = ErrorScreenshot(
            id=screenshot_id,
            claim_id=claim_id,
            portal_key="broward",
            portal_name="Broward County Clerk",
            file_path="screenshots/test.png",
            created_at=datetime.now(),
        )
        session.add(screenshot)
        await session.commit()

    # Execute cleanup for claims
    res = await execute_enterprise_cleanup(
        categories=["claims"],
        time_scope="all_time",
        operator="TEST_RUNNER",
        dry_run=False,
    )
    assert res.success is True
    assert res.records_deleted.get("claims", 0) >= 1

    # Verify all child records are also gone
    async with TaskAsyncSessionLocal() as session:
        assert (await session.execute(select(ClaimRecord).where(ClaimRecord.id == claim_id))).scalar_one_or_none() is None
        assert (await session.execute(select(ScrapedCourtCase).where(ScrapedCourtCase.id == case_id))).scalar_one_or_none() is None
        assert (await session.execute(select(MatchPair).where(MatchPair.id == match_id))).scalar_one_or_none() is None
        assert (await session.execute(select(ErrorScreenshot).where(ErrorScreenshot.id == screenshot_id))).scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_execute_cleanup_telemetry_preserves_audit_trail():
    """Verify that telemetry cleanup deletes audit logs but preserves the cleanup operation's own audit record."""
    dummy_audit_id = str(uuid.uuid4())
    async with TaskAsyncSessionLocal() as session:
        dummy_audit = AuditLog(
            id=dummy_audit_id,
            action="TEST_ACTION",
            entity_type="SYSTEM",
            description="Pre-cleanup telemetry entry",
            user_id="operator@test.com",
            user_email="operator@test.com",
            status="INFO",
            timestamp=datetime.now(),
        )
        session.add(dummy_audit)
        await session.commit()

    res = await execute_enterprise_cleanup(
        categories=["telemetry"],
        time_scope="all_time",
        operator="TEST_RUNNER",
        dry_run=False,
    )
    assert res.success is True

    # Verify: dummy audit log is deleted, but ENTERPRISE_CLEANUP audit log exists
    async with TaskAsyncSessionLocal() as session:
        dummy_check = (await session.execute(select(AuditLog).where(AuditLog.id == dummy_audit_id))).scalar_one_or_none()
        assert dummy_check is None

        cleanup_audits = (
            await session.execute(
                select(AuditLog).where(
                    AuditLog.action == "ENTERPRISE_CLEANUP",
                    AuditLog.entity_id == res.cleanup_id,
                )
            )
        ).scalar_one_or_none()
        assert cleanup_audits is not None
        assert cleanup_audits.status == "SUCCESS"


@pytest.mark.asyncio
async def test_execute_cleanup_idempotent():
    """Verify that running cleanup repeatedly with identical criteria is safe and idempotent."""
    res1 = await execute_enterprise_cleanup(
        categories=["claims", "court_cases", "fuzzy_matches"],
        time_scope="current_month",
        operator="TEST_RUNNER",
        dry_run=False,
    )
    assert res1.success is True

    # Immediate second run
    res2 = await execute_enterprise_cleanup(
        categories=["claims", "court_cases", "fuzzy_matches"],
        time_scope="current_month",
        operator="TEST_RUNNER",
        dry_run=False,
    )
    assert res2.success is True
    assert res2.total_records_deleted == 0


@pytest.mark.asyncio
async def test_cleanup_api_endpoints():
    """Test the REST API endpoints for categories, preview, and execution."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Categories
        cat_resp = await client.get("/api/v1/cleanup/categories")
        assert cat_resp.status_code == 200
        categories = cat_resp.json()
        assert len(categories) >= 10
        cat_ids = [c["id"] for c in categories]
        assert "claims" in cat_ids
        assert "notifications" in cat_ids
        assert "telemetry" in cat_ids

        # 2. Preview
        prev_resp = await client.post(
            "/api/v1/cleanup/preview",
            json={"categories": ["claims", "notifications"], "time_scope": "current_month"},
        )
        assert prev_resp.status_code == 200
        prev_data = prev_resp.json()
        assert "record_counts" in prev_data
        assert "total_database_records" in prev_data

        # 3. Execute without confirmation fails with 400
        fail_exec = await client.post(
            "/api/v1/cleanup/execute",
            json={"categories": ["notifications"], "time_scope": "current_month", "confirmed": False},
        )
        assert fail_exec.status_code == 400

        # 4. Dry-run execution succeeds without confirmation
        dry_exec = await client.post(
            "/api/v1/cleanup/execute",
            json={"categories": ["notifications"], "time_scope": "current_month", "dry_run": True},
        )
        assert dry_exec.status_code == 200
        assert "Dry-run simulation completed" in dry_exec.json()["message"]


@pytest.mark.asyncio
async def test_dashboard_stats_reconciled_after_cleanup():
    """Verify that dashboard metrics and claims /stats API are immediately reconciled after cleanup."""
    test_claim_id = str(uuid.uuid4())
    async with TaskAsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=test_claim_id,
            claim_number=f"TEST-STATS-{test_claim_id[:6]}",
            dol="09/01/2026",
            insured_first_name="Stats",
            insured_last_name="User",
            policy_state="FL",
            loss_location_state="FL",
            record_status=RecordStatusEnum.NEW,
            created_at=datetime.now(),
        )
        session.add(claim)
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Check stats before cleanup
        before_resp = await client.get("/api/v1/claims/stats")
        assert before_resp.status_code == 200
        before_total = before_resp.json()["total_claims"]
        assert before_total >= 1

        # Execute cleanup
        clean_resp = await client.post(
            "/api/v1/cleanup/execute",
            json={"categories": ["claims"], "time_scope": "all_time", "confirmed": True},
        )
        assert clean_resp.status_code == 200
        assert clean_resp.json()["records_deleted"]["claims"] >= 1

        # Check stats after cleanup: must be exactly reconciled!
        after_resp = await client.get("/api/v1/claims/stats")
        assert after_resp.status_code == 200
        after_total = after_resp.json()["total_claims"]
        assert after_total == 0
