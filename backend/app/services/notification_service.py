"""Central Notification Orchestrator: rule checking, idempotency, template rendering, and Celery queue dispatch."""

import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.celery_app import celery_app
from app.models.notification import Notification, NotificationTemplate
from app.services.email_service import TemplateRenderer
from app.services.settings_service import get_system_settings_async

logger = logging.getLogger("uaic_orchestrator.notification_service")


class NotificationService:
    """Orchestrates notification dispatch across all system events with master toggle and rule guards."""

    @classmethod
    async def emit_event(
        cls,
        db: AsyncSession,
        event_type: str,
        context: dict[str, Any],
        claim_id: str | None = None,
        claim_number: str | None = None,
        idempotency_key: str | None = None,
        override_recipient: str | None = None,
        override_provider: str | None = None,
    ) -> Notification | None:
        """
        Emits an application notification event:
        1. Checks Master ON/OFF Switch (email_notifications_enabled).
        2. Checks Per-Event Notification Rule.
        3. Validates Idempotency (prevent duplicate emails on retries).
        4. Renders dynamic subject and HTML body.
        5. Persists Notification record.
        6. Enqueues Celery task on the 'notifications' queue.
        """
        sys_settings = await get_system_settings_async()
        email_settings = sys_settings.email

        # 1. Master Toggle Guard (User Requirement)
        if not email_settings.email_notifications_enabled and event_type != "TEST_EMAIL":
            logger.info(f"[NotificationService] Notification engine is DISABLED globally. Skipping event: {event_type}")
            return None

        # 2. Granular Event Rule Guard
        rule_key = event_type.lower()
        # Normalize rule key
        if "guidewire_activity_created" in rule_key:
            rule_enabled = email_settings.rules.get("guidewire_activity_created", True)
        elif "guidewire" in rule_key and "fail" in rule_key:
            rule_enabled = email_settings.rules.get("guidewire_activity_failed", True)
        elif "scraper" in rule_key:
            rule_enabled = email_settings.rules.get("scraper_failed", True)
        elif "claim" in rule_key and "fail" in rule_key:
            rule_enabled = email_settings.rules.get("claim_failed", True)
        else:
            rule_enabled = email_settings.rules.get(rule_key, True)

        if not rule_enabled and event_type != "TEST_EMAIL":
            logger.info(f"[NotificationService] Rule for event '{event_type}' is DISABLED. Skipping.")
            return None

        # 3. Idempotency Check
        if idempotency_key:
            stmt = select(Notification).where(Notification.idempotency_key == idempotency_key)
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                if existing.status in ["SENT", "QUEUED", "SENDING"]:
                    logger.info(f"[NotificationService] Idempotency match: {idempotency_key} already in status '{existing.status}'. Skipping duplicate.")
                    return existing

        # 4. Resolve Recipients
        recipients = [override_recipient] if override_recipient else email_settings.to_recipients
        if not recipients:
            recipients = [sys_settings.integration.notification_email or "claims-ops@test.com"]
        to_str = ", ".join([r.strip() for r in recipients if r.strip()])
        cc_str = ", ".join(email_settings.cc_recipients) if email_settings.cc_recipients else None
        bcc_str = ", ".join(email_settings.bcc_recipients) if email_settings.bcc_recipients else None

        # 5. Render Subject & Body from Template or Default
        selected_provider = override_provider or email_settings.provider
        subject_template = None
        body_html_template = None
        body_text_template = None
        try:
            norm_event = event_type.upper().strip()
            stmt = select(NotificationTemplate).where(
                NotificationTemplate.event_type == norm_event,
                NotificationTemplate.is_active.is_(True),
            )
            res = await db.execute(stmt)
            custom_tpl = res.scalar_one_or_none()
            if custom_tpl:
                subject_template = custom_tpl.subject_template
                body_html_template = custom_tpl.body_template_html
                body_text_template = custom_tpl.body_template_text or ""
        except Exception as e:
            logger.warning(f"[NotificationService] Failed checking custom template for {event_type}: {e}")

        if not subject_template or not body_html_template:
            tpl = TemplateRenderer.get_template(event_type)
            subject_template = subject_template or tpl["subject"]
            body_html_template = body_html_template or tpl["body_html"]
            body_text_template = body_text_template if body_text_template is not None else tpl.get("body_text", "")

        # Augment context with standard dynamic variables
        context.setdefault("timestamp", datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC"))
        context.setdefault("environment", "Production" if not sys_settings.integration.guidewire_mock_mode else "Development / Mock")
        context.setdefault("claim_number", claim_number or context.get("claim_number", "N/A"))
        context.setdefault("provider", selected_provider)
        context.setdefault("recipient", to_str)

        rendered_subject = TemplateRenderer.render(subject_template, context)
        rendered_html = TemplateRenderer.render(body_html_template, context)
        rendered_text = TemplateRenderer.render(body_text_template, context)

        # 6. Create Notification Record in DB
        notification = Notification(
            event_type=event_type,
            claim_id=claim_id,
            claim_number=claim_number,
            recipient=to_str,
            cc=cc_str,
            bcc=bcc_str,
            subject=rendered_subject,
            body_html=rendered_html,
            body_text=rendered_text,
            provider=selected_provider,
            status="QUEUED",
            idempotency_key=idempotency_key,
            queued_at=datetime.now(UTC),
            details=context,
        )
        db.add(notification)
        await db.commit()
        await db.refresh(notification)

        # 7. Enqueue Async Celery Task
        try:
            celery_app.send_task(
                "app.tasks.notification_tasks.send_notification_email_task",
                args=[notification.id],
                queue="notifications",
            )
            logger.info(f"[NotificationService] Dispatched notification {notification.id} to Celery 'notifications' queue.")
        except Exception as e:
            logger.error(f"[NotificationService] Failed to enqueue Celery notification task: {e}")
            notification.status = "FAILED"
            notification.error_message = f"Queue error: {e}"
            notification.failed_at = datetime.now(UTC)
            await db.commit()

        return notification
