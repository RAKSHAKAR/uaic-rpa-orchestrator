"""Portal Cooldown & Rate-Limit Tracking Service.

Manages portal-specific cooldown states using Redis with in-memory fallback,
enabling non-blocking execution and automated retry scheduling for rate-limited
or security-blocked county court portals.

Enhanced (IMP-2026-1102-001):
- Portal operational state metadata (first_failure_ts, health_check_result, etc.)
- Pre-redispatch health check support
- Structured state query for monitoring
"""

import json
import logging
import time
from datetime import UTC, datetime
from typing import Any

import redis

from app.core.config import settings

logger = logging.getLogger("uaic_orchestrator.services.cooldown")

# Local in-memory fallback dictionary: {portal_key: {"until": float, "reason": str, "set_at": str}}
_LOCAL_COOLDOWN_CACHE: dict[str, dict[str, Any]] = {}

# Portal operational state metadata (separate from cooldown TTL)
# Persists for diagnostics beyond cooldown expiry
_LOCAL_PORTAL_STATE: dict[str, dict[str, Any]] = {}

COOLDOWN_KEY_PREFIX = "uaic:cooldown:"
PORTAL_STATE_KEY_PREFIX = "uaic:portal_state:"

# All 8 canonical portal keys
ALL_PORTAL_KEYS = [
    "broward",
    "hillsborough",
    "miami",
    "travis",
    "dallas",
    "harris_jp",
    "harris_cclerk",
    "harris_district",
]

# Portal operational sub-states (stored as metadata alongside BotStatusEnum)
class PortalOperationalState:
    READY = "READY"
    RUNNING = "RUNNING"
    CAPTCHA_DETECTED = "CAPTCHA_DETECTED"
    AWAITING_HUMAN = "AWAITING_HUMAN"
    WAF_BLOCKED = "WAF_BLOCKED"
    RATE_LIMITED = "RATE_LIMITED"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    COOLDOWN = "COOLDOWN"
    RETRY_PENDING = "RETRY_PENDING"
    RE_DISPATCHED = "RE_DISPATCHED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    MANUAL_INTERVENTION_REQUIRED = "MANUAL_INTERVENTION_REQUIRED"


def _get_redis_client() -> redis.Redis | None:
    """Returns a connected Redis client, or None if unavailable."""
    try:
        r = redis.Redis.from_url(
            settings.CELERY_BROKER_URL, socket_connect_timeout=1.0, socket_timeout=1.0
        )
        r.ping()
        return r
    except Exception as e:
        logger.debug(f"Redis not available for cooldown service, using in-memory store: {e}")
        return None


def set_portal_cooldown(
    portal_key: str,
    seconds: int | None = None,
    reason: str = "Rate limit / Security block",
    cooldown_seconds: int | None = None,
) -> dict[str, Any]:
    """
    Places a portal into cooldown for the specified number of seconds (default 5 minutes).
    Stores expiration and reason in Redis (with TTL) and in-memory cache.
    """
    effective_seconds = (
        cooldown_seconds
        if cooldown_seconds is not None
        else (seconds if seconds is not None else 300)
    )
    expires_at = time.time() + max(effective_seconds, 5)
    now_iso = datetime.now(UTC).isoformat()
    data = {
        "portal_key": portal_key,
        "cooldown_seconds": effective_seconds,
        "expires_at": expires_at,
        "reason": reason,
        "set_at": now_iso,
    }

    _LOCAL_COOLDOWN_CACHE[portal_key] = data

    r = _get_redis_client()
    if r:
        try:
            key = f"{COOLDOWN_KEY_PREFIX}{portal_key}"
            r.set(key, json.dumps(data), ex=max(effective_seconds, 5))
            logger.info(
                f"Set Redis cooldown for portal '{portal_key}': {effective_seconds}s (reason: {reason})"
            )
        except Exception as e:
            logger.warning(f"Could not persist portal cooldown to Redis: {e}")

    logger.warning(f"Portal '{portal_key}' entered cooldown for {effective_seconds}s: {reason}")
    return data


