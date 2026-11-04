"""Centralized Error Classification and Handling for UAIC Portal Automation.

Provides structured error classification with unique error codes, categories,
severity levels, and recovery action metadata for all 8 county portal bots.

IMP-2026-1102-001: CAPTCHA, WAF, Exception Handling & Automated Cooldown Re-dispatch
"""

from __future__ import annotations

import enum
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger("uaic_orchestrator.services.error_classifier")


# ---------------------------------------------------------------------------
# Error Code Catalog
# ---------------------------------------------------------------------------


class ErrorCode(enum.StrEnum):
    """Unique error codes for every failure category across all 8 portal bots."""

    # CAPTCHA errors
    CAPTCHA_DETECTED = "CAP-001"
    CAPTCHA_RESOLVED = "CAP-002"
    CAPTCHA_TIMEOUT = "CAP-003"
    CAPTCHA_MAX_ATTEMPTS = "CAP-004"
    CAPTCHA_VERIFICATION_FAILED = "CAP-005"
    CAPTCHA_BALANCE_EXHAUSTED = "CAP-006"
    CAPTCHA_EXTENSION_ERROR = "CAP-007"

    # Session errors
    SESSION_TIMEOUT_POPUP = "SES-001"
    SESSION_EXPIRED_REDIRECT = "SES-002"
    SESSION_RECOVERY_SUCCESS = "SES-003"
    SESSION_RECOVERY_FAILED = "SES-004"
    SESSION_AUTHENTICATION_FAILED = "SES-005"

    # WAF / Security block errors
    WAF_RATE_LIMIT = "WAF-001"
    WAF_PERIMETERX = "WAF-002"
    WAF_CLOUDFLARE = "WAF-003"
    WAF_DATADOME = "WAF-004"
    WAF_IP_BAN = "WAF-005"
    WAF_GENERIC_BLOCK = "WAF-006"
    WAF_TURNSTILE_CHALLENGE = "WAF-007"

    # Network / navigation errors
    NETWORK_TIMEOUT = "NET-001"
    NETWORK_CONNECTION_ERROR = "NET-002"
    PORTAL_UNAVAILABLE = "NET-003"
    PORTAL_NAVIGATION_FAILED = "NET-004"
    HTTP_ERROR = "NET-005"
    UNEXPECTED_REDIRECT = "NET-006"

    # Login / authentication errors
    LOGIN_FAILED = "AUTH-001"
    LOGIN_CREDENTIAL_MISSING = "AUTH-002"
    EXTENSION_BLOCKED = "AUTH-003"
    EXTENSION_INIT_FAILED = "AUTH-004"

    # Search / extraction errors
    SEARCH_SUBMISSION_FAILED = "SRCH-001"
    SEARCH_EMPTY_RESULT = "SRCH-002"
    EXTRACTION_FAILED = "SRCH-003"
    PAGINATION_FAILED = "SRCH-004"

    # Downstream / integration errors
    FUZZY_MATCH_FAILED = "FUZ-001"
    GUIDEWIRE_PUSH_FAILED = "GW-001"
    GUIDEWIRE_PAYLOAD_INVALID = "GW-002"

    # Task / infrastructure errors
    CELERY_TASK_FAILED = "TASK-001"
    REDIS_UNAVAILABLE = "TASK-002"
    WORKER_RESTART = "TASK-003"
    DUPLICATE_DISPATCH = "TASK-004"

    # Cooldown / re-dispatch errors
    COOLDOWN_ACTIVE = "CD-001"
    COOLDOWN_EXPIRED = "CD-002"
    REDISPATCH_SUCCESS = "CD-003"
    REDISPATCH_BLOCKED = "CD-004"
    HEALTH_CHECK_FAILED = "CD-005"
    HEALTH_CHECK_PASSED = "CD-006"

    # General
    UNKNOWN_ERROR = "ERR-001"
    MAX_RETRIES_EXHAUSTED = "ERR-002"
    MANUAL_INTERVENTION_REQUIRED = "ERR-003"


