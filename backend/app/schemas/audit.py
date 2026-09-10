"""Pydantic schemas for audit log validation, filtering, and API responses."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AuditLogResponse(BaseModel):
    """Schema for serialized audit log entry."""

    id: str
    timestamp: datetime
    user_id: str
    user_email: str
    ip_address: str | None = None
    user_agent: str | None = None
    action: str
    entity_type: str
    entity_id: str | None = None
    claim_number: str | None = None
    description: str
    status: str = "SUCCESS"
    details: dict[str, Any] | None = None

    model_config = ConfigDict(from_attributes=True)


class AuditLogListResponse(BaseModel):
    """Paginated list response for audit logs."""

    items: list[AuditLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AuditLogStatsResponse(BaseModel):
    """Aggregated statistics and KPI metrics for audit events."""

    total_events: int = 0
    total_today: int = 0
    total_claims_ops: int = 0
    total_settings_ops: int = 0
    total_match_reviews: int = 0
    total_failures: int = 0
    by_action: dict[str, int] = Field(default_factory=dict)
    by_entity_type: dict[str, int] = Field(default_factory=dict)
    by_status: dict[str, int] = Field(default_factory=dict)
