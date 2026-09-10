"""Pydantic schemas for Ingestion Batch & Queue Monitoring."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BatchSummaryResponse(BaseModel):
    id: str
    filename: str
    total_records: int
    processed_records: int
    failed_records: int
    duplicate_records: int = 0
    invalid_records: int = 0
    status: str
    error_message: str | None = None
    mapping_config: dict | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QueueStatusResponse(BaseModel):
    active_tasks: int
    pending_tasks: int
    failed_tasks: int
    completed_tasks: int
    queues: dict[str, int]
    workers_online: int


class RetriggerRequest(BaseModel):
    claim_ids: list[str] | None = None  # If empty, retrigger all failed claims


class RetriggerResponse(BaseModel):
    status: str
    retriggered_count: int
    message: str


class TargetFieldDefinition(BaseModel):
    key: str
    label: str
    required: bool
    description: str


class ColumnMappingRecommendation(BaseModel):
    target_key: str
    target_label: str
    source_column: str | None = None
    confidence: str  # EXACT, HIGH_FUZZY, LOW_FUZZY, UNMAPPED
    confidence_score: float = 0.0
    required: bool = False


class FilePreviewRecord(BaseModel):
    row_number: int
    claim_number: str
    insured_name: str | None = None
    claimant_name: str | None = None
    driver_name: str | None = None
    dol: str | None = None
    policy_state: str | None = None
    loss_location: str | None = None
    target_bots: list[str] = []


class FilePreviewResponse(BaseModel):
    filename: str
    filesize_bytes: int
    filesize_formatted: str
    file_type: str
    total_records: int
    valid_records: int
    invalid_records: int
    sheet_names: list[str] = []
    detected_columns: list[str] = []
    column_samples: dict[str, list[str]] = {}
    target_fields: list[TargetFieldDefinition] = []
    mapping_recommendations: list[ColumnMappingRecommendation] = []
    florida_claims_count: int = 0
    texas_claims_count: int = 0
    cross_state_claims_count: int = 0
    estimated_bot_runs: int = 0
    preview_records: list[FilePreviewRecord] = []


class ValidationIssue(BaseModel):
    row_number: int
    claim_number: str | None = None
    issue_type: str  # INVALID, DUPLICATE_IN_FILE, DUPLICATE_IN_DB
    reason: str


class FileValidationResponse(BaseModel):
    filename: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    duplicate_rows: int
    duplicate_strategy: str
    florida_claims_count: int = 0
    texas_claims_count: int = 0
    cross_state_claims_count: int = 0
    estimated_bot_runs: int = 0
    issues: list[ValidationIssue] = []
    preview_records: list[FilePreviewRecord] = []
    can_proceed: bool = True


class LiveQueueItemResponse(BaseModel):
    id: str
    claim_number: str
    exposure_number: str | None = None
    insured_name: str | None = None
    claimant_name: str | None = None
    driver_name: str | None = None
    dol: str | None = None
    policy_state: str | None = None
    loss_location_state: str | None = None
    loss_location_city: str | None = None
    loss_location_county: str | None = None
    record_status: str
    fuzzy_match_status: str | None = None
    queue_position: int | None = None
    portals_to_run: list[str] = []
    bot_statuses: dict[str, str] = {}
    total_duration_seconds: float | None = None
    current_portal: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class LiveQueueStateResponse(BaseModel):
    auto_queue_enabled: bool
    is_running: bool
    current_claim_id: str | None = None
    max_concurrency: int = 3
    available_slots: int = 3
    active_items: list[LiveQueueItemResponse] = []
    active_item: LiveQueueItemResponse | None = None
    pending_items: list[LiveQueueItemResponse] = []
    recently_completed: list[LiveQueueItemResponse] = []
    total_pending_count: int = 0
    total_in_progress_count: int = 0
    workers_online: int = 0


class ConcurrencyUpdateRequest(BaseModel):
    concurrency: int


class SeedDemoClaimsRequest(BaseModel):
    count: int = 10


class RunSelectedQueueRequest(BaseModel):
    claim_ids: list[str]




