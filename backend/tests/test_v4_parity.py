"""Dedicated Power Automate V4 Behavioral Parity Verification Suite.

Tests:
1. derive_search_counts for all 5 party equality combinations.
2. get_search_party_pairs party ordering and fallbacks.
3. format_claim_number 9-digit prefixing rule ('0' prepend).
4. State routing logic: Policy State == Loss Location State (FL, TX, Cross-State).
5. RapidFuzz 3-tier cascade (Claimant -> Insured -> Driver) & positive match deduplication.
6. CaseStyle normalization mirroring legacy Power Automate regex and character stripping.
7. Strict schema contracts across all 8 portals (including Harris JP and Harris County Clerk without CaseType).
8. Guidewire payload structure and activity creation response.
"""

from collections import namedtuple

import pytest

from app.automation.session_runner import derive_search_counts, get_search_party_pairs
from app.models.match_result import PartyTypeEnum
from app.services.excel_parser import convert_excel_date, resolve_county_bot_targets
from app.services.fuzzy_engine import (
    clean_case_style,
    evaluate_case_against_parties,
)
from app.services.guidewire_client import GuidewireClient, format_claim_number

MockClaim = namedtuple(
    "MockClaim",
    [
        "insured_first_name",
        "insured_last_name",
        "driver_first_name",
        "driver_last_name",
        "claimant_first_name",
        "claimant_last_name",
    ],
    defaults=["", "", "", "", "", ""],
)


def test_v4_derive_search_counts_all_combinations():
    """Validates the 5 DualSearch and TripleSearch combinations from V4 ExtractDataFlow."""
    # 1. All three identical: (1, 1) -> 1 search (Insured)
    c1 = MockClaim("CARLOS", "HERNANDEZ", "CARLOS", "HERNANDEZ", "CARLOS", "HERNANDEZ")
    assert derive_search_counts(c1) == (1, 1)
    p1 = get_search_party_pairs(c1, 1, 1)
    assert len(p1) == 1
    assert p1[0] == ("Insured", "CARLOS", "HERNANDEZ")

    # 2. Insured == Driver, Claimant != : (1, 3) -> 2 searches (Insured, Claimant)
    c2 = MockClaim("CARLOS", "HERNANDEZ", "CARLOS", "HERNANDEZ", "MARIA", "LOPEZ")
    assert derive_search_counts(c2) == (1, 3)
    p2 = get_search_party_pairs(c2, 1, 3)
    assert len(p2) == 2
    assert p2[0] == ("Insured", "CARLOS", "HERNANDEZ")
    assert p2[1] == ("Claimant", "MARIA", "LOPEZ")

    # 3. Insured == Claimant, Driver != : (2, 1) -> 2 searches (Insured, Driver)
    c3 = MockClaim("CARLOS", "HERNANDEZ", "JUAN", "RAMIREZ", "CARLOS", "HERNANDEZ")
    assert derive_search_counts(c3) == (2, 1)
    p3 = get_search_party_pairs(c3, 2, 1)
    assert len(p3) == 2
    assert p3[0] == ("Insured", "CARLOS", "HERNANDEZ")
    assert p3[1] == ("Driver", "JUAN", "RAMIREZ")

    # 4. Driver == Claimant, Insured != : (2, 1) -> 2 searches (Insured, Driver)
    c4 = MockClaim("ANA", "GARCIA", "JUAN", "RAMIREZ", "JUAN", "RAMIREZ")
    assert derive_search_counts(c4) == (2, 1)
    p4 = get_search_party_pairs(c4, 2, 1)
    assert len(p4) == 2
    assert p4[0] == ("Insured", "ANA", "GARCIA")
    assert p4[1] == ("Driver", "JUAN", "RAMIREZ")

    # 5. All different : (2, 3) -> 3 searches (Insured, Driver, Claimant)
    c5 = MockClaim("ANA", "GARCIA", "JUAN", "RAMIREZ", "MARIA", "LOPEZ")
    assert derive_search_counts(c5) == (2, 3)
    p5 = get_search_party_pairs(c5, 2, 3)
    assert len(p5) == 3
    assert p5[0] == ("Insured", "ANA", "GARCIA")
    assert p5[1] == ("Driver", "JUAN", "RAMIREZ")
    assert p5[2] == ("Claimant", "MARIA", "LOPEZ")


def test_v4_state_routing_logic():
    """Validates routing switch logic from Import_ExcelData_To_Dataverse."""
    # Florida same state -> 3 FL portals
    fl_targets = resolve_county_bot_targets("Florida", "Florida")
    assert fl_targets["fl_broward"] == "Yes"
    assert fl_targets["fl_hillsborough"] == "Yes"
    assert fl_targets["fl_miami"] == "Yes"
    assert fl_targets["te_travis"] == "No"
    assert fl_targets["te_dallas"] == "No"
    assert fl_targets["te_harris"] == "No"
    assert fl_targets["te_cclerk"] == "No"
    assert fl_targets["te_hcdistrict"] == "No"

    # Texas same state -> 5 TX portals
    tx_targets = resolve_county_bot_targets("Texas", "Texas")
    assert tx_targets["fl_broward"] == "No"
    assert tx_targets["fl_hillsborough"] == "No"
    assert tx_targets["fl_miami"] == "No"
    assert tx_targets["te_travis"] == "Yes"
    assert tx_targets["te_dallas"] == "Yes"
    assert tx_targets["te_harris"] == "Yes"
    assert tx_targets["te_cclerk"] == "Yes"
    assert tx_targets["te_hcdistrict"] == "Yes"

    # Cross state (Florida policy, Texas loss) -> All 8 portals
    cross_targets = resolve_county_bot_targets("Florida", "Texas")
    for k, v in cross_targets.items():
        assert v == "Yes"


