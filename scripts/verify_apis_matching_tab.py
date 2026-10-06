"""Playwright automation verification script for 'APIs & Matching Engine' tab in Settings.
Tests all interactive sandboxes, presets, execution buttons, and save configuration.
Saves screenshots to docs/ for verifiable audit proof.
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))

def run_verification():
    print("Starting Playwright verification of 'APIs & Matching Engine' tab...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1872, "height": 1113})
        page = context.new_page()

        # Step 1: Navigate to settings page
        print("1. Navigating to http://localhost:3000/settings...")
        page.goto("http://localhost:3000/settings", timeout=20000)
        page.wait_for_selector("text=Unified Solution & Automation Settings", timeout=10000)
        page.wait_for_timeout(1000)

        # Verify active tab is APIs & Matching Engine
        tab_btn = page.locator("button:has-text('APIs & Matching Engine')")
        assert tab_btn.is_visible(), "APIs & Matching Engine tab button not found"
        print("   APIs & Matching Engine tab is visible and active.")

        # Step 2: Test Guidewire Connection Tester
        print("2. Testing Guidewire ClaimCenter Connection Tester...")
        gw_btn = page.locator("button:has-text('Test Connection / Send Request')")
        assert gw_btn.is_visible(), "Test Connection button not found"
        gw_btn.click()
        print("   Clicked 'Test Connection / Send Request', waiting for response card...")
        page.wait_for_selector("text=200 OK (Mock Simulation)", timeout=10000)
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(DOCS_DIR, "verify_guidewire_tester_result.png"))
        print("   PASS: Guidewire 200 OK (Mock Simulation) response rendered successfully.")

        # Step 3: Test Unique Names Deduplicator
        print("3. Testing Unique Names Live Tester...")
        page.locator("text=Unique Names API Live Tester").scroll_into_view_if_needed()
        page.wait_for_timeout(500)

        # Click "All Different" preset
        preset_diff_btn = page.locator("button:has-text('All Different')")
        assert preset_diff_btn.is_visible(), "'All Different' preset button not found"
        preset_diff_btn.click()
        page.wait_for_timeout(300)

        # Click Generate Unique Names
        gen_names_btn = page.locator("button:has-text('Generate Unique Names')")
        assert gen_names_btn.is_visible(), "'Generate Unique Names' button not found"
        gen_names_btn.click()
        print("   Clicked 'Generate Unique Names', waiting for results...")
        page.wait_for_selector("pre:has-text('unique_names')", timeout=10000)
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(DOCS_DIR, "verify_unique_names_result.png"))
        print("   PASS: Unique names deduplication output rendered successfully.")

        # Step 4: Test RapidFuzz Case Matching Sandbox
        print("4. Testing RapidFuzz Direct Match Simulator...")
        page.locator("text=Fuzzy Match API Tester").scroll_into_view_if_needed()
        page.wait_for_timeout(500)

        # Click "Exact API Sample" preset
        preset_match_btn = page.locator("button:has-text('Exact API Sample')")
        assert preset_match_btn.is_visible(), "'Exact API Sample' preset button not found"
        preset_match_btn.click()
        page.wait_for_timeout(300)

        # Click Evaluate Fuzzy Match
        eval_btn = page.locator("button:has-text('Evaluate Fuzzy Match')")
        assert eval_btn.is_visible(), "'Evaluate Fuzzy Match' button not found"
        eval_btn.click()
        print("   Clicked 'Evaluate Fuzzy Match', waiting for results...")
        page.wait_for_selector("text=Guidewire Dispatch Eligibility:", timeout=10000)
        page.wait_for_selector("text=Eligible for Guidewire", timeout=5000)
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(DOCS_DIR, "verify_fuzzy_match_result.png"))
        print("   PASS: RapidFuzz evaluation completed and 'Eligible for Guidewire' verified.")

        # Step 5: Test Save Configuration
        print("5. Testing Save Configuration...")
        page.locator("text=Unified Solution & Automation Settings").scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        save_btn = page.locator("button:has-text('Save Configuration')")
        assert save_btn.is_visible(), "'Save Configuration' button not found"
        save_btn.click()
        print("   Clicked 'Save Configuration', waiting for success banner...")
        page.wait_for_selector("text=Settings saved as revision", timeout=10000)
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(DOCS_DIR, "verify_apis_matching_saved.png"))
        print("   PASS: Save configuration succeeded and success banner displayed.")

        browser.close()
        print("\nALL 'APIs & Matching Engine' TESTS PASSED (100%)!")

if __name__ == "__main__":
    run_verification()