class ErrorCategory(enum.StrEnum):
    """High-level grouping of error codes."""

    CAPTCHA = "CAPTCHA"
    SESSION = "SESSION"
    WAF_SECURITY = "WAF_SECURITY"
    NETWORK = "NETWORK"
    AUTHENTICATION = "AUTHENTICATION"
    SEARCH_EXTRACTION = "SEARCH_EXTRACTION"
    FUZZY_MATCHING = "FUZZY_MATCHING"
    GUIDEWIRE = "GUIDEWIRE"
    TASK_INFRASTRUCTURE = "TASK_INFRASTRUCTURE"
    COOLDOWN_REDISPATCH = "COOLDOWN_REDISPATCH"
    GENERAL = "GENERAL"


class ErrorSeverity(enum.StrEnum):
    """Severity levels for operational triage."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class RecoveryAction(enum.StrEnum):
    """Prescribed recovery action for each error category."""

    INITIATE_CAPTCHA_RESOLUTION = "INITIATE_CAPTCHA_RESOLUTION"
    PAUSE_AND_ESCALATE = "PAUSE_AND_ESCALATE"
    STOP_AND_RECOVER_SESSION = "STOP_AND_RECOVER_SESSION"
    APPLY_PORTAL_COOLDOWN = "APPLY_PORTAL_COOLDOWN"
    STOP_AND_APPLY_APPROVED_HANDLING = "STOP_AND_APPLY_APPROVED_HANDLING"
    BOUNDED_RETRY_WITH_BACKOFF = "BOUNDED_RETRY_WITH_BACKOFF"
    PORTAL_AVAILABILITY_CHECK = "PORTAL_AVAILABILITY_CHECK"
    RAISE_AUTH_ERROR = "RAISE_AUTH_ERROR"
    PRESERVE_CONTEXT_CLASSIFY_RETRYABILITY = "PRESERVE_CONTEXT_CLASSIFY_RETRYABILITY"
    APPLY_FUZZY_RULES = "APPLY_FUZZY_RULES"
    IDEMPOTENT_GUIDEWIRE_RETRY = "IDEMPOTENT_GUIDEWIRE_RETRY"
    RECOVER_WITHOUT_LOSING_WORK = "RECOVER_WITHOUT_LOSING_WORK"
    MARK_AWAITING_HUMAN = "MARK_AWAITING_HUMAN"
    NO_ACTION = "NO_ACTION"
    REDISPATCH_AFTER_COOLDOWN = "REDISPATCH_AFTER_COOLDOWN"


# ---------------------------------------------------------------------------
# Error Classification Metadata Table
# ---------------------------------------------------------------------------

_ERROR_METADATA: dict[ErrorCode, dict[str, Any]] = {
    # CAPTCHA
    ErrorCode.CAPTCHA_DETECTED: {
        "category": ErrorCategory.CAPTCHA,
        "severity": ErrorSeverity.INFO,
        "retry_eligible": True,
        "cooldown_required": False,
        "recovery_action": RecoveryAction.INITIATE_CAPTCHA_RESOLUTION,
        "human_intervention": False,
    },
    ErrorCode.CAPTCHA_RESOLVED: {
        "category": ErrorCategory.CAPTCHA,
        "severity": ErrorSeverity.INFO,
        "retry_eligible": False,
        "cooldown_required": False,
        "recovery_action": RecoveryAction.NO_ACTION,
        "human_intervention": False,
    },
    ErrorCode.CAPTCHA_TIMEOUT: {
        "category": ErrorCategory.CAPTCHA,
        "severity": ErrorSeverity.WARNING,
        "retry_eligible": True,
        "cooldown_required": False,
        "recovery_action": RecoveryAction.PAUSE_AND_ESCALATE,
        "human_intervention": False,
    },
    ErrorCode.CAPTCHA_MAX_ATTEMPTS: {
        "category": ErrorCategory.CAPTCHA,
        "severity": ErrorSeverity.ERROR,
        "retry_eligible": False,
        "cooldown_required": False,
        "recovery_action": RecoveryAction.MARK_AWAITING_HUMAN,
        "human_intervention": True,
    },
    ErrorCode.CAPTCHA_VERIFICATION_FAILED: {
        "category": ErrorCategory.CAPTCHA,
        "severity": ErrorSeverity.ERROR,
        "retry_eligible": True,
        "cooldown_required": False,
        "recovery_action": RecoveryAction.PAUSE_AND_ESCALATE,
        "human_intervention": False,
    },
    ErrorCode.CAPTCHA_BALANCE_EXHAUSTED: {
        "category": ErrorCategory.CAPTCHA,
        "severity": ErrorSeverity.CRITICAL,
        "retry_eligible": False,
        "cooldown_required": False,
        "recovery_action": RecoveryAction.MARK_AWAITING_HUMAN,
        "human_intervention": True,
    },
    # Session
    ErrorCode.SESSION_TIMEOUT_POPUP: {
        "category": ErrorCategory.SESSION,
        "severity": ErrorSeverity.WARNING,
        "retry_eligible": True,
        "cooldown_required": False,
        "recovery_action": RecoveryAction.STOP_AND_RECOVER_SESSION,
        "human_intervention": False,
    },
    ErrorCode.SESSION_EXPIRED_REDIRECT: {
        "category": ErrorCategory.SESSION,
        "severity": ErrorSeverity.WARNING,
        "retry_eligible": True,
        "cooldown_required": False,
        "recovery_action": RecoveryAction.STOP_AND_RECOVER_SESSION,
        "human_intervention": False,
    },
    ErrorCode.SESSION_AUTHENTICATION_FAILED: {
        "category": ErrorCategory.SESSION,
        "severity": ErrorSeverity.ERROR,
        "retry_eligible": False,
        "cooldown_required": False,
        "recovery_action": RecoveryAction.RAISE_AUTH_ERROR,
        "human_intervention": True,
    },
    # WAF / Security
    ErrorCode.WAF_RATE_LIMIT: {
        "category": ErrorCategory.WAF_SECURITY,
        "severity": ErrorSeverity.ERROR,
        "retry_eligible": True,
        "cooldown_required": True,
        "recovery_action": RecoveryAction.APPLY_PORTAL_COOLDOWN,
        "human_intervention": False,
    },
    ErrorCode.WAF_PERIMETERX: {
        "category": ErrorCategory.WAF_SECURITY,
        "severity": ErrorSeverity.ERROR,
        "retry_eligible": True,
        "cooldown_required": True,
        "recovery_action": RecoveryAction.STOP_AND_APPLY_APPROVED_HANDLING,
        "human_intervention": False,
    },
    ErrorCode.WAF_CLOUDFLARE: {
        "category": ErrorCategory.WAF_SECURITY,
        "severity": ErrorSeverity.ERROR,
        "retry_eligible": True,
        "cooldown_required": True,
        "recovery_action": RecoveryAction.APPLY_PORTAL_COOLDOWN,
        "human_intervention": False,
    },
    ErrorCode.WAF_IP_BAN: {
        "category": ErrorCategory.WAF_SECURITY,
        "severity": ErrorSeverity.CRITICAL,
        "retry_eligible": True,
        "cooldown_required": True,
        "recovery_action": RecoveryAction.MARK_AWAITING_HUMAN,
        "human_intervention": True,
    },
    ErrorCode.WAF_GENERIC_BLOCK: {
        "category": ErrorCategory.WAF_SECURITY,
        "severity": ErrorSeverity.ERROR,
        "retry_eligible": True,
        "cooldown_required": True,
        "recovery_action": RecoveryAction.APPLY_PORTAL_COOLDOWN,
        "human_intervention": False,
    },
    # Network
    ErrorCode.NETWORK_TIMEOUT: {
        "category": ErrorCategory.NETWORK,
        "severity": ErrorSeverity.WARNING,
        "retry_eligible": True,
        "cooldown_required": False,
        "recovery_action": RecoveryAction.BOUNDED_RETRY_WITH_BACKOFF,
        "human_intervention": False,
    },
    ErrorCode.PORTAL_UNAVAILABLE: {
        "category": ErrorCategory.NETWORK,
        "severity": ErrorSeverity.ERROR,
        "retry_eligible": True,
        "cooldown_required": True,
        "recovery_action": RecoveryAction.PORTAL_AVAILABILITY_CHECK,
        "human_intervention": False,
    },
    # Extraction
    ErrorCode.EXTRACTION_FAILED: {
        "category": ErrorCategory.SEARCH_EXTRACTION,
        "severity": ErrorSeverity.ERROR,
        "retry_eligible": True,
        "cooldown_required": False,
        "recovery_action": RecoveryAction.PRESERVE_CONTEXT_CLASSIFY_RETRYABILITY,
        "human_intervention": False,
    },
    # Guidewire
    ErrorCode.GUIDEWIRE_PUSH_FAILED: {
        "category": ErrorCategory.GUIDEWIRE,
        "severity": ErrorSeverity.ERROR,
        "retry_eligible": True,
        "cooldown_required": False,
        "recovery_action": RecoveryAction.IDEMPOTENT_GUIDEWIRE_RETRY,
        "human_intervention": False,
    },
    # Infrastructure
    ErrorCode.REDIS_UNAVAILABLE: {
        "category": ErrorCategory.TASK_INFRASTRUCTURE,
        "severity": ErrorSeverity.WARNING,
        "retry_eligible": True,
        "cooldown_required": False,
        "recovery_action": RecoveryAction.RECOVER_WITHOUT_LOSING_WORK,
        "human_intervention": False,
    },
    ErrorCode.DUPLICATE_DISPATCH: {
        "category": ErrorCategory.TASK_INFRASTRUCTURE,
        "severity": ErrorSeverity.WARNING,
        "retry_eligible": False,
        "cooldown_required": False,
        "recovery_action": RecoveryAction.NO_ACTION,
        "human_intervention": False,
    },
    # Cooldown
    ErrorCode.REDISPATCH_BLOCKED: {
        "category": ErrorCategory.COOLDOWN_REDISPATCH,
        "severity": ErrorSeverity.WARNING,
        "retry_eligible": False,
        "cooldown_required": True,
        "recovery_action": RecoveryAction.REDISPATCH_AFTER_COOLDOWN,
        "human_intervention": False,
    },
    ErrorCode.HEALTH_CHECK_FAILED: {
        "category": ErrorCategory.COOLDOWN_REDISPATCH,
        "severity": ErrorSeverity.ERROR,
        "retry_eligible": True,
        "cooldown_required": True,
        "recovery_action": RecoveryAction.APPLY_PORTAL_COOLDOWN,
        "human_intervention": False,
    },
    # General
    ErrorCode.MAX_RETRIES_EXHAUSTED: {
        "category": ErrorCategory.GENERAL,
        "severity": ErrorSeverity.ERROR,
        "retry_eligible": False,
        "cooldown_required": False,
        "recovery_action": RecoveryAction.MARK_AWAITING_HUMAN,
        "human_intervention": True,
    },
    ErrorCode.MANUAL_INTERVENTION_REQUIRED: {
        "category": ErrorCategory.GENERAL,
        "severity": ErrorSeverity.CRITICAL,
        "retry_eligible": False,
        "cooldown_required": False,
        "recovery_action": RecoveryAction.MARK_AWAITING_HUMAN,
        "human_intervention": True,
    },
}

# Default fallback metadata for unregistered codes
_DEFAULT_METADATA: dict[str, Any] = {
    "category": ErrorCategory.GENERAL,
    "severity": ErrorSeverity.ERROR,
    "retry_eligible": False,
    "cooldown_required": False,
    "recovery_action": RecoveryAction.NO_ACTION,
    "human_intervention": False,
}


# ---------------------------------------------------------------------------
# ErrorEvent Dataclass
# ---------------------------------------------------------------------------


@dataclass
class ErrorEvent:
    """Structured error event capturing all required classification fields."""

    error_code: ErrorCode
    portal_id: str  # e.g. "fl_broward", "te_travis"
    bot_id: str  # Matches portal key in scraper_tasks.py (e.g. "broward", "travis")
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    execution_stage: str
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    # Recovery metadata
    retry_eligible: bool = False
    cooldown_required: bool = False
    cooldown_seconds: int = 0
    recovery_action: RecoveryAction = RecoveryAction.NO_ACTION
    human_intervention: bool = False

    # Context
    claim_id: str | None = None
    task_id: str | None = None
    parent_task_id: str | None = None
    retry_attempt: int = 0
    max_retries: int = 0

    # Outcome
    final_outcome: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict for logging and API responses."""
        return {
            "error_code": self.error_code.value,
            "portal_id": self.portal_id,
            "bot_id": self.bot_id,
            "severity": self.severity.value,
            "category": self.category.value,
            "message": self.message,
            "execution_stage": self.execution_stage,
            "timestamp": self.timestamp,
            "retry_eligible": self.retry_eligible,
            "cooldown_required": self.cooldown_required,
            "cooldown_seconds": self.cooldown_seconds,
            "recovery_action": self.recovery_action.value,
            "human_intervention": self.human_intervention,
            "claim_id": self.claim_id,
            "task_id": self.task_id,
            "parent_task_id": self.parent_task_id,
            "retry_attempt": self.retry_attempt,
            "max_retries": self.max_retries,
            "final_outcome": self.final_outcome,
            **self.extra,
        }


