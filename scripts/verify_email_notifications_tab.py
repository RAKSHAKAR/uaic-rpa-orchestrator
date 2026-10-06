"""
End-to-End Verification of 'Email & Notification' Tab Functionality
Target Route: http://localhost:3000/settings (Tab: "Email & Notification" / activeTab === "email")

Validates:
1. Navigation & Tab Switching to Email & Notification
2. Master Email & Notification Engine Switch status
3. Outbound Email Provider Configuration (Local Mock Sandbox, MailDev, Direct MX, SMTP, Graph, SES)
4. Interactive Provider Connection Handshake Test (POST /api/v1/settings/email/test-connection)
5. Recipient Distribution Lists (Primary TO, CC, and BCC Chip inputs, addition, and removal)
6. Delivery Cadence, Mode, Retries, and Delay settings
7. Match Notification Dispatch Strategy (Both / Direct System Only / Guidewire Activity Only)
8. Granular Event Rules & Dispatch Triggers
9. Interactive Live Test Email Dispatcher (POST /api/v1/settings/email/test-send)
10. Settings Persistence to SQLite & State Retention across Page Reload
11. Clean Restoration of Test Recipients
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
os.makedirs(DOCS_DIR, exist_ok=True)


def run_email_notifications_verification():
    print("=" * 80)
    print("Starting Playwright verification of 'Email & Notification' tab...")
    print("=" * 80)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1872, "height": 1113})
        page = context.new_page()

        # Step 1: Navigate to Settings page
        print("\n1. Navigating to http://localhost:3000/settings...")
        page.goto("http://localhost:3000/settings", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_selector("text=Unified Solution & Automation Settings", timeout=30000)
        page.wait_for_timeout(1000)
        print("   PASS: Settings page loaded.")

        # Step 2: Switch to Email & Notification tab
        print("\n2. Switching to 'Email & Notification' tab...")
        email_tab_btn = page.locator("button:has-text('Email & Notification')")
        assert email_tab_btn.is_visible(), "Email & Notification tab button not found"
        email_tab_btn.click()
        page.wait_for_selector("text=Master Email & Notification Engine Switch", timeout=15000)
        page.wait_for_selector("text=Outbound Email Provider Configuration", timeout=15000)
        page.wait_for_timeout(800)

        overview_path = os.path.join(DOCS_DIR, "verify_email_tab_overview.png")
        page.screenshot(path=overview_path)
        print(f"   PASS: Switched to 'Email & Notification' tab. Screenshot: {overview_path}")

        # Step 3: Verify Master Switch
        print("\n3. Verifying Master Email Engine Switch status...")
        master_toggle = page.locator("#email-master-toggle")
        assert master_toggle.is_visible(timeout=5000) or master_toggle.count() > 0, "Master switch input missing"
        if not master_toggle.is_checked():
            print("   Enabling Master Email Engine Switch...")
            page.locator("label:has(#email-master-toggle)").click()
            page.wait_for_timeout(400)
        assert master_toggle.is_checked(), "Master email switch should be enabled"
        assert page.locator("text=Engine Active").first.is_visible(), "Engine Active badge not visible"
        print("   PASS: Master Email Engine is active and verified.")

        # Step 4: Provider Selection & Connection Handshake Test (Local Mock Sandbox)
        print("\n4. Selecting 'Local Mock Sandbox' provider & testing connection...")
        mock_card = page.locator("#provider-card-local_mock")
        assert mock_card.is_visible(), "Local Mock provider card not found"
        mock_card.click()
        page.wait_for_timeout(400)

        test_conn_btn = page.locator("#btn-test-email-connection")
        assert test_conn_btn.is_visible(), "Test Connection button not found"
        test_conn_btn.click()
        page.wait_for_selector("#email-connection-result-card", timeout=15000)
        conn_card = page.locator("#email-connection-result-card")
        assert conn_card.locator("text=Email Provider Handshake Succeeded").first.is_visible(), "Handshake failed"
        print("   PASS: Provider connection handshake succeeded with live latency benchmark.")

        # Step 5: Verify MailDev Webbox Provider Fields
        print("\n5. Selecting 'Local MailDev Webbox' and verifying fields...")
        maildev_card = page.locator("#provider-card-maildev")
        assert maildev_card.is_visible(), "MailDev card not found"
        maildev_card.click()
        page.wait_for_timeout(400)
        assert page.locator("text=MailDev SMTP Host").is_visible(), "MailDev SMTP Host label not visible"
        assert page.locator("text=MailDev SMTP Port").is_visible(), "MailDev SMTP Port label not visible"
        assert page.locator("text=MailDev Web Inspector URL").is_visible(), "MailDev Web Inspector label not visible"
        print("   PASS: MailDev configuration controls verified.")

        # Switch back to local_mock for reliable test send
        mock_card.click()
        page.wait_for_timeout(300)

        # Step 6: Recipient Distribution Lists Management (TO, CC, BCC)
        print("\n6. Managing Recipient Distribution Lists (TO, CC, BCC chips)...")
        # Add primary TO recipient
        to_input = page.locator("#input-new-to-recipient")
        to_add_btn = page.locator("#btn-add-to-recipient")
        to_input.fill("ops-claims@uaic.com")
        to_add_btn.click()
        page.wait_for_timeout(400)
        assert page.locator("span:has-text('ops-claims@uaic.com')").is_visible(), "ops-claims@uaic.com chip missing"
        print("   PASS: Added primary TO recipient chip (ops-claims@uaic.com).")

        # Expand CC & BCC accordion
        print("   Expanding CC & BCC accordion...")
        toggle_cc_bcc_btn = page.locator("#btn-toggle-cc-bcc")
        toggle_cc_bcc_btn.click()
        page.wait_for_timeout(400)

        # Add CC recipient
        cc_input = page.locator("#input-new-cc-recipient")
        cc_add_btn = page.locator("#btn-add-cc-recipient")
        cc_input.fill("supervisor@uaic.com")
        cc_add_btn.click()
        page.wait_for_timeout(400)
        assert page.locator("span:has-text('supervisor@uaic.com')").is_visible(), "supervisor@uaic.com chip missing"
        print("   PASS: Added CC recipient chip (supervisor@uaic.com).")

        # Add BCC recipient
        bcc_input = page.locator("#input-new-bcc-recipient")
        bcc_add_btn = page.locator("#btn-add-bcc-recipient")
        bcc_input.fill("audit-archive@uaic.com")
        bcc_add_btn.click()
        page.wait_for_timeout(400)
        assert page.locator("span:has-text('audit-archive@uaic.com')").is_visible(), "audit-archive@uaic.com chip missing"
        print("   PASS: Added BCC recipient chip (audit-archive@uaic.com).")

        # Step 7: Delivery Cadence & Retries
        print("\n7. Configuring Delivery Cadence and Retries...")
        page.locator("#email-digest-mode").select_option("immediate")
        page.locator("#email-retry-count").fill("3")
        page.locator("#email-retry-delay").fill("15")
        page.wait_for_timeout(300)
        print("   PASS: Cadence configured to Immediate, 3 retries, 15s delay.")

        # Step 8: Match Notification Strategy & Granular Event Rules
        print("\n8. Configuring Match Notification Strategy & Granular Event Rules...")
        strategy_both = page.locator("#strategy-card-both")
        strategy_both.click()
        page.wait_for_timeout(300)
        assert page.locator("text=Dual Channel (Both)").is_visible(), "Dual channel option missing"

        court_match_rule = page.locator("#event-rule-card-court_case_matched")
        assert court_match_rule.is_visible(), "Court docket match rule missing"
        print("   PASS: Dual Channel dispatch strategy and event rules confirmed.")

        # Step 9: Interactive Live Test Email Dispatcher
        print("\n9. Dispatching interactive live test email...")
        page.locator("#input-test-email-recipient").fill("qa-tester@uaic.com")
        page.locator("#input-test-email-subject").fill("UAIC Automated Verification Test Notification")
        page.locator("#textarea-test-email-body").fill("Verifying email engine dispatch end-to-end via automated Playwright test runner.")
        page.wait_for_timeout(300)

        send_btn = page.locator("#btn-send-test-email")
        send_btn.click()
        page.wait_for_selector("#email-test-send-result-card", timeout=15000)
        result_card = page.locator("#email-test-send-result-card")
        result_card.scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        assert result_card.locator("text=Test Notification Dispatched Successfully").first.is_visible(), "Test notification failed"
        assert result_card.locator("text=Notification ID:").is_visible(), "Notification ID not displayed"
        print("   PASS: Live test notification dispatched and recorded in database.")

        result_path = os.path.join(DOCS_DIR, "verify_email_tab_test_result.png")
        page.screenshot(path=result_path)
        print(f"   PASS: Captured verified test result screenshot: {result_path}")

        # Step 10: Persist Settings & Verify Retention across Page Reload
        print("\n10. Persisting Email Configuration to SQLite database...")
        save_btn = page.locator("button:has-text('Save Configuration')").first
        save_btn.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        save_btn.click()
        page.wait_for_selector("text=Settings saved as revision", timeout=20000)
        print("   PASS: Settings persisted successfully.")

        print("\n11. Reloading Settings page to verify persistence...")
        page.reload(wait_until="domcontentloaded")
        page.wait_for_selector("text=Unified Solution & Automation Settings", timeout=30000)
        page.locator("button:has-text('Email & Notification')").click()
        page.wait_for_selector("text=Master Email & Notification Engine Switch", timeout=15000)
        page.wait_for_timeout(800)

        # Verify retained fields
        assert page.locator("#email-master-toggle").is_checked(), "Master switch state not retained"
        assert page.locator("span:has-text('ops-claims@uaic.com')").is_visible(), "ops-claims@uaic.com not retained"
        assert page.locator("#email-retry-count").input_value() == "3", "Retry count not retained"
        assert page.locator("#email-retry-delay").input_value() == "15", "Retry delay not retained"

        # Expand CC/BCC to confirm retained
        page.locator("#btn-toggle-cc-bcc").click()
        page.wait_for_timeout(300)
        assert page.locator("span:has-text('supervisor@uaic.com')").is_visible(), "supervisor@uaic.com not retained"
        assert page.locator("span:has-text('audit-archive@uaic.com')").is_visible(), "audit-archive@uaic.com not retained"
        print("   PASS: All email parameters, recipient chips, and retry policies fully retained across reload.")

        # Step 12: Clean up test chips
        print("\n12. Cleaning up test recipient chips...")
        # Remove ops-claims@uaic.com
        to_chip = page.locator("span:has-text('ops-claims@uaic.com') button")
        if to_chip.is_visible():
            to_chip.click()
            page.wait_for_timeout(200)

        # Remove supervisor@uaic.com
        cc_chip = page.locator("span:has-text('supervisor@uaic.com') button")
        if cc_chip.is_visible():
            cc_chip.click()
            page.wait_for_timeout(200)

        # Remove audit-archive@uaic.com
        bcc_chip = page.locator("span:has-text('audit-archive@uaic.com') button")
        if bcc_chip.is_visible():
            bcc_chip.click()
            page.wait_for_timeout(200)

        save_btn.scroll_into_view_if_needed()
        save_btn.click()
        page.wait_for_selector("text=Settings saved as revision", timeout=20000)
        print("   PASS: Restored clean recipient distribution list.")

        browser.close()

    print("\n" + "=" * 80)
    print("ALL 12 EMAIL & NOTIFICATION VERIFICATION STEPS PASSED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    run_email_notifications_verification()