def is_portal_in_cooldown(portal_key: str) -> tuple[bool, int, str]:
    """
    Checks if a portal is currently in cooldown.
    Returns:
        (is_in_cooldown: bool, remaining_seconds: int, reason: str)
    """
    now = time.time()

    # 1. Check Redis first if available
    r = _get_redis_client()
    if r:
        try:
            key = f"{COOLDOWN_KEY_PREFIX}{portal_key}"
            raw = r.get(key)
            if raw:
                payload = json.loads(raw)
                exp = payload.get("expires_at", 0)
                remaining = int(exp - now)
                if remaining > 0:
                    return True, remaining, payload.get("reason", "In cooldown")
                else:
                    # Expired, clear from Redis
                    r.delete(key)
        except Exception as e:
            logger.debug(f"Error checking Redis cooldown for '{portal_key}': {e}")

    # 2. Check local in-memory fallback
    local_data = _LOCAL_COOLDOWN_CACHE.get(portal_key)
    if local_data:
        exp = local_data.get("expires_at", 0)
        remaining = int(exp - now)
        if remaining > 0:
            return True, remaining, local_data.get("reason", "In cooldown")
        else:
            _LOCAL_COOLDOWN_CACHE.pop(portal_key, None)

    return False, 0, ""


def clear_portal_cooldown(portal_key: str) -> bool:
    """Clears cooldown state for a portal, allowing immediate reprocessing."""
    _LOCAL_COOLDOWN_CACHE.pop(portal_key, None)
    r = _get_redis_client()
    if r:
        try:
            key = f"{COOLDOWN_KEY_PREFIX}{portal_key}"
            r.delete(key)
            logger.info(f"Cleared Redis cooldown for portal '{portal_key}'")
            return True
        except Exception as e:
            logger.warning(f"Could not delete Redis cooldown key: {e}")
    return True


def clear_all_portal_cooldowns() -> bool:
    """Clears all active portal cooldowns from local cache and Redis."""
    _LOCAL_COOLDOWN_CACHE.clear()
    r = _get_redis_client()
    if r:
        try:
            for k in [
                "broward",
                "hillsborough",
                "miami",
                "travis",
                "dallas",
                "harris_jp",
                "harris_cclerk",
                "harris_district",
            ]:
                r.delete(f"{COOLDOWN_KEY_PREFIX}{k}")
        except Exception as e:
            logger.warning(f"Could not clear all Redis cooldowns: {e}")
    return True


def get_all_portal_cooldowns(portal_keys: list[str] | None = None) -> dict[str, dict[str, Any]]:
    """Returns the cooldown status of all registered or requested portals."""
    default_keys = [
        "broward",
        "hillsborough",
        "miami",
        "travis",
        "dallas",
        "harris_jp",
        "harris_cclerk",
        "harris_district",
    ]
    keys = portal_keys or default_keys
    result: dict[str, dict[str, Any]] = {}

    for k in keys:
        in_cooldown, remaining, reason = is_portal_in_cooldown(k)
        result[k] = {
            "portal_key": k,
            "in_cooldown": in_cooldown,
            "remaining_seconds": remaining,
            "reason": reason,
        }

    return result


# ---------------------------------------------------------------------------
# Portal Operational State (IMP-2026-1102-001)
# ---------------------------------------------------------------------------


