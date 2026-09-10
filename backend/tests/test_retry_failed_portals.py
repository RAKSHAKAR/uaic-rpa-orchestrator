"""Unit and integration tests for Retry from Failed Portal Only (§66)."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.main import app
from app.models.claim import BotStatusEnum, ClaimRecord, RecordStatusEnum
from app.models.court_case import ScrapedCourtCase
from app.tasks.retry_tasks import _async_retrigger_failed_cases
from app.tasks.scraper_tasks import _async_orchestrate_scrapers


@pytest.fixture
async def sample_claim_with_failures():
    """Create a test claim with one COMPLETED portal and two FAILED portals."""
    async with AsyncSessionLocal() as session:
        claim_id = str(uuid.uuid4())
        claim = ClaimRecord(
            id=claim_id,
            claim_number=f"RET{uuid.uuid4().hex[:6].upper()}",
            exposure_number="1",
            policy_state="FL",
            loss_location_state="FL",
            insured_first_name="John",
            insured_last_name="Doe",
            claimant_first_name="Jane",
            claimant_last_name="Smith",
            driver_first_name="John",
            driver_last_name="Doe",
            dol="05/12/2023",
            record_status=RecordStatusEnum.FAILED,
            retry_count=1,
            # FL portals: Broward COMPLETED, Hillsborough & Miami FAILED
            fl_website_broward="Yes",
            fl_botstatus_broward=BotStatusEnum.COMPLETED,
            fl_website_hillsborough="Yes",
            fl_botstatus_hillsborough=BotStatusEnum.FAILED,
            fl_website_miami="Yes",
            fl_botstatus_miami=BotStatusEnum.FAILED,
        )
        session.add(claim)

        # Existing case for Broward
        existing_broward_case = ScrapedCourtCase(
            claim_id=claim_id,
            county_name="Broward County Clerk",
            county_website="https://www.browardclerk.org",
            case_number="CACE-23-001234",
            case_style="Smith vs Doe",
            filing_date="06/01/2023",
            case_status="Open",
            case_type="Civil",
            raw_payload={"CaseNumber": "CACE-23-001234"},
        )
        session.add(existing_broward_case)
        await session.commit()

        yield claim_id

        # Cleanup
        async with AsyncSessionLocal() as cleanup_session:
            db_claim = await cleanup_session.get(ClaimRecord, claim_id)
            if db_claim:
                await cleanup_session.delete(db_claim)
                await cleanup_session.commit()


@pytest.mark.asyncio
async def test_retry_failed_endpoint_success(sample_claim_with_failures):
    """Test POST /api/v1/claims/{id}/retry-failed dispatches only failed portals."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.api.v1.endpoints.claims.celery_app.send_task") as mock_send_task:
            response = await client.post(f"/api/v1/claims/{sample_claim_with_failures}/retry-failed")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "hillsborough" in data["retried_portals"]
            assert "miami" in data["retried_portals"]
            assert "broward" not in data["retried_portals"]

            # Verify Celery task was dispatched with retry_failed_only=True
            mock_send_task.assert_called_once_with(
                "app.tasks.scraper_tasks.orchestrate_court_scrapers_task",
                args=[sample_claim_with_failures, None, True],
                queue="scrapers",
            )


@pytest.mark.asyncio
async def test_retry_failed_endpoint_no_failures():
    """Test POST /api/v1/claims/{id}/retry-failed when all portals are already COMPLETED."""
    async with AsyncSessionLocal() as session:
        claim_id = str(uuid.uuid4())
        claim = ClaimRecord(
            id=claim_id,
            claim_number=f"ALL{uuid.uuid4().hex[:6].upper()}",
            exposure_number="1",
            policy_state="FL",
            loss_location_state="FL",
            record_status=RecordStatusEnum.SCRAPING_COMPLETED,
            fl_website_broward="Yes",
            fl_botstatus_broward=BotStatusEnum.COMPLETED,
            fl_website_hillsborough="Yes",
            fl_botstatus_hillsborough=BotStatusEnum.COMPLETED,
        )
        session.add(claim)
        await session.commit()

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch("app.api.v1.endpoints.claims.celery_app.send_task") as mock_send_task:
                response = await client.post(f"/api/v1/claims/{claim_id}/retry-failed")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "info"
                assert data["retried_portals"] == []
                mock_send_task.assert_not_called()
    finally:
        async with AsyncSessionLocal() as session:
            c = await session.get(ClaimRecord, claim_id)
            if c:
                await session.delete(c)
                await session.commit()


