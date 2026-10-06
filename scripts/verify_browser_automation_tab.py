"""Playwright automation verification script for 'Browser Automation & Fleet' tab in Settings.
Tests:
- Tab navigation & header verification
- Multi-engine switching (Chromium, Chrome, Edge)
- Execution mode toggle (Attended GUI vs Headless)
- Typing speed presets & dynamics
- Extension Health Diagnostics test ("Check Health")
- One-time Toolbar Pinning & Profile Setup ("Setup & Pin Now")
- Live Browser Launch Verification ("Launch Headless Test")
- Concurrency slider & 10-column worker presets (1x - 10x)
- Live Parallel Fleet Concurrency Launch Test (2x parallel workers)
- Proxy Gateway Egress status indicator
- Settings persistence (Save Configuration)
Saves visual verification screenshots into docs/.
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))


def run_automation_tab_verification():
    print("=" * 75)
    print("Starting Playwright verification of 'Browser Automation & Fleet' tab...")
    print("=" * 75)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1872, "height": 1113})
        page = context.new_page()

        # Step 1: Navigate to settings page
        print("\n1. Navigating to http://localhost:3000/settings...")
        page.goto("http://localhost:3000/settings", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_selector("text=Unified Solution & Automation Settings", timeout=30000)
        page.wait_for_timeout(1000)
        print("   PASS: Settings page loaded.")

        # Step 2: Switch to Browser Automation & Fleet tab
        print("\n2. Switching to 'Browser Automation & Fleet' tab...")
        automation_tab_btn = page.locator("button:has-text('Browser Automation & Fleet')")
        assert automation_tab_btn.is_visible(), "Browser Automation & Fleet tab button not found"
        automation_tab_btn.click()
        page.wait_for_selector("text=Browser Automation & RPA Execution Fleet", timeout=10000)
        page.wait_for_timeout(800)

        overview_path = os.path.join(DOCS_DIR, "verify_automation_tab_overview.png")
        page.screenshot(path=overview_path)
        print(f"   PASS: Switched to 'Browser Automation & Fleet' tab. Screenshot: {overview_path}")

        # Step 3: Verify Browser Engine selection cards
        print("\n3. Testing Browser Engine Selector (Chromium, Chrome, Edge)...")
        chromium_opt = page.locator("label:has-text('Chromium (Bundled)')").first
        chrome_opt = page.locator("label:has-text('Google Chrome')").first
        edge_opt = page.locator("label:has-text('Microsoft Edge')").first
        assert chromium_opt.is_visible(), "Chromium option not visible"
        assert chrome_opt.is_visible(), "Google Chrome option not visible"
        assert edge_opt.is_visible(), "Microsoft Edge option not visible"

        # Select Chrome and check label
        chrome_opt.click()
        page.wait_for_timeout(300)
        selected_engine_badge = page.locator("span:text-is('CHROME')").first
        assert selected_engine_badge.is_visible(), "Selected engine badge did not update to CHROME"
        print("   [x] Google Chrome engine selected successfully.")

        # Switch back to Chromium (Bundled default)
        chromium_opt.click()
        page.wait_for_timeout(300)
        selected_engine_badge = page.locator("span:text-is('CHROMIUM')").first
        assert selected_engine_badge.is_visible(), "Selected engine badge did not revert to CHROMIUM"
        print("   [x] Chromium engine selected successfully.")
        print("   PASS: Engine selector operates smoothly.")

        # Step 4: Verify Attended GUI vs Headless Mode selection
        print("\n4. Testing Attended (Visible GUI) vs Headless (Background) Mode Cards...")
        attended_card = page.locator("div:has-text('Attended (Visible GUI)'):has-text('Real Desktop Window')").first
        headless_card = page.locator("div:has-text('Headless (Background)'):has-text('Silent Execution')").first
        assert attended_card.is_visible(), "Attended mode card not visible"
        assert headless_card.is_visible(), "Headless mode card not visible"

        # Click Attended mode
        attended_card = page.locator("div.cursor-pointer:has-text('Real Desktop Window')").first
        attended_card.click()
        page.wait_for_timeout(400)
        assert page.locator("span:has-text('Active: Attended (Visible GUI)')").first.is_visible()
        print("   [x] Attended mode selected and verified.", flush=True)

        # Click Headless mode for background execution
        headless_card = page.locator("div.cursor-pointer:has-text('Silent Execution')").first
        headless_card.click()
        page.wait_for_timeout(400)
        assert page.locator("span:has-text('Active: Headless (Background)')").first.is_visible()
        print("   [x] Headless mode selected and verified.", flush=True)
        print("   PASS: Execution mode toggle operates smoothly.", flush=True)

        # Step 5: Test Execution Timing Presets
        print("\n5. Testing Execution Timing & Keystroke Dynamics Presets...")
        fast_preset = page.locator("button:has-text('Fast'):has-text('Snappy')").first
        turbo_preset = page.locator("button:has-text('Turbo / Instant'):has-text('Recommended')").first
        assert fast_preset.is_visible(), "Fast preset button not visible"
        assert turbo_preset.is_visible(), "Turbo preset button not visible"

        fast_preset.click()
        page.wait_for_timeout(200)
        assert page.locator("span:has-text('FAST (15ms/char)')").first.is_visible()
        print("   [x] Fast speed preset activated (15ms/char).")

        turbo_preset.click()
        page.wait_for_timeout(200)
        assert page.locator("span:has-text('Turbo / Instant (0ms)')").first.is_visible()
        print("   [x] Turbo speed preset activated (0ms/char).")
        print("   PASS: Keystroke timing presets verified.")

        # Step 6: Test Extension Health Diagnostics
        print("\n6. Testing Extension Health Diagnostics ('Check Health')...")
        check_health_btn = page.locator("button:has-text('Check Health')").first
        assert check_health_btn.is_visible(), "Check Health button not visible"
        check_health_btn.click()
        page.wait_for_selector("text=Found on Disk", timeout=15000)
        assert page.locator("text=Manifest V3 Valid").first.is_visible()
        print("   PASS: Extension Health Diagnostics verified: Found on Disk & Manifest V3 Valid.")

        # Step 7: Test Toolbar Pinning & Profile Setup Action
        print("\n7. Testing One-Time Toolbar Pinning ('Setup & Pin Now')...")
        setup_pin_btn = page.locator("button:has-text('Setup & Pin Now')").first
        assert setup_pin_btn.is_visible(), "Setup & Pin Now button not visible"
        setup_pin_btn.click()

        # Wait for feedback or completion (endpoint launches headless browser to verify profile)
        print("   Waiting for one-time toolbar pinning and profile verification...", flush=True)
        page.wait_for_selector("text=AntiCaptcha extension verified & pinned", timeout=60000)
        print("   PASS: Toolbar Pinning verified & persistent profile configured.", flush=True)

        # Step 8: Test Live Browser Launch Verification
        print("\n8. Testing Live Browser Launch Verification...", flush=True)
        launch_test_btn = page.locator("button.bg-purple-600:has-text('Launch')").first
        launch_test_btn.scroll_into_view_if_needed()
        assert launch_test_btn.is_visible(), "Launch Browser Test button not visible"
        btn_label = launch_test_btn.text_content().strip()
        print(f"   Clicking launch button: '{btn_label}'...", flush=True)
        launch_test_btn.click()

        print("   Waiting for browser launch verification response...", flush=True)
        page.wait_for_selector("text=Live Launch Verified Successfully", timeout=75000)
        print("   PASS: Live browser launch completed and verified successfully.", flush=True)

        # Step 9: Test Parallel RPA Concurrency Slider & Presets
        print("\n9. Testing Parallel RPA Concurrency (1–10x scale)...", flush=True)
        concurrency_2x_btn = page.locator("button:has-text('2x'):has-text('Duo')").first
        concurrency_2x_btn.scroll_into_view_if_needed()
        assert concurrency_2x_btn.is_visible(), "2x Duo preset button not visible"
        concurrency_2x_btn.click()
        page.wait_for_timeout(400)
        assert page.locator("span:text-is('2 Parallel Workers')").first.is_visible()
        print("   [x] 2x Concurrency Duo preset activated.", flush=True)

        # Step 10: Test Live Parallel Fleet Concurrency Launch
        print("\n10. Testing Live Fleet Concurrency Launch (2 Parallel Workers)...", flush=True)
        fleet_test_btn = page.locator("button:has-text('Test Fleet Launch')").first
        fleet_test_btn.scroll_into_view_if_needed()
        assert fleet_test_btn.is_visible(), "Fleet test launch button not visible"
        fleet_label = fleet_test_btn.text_content().strip()
        print(f"   Clicking fleet test button: '{fleet_label}'...", flush=True)
        fleet_test_btn.click()

        print("   Waiting for parallel workers to launch and report status...", flush=True)
        page.wait_for_selector("text=Fleet Launch Succeeded", timeout=75000)
        assert page.locator("text=Worker #1").first.is_visible()
        assert page.locator("text=Worker #2").first.is_visible()
        print("   PASS: Parallel fleet launch verified with workers operating concurrently.", flush=True)

        # Step 11: Verify Proxy Gateway Egress status card
        print("\n11. Verifying Proxy Gateway Egress Status indicator...")
        proxy_card = page.locator("div:has-text('Proxy Gateway Egress Status')").first
        assert proxy_card.is_visible(), "Proxy Gateway Egress Status card not visible"
        print("   PASS: Proxy Gateway status indicator verified.")

        # Step 12: Test Saving Configuration
        print("\n12. Testing Settings Persistence (Save Configuration)...")
        save_btn = page.locator("button:has-text('Save Extension Config')").first
        save_btn.scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        save_btn.click()
        try:
            page.wait_for_selector("text=Settings saved as revision", timeout=25000)
        except Exception:
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_selector("text=Settings saved as revision", timeout=15000)
        print("   PASS: Settings saved and persisted to database.")

        # Final full-page screenshot
        tests_path = os.path.join(DOCS_DIR, "verify_automation_tab_tests.png")
        page.screenshot(path=tests_path)
        print(f"\nCaptured verified tab state screenshot: {tests_path}")

        browser.close()

    print("\n" + "=" * 75)
    print("ALL 12 BROWSER AUTOMATION & FLEET VERIFICATION STEPS PASSED SUCCESSFULLY!")
    print("=" * 75)


if __name__ == "__main__":
    run_automation_tab_verification()
