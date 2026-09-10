"""FastAPI router for notification logs, dynamic template previews, and event rules."""

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.notification import Notification, NotificationTemplate
from app.services.email_service import TemplateRenderer
from app.services.settings_service import get_system_settings_async, save_system_settings_async

logger = logging.getLogger("uaic_orchestrator.api.notifications")

router = APIRouter()


class TemplateUpdateRequest(BaseModel):
    """Payload to save or update a custom dynamic notification template."""

    name: str | None = None
    subject_template: str = Field(..., min_length=1, description="Subject template with variable placeholders")
    body_template_html: str = Field(..., min_length=1, description="HTML body template")
    body_template_text: str | None = Field(None, description="Plaintext fallback template")
    is_active: bool = True


class TemplatePreviewRequest(BaseModel):
    """Payload to preview a dynamic template with mock or custom context data."""

    event_type: str | None = None
    subject_template: str | None = None
    body_template_html: str | None = None
    body_template_text: str | None = None
    template_str: str | None = None  # Backward compatibility
    sample_data: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    is_html: bool = True


class TemplatePreviewResponse(BaseModel):
    """Rendered template preview with subject, HTML, plaintext, and backward-compatible rendered_content."""

    event_type: str
    subject: str
    body_html: str
    body_text: str
    rendered_content: str


PARAMETER_CATALOG: list[dict[str, str]] = [
    {
        "token": "claim_number",
        "label": "Claim Number",
        "category": "Claim Info",
        "description": "10-digit zero-prefixed claim identifier",
        "sample": "0100456789",
    },
    {
        "token": "exposure_number",
        "label": "Exposure Number",
        "category": "Claim Info",
        "description": "Guidewire exposure code (e.g. 001)",
        "sample": "001",
    },
    {
        "token": "insured_name",
        "label": "Insured Name",
        "category": "Parties",
        "description": "Full name of the policyholder / insured party",
        "sample": "JOHNATHAN DOE",
    },
    {
        "token": "claimant_name",
        "label": "Claimant Name",
        "category": "Parties",
        "description": "Full name of the claimant",
        "sample": "JANE SMITH",
    },
    {
        "token": "party_name",
        "label": "Primary Party Name",
        "category": "Parties",
        "description": "Primary party associated with the event",
        "sample": "JOHNATHAN DOE",
    },
    {
        "token": "activity_id",
        "label": "Activity ID",
        "category": "Guidewire",
        "description": "Guidewire ClaimCenter activity identifier",
        "sample": "ACT-77829-SAMPLE",
    },
    {
        "token": "county_name",
        "label": "County / Portal",
        "category": "Court & Match Info",
        "description": "Court name or jurisdiction website",
        "sample": "Broward County",
    },
    {
        "token": "matched_count",
        "label": "Match Count",
        "category": "Court & Match Info",
        "description": "Total number of confirmed matching court cases",
        "sample": "2",
    },
    {
        "token": "matched_cases_table",
        "label": "Matched Cases Table (HTML)",
        "category": "Court & Match Info",
        "description": "Full styled HTML table of matched dockets with case numbers, filing dates, parties",
        "sample": "<table>...</table>",
    },
    {
        "token": "error_message",
        "label": "Error Message",
        "category": "System & Runtime",
        "description": "Diagnostic error message if event failed",
        "sample": "Connection refused by destination endpoint",
    },
    {
        "token": "http_status",
        "label": "HTTP Status",
        "category": "System & Runtime",
        "description": "HTTP response status code",
        "sample": "502 Bad Gateway",
    },
    {
        "token": "attempt_number",
        "label": "Attempt Number",
        "category": "System & Runtime",
        "description": "Current retry attempt count",
        "sample": "1 of 3",
    },
    {
        "token": "timestamp",
        "label": "Timestamp",
        "category": "System & Runtime",
        "description": "Formatted execution timestamp (UTC)",
        "sample": "2026-09-05 16:30:00 UTC",
    },
    {
        "token": "environment",
        "label": "Environment",
        "category": "System & Runtime",
        "description": "Production or Development / Mock mode",
        "sample": "Development / Staging",
    },
    {
        "token": "recipient",
        "label": "Recipient Email",
        "category": "System & Runtime",
        "description": "Destination email recipient address",
        "sample": "priyer@test.com",
    },
    {
        "token": "provider",
        "label": "Email Provider",
        "category": "System & Runtime",
        "description": "Active email transport provider (maildev, smtp, direct_mx, local_mock)",
        "sample": "maildev",
    },
    {
        "token": "custom_body",
        "label": "Custom Body",
        "category": "System & Runtime",
        "description": "Custom message or interactive test body",
        "sample": "Interactive verification dispatch",
    },
]


