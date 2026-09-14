from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import NotificationTemplate
from app.services.notification_service import NotificationService


@pytest.fixture
def mock_db_session():
    return AsyncMock(spec=AsyncSession)

@pytest.mark.asyncio
@patch("app.services.notification_service.get_system_settings_async")
@patch("app.services.notification_service.celery_app")
async def test_end_to_end_notification_rendering(
    mock_celery_app,
    mock_get_settings,
    mock_db_session
):
    mock_settings = AsyncMock()
    mock_settings.email.email_notifications_enabled = True
    mock_settings.email.digest_mode = "immediate"
    mock_settings.email.rules = {"guidewire_activity_created": True}
    mock_settings.email.to_recipients = ["test@example.com"]
    mock_settings.integration.guidewire_mock_mode = False
    mock_get_settings.return_value = mock_settings

    # Mock DB execute to return NO idempotency match but YES a custom template
    def mock_db_execute(stmt):
        mock_result = MagicMock()
        stmt_str = str(stmt).lower()
        if "notificationtemplate" in stmt_str or "notification_template" in stmt_str:
            template = NotificationTemplate(
                event_type="GUIDEWIRE_ACTIVITY_CREATED",
                subject_template="Action Required: {{claim_number}}",
                body_template_html="<p>Claim: {{claim_number}}, Activity: {{activity_id}}</p>",
                is_active=True
            )
            mock_result.scalar_one_or_none.return_value = template
        else:
            mock_result.scalar_one_or_none.return_value = None
        return mock_result

    mock_db_session.execute.side_effect = mock_db_execute

    context = {
        "claim_number": "CLM-999",
        "activity_id": "ACT-123"
    }
    
    notification = await NotificationService.emit_event(
        db=mock_db_session,
        event_type="GUIDEWIRE_ACTIVITY_CREATED",
        context=context,
        idempotency_key="unique_123"
    )

    assert notification is not None
    assert notification.subject == "Action Required: CLM-999"
    assert notification.body_html == "<p>Claim: CLM-999, Activity: ACT-123</p>"
    assert notification.status == "QUEUED"
    
    # Assert DB commit was called
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called()
    
    # Assert Celery task was sent
    mock_celery_app.send_task.assert_called_once()
