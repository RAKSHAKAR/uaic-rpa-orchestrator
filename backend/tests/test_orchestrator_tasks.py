"""Integration tests for scraping orchestration, fuzzy matching tasks, and Guidewire trigger."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import Base, TaskAsyncSessionLocal, engine
from app.models.claim import ClaimRecord, FuzzyMatchStatusEnum, RecordStatusEnum
from app.tasks.fuzzy_tasks import _async_evaluate_fuzzy_matches, _async_notify_guidewire
from app.tasks.scraper_tasks import _async_orchestrate_scrapers


@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.mark.asyncio
@pytest.mark.requires_redis
async def test_end_to_end_orchestration_and_guidewire_trigger():
    claim_id = str(uuid.uuid4())

    # 1. Insert Claim
    async with TaskAsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number=f"TEST-ORCH-{claim_id[:6]}",
            exposure_number="1",
            claimant_first_name="Sergio",
            claimant_last_name="Gonzalez",
            insured_first_name="Marco",
            insured_last_name="Rodriguez",
            fl_website_miami="Yes",
            fl_website_hillsborough="Yes",
            te_website_dallas="No",
            te_website_travis="No",
            te_website_harris="No",
            te_website_cclerk="No",
            te_website_hcdistrict="No",
            fl_website_broward="No",
            record_status=RecordStatusEnum.NEW,
        )
        session.add(claim)
        await session.commit()

    # 2. Mock Florida Scrapers
    miami_cases = [{
        "CaseNumber": "2026-111719-CC-26",
        "CaseStyle": "MIGUEL TOLEDO ET AL VS SERGIO GONZALEZ ET AL",
        "CountyWebsite": "https://www2.miamidadeclerk.gov/ocs/",
        "FilingDate": "08/21/2026",
        "CaseStatus": "OPEN",
        "CaseType": "CIRCUIT CIVIL",
        "Court": "SD 04",
    }]

    with patch("app.core.celery_app.celery_app.send_task", MagicMock()), \
         patch("app.automation.florida.miami.MiamiDadeScraper.search_by_party_name", AsyncMock(return_value=miami_cases)), \
         patch("app.automation.florida.hillsborough.HillsboroughScraper.search_by_party_name", AsyncMock(return_value=[])):
        
        await _async_orchestrate_scrapers(claim_id)

    # 3. Verify Scraped Case Persisted in DB
    async with TaskAsyncSessionLocal() as session:
        q = select(ClaimRecord).where(ClaimRecord.id == claim_id).options(selectinload(ClaimRecord.scraped_cases))
        res = await session.execute(q)
        claim_after_scrape = res.scalar_one()
        assert len(claim_after_scrape.scraped_cases) == 1
        assert claim_after_scrape.scraped_cases[0].case_number == "2026-111719-CC-26"

    # 4. Run Fuzzy Matching
    with patch("app.core.celery_app.celery_app.send_task", MagicMock()):
        await _async_evaluate_fuzzy_matches(claim_id)

    # 5. Verify Fuzzy Match Found and Dispatched
    async with TaskAsyncSessionLocal() as session:
        q = select(ClaimRecord).where(ClaimRecord.id == claim_id)
        res = await session.execute(q)
        claim_after_match = res.scalar_one()
        assert claim_after_match.record_status == RecordStatusEnum.MATCH_FOUND
        assert claim_after_match.fuzzy_match_status == FuzzyMatchStatusEnum.COMPLETED
        assert claim_after_match.final_matched_json is not None
        assert "CaseItems" in claim_after_match.final_matched_json

    # 6. Run Guidewire Notification
    await _async_notify_guidewire(claim_id)

    # 7. Verify Completed Status and Activity ID
    async with TaskAsyncSessionLocal() as session:
        q = select(ClaimRecord).where(ClaimRecord.id == claim_id)
        res = await session.execute(q)
        claim_final = res.scalar_one()
        assert claim_final.record_status == RecordStatusEnum.COMPLETED
        assert claim_final.activity_id is not None
        assert "MOCK-ACT" in claim_final.activity_id or "GW-" in claim_final.activity_id

        # Clean up
        await session.delete(claim_final)
        await session.commit()