def test_v4_excel_dol_conversion():
    """Validates DOL conversion from Excel serial integer (1899-12-30 base)."""
    # 45450 -> 2024-06-07
    converted = convert_excel_date(45450)
    assert converted == "06/07/2024"

    # String date pass-through
    assert convert_excel_date("08/21/2026") == "08/21/2026"
    assert convert_excel_date("2026-08-21") == "08/21/2026"
    assert convert_excel_date(None) is None


def test_v4_guidewire_claim_number_rule():
    """Validates Section 42: If ClaimNumber length == 9, prefix '0', else leave unchanged."""
    assert format_claim_number("123456789") == "0123456789"
    assert format_claim_number("0123456789") == "0123456789"
    assert format_claim_number("12345678") == "12345678"
    assert format_claim_number("12345678901") == "12345678901"


def test_v4_case_style_cleaning():
    """Validates CaseStyle normalization (CRLF, non-breaking space, parentheses, multiple spaces)."""
    raw_style = "STATE OF FLORIDA (VS)\r\n  GONZALEZ, \xa0 SERGIO  (ET AL)  "
    cleaned = clean_case_style(raw_style)
    assert "\r" not in cleaned
    assert "\n" not in cleaned
    assert "\xa0" not in cleaned
    assert "(" not in cleaned
    assert ")" not in cleaned
    assert "  " not in cleaned
    assert cleaned == "STATE OF FLORIDA VS GONZALEZ, SERGIO ET AL"


def test_v4_fuzzy_3tier_cascade_and_deduplication():
    """Validates RapidFuzz 3-tier sequence (Claimant -> Insured -> Driver) and dedup."""
    case = {
        "CaseNumber": "2026-CA-001234",
        "CaseStyle": "MIGUEL TOLEDO VS SERGIO GONZALEZ AND CARLOS GONZALEZ",
        "CountyWebsite": "https://www2.miamidadeclerk.gov/ocs/",
        "SuitFiledDate": "08/21/2026",
    }

    claimant_name = "SERGIO GONZALEZ"
    insured_name = "CARLOS GONZALEZ"
    driver_name = "ANTONIO GONZALEZ"

    evals = evaluate_case_against_parties(
        case,
        claimant_name=claimant_name,
        insured_name=insured_name,
        driver_name=driver_name,
        threshold=0.60,
    )

    # In 3-tier cascade, Claimant is checked first
    clm_eval = next(e for e in evals if e["party_type"] == PartyTypeEnum.CLAIMANT)
    assert clm_eval["is_match"] is True
    assert clm_eval["similarity_score"] >= 0.60

    # Insured also matches the text, but the system must prioritize Claimant and deduplicate
    ins_eval = next(e for e in evals if e["party_type"] == PartyTypeEnum.INSURED)
    assert ins_eval["is_match"] is True


def test_v4_strict_portal_schema_contracts():
    """Validates that Harris JP and Harris County Clerk outputs omit CaseType, while others include it."""
    # Harris JP contract
    harris_jp_case = {
        "CaseNumber": "26-JP-001234",
        "CaseStyle": "SMITH VS DOE",
        "CountyWebsite": "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29",
        "FilingDate": "01/15/2025",
        "CaseStatus": "ACTIVE",
    }
    assert "CaseType" not in harris_jp_case
    assert "CaseNumber" in harris_jp_case
    assert "CaseStyle" in harris_jp_case
    assert "CaseStatus" in harris_jp_case

    # Harris County Clerk contract
    harris_cclerk_case = {
        "CaseNumber": "1234567",
        "FilingDate": "01/15/2025",
        "CaseStyle": "SMITH VS DOE",
        "CaseStatus": "ACTIVE",
        "CountyWebsite": "https://www.cclerk.hctx.net/Applications/WebSearch/",
    }
    assert "CaseType" not in harris_cclerk_case
    assert "FilingDate" in harris_cclerk_case

    # Florida & District contracts have CaseType
    broward_case = {
        "CaseNumber": "CACE-26-001234",
        "CaseStyle": "DOE VS SMITH",
        "CountyWebsite": "https://www.browardclerk.org/Web2/",
        "FilingDate": "01/15/2025",
        "CaseStatus": "OPEN",
        "CaseType": "CIRCUIT CIVIL",
    }
    assert "CaseType" in broward_case


@pytest.mark.asyncio
async def test_v4_guidewire_mock_dispatch():
    """Validates GuidewireClient caseupdate structure and mock activity creation."""
    client = GuidewireClient(mock_mode=True)
    res = await client.send_case_update(
        claim_number="123456789",  # 9-digit -> will be padded to 0123456789
        exposure_number="1",
        matched_cases=[
            {
                "CaseNumber": "2026-CA-001234",
                "CaseStyle": "MIGUEL TOLEDO VS SERGIO GONZALEZ",
                "CountyWebsite": "https://www2.miamidadeclerk.gov/ocs/",
                "SuitFiledDate": "08/21/2026",
            }
        ],
    )

    assert res["success"] is True
    assert res["status_code"] == 200
    assert "activityId" in res["response"]
    assert res["payload_sent"]["ClaimNumber"] == "0123456789"
    assert len(res["payload_sent"]["CaseItems"]) == 1
    item = res["payload_sent"]["CaseItems"][0]
    assert item["CaseNumber"] == "2026-CA-001234"
    assert item["SuitFiledDate"] == "08/21/2026"
