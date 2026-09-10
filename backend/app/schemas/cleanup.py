"""Pydantic schemas for the Enterprise Data Cleanup & Retention Engine."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class CleanupCategoryEnum(StrEnum):
    CLAIMS = "claims"
    QUEUE = "queue"
    COURT_CASES = "court_cases"
    FUZZY_MATCHES = "fuzzy_matches"
    GUIDEWIRE_ACTIVITIES = "guidewire_activities"
    NOTIFICATIONS = "notifications"
    NOTIFICATION_DELIVERIES = "notification_deliveries"
    TELEMETRY = "telemetry"
    BOT_HISTORY = "bot_history"
    ERROR_SCREENSHOTS = "error_screenshots"
    DASHBOARD_METRICS = "dashboard_metrics"
    RUN_HISTORY = "run_history"
    APP_LOGS = "app_logs"
    SCRAPER_LOGS = "scraper_logs"
    TEMP_CACHES = "temp_caches"
    GENERATED_EXPORTS = "generated_exports"
    REDIS_RUNTIME = "redis_runtime"
    ALL_OPERATIONAL = "all_operational"
    ALL_SUPPORTED = "all_supported"



class TimeScopeEnum(StrEnum):
    CURRENT_MONTH = "current_month"
    PREVIOUS_MONTH = "previous_month"
    LAST_N_DAYS = "last_n_days"
    LAST_N_WEEKS = "last_n_weeks"
    LAST_N_MONTHS = "last_n_months"
    LAST_N_YEARS = "last_n_years"
    CUSTOM_RANGE = "custom_range"
    BEFORE_DATE = "before_date"
    AFTER_DATE = "after_date"
    ALL_TIME = "all_time"


class CategoryMetadata(BaseModel):
    id: str
    name: str
    description: str
    is_database: bool
    current_count: int = 0


class CleanupPreviewRequest(BaseModel):
    categories: list[str] = Field(
        default=["all_operational"],
        description="List of category IDs or 'all_operational'",
    )
    time_scope: str = Field(
        default="current_month",
        description="Time scope identifier (current_month, previous_month, last_n_days, etc.)",
    )
    n_units: int | None = Field(
        default=None,
        description="Value for N in last_n_days, last_n_weeks, etc.",
    )
    start_date: str | None = Field(
        default=None,
        description="Start date for custom_range (YYYY-MM-DD or ISO)",
    )
    end_date: str | None = Field(
        default=None,
        description="End date for custom_range (YYYY-MM-DD or ISO)",
    )
    before_date: str | None = Field(
        default=None,
        description="Cutoff date for before_date",
    )
    after_date: str | None = Field(
        default=None,
        description="Cutoff date for after_date",
    )


class CleanupPreviewResponse(BaseModel):
    time_scope: str
    start_time: str | None = None
    end_time: str | None = None
    categories: list[str]
    record_counts: dict[str, int]
    file_counts: dict[str, int]
    total_database_records: int
    total_files: int
    can_proceed: bool = True
    warnings: list[str] = Field(default_factory=list)


class CleanupExecuteRequest(BaseModel):
    categories: list[str] = Field(
        default=["all_operational"],
        description="List of category IDs or 'all_operational'",
    )
    time_scope: str = Field(
        default="current_month",
        description="Time scope identifier",
    )
    n_units: int | None = None
    start_date: str | None = None
    end_date: str | None = None
    before_date: str | None = None
    after_date: str | None = None
    confirmed: bool = Field(
        default=False,
        description="Explicit user confirmation required to execute deletion",
    )
    dry_run: bool = Field(
        default=False,
        description="If True, only simulates deletion without committing changes",
    )


class CleanupExecuteResponse(BaseModel):
    cleanup_id: str
    success: bool
    started_at: str
    completed_at: str
    time_scope: str
    start_time: str | None = None
    end_time: str | None = None
    records_deleted: dict[str, int]
    total_records_deleted: int
    files_deleted: int
    redis_purged: bool
    referential_integrity: str = "PASS"
    dashboard_reconciliation: str = "PASS"
    notification_history_reconciliation: str = "PASS"
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
