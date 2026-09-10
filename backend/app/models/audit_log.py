"""SQLAlchemy model for enterprise audit logging (who did what, when, and changes made)."""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AuditLog(Base):
    """Immutable audit trail log for tracking operator actions, automation events, and configurations."""

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), index=True
    )

    # Operator / Client Identity
    user_id: Mapped[str] = mapped_column(String(100), default="operator", index=True)
    user_email: Mapped[str] = mapped_column(
        String(255), default="operator@test.com", index=True
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Action & Entity Categorization
    action: Mapped[str] = mapped_column(
        String(60), index=True
    )  # e.g. CLAIM_CREATED, SETTINGS_UPDATED, AUTOMATION_STARTED
    entity_type: Mapped[str] = mapped_column(
        String(40), index=True
    )  # e.g. CLAIM, SETTINGS, MATCH, BATCH, QUEUE, SYSTEM
    entity_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    claim_number: Mapped[str | None] = mapped_column(
        String(50), nullable=True, index=True
    )

    # Context & Result
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(20), default="SUCCESS", index=True
    )  # SUCCESS, FAILURE, WARNING, INFO

    # JSON Payload (All credentials strictly masked)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<AuditLog {self.id} | {self.action} on {self.entity_type}:{self.entity_id} by {self.user_email}>"
