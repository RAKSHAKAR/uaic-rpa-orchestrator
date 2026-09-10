from app.services.excel_parser import convert_excel_date, resolve_county_bot_targets
from app.services.fuzzy_engine import (
    calculate_match_score,
    clean_case_style,
    is_case_eligible,
)
from app.services.guidewire_client import format_claim_number


def test_convert_excel_date():
    # Excel serial dates
    # 44197 -> 2021-01-01 -> 01/01/2021
    assert convert_excel_date(44197) == "01/01/2021"
    # String date parsing
    assert convert_excel_date("2022-05-15") == "05/15/2022"
    assert convert_excel_date("04/10/2023") == "04/10/2023"
    assert convert_excel_date(None) is None
    assert convert_excel_date("null") is None


def test_resolve_county_bot_targets():
    # Florida same state
    fl_targets = resolve_county_bot_targets("Florida", "Florida")
    assert fl_targets["fl_broward"] == "Yes"
    assert fl_targets["fl_hillsborough"] == "Yes"
    assert fl_targets["fl_miami"] == "Yes"
    assert fl_targets["te_travis"] == "No"

    # Texas same state
    tx_targets = resolve_county_bot_targets("Texas", "Texas")
    assert tx_targets["fl_broward"] == "No"
    assert tx_targets["te_dallas"] == "Yes"
    assert tx_targets["te_harris"] == "Yes"
    assert tx_targets["te_cclerk"] == "Yes"

    # Cross-state routing
    cross_targets = resolve_county_bot_targets("Florida", "Texas")
    assert cross_targets["fl_broward"] == "Yes"
    assert cross_targets["te_dallas"] == "Yes"


def test_clean_case_style():
    dirty_style = "JOHN DOE (PLAINTIFF)\r\nVS.\nJANE SMITH \xa0(DEFENDANT)  "
    cleaned = clean_case_style(dirty_style)
    assert "\r" not in cleaned
    assert "\n" not in cleaned
    assert "\xa0" not in cleaned
    assert "(" not in cleaned
    assert ")" not in cleaned
    assert "  " not in cleaned
    assert cleaned == "JOHN DOE PLAINTIFF VS. JANE SMITH DEFENDANT"


def test_calculate_match_score():
    # High confidence match
    score = calculate_match_score("John Doe", "DOE, JOHN VS STATE FARM")
    assert score >= 0.80

    # Medium confidence match
    score_med = calculate_match_score("Jonathan Doe", "JOHN DOE VS SMITH")
    assert score_med >= 0.60

    # Dissimilar
    score_low = calculate_match_score("Alice Wonderland", "BOB BUILDER VS STATE")
    assert score_low < 0.40


def test_is_case_eligible():
    # Eligible case
    assert is_case_eligible(
        filing_date="2021-06-15",
        case_status="OPEN",
        case_type="CIRCUIT CIVIL",
    ) is True

    # Ineligible old filing date
    assert is_case_eligible(
        filing_date="2005-01-01",
        case_status="OPEN",
        case_type="CIRCUIT CIVIL",
    ) is False

    # Ineligible case status
    assert is_case_eligible(
        filing_date="2022-01-01",
        case_status="EXPUNGED AND PURGED",
        case_type="CIRCUIT CIVIL",
    ) is False


def test_format_claim_number():
    # 9 digits -> prefix 0
    assert format_claim_number("123456789") == "0123456789"
    # 10 digits -> keep unchanged
    assert format_claim_number("0123456789") == "0123456789"
