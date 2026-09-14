"""Integration tests for GuidewireActivity and FilteredOutCase pipeline persistence."""

import uuid

import pytest
from sqlalchemy import select

from app.core.database import TaskAsyncSessionLocal, init_db
from app.models import (
    ClaimRecord,
    FilteredOutCase,
    GuidewireActivity,
    RecordStatusEnum,
    ScrapedCourtCase,
)
from app.tasks.fuzzy_tasks import _async_evaluate_fuzzy_matches, _async_notify_guidewire


@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    """Ensure database schema is created and initialized."""
    await init_db()
    yield


@pytest.mark.asyncio
async def test_evaluate_fuzzy_matches_persists_filtered_out_cases():
    """Verify _async_evaluate_fuzzy_matches persists FilteredOutCase records for ineligible/non-matched cases."""
    claim_id = str(uuid.uuid4())
    case1_id = str(uuid.uuid4())
    case2_id = str(uuid.uuid4())

    async with TaskAsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number="CLM-FILTER-TEST-001",
            insured_first_name="Alexander",
            insured_last_name="Hamilton",
            claimant_first_name="Aaron",
            claimant_last_name="Burr",
            record_status=RecordStatusEnum.SCRAPING_COMPLETED,
        )
        session.add(claim)

        # Case 1: Ineligible case status (e.g. TRAFFIC or DISMISSED)
        case1 = ScrapedCourtCase(
            id=case1_id,
            claim_id=claim_id,
            county_name="broward",
            county_website="https://www.browardclerk.org/Web2/",
            case_number="COCE-24-TRAFFIC-001",
            case_style="STATE OF FLORIDA VS UNRELATED DRIVER",
            case_type="TRAFFIC INFRACTION",
            case_status="DISMISSED",
            filing_date="01/01/2005",  # Prior to 2010 min_filing_date
        )

        # Case 2: Eligible status but completely unrelated names
        case2 = ScrapedCourtCase(
            id=case2_id,
            claim_id=claim_id,
            county_name="broward",
            county_website="https://www.browardclerk.org/Web2/",
            case_number="CACE-24-009999",
            case_style="COMPLETELY DIFFERENT PERSON VS ANOTHER STRANGER",
            case_type="CIVIL",
            case_status="OPEN",
            filing_date="05/15/2023",
        )
        session.add_all([case1, case2])
        await session.commit()

    # Execute fuzzy matching pipeline
    await _async_evaluate_fuzzy_matches(claim_id)

    # Verify FilteredOutCase records were created
    async with TaskAsyncSessionLocal() as session:
        q = select(FilteredOutCase).where(FilteredOutCase.claim_id == claim_id)
        res = await session.execute(q)
        filtered_cases = list(res.scalars().all())

        assert len(filtered_cases) >= 1
        case_nums = [fc.case_number for fc in filtered_cases]
        assert "COCE-24-TRAFFIC-001" in case_nums

        # Clean up
        claim_rec = await session.get(ClaimRecord, claim_id)
        if claim_rec:
            await session.delete(claim_rec)
            await session.commit()


@pytest.mark.asyncio
async def test_notify_guidewire_persists_guidewire_activity_record():
    """Verify _async_notify_guidewire persists a GuidewireActivity record in the database."""
    claim_id = str(uuid.uuid4())

    async with TaskAsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number="0123456789",
            exposure_number="001",
            insured_first_name="Thomas",
            insured_last_name="Jefferson",
            claimant_first_name="John",
            claimant_last_name="Adams",
            record_status=RecordStatusEnum.MATCH_FOUND,
            final_matched_json={
                "CaseItems": [
                    {
                        "CaseNumber": "COCE-24-8888",
                        "CaseStyle": "JOHN ADAMS VS THOMAS JEFFERSON",
                        "CountyWebsite": "https://www.browardclerk.org/Web2/",
                        "SuitFiledDate": "2024-01-15",
                    }
                ]
            },
        )
        session.add(claim)
        await session.commit()

    # Trigger Guidewire notification helper (mock mode is enabled in test environment)
    await _async_notify_guidewire(claim_id)

    # Verify GuidewireActivity record
    async with TaskAsyncSessionLocal() as session:
        q = select(GuidewireActivity).where(GuidewireActivity.claim_id == claim_id)
        res = await session.execute(q)
        activities = list(res.scalars().all())

        assert len(activities) == 1
        act = activities[0]
        assert act.claim_number == "0123456789"
        assert act.exposure_number == "001"
        assert act.status == "SUCCESS"
        assert act.http_status == 200
        assert act.guidewire_activity_id is not None
        assert "ClaimNumber" in act.request_payload

        # Clean up
        claim_rec = await session.get(ClaimRecord, claim_id)
        if claim_rec:
            await session.delete(claim_rec)
            await session.commit()
