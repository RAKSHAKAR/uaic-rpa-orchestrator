"""ClaimRecord and IngestionBatch SQLAlchemy Models."""

import enum
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.court_case import ScrapedCourtCase
    from app.models.error_screenshot import ErrorScreenshot
    from app.models.guidewire import FilteredOutCase, GuidewireActivity
    from app.models.match_result import MatchPair


class RecordStatusEnum(enum.StrEnum):
    """Corresponds to legacy Dataverse uaic_recordstatus optionset."""
    NEW = "NEW"                                     # 870300000: New Record Added
    SCRAPING_IN_PROGRESS = "SCRAPING_IN_PROGRESS"   # 870300001: Web Scrapping in Progress
    SCRAPING_COMPLETED = "SCRAPING_COMPLETED"       # 870300002: Web Scrapping Completed
    MATCH_FOUND = "MATCH_FOUND"                     # 870300003: Positive Match Found
    NO_MATCH_FOUND = "NO_MATCH_FOUND"               # 870300004: Positive Match Not Found
    MANUAL_REVIEW = "MANUAL_REVIEW"                 # Borderline fuzzy match requiring human review
    FAILED = "FAILED"                               # Processing/Scraping failure
    COMPLETED = "COMPLETED"                         # 870300005: Completed / Guidewire Updated


class FuzzyMatchStatusEnum(enum.StrEnum):
    """Corresponds to legacy Dataverse uaic_fuzzymatchchoice optionset."""
    NEW = "NEW"                                     # 870300000: Fuzzy Match New
    IN_PROGRESS = "IN_PROGRESS"                     # 870300001: Fuzzy Match Inprogress
    COMPLETED = "COMPLETED"                         # 870300002: Fuzzy Match Completed
    NO_MATCH_FOUND = "NO_MATCH_FOUND"               # 870300003: No Positive Match Found
    PENDING_REVIEW = "PENDING_REVIEW"               # Flagged for human review


class BotStatusEnum(enum.StrEnum):
    """Corresponds to legacy Dataverse uaic_botstatus optionset."""
    NOT_TRIGGERED = "NOT_TRIGGERED"
    IN_PROGRESS = "IN_PROGRESS"                     # 870300000
    COMPLETED = "COMPLETED"                         # 870300001
    FAILED = "FAILED"                               # 870300002
    NO_MATCH_FOUND = "NO_MATCH_FOUND"               # 870300003
    BLOCKED = "BLOCKED"                             # Rate limit / WAF / Security challenge block


class IngestionBatch(Base):
    """Tracks file ingestion batches for Excel/CSV uploads."""
    __tablename__ = "ingestion_batches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    total_records: Mapped[int] = mapped_column(Integer, default=0)
    processed_records: Mapped[int] = mapped_column(Integer, default=0)
    failed_records: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_records: Mapped[int] = mapped_column(Integer, default=0)
    invalid_records: Mapped[int] = mapped_column(Integer, default=0)
    mapping_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    failed_rows_data: Mapped[list | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="PROCESSING")  # PROCESSING, COMPLETED, FAILED
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    claims: Mapped[list[ClaimRecord]] = relationship("ClaimRecord", back_populates="batch", cascade="all, delete-orphan")


