"""Pydantic schemas for Claim validation, ingestion, and responses."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.claim import BotStatusEnum, FuzzyMatchStatusEnum, RecordStatusEnum


class ClaimRowSchema(BaseModel):
    """Schema for validating raw rows parsed from Excel/CSV upload."""
    claim_number: str = Field(..., alias="Claim Number")
    insured_first_name: str | None = Field(None, alias="Insured First Name")
    insured_last_name: str | None = Field(None, alias="Insured Last Name")
    claimant_first_name: str | None = Field(None, alias="Claimant First Name")
    claimant_last_name: str | None = Field(None, alias="Claimant Last Name")
    driver_first_name: str | None = Field(None, alias="Driver First Name (Insured Vehicle)")
    driver_last_name: str | None = Field(None, alias="Driver Last Name (Insured Vehicle)")
    dol: str | None = Field(None, alias="DOL")
    # Note: garaging_city, garaging_state, loss_location_city, loss_location_county removed from
    # ingestion mapping (fields still exist in DB model and API responses for data integrity).
    loss_location_state: str | None = Field(None, alias="Loss Location State")
    policy_state: str | None = Field(None, alias="Policy State")
    exposure_number: str | None = Field(None, alias="Exposure Number")
    primary_key: str | None = Field(None, alias="Primary Key")

    model_config = ConfigDict(populate_by_name=True)


class BotStatusDetail(BaseModel):
    name: str
    website_url: str
    target: str  # Yes / No
    status: BotStatusEnum
    cases_found: int = 0


class ScrapedCaseResponse(BaseModel):
    id: str
    county_name: str
    case_number: str
    case_style: str
    filing_date: str | None = None
    case_status: str | None = None
    case_type: str | None = None
    raw_payload: dict[str, Any] | None = None
    party_name_searched: str | None = None
    source_url: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ErrorScreenshotResponse(BaseModel):
    id: str
    claim_id: str
    portal_key: str
    portal_name: str
    page_url: str | None = None
    page_title: str | None = None
    exception_message: str | None = None
    attempt_number: int = 1
    file_path: str
    image_url: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ClaimResponse(BaseModel):
    id: str
    batch_id: str | None = None
    claim_number: str
    exposure_number: str | None = None
    primary_key: str | None = None
    dol: str | None = None
    
    insured_name: str
    claimant_name: str
    driver_name: str
    
    insured_first_name: str | None = None
    insured_last_name: str | None = None
    claimant_first_name: str | None = None
    claimant_last_name: str | None = None
    driver_first_name: str | None = None
    driver_last_name: str | None = None
    
    loss_location_state: str | None = None
    policy_state: str | None = None
    
    record_status: RecordStatusEnum
    fuzzy_match_status: FuzzyMatchStatusEnum
    
    bots: list[BotStatusDetail] = []
    court_cases: list[ScrapedCaseResponse] = []
    final_matched_json: dict[str, Any] | None = None
    activity_id: str | None = None
    retry_count: int = 0
    last_error: str | None = None
    action_timings: dict[str, Any] | None = None
    total_duration_seconds: float | None = None
    
    created_at: datetime
    updated_at: datetime
    created_on: datetime | None = None
    modified_on: datetime | None = None
    created_by: str = "system"
    modified_by: str = "system"

    model_config = ConfigDict(from_attributes=True)


class ClaimListResponse(BaseModel):
    total: int
    items: list[ClaimResponse]
    page: int
    page_size: int
    total_pages: int = 1


class ProcessingLogEntry(BaseModel):
    timestamp: str | None = None
    level: str = "INFO"
    stage: str | None = None
    portal_key: str | None = None
    category: str | None = "orchestration"
    message: str
    actor: str = "system"
    duration_seconds: float | None = None
    details: dict[str, Any] | None = None


class ExceptionLogEntry(BaseModel):
    id: str | None = None
    timestamp: str | None = None
    stage: str | None = None
    portal_key: str | None = None
    portal_name: str | None = None
    exception_type: str | None = None
    message: str
    exception_message: str | None = None
    stack_trace: str | None = None
    page_url: str | None = None
    screenshot_id: str | None = None
    screenshot_url: str | None = None
    attempt_number: int | None = 1


class ClaimCombinedLogsResponse(BaseModel):
    claim_id: str
    claim_number: str
    created_at: datetime | None = None
    created_on: datetime | None = None
    created_by: str = "system"
    updated_at: datetime | None = None
    modified_on: datetime | None = None
    modified_by: str = "system"
    total_duration_seconds: float | None = None
    record_status: RecordStatusEnum | None = None
    fuzzy_match_status: FuzzyMatchStatusEnum | None = None
    audit_logs: list[Any] = []
    processing_logs: list[ProcessingLogEntry] = []
    exception_logs: list[ExceptionLogEntry] = []
    portal_logs: dict[str, str] = {}


class ClaimCreate(BaseModel):
    claim_number: str = Field(..., min_length=1, description="Unique claim identifier")
    exposure_number: str | None = "1"
    primary_key: str | None = None
    insured_first_name: str | None = None
    insured_last_name: str | None = None
    claimant_first_name: str | None = None
    claimant_last_name: str | None = None
    driver_first_name: str | None = None
    driver_last_name: str | None = None
    dol: str | None = None
    loss_location_state: str | None = None
    policy_state: str | None = None
    created_by: str | None = None
    modified_by: str | None = None
    fl_website_broward: str | None = None
    fl_website_hillsborough: str | None = None
    fl_website_miami: str | None = None
    te_website_travis: str | None = None
    te_website_dallas: str | None = None
    te_website_harris: str | None = None
    te_website_cclerk: str | None = None
    te_website_hcdistrict: str | None = None


class ClaimUpdate(BaseModel):
    claim_number: str | None = None
    exposure_number: str | None = None
    primary_key: str | None = None
    insured_first_name: str | None = None
    insured_last_name: str | None = None
    claimant_first_name: str | None = None
    claimant_last_name: str | None = None
    driver_first_name: str | None = None
    driver_last_name: str | None = None
    dol: str | None = None
    loss_location_state: str | None = None
    policy_state: str | None = None
    record_status: RecordStatusEnum | None = None
    fuzzy_match_status: FuzzyMatchStatusEnum | None = None
    modified_by: str | None = None
    fl_website_broward: str | None = None
    fl_website_hillsborough: str | None = None
    fl_website_miami: str | None = None
    te_website_travis: str | None = None
    te_website_dallas: str | None = None
    te_website_harris: str | None = None
    te_website_cclerk: str | None = None
    te_website_hcdistrict: str | None = None


class BulkActionRequest(BaseModel):
    claim_ids: list[str]
    status: RecordStatusEnum | None = None
    failed_portals_only: bool = True


class BulkActionResponse(BaseModel):
    success: bool
    affected_count: int
    message: str


class CleanDatabaseResponse(BaseModel):
    success: bool
    message: str
    cleared_counts: dict[str, int]

