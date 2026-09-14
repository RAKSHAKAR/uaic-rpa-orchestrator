from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.services.notification_service import NotificationService
from app.tasks.notification_tasks import _execute_notification_delivery


@pytest.fixture
def mock_db_session():
    return AsyncMock(spec=AsyncSession)

@pytest.mark.asyncio
@patch("app.services.notification_service.get_system_settings_async")
@patch("app.services.notification_service.celery_app")
async def test_idempotency_prevents_duplicate_dispatch(
    mock_celery_app,
    mock_get_settings,
    mock_db_session
):
    mock_settings = AsyncMock()
    mock_settings.email.email_notifications_enabled = True
    mock_settings.email.rules = {"guidewire_activity_created": True}
    mock_get_settings.return_value = mock_settings

    # Mock DB to return an existing QUEUED notification for the same idempotency key
    existing_notification = Notification(
        id="existing_id",
        status="QUEUED",
        idempotency_key="GUIDEWIRE_ACTIVITY_CREATED:123:456"
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_notification
    mock_db_session.execute.return_value = mock_result

    notification = await NotificationService.emit_event(
        db=mock_db_session,
        event_type="GUIDEWIRE_ACTIVITY_CREATED",
        context={"claim_id": "123", "activity_id": "456"},
        idempotency_key="GUIDEWIRE_ACTIVITY_CREATED:123:456"
    )

    assert notification is not None
    assert notification.id == "existing_id"
    
    # Assert DB was not modified
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()
    
    # Assert Celery task was not re-sent
    mock_celery_app.send_task.assert_not_called()

@pytest.mark.asyncio
@patch("app.tasks.notification_tasks.get_email_provider")
@patch("app.tasks.notification_tasks.get_system_settings_async")
@patch("app.tasks.notification_tasks.AsyncSessionLocal")
async def test_notification_retry_failure_records_error(
    mock_session_local,
    mock_get_settings,
    mock_get_provider
):
    mock_db = AsyncMock()
    mock_session_local.return_value.__aenter__.return_value = mock_db
    
    # Mock settings
    mock_settings = AsyncMock()
    mock_settings.email.email_notifications_enabled = True
    mock_settings.email.from_name = "System"
    mock_settings.email.from_email = "test@test.com"
    mock_settings.email.reply_to = ""
    mock_get_settings.return_value = mock_settings
    
    # Mock Notification
    notification = Notification(
        id="notif_123",
        status="QUEUED",
        recipient="test@example.com",
        cc="",
        bcc="",
        subject="Test",
        body_html="<p>Test</p>",
        body_text="Test",
        provider="smtp"
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = notification
    mock_db.execute.return_value = mock_result
    
    # Mock Email Provider to FAIL
    mock_provider = MagicMock()
    mock_provider_result = MagicMock()
    mock_provider_result.success = False
    mock_provider_result.error = "SMTP Connection Timeout"
    mock_provider.send_email.return_value = mock_provider_result
    mock_get_provider.return_value = mock_provider
    
    result = await _execute_notification_delivery("notif_123")
    
    assert result["success"] is False
    assert result["status"] == "FAILED"
    assert result["error"] == "SMTP Connection Timeout"
    
    assert notification.status == "FAILED"
    assert notification.error_message == "SMTP Connection Timeout"
    assert notification.failed_at is not None
    mock_db.commit.assert_called()