# ---------------------------------------------------------------------------
# Portal ID Mapping (canonical portal key → display identifiers)
# ---------------------------------------------------------------------------

PORTAL_ID_MAP: dict[str, dict[str, str]] = {
    "broward": {
        "portal_id": "fl_broward",
        "display_name": "Broward County Clerk (Florida)",
        "url": "https://www.browardclerk.org/Web2",
    },
    "hillsborough": {
        "portal_id": "fl_hillsborough",
        "display_name": "Hillsborough County Clerk – HOVER (Florida)",
        "url": "https://hover.hillsclerk.com/",
    },
    "miami": {
        "portal_id": "fl_miami",
        "display_name": "Miami-Dade County Clerk – OCS (Florida)",
        "url": "https://www2.miamidadeclerk.gov/ocs/",
    },
    "travis": {
        "portal_id": "te_travis",
        "display_name": "Travis County Odyssey Portal (Texas)",
        "url": "https://odysseyweb.traviscountytx.gov/Portal/",
    },
    "dallas": {
        "portal_id": "te_dallas",
        "display_name": "Dallas County Courts Portal (Texas)",
        "url": "https://courtsportal.dallascounty.org/DALLASPROD/",
    },
    "harris_jp": {
        "portal_id": "te_harris_jp",
        "display_name": "Harris County Justice of the Peace (Texas)",
        "url": "https://jpodysseyportal.harriscountytx.gov/",
    },
    "harris_cclerk": {
        "portal_id": "te_harris_cclerk",
        "display_name": "Harris County Clerk WebSearch (Texas)",
        "url": "https://www.cclerk.hctx.net/",
    },
    "harris_district": {
        "portal_id": "te_harris_district",
        "display_name": "Harris County District Clerk (Texas)",
        "url": "https://www.hcdistrictclerk.com/",
    },
}


