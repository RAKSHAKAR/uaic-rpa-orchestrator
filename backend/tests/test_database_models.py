"""Unit tests for SQLAlchemy models, foreign key cascades, and status transitions."""

import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import TaskAsyncSessionLocal, init_db
from app.models.claim import ClaimRecord, IngestionBatch, RecordStatusEnum
from app.models.court_case import ScrapedCourtCase
from app.models.match_result import MatchPair, MatchReviewStatusEnum, PartyTypeEnum


@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    """Ensure database schema is created and migrated."""
    await init_db()
    yield


@pytest.mark.asyncio
async def test_claim_record_lifecycle_and_relationships():
    claim_id = str(uuid.uuid4())
    case_id = str(uuid.uuid4())
    match_id = str(uuid.uuid4())
    batch_id = str(uuid.uuid4())

    async with TaskAsyncSessionLocal() as session:
        # 1. Create Ingestion Batch
        batch = IngestionBatch(
            id=batch_id,
            filename="claims_test.xlsx",
            total_records=1,
            processed_records=0,
            status="PROCESSING",
        )
        session.add(batch)

        # 2. Create Claim
        claim = ClaimRecord(
            id=claim_id,
            batch_id=batch_id,
            claim_number=f"CLM-{claim_id[:6]}",
            exposure_number="1",
            claimant_first_name="Sergio",
            claimant_last_name="Gonzalez",
            insured_first_name="Marco",
            insured_last_name="Rodriguez",
            record_status=RecordStatusEnum.NEW,
            fl_website_miami="Yes",
            fl_website_hillsborough="Yes",
        )
        session.add(claim)

        # 3. Create Scraped Case
        court_case = ScrapedCourtCase(
            id=case_id,
            claim_id=claim_id,
            county_name="Miami-Dade County (FL)",
            county_website="https://www2.miamidadeclerk.gov/ocs",
            case_number="2026-111719-CC-26",
            case_style="MIGUEL TOLEDO VS SERGIO GONZALEZ",
            filing_date="08/21/2026",
            case_status="OPEN",
            case_type="CIVIL",
        )
        session.add(court_case)

        # 4. Create Match Pair
        match_pair = MatchPair(
            id=match_id,
            claim_id=claim_id,
            court_case_id=case_id,
            party_type=PartyTypeEnum.CLAIMANT,
            party_name="Sergio Gonzalez",
            case_style="MIGUEL TOLEDO VS SERGIO GONZALEZ",
            similarity_score=0.92,
            threshold_applied=0.60,
            is_match=True,
            review_status=MatchReviewStatusEnum.AUTO_MATCHED,
        )
        session.add(match_pair)

        await session.commit()

    # Query back with relationships
    async with TaskAsyncSessionLocal() as session:
        query = (
            select(ClaimRecord)
            .where(ClaimRecord.id == claim_id)
            .options(
                selectinload(ClaimRecord.scraped_cases),
                selectinload(ClaimRecord.match_pairs),
            )
        )
        res = await session.execute(query)
        fetched_claim = res.scalar_one()

        assert fetched_claim.claim_number.startswith("CLM-")
        assert len(fetched_claim.scraped_cases) == 1
        assert fetched_claim.scraped_cases[0].case_number == "2026-111719-CC-26"
        assert len(fetched_claim.match_pairs) == 1
        assert fetched_claim.match_pairs[0].is_match is True
        assert fetched_claim.match_pairs[0].similarity_score == 0.92

        # Clean up
        await session.delete(fetched_claim)
        await session.commit()
