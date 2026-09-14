"""Guidewire integration, fuzzy filtering audit, and automation settings database models."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

# Dual dialect-compatible types supporting SQLite (development/tests) and PostgreSQL (production)
UUIDType = Uuid(as_uuid=True).with_variant(PG_UUID(as_uuid=True), "postgresql")
JSONType = JSON().with_variant(JSONB, "postgresql")


class GuidewireActivity(Base):
    """Audits all outbound payloads and inbound responses for Guidewire ClaimCenter."""

    __tablename__ = "guidewire_activities"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    claim_id = Column(
        String(36),
        ForeignKey("claim_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    transaction_id = Column(UUIDType, nullable=False, unique=True, index=True, default=uuid.uuid4)
    claim_number = Column(String(20), nullable=False, index=True)
    exposure_number = Column(String(10), nullable=False, default="001")

    request_payload = Column(JSONType, nullable=False)
    response_payload = Column(JSONType, nullable=True)
    http_status = Column(Integer, nullable=True)

    status = Column(String(30), nullable=False, default="PENDING", index=True)
    guidewire_claim_id = Column(String(50), nullable=True)
    guidewire_activity_id = Column(String(50), nullable=True, index=True)
    error_details = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    claim = relationship("ClaimRecord", back_populates="guidewire_activities", lazy="selectin")


class FilteredOutCase(Base):
    """Captures cases matched by Fuzzy Logic but excluded prior to Guidewire."""

    __tablename__ = "filtered_out_cases"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    claim_id = Column(
        String(36),
        ForeignKey("claim_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    case_number = Column(String(100), nullable=False)
    case_style = Column(String(500), nullable=False)
    case_type = Column(String(100), nullable=True)
    case_status = Column(String(100), nullable=True)
    filing_date = Column(DateTime, nullable=True)
    fuzzy_score = Column(Float, nullable=False)
    exclusion_reasons = Column(JSONType, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    claim = relationship("ClaimRecord", back_populates="filtered_cases", lazy="selectin")


class AutomationSetting(Base):
    """Persists dynamic runtime automation configuration key-value pairs."""

    __tablename__ = "automation_settings"

    key = Column(String(100), primary_key=True)
    value = Column(JSONType, nullable=False)
    category = Column(String(50), nullable=True, default="general", index=True)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    audit_logs = relationship(
        "SettingsAuditLog",
        back_populates="setting",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class SettingsAuditLog(Base):
    """Tracks historical changes and audit trails for system automation settings."""

    __tablename__ = "settings_audit_logs"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    key = Column(
        String(100),
        ForeignKey("automation_settings.key", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    old_value = Column(JSONType, nullable=True)
    new_value = Column(JSONType, nullable=False)
    updated_by = Column(String(100), nullable=False, default="system")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    setting = relationship("AutomationSetting", back_populates="audit_logs", lazy="selectin")


__all__ = [
    "AutomationSetting",
    "FilteredOutCase",
    "GuidewireActivity",
    "SettingsAuditLog",
]