# ---------------------------------------------------------------------------
# WAF block text → error code mapping (used by exception classifier)
# ---------------------------------------------------------------------------

_WAF_SIGNATURE_MAP: list[tuple[list[str], ErrorCode, int]] = [
    # (keywords, error_code, default_cooldown_seconds)
    (
        ["perimeterx", "powered by perimeterx", "px-captcha", "automation tools to browse",
         "press & hold", "press and hold", "_pxhd", "perimeterx, inc"],
        ErrorCode.WAF_PERIMETERX,
        300,
    ),
    (
        ["waf rate limit", "rate limit", "429 too many requests", "rate limit exceeded", "too many requests", "rate limited",
         "request limit reached", "retry after", "429"],
        ErrorCode.WAF_RATE_LIMIT,
        600,
    ),
    (
        ["cloudflare ray id", "error 1020", "blocked by cloudflare",
         "sorry, you have been blocked", "attention required! | cloudflare",
         "cf-browser-verification", "cf-challenge", "checking your browser"],
        ErrorCode.WAF_CLOUDFLARE,
        300,
    ),
    (
        ["datadome", "protected by datadome"],
        ErrorCode.WAF_DATADOME,
        300,
    ),
    (
        ["your ip has been blocked", "ip address has been banned",
         "client ip forbidden", "access has been restricted"],
        ErrorCode.WAF_IP_BAN,
        600,
    ),
]


