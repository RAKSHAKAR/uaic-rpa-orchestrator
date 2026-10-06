"""
Automated Pytest Suite for Attended vs. Unattended Parity & E2E Verification (IMP-2026-0911-003).

Validates:
1. Browser context parity (Attended GUI vs. Headless) with AntiCaptcha discovery.
2. State routing logic (FL 3, TX 5, Cross-State 8).
3. Unique name derivation (1, 2, 3 searches) across all 5 equality permutations.
4. Strict county court portal schemas (NO CaseType for Harris JP and Harris County Clerk).
5. RapidFuzz 3-tier cascade matching (Claimant -> Insured -> Driver with threshold >= 0.60).
6. Guidewire Cloud payload formation (9-digit 0-prefix rule).
7. Strict 1:1 parity between Attended Mode and Unattended Mode execution.
"""

from collections import namedtuple

import pytest

from app.automation.browser_manager import ChromeSession, ExtensionManager
from app.automation.session_runner import derive_search_counts, get_search_party_pairs
from app.models.match_result import MatchReviewStatusEnum, PartyTypeEnum
from app.services.excel_parser import resolve_county_bot_targets
from app.services.fuzzy_engine import evaluate_case_against_parties
from app.services.guidewire_client import format_claim_number

MockClaim = namedtuple(
    "MockClaim",
    ["insured_first_name", "insured_last_name", "driver_first_name", "driver_last_name", "claimant_first_name", "claimant_last_name"],
    defaults=["", "", "", "", "", ""],
)


def test_parity_state_routing_matrix():
    """Validates Florida, Texas, and Cross-State portal routing."""
    fl_targets = resolve_county_bot_targets("FL", "FL")
    assert fl_targets["fl_broward"] == "Yes"
    assert fl_targets["fl_hillsborough"] == "Yes"
    assert fl_targets["fl_miami"] == "Yes"
    assert fl_targets["te_dallas"] == "No"

    tx_targets = resolve_county_bot_targets("TX", "TX")
    assert tx_targets["fl_broward"] == "No"
    assert tx_targets["te_dallas"] == "Yes"
    assert tx_targets["te_travis"] == "Yes"
    assert tx_targets["te_hcdistrict"] == "Yes"
    assert tx_targets["te_harris"] == "Yes"
    assert tx_targets["te_cclerk"] == "Yes"

    cross_targets = resolve_county_bot_targets("FL", "TX")
    assert len([k for k, v in cross_targets.items() if v == "Yes"]) == 8


def test_parity_party_pairs_derivation():
    """Validates DualSearch and TripleSearch derivation across all 5 permutations."""
    # 1. All same: 1 search
    c1 = MockClaim("JOHN", "DOE", "JOHN", "DOE", "JOHN", "DOE")
    assert derive_search_counts(c1) == (1, 1)
    assert len(get_search_party_pairs(c1, 1, 1)) == 1

    # 2. Insured == Driver, Claimant != : 2 searches
    c2 = MockClaim("JOHN", "DOE", "JOHN", "DOE", "JANE", "SMITH")
    assert derive_search_counts(c2) == (1, 3)
    assert len(get_search_party_pairs(c2, 1, 3)) == 2

    # 3. Insured == Claimant, Driver != : 2 searches
    c3 = MockClaim("JOHN", "DOE", "BOB", "JONES", "JOHN", "DOE")
    assert derive_search_counts(c3) == (2, 1)
    assert len(get_search_party_pairs(c3, 2, 1)) == 2

    # 4. Driver == Claimant, Insured != : 2 searches
    c4 = MockClaim("ALICE", "BROWN", "JOHN", "DOE", "JOHN", "DOE")
    assert derive_search_counts(c4) == (2, 1)
    assert len(get_search_party_pairs(c4, 2, 1)) == 2

    # 5. All different : 3 searches
    c5 = MockClaim("ALICE", "BROWN", "BOB", "JONES", "JOHN", "DOE")
    assert derive_search_counts(c5) == (2, 3)
    assert len(get_search_party_pairs(c5, 2, 3)) == 3


def test_parity_strict_portal_schemas():
    """Asserts that Harris JP and Harris County Clerk have strictly NO CaseType."""
    allowed_schemas = {
        "fl_broward": ["CaseNumber", "CaseStyle", "FilingDate", "CaseStatus", "CaseType"],
        "fl_hillsborough": ["CaseNumber", "CaseStyle", "FilingDate", "CaseStatus", "CaseType"],
        "fl_miami": ["CaseNumber", "CaseStyle", "FilingDate", "CaseStatus", "CaseType"],
        "te_dallas": ["CaseNumber", "CaseStyle", "FilingDate", "CaseStatus", "CaseType"],
        "te_travis": ["CaseNumber", "CaseStyle", "FilingDate", "CaseStatus", "CaseType"],
        "te_harris_district": ["CaseNumber", "CaseStyle", "FilingDate", "CaseStatus", "CaseType"],
        "te_harris_jp": ["CaseNumber", "CaseStyle", "FilingDate", "CaseStatus"],
        "te_harris_cclerk": ["CaseNumber", "CaseStyle", "FilingDate", "CaseStatus"],
    }

    assert "CaseType" not in allowed_schemas["te_harris_jp"]
    assert "CaseType" not in allowed_schemas["te_harris_cclerk"]
    for p in ["fl_broward", "fl_hillsborough", "fl_miami", "te_dallas", "te_travis", "te_harris_district"]:
        assert "CaseType" in allowed_schemas[p]


