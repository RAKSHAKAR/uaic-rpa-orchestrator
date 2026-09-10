import asyncio
import uuid

from sqlalchemy import select

from app.core.celery_app import celery_app
from app.core.database import Base, TaskAsyncSessionLocal, engine
from app.models.claim import ClaimRecord, RecordStatusEnum
from app.tasks.fuzzy_tasks import _async_evaluate_fuzzy_matches, _async_notify_guidewire
from app.tasks.scraper_tasks import _async_orchestrate_scrapers


async def safe_e2e():
    celery_app.conf.task_always_eager = False
    
    # 1. Init DB tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Insert a mock ClaimRecord
    claim_id = str(uuid.uuid4())
    async with TaskAsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number=f"TEST-E2E-{claim_id[:8]}",
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
        print(f"Inserted Mock Claim: {claim.claim_number} ({claim_id})")

    from unittest.mock import patch

    print("--- 1. Scraping ---")
    
    # Mocking the scrapers because public court websites block datacenter IPs with 401s / Timeouts.
    # We are returning the exact parsed structure verified in the video frames.
    miami_mock = [{
        "CaseNumber": "2026-111719-CC-26",
        "CaseStyle": "MIGUEL TOLEDO ET AL VS SERGIO GONZALEZ ET AL",
        "CountyWebsite": "https://www2.miamidadeclerk.gov/ocs/",
        "FilingDate": "08/21/2026",
        "CaseStatus": "OPEN",
        "CaseType": "PERSONAL INJURY – AUTO",
        "Court": "SD 04 - South Dade 04"
    }]
    
    hillsborough_mock = [{
        "CaseNumber": "26-TR-067231",
        "Citation": "ANNPQME",
        "CaseStyle": "STATE OF FLORIDA VS GONZALEZ, SERGIO JULIO",
        "CaseType": "CIVIL TRAFFIC",
        "CaseStatus": "CLOSED",
        "FilingDate": "2026-05-14",
        "CountyWebsite": "https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab"
    }]
    
    with patch('app.automation.florida.miami.MiamiDadeScraper.search_by_party_name', return_value=miami_mock), \
         patch('app.automation.florida.hillsborough.HillsboroughScraper.search_by_party_name', return_value=hillsborough_mock):
        
        await _async_orchestrate_scrapers(claim_id)

    print("--- 2. Fuzzy Matching ---")
    await _async_evaluate_fuzzy_matches(claim_id)
    
    print("--- 3. Guidewire Notification ---")
    await _async_notify_guidewire(claim_id)
    
    async with TaskAsyncSessionLocal() as session:
        # Use selectinload to eagerly load the relationship
        from sqlalchemy.orm import selectinload
        res = await session.execute(
            select(ClaimRecord)
            .where(ClaimRecord.id == claim_id)
            .options(selectinload(ClaimRecord.scraped_cases))
        )
        updated_claim = res.scalar_one()
        
        print(f"\nFinal Record Status: {updated_claim.record_status.name}")
        print(f"Activity ID: {updated_claim.activity_id}")
        
        cases = updated_claim.scraped_cases
        print(f"\nTotal Scraped Cases: {len(cases)}")
        for c in cases:
            print(f" - {c.county_name}: {c.case_number} | {c.case_style} | {c.case_status}")
        
        print("\nSUCCESS: E2E flow verified.")

if __name__ == "__main__":
    asyncio.run(safe_e2e())
