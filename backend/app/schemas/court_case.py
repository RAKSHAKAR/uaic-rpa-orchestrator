"""Pydantic schemas for Court Cases."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ScrapedCourtCaseSchema(BaseModel):
    """Schema for individual scraped court case."""
    id: str
    claim_id: str
    county_name: str
    county_website: str
    case_number: str
    case_style: str
    cleaned_case_style: str | None = None
    filing_date: str | None = None
    case_status: str | None = None
    case_type: str | None = None
    raw_payload: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourtCaseFilterPayload(BaseModel):
    min_filing_date: str = "2010-01-01"
    allowed_statuses: list[str] | None = None
    allowed_types: list[str] | None = None
