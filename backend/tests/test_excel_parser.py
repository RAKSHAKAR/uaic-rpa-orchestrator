"""Unit and regression tests for Excel and CSV ingestion, date serial parsing, and state routing."""

import os

from app.services.excel_parser import (
    convert_excel_date,
    parse_claim_file,
    resolve_county_bot_targets,
)

# ============================================================================
# 1. Serial Date Parsing Tests
# ============================================================================

def test_convert_excel_date_serial_numbers():
    # 44197 -> 2021-01-01 -> 01/01/2021
    assert convert_excel_date(44197) == "01/01/2021"
    # Float serial
    assert convert_excel_date(44197.0) == "01/01/2021"


def test_convert_excel_date_strings():
    assert convert_excel_date("2023-04-15") == "04/15/2023"
    assert convert_excel_date("04/15/2023") == "04/15/2023"
    assert convert_excel_date("2024/12/31") == "12/31/2024"


def test_convert_excel_date_null_and_edge_cases():
    assert convert_excel_date(None) is None
    assert convert_excel_date("") is None
    assert convert_excel_date("null") is None
    assert convert_excel_date("nan") is None
    assert convert_excel_date("None") is None


# ============================================================================
# 2. State to County RPA Routing Tests (Power Automate Switch logic)
# ============================================================================

def test_resolve_county_bot_targets_florida():
    # When policy state is Florida and loss location is Florida
    targets = resolve_county_bot_targets("Florida", "Florida")
    assert targets["fl_broward"] == "Yes"
    assert targets["fl_hillsborough"] == "Yes"
    assert targets["fl_miami"] == "Yes"
    assert targets["te_dallas"] == "No"
    assert targets["te_travis"] == "No"
    assert targets["te_harris"] == "No"
    assert targets["te_cclerk"] == "No"
    assert targets["te_hcdistrict"] == "No"


def test_resolve_county_bot_targets_texas():
    # When policy state is Texas and loss location is Texas
    targets = resolve_county_bot_targets("Texas", "Texas")
    assert targets["fl_broward"] == "No"
    assert targets["fl_hillsborough"] == "No"
    assert targets["fl_miami"] == "No"
    assert targets["te_dallas"] == "Yes"
    assert targets["te_travis"] == "Yes"
    assert targets["te_harris"] == "Yes"
    assert targets["te_cclerk"] == "Yes"
    assert targets["te_hcdistrict"] == "Yes"


def test_resolve_county_bot_targets_cross_state():
    # Cross-state claim: Florida policy, Texas accident -> All scrapers enabled
    cross = resolve_county_bot_targets("Florida", "Texas")
    for key, val in cross.items():
        assert val == "Yes"

    # Missing states -> All scrapers enabled
    empty = resolve_county_bot_targets(None, None)
    for key, val in empty.items():
        assert val == "Yes"


# ============================================================================
# 3. File Parsing Tests (Existing sample files)
# ============================================================================

def test_parse_sample_claims_excel():
    path = r"c:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC\sample_claims.xlsx"
    if os.path.exists(path):
        records = parse_claim_file(path)
        assert len(records) > 0
        first = records[0]
        assert "Claim Number" in first
        assert "Insured First Name" in first
        assert "Claimant First Name" in first
        assert "Exposure Number" in first
