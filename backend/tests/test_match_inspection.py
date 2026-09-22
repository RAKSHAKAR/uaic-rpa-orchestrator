"""Tests for Fuzzy Match Candidate Inspection & Resolution Modal parity and endpoints."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import AsyncSessionLocal
from app.main import app
from app.models.claim import ClaimRecord, RecordStatusEnum
from app.models.court_case import ScrapedCourtCase
from app.models.match_result import MatchPair, MatchReviewStatusEnum, PartyTypeEnum


@pytest.mark.asyncio
async def test_match_inspection_enriched_pending_and_detail():
    """Verify GET /api/v1/matches/pending and GET /api/v1/matches/{id} return full claim and court case metadata."""
    claim_id = str(uuid.uuid4())
    case_id = str(uuid.uuid4())
    match_id = str(uuid.uuid4())

    async with AsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number="CLM-INSPECT-777",
            exposure_number="002",
            dol="04/12/2023",
            policy_state="FL",
            loss_location_state="FL",
            insured_first_name="Marcus",
            insured_last_name="Vance",
            claimant_first_name="Elena",
            claimant_last_name="Rostova",
            driver_first_name="David",
            driver_last_name="Vance",
            record_status=RecordStatusEnum.MANUAL_REVIEW,
        )
        session.add(claim)

        case = ScrapedCourtCase(
            id=case_id,
            claim_id=claim_id,
            county_name="Hillsborough County",
            county_website="https://hover.hillsclerk.com",
            case_number="23-CA-004412",
            case_style="Elena Rostova vs Marcus Vance",
            cleaned_case_style="ELENA ROSTOVA VS MARCUS VANCE",
            filing_date="05/01/2023",
            case_status="PENDING",
            case_type="AUTO NEGLIGENCE",
            raw_payload={"Court": "Thirteenth Judicial Circuit", "Division": "Circuit Civil"},
        )
        session.add(case)

        mp = MatchPair(
            id=match_id,
            claim_id=claim_id,
            court_case_id=case_id,
            party_type=PartyTypeEnum.CLAIMANT,
            party_name="Elena Rostova",
            case_style="Elena Rostova vs Marcus Vance",
            similarity_score=0.92,
            threshold_applied=0.60,
            review_status=MatchReviewStatusEnum.PENDING_REVIEW,
        )
        session.add(mp)
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Test /pending contains enriched metadata
        res = await ac.get("/api/v1/matches/pending")
        assert res.status_code == 200
        items = res.json()
        target = next((item for item in items if item["id"] == match_id), None)
        assert target is not None
        assert target["claim_number"] == "CLM-INSPECT-777"
        assert target["exposure_number"] == "002"
        assert target["dol"] == "04/12/2023"
        assert target["policy_state"] == "FL"
        assert target["insured_name"] == "Marcus Vance"
        assert target["claimant_name"] == "Elena Rostova"
        assert target["driver_name"] == "David Vance"
        assert target["case_number"] == "23-CA-004412"
        assert target["county_name"] == "Hillsborough County"
        assert target["case_type"] == "AUTO NEGLIGENCE"
        assert target["case_status"] == "PENDING"
        assert target["similarity_score"] == 0.92

        # 2. Test single match inspection endpoint GET /api/v1/matches/{id}
        res_single = await ac.get(f"/api/v1/matches/{match_id}")
        assert res_single.status_code == 200
        single_data = res_single.json()
        assert single_data["id"] == match_id
        assert single_data["claim_number"] == "CLM-INSPECT-777"
        assert single_data["county_website"] == "https://hover.hillsclerk.com"
        assert single_data["cleaned_case_style"] == "ELENA ROSTOVA VS MARCUS VANCE"

        # 3. Test review resolution with review notes and reviewer name
        review_payload = {
            "decision": "APPROVED",
            "reviewed_by": "Senior Adjuster Jane",
            "review_notes": "Cross-verified vehicle VIN and driver license from police report.",
        }
        res_review = await ac.post(f"/api/v1/matches/{match_id}/review", json=review_payload)
        assert res_review.status_code == 200

        # 4. Verify match status and notes persisted
        res_after = await ac.get(f"/api/v1/matches/{match_id}")
        assert res_after.status_code == 200
        after_data = res_after.json()
        assert after_data["review_status"] == "APPROVED"
        assert after_data["reviewed_by"] == "Senior Adjuster Jane"
        assert after_data["review_notes"] == "Cross-verified vehicle VIN and driver license from police report."
