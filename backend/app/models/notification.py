"""SQLAlchemy models for enterprise notification logs, templates, and routing rules."""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Notification(Base):
    """Persistent record of an email notification dispatch and delivery lifecycle."""

    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    event_type: Mapped[str] = mapped_column(
        String(60), index=True
    )  # GUIDEWIRE_ACTIVITY_CREATED, GUIDEWIRE_ACTIVITY_FAILED, SCRAPER_FAILED, CLAIM_PROCESSING_FAILED, TEST_EMAIL
    claim_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    claim_number: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)

    # Recipient routing
    recipient: Mapped[str] = mapped_column(String(500), index=True)  # Primary To address(es)
    cc: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bcc: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Message Content
    subject: Mapped[str] = mapped_column(String(255))
    body_html: Mapped[str] = mapped_column(Text)
    body_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Delivery & Provider Details
    provider: Mapped[str] = mapped_column(String(50), default="local_mock")
    status: Mapped[str] = mapped_column(
        String(30), default="PENDING", index=True
    )  # PENDING, QUEUED, SENDING, SENT, FAILED, RETRYING, SKIPPED
    idempotency_key: Mapped[str | None] = mapped_column(
        String(150), nullable=True, unique=True, index=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Telemetry Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), index=True
    )
    queued_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    failed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Context Metadata (Payload details, Correlation IDs)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Delivery Receipt & Verification Provenance (RFC 3798/822 server acknowledgment)
    delivery_receipt: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<Notification {self.id} | {self.event_type} | {self.status} to {self.recipient}>"


class NotificationTemplate(Base):
    """Configurable dynamic email template with event bindings and variable placeholders."""

    __tablename__ = "notification_templates"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    event_type: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    subject_template: Mapped[str] = mapped_column(String(255))
    body_template_html: Mapped[str] = mapped_column(Text)
    body_template_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    def __repr__(self) -> str:
        return f"<NotificationTemplate {self.name} for {self.event_type}>"


class NotificationRule(Base):
    """Configurable routing rules to enable/disable specific event notification triggers."""

    __tablename__ = "notification_rules"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    event_type: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    channels: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    recipient_override: Mapped[str | None] = mapped_column(String(500), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    def __repr__(self) -> str:
        return f"<NotificationRule {self.event_type} | enabled={self.is_enabled}>"