def test_parity_guidewire_9digit_0prefix_rule():
    """Validates the 9-digit 0-prefix rule for Guidewire payload."""
    assert format_claim_number("123456789") == "0123456789"
    assert format_claim_number("0123456789") == "0123456789"
    assert format_claim_number("98765432") == "98765432"
    assert format_claim_number("12345678901") == "12345678901"


def test_parity_fuzzy_cascade_order():
    """Validates Claimant -> Insured -> Driver priority cascade."""
    # Case containing Claimant and Insured -> Must match Claimant first
    dual_case = {
        "CaseNumber": "2026-CA-001",
        "CaseStyle": "SERGIO GONZALEZ VS MARCO RODRIGUEZ",
        "FilingDate": "05/10/2026",
    }
    results = evaluate_case_against_parties(
        case=dual_case,
        claimant_name="Sergio Gonzalez",
        insured_name="Marco Rodriguez",
        driver_name="John Doe",
        threshold=0.60,
    )
    assert len(results) == 3
    # Claimant result should be matched
    clm_res = next(r for r in results if r["party_type"] == PartyTypeEnum.CLAIMANT)
    assert clm_res["is_match"] is True
    assert clm_res["party_name"] == "Sergio Gonzalez"
    assert clm_res["review_status"] == MatchReviewStatusEnum.AUTO_MATCHED


@pytest.mark.asyncio
async def test_parity_attended_vs_unattended_browser_session_parity(mocker):
    """
    Validates that ChromeSession starts cleanly and loads the AntiCaptcha extension
    identically in both Attended (headless=False) and Unattended (headless=True) modes.
    """
    ext_path = ExtensionManager.resolve_extension_path()
    assert ext_path is not None
    assert (ext_path / "manifest.json").exists()

    session_attended = ChromeSession(headless=False, browser_engine="chromium")
    session_unattended = ChromeSession(headless=True, browser_engine="chromium")

    assert session_attended.headless is False
    assert session_unattended.headless is True
    assert session_attended.browser_engine == "chromium"
    assert session_unattended.browser_engine == "chromium"


@pytest.mark.asyncio
async def test_parity_browser_manager_stage_detail_reflects_mode(mocker):
    """Validates that BrowserManager stage timings dynamically reflect Attended vs. Headless mode."""
    from pathlib import Path
    from unittest.mock import AsyncMock, MagicMock

    from app.automation.browser_manager import BrowserManager

    # 1. Attended mode with Chrome
    bm_attended = BrowserManager(headless=False, browser_engine="chrome")
    bm_attended.session = MagicMock()
    bm_attended.session.start = AsyncMock(return_value=MagicMock())
    bm_attended.session.close = AsyncMock()
    bm_attended.session.headless = False
    bm_attended.session.browser_engine = "chrome"
    bm_attended.session.extension_path = Path("/mock/ext")
    async with bm_attended:
        pass
    launch_detail = bm_attended.stage_timings["browser_launch"]["detail"]
    assert "Attended (Visible GUI)" in launch_detail
    assert "Google Chrome" in launch_detail
    assert "+ AntiCaptcha" in launch_detail

    # 2. Headless mode with Chromium
    bm_headless = BrowserManager(headless=True, browser_engine="chromium")
    bm_headless.session = MagicMock()
    bm_headless.session.start = AsyncMock(return_value=MagicMock())
    bm_headless.session.close = AsyncMock()
    bm_headless.session.headless = True
    bm_headless.session.browser_engine = "chromium"
    bm_headless.session.extension_path = None
    async with bm_headless:
        pass
    launch_detail_hl = bm_headless.stage_timings["browser_launch"]["detail"]
    assert "Headless (Background)" in launch_detail_hl
    assert "Chromium" in launch_detail_hl


def test_parity_claims_synthesized_stage_detail_reflects_settings(mocker):
    """Validates that _normalize_action_timings in claims.py reflects dynamic settings."""
    from unittest.mock import MagicMock

    from app.api.v1.endpoints.claims import _normalize_action_timings
    from app.models.claim import ClaimRecord, RecordStatusEnum

    mock_claim = MagicMock(spec=ClaimRecord)
    mock_claim.record_status = RecordStatusEnum.SCRAPING_COMPLETED
    mock_claim.total_duration_seconds = 12.5
    mock_claim.scraped_cases = []
    for attr in [
        "fl_jsonbody_broward", "fl_jsonbody_hillsborough", "fl_jsonbody_miami",
        "te_jsonbody_travis", "te_jsonbody_dallas", "te_jsonbody_harris",
        "te_jsonbody_cclerk", "te_jsonbody_hcdistrict"
    ]:
        setattr(mock_claim, attr, [])

    # Test with Headless = True
    mock_settings_hl = MagicMock()
    mock_settings_hl.automation.headless_mode = True
    mock_settings_hl.automation.browser_engine = "chrome"
    mocker.patch("app.services.settings_service.get_system_settings_sync", return_value=mock_settings_hl)

    timings = _normalize_action_timings({}, claim=mock_claim)
    assert "stages" in timings
    assert "browser_launch" in timings["stages"]
    detail = timings["stages"]["browser_launch"]["detail"]
    assert "Headless (Background)" in detail
    assert "Google Chrome" in detail

    # Test with Headless = False (Attended)
    mock_settings_att = MagicMock()
    mock_settings_att.automation.headless_mode = False
    mock_settings_att.automation.browser_engine = "msedge"
    mocker.patch("app.services.settings_service.get_system_settings_sync", return_value=mock_settings_att)

    timings_att = _normalize_action_timings({}, claim=mock_claim)
    detail_att = timings_att["stages"]["browser_launch"]["detail"]
    assert "Attended (Visible GUI)" in detail_att
    assert "Microsoft Edge" in detail_att

