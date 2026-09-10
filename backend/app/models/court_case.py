"""ScrapedCourtCase SQLAlchemy Model."""

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.claim import ClaimRecord
    from app.models.match_result import MatchPair


class ScrapedCourtCase(Base):
    """Stores normalized individual court cases scraped from county clerk portals."""
    __tablename__ = "scraped_court_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    claim_id: Mapped[str] = mapped_column(String(36), ForeignKey("claim_records.id"), nullable=False, index=True)

    # County Metadata
    county_name: Mapped[str] = mapped_column(String(100), nullable=False)
    county_website: Mapped[str] = mapped_column(String(255), nullable=False)

    # Case Details
    case_number: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    case_style: Mapped[str] = mapped_column(Text, nullable=False)
    cleaned_case_style: Mapped[str | None] = mapped_column(Text, nullable=True)
    filing_date: Mapped[str | None] = mapped_column(String(50), nullable=True)  # YYYY-MM-DD or MM/DD/YYYY
    case_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    case_type: Mapped[str | None] = mapped_column(String(150), nullable=True)

    # Raw Payload from Scraper
    raw_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    claim: Mapped["ClaimRecord"] = relationship("ClaimRecord", back_populates="scraped_cases", lazy="selectin")
    match_pairs: Mapped[list["MatchPair"]] = relationship("MatchPair", back_populates="court_case", cascade="all, delete-orphan", lazy="selectin")
