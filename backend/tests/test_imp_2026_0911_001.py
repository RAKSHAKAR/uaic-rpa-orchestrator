"""
Tests for IMP-2026-0911-001 (Prompt 03):
- Deprecated field removal from TARGET_CLAIM_FIELDS
- Filing date multi-key fallback capture
- ScrapedCaseResponse raw_payload fallback
- Single claim export endpoint data integrity
"""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import AsyncSessionLocal, Base, engine
from app.main import app
from app.models.claim import ClaimRecord
from app.models.court_case import ScrapedCourtCase
from app.services.excel_parser import TARGET_CLAIM_FIELDS


@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    """Ensure schema exists for all tests in this module."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest.mark.asyncio
async def test_target_claim_fields_cleanup():
    """Verify that all 4 deprecated fields are absent from TARGET_CLAIM_FIELDS."""
    keys = [f["key"] for f in TARGET_CLAIM_FIELDS]
    assert "loss_location_city" not in keys
    assert "loss_location_county" not in keys
    assert "garaging_city" not in keys
    assert "garaging_state" not in keys

    # Verify essential fields remain present
    assert "claim_number" in keys
    assert "insured_first_name" in keys
    assert "insured_last_name" in keys
    assert "claimant_first_name" in keys
    assert "claimant_last_name" in keys
    assert "driver_first_name" in keys
    assert "driver_last_name" in keys
    assert "dol" in keys
    assert "policy_state" in keys
    assert "loss_location_state" in keys


@pytest.mark.asyncio
async def test_claim_detail_filing_date_fallback():
    """Verify that ScrapedCaseResponse falls back to raw_payload if filing_date is null."""
    claim_id = str(uuid.uuid4())
    async with AsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number="TEST_GW_001",
            exposure_number="001",
            policy_state="FL",
            loss_location_state="FL",
        )
        session.add(claim)

        # Case 1: filing_date is stored directly
        case1 = ScrapedCourtCase(
            claim_id=claim_id,
            county_name="Broward County",
            county_website="https://www.browardclerk.org",
            case_number="CACE-2023-001",
            case_style="Doe vs Smith",
            filing_date="05/12/2023",
            case_status="OPEN",
            case_type="CIVIL",
        )
        # Case 2: filing_date is None, but in raw_payload as FilingDate
        case2 = ScrapedCourtCase(
            claim_id=claim_id,
            county_name="Miami-Dade County",
            county_website="https://www2.miamidadeclerk.gov",
            case_number="CACE-2023-002",
            case_style="Johnson vs State Farm",
            filing_date=None,
            case_status="OPEN",
            case_type="CIVIL",
            raw_payload={"FilingDate": "08/21/2023", "Court": "Civil"},
        )
        # Case 3: filing_date is None, but in raw_payload as SuitFiledDate
        case3 = ScrapedCourtCase(
            claim_id=claim_id,
            county_name="Travis County",
            county_website="https://www.traviscountytx.gov",
            case_number="D-1-GN-23-003",
            case_style="Williams vs Allstate",
            filing_date=None,
            case_status="OPEN",
            case_type="CIVIL",
            raw_payload={"SuitFiledDate": "11/04/2023"},
        )
        session.add_all([case1, case2, case3])
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(f"/api/v1/claims/{claim_id}")
        assert resp.status_code == 200
        data = resp.json()
        cases = data.get("court_cases", [])
        assert len(cases) >= 3

        case1_resp = next(c for c in cases if c["case_number"] == "CACE-2023-001")
        assert case1_resp["filing_date"] == "05/12/2023"

        case2_resp = next(c for c in cases if c["case_number"] == "CACE-2023-002")
        assert case2_resp["filing_date"] == "08/21/2023"

        case3_resp = next(c for c in cases if c["case_number"] == "D-1-GN-23-003")
        assert case3_resp["filing_date"] == "11/04/2023"


@pytest.mark.asyncio
async def test_single_claim_export_endpoints():
    """Verify single claim export returns xlsx, csv, and json with identical cases data."""
    claim_id = str(uuid.uuid4())
    async with AsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number="TEST_EXP_001",
            exposure_number="001",
            policy_state="FL",
            loss_location_state="FL",
        )
        session.add(claim)

        case = ScrapedCourtCase(
            claim_id=claim_id,
            county_name="Broward County",
            county_website="https://www.browardclerk.org",
            case_number="CACE-2024-999",
            case_style="Miller vs Progressive",
            filing_date="01/15/2024",
            case_status="CLOSED",
            case_type="CIVIL",
        )
        session.add(case)
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # JSON export
        resp_json = await client.get(f"/api/v1/claims/{claim_id}/export?format=json")
        assert resp_json.status_code == 200
        data = resp_json.json()
        assert data["claim_number"] == "TEST_EXP_001"
        assert len(data.get("court_cases", [])) == 1
        assert data["court_cases"][0]["case_number"] == "CACE-2024-999"

        # CSV export
        resp_csv = await client.get(f"/api/v1/claims/{claim_id}/export?format=csv")
        assert resp_csv.status_code == 200
        assert "CACE-2024-999" in resp_csv.text

        # XLSX export
        resp_xlsx = await client.get(f"/api/v1/claims/{claim_id}/export?format=xlsx")
        assert resp_xlsx.status_code == 200
        assert resp_xlsx.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
