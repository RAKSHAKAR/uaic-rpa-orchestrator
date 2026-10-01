"""Power Automate V4 retains each matching court result row through Guidewire."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.automation.session_runner import SingleSessionBrowserRunner
from app.core.database import Base
from app.models.claim import ClaimRecord, RecordStatusEnum
from app.models.court_case import ScrapedCourtCase
from app.models.guidewire import GuidewireActivity
from app.schemas.settings import SystemSettings
from app.tasks import fuzzy_tasks, queue_runner


@pytest.mark.asyncio
async def test_browser_session_preserves_repeated_case_rows_across_party_searches(monkeypatch):
    runner = SingleSessionBrowserRunner()
    page = MagicMock()
    monkeypatch.setattr(runner, "get_or_create_tab", AsyncMock(return_value=page))
    scraper = MagicMock()
    scraper.base_url = "https://example.test/court"
    scraper.county_name = "Example Court"
    scraper.stage_timings = {}
    case = {"CaseNumber": "2024-12345", "CaseStyle": "EXAMPLE VS ACME"}
    scraper.search_on_page = AsyncMock(side_effect=[[case], [case.copy()]])

    rows = await runner.execute_portal_searches(
        "example", scraper, [("claimant", "Jane", "Example"), ("insured", "Robert", "Example")]
    )

    assert rows == [case, case]
    assert scraper.search_on_page.await_count == 2


@pytest.mark.asyncio
async def test_harris_district_same_number_role_rows_reach_guidewire(tmp_path, monkeypatch):
    import app.models  # noqa: F401

    engine = create_async_engine(f"sqlite+aiosqlite:///{(tmp_path / 'v4_rows.db').as_posix()}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
    monkeypatch.setattr(fuzzy_tasks, "TaskAsyncSessionLocal", session_factory)

    settings = SystemSettings()
    settings.integration.notification_dispatch_mode = "guidewire_activity"
    settings.integration.auto_push_on_match = True
    settings.integration.guidewire_mock_mode = True

    async def runtime_settings():
        return settings

    monkeypatch.setattr(fuzzy_tasks, "get_system_settings_async", runtime_settings)
    monkeypatch.setattr(fuzzy_tasks.NotificationService, "emit_event", AsyncMock())
    monkeypatch.setattr(fuzzy_tasks, "log_audit_event_async", AsyncMock())
    monkeypatch.setattr(fuzzy_tasks.celery_app, "send_task", MagicMock())
    monkeypatch.setattr(queue_runner, "remove_active_queue_item_id", MagicMock())
    monkeypatch.setattr(queue_runner, "is_auto_queue_enabled", MagicMock(return_value=False))

    claim_id = str(uuid.uuid4())
    case_number = "2024-12345"
    case_styles = [
        "JANE EXAMPLE VS ROBERT WILLIAMS",
        "JANE EXAMPLE VS ACME CORPORATION",
    ]
    async with session_factory() as db:
        db.add(ClaimRecord(
            id=claim_id,
            claim_number="TEST-V4-ROLE-ROWS",
            exposure_number="001",
            claimant_first_name="Jane",
            claimant_last_name="Example",
            record_status=RecordStatusEnum.SCRAPING_COMPLETED,
        ))
        for style in case_styles:
            db.add(ScrapedCourtCase(
                id=str(uuid.uuid4()),
                claim_id=claim_id,
                county_name="Harris District Court (TX)",
                county_website="https://www.hcdistrictclerk.com/",
                case_number=case_number,
                case_style=style,
                filing_date="06/15/2024",
                case_status="OPEN",
                case_type="CIVIL",
            ))
        await db.commit()

    try:
        await fuzzy_tasks._async_evaluate_fuzzy_matches(claim_id)
        async with session_factory() as db:
            claim = await db.get(ClaimRecord, claim_id)
            matched = claim.final_matched_json["CaseItems"]
            assert len(matched) == 2
            assert [item["CaseNumber"] for item in matched] == [case_number] * 2
            assert [item["CaseStyle"] for item in matched] == case_styles

        await fuzzy_tasks._async_notify_guidewire(claim_id)
        async with session_factory() as db:
            activity = (await db.execute(
                select(GuidewireActivity).where(GuidewireActivity.claim_id == claim_id)
            )).scalar_one()
            case_items = activity.request_payload["CaseItems"]
            assert len(case_items) == 2
            assert [item["CaseNumber"] for item in case_items] == [case_number] * 2
            assert [item["CaseStyle"] for item in case_items] == case_styles
    finally:
        await engine.dispose()
