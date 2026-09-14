"""Models package exporting all database entities."""

from app.models.audit_log import AuditLog
from app.models.claim import (
    BotStatusEnum,
    Claim,
    ClaimRecord,
    FuzzyMatchStatusEnum,
    IngestionBatch,
    RecordStatusEnum,
)
from app.models.court_case import ScrapedCourtCase
from app.models.error_screenshot import ErrorScreenshot
from app.models.guidewire import (
    AutomationSetting,
    FilteredOutCase,
    GuidewireActivity,
    SettingsAuditLog,
)
from app.models.match_result import (
    MatchPair,
    MatchReviewStatusEnum,
    PartyTypeEnum,
)
from app.models.notification import (
    Notification,
    NotificationRule,
    NotificationTemplate,
)

__all__ = [
    "AuditLog",
    "AutomationSetting",
    "BotStatusEnum",
    "Claim",
    "ClaimRecord",
    "ErrorScreenshot",
    "FilteredOutCase",
    "FuzzyMatchStatusEnum",
    "GuidewireActivity",
    "IngestionBatch",
    "MatchPair",
    "MatchReviewStatusEnum",
    "Notification",
    "NotificationRule",
    "NotificationTemplate",
    "PartyTypeEnum",
    "RecordStatusEnum",
    "ScrapedCourtCase",
    "SettingsAuditLog",
]
