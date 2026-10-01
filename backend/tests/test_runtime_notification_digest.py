"""Database-backed verification that digest settings dispatch complete periods."""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models.notification import Notification
from app.tasks import notification_tasks


@pytest.mark.asyncio
async def test_hourly_digest_groups_prior_hour_and_retains_current_hour(tmp_path, monkeypatch):
    engine = create_async_engine(f"sqlite+aiosqlite:///{(tmp_path / 'digest.db').as_posix()}")
    async with engine.begin() as conn:
        await conn.run_sync(Notification.__table__.create)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(notification_tasks, "AsyncSessionLocal", session_factory)
    monkeypatch.setattr(
        notification_tasks,
        "get_system_settings_async",
        lambda: _settings(),
    )
    sent = MagicMock()
    monkeypatch.setattr(notification_tasks.celery_app, "send_task", sent)

    current_hour = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
    async with session_factory() as db:
        for subject, created in (
            ("Earlier case A", current_hour - timedelta(minutes=50)),
            ("Earlier case B", current_hour - timedelta(minutes=20)),
            ("Current case", current_hour + timedelta(minutes=1)),
        ):
            db.add(Notification(
                event_type="SCRAPER_FAILED",
                recipient="ops@example.test",
                subject=subject,
                body_html="<p>Update</p>",
                body_text="Update",
                provider="local_mock",
                status="PENDING_DIGEST",
                created_at=created,
            ))
        await db.commit()

    try:
        assert await notification_tasks._dispatch_due_digests() == 1
        async with session_factory() as db:
            notifications = list((await db.execute(select(Notification))).scalars().all())
        statuses = {item.subject: item.status for item in notifications}
        assert statuses["Earlier case A"] == "DIGESTED"
        assert statuses["Earlier case B"] == "DIGESTED"
        assert statuses["Current case"] == "PENDING_DIGEST"
        digest = next(item for item in notifications if item.event_type == "DIGEST")
        assert digest.status == "QUEUED"
        assert "Earlier case A" in digest.body_text
        assert "Earlier case B" in digest.body_text
        assert "Current case" not in digest.body_text
        sent.assert_called_once()
        assert sent.call_args.args[0] == "app.tasks.notification_tasks.send_notification_email_task"
        assert sent.call_args.kwargs["args"] == [digest.id]
    finally:
        await engine.dispose()


async def _settings():
    return SimpleNamespace(email=SimpleNamespace(
        email_notifications_enabled=True,
        digest_mode="hourly_digest",
    ))
