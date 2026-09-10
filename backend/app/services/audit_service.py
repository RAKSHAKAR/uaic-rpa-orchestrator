"""Enterprise Audit Service — credential sanitization, client context extraction, and audit event recording."""

import asyncio
import logging
from typing import Any

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import TaskAsyncSessionLocal
from app.models.audit_log import AuditLog

logger = logging.getLogger("uaic_orchestrator.audit")

# Sensitive substrings to redact
REDACTED_SUBSTRINGS = (
    "password",
    "secret",
    "token",
    "api_key",
    "apikey",
    "credential",
    "private_key",
    "connection_string",
    "auth",
    "jwt",
)


def sanitize_payload(data: Any) -> Any:
    """Recursively scrub any sensitive credentials, passwords, or API keys from dictionary/list payloads."""
    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            key_lower = str(k).lower()
            if any(sub in key_lower for sub in REDACTED_SUBSTRINGS):
                cleaned[k] = "[REDACTED]"
            else:
                cleaned[k] = sanitize_payload(v)
        return cleaned
    elif isinstance(data, list):
        return [sanitize_payload(item) for item in data]
    elif isinstance(data, tuple):
        return tuple(sanitize_payload(item) for item in data)
    return data


def extract_client_context(request: Request | None = None) -> dict[str, str | None]:
    """Extract operator identity, client IP, and user-agent from FastAPI request headers."""
    if not request:
        return {
            "user_id": "system",
            "user_email": "system@test.com",
            "ip_address": "127.0.0.1",
            "user_agent": "system/background-worker",
        }

    # Extract Client IP
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        ip_address = forwarded.split(",")[0].strip()
    elif request.headers.get("x-real-ip"):
        ip_address = request.headers.get("x-real-ip")
    elif request.client and request.client.host:
        ip_address = request.client.host
    else:
        ip_address = "127.0.0.1"

    # Extract User-Agent
    user_agent = request.headers.get("user-agent")

    # Extract User Identity
    user_id = request.headers.get("x-user-id", "operator")
    user_email = request.headers.get("x-user-email", "operator@test.com")

    return {
        "user_id": user_id,
        "user_email": user_email,
        "ip_address": ip_address,
        "user_agent": user_agent[:500] if user_agent else None,
    }


async def log_audit_event_async(
    session: AsyncSession,
    action: str,
    entity_type: str,
    description: str,
    entity_id: str | None = None,
    claim_number: str | None = None,
    user_id: str | None = None,
    user_email: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    status: str = "SUCCESS",
    details: dict[str, Any] | None = None,
) -> AuditLog:
    """Persist an audit log record within the current database session."""
    sanitized_details = sanitize_payload(details) if details is not None else None

    audit_entry = AuditLog(
        action=action.upper(),
        entity_type=entity_type.upper(),
        description=description,
        entity_id=entity_id,
        claim_number=claim_number,
        user_id=user_id or "operator",
        user_email=user_email or "operator@test.com",
        ip_address=ip_address,
        user_agent=user_agent,
        status=status.upper(),
        details=sanitized_details,
    )
    session.add(audit_entry)
    await session.flush()
    return audit_entry


def record_audit_event_background(
    action: str,
    entity_type: str,
    description: str,
    entity_id: str | None = None,
    claim_number: str | None = None,
    user_id: str | None = None,
    user_email: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    status: str = "SUCCESS",
    details: dict[str, Any] | None = None,
) -> None:
    """Non-blocking fire-and-forget helper using dedicated session to record audit events."""

    async def _runner():
        try:
            async with TaskAsyncSessionLocal() as session:
                await log_audit_event_async(
                    session=session,
                    action=action,
                    entity_type=entity_type,
                    description=description,
                    entity_id=entity_id,
                    claim_number=claim_number,
                    user_id=user_id,
                    user_email=user_email,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    status=status,
                    details=details,
                )
                await session.commit()
        except Exception as e:
            logger.warning(f"Failed to record background audit event '{action}': {e}")

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(_runner())
        else:
            asyncio.run(_runner())
    except Exception:
        try:
            asyncio.run(_runner())
        except Exception as e:
            logger.warning(f"Could not dispatch audit runner: {e}")