def classify_exception(
    exc: Exception | None = None,
    *,
    portal_key: str = "unknown",
    execution_stage: str = "unknown",
    claim_id: str | None = None,
    task_id: str | None = None,
    retry_attempt: int = 0,
    max_retries: int = 0,
    cooldown_override: int | None = None,
) -> ErrorEvent:
    """Classify an exception into a structured ErrorEvent.

    Args:
        exc: The caught exception (may be None for informational events).
        portal_key: Short portal key (e.g. "broward", "travis").
        execution_stage: Stage label (e.g. "CAPTCHA_WAIT", "NAV_TO_SEARCH").
        claim_id: Correlation identifier for the claim being processed.
        task_id: Current Celery task ID.
        retry_attempt: Current retry/attempt number.
        max_retries: Configured maximum retries.
        cooldown_override: Override the default cooldown duration.

    Returns:
        Fully classified ErrorEvent.
    """
    from app.automation.base import (
        CaptchaResolutionError,
        PortalAuthenticationError,
        PortalConfigurationError,
        PortalSearchError,
        SecurityBlockException,
    )

    # Resolve portal display identifiers
    portal_info = PORTAL_ID_MAP.get(portal_key, {})
    portal_id = portal_info.get("portal_id", f"unknown_{portal_key}")

    # Default
    error_code = ErrorCode.UNKNOWN_ERROR
    message = str(exc) if exc else "Unknown error"
    cooldown_seconds = cooldown_override or 0

    if exc is None:
        return ErrorEvent(
            error_code=ErrorCode.UNKNOWN_ERROR,
            portal_id=portal_id,
            bot_id=portal_key,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.GENERAL,
            message=message,
            execution_stage=execution_stage,
            claim_id=claim_id,
            task_id=task_id,
            retry_attempt=retry_attempt,
            max_retries=max_retries,
        )

    # 1. SecurityBlockException — WAF / rate-limit / PerimeterX
    if isinstance(exc, SecurityBlockException):
        sbe_msg_lower = exc.message.lower()
        error_code = ErrorCode.WAF_GENERIC_BLOCK  # default
        for keywords, code, default_cooldown in _WAF_SIGNATURE_MAP:
            if any(kw in sbe_msg_lower for kw in keywords):
                error_code = code
                if not cooldown_override:
                    cooldown_seconds = exc.cooldown_seconds or default_cooldown
                break
        if not cooldown_seconds:
            cooldown_seconds = exc.cooldown_seconds or 300

    # 2. CaptchaResolutionError
    elif isinstance(exc, CaptchaResolutionError):
        error_code = ErrorCode.CAPTCHA_MAX_ATTEMPTS
        message = str(exc)

    # 3. PortalAuthenticationError
    elif isinstance(exc, PortalAuthenticationError):
        error_code = ErrorCode.LOGIN_FAILED
        message = str(exc)

    # 4. PortalConfigurationError
    elif isinstance(exc, PortalConfigurationError):
        error_code = ErrorCode.EXTENSION_BLOCKED if "extension" in str(exc).lower() else ErrorCode.LOGIN_CREDENTIAL_MISSING

    # 5. PortalSearchError (generic scraper failure)
    elif isinstance(exc, PortalSearchError):
        error_code = ErrorCode.SEARCH_SUBMISSION_FAILED
        message = str(exc)

    # 6. TimeoutError / asyncio.TimeoutError
    elif "timeout" in type(exc).__name__.lower() or "timeout" in str(exc).lower():
        error_code = ErrorCode.NETWORK_TIMEOUT
        message = str(exc)

    # 7. ConnectionError / network errors
    elif "connection" in type(exc).__name__.lower() or "connection" in str(exc).lower():
        error_code = ErrorCode.NETWORK_CONNECTION_ERROR
        message = str(exc)

    # Look up metadata from catalog
    meta = _ERROR_METADATA.get(error_code, _DEFAULT_METADATA)

    event = ErrorEvent(
        error_code=error_code,
        portal_id=portal_id,
        bot_id=portal_key,
        severity=meta["severity"],
        category=meta["category"],
        message=message,
        execution_stage=execution_stage,
        retry_eligible=meta["retry_eligible"],
        cooldown_required=meta["cooldown_required"],
        cooldown_seconds=cooldown_seconds,
        recovery_action=meta["recovery_action"],
        human_intervention=meta["human_intervention"],
        claim_id=claim_id,
        task_id=task_id,
        retry_attempt=retry_attempt,
        max_retries=max_retries,
    )

    # Log the classified event
    log_fn = {
        ErrorSeverity.INFO: logger.info,
        ErrorSeverity.WARNING: logger.warning,
        ErrorSeverity.ERROR: logger.error,
        ErrorSeverity.CRITICAL: logger.critical,
    }.get(event.severity, logger.error)

    log_fn(
        f"[{portal_key}] [{event.error_code.value}] {event.category.value}: {event.message} "
        f"(stage={execution_stage}, retry_eligible={event.retry_eligible}, "
        f"cooldown={event.cooldown_seconds}s, human={event.human_intervention})"
    )

    return event


