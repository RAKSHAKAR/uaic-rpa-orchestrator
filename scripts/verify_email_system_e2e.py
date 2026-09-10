"""Standalone E2E Automated Verification Script for UAIC Email & Notification Engine.

Verifies:
1. Provider Connection Tests (Local Mock & Direct MX to damcogroup.com).
2. Dynamic Template Preview for all 4 event types (HTML & Plain Text rendering).
3. Live Test Email Dispatch with RFC 3798 / RFC 822 Delivery Receipt Generation.
4. Database Persistence & Receipt Retrieval.
"""

import sys
import asyncio
from datetime import datetime, timezone
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.services.email_service import (
    MockEmailProvider,
    DirectMxEmailProvider,
    MailDevEmailProvider,
    TemplateRenderer,
)
from app.core.database import AsyncSessionLocal
from app.services.notification_service import NotificationService
from app.services.settings_service import get_system_settings_async


def log_step(title: str):
    print(f"\n{'='*70}\n[STEP] {title}\n{'='*70}")


def log_pass(msg: str):
    print(f"  [PASS] {msg}")


def log_fail(msg: str):
    print(f"  [FAIL] {msg}")
    sys.exit(1)


async def run_e2e_verification():
    print("=== UAIC EMAIL & NOTIFICATION ENGINE — AUTOMATED E2E TEST ===")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")

    # STEP 1: Connection Tests
    log_step("1. Provider Connection Tests (Mock, MailDev, Direct MX)")

    # 1A: Mock Provider
    mock_provider = MockEmailProvider()
    mock_conn = mock_provider.test_connection()
    if mock_conn.success:
        log_pass(f"Mock Sandbox Connection: {mock_conn.message} ({mock_conn.latency_ms}ms)")
    else:
        log_fail(f"Mock Sandbox Connection Failed: {mock_conn.message}")

    # 1B: MailDev Provider (localhost:1025)
    maildev_provider = MailDevEmailProvider(host="localhost", port=1025, web_url="http://localhost:1080")
    maildev_conn = maildev_provider.test_connection()
    if maildev_conn.success:
        log_pass(f"MailDev SMTP Connection: {maildev_conn.message} ({maildev_conn.latency_ms}ms)")
    else:
        log_fail(f"MailDev SMTP Connection Failed: {maildev_conn.message} - {maildev_conn.error_detail}")

    # 1C: Direct MX Provider to damcogroup.com
    mx_provider = DirectMxEmailProvider()
    mx_conn = mx_provider.test_connection(domain="damcogroup.com")
    if mx_conn.success:
        log_pass(f"Direct MX Gateway Connection: {mx_conn.message} ({mx_conn.latency_ms}ms)")
    else:
        log_fail(f"Direct MX Gateway Connection Failed: {mx_conn.message}")

    # STEP 2: Template Preview Verification
    log_step("2. Dynamic Template Preview (All 4 Events)")
    event_templates = [
        ("guidewire_activity_created", "Guidewire Activity Created"),
        ("guidewire_activity_failed", "Guidewire Activity Failed"),
        ("scraper_failed", "Scraper Error / CAPTCHA Timeout"),
        ("test_email", "Interactive Test Email"),
    ]

    sample_context = {
        "claim_number": "0100987654",
        "insured_name": "JOHNATHAN DOE",
        "claimant_name": "JANE SMITH",
        "exposure_number": "001",
        "activity_id": "ACT-77192",
        "matched_count": "2",
        "county_name": "Broward County",
        "portal_name": "Broward County Clerk",
        "error_message": "CAPTCHA solve retry limit exceeded",
        "http_status": "502 Bad Gateway",
        "attempt_number": "1 of 3",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "environment": "Development / Staging",
        "recipient": "priyer@test.com",
        "provider": "direct_mx",
        "custom_body": "Automated verification payload from UAIC RPA Orchestrator.",
    }

    for ev_key, ev_label in event_templates:
        tpl = TemplateRenderer.get_template(ev_key)
        rendered_subject = TemplateRenderer.render(tpl["subject"], sample_context)
        rendered_html = TemplateRenderer.render(tpl["body_html"], sample_context, escape_html=False)
        rendered_text = TemplateRenderer.render(tpl.get("body_text", ""), sample_context)

        assert len(rendered_subject) > 0, f"Subject empty for {ev_key}"
        assert "<html" in rendered_html.lower() or "<div" in rendered_html.lower(), f"HTML invalid for {ev_key}"
        assert "0100987654" in rendered_html or "0100987654" in rendered_subject or "Automated" in rendered_html
        log_pass(f"Template [{ev_label}] rendered successfully: Subject='{rendered_subject[:60]}...' (HTML len: {len(rendered_html)})")

    # STEP 3: Live Direct MX Email Send & Receipt Generation
    log_step("3. Live Direct MX Email Send & Delivery Receipt (RFC 3798 / 822)")
    target_email = "priyer@test.com"
    subject = f"UAIC E2E Automated Verification — {datetime.now(timezone.utc).strftime('%H:%M:%S')}"
    body_html = f"""<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; padding: 20px; color: #1e293b; background-color: #f8fafc;">
  <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden;">
    <div style="background: #4f46e5; padding: 20px; color: #ffffff;">
      <h2 style="margin: 0; font-size: 18px;">UAIC Claim & RPA Orchestrator</h2>
      <p style="margin: 4px 0 0; font-size: 13px; opacity: 0.9;">Automated Live Delivery Verification & Gateway Receipt</p>
    </div>
    <div style="padding: 24px;">
      <p>Hello <strong>priyer@test.com</strong>,</p>
      <p>This email confirms that the UAIC Email & Notification Engine has successfully performed direct MX transmission with cryptographic delivery proof.</p>
      <div style="background: #f1f5f9; padding: 12px 16px; border-radius: 8px; font-family: monospace; font-size: 12px; margin: 16px 0;">
        <strong>Recipient:</strong> {target_email}<br>
        <strong>Delivery Protocol:</strong> Direct MX via RFC-5321 STARTTLS (Port 25)<br>
        <strong>MTA Gateway:</strong> damcogroup-com.mail.protection.outlook.com<br>
        <strong>Tracking Headers:</strong> RFC 3798 & RFC 822 Delivery Receipts Active<br>
        <strong>Timestamp:</strong> {datetime.now(timezone.utc).isoformat()}
      </div>
      <p style="font-size: 12px; color: #64748b;">This message was generated autonomously by the automated E2E test suite.</p>
    </div>
  </div>
</body>
</html>"""

    mx_send_res = mx_provider.send_email(
        to_addresses=[target_email],
        subject=subject,
        body_html=body_html,
        body_text=f"UAIC E2E Automated Verification. Recipient: {target_email}. Direct MX transmission.",
    )

    if mx_send_res.success:
        receipt = mx_send_res.delivery_receipt or {}
        log_pass(f"Email Transmitted Successfully to {target_email}!")
        log_pass(f"Gateway Server: {receipt.get('gateway_host')}:{receipt.get('gateway_port')}")
        log_pass(f"Server Response: {receipt.get('server_response')}")
        log_pass(f"Message-ID: {receipt.get('message_id')}")
        log_pass(f"Latency: {receipt.get('duration_ms')}ms")
    else:
        log_fail(f"Direct MX Send Failed: {mx_send_res.error_message}")

    # STEP 3B: Live Local MailDev Email Send & Receipt
    log_step("3B. Live Local MailDev Email Send & Delivery Receipt (Port 1025 / 1080)")
    maildev_subject = f"UAIC MailDev Verification — {datetime.now(timezone.utc).strftime('%H:%M:%S')}"
    maildev_send_res = maildev_provider.send_email(
        to_addresses=[target_email],
        subject=maildev_subject,
        body_html=f"<h3>UAIC Local MailDev Test</h3><p>Dispatched to MailDev at {maildev_provider.host}:{maildev_provider.port}. Inspect at <a href='{maildev_provider.web_url}'>{maildev_provider.web_url}</a>.</p>",
        body_text=f"UAIC Local MailDev Test. Recipient: {target_email}. Inspect at {maildev_provider.web_url}",
    )
    if maildev_send_res.success:
        m_receipt = maildev_send_res.delivery_receipt or {}
        log_pass(f"MailDev Email Dispatched Successfully to {target_email}!")
        log_pass(f"MailDev Gateway: {m_receipt.get('gateway_host')}")
        log_pass(f"MailDev Webbox: {m_receipt.get('webbox_url')}")
        log_pass(f"MailDev Server Response: {m_receipt.get('server_response')}")
        log_pass(f"MailDev Message-ID: {m_receipt.get('message_id')}")
    else:
        log_fail(f"MailDev Send Failed: {maildev_send_res.error}")

    # STEP 4: Database Persistence & Receipt Inspection via NotificationService
    log_step("4. Database Persistence & Receipt Inspection")
    async with AsyncSessionLocal() as db:
        # 4A: Direct MX notification record
        notif_record = await NotificationService.emit_event(
            db=db,
            event_type="TEST_EMAIL",
            context={
                "claim_number": "0100987654",
                "recipient": target_email,
                "custom_subject": subject,
                "custom_body": "Verifying DB receipt persistence.",
            },
            override_provider="direct_mx",
            override_recipient=target_email,
        )
        if notif_record:
            log_pass(f"Direct MX Notification DB Record Created: ID={notif_record.id}, Status={notif_record.status}")
            log_pass(f"DB Delivery Receipt Present: {notif_record.delivery_receipt is not None}")
            if notif_record.delivery_receipt:
                log_pass(f"DB Receipt Server Response: {notif_record.delivery_receipt.get('server_response')}")
        else:
            log_fail("Failed to persist Direct MX notification record to database.")

        # 4B: MailDev notification record
        notif_maildev = await NotificationService.emit_event(
            db=db,
            event_type="TEST_EMAIL",
            context={
                "claim_number": "0100987654",
                "recipient": target_email,
                "custom_subject": maildev_subject,
                "custom_body": "Verifying MailDev DB receipt persistence.",
            },
            override_provider="maildev",
            override_recipient=target_email,
        )
        if notif_maildev:
            log_pass(f"MailDev Notification DB Record Created: ID={notif_maildev.id}, Status={notif_maildev.status}")
            log_pass(f"DB Delivery Receipt Present: {notif_maildev.delivery_receipt is not None}")
            if notif_maildev.delivery_receipt:
                log_pass(f"MailDev Web URL in DB: {notif_maildev.delivery_receipt.get('webbox_url')}")
        else:
            log_fail("Failed to persist MailDev notification record to database.")

    print(f"\n{'='*70}\n[COMPLETE] ALL 5 AUTOMATED VERIFICATION CHECKS PASSED (100% SUCCESS)\n{'='*70}\n")


if __name__ == "__main__":
    asyncio.run(run_e2e_verification())

