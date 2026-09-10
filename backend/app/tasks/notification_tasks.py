"""Celery tasks for asynchronous email notification delivery on dedicated 'notifications' queue."""

import asyncio
import logging
from datetime import UTC, datetime

from sqlalchemy import select

from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.notification import Notification
from app.services.email_service import get_email_provider
from app.services.settings_service import get_system_settings_async

logger = logging.getLogger("uaic_orchestrator.tasks.notification")


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
                notification.sent_at = datetime.now(UTC)
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
                notification.failed_at = datetime.now(UTC)
                notification.error_message = result.error or "Unknown delivery failure"
                if result.delivery_receipt:
                    notification.delivery_receipt = result.delivery_receipt
                await db.commit()
                logger.error(f"[NotificationTask] Notification {notification_id} FAILED: {result.error}")
                return {"success": False, "status": "FAILED", "error": result.error}

        except Exception as e:
            notification.status = "FAILED"
            notification.failed_at = datetime.now(UTC)
            notification.error_message = str(e)
            await db.commit()
            logger.error(f"[NotificationTask] Exception delivering notification {notification_id}: {e}")
            return {"success": False, "status": "FAILED", "error": str(e)}


@celery_app.task(
    bind=True,
    name="app.tasks.notification_tasks.send_notification_email_task",
    max_retries=3,
    default_retry_delay=30,
)
def send_notification_email_task(self, notification_id: str) -> dict[str, str | bool]:
    """Celery task running on 'notifications' queue to deliver email messages."""
    logger.info(f"[Celery:notifications] Processing delivery for notification: {notification_id}")
    try:
        return asyncio.run(_execute_notification_delivery(notification_id))
    except Exception as exc:
        logger.error(f"[Celery:notifications] Task failed with unhandled exception: {exc}")
        raise self.retry(exc=exc)
