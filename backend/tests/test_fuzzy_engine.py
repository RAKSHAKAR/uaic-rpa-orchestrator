"""Unit and edge-case tests for the RapidFuzz matching engine and business filters."""

from app.models.match_result import MatchReviewStatusEnum, PartyTypeEnum
from app.services.fuzzy_engine import (
    calculate_match_score,
    clean_case_style,
    clean_party_name,
    evaluate_case_against_parties,
    is_case_eligible,
)

# ============================================================================
# 1. Name and Style Cleaning Tests
# ============================================================================

def test_clean_party_name_variations():
    assert clean_party_name("John", "Doe") == "John Doe"
    assert clean_party_name("  John  ", "  Doe  ") == "John Doe"
    assert clean_party_name(None, "Doe") == "Doe"
    assert clean_party_name("John", None) == "John"
    assert clean_party_name(None, None) == ""
    assert clean_party_name("Mary   Jane", "Watson") == "Mary Jane Watson"


def test_clean_case_style_normalization():
    assert clean_case_style(None) == ""
    assert clean_case_style("") == ""
    
    # Strip carriage returns, tabs, non-breaking spaces
    raw = "STATE OF FLORIDA\r\nVS.\nDOE, JOHN \xa0(DEFENDANT)"
    cleaned = clean_case_style(raw)
    assert cleaned == "STATE OF FLORIDA VS. DOE, JOHN DEFENDANT"
    assert "(" not in cleaned
    assert ")" not in cleaned
    assert "\r" not in cleaned
    assert "\n" not in cleaned
    assert "\xa0" not in cleaned


# ============================================================================
# 2. RapidFuzz Scoring Tests
# ============================================================================

def test_calculate_match_score_exact_and_near():
    # Exact match
    score = calculate_match_score("John Doe", "John Doe")
    assert score == 1.0

    # Inverted name order in case style (e.g., DOE, JOHN VS STATE)
    score_inv = calculate_match_score("John Doe", "DOE, JOHN VS ALLSTATE")
    assert score_inv >= 0.85

    # With middle name
    score_mid = calculate_match_score("Sergio Gonzalez", "STATE OF FLORIDA VS GONZALEZ, SERGIO JULIO")
    assert score_mid >= 0.80

    # Partial / Borderline
    score_part = calculate_match_score("Robert Smith", "BOB SMITH VS TRAVELERS")
    assert score_part >= 0.50

    # Completely different
    score_diff = calculate_match_score("Alice Wonder", "MARK ANTHONY VS CITIZENS")
    assert score_diff < 0.40

    # Empty inputs
    assert calculate_match_score("", "Case Style") == 0.0
    assert calculate_match_score("John Doe", "") == 0.0


# ============================================================================
# 3. Case Eligibility & Whitelist Filtering Tests
# ============================================================================

def test_is_case_eligible_filing_date():
    # Modern filing date >= 2010
    assert is_case_eligible(filing_date="2021-05-10", case_status="OPEN", case_type="CIVIL") is True
    assert is_case_eligible(filing_date="05/10/2021", case_status="OPEN", case_type="CIVIL") is True
    assert is_case_eligible(filing_date="2026/08/21", case_status="OPEN", case_type="CIVIL") is True

    # Pre-2010 filing date -> Ineligible
    assert is_case_eligible(filing_date="2008-11-20", case_status="OPEN", case_type="CIVIL") is False
    assert is_case_eligible(filing_date="01/01/1999", case_status="OPEN", case_type="CIVIL") is False

    # Custom minimum filing date
    assert is_case_eligible(filing_date="2015-01-01", case_status="OPEN", case_type="CIVIL", min_filing_date="2018-01-01") is False


def test_is_case_eligible_status_and_type():
    allowed_statuses = ["OPEN", "ACTIVE", "REOPENED"]
    allowed_types = ["CIRCUIT CIVIL", "COUNTY CIVIL", "PERSONAL INJURY – AUTO"]

    # Allowed status and type
    assert is_case_eligible("2022-01-01", "OPEN", "CIRCUIT CIVIL", allowed_statuses=allowed_statuses, allowed_types=allowed_types) is True
    assert is_case_eligible("2022-01-01", "active", "county civil", allowed_statuses=allowed_statuses, allowed_types=allowed_types) is True

    # Disallowed status
    assert is_case_eligible("2022-01-01", "CLOSED", "CIRCUIT CIVIL", allowed_statuses=allowed_statuses, allowed_types=allowed_types) is False
    assert is_case_eligible("2022-01-01", "DISMISSED", "CIRCUIT CIVIL", allowed_statuses=allowed_statuses, allowed_types=allowed_types) is False

    # Disallowed type
    assert is_case_eligible("2022-01-01", "OPEN", "PROBATE", allowed_statuses=allowed_statuses, allowed_types=allowed_types) is False
    assert is_case_eligible("2022-01-01", "OPEN", "CRIMINAL FELONY", allowed_statuses=allowed_statuses, allowed_types=allowed_types) is False


# ============================================================================
# 4. Multi-Party Evaluation Tests
# ============================================================================

def test_evaluate_case_against_parties():
    case = {
        "CaseNumber": "2026-111719-CC-26",
        "CaseStyle": "MIGUEL TOLEDO ET AL VS SERGIO GONZALEZ ET AL",
        "CountyWebsite": "https://www2.miamidadeclerk.gov/ocs/",
        "SuitFiledDate": "08/21/2026",
    }

    evaluations = evaluate_case_against_parties(
        case=case,
        claimant_name="Sergio Gonzalez",
        insured_name="Marco Rodriguez",
        driver_name="Jane Doe",
        threshold=0.60,
        borderline_threshold=0.40,
    )

    # 3 evaluations (Claimant, Insured, Driver)
    assert len(evaluations) == 3

    # Claimant matches "SERGIO GONZALEZ"
    claimant_eval = next(e for e in evaluations if e["party_type"] == PartyTypeEnum.CLAIMANT)
    assert claimant_eval["is_match"] is True
    assert claimant_eval["review_status"] == MatchReviewStatusEnum.AUTO_MATCHED
    assert claimant_eval["similarity_score"] >= 0.80

    # Insured does not match threshold, flagged borderline or rejected
    insured_eval = next(e for e in evaluations if e["party_type"] == PartyTypeEnum.INSURED)
    assert insured_eval["is_match"] is False
    assert insured_eval["review_status"] in [MatchReviewStatusEnum.PENDING_REVIEW, MatchReviewStatusEnum.REJECTED]

    # Driver does not match threshold
    driver_eval = next(e for e in evaluations if e["party_type"] == PartyTypeEnum.DRIVER)
    assert driver_eval["is_match"] is False
