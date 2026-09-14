from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.notification_service import NotificationService


@pytest.fixture
def mock_db_session():
    return AsyncMock(spec=AsyncSession)

@pytest.mark.asyncio
@patch("app.services.notification_service.get_system_settings_async")
@patch("app.services.notification_service.celery_app")
async def test_digest_mode_holds_notification_as_pending(
    mock_celery_app,
    mock_get_settings,
    mock_db_session
):
    mock_settings = AsyncMock()
    mock_settings.email.digest_mode = "daily_digest"
    mock_settings.email.email_notifications_enabled = True
    mock_settings.email.rules = {"guidewire_activity_created": True}
    mock_settings.email.to_recipients = ["test@example.com"]
    mock_settings.email.provider = "local_mock"
    mock_settings.integration.guidewire_mock_mode = True
    mock_get_settings.return_value = mock_settings

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    context = {"claim_number": "123456789"}
    
    notification = await NotificationService.emit_event(
        db=mock_db_session,
        event_type="GUIDEWIRE_ACTIVITY_CREATED",
        context=context,
        idempotency_key="test_key_digest"
    )

    assert notification is not None
    assert notification.status == "PENDING_DIGEST"
    mock_celery_app.send_task.assert_not_called()
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called()

@pytest.mark.asyncio
@patch("app.services.notification_service.get_system_settings_async")
@patch("app.services.notification_service.celery_app")
async def test_immediate_mode_queues_notification(
    mock_celery_app,
    mock_get_settings,
    mock_db_session
):
    mock_settings = AsyncMock()
    mock_settings.email.digest_mode = "immediate"
    mock_settings.email.email_notifications_enabled = True
    mock_settings.email.rules = {"guidewire_activity_created": True}
    mock_settings.email.to_recipients = ["test@example.com"]
    mock_settings.email.provider = "local_mock"
    mock_settings.integration.guidewire_mock_mode = True
    mock_get_settings.return_value = mock_settings

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    context = {"claim_number": "987654321"}
    
    notification = await NotificationService.emit_event(
        db=mock_db_session,
        event_type="GUIDEWIRE_ACTIVITY_CREATED",
        context=context,
        idempotency_key="test_key_immediate"
    )

    assert notification is not None
    assert notification.status == "QUEUED"
    mock_celery_app.send_task.assert_called_once()
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called()