@router.get("", response_model=dict[str, Any])
async def get_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=5, le=500),
    status: str | None = Query(None, description="Filter by status: SENT, FAILED, QUEUED, SENDING, SKIPPED"),
    event_type: str | None = Query(None, description="Filter by event type"),
    search: str | None = Query(None, description="Search recipient, subject, or claim number"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve paginated notification delivery history with filtering and search."""
    query = select(Notification)

    if status and status.upper() != "ALL":
        query = query.where(Notification.status == status.upper())

    if event_type and event_type.upper() != "ALL":
        query = query.where(Notification.event_type.ilike(f"%{event_type}%"))

    if search:
        s = f"%{search.strip()}%"
        query = query.where(
            Notification.recipient.ilike(s)
            | Notification.subject.ilike(s)
            | func.coalesce(Notification.claim_number, "").ilike(s)
        )

    # Count total matching
    count_query = select(func.count()).select_from(query.subquery())
    total_res = await db.execute(count_query)
    total_count = total_res.scalar() or 0

    # Paginate and order by newest first
    query = query.order_by(desc(Notification.created_at)).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    serialized = []
    for item in items:
        serialized.append({
            "id": item.id,
            "event_type": item.event_type,
            "claim_id": item.claim_id,
            "claim_number": item.claim_number,
            "recipient": item.recipient,
            "cc": item.cc,
            "bcc": item.bcc,
            "subject": item.subject,
            "provider": item.provider,
            "status": item.status,
            "error_message": item.error_message,
            "retry_count": item.retry_count,
            "created_at": item.created_at.isoformat() if item.created_at else "",
            "sent_at": item.sent_at.isoformat() if item.sent_at else None,
            "failed_at": item.failed_at.isoformat() if item.failed_at else None,
            "delivery_receipt": item.delivery_receipt,
            "details": item.details,
        })

    return {
        "items": serialized,
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": (total_count + page_size - 1) // page_size if total_count > 0 else 1,
    }


@router.get("/templates", response_model=list[dict[str, Any]])
async def get_notification_templates(db: AsyncSession = Depends(get_db)) -> list[dict[str, Any]]:
    """Get list of standard and custom notification templates with variable placeholders and parameter catalog."""
    # Query any custom DB overrides
    stmt = select(NotificationTemplate)
    res = await db.execute(stmt)
    db_templates = {item.event_type.upper(): item for item in res.scalars().all()}

    templates = []
    for event_key, default_tpl in TemplateRenderer.DEFAULT_TEMPLATES.items():
        custom = db_templates.get(event_key.upper())
        if custom:
            templates.append({
                "id": custom.id,
                "name": custom.name or default_tpl["name"],
                "event_type": event_key,
                "subject_template": custom.subject_template,
                "body_template_html": custom.body_template_html,
                "body_template_text": custom.body_template_text or "",
                "is_active": custom.is_active,
                "is_custom": True,
                "updated_at": custom.updated_at.isoformat() if custom.updated_at else (custom.created_at.isoformat() if custom.created_at else None),
                "available_variables": [p["token"] for p in PARAMETER_CATALOG],
                "parameter_catalog": PARAMETER_CATALOG,
            })
        else:
            templates.append({
                "id": event_key,
                "name": default_tpl["name"],
                "event_type": event_key,
                "subject_template": default_tpl["subject"],
                "body_template_html": default_tpl["body_html"],
                "body_template_text": default_tpl.get("body_text", ""),
                "is_active": True,
                "is_custom": False,
                "updated_at": None,
                "available_variables": [p["token"] for p in PARAMETER_CATALOG],
                "parameter_catalog": PARAMETER_CATALOG,
            })

    # Add any custom templates created in DB that aren't in default list
    for ev_key, custom in db_templates.items():
        if ev_key not in TemplateRenderer.DEFAULT_TEMPLATES:
            templates.append({
                "id": custom.id,
                "name": custom.name,
                "event_type": custom.event_type,
                "subject_template": custom.subject_template,
                "body_template_html": custom.body_template_html,
                "body_template_text": custom.body_template_text or "",
                "is_active": custom.is_active,
                "is_custom": True,
                "updated_at": custom.updated_at.isoformat() if custom.updated_at else None,
                "available_variables": [p["token"] for p in PARAMETER_CATALOG],
                "parameter_catalog": PARAMETER_CATALOG,
            })

    return templates


@router.get("/templates/tokens", response_model=list[dict[str, str]])
async def get_template_tokens() -> list[dict[str, str]]:
    """Retrieve full dynamic parameter palette and token selector catalog."""
    return PARAMETER_CATALOG


@router.put("/templates/{event_type}", response_model=dict[str, Any])
async def update_notification_template(
    event_type: str,
    payload: TemplateUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Save or update custom email template override for an event."""
    norm_key = event_type.upper().strip()
    stmt = select(NotificationTemplate).where(NotificationTemplate.event_type == norm_key)
    res = await db.execute(stmt)
    tpl = res.scalar_one_or_none()

    default_info = TemplateRenderer.DEFAULT_TEMPLATES.get(norm_key, {})
    name = payload.name or (tpl.name if tpl else default_info.get("name", norm_key))

    if tpl:
        tpl.name = name
        tpl.subject_template = payload.subject_template
        tpl.body_template_html = payload.body_template_html
        tpl.body_template_text = payload.body_template_text
        tpl.is_active = payload.is_active
        tpl.updated_at = datetime.now(UTC)
    else:
        tpl = NotificationTemplate(
            id=str(uuid.uuid4()),
            name=name,
            event_type=norm_key,
            subject_template=payload.subject_template,
            body_template_html=payload.body_template_html,
            body_template_text=payload.body_template_text,
            is_active=payload.is_active,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db.add(tpl)

    await db.commit()
    await db.refresh(tpl)
    logger.info(f"Persisted custom template for event '{norm_key}'")

    return {
        "id": tpl.id,
        "name": tpl.name,
        "event_type": tpl.event_type,
        "subject_template": tpl.subject_template,
        "body_template_html": tpl.body_template_html,
        "body_template_text": tpl.body_template_text or "",
        "is_active": tpl.is_active,
        "is_custom": True,
        "updated_at": tpl.updated_at.isoformat() if tpl.updated_at else None,
        "available_variables": [p["token"] for p in PARAMETER_CATALOG],
        "parameter_catalog": PARAMETER_CATALOG,
    }


@router.post("/templates/{event_type}/reset", response_model=dict[str, Any])
async def reset_notification_template(
    event_type: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Reset a notification template to its system default definition."""
    norm_key = event_type.upper().strip()
    stmt = select(NotificationTemplate).where(NotificationTemplate.event_type == norm_key)
    res = await db.execute(stmt)
    tpl = res.scalar_one_or_none()
    if tpl:
        await db.delete(tpl)
        await db.commit()
        logger.info(f"Reset custom template for event '{norm_key}' to default.")

    default_tpl = TemplateRenderer.get_template(norm_key)
    return {
        "id": norm_key,
        "name": default_tpl.get("name", norm_key),
        "event_type": norm_key,
        "subject_template": default_tpl["subject"],
        "body_template_html": default_tpl["body_html"],
        "body_template_text": default_tpl.get("body_text", ""),
        "is_active": True,
        "is_custom": False,
        "updated_at": None,
        "available_variables": [p["token"] for p in PARAMETER_CATALOG],
        "parameter_catalog": PARAMETER_CATALOG,
    }


@router.post("/templates/preview", response_model=TemplatePreviewResponse)
async def preview_template(
    payload: TemplatePreviewRequest,
    db: AsyncSession = Depends(get_db),
) -> TemplatePreviewResponse:
    """Render a dynamic template preview with sample mock context data or live custom draft strings."""
    sample_table = (
        '<table style="width: 100%; border-collapse: collapse; margin-top: 8px; border: 1px solid #cbd5e1; font-size: 12px;">'
        '<tr style="background-color: #f1f5f9; text-align: left;"><th style="padding: 6px 10px;">Case Number</th><th style="padding: 6px 10px;">Filing Date</th><th style="padding: 6px 10px;">Case Style</th><th style="padding: 6px 10px;">Status</th></tr>'
        '<tr style="border-top: 1px solid #e2e8f0;"><td style="padding: 6px 10px; font-family: monospace; font-weight: bold; color: #0284c7;">CACE-24-001234</td><td style="padding: 6px 10px;">03/15/2024</td><td style="padding: 6px 10px;">JOHNATHAN DOE vs AUTO INS CO</td><td style="padding: 6px 10px;"><span style="background: #dcfce7; color: #15803d; padding: 2px 6px; border-radius: 4px; font-size: 11px;">OPEN</span></td></tr>'
        '<tr style="border-top: 1px solid #e2e8f0;"><td style="padding: 6px 10px; font-family: monospace; font-weight: bold; color: #0284c7;">COCE-24-005678</td><td style="padding: 6px 10px;">05/20/2024</td><td style="padding: 6px 10px;">JANE SMITH vs JOHNATHAN DOE</td><td style="padding: 6px 10px;"><span style="background: #dcfce7; color: #15803d; padding: 2px 6px; border-radius: 4px; font-size: 11px;">PENDING</span></td></tr>'
        '</table>'
    )
    sample_context = {
        "claim_number": "0100456789",
        "exposure_number": "001",
        "activity_id": "ACT-77829-SAMPLE",
        "party_name": "JOHNATHAN DOE",
        "insured_name": "JOHNATHAN DOE",
        "claimant_name": "JANE SMITH",
        "matched_count": "2",
        "county_name": "Broward County",
        "portal_name": "Broward County Clerk",
        "matched_cases_table": sample_table,
        "error_message": "Connection refused by destination endpoint",
        "http_status": "502 Bad Gateway",
        "attempt_number": "1 of 3",
        "timestamp": "2026-09-05 16:30:00 UTC",
        "environment": "Development / Staging",
        "recipient": "priyer@test.com",
        "provider": "direct_mx",
        "custom_body": "This is an interactive verification email dispatched from the UAIC Claim & RPA Orchestrator.",
    }

    # Merge custom overrides
    if payload.sample_data:
        sample_context.update(payload.sample_data)
    if payload.context:
        sample_context.update(payload.context)

    # Resolve event type and base template
    ev_type = (payload.event_type or "GUIDEWIRE_ACTIVITY_CREATED").strip().upper()

    # Query DB for custom template override if not provided in payload draft
    stmt = select(NotificationTemplate).where(NotificationTemplate.event_type == ev_type)
    res = await db.execute(stmt)
    custom_tpl = res.scalar_one_or_none()
    default_tpl = TemplateRenderer.get_template(ev_type)

    subject_tpl = payload.subject_template or (custom_tpl.subject_template if custom_tpl else default_tpl["subject"])
    html_tpl = payload.body_template_html or payload.template_str or (custom_tpl.body_template_html if custom_tpl else default_tpl["body_html"])
    text_tpl = payload.body_template_text or (custom_tpl.body_template_text if custom_tpl and custom_tpl.body_template_text else default_tpl.get("body_text", ""))

    rendered_subject = TemplateRenderer.render(subject_tpl, sample_context)
    rendered_html = TemplateRenderer.render(html_tpl, sample_context, escape_html=False)
    rendered_text = TemplateRenderer.render(text_tpl, sample_context)

    return TemplatePreviewResponse(
        event_type=ev_type,
        subject=rendered_subject,
        body_html=rendered_html,
        body_text=rendered_text,
        rendered_content=rendered_html,
    )


@router.get("/templates/{template_id}/preview", response_model=TemplatePreviewResponse)
async def get_template_preview_by_id(
    template_id: str,
    db: AsyncSession = Depends(get_db),
) -> TemplatePreviewResponse:
    """GET dynamic preview for a template by ID or event type."""
    req = TemplatePreviewRequest(event_type=template_id)
    return await preview_template(req, db=db)


@router.get("/rules", response_model=dict[str, bool])
async def get_notification_rules() -> dict[str, bool]:
    """Retrieve the per-event notification trigger enablement rules."""
    sys_settings = await get_system_settings_async()
    return sys_settings.email.rules


@router.put("/rules", response_model=dict[str, bool])
async def update_notification_rules(rules: dict[str, bool]) -> dict[str, bool]:
    """Update event notification trigger rules and persist in settings."""
    sys_settings = await get_system_settings_async()
    sys_settings.email.rules.update(rules)
    await save_system_settings_async(sys_settings)
    logger.info(f"Updated notification rules: {sys_settings.email.rules}")
    return sys_settings.email.rules


@router.get("/{notification_id}", response_model=dict[str, Any])
async def get_notification_detail(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve full detail, delivery receipt, and HTML payload of a specific notification."""
    stmt = select(Notification).where(Notification.id == notification_id)
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Notification not found")

    return {
        "id": item.id,
        "event_type": item.event_type,
        "claim_id": item.claim_id,
        "claim_number": item.claim_number,
        "recipient": item.recipient,
        "cc": item.cc,
        "bcc": item.bcc,
        "subject": item.subject,
        "body_html": item.body_html,
        "body_text": item.body_text,
        "provider": item.provider,
        "status": item.status,
        "idempotency_key": item.idempotency_key,
        "error_message": item.error_message,
        "retry_count": item.retry_count,
        "created_at": item.created_at.isoformat() if item.created_at else "",
        "queued_at": item.queued_at.isoformat() if item.queued_at else None,
        "sent_at": item.sent_at.isoformat() if item.sent_at else None,
        "failed_at": item.failed_at.isoformat() if item.failed_at else None,
        "delivery_receipt": item.delivery_receipt,
        "details": item.details,
    }
