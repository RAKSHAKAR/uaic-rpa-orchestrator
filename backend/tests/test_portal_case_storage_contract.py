"""Portal payload shape and transactional replacement after a complete search."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base
from app.models.claim import BotStatusEnum, ClaimRecord, RecordStatusEnum
from app.models.court_case import ScrapedCourtCase
from app.schemas.settings import SystemSettings
from app.tasks import scraper_tasks


def test_canonical_case_keeps_exact_v4_fields_and_validates_date():
    case = {
        "CaseNumber": "24-123",
        "CaseStyle": "ALPHA VS BETA",
        "FilingDate": "2024-06-15",
        "CaseStatus": "OPEN",
        "CaseType": "CIVIL",
        "CountyWebsite": "should not be in raw payload",
    }
    assert scraper_tasks.canonical_portal_case("dallas", case) == {
        "CaseNumber": "24-123",
        "CaseStyle": "ALPHA VS BETA",
        "FilingDate": "06/15/2024",
        "CaseStatus": "OPEN",
        "CaseType": "CIVIL",
    }
    assert set(scraper_tasks.canonical_portal_case("harris_jp", case)) == {
        "CaseNumber", "CaseStyle", "FilingDate", "CaseStatus"
    }
    with pytest.raises(ValueError, match="valid filing date"):
        scraper_tasks.canonical_portal_case("dallas", {**case, "FilingDate": "unknown"})


@pytest.mark.asyncio
async def test_failed_search_preserves_previous_case_until_successful_replacement(tmp_path, monkeypatch):
    import app.models  # noqa: F401

    engine = create_async_engine(f"sqlite+aiosqlite:///{(tmp_path / 'cases.db').as_posix()}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
    monkeypatch.setattr(scraper_tasks, "TaskAsyncSessionLocal", session_factory)

    async def runtime_settings():
        return SystemSettings()

    monkeypatch.setattr(scraper_tasks, "get_system_settings_async", runtime_settings)
    monkeypatch.setattr(scraper_tasks, "_acquire_browser_slot", AsyncMock(return_value=True))
    monkeypatch.setattr(scraper_tasks, "_release_browser_slot", AsyncMock())
    monkeypatch.setattr(scraper_tasks, "is_portal_in_cooldown", lambda _: (False, 0, ""))
    monkeypatch.setattr(scraper_tasks, "append_portal_execution_log", lambda *args, **kwargs: None)
    monkeypatch.setattr(scraper_tasks, "log_audit_event_async", AsyncMock())
    monkeypatch.setattr(scraper_tasks.celery_app, "send_task", MagicMock())
    from app.automation.browser_manager import ChromeSession

    monkeypatch.setattr(ChromeSession, "configure_and_pin_profile", MagicMock())

    tab = MagicMock()
    tab.is_closed.return_value = True
    tab.bring_to_front = AsyncMock()
    browser = MagicMock(stage_timings={}, tabs={"broward": tab})
    browser.get_or_create_tab = AsyncMock(return_value=tab)
    runner = MagicMock()
    runner.__aenter__ = AsyncMock(return_value=browser)
    runner.__aexit__ = AsyncMock(return_value=None)
    monkeypatch.setattr(scraper_tasks, "SingleSessionBrowserRunner", lambda **kwargs: runner)
    monkeypatch.setattr(scraper_tasks.BrowardScraper, "capture_screenshot_on_error", AsyncMock(return_value=None))

    claim_id = str(uuid.uuid4())
    old_payload = {
        "CaseNumber": "OLD-1", "CaseStyle": "OLD VS CASE", "FilingDate": "05/01/2020",
        "CaseStatus": "OPEN", "CaseType": "CIVIL",
    }
    async with session_factory() as db:
        db.add(ClaimRecord(
            id=claim_id,
            claim_number="TEST-PRESERVE-CASE",
            claimant_first_name="Jane",
            claimant_last_name="Example",
            fl_website_broward="Yes",
            fl_jsonbody_broward=[old_payload],
            fl_botstatus_broward=BotStatusEnum.COMPLETED,
            record_status=RecordStatusEnum.NEW,
        ))
        db.add(ScrapedCourtCase(
            claim_id=claim_id, county_name="Broward County (FL)", county_website="https://example.test",
            case_number="OLD-1", case_style="OLD VS CASE", filing_date="05/01/2020",
            case_status="OPEN", case_type="CIVIL", raw_payload=old_payload,
        ))
        await db.commit()

    try:
        monkeypatch.setattr(
            scraper_tasks.BrowardScraper, "search_on_page",
            AsyncMock(side_effect=RuntimeError("portal unavailable")),
        )
        await scraper_tasks._async_orchestrate_scrapers(claim_id)
        async with session_factory() as db:
            claim = await db.get(ClaimRecord, claim_id)
            rows = list((await db.execute(select(ScrapedCourtCase).where(ScrapedCourtCase.claim_id == claim_id))).scalars())
            assert claim.fl_botstatus_broward == BotStatusEnum.FAILED
            assert claim.fl_jsonbody_broward == [old_payload]
            assert [row.case_number for row in rows] == ["OLD-1"]

        new_payload = {
            "CaseNumber": "NEW-2", "CaseStyle": "JANE VS EXAMPLE", "FilingDate": "06/15/2024",
            "CaseStatus": "OPEN", "CaseType": "CIVIL", "Extra": "drop this",
        }
        monkeypatch.setattr(
            scraper_tasks.BrowardScraper, "search_on_page",
            AsyncMock(return_value=[new_payload]),
        )
        await scraper_tasks._async_orchestrate_scrapers(claim_id)
        async with session_factory() as db:
            claim = await db.get(ClaimRecord, claim_id)
            rows = list((await db.execute(select(ScrapedCourtCase).where(ScrapedCourtCase.claim_id == claim_id))).scalars())
            assert claim.fl_botstatus_broward == BotStatusEnum.COMPLETED
            assert [row.case_number for row in rows] == ["NEW-2"]
            assert set(rows[0].raw_payload) == set(scraper_tasks.PORTAL_CASE_FIELDS["broward"])

        # V4 stores each result row, including distinct party roles sharing a
        # case number and the same row repeated by a later name search.
        async with session_factory() as db:
            claim = await db.get(ClaimRecord, claim_id)
            claim.insured_first_name = "Robert"
            claim.insured_last_name = "Williams"
            await db.commit()

        role_one = {
            "CaseNumber": "DUP-3", "CaseStyle": "ROBERT WILLIAMS VS JANE EXAMPLE",
            "FilingDate": "06/15/2024", "CaseStatus": "OPEN", "CaseType": "CIVIL",
        }
        role_two = {
            "CaseNumber": "DUP-3", "CaseStyle": "JANE EXAMPLE VS ACME CORP",
            "FilingDate": "06/15/2024", "CaseStatus": "OPEN", "CaseType": "CIVIL",
        }

        async def repeated_rows(*, first_name, **_kwargs):
            return [role_one, role_two] if first_name == "Robert" else [role_one]

        search = AsyncMock(side_effect=repeated_rows)
        monkeypatch.setattr(scraper_tasks.BrowardScraper, "search_on_page", search)
        monkeypatch.setattr(scraper_tasks.BrowardScraper, "return_to_search_state", AsyncMock())
        await scraper_tasks._async_orchestrate_scrapers(claim_id)
        assert search.await_count == 2
        async with session_factory() as db:
            claim = await db.get(ClaimRecord, claim_id)
            rows = list((await db.execute(select(ScrapedCourtCase).where(ScrapedCourtCase.claim_id == claim_id))).scalars())
            expected_styles = [role_one["CaseStyle"], role_two["CaseStyle"], role_one["CaseStyle"]]
            assert claim.fl_botstatus_broward == BotStatusEnum.COMPLETED
            assert [case["CaseNumber"] for case in claim.fl_jsonbody_broward] == ["DUP-3"] * 3
            assert [case["CaseStyle"] for case in claim.fl_jsonbody_broward] == expected_styles
            assert [row.case_number for row in rows] == ["DUP-3"] * 3
            assert [row.case_style for row in rows] == expected_styles
            assert [row.raw_payload for row in rows] == claim.fl_jsonbody_broward
    finally:
        await engine.dispose()
