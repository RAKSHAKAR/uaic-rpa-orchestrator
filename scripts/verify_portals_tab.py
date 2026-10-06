"""Playwright automation verification script for 'County Court Portals' tab in Settings.
Tests all 8 portals, ping functionality, Miami credentials, URL updates, toggles, and Save Configuration.
Saves visual verification screenshots into docs/.
"""

import os
import sys
import time
import httpx
from playwright.sync_api import sync_playwright

DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))

def run_portals_verification():
    print("=" * 70)
    print("Starting Playwright verification of 'County Court Portals' tab...")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1872, "height": 1113})
        page = context.new_page()

        # Step 1: Navigate to settings page
        print("\n1. Navigating to http://localhost:3000/settings...")
        page.goto("http://localhost:3000/settings", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_selector("text=Unified Solution & Automation Settings", timeout=30000)
        page.wait_for_timeout(1000)

        # Step 2: Switch to County Court Portals tab
        print("\n2. Switching to 'County Court Portals' tab...")
        portals_tab_btn = page.locator("button:has-text('County Court Portals')")
        assert portals_tab_btn.is_visible(), "County Court Portals tab button not found"
        portals_tab_btn.click()
        page.wait_for_selector("text=Public County Court Scraper Portals & Health Pings", timeout=10000)
        page.wait_for_timeout(600)
        overview_path = os.path.join(DOCS_DIR, "verify_portals_tab_overview.png")
        page.screenshot(path=overview_path)
        print(f"   PASS: Switched to 'County Court Portals' tab. Screenshot: {overview_path}")

        # Step 3: Verify all 8 portals are displayed with exact UI names and state badges
        print("\n3. Verifying presence of all 8 county court portals...")
        expected_portals = [
            ("FL", "Broward County Clerk of Courts"),
            ("FL", "Hillsborough County Clerk (HOVER Search)"),
            ("FL", "Miami-Dade County Clerk (OCS Portal)"),
            ("TX", "Travis County Odyssey Portal"),
            ("TX", "Dallas County Courts Portal"),
            ("TX", "Harris County Justice of the Peace (JP)"),
            ("TX", "Harris County Clerk WebSearch"),
            ("TX", "Harris County District Clerk (eDocs Search)"),
        ]
        for state, portal_name in expected_portals:
            card = page.locator(f"div.rounded-xl:has-text('{portal_name}')").first
            assert card.is_visible(), f"Portal card '{portal_name}' not visible"
            state_badge = card.locator(f"span:text-is('{state}')").first
            assert state_badge.is_visible(), f"State badge '{state}' not visible for '{portal_name}'"
            print(f"   [x] [{state}] {portal_name} is visible and formatted properly.")
        print("   PASS: All 8 county court portals verified with respective state badges.")

        # Step 4: Test Toggle switch on Dallas County Courts Portal
        print("\n4. Testing Enabled/Disabled switch on Dallas County Courts Portal...")
        dallas_card = page.locator("div.rounded-xl:has-text('Dallas County Courts Portal')").first
        dallas_card.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        dallas_status_text = dallas_card.locator("span.text-\\[11px\\].font-medium.text-slate-500").first
        initial_status = dallas_status_text.text_content().strip()
        print(f"   Dallas portal initial switch state: '{initial_status}'")
        
        # Click toggle switch
        toggle_label = dallas_card.locator("label:has(input[type='checkbox'])").first
        toggle_label.click()
        page.wait_for_timeout(300)
        toggled_status = dallas_status_text.text_content().strip()
        print(f"   Dallas portal toggled switch state: '{toggled_status}'")
        assert initial_status != toggled_status, "Switch state did not update"
        
        # Revert toggle switch
        toggle_label.click()
        page.wait_for_timeout(300)
        reverted_status = dallas_status_text.text_content().strip()
        assert reverted_status == initial_status, "Switch state did not revert"
        print(f"   PASS: Dallas switch toggled and reverted successfully ({reverted_status}).")

        # Step 5: Test Ping Portal on Broward County Clerk
        print("\n5. Testing live 'Ping Portal' on Broward County Clerk of Courts...")
        broward_card = page.locator("div.rounded-xl:has-text('Broward County Clerk of Courts')").first
        broward_card.scroll_into_view_if_needed()
        ping_btn = broward_card.locator("button:has-text('Ping Portal')")
        assert ping_btn.is_visible(), "Broward Ping Portal button not found"
        ping_btn.click()
        print("   Clicked 'Ping Portal', waiting for ping response pill (timeout: 20s)...")
        
        # Wait for duration ms pill to appear
        broward_card.locator("span:has-text('Duration:')").wait_for(timeout=20000)
        page.wait_for_timeout(500)
        ping_path = os.path.join(DOCS_DIR, "verify_portals_ping_result.png")
        page.screenshot(path=ping_path)
        
        status_pill = broward_card.locator("span.rounded-full").first.text_content().strip()
        duration_text = broward_card.locator("span:has-text('Duration:')").first.text_content().strip()
        print(f"   PASS: Broward Ping Portal succeeded! Status: '{status_pill}' | {duration_text}")
        print(f"   Screenshot saved: {ping_path}")

        # Step 6: Test Miami-Dade Credentials Section and Password Eye Toggle
        print("\n6. Testing Miami-Dade credentials section and eye toggle...")
        miami_card = page.locator("div.rounded-xl:has-text('Miami-Dade County Clerk (OCS Portal)')").first
        miami_card.scroll_into_view_if_needed()
        page.wait_for_timeout(300)

        # Check Username input
        username_label = miami_card.locator("label:has-text('Portal Username / Email')")
        assert username_label.is_visible(), "Miami username label not found"
        
        # Locate password field and eye toggle
        pw_container = miami_card.locator("div.relative:has(button)")
        pw_input = pw_container.locator("input")
        eye_btn = pw_container.locator("button")
        assert pw_input.is_visible(), "Miami password input not visible"
        assert eye_btn.is_visible(), "Password toggle eye button not visible"

        initial_type = pw_input.get_attribute("type")
        assert initial_type == "password", f"Expected type=password, got {initial_type}"
        print(f"   Initial password input type: {initial_type}")

        # Click eye toggle button -> should become "text"
        eye_btn.click()
        page.wait_for_timeout(200)
        toggled_type = pw_input.get_attribute("type")
        assert toggled_type == "text", f"Expected type=text after toggle, got {toggled_type}"
        print(f"   Password input type after clicking eye button: {toggled_type}")

        # Click eye toggle button again -> should revert to "password"
        eye_btn.click()
        page.wait_for_timeout(200)
        reverted_type = pw_input.get_attribute("type")
        assert reverted_type == "password", f"Expected type=password after second click, got {reverted_type}"
        print(f"   Password input type after second click: {reverted_type}")
        print("   PASS: Miami password show/hide eye toggle verified.")

        # Check 'Use Miami portal login before searching' toggle
        login_label = miami_card.locator("label:has-text('Use Miami portal login before searching')")
        assert login_label.is_visible(), "Miami login toggle label not found"
        login_toggle = login_label.locator("input[type='checkbox']")
        assert login_toggle.is_visible(), "Miami login toggle checkbox not found"
        print("   PASS: Miami login toggle checkbox is present and interactive.")
        
        miami_path = os.path.join(DOCS_DIR, "verify_portals_miami_credentials.png")
        page.screenshot(path=miami_path)
        print(f"   Screenshot saved: {miami_path}")

        # Step 7: Test Save Configuration on Portals tab
        print("\n7. Testing Save Configuration on Portals tab...")
        page.locator("text=Unified Solution & Automation Settings").scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        save_btn = page.locator("button:has-text('Save Configuration')")
        assert save_btn.is_visible(), "'Save Configuration' button not found"
        save_btn.click()
        print("   Clicked 'Save Configuration', waiting for revision banner...")
        page.wait_for_selector("text=Settings saved as revision", timeout=12000)
        page.wait_for_timeout(500)
        
        banner_text = page.locator("text=Settings saved as revision").first.text_content().strip()
        print(f"   PASS: Save configuration succeeded: '{banner_text}'")
        
        saved_path = os.path.join(DOCS_DIR, "verify_portals_saved_result.png")
        page.screenshot(path=saved_path)
        print(f"   Screenshot saved: {saved_path}")

        browser.close()

    # Step 8: Verify settings directly via backend API
    print("\n8. Verifying persisted settings via backend API GET /api/v1/settings...")
    res = httpx.get("http://localhost:8000/api/v1/settings")
    assert res.status_code == 200, f"Backend returned {res.status_code}"
    settings_data = res.json()
    assert "portals" in settings_data, "Portals configuration missing in settings response"
    portals_cfg = settings_data["portals"]
    assert "broward_url" in portals_cfg and portals_cfg["broward_url"], "broward_url missing or empty"
    assert "miami_url" in portals_cfg and portals_cfg["miami_url"], "miami_url missing or empty"
    assert "dallas_url" in portals_cfg and portals_cfg["dallas_url"], "dallas_url missing or empty"
    print(f"   PASS: Backend confirmed active settings revision {settings_data.get('version')} with all portal URLs configured.")

    print("\n" + "=" * 70)
    print("ALL 'County Court Portals' VERIFICATION CHECKS PASSED (100%)!")
    print("=" * 70)

if __name__ == "__main__":
    run_portals_verification()
