"""
Tests for IMP-2026-0911-002 (Prompt 03):
- State routing notation normalization (FL/Florida and TX/Texas cross-notations)
- Miami-Dade classification under Florida
- Match exceptions export endpoints (xlsx, csv, json)
- Expanded filing date fallback keys in ScrapedCaseResponse
"""

import json
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import AsyncSessionLocal, Base, engine
from app.main import app
from app.models.claim import ClaimRecord
from app.models.court_case import ScrapedCourtCase
from app.models.match_result import MatchPair, MatchReviewStatusEnum, PartyTypeEnum
from app.services.excel_parser import resolve_county_bot_targets


@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    """Ensure schema exists for all tests in this module."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def test_state_routing_normalization_florida():
    """Verify that FL/Florida variations normalize to Florida 3 bots and exclude Texas."""
    test_pairs = [
        ("FL", "Florida"),
        ("Florida", "FL"),
        ("FLORIDA", "florida"),
        ("fl", "FL"),
        ("Fl", "Florida"),
    ]
    for p_st, l_st in test_pairs:
        targets = resolve_county_bot_targets(p_st, l_st)
        # Florida bots must be 'Yes'
        assert targets["fl_broward"] == "Yes", f"Failed for {p_st}, {l_st}"
        assert targets["fl_hillsborough"] == "Yes", f"Failed for {p_st}, {l_st}"
        assert targets["fl_miami"] == "Yes", f"Failed for {p_st}, {l_st}"

        # Texas bots must be 'No'
        assert targets["te_travis"] == "No", f"Failed for {p_st}, {l_st}"
        assert targets["te_dallas"] == "No", f"Failed for {p_st}, {l_st}"
        assert targets["te_harris"] == "No", f"Failed for {p_st}, {l_st}"
        assert targets["te_cclerk"] == "No", f"Failed for {p_st}, {l_st}"
        assert targets["te_hcdistrict"] == "No", f"Failed for {p_st}, {l_st}"


def test_state_routing_normalization_texas():
    """Verify that TX/Texas variations normalize to Texas 5 bots and exclude Florida."""
    test_pairs = [
        ("TX", "Texas"),
        ("Texas", "TX"),
        ("TEXAS", "texas"),
        ("tx", "TX"),
        ("Tx", "Texas"),
    ]
    for p_st, l_st in test_pairs:
        targets = resolve_county_bot_targets(p_st, l_st)
        # Texas bots must be 'Yes'
        assert targets["te_travis"] == "Yes", f"Failed for {p_st}, {l_st}"
        assert targets["te_dallas"] == "Yes", f"Failed for {p_st}, {l_st}"
        assert targets["te_harris"] == "Yes", f"Failed for {p_st}, {l_st}"
        assert targets["te_cclerk"] == "Yes", f"Failed for {p_st}, {l_st}"
        assert targets["te_hcdistrict"] == "Yes", f"Failed for {p_st}, {l_st}"

        # Florida bots must be 'No' (including Miami-Dade)
        assert targets["fl_broward"] == "No", f"Failed for {p_st}, {l_st}"
        assert targets["fl_hillsborough"] == "No", f"Failed for {p_st}, {l_st}"
        assert targets["fl_miami"] == "No", f"Failed for {p_st}, {l_st}"


def test_state_routing_cross_state():
    """Verify that cross-state claims route to all 8 county portals."""
    test_pairs = [
        ("FL", "TX"),
        ("Texas", "Florida"),
        ("Florida", "GA"),
        ("NY", "TX"),
    ]
    for p_st, l_st in test_pairs:
        targets = resolve_county_bot_targets(p_st, l_st)
        assert all(val == "Yes" for val in targets.values()), f"Failed for {p_st}, {l_st}"


@pytest.mark.asyncio
async def test_match_exceptions_export_xlsx():
    """Verify GET /api/v1/matches/export?format=xlsx generates valid Excel binary."""
    claim_id = str(uuid.uuid4())
    case_id = str(uuid.uuid4())
    match_id = str(uuid.uuid4())

    async with AsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number="TEST_MATCH_EXP_001",
            exposure_number="001",
            policy_state="FL",
            loss_location_state="FL",
        )
        session.add(claim)

        case = ScrapedCourtCase(
            id=case_id,
            claim_id=claim_id,
            county_name="Broward County",
            county_website="https://www.browardclerk.org",
            case_number="CACE-2023-999",
            case_style="State Farm vs John Doe",
            filing_date="06/15/2023",
            case_status="OPEN",
            case_type="CIVIL",
        )
        session.add(case)

        mp = MatchPair(
            id=match_id,
            claim_id=claim_id,
            court_case_id=case_id,
            party_type=PartyTypeEnum.INSURED,
            party_name="John Doe",
            case_style="State Farm vs John Doe",
            similarity_score=0.75,
            threshold_applied=0.60,
            review_status=MatchReviewStatusEnum.PENDING_REVIEW,
        )
        session.add(mp)
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/matches/export?format=xlsx")
        assert response.status_code == 200
        assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers.get("content-type", "")
        assert "attachment; filename=exceptions_export_" in response.headers.get("content-disposition", "")
        assert response.content.startswith(b"PK"), "Excel output must start with ZIP magic bytes PK"


@pytest.mark.asyncio
async def test_match_exceptions_export_csv():
    """Verify GET /api/v1/matches/export?format=csv returns proper CSV headers and data."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/matches/export?format=csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        text = response.text
        assert "Match ID" in text
        assert "Claim Number" in text
        assert "Party Name" in text
        assert "Similarity Score (%)" in text
        assert "Court Case Number" in text


@pytest.mark.asyncio
async def test_match_exceptions_export_json():
    """Verify GET /api/v1/matches/export?format=json returns valid JSON array."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/matches/export?format=json")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")
        data = json.loads(response.text)
        assert isinstance(data, list)
        if len(data) > 0:
            item = data[0]
            assert "Match ID" in item
            assert "Similarity Score (%)" in item


@pytest.mark.asyncio
async def test_scraped_case_expanded_date_filed_fallback():
    """Verify that ScrapedCaseResponse recognizes DateFiled in raw_payload."""
    claim_id = str(uuid.uuid4())
    async with AsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number="TEST_DATEFILED_001",
            exposure_number="001",
            policy_state="FL",
            loss_location_state="FL",
        )
        session.add(claim)

        case = ScrapedCourtCase(
            claim_id=claim_id,
            county_name="Hillsborough County",
            county_website="https://hover.hillsclerk.com",
            case_number="23-CA-008888",
            case_style="Jane Roe vs Acme",
            filing_date=None,  # explicitly null in DB column
            case_status="PENDING",
            case_type="CIRCUIT CIVIL",
            raw_payload={"DateFiled": "08/21/2023", "OtherField": "Value"},
        )
        session.add(case)
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/claims/{claim_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["court_cases"]) == 1
        assert data["court_cases"][0]["filing_date"] == "08/21/2023"
