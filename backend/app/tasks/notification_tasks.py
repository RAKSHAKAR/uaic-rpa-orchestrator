"""Celery tasks for asynchronous email notification delivery on dedicated 'notifications' queue."""

import asyncio
import html
import logging
from collections import defaultdict
from datetime import datetime

from sqlalchemy import select

from app.compat import utc_now
from app.core.celery_app import celery_app
from app.core.database import TaskAsyncSessionLocal

# Module-level alias used by all internal functions.
# Tests monkeypatch `notification_tasks.AsyncSessionLocal` to inject an in-memory
# session factory — this alias is the single patchable reference point.
AsyncSessionLocal = TaskAsyncSessionLocal

from app.models.notification import Notification
from app.services.email_service import get_email_provider
from app.services.settings_service import get_system_settings_async, get_system_settings_sync

logger = logging.getLogger("uaic_orchestrator.tasks.notification")


async def _mark_notification_retry(notification_id: str, retry_count: int) -> None:
    async with AsyncSessionLocal() as db:
        notification = await db.get(Notification, notification_id)
        if notification:
            notification.status = "RETRYING"
            notification.retry_count = retry_count
            await db.commit()


def _digest_cutoff(now: datetime, mode: str) -> datetime:
    """Return the latest completed wall-clock digest period in UTC."""
    if mode == "hourly_digest":
        return now.replace(minute=0, second=0, microsecond=0)
    if mode == "daily_digest":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    return now


async def _dispatch_due_digests() -> int:
    """Combine pending notifications at the configured UTC digest boundary."""
    email_cfg = (await get_system_settings_async()).email
    if not email_cfg.email_notifications_enabled:
        return 0
    cutoff = _digest_cutoff(utc_now(), email_cfg.digest_mode)
    async with AsyncSessionLocal() as db:
        stmt = (
            select(Notification)
            .where(Notification.status == "PENDING_DIGEST", Notification.created_at < cutoff)
            .order_by(Notification.created_at.asc())
            .with_for_update(skip_locked=True)
        )
        rows = list((await db.execute(stmt)).scalars().all())
        groups = defaultdict(list)
        for row in rows:
            groups[(row.recipient, row.cc, row.bcc, row.provider)].append(row)

        digest_ids = []
        for (recipient, cc, bcc, provider), items in groups.items():
            subject = f"UAIC claim activity digest ({len(items)} updates)"
            plain_items = [f"{item.subject}\n{item.body_text or ''}" for item in items]
            body_text = "\n\n".join(plain_items)
            body_html = "<h1>Claim activity digest</h1>" + "".join(
                f"<section><h2>{html.escape(item.subject)}</h2><pre>{html.escape(item.body_text or '')}</pre></section>"
                for item in items
            )
            digest = Notification(
                event_type="DIGEST",
                recipient=recipient,
                cc=cc,
                bcc=bcc,
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                provider=provider,
                status="QUEUED",
                queued_at=utc_now(),
                details={"source_notification_ids": [item.id for item in items]},
            )
            db.add(digest)
            await db.flush()
            digest_ids.append(digest.id)
            for item in items:
                item.status = "DIGESTED"
                item.details = {**(item.details or {}), "digest_notification_id": digest.id}
        await db.commit()

    for digest_id in digest_ids:
        try:
            celery_app.send_task(
                "app.tasks.notification_tasks.send_notification_email_task",
                args=[digest_id],
                queue="notifications",
                retry=False,
            )
        except Exception:
            logger.exception("Failed to enqueue digest %s", digest_id)
            async with AsyncSessionLocal() as db:
                digest = await db.get(Notification, digest_id)
                if digest:
                    digest.status = "FAILED"
                    digest.error_message = "Digest queue dispatch failed"
                    source_ids = (digest.details or {}).get("source_notification_ids", [])
                    if source_ids:
                        sources = list((await db.execute(
                            select(Notification).where(Notification.id.in_(source_ids))
                        )).scalars().all())
                        for source in sources:
                            source.status = "PENDING_DIGEST"
                    await db.commit()
    return len(digest_ids)


@celery_app.task(name="app.tasks.notification_tasks.dispatch_due_digests_task")
def dispatch_due_digests_task() -> int:
    return asyncio.run(_dispatch_due_digests())


