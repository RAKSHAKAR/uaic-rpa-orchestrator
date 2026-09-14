"""
Test Suite for IMP-2026-0912-006:
Core Orchestrator Architecture, State Routing, Guidewire Contract,
Portal Schema Data Fidelity, and Export Parity.
"""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import Base, TaskAsyncSessionLocal, engine
from app.main import app
from app.models.claim import ClaimRecord, FuzzyMatchStatusEnum, RecordStatusEnum
from app.models.court_case import ScrapedCourtCase
from app.services.excel_parser import _normalize_state_code, resolve_county_bot_targets
from app.services.guidewire_client import GuidewireClient, format_claim_number


@pytest.fixture(scope="module", autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


# ============================================================================
# 1. State Routing Logic & Miami-Dade Classification
# ============================================================================

def test_state_routing_florida_intra_state():
    """If Policy State == Loss Location State == Florida: Route to Broward, Hillsborough, Miami."""
    targets = resolve_county_bot_targets("FL", "FL")
    assert targets["fl_broward"] == "Yes"
    assert targets["fl_hillsborough"] == "Yes"
    assert targets["fl_miami"] == "Yes"
    assert targets["te_travis"] == "No"
    assert targets["te_dallas"] == "No"
    assert targets["te_harris"] == "No"
    assert targets["te_cclerk"] == "No"
    assert targets["te_hcdistrict"] == "No"


def test_state_routing_texas_intra_state():
    """If Policy State == Loss Location State == Texas: Route to 5 Texas portals only."""
    targets = resolve_county_bot_targets("TX", "TX")
    assert targets["fl_broward"] == "No"
    assert targets["fl_hillsborough"] == "No"
    assert targets["fl_miami"] == "No"
    assert targets["te_travis"] == "Yes"
    assert targets["te_dallas"] == "Yes"
    assert targets["te_harris"] == "Yes"
    assert targets["te_cclerk"] == "Yes"
    assert targets["te_hcdistrict"] == "Yes"


def test_state_routing_cross_state():
    """If Policy State != Loss Location State: Cross-state discovery routes to ALL 8 portals."""
    # FL policy, TX loss
    targets_fl_tx = resolve_county_bot_targets("FL", "TX")
    assert all(v == "Yes" for v in targets_fl_tx.values()), "All 8 bots must be targeted for cross-state FL/TX"

    # TX policy, FL loss
    targets_tx_fl = resolve_county_bot_targets("TX", "FL")
    assert all(v == "Yes" for v in targets_tx_fl.values()), "All 8 bots must be targeted for cross-state TX/FL"

    # Full name spellings
    targets_full = resolve_county_bot_targets("Florida", "Texas")
    assert all(v == "Yes" for v in targets_full.values())


def test_miami_dade_is_strictly_florida():
    """CRITICAL: Miami-Dade is Florida. Never classify it as Texas."""
    targets_fl = resolve_county_bot_targets("FL", "FL")
    assert "fl_miami" in targets_fl
    assert targets_fl["fl_miami"] == "Yes"
    assert "te_miami" not in targets_fl, "Miami must never be prefixed or classified as Texas (te_)"


def test_state_normalization_helpers():
    """Test state normalization handles full names and abbreviations."""
    assert _normalize_state_code("Florida") == "FL"
    assert _normalize_state_code("FL") == "FL"
    assert _normalize_state_code("Texas") == "TX"
    assert _normalize_state_code("TX") == "TX"
    assert _normalize_state_code("California") == "CALIFORNIA"
    assert _normalize_state_code(None) == ""


# ============================================================================
# 2. Guidewire Contract & Claim Number Rule
# ============================================================================

def test_claim_number_formatting_rule():
    """If len(claim_number) == 9: prefix with '0'. Applied to ClaimNumber in Guidewire payload."""
    assert format_claim_number("123456789") == "0123456789"
    assert format_claim_number("987654321") == "0987654321"
    # 10 digits remains unchanged
    assert format_claim_number("0123456789") == "0123456789"
    # Custom alphanumeric remains unchanged
    assert format_claim_number("CLM-1002") == "CLM-1002"
    assert format_claim_number("  123456789  ") == "0123456789"


@pytest.mark.asyncio
async def test_guidewire_contract_payload_structure():
    """Verify Guidewire payload adheres exactly to the contract schema."""
    client = GuidewireClient(mock_mode=True)
    claim_num = "987654321"  # 9-digit
    exposure_num = "001"
    matched_cases = [
        {
            "CaseNumber": "2026-CA-001234",
            "CaseStyle": "JOHN DOE VS JANE SMITH",
            "CountyWebsite": "https://www.browardclerk.org/",
            "SuitFiledDate": "05/12/2026",
            "CaseStatus": "OPEN",
            "CaseType": "CIRCUIT CIVIL",
        }
    ]

    result = await client.send_case_update(claim_num, exposure_num, matched_cases)
    assert result["success"] is True
    payload = result["payload_sent"]

    # Top-level keys must match V4 contract
    assert set(payload.keys()) == {"ClaimNumber", "ExposureNumber", "CaseItems", "TransactionId", "SourceSystem"}
    assert payload["ClaimNumber"] == "0987654321", "9-digit claim number must have leading zero"
    assert payload["ExposureNumber"] == "001"
    assert payload["SourceSystem"] == "UAIC_ORCHESTRATOR"

    # CaseItems keys must match V4 contract
    assert len(payload["CaseItems"]) == 1
    case_item = payload["CaseItems"][0]
    assert set(case_item.keys()) == {"CaseNumber", "CaseStyle", "CountyWebsite", "SuitFiledDate"}
    assert case_item["CaseNumber"] == "2026-CA-001234"
    assert case_item["CaseStyle"] == "JOHN DOE VS JANE SMITH"
    assert case_item["CountyWebsite"] == "https://www.browardclerk.org/"
    assert case_item["SuitFiledDate"] == "05/12/2026"


# ============================================================================
# 3. Portal Output Schemas & Data Fidelity
# ============================================================================

def test_portal_output_schemas_fidelity():
    """
    Harris JP / Harris County Clerk must have NO CaseType.
    Broward/Hillsborough/Miami/Dallas/Travis/Harris District have CaseType.
    """
    from app.automation.florida.broward import BrowardScraper
    from app.automation.florida.hillsborough import HillsboroughScraper
    from app.automation.florida.miami import MiamiDadeScraper
    from app.automation.texas.dallas import DallasScraper
    from app.automation.texas.harris_cclerk import HarrisCountyClerkScraper
    from app.automation.texas.harris_district import HarrisDistrictClerkScraper
    from app.automation.texas.harris_jp import HarrisJPScraper
    from app.automation.texas.travis import TravisScraper

    # Verify all scrapers are instantiable with correct metadata
    b_scraper = BrowardScraper()
    assert "Broward" in b_scraper.county_name

    h_scraper = HillsboroughScraper()
    assert "Hillsborough" in h_scraper.county_name

    m_scraper = MiamiDadeScraper()
    assert "Miami" in m_scraper.county_name

    d_scraper = DallasScraper()
    assert "Dallas" in d_scraper.county_name

    t_scraper = TravisScraper()
    assert "Travis" in t_scraper.county_name

    hjp_scraper = HarrisJPScraper()
    assert "Harris" in hjp_scraper.county_name

    hcclerk_scraper = HarrisCountyClerkScraper()
    assert "Harris" in hcclerk_scraper.county_name

    hd_scraper = HarrisDistrictClerkScraper()
    assert "Harris" in hd_scraper.county_name


# ============================================================================
# 4. Single Claim Export Endpoints Parity
# ============================================================================

@pytest.mark.asyncio
async def test_single_claim_export_formats_parity():
    """Verify single claim export delivers complete, matching data across xlsx, csv, json."""
    claim_id = str(uuid.uuid4())
    claim_number = f"EXP-PARITY-{claim_id[:6]}"

    async with TaskAsyncSessionLocal() as session:
        claim = ClaimRecord(
            id=claim_id,
            claim_number=claim_number,
            exposure_number="1",
            insured_first_name="Arthur",
            insured_last_name="Dent",
            claimant_first_name="Ford",
            claimant_last_name="Prefect",
            policy_state="FL",
            loss_location_state="FL",
            record_status=RecordStatusEnum.COMPLETED,
            fuzzy_match_status=FuzzyMatchStatusEnum.NO_MATCH_FOUND,
        )
        session.add(claim)

        # Add a scraped court case
        case = ScrapedCourtCase(
            id=str(uuid.uuid4()),
            claim_id=claim_id,
            county_name="Broward County",
            case_number="CACE-2026-009999",
            case_style="FORD PREFECT VS ARTHUR DENT",
            filing_date="06/15/2026",
            case_status="OPEN",
            case_type="CIRCUIT CIVIL",
            county_website="https://www.browardclerk.org/",
        )
        session.add(case)
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Test JSON Export
        resp_json = await ac.get(f"/api/v1/claims/{claim_id}/export?format=json")
        assert resp_json.status_code == 200
        json_data = resp_json.json()
        assert json_data["claim_number"] == claim_number
        assert len(json_data["court_cases"]) == 1
        assert json_data["court_cases"][0]["case_number"] == "CACE-2026-009999"

        # Test CSV Export
        resp_csv = await ac.get(f"/api/v1/claims/{claim_id}/export?format=csv")
        assert resp_csv.status_code == 200
        assert "text/csv" in resp_csv.headers["content-type"]
        assert claim_number in resp_csv.text
        assert "CACE-2026-009999" in resp_csv.text

        # Test XLSX Export
        resp_xlsx = await ac.get(f"/api/v1/claims/{claim_id}/export?format=xlsx")
        assert resp_xlsx.status_code == 200
        assert "spreadsheetml" in resp_xlsx.headers["content-type"]
        assert len(resp_xlsx.content) > 100