@pytest.mark.asyncio
async def test_retry_failed_endpoint_not_found():
    """Test POST /api/v1/claims/{id}/retry-failed returns 404 for nonexistent claim."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(f"/api/v1/claims/{uuid.uuid4()}/retry-failed")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_bulk_retry_failed_portals_only(sample_claim_with_failures):
    """Test POST /api/v1/claims/bulk-retry with failed_portals_only=True."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.api.v1.endpoints.claims.celery_app.send_task") as mock_send_task:
            response = await client.post(
                "/api/v1/claims/bulk-retry",
                json={"claim_ids": [sample_claim_with_failures], "failed_portals_only": True},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["affected_count"] == 1
            assert "failed portals only" in data["message"]

            mock_send_task.assert_called_once_with(
                "app.tasks.scraper_tasks.orchestrate_court_scrapers_task",
                args=[sample_claim_with_failures, None, True],
                queue="scrapers",
            )


@pytest.mark.asyncio
async def test_async_orchestrate_scrapers_retry_failed_only(sample_claim_with_failures):
    """Test _async_orchestrate_scrapers runs ONLY failed portals and preserves completed cases."""
    from app.automation.florida.hillsborough import HillsboroughScraper
    from app.automation.florida.miami import MiamiDadeScraper

    mock_runner = AsyncMock()
    mock_session = AsyncMock()
    mock_runner.__aenter__.return_value = mock_session
    mock_session.stage_timings = {}
    mock_session.tabs = {}

    # Mock get_or_create_tab to return a fake page
    mock_page = AsyncMock()
    mock_session.get_or_create_tab = AsyncMock(return_value=mock_page)

    # Mock search_on_page at the class level for the scrapers that will be exercised
    hillsborough_case = {
        "CaseNumber": "HILL-2023-9999",
        "CaseStyle": "Smith v Doe",
        "FilingDate": "06/15/2023",
        "CaseStatus": "Pending",
        "CaseType": "Auto Negligence",
    }

    original_hillsborough_search = HillsboroughScraper.search_on_page
    original_miami_search = MiamiDadeScraper.search_on_page

    async def hillsborough_mock(self, page, first_name, last_name, date_of_loss=None, **kwargs):
        return [hillsborough_case]

    async def miami_mock(self, page, first_name, last_name, date_of_loss=None, **kwargs):
        return []

    HillsboroughScraper.search_on_page = hillsborough_mock
    MiamiDadeScraper.search_on_page = miami_mock

    try:
        with patch("app.tasks.scraper_tasks.SingleSessionBrowserRunner", return_value=mock_runner), \
             patch("app.tasks.scraper_tasks.celery_app.send_task") as mock_fuzzy_task:

            await _async_orchestrate_scrapers(
                claim_id=sample_claim_with_failures,
                single_bot_key=None,
                retry_failed_only=True,
            )

            # Verify fuzzy matcher was dispatched
            mock_fuzzy_task.assert_called_once_with(
                "app.tasks.fuzzy_tasks.evaluate_fuzzy_matches_task",
                args=[sample_claim_with_failures],
                queue="matcher",
            )
    finally:
        HillsboroughScraper.search_on_page = original_hillsborough_search
        MiamiDadeScraper.search_on_page = original_miami_search

    # Verify database state after retry
    async with AsyncSessionLocal() as session:
        claim = await session.get(ClaimRecord, sample_claim_with_failures)
        assert claim is not None
        # Broward was NOT retried and remains COMPLETED
        assert claim.fl_botstatus_broward == BotStatusEnum.COMPLETED
        # Hillsborough succeeded and changed from FAILED to COMPLETED
        assert claim.fl_botstatus_hillsborough == BotStatusEnum.COMPLETED
        # Miami returned 0 cases and changed from FAILED to NO_MATCH_FOUND
        assert claim.fl_botstatus_miami == BotStatusEnum.NO_MATCH_FOUND
        # Overall claim status should now be SCRAPING_COMPLETED since all portals succeeded
        assert claim.record_status == RecordStatusEnum.SCRAPING_COMPLETED

        # Check scraped cases
        cases_q = select(ScrapedCourtCase).where(ScrapedCourtCase.claim_id == sample_claim_with_failures)
        res = await session.execute(cases_q)
        all_cases = res.scalars().all()

        # Both the original Broward case and the new Hillsborough case must exist!
        case_numbers = [c.case_number for c in all_cases]
        assert "CACE-23-001234" in case_numbers, "Original Broward case must be preserved!"
        assert "HILL-2023-9999" in case_numbers, "New Hillsborough case must be inserted!"
        assert len(all_cases) == 2


@pytest.mark.asyncio
async def test_async_retrigger_failed_cases_scheduled_task(sample_claim_with_failures):
    """Test periodic retrigger_failed_cases Celery Beat task passes retry_failed_only=True."""
    with patch("app.tasks.retry_tasks.celery_app.send_task") as mock_send_task:
        await _async_retrigger_failed_cases()

        mock_send_task.assert_called_with(
            "app.tasks.scraper_tasks.orchestrate_court_scrapers_task",
            args=[sample_claim_with_failures, None, True],
            queue="scrapers",
        )
