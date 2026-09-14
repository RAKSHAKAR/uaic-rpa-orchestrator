"""Pydantic schemas for Fuzzy Matching, manual review, and approvals."""

from datetime import datetime

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
    reference_string: str
    target_strings: list[str]
    threshold: float = 0.60


class FuzzyMatchScore(BaseModel):
    target_string: str
    result: str  # "Match Found" | "No Match Found"
    score: float


class DirectFuzzyMatchResponse(BaseModel):
    reference_string: str
    threshold_applied: float
    matches: list[FuzzyMatchScore]


# --- Unique Names API Schemas ---

class UniqueNameItem(BaseModel):
    party_type: str
    first_name: str | None = None
    last_name: str | None = None
    full_name: str
    search_order: int


class UniqueNamesRequest(BaseModel):
    claim_id: str | None = None
    insured_first_name: str | None = None
    insured_last_name: str | None = None
    driver_first_name: str | None = None
    driver_last_name: str | None = None
    claimant_first_name: str | None = None
    claimant_last_name: str | None = None
    threshold: float = 0.85


class UniqueNamesResponse(BaseModel):
    unique_names: list[UniqueNameItem]
    total_unique_names: int
    count: int | None = None
    dual_search: int
    triple_search: int
    claim_number: str | None = None

