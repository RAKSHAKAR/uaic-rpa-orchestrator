"""Pydantic schemas for Fuzzy Matching, manual review, and approvals."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.match_result import MatchReviewStatusEnum, PartyTypeEnum


class MatchPairResponse(BaseModel):
    id: str
    claim_id: str
    court_case_id: str
    
    # Party details
    party_type: PartyTypeEnum
    party_name: str
    case_style: str
    
    # Case metadata
    county_name: str | None = None
    case_number: str | None = None
    filing_date: str | None = None
    county_website: str | None = None
    case_status: str | None = None
    case_type: str | None = None
    cleaned_case_style: str | None = None
    raw_payload: dict | None = None

    # Claim Master metadata
    claim_number: str | None = None
    exposure_number: str | None = None
    dol: str | None = None
    policy_state: str | None = None
    loss_location_state: str | None = None
    insured_name: str | None = None
    claimant_name: str | None = None
    driver_name: str | None = None
    claim_status: str | None = None
    
    # Scores & Status
    similarity_score: float
    threshold_applied: float
    is_match: bool
    review_status: MatchReviewStatusEnum
    
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    review_notes: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MatchReviewRequest(BaseModel):
    decision: MatchReviewStatusEnum  # APPROVED or REJECTED
    reviewed_by: str = "Admin"
    review_notes: str | None = None


class FuzzyThresholdConfig(BaseModel):
    threshold: float = 0.60
    borderline_threshold: float = 0.40


# --- Legacy Power Automate Fuzzy Match API schemas ---

class FuzzySearchRequest(BaseModel):
    """Request body for the legacy Power Automate fuzzy match search endpoint."""
    search_name: str
    threshold: float = 0.60
    party_type: str | None = None  # insured | driver | claimant | None (any)
    limit: int = 100
    min_filing_year: int = 2010


class FuzzyMatchItem(BaseModel):
    """A single court case result from the fuzzy match search."""
    court_case_id: str
    case_number: str
    case_style: str
    county_name: str
    county_website: str | None = None
    filing_date: str | None = None
    case_status: str | None = None
    case_type: str | None = None
    similarity_score: float
    claim_id: str | None = None


class FuzzySearchResponse(BaseModel):
    """Response body for the legacy Power Automate fuzzy match search endpoint."""
    matches: list[FuzzyMatchItem]
    total: int
    threshold_applied: float
    search_name: str
    duration_ms: float


# --- Extract Unique Party Names API schema ---

class ExtractNamesResponse(BaseModel):
    """Unique party name lists extracted from all ClaimRecord rows."""
    insured: list[str]
    driver: list[str]
    claimant: list[str]
    total: int


# --- Direct Legacy /fuzzymatchapi Parity Schemas ---

class DirectFuzzyMatchRequest(BaseModel):
    # Canonical PowerAutomateSolutions/fuzzy-match-api fields
    text1: str | None = None
    text2: str | None = None
    threshold: float = 0.60
    filing_date: str | None = None
    min_filing_date: str | None = None
    cases: list[dict[str, Any]] | None = None

    # Backward compatibility with array evaluator
    reference_string: str | None = None
    target_strings: list[str] | None = None

    model_config = ConfigDict(extra="ignore")


class FuzzyMatchScore(BaseModel):
    target_string: str
    result: str  # "Match Found" | "No Match Found"
    score: float
    filing_date: str | None = None
    guidewire_eligible: bool | None = None
    filter_reason: str | None = None


class DirectFuzzyMatchResponse(BaseModel):
    # Canonical fuzzy-match-api response fields
    result: str = "No Match Found"
    score: float = 0.0
    text1: str | None = None
    text2: str | None = None
    threshold_applied: float = 60.0
    filing_date: str | None = None
    min_filing_date: str | None = None
    guidewire_eligible: bool | None = None
    filter_reason: str | None = None

    # Array / Batch case compatibility fields
    reference_string: str | None = None
    matches: list[FuzzyMatchScore] | None = None
    cases: list[dict[str, Any]] | None = None
    cases_results: list[dict[str, Any]] | None = None
    cases_evaluated: int | None = None
    eligible_for_guidewire: int | None = None

    model_config = ConfigDict(extra="ignore")


# --- Unique Names API Schemas ---

class UniqueNameItem(BaseModel):
    party_type: str
    first_name: str | None = None
    last_name: str | None = None
    full_name: str
    name: str | None = None
    search_order: int
    target_number: int | None = None


class UniqueNamesRequest(BaseModel):
    claim_id: str | None = None
    claim_number: str | None = None
    threshold: float = 0.60
    noise_patterns: list[str] | None = None

    # Canonical 3-array format (Guidewire / Robin / UI Live Tester)
    Claimants: list[Any] | None = None
    claimants: list[Any] | None = None
    Insureds: list[Any] | None = None
    insureds: list[Any] | None = None
    Drivers: list[Any] | None = None
    drivers: list[Any] | None = None
    parties: list[Any] | None = None

    # Backwards-compatible flat string fields
    insured_first_name: str | None = None
    insured_last_name: str | None = None
    driver_first_name: str | None = None
    driver_last_name: str | None = None
    claimant_first_name: str | None = None
    claimant_last_name: str | None = None

    model_config = ConfigDict(extra="ignore")


class UniqueNamesResponse(BaseModel):
    unique_names: list[UniqueNameItem]
    total_unique_names: int
    count: int | None = None

    model_config = ConfigDict(extra="ignore")

