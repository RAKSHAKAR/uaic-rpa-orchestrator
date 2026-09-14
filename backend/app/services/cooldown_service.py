"""Portal Cooldown & Rate-Limit Tracking Service.

Manages portal-specific cooldown states using Redis with in-memory fallback,
enabling non-blocking execution and automated retry scheduling for rate-limited
or security-blocked county court portals.
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

COOLDOWN_KEY_PREFIX = "uaic:cooldown:"


def _get_redis_client() -> redis.Redis | None:
    """Returns a connected Redis client, or None if unavailable."""
    try:
        r = redis.Redis.from_url(settings.CELERY_BROKER_URL, socket_connect_timeout=1.0, socket_timeout=1.0)
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
    effective_seconds = cooldown_seconds if cooldown_seconds is not None else (seconds if seconds is not None else 300)
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
            logger.info(f"Set Redis cooldown for portal '{portal_key}': {effective_seconds}s (reason: {reason})")
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
                "broward", "hillsborough", "miami",
                "travis", "dallas", "harris_jp", "harris_cclerk", "harris_district"
            ]:
                r.delete(f"{COOLDOWN_KEY_PREFIX}{k}")
        except Exception as e:
            logger.warning(f"Could not clear all Redis cooldowns: {e}")
    return True


def get_all_portal_cooldowns(portal_keys: list[str] | None = None) -> dict[str, dict[str, Any]]:
    """Returns the cooldown status of all registered or requested portals."""
    default_keys = [
        "broward", "hillsborough", "miami",
        "travis", "dallas", "harris_jp", "harris_cclerk", "harris_district"
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
