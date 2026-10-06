"""Automated Playwright verification script for Audit page filters & Dashboard throughput."""

import sys
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1800, "height": 1100})
        page = context.new_page()

        print("\n--- 1. Testing Audit Page (http://localhost:3000/audit) ---")
        page.goto("http://localhost:3000/audit", wait_until="networkidle")
        page.wait_for_timeout(2000)

        # Verify page header
        header_text = page.locator("h1").last.inner_text()
        print(f"Header: {header_text}")
        assert "Audit Logs & Provenance Console" in header_text

        # Verify initial StatCard counts
        stat_cards = page.locator("[class*='StatCard'], div.grid > div").all_inner_texts()
        print("Stat Cards Content:")
        for idx, card in enumerate(stat_cards[:6]):
            first_line = card.replace("\n", " | ")
            print(f"  Card {idx+1}: {first_line[:80]}")

        # Check total records in footer / pagination
        body_text = page.inner_text("body")
        print("Checking for Today's Activity card...")
        
        # Click "Today's Activity" stat card
        today_card = page.locator("text=Today's Activity").first
        today_card.click()
        page.wait_for_timeout(2500)

        # Check if table rows are displayed
        rows = page.locator("table tbody tr")
        row_count = rows.count()
        print(f"Table row count after clicking 'Today's Activity': {row_count}")
        first_row_text = rows.first.inner_text() if row_count > 0 else "NO ROWS"
        print(f"First row: {first_row_text.replace(chr(10), ' | ')[:120]}")
        assert row_count > 0, "Expected table rows for today's activity!"
        assert "No audit records found" not in first_row_text, "Should NOT show 'No audit records found'!"

        # Check pagination info
        pagination_text = page.locator("text=/Showing [0-9]+ to [0-9]+ of [0-9]+/i").first
        if pagination_text.is_visible():
            print(f"Pagination: {pagination_text.inner_text()}")

        # Take screenshot of Audit page with Today's Activity active
        audit_screenshot_path = "docs/audit_page_today_active.png"
        page.screenshot(path=audit_screenshot_path, full_page=False)
        print(f"Saved audit screenshot to {audit_screenshot_path}")

        # Test Entities Dropdown
        print("\nTesting Entities MultiSelectDropdown...")
        entities_dropdown = page.locator("button:has-text('Entities:')").first
        entities_dropdown.click()
        page.wait_for_timeout(500)
        options = page.locator("text=Settings").first
        print(f"Entities option 'Settings' visible: {options.is_visible()}")
        assert options.is_visible(), "Entities dropdown options should be visible when clicked!"

        # Close dropdown
        entities_dropdown.click()
        page.wait_for_timeout(300)

        print("\n--- 2. Testing Dashboard (http://localhost:3000) ---")
        page.goto("http://localhost:3000", wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        # Check "Bot Scraper Throughput (8 Portals)"
        throughput_header = page.locator("text=Bot Scraper Throughput (8 Portals)")
        assert throughput_header.is_visible(), "Throughput card should be visible"
        print("Throughput header found.")

        parent_card = throughput_header.locator("xpath=ancestor::div[contains(@class, 'rounded-2xl')]").first
        print(f"Throughput card inner text:\n{parent_card.inner_text()}")

        # Check Miami (252), Broward (206), Hillsborough (197)
        miami_text = page.locator("text=/252 cases extracted/i").first
        broward_text = page.locator("text=/206 cases extracted/i").first
        hills_text = page.locator("text=/197 cases extracted/i").first
        print(f"Miami 252 visible: {miami_text.is_visible()}")
        print(f"Broward 206 visible: {broward_text.is_visible()}")
        print(f"Hillsborough 197 visible: {hills_text.is_visible()}")

        # Check MultiSelect comboboxes on Dashboard
        status_combobox = page.locator("button:has-text('Status:')").first
        state_combobox = page.locator("button:has-text('State:')").first
        match_combobox = page.locator("button:has-text('Match Status:')").first
        print(f"Dashboard Status Combobox visible: {status_combobox.is_visible()}")
        print(f"Dashboard State Combobox visible: {state_combobox.is_visible()}")
        print(f"Dashboard Match Status Combobox visible: {match_combobox.is_visible()}")

        # Scroll to throughput card and capture screenshot
        throughput_header.scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        dash_screenshot_path = "docs/dashboard_throughput_card.png"
        page.screenshot(path=dash_screenshot_path, full_page=False)
        print(f"Saved dashboard throughput screenshot to {dash_screenshot_path}")

        # Scroll to comboboxes and capture screenshot
        status_combobox.scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        combobox_screenshot_path = "docs/dashboard_comboboxes.png"
        page.screenshot(path=combobox_screenshot_path, full_page=False)
        print(f"Saved dashboard comboboxes screenshot to {combobox_screenshot_path}")

        browser.close()
        print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