async def _execute_notification_delivery(notification_id: str) -> dict[str, str | bool]:
    """Execute asynchronous email delivery and update database delivery status."""
    async with AsyncSessionLocal() as db:
        stmt = select(Notification).where(Notification.id == notification_id)
        res = await db.execute(stmt)
        notification = res.scalar_one_or_none()

        if not notification:
            logger.warning(f"[NotificationTask] Notification {notification_id} not found in database.")
            return {"success": False, "error": "Notification record not found"}

        sys_settings = await get_system_settings_async()
        email_settings = sys_settings.email

        # Master Toggle Guard
        if not email_settings.email_notifications_enabled:
            notification.status = "SKIPPED"
            notification.error_message = "Notification Engine is disabled globally."
            await db.commit()
            logger.info(f"[NotificationTask] Notification {notification_id} marked as SKIPPED (master switch is OFF).")
            return {"success": True, "status": "SKIPPED"}

        notification.status = "SENDING"
        await db.commit()

        # Parse recipients
        to_list = [r.strip() for r in notification.recipient.split(",") if r.strip()]
        cc_list = [c.strip() for c in notification.cc.split(",") if c.strip()] if notification.cc else []
        bcc_list = [b.strip() for b in notification.bcc.split(",") if b.strip()] if notification.bcc else []

        provider = get_email_provider(email_settings, override_provider=notification.provider)

        try:
            result = provider.send_email(
                to_addresses=to_list,
                subject=notification.subject,
                body_html=notification.body_html,
                body_text=notification.body_text,
                cc_addresses=cc_list,
                bcc_addresses=bcc_list,
                from_name=email_settings.from_name,
                from_email=email_settings.from_email,
                reply_to=email_settings.reply_to,
            )

            if result.success:
                notification.status = "SENT"
                notification.sent_at = utc_now()
                notification.error_message = None
                if result.delivery_receipt:
                    notification.delivery_receipt = result.delivery_receipt
                    current_details = dict(notification.details or {})
                    current_details["delivery_receipt"] = result.delivery_receipt
                    notification.details = current_details
                await db.commit()
                logger.info(f"[NotificationTask] Notification {notification_id} SENT successfully via {result.provider} in {result.duration_ms:.1f}ms.")
                return {"success": True, "status": "SENT"}
            else:
                notification.status = "FAILED"
                notification.failed_at = utc_now()
                notification.error_message = result.error or "Unknown delivery failure"
                if result.delivery_receipt:
                    notification.delivery_receipt = result.delivery_receipt
                await db.commit()
                logger.error(f"[NotificationTask] Notification {notification_id} FAILED: {result.error}")
                return {"success": False, "status": "FAILED", "error": result.error}

        except Exception as e:
            notification.status = "FAILED"
            notification.failed_at = utc_now()
            notification.error_message = str(e)
            await db.commit()
            logger.error(f"[NotificationTask] Exception delivering notification {notification_id}: {e}")
            return {"success": False, "status": "FAILED", "error": str(e)}


@celery_app.task(
    bind=True,
    name="app.tasks.notification_tasks.send_notification_email_task",
)
def send_notification_email_task(self, notification_id: str) -> dict[str, str | bool]:
    """Celery task running on 'notifications' queue to deliver email messages."""
    logger.info(f"[Celery:notifications] Processing delivery for notification: {notification_id}")
    email_cfg = get_system_settings_sync().email
    try:
        result = asyncio.run(_execute_notification_delivery(notification_id))
        if result["success"] or result.get("status") != "FAILED":
            return result
        error = RuntimeError(str(result.get("error") or "Email delivery failed"))
    except Exception as exc:
        logger.error("[Celery:notifications] Delivery attempt failed: %s", exc)
        error = exc
    if self.request.retries >= email_cfg.retry_count:
        return {"success": False, "status": "FAILED", "error": str(error)}
    asyncio.run(_mark_notification_retry(notification_id, self.request.retries + 1))
    raise self.retry(
        exc=error,
        countdown=email_cfg.retry_delay_seconds,
        max_retries=email_cfg.retry_count,
    )