def make_error_event(
    error_code: ErrorCode,
    portal_key: str,
    message: str,
    execution_stage: str,
    *,
    claim_id: str | None = None,
    task_id: str | None = None,
    cooldown_seconds: int = 0,
    retry_attempt: int = 0,
    max_retries: int = 0,
    extra: dict[str, Any] | None = None,
) -> ErrorEvent:
    """Convenience factory to create an ErrorEvent directly from an error code."""
    portal_info = PORTAL_ID_MAP.get(portal_key, {})
    portal_id = portal_info.get("portal_id", f"unknown_{portal_key}")
    meta = _ERROR_METADATA.get(error_code, _DEFAULT_METADATA)

    return ErrorEvent(
        error_code=error_code,
        portal_id=portal_id,
        bot_id=portal_key,
        severity=meta["severity"],
        category=meta["category"],
        message=message,
        execution_stage=execution_stage,
        retry_eligible=meta["retry_eligible"],
        cooldown_required=meta["cooldown_required"] or (cooldown_seconds > 0),
        cooldown_seconds=cooldown_seconds,
        recovery_action=meta["recovery_action"],
        human_intervention=meta["human_intervention"],
        claim_id=claim_id,
        task_id=task_id,
        retry_attempt=retry_attempt,
        max_retries=max_retries,
        extra=extra or {},
    )
