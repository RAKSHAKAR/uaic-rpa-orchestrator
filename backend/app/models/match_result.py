"""MatchPair SQLAlchemy Model for fuzzy matching audit and human review."""

import enum
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.claim import ClaimRecord
    from app.models.court_case import ScrapedCourtCase


class PartyTypeEnum(enum.StrEnum):
    CLAIMANT = "CLAIMANT"
    INSURED = "INSURED"
    DRIVER = "DRIVER"


class MatchReviewStatusEnum(enum.StrEnum):
    AUTO_MATCHED = "AUTO_MATCHED"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class MatchPair(Base):
    """Audit table for party-to-case fuzzy comparison pairs with human review capability."""
    __tablename__ = "match_pairs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    claim_id: Mapped[str] = mapped_column(String(36), ForeignKey("claim_records.id"), nullable=False, index=True)
    court_case_id: Mapped[str] = mapped_column(String(36), ForeignKey("scraped_court_cases.id"), nullable=False, index=True)

    # Comparison Details
    party_type: Mapped[PartyTypeEnum] = mapped_column(Enum(PartyTypeEnum), nullable=False)
    party_name: Mapped[str] = mapped_column(String(200), nullable=False)
    case_style: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Matching Scores & Decision
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    threshold_applied: Mapped[float] = mapped_column(Float, default=0.60)
    is_match: Mapped[bool] = mapped_column(Boolean, default=False)
    review_status: Mapped[MatchReviewStatusEnum] = mapped_column(
        Enum(MatchReviewStatusEnum), default=MatchReviewStatusEnum.PENDING_REVIEW, index=True
    )

    # Human Review Metadata
    reviewed_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    claim: Mapped["ClaimRecord"] = relationship("ClaimRecord", back_populates="match_pairs", lazy="selectin")
    court_case: Mapped["ScrapedCourtCase"] = relationship("ScrapedCourtCase", back_populates="match_pairs", lazy="selectin")