class ClaimRecord(Base):
    """Main claim record model mirroring legacy uaic_uaic_bot_creation_database."""
    __tablename__ = "claim_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("ingestion_batches.id"), nullable=True)
    
    # Claim and Primary Identifiers
    claim_number: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    exposure_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    primary_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    log_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    dol: Mapped[str | None] = mapped_column(String(50), nullable=True)  # Date of Loss (MM/DD/YYYY)

    # Party Names
    insured_first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    insured_last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    claimant_first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    claimant_last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    driver_first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    driver_last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Geographic / Location Data
    loss_location_state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    policy_state: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Processing & Lifecycle Status
    record_status: Mapped[RecordStatusEnum] = mapped_column(
        Enum(RecordStatusEnum), default=RecordStatusEnum.NEW, index=True
    )
    fuzzy_match_status: Mapped[FuzzyMatchStatusEnum] = mapped_column(
        Enum(FuzzyMatchStatusEnum), default=FuzzyMatchStatusEnum.NEW, index=True
    )

    # -------------------------------------------------------------
    # Florida County RPA Bot Target Flags & Status
    # -------------------------------------------------------------
    fl_website_broward: Mapped[str | None] = mapped_column(String(10), default="No")
    fl_botstatus_broward: Mapped[BotStatusEnum] = mapped_column(Enum(BotStatusEnum), default=BotStatusEnum.NOT_TRIGGERED)
    fl_jsonbody_broward: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    fl_website_hillsborough: Mapped[str | None] = mapped_column(String(10), default="No")
    fl_botstatus_hillsborough: Mapped[BotStatusEnum] = mapped_column(Enum(BotStatusEnum), default=BotStatusEnum.NOT_TRIGGERED)
    fl_jsonbody_hillsborough: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    fl_website_miami: Mapped[str | None] = mapped_column(String(10), default="No")
    fl_botstatus_miami: Mapped[BotStatusEnum] = mapped_column(Enum(BotStatusEnum), default=BotStatusEnum.NOT_TRIGGERED)
    fl_jsonbody_miami: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # -------------------------------------------------------------
    # Texas County RPA Bot Target Flags & Status
    # -------------------------------------------------------------
    te_website_travis: Mapped[str | None] = mapped_column(String(10), default="No")
    te_botstatus_travis: Mapped[BotStatusEnum] = mapped_column(Enum(BotStatusEnum), default=BotStatusEnum.NOT_TRIGGERED)
    te_jsonbody_travis: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    te_website_dallas: Mapped[str | None] = mapped_column(String(10), default="No")
    te_botstatus_dallas: Mapped[BotStatusEnum] = mapped_column(Enum(BotStatusEnum), default=BotStatusEnum.NOT_TRIGGERED)
    te_jsonbody_dallas: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    te_website_harris: Mapped[str | None] = mapped_column(String(10), default="No")
    te_botstatus_harris: Mapped[BotStatusEnum] = mapped_column(Enum(BotStatusEnum), default=BotStatusEnum.NOT_TRIGGERED)
    te_jsonbody_harris: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    te_website_cclerk: Mapped[str | None] = mapped_column(String(10), default="No")
    te_botstatus_cclerk: Mapped[BotStatusEnum] = mapped_column(Enum(BotStatusEnum), default=BotStatusEnum.NOT_TRIGGERED)
    te_jsonbody_cclerk: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    te_website_hcdistrict: Mapped[str | None] = mapped_column(String(10), default="No")
    te_botstatus_hcdistrict: Mapped[BotStatusEnum] = mapped_column(Enum(BotStatusEnum), default=BotStatusEnum.NOT_TRIGGERED)
    te_jsonbody_hcdistrict: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Downstream Notification & Match Output
    final_matched_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    activity_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Workflow Action Telemetry & Granular Durations
    action_timings: Mapped[dict | None] = mapped_column(JSON, default=dict, nullable=True)
    total_duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    batch: Mapped[IngestionBatch | None] = relationship("IngestionBatch", back_populates="claims", lazy="selectin")
    scraped_cases: Mapped[list["ScrapedCourtCase"]] = relationship("ScrapedCourtCase", back_populates="claim", cascade="all, delete-orphan", lazy="selectin")
    match_pairs: Mapped[list["MatchPair"]] = relationship("MatchPair", back_populates="claim", cascade="all, delete-orphan", lazy="selectin")
    error_screenshots: Mapped[list["ErrorScreenshot"]] = relationship("ErrorScreenshot", back_populates="claim", cascade="all, delete-orphan", lazy="selectin")
    guidewire_activities: Mapped[list["GuidewireActivity"]] = relationship("GuidewireActivity", back_populates="claim", cascade="all, delete-orphan", lazy="selectin")
    filtered_cases: Mapped[list["FilteredOutCase"]] = relationship("FilteredOutCase", back_populates="claim", cascade="all, delete-orphan", lazy="selectin")


# Alias for backward compatibility and prompt diagram conventions
Claim = ClaimRecord
