"""ErrorScreenshot SQLAlchemy Model for Portal Failure Capture."""

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.claim import ClaimRecord


class ErrorScreenshot(Base):
    """Stores error screenshots and diagnostics captured when a portal scraper fails."""
    __tablename__ = "error_screenshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    claim_id: Mapped[str] = mapped_column(String(36), ForeignKey("claim_records.id", ondelete="CASCADE"), nullable=False, index=True)

    portal_key: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    portal_name: Mapped[str] = mapped_column(String(100), nullable=False)
    page_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    page_title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    exception_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)
    storage_provider: Mapped[str] = mapped_column(String(50), default="local")
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    claim: Mapped["ClaimRecord"] = relationship("ClaimRecord", back_populates="error_screenshots", lazy="selectin")