def set_portal_operational_state(
    portal_key: str,
    state: str,
    *,
    error_code: str | None = None,
    error_category: str | None = None,
    blocking_reason: str | None = None,
    first_failure_ts: str | None = None,
    claim_id: str | None = None,
    task_id: str | None = None,
    retry_count: int = 0,
    max_retries: int = 0,
    cooldown_start: str | None = None,
    cooldown_expiry: str | None = None,
    cooldown_seconds: int = 0,
    health_check_result: str | None = None,
    last_health_check_ts: str | None = None,
    last_successful_execution: str | None = None,
    human_intervention: bool = False,
    redispatch_task_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Persist structured portal operational state for monitoring and re-dispatch decisions.

    State is stored in Redis (TTL=7200s) with in-memory fallback.
    This is separate from the cooldown TTL key and is retained for diagnostics.
    """
    now_iso = datetime.now(UTC).isoformat()
    state_data: dict[str, Any] = {
        "portal_key": portal_key,
        "operational_state": state,
        "error_code": error_code,
        "error_category": error_category,
        "blocking_reason": blocking_reason,
        "first_failure_ts": first_failure_ts or now_iso,
        "most_recent_failure_ts": now_iso,
        "claim_id": claim_id,
        "task_id": task_id,
        "retry_count": retry_count,
        "max_retries": max_retries,
        "cooldown_start": cooldown_start,
        "cooldown_expiry": cooldown_expiry,
        "cooldown_seconds": cooldown_seconds,
        "health_check_result": health_check_result,
        "last_health_check_ts": last_health_check_ts,
        "last_successful_execution": last_successful_execution,
        "human_intervention": human_intervention,
        "redispatch_task_id": redispatch_task_id,
        "updated_at": now_iso,
        **(extra or {}),
    }

    _LOCAL_PORTAL_STATE[portal_key] = state_data

    r = _get_redis_client()
    if r:
        try:
            key = f"{PORTAL_STATE_KEY_PREFIX}{portal_key}"
            r.set(key, json.dumps(state_data), ex=7200)  # 2-hour TTL for diagnostics
        except Exception as e:
            logger.debug(f"Could not persist portal operational state to Redis for '{portal_key}': {e}")

    logger.info(f"Portal '{portal_key}' operational state -> {state} (error_code={error_code})")
    return state_data


def get_portal_operational_state(portal_key: str) -> dict[str, Any]:
    """Retrieve the current operational state metadata for a portal.

    Returns an empty dict if no state has been recorded.
    """
    # 1. Check Redis first
    r = _get_redis_client()
    if r:
        try:
            key = f"{PORTAL_STATE_KEY_PREFIX}{portal_key}"
            raw = r.get(key)
            if raw:
                return json.loads(raw)
        except Exception as e:
            logger.debug(f"Error reading portal state from Redis for '{portal_key}': {e}")

    # 2. In-memory fallback
    return _LOCAL_PORTAL_STATE.get(portal_key, {})


def get_all_portal_operational_states(
    portal_keys: list[str] | None = None,
) -> dict[str, dict[str, Any]]:
    """Return operational state metadata for all or requested portals.

    Merges cooldown status with operational state for a unified monitoring view.
    """
    keys = portal_keys or ALL_PORTAL_KEYS
    result: dict[str, dict[str, Any]] = {}

    for k in keys:
        state = get_portal_operational_state(k)
        in_cooldown, remaining, reason = is_portal_in_cooldown(k)
        result[k] = {
            **state,
            "portal_key": k,
            "in_cooldown": in_cooldown,
            "cooldown_remaining_seconds": remaining,
            "cooldown_reason": reason if in_cooldown else None,
        }

    return result


def check_portal_ready_for_redispatch(
    portal_key: str,
    *,
    require_health_check: bool = False,
) -> tuple[bool, str]:
    """Determine whether a portal is eligible for re-dispatch after cooldown.

    Checks:
    1. Cooldown has fully expired.
    2. Portal is not in MANUAL_INTERVENTION_REQUIRED state (unless explicitly reset).
    3. Optionally, a health check result is recorded and passed.

    Args:
        portal_key: Short portal key (e.g. "travis").
        require_health_check: If True, also verify health_check_result == "PASSED".

    Returns:
        (ready: bool, reason: str)
    """
    in_cooldown, remaining, cooldown_reason = is_portal_in_cooldown(portal_key)
    if in_cooldown:
        return False, f"Portal '{portal_key}' still in cooldown ({remaining}s remaining): {cooldown_reason}"

    state = get_portal_operational_state(portal_key)
    op_state = state.get("operational_state", "")

    if op_state == PortalOperationalState.MANUAL_INTERVENTION_REQUIRED:
        return (
            False,
            f"Portal '{portal_key}' requires manual intervention before re-dispatch.",
        )

    if require_health_check:
        hc_result = state.get("health_check_result")
        if hc_result != "PASSED":
            return (
                False,
                f"Portal '{portal_key}' health check has not confirmed availability "
                f"(last result: {hc_result!r}). Re-dispatch blocked pending health verification.",
            )

    return True, f"Portal '{portal_key}' is eligible for re-dispatch."
