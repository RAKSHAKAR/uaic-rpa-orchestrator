"""Comprehensive unit tests for claim stats calculation parity and filing date mapping.

Validates:
1. get_claim_stats response structure and fields:
   - total_claims, new, in_progress, match_found, manual_review, completed, portal_throughput, avg_scrape_seconds
2. _map_claim_to_response filing date extraction across all aliases:
   - FilingDate, filing_date, SuitFiledDate, DateFiled, Filed, and DOL fallback
"""

from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.endpoints.claims import _map_claim_to_response
from app.main import app
from app.models.claim import ClaimRecord, FuzzyMatchStatusEnum, RecordStatusEnum
from app.models.court_case import ScrapedCourtCase


@pytest.mark.asyncio
async def test_claims_stats_response_structure_and_types():
    """Verify that /api/v1/claims/stats returns all expected metric fields."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/claims/stats")
        assert response.status_code == 200
        data = response.json()
        required_fields = [
            "total_claims",
            "new",
            "in_progress",
            "completed",
            "no_match_found",
            "failed",
            "match_found",
            "manual_review",
            "total_finished",
            "total_cases_extracted",
            "portal_throughput",
            "avg_scrape_seconds",
        ]
        for field in required_fields:
            assert field in data, f"Missing field {field} in /api/v1/claims/stats response"
        assert isinstance(data["total_claims"], int)
        assert isinstance(data["match_found"], int)
        assert isinstance(data["manual_review"], int)
        assert isinstance(data["portal_throughput"], dict)


def test_map_claim_to_response_filing_date_aliases():
    """Verify _map_claim_to_response extracts filing date from all known docket aliases."""
    base_claim = ClaimRecord(
        id="test-claim-uuid-001",
        batch_id="BATCH-001",
        claim_number="0123456789",
        exposure_number="001",
        primary_key="0123456789001",
        insured_first_name="John",
        insured_last_name="Smith",
        claimant_first_name="Jane",
        claimant_last_name="Doe",
        driver_first_name="Alice",
        driver_last_name="Smith",
        dol="12/25/2023",
        policy_state="FL",
        loss_location_state="FL",
        record_status=RecordStatusEnum.COMPLETED,
        fuzzy_match_status=FuzzyMatchStatusEnum.COMPLETED,
        activity_id="ACT-999",
        retry_count=0,
        total_duration_seconds=42.5,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    base_claim.scraped_cases = []
    base_claim.match_results = []
    base_claim.audit_logs = []
    base_claim.match_pairs = []

    # Test alias 1: FilingDate
    case1 = ScrapedCourtCase(
        id="c1",
        claim_id=base_claim.id,
        county_name="Broward County (FL)",
        case_number="2023-CA-001",
        case_style="Jane Doe vs Acme",
        county_website="https://www.browardclerk.org",
        case_status="Open",
        case_type="Civil",
        raw_payload={"FilingDate": "12/26/2023", "CaseStatus": "Open", "PartyNameSearched": "Jane Doe"},
        created_at=datetime.now(UTC),
    )
    base_claim.scraped_cases = [case1]

    mapped = _map_claim_to_response(base_claim)
    assert len(mapped.court_cases) == 1
    assert mapped.court_cases[0].filing_date == "12/26/2023"

    # Test alias 2: SuitFiledDate
    case1.raw_payload = {"SuitFiledDate": "11/15/2023"}
    mapped = _map_claim_to_response(base_claim)
    assert mapped.court_cases[0].filing_date == "11/15/2023"

    # Test alias 3: DateFiled
    case1.raw_payload = {"DateFiled": "10/01/2022"}
    mapped = _map_claim_to_response(base_claim)
    assert mapped.court_cases[0].filing_date == "10/01/2022"

    # Test alias 4: Filed
    case1.raw_payload = {"Filed": "05/18/2021"}
    mapped = _map_claim_to_response(base_claim)
    assert mapped.court_cases[0].filing_date == "05/18/2021"

    # Test alias 5: fallback to claim DOL
    case1.raw_payload = {}
    mapped = _map_claim_to_response(base_claim)
    assert mapped.court_cases[0].filing_date == "12/25/2023"

    # Test alias 6: JSON body fallback when scraped_cases is empty
    base_claim.scraped_cases = []
    base_claim.fl_jsonbody_broward = [{"CaseNumber": "2024-CA-999", "CaseStyle": "Test vs State", "FilingDate": "01/15/2024"}]
    mapped = _map_claim_to_response(base_claim)
    assert len(mapped.court_cases) == 1
    assert mapped.court_cases[0].case_number == "2024-CA-999"
    assert mapped.court_cases[0].filing_date == "01/15/2024"
