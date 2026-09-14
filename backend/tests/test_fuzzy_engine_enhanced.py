"""Enhanced fuzzy engine and business eligibility tests (TC-FUZ-001 through TC-FUZ-011)."""

from app.models.match_result import MatchReviewStatusEnum, PartyTypeEnum
from app.services.fuzzy_engine import (
    evaluate_case_against_parties,
    is_case_eligible,
)


def test_tc_fuz_001_filing_date_2011_01_01_passes():
    """TC-FUZ-001: Filing date 2011-01-01 passes strictly after 2010 rule."""
    assert is_case_eligible("2011-01-01", "OPEN", "CIVIL") is True


def test_tc_fuz_002_filing_date_2010_12_31_excluded():
    """TC-FUZ-002: Filing date 2010-12-31 is excluded (filed in year 2010)."""
    assert is_case_eligible("2010-12-31", "OPEN", "CIVIL") is False


def test_tc_fuz_003_filing_date_2010_01_01_excluded():
    """TC-FUZ-003: Filing date 2010-01-01 is excluded."""
    assert is_case_eligible("2010-01-01", "OPEN", "CIVIL") is False


def test_tc_fuz_004_filing_date_2009_06_15_excluded():
    """TC-FUZ-004: Filing date 2009-06-15 is excluded."""
    assert is_case_eligible("2009-06-15", "OPEN", "CIVIL") is False


def test_tc_fuz_005_approved_status_open_passes():
    """TC-FUZ-005: Approved status OPEN passes."""
    assert is_case_eligible("2023-01-01", "OPEN", "CIVIL", allowed_statuses=["OPEN", "ACTIVE"]) is True


def test_tc_fuz_006_unapproved_status_dismissed_excluded():
    """TC-FUZ-006: Unapproved status DISMISSED is excluded."""
    assert is_case_eligible("2023-01-01", "DISMISSED", "CIVIL", allowed_statuses=["OPEN", "ACTIVE"]) is False


def test_tc_fuz_007_approved_type_circuit_civil_passes():
    """TC-FUZ-007: Approved type CIRCUIT CIVIL passes."""
    assert is_case_eligible("2023-01-01", "OPEN", "CIRCUIT CIVIL", allowed_types=["CIRCUIT CIVIL"]) is True


def test_tc_fuz_008_unapproved_type_criminal_excluded():
    """TC-FUZ-008: Unapproved type CRIMINAL is excluded."""
    assert is_case_eligible("2023-01-01", "OPEN", "CRIMINAL", allowed_types=["CIRCUIT CIVIL"]) is False


def test_tc_fuz_009_claimant_match_tier1():
    """TC-FUZ-009: Claimant tier matches when claimant name is in case style."""
    case = {"CaseNumber": "1", "CaseStyle": "ALICE SMITH VS BOB BROWN"}
    evals = evaluate_case_against_parties(case, claimant_name="Alice Smith", insured_name="Charlie Davis", driver_name=None)
    claimant_eval = next(e for e in evals if e["party_type"] == PartyTypeEnum.CLAIMANT)
    assert claimant_eval["is_match"] is True
    assert claimant_eval["review_status"] == MatchReviewStatusEnum.AUTO_MATCHED


def test_tc_fuz_010_insured_match_tier2():
    """TC-FUZ-010: Insured tier matches when claimant does not match."""
    case = {"CaseNumber": "2", "CaseStyle": "CHARLIE DAVIS VS OTHER PARTY"}
    evals = evaluate_case_against_parties(case, claimant_name="Alice Smith", insured_name="Charlie Davis", driver_name=None)
    claimant_eval = next(e for e in evals if e["party_type"] == PartyTypeEnum.CLAIMANT)
    insured_eval = next(e for e in evals if e["party_type"] == PartyTypeEnum.INSURED)
    assert claimant_eval["is_match"] is False
    assert insured_eval["is_match"] is True


def test_tc_fuz_011_no_duplicate_evaluations_per_party():
    """TC-FUZ-011: Multi-party evaluation produces exactly one evaluation per unique party type."""
    case = {"CaseNumber": "3", "CaseStyle": "JOHN DOE VS STATE"}
    evals = evaluate_case_against_parties(case, claimant_name="John Doe", insured_name="Jane Doe", driver_name="Bob")
    party_types = [e["party_type"] for e in evals]
    assert len(party_types) == len(set(party_types)) == 3
