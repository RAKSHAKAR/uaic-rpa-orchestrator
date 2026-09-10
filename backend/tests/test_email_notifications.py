"""Unit and integration tests for the Email & Notification Engine."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import AsyncSessionLocal
from app.main import app
from app.services.email_service import (
    MockEmailProvider,
    TemplateRenderer,
)
from app.services.notification_service import NotificationService
from app.services.settings_service import get_system_settings_async, save_system_settings_async


@pytest.mark.asyncio
async def test_mock_email_provider_dispatch():
    """Verify MockEmailProvider records dispatched emails and connection test succeeds."""
    provider = MockEmailProvider()
    MockEmailProvider.sent_emails.clear()

    # Test connection
    conn_res = provider.test_connection()
    assert conn_res.success is True
    assert conn_res.provider == "local_mock"
    assert conn_res.latency_ms > 0

    # Test sending email
    res = provider.send_email(
        to_addresses=["operator@test.com"],
        subject="Test Claim Update",
        body_html="<p>Test Content</p>",
        body_text="Test Content",
    )
    assert res.success is True
    assert res.provider == "local_mock"
    assert len(MockEmailProvider.sent_emails) == 1
    assert MockEmailProvider.sent_emails[0]["to"] == ["operator@test.com"]
    assert MockEmailProvider.sent_emails[0]["subject"] == "Test Claim Update"


@pytest.mark.asyncio
async def test_template_renderer_variable_substitution():
    """Verify TemplateRenderer substitutes dynamic variables accurately."""
    template = "Claim {{claim_number}} - Activity {{activity_id}} for {{party_name}}"
    context = {
        "claim_number": "0100998877",
        "activity_id": "ACT-887766",
        "party_name": "JANE DOE",
    }
    rendered = TemplateRenderer.render(template, context)
    assert rendered == "Claim 0100998877 - Activity ACT-887766 for JANE DOE"

    # Missing variable should be empty string
    partial_context = {"claim_number": "0100998877"}
    rendered_partial = TemplateRenderer.render(template, partial_context)
    assert rendered_partial == "Claim 0100998877 - Activity  for "


@pytest.mark.asyncio
@pytest.mark.requires_redis
async def test_notification_service_master_switch():
    """Verify that when the Master Notification Toggle is disabled, no notifications are emitted."""
    sys_settings = await get_system_settings_async()
    original_state = sys_settings.email.email_notifications_enabled

    try:
        # Disable master toggle
        sys_settings.email.email_notifications_enabled = False
        await save_system_settings_async(sys_settings)

        async with AsyncSessionLocal() as db:
            result = await NotificationService.emit_event(
                db=db,
                event_type="GUIDEWIRE_ACTIVITY_CREATED",
                context={"claim_number": "0100000001"},
            )
            assert result is None, "Expected notification to be skipped when master switch is OFF"

        # Re-enable master toggle
        sys_settings.email.email_notifications_enabled = True
        sys_settings.email.provider = "local_mock"
        await save_system_settings_async(sys_settings)

        async with AsyncSessionLocal() as db:
            result_enabled = await NotificationService.emit_event(
                db=db,
                event_type="GUIDEWIRE_ACTIVITY_CREATED",
                context={"claim_number": "0100000001", "exposure_number": "001", "activity_id": "ACT-123", "party_name": "JOHN DOE", "matched_count": 1},
                idempotency_key="TEST:MASTER:TOGGLE:1",
            )
            assert result_enabled is not None
            assert result_enabled.status in ["QUEUED", "SENT"]
            assert result_enabled.idempotency_key == "TEST:MASTER:TOGGLE:1"

    finally:
        sys_settings.email.email_notifications_enabled = original_state
        await save_system_settings_async(sys_settings)


@pytest.mark.asyncio
@pytest.mark.requires_redis
async def test_notification_service_idempotency():
    """Verify that duplicate events with the same idempotency key are skipped."""
    sys_settings = await get_system_settings_async()
    sys_settings.email.email_notifications_enabled = True
    sys_settings.email.provider = "local_mock"
    await save_system_settings_async(sys_settings)

    test_key = "IDEMPOTENT:TEST:EVENT:999"

    async with AsyncSessionLocal() as db:
        first = await NotificationService.emit_event(
            db=db,
            event_type="GUIDEWIRE_ACTIVITY_CREATED",
            context={"claim_number": "0100999999", "exposure_number": "001", "activity_id": "ACT-999", "party_name": "ALICE SMITH", "matched_count": 1},
            idempotency_key=test_key,
        )
        assert first is not None

        # Second emission with same key
        second = await NotificationService.emit_event(
            db=db,
            event_type="GUIDEWIRE_ACTIVITY_CREATED",
            context={"claim_number": "0100999999", "exposure_number": "001", "activity_id": "ACT-999", "party_name": "ALICE SMITH", "matched_count": 1},
            idempotency_key=test_key,
        )
        assert second is not None
        assert first.id == second.id, "Second call must return the existing notification without creating a new record"


@pytest.mark.asyncio
async def test_email_test_connection_api():
    """Verify POST /api/v1/settings/email/test-connection endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post(
            "/api/v1/settings/email/test-connection",
            json={"provider": "local_mock"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["provider"] == "local_mock"
        assert data["duration_ms"] >= 0


@pytest.mark.asyncio
@pytest.mark.requires_redis
async def test_email_test_send_api():
    """Verify POST /api/v1/settings/email/test-send endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post(
            "/api/v1/settings/email/test-send",
            json={"recipient": "test-operator@test.com", "subject": "Automated Unit Test Email"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["recipient"] == "test-operator@test.com"
        assert len(data["notification_id"]) > 0


@pytest.mark.asyncio
async def test_notifications_history_api():
    """Verify GET /api/v1/notifications paginated listing."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/v1/notifications?page=1&page_size=10")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_notification_templates_and_rules_api():
    """Verify templates preview and rules endpoints."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Templates listing
        tpl_resp = await ac.get("/api/v1/notifications/templates")
        assert tpl_resp.status_code == 200
        templates = tpl_resp.json()
        assert len(templates) >= 3

        # Preview template
        prev_resp = await ac.post(
            "/api/v1/notifications/templates/preview",
            json={
                "template_str": "Test for Claim {{claim_number}}",
                "context": {"claim_number": "0100777777"},
            },
        )
        assert prev_resp.status_code == 200
        assert prev_resp.json()["rendered_content"] == "Test for Claim 0100777777"

        # Rules listing
        rules_resp = await ac.get("/api/v1/notifications/rules")
        assert rules_resp.status_code == 200
        assert "guidewire_activity_created" in rules_resp.json()


@pytest.mark.asyncio
async def test_email_connection_direct_mx_automated():
    """Verify Direct MX gateway reachability test for corporate domain damcogroup.com."""
    from app.services.email_service import DirectMxEmailProvider

    provider = DirectMxEmailProvider()
    result = provider.test_connection(domain="damcogroup.com")
    assert result.success is True
    assert result.provider == "direct_mx"
    assert "damcogroup-com.mail.protection.outlook.com" in result.message
    assert result.latency_ms > 0

    # Test via API endpoint
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post(
            "/api/v1/settings/email/test-connection",
            json={"provider": "direct_mx", "recipient_domain": "damcogroup.com"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["provider"] == "direct_mx"
        assert "damcogroup-com.mail.protection.outlook.com" in data["message"]


@pytest.mark.asyncio
async def test_preview_all_four_templates_automated():
    """Verify Dynamic Template Previewer endpoint renders all 4 template types with sample tokens."""
    event_types = [
        "guidewire_activity_created",
        "guidewire_activity_failed",
        "scraper_failed",
        "test_email",
    ]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        for ev in event_types:
            # Test POST preview
            resp = await ac.post(
                "/api/v1/notifications/templates/preview",
                json={
                    "event_type": ev,
                    "sample_data": {
                        "claim_number": "0100987654",
                        "insured_name": "JOHN DOE",
                        "claimant_name": "JANE SMITH",
                        "activity_id": "ACT-77192",
                        "portal_name": "Broward County Clerk",
                    },
                },
            )
            assert resp.status_code == 200, f"Failed previewing {ev}"
            data = resp.json()
            assert data["event_type"].lower() == ev.lower()
            assert len(data["subject"]) > 0
            assert len(data["body_html"]) > 0
            assert "<html" in data["body_html"].lower() or "<div" in data["body_html"].lower()
            assert len(data["rendered_content"]) > 0

            # Test GET preview by template ID
            get_resp = await ac.get(f"/api/v1/notifications/templates/{ev}/preview")
            assert get_resp.status_code == 200
            get_data = get_resp.json()
            assert get_data["event_type"].lower() == ev.lower()
            assert len(get_data["subject"]) > 0


@pytest.mark.asyncio
async def test_send_email_delivery_receipt_mock_automated():
    """Verify delivery receipt structure, RFC headers, and persistence in DB via Mock provider."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post(
            "/api/v1/settings/email/test-send",
            json={
                "recipient": "priyer@test.com",
                "subject": "Automated Mock Receipt Test",
                "body": "Verifying delivery receipt metadata storage.",
                "provider": "local_mock",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        notif_id = data["notification_id"]

        # Execute asynchronous delivery handler synchronously for test
        from app.tasks.notification_tasks import _execute_notification_delivery
        exec_res = await _execute_notification_delivery(notif_id)
        assert exec_res["success"] is True

        # Fetch detail from /notifications/{id}
        detail_resp = await ac.get(f"/api/v1/notifications/{notif_id}")
        assert detail_resp.status_code == 200
        notif_detail = detail_resp.json()
        assert notif_detail["id"] == notif_id
        assert notif_detail["recipient"] == "priyer@test.com"
        assert notif_detail["status"] == "SENT"
        assert notif_detail["delivery_receipt"] is not None
        receipt = notif_detail["delivery_receipt"]
        assert receipt["provider"] == "local_mock"
        assert receipt["status"] == "MOCK_RECORDED"
        assert receipt["receipt_requested"] is True
        assert "message_id" in receipt


@pytest.mark.asyncio
async def test_direct_mx_delivery_to_damcogroup_automated():
    """Verify live direct MX delivery transmission to damcogroup-com.mail.protection.outlook.com:25."""
    from app.services.email_service import DirectMxEmailProvider

    provider = DirectMxEmailProvider()
    res = provider.send_email(
        to_addresses=["priyer@damcogroup.com"],
        subject="UAIC Automated Live Direct MX Test",
        body_html="<h3>Automated Verification</h3><p>Direct MX transmission test.</p>",
        body_text="Automated Direct MX transmission test.",
    )
    assert res.success is True
    assert res.provider == "direct_mx"
    assert res.delivery_receipt is not None
    assert "damcogroup-com.mail.protection.outlook.com" in res.delivery_receipt.get("gateway_host", "")
    # Server response from Microsoft 365 gateway indicates queued mail
    resp_str = str(res.delivery_receipt.get("server_response", "")).lower()
    assert "250" in resp_str or "queued" in resp_str or "2.6.0" in resp_str or res.delivery_receipt.get("server_code") == 250


@pytest.mark.asyncio
@pytest.mark.requires_maildev
async def test_maildev_provider_connection_automated():
    """Verify local MailDev connection and EHLO handshake on port 1025."""
    from app.services.email_service import MailDevEmailProvider

    provider = MailDevEmailProvider(host="localhost", port=1025, web_url="http://localhost:1080")
    result = provider.test_connection()
    assert result.success is True
    assert result.provider == "maildev"
    assert "1025" in result.message
    assert result.latency_ms > 0

    # Test via API endpoint
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post(
            "/api/v1/settings/email/test-connection",
            json={"provider": "maildev", "smtp_host": "localhost", "smtp_port": 1025},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["provider"] == "maildev"
        assert "1025" in data["message"]


@pytest.mark.asyncio
@pytest.mark.requires_maildev
async def test_maildev_provider_send_and_receipt_automated():
    """Verify live email delivery into local MailDev server with delivery receipt and webbox URL."""
    from app.services.email_service import MailDevEmailProvider

    provider = MailDevEmailProvider(host="localhost", port=1025, web_url="http://localhost:1080")
    res = provider.send_email(
        to_addresses=["priyer@test.com"],
        subject="UAIC Automated MailDev Verification Test",
        body_html="<h3>MailDev Local Inspection</h3><p>Automated verification message.</p>",
        body_text="Automated MailDev verification message.",
    )
    assert res.success is True
    assert res.provider == "maildev"
    assert res.delivery_receipt is not None
    receipt = res.delivery_receipt
    assert receipt["provider"] == "maildev"
    assert "1025" in receipt["gateway_host"]
    assert receipt["webbox_url"] == "http://localhost:1080"
    assert "250" in receipt["server_response"]
    assert receipt["receipt_requested"] is True
    assert "message_id" in receipt

    # Test via API endpoint /api/v1/settings/email/test-send
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post(
            "/api/v1/settings/email/test-send",
            json={
                "recipient": "priyer@test.com",
                "subject": "UAIC Test Send via MailDev Endpoint",
                "body": "Verifying MailDev delivery via test-send endpoint.",
                "provider": "maildev",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        notif_id = data["notification_id"]

        # Execute asynchronous delivery handler synchronously for test
        from app.tasks.notification_tasks import _execute_notification_delivery
        exec_res = await _execute_notification_delivery(notif_id)
        assert exec_res["success"] is True

        # Verify notification details in DB
        detail_resp = await ac.get(f"/api/v1/notifications/{notif_id}")
        assert detail_resp.status_code == 200
        notif_detail = detail_resp.json()
        assert notif_detail["id"] == notif_id
        assert notif_detail["recipient"] == "priyer@test.com"
        assert notif_detail["provider"] == "maildev"
        assert notif_detail["status"] == "SENT"
        assert notif_detail["delivery_receipt"] is not None
        assert notif_detail["delivery_receipt"]["webbox_url"] == "http://localhost:1080"


@pytest.mark.asyncio
async def test_template_studio_crud_and_preview():
    """Verify Template Studio: fetch templates, update custom template, preview live, and reset to default."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Fetch templates catalog
        tpl_resp = await ac.get("/api/v1/notifications/templates")
        assert tpl_resp.status_code == 200
        tpls = tpl_resp.json()
        assert len(tpls) >= 4
        # Verify court case matched template exists
        match_tpl = next((t for t in tpls if t["event_type"] == "COURT_CASE_MATCHED"), None)
        assert match_tpl is not None
        assert "parameter_catalog" in match_tpl
        assert len(match_tpl["parameter_catalog"]) > 5

        # 2. Fetch token catalog
        tokens_resp = await ac.get("/api/v1/notifications/templates/tokens")
        assert tokens_resp.status_code == 200
        tokens = tokens_resp.json()
        assert any(t["token"] == "matched_cases_table" for t in tokens)
        assert any(t["token"] == "claim_number" for t in tokens)

        # 3. Live Preview with draft strings
        preview_resp = await ac.post(
            "/api/v1/notifications/templates/preview",
            json={
                "event_type": "COURT_CASE_MATCHED",
                "subject_template": "CUSTOM SUBJECT: {{claim_number}} has {{matched_count}} matches",
                "body_template_html": "<p>Hello {{insured_name}}, matches: {{matched_cases_table}}</p>",
                "body_template_text": "Claim {{claim_number}}",
            },
        )
        assert preview_resp.status_code == 200
        pdata = preview_resp.json()
        assert "CUSTOM SUBJECT: 0100456789 has 2 matches" in pdata["subject"]
        assert "JOHNATHAN DOE" in pdata["body_html"]
        assert "CACE-24-001234" in pdata["body_html"]

        # 4. Save custom template override (PUT)
        put_resp = await ac.put(
            "/api/v1/notifications/templates/COURT_CASE_MATCHED",
            json={
                "name": "Custom Court Case Match Template",
                "subject_template": "DOCKET MATCH: Claim {{claim_number}} ({{matched_count}})",
                "body_template_html": "<div>Custom Match Body for {{insured_name}}</div>",
                "body_template_text": "Match for {{claim_number}}",
            },
        )
        assert put_resp.status_code == 200
        put_data = put_resp.json()
        assert put_data["is_custom"] is True
        assert put_data["subject_template"] == "DOCKET MATCH: Claim {{claim_number}} ({{matched_count}})"

        # 5. Verify emit_event uses custom template from DB
        async with AsyncSessionLocal() as db:
            notif = await NotificationService.emit_event(
                db=db,
                event_type="COURT_CASE_MATCHED",
                context={"claim_number": "0100112233", "insured_name": "SARAH CONNOR", "matched_count": 3},
                idempotency_key=f"TEST:CUSTOM:TPL:{uuid.uuid4().hex[:8]}",
            )
            assert notif is not None
            assert notif.subject == "DOCKET MATCH: Claim 0100112233 (3)"
            assert "Custom Match Body for SARAH CONNOR" in notif.body_html

        # 6. Reset to default (POST reset)
        reset_resp = await ac.post("/api/v1/notifications/templates/COURT_CASE_MATCHED/reset")
        assert reset_resp.status_code == 200
        reset_data = reset_resp.json()
        assert reset_data["is_custom"] is False
        assert "Court Docket Match Discovered" in reset_data["subject_template"]



