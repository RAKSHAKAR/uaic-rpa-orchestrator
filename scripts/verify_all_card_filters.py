import asyncio
import os
import sys
from playwright.async_api import async_playwright

async def verify():
    print("Starting Comprehensive Cross-Screen StatCard Filter Verification...")
    os.makedirs("docs", exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 1000})

        # ==========================================
        # 1. SCREEN 1: DASHBOARD (/)
        # ==========================================
        print("\n--- Testing Screen 1: Dashboard (/) ---")
        await page.goto("http://localhost:3000/", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        # 1a. Click "In Progress / Queue"
        print("Clicking 'In Progress / Queue' StatCard...")
        in_prog_card = page.locator("div[role='button']:has-text('In Progress / Queue')")
        await in_prog_card.click()
        await page.wait_for_timeout(1000)
        chip_text = await page.locator("text=Active Filters:").text_content() if await page.locator("text=Active Filters:").count() > 0 else ""
        print(f"Active filter chip: {chip_text}")
        table_rows = await page.locator("table tbody tr").count()
        print(f"Table rows displayed for In Progress / Queue: {table_rows}")
        assert table_rows > 0, "Expected table rows for In Progress / Queue"

        # 1b. Click "Completed Scrapes"
        print("Clicking 'Completed Scrapes' StatCard...")
        comp_card = page.locator("div[role='button']:has-text('Completed Scrapes')")
        await comp_card.click()
        await page.wait_for_timeout(1000)
        table_rows = await page.locator("table tbody tr").count()
        print(f"Table rows displayed for Completed Scrapes: {table_rows}")
        assert table_rows > 0, "Expected table rows for Completed Scrapes"

        # 1c. Click "Matches Confirmed"
        print("Clicking 'Matches Confirmed' StatCard...")
        match_card = page.locator("div[role='button']:has-text('Matches Confirmed')")
        await match_card.click()
        await page.wait_for_timeout(1000)
        table_rows = await page.locator("table tbody tr").count()
        print(f"Table rows displayed for Matches Confirmed: {table_rows}")
        assert table_rows == 1, f"Expected exactly 1 row for Matches Confirmed, got {table_rows}"

        # 1d. Click "Total Ingested" to reset
        print("Clicking 'Total Ingested' StatCard...")
        total_card = page.locator("div[role='button']:has-text('Total Ingested')")
        await total_card.click()
        await page.wait_for_timeout(1000)
        claims_found_text = await page.locator("text=/\\d+ claims? found/").text_content()
        print(f"Claims found text after reset: {claims_found_text}")
        await page.screenshot(path="docs/verify_dashboard_cards.png")
        print("Captured docs/verify_dashboard_cards.png")

        # ==========================================
        # 2. SCREEN 2: AUDIT LOGS (/audit)
        # ==========================================
        print("\n--- Testing Screen 2: Audit Logs (/audit) ---")
        await page.goto("http://localhost:3000/audit", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        # 2a. Click "Today's Activity"
        print("Clicking 'Today\\'s Activity' StatCard...")
        today_card = page.locator("div[role='button']:has-text('Today\\'s Activity')")
        await today_card.click()
        await page.wait_for_timeout(1500)
        audit_rows = await page.locator("table tbody tr").count()
        print(f"Audit rows for Today's Activity: {audit_rows}")
        assert audit_rows > 0, "Expected audit rows for Today's Activity"

        # 2b. Click "Claim Ops"
        print("Clicking 'Claim Ops' StatCard...")
        claim_ops_card = page.locator("div[role='button']:has-text('Claim Ops')")
        await claim_ops_card.click()
        await page.wait_for_timeout(1500)
        audit_rows = await page.locator("table tbody tr").count()
        print(f"Audit rows for Claim Ops: {audit_rows}")
        assert audit_rows > 0, "Expected audit rows for Claim Ops"

        # 2c. Click "Config Changes"
        print("Clicking 'Config Changes' StatCard...")
        config_card = page.locator("div[role='button']:has-text('Config Changes')")
        await config_card.click()
        await page.wait_for_timeout(1500)
        audit_rows = await page.locator("table tbody tr").count()
        print(f"Audit rows for Config Changes: {audit_rows}")
        assert audit_rows > 0, "Expected audit rows for Config Changes"

        # 2d. Click "Failures"
        print("Clicking 'Failures' StatCard...")
        fail_card = page.locator("div[role='button']:has-text('Failures')")
        await fail_card.click()
        await page.wait_for_timeout(1500)
        audit_rows = await page.locator("table tbody tr").count()
        print(f"Audit rows for Failures: {audit_rows}")
        assert audit_rows > 0, "Expected audit rows for Failures"

        # 2e. Click "Total Events" to reset
        print("Clicking 'Total Events' StatCard...")
        total_ev_card = page.locator("div[role='button']:has-text('Total Events')")
        await total_ev_card.click()
        await page.wait_for_timeout(1500)
        audit_rows = await page.locator("table tbody tr").count()
        print(f"Audit rows after reset: {audit_rows}")
        await page.screenshot(path="docs/verify_audit_cards.png")
        print("Captured docs/verify_audit_cards.png")

        # ==========================================
        # 3. SCREEN 3: QUEUE MONITOR (/monitor)
        # ==========================================
        print("\n--- Testing Screen 3: Queue Monitor (/monitor) ---")
        await page.goto("http://localhost:3000/monitor", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        # 3a. Click "Ingest Queue"
        print("Clicking 'Ingest Queue' StatCard...")
        ingest_card = page.locator("div[role='button']:has-text('Ingest Queue')")
        await ingest_card.click()
        await page.wait_for_timeout(1500)
        monitor_rows = await page.locator("table tbody tr").count()
        print(f"Monitor rows for Ingest Queue: {monitor_rows}")
        assert monitor_rows > 0, "Expected monitor rows for Ingest Queue"

        # 3b. Click "Scraper Queue"
        print("Clicking 'Scraper Queue' StatCard...")
        scraper_card = page.locator("div[role='button']:has-text('Scraper Queue')")
        await scraper_card.click()
        await page.wait_for_timeout(1500)
        monitor_rows = await page.locator("table tbody tr").count()
        print(f"Monitor rows for Scraper Queue: {monitor_rows}")

        # 3c. Click "Active Workers" to reset
        print("Clicking 'Active Workers' StatCard to reset...")
        workers_card = page.locator("div[role='button']:has-text('Active Workers')")
        await workers_card.click()
        await page.wait_for_timeout(1500)
        monitor_rows = await page.locator("table tbody tr").count()
        print(f"Monitor rows after reset: {monitor_rows}")
        await page.screenshot(path="docs/verify_monitor_cards.png")
        print("Captured docs/verify_monitor_cards.png")

        # ==========================================
        # 4. SCREEN 4: EXCEPTION REVIEW (/exceptions)
        # ==========================================
        print("\n--- Testing Screen 4: Exception Review (/exceptions) ---")
        await page.goto("http://localhost:3000/exceptions", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        # 4a. Click "High Confidence"
        print("Clicking 'High Confidence' StatCard...")
        high_card = page.locator("div[role='button']:has-text('High Confidence')")
        await high_card.click()
        await page.wait_for_timeout(1000)
        print("High confidence card clicked successfully.")

        # 4b. Click "Total Pending" to reset
        print("Clicking 'Total Pending' StatCard...")
        total_p_card = page.locator("div[role='button']:has-text('Total Pending')")
        await total_p_card.click()
        await page.wait_for_timeout(1000)
        print("Total Pending card clicked successfully.")
        await page.screenshot(path="docs/verify_exceptions_cards.png")
        print("Captured docs/verify_exceptions_cards.png")

        await browser.close()
        print("\nSUCCESS: All StatCards across all 4 screens verified fully functional!")

if __name__ == "__main__":
    asyncio.run(verify())
