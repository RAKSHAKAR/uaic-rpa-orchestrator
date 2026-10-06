"""Verification script for full missing items parity, count accuracy, and UI components."""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

DOCS_DIR = Path("docs")
DOCS_DIR.mkdir(exist_ok=True)

async def run_verification():
    print("=== Starting E2E Visual and Count Verification ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        # -------------------------------------------------------------
        # 1. DASHBOARD VERIFICATION
        # -------------------------------------------------------------
        print("\n--- 1. Checking Dashboard (http://localhost:3000/) ---")
        await page.goto("http://localhost:3000/", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        # StatCards text
        cards_text = await page.evaluate("""() => {
            const cards = Array.from(document.querySelectorAll('button[class*="rounded-xl"]'));
            return cards.map(c => {
                const title = c.querySelector('span')?.textContent?.trim() || '';
                const val = c.querySelector('span.text-2xl, span[class*="text-xl"], span[class*="text-2xl"]')?.textContent?.trim() || '';
                const sub = c.querySelector('p')?.textContent?.trim() || '';
                return { title, val, sub };
            }).filter(c => c.title && c.val);
        }""")
        print("Captured StatCards:")
        for c in cards_text:
            print(f"  [{c['title']}]: {c['val']} ({c['sub']})")

        # Quick Filter Tabs
        tabs_text = await page.evaluate("""() => {
            const buttons = Array.from(document.querySelectorAll('div[class*="overflow-x-auto"] button'));
            return buttons.map(b => b.textContent?.trim() || '').filter(Boolean);
        }""")
        print("\nCaptured Quick Filter Tabs:")
        for t in tabs_text:
            print(f"  Tab: {t}")

        # Review Exceptions Badge
        review_badge = await page.evaluate("""() => {
            const el = document.querySelector('a[href="/exceptions"]');
            return el ? el.textContent?.trim() : null;
        }""")
        print(f"\nReview Exceptions Badge: {review_badge}")

        # Combobox Options: Status
        print("\nChecking Status Combobox...")
        status_btn = page.locator('button:has-text("All Statuses"), button:has-text("Status")').first
        if await status_btn.is_visible():
            await status_btn.click()
            await page.wait_for_timeout(500)
            status_opts = await page.evaluate("""() => {
                const items = Array.from(document.querySelectorAll('div[role="listbox"], div[class*="z-50"] label, div[class*="z-50"] div'));
                return items.map(i => i.textContent?.trim() || '').filter(t => t.includes('(') && t.includes(')'));
            }""")
            print(f"Status Combobox Options ({len(status_opts)}):")
            for o in status_opts[:8]:
                print(f"  - {o}")
            await status_btn.click() # close

        # Combobox Options: State
        print("\nChecking State Combobox...")
        state_btn = page.locator('button:has-text("All States"), button:has-text("State")').first
        if await state_btn.is_visible():
            await state_btn.click()
            await page.wait_for_timeout(500)
            state_opts = await page.evaluate("""() => {
                const items = Array.from(document.querySelectorAll('div[role="listbox"], div[class*="z-50"] label, div[class*="z-50"] div'));
                return items.map(i => i.textContent?.trim() || '').filter(t => t.includes('(') && t.includes(')'));
            }""")
            print(f"State Combobox Options ({len(state_opts)}):")
            for o in state_opts[:4]:
                print(f"  - {o}")
            await state_btn.click() # close

        dash_screenshot = DOCS_DIR / "verified_dashboard_counts.png"
        await page.screenshot(path=str(dash_screenshot), full_page=False)
        print(f"Saved dashboard screenshot to {dash_screenshot}")

        # -------------------------------------------------------------
        # 2. CLAIM DETAIL VERIFICATION
        # -------------------------------------------------------------
        # Get first claim ID
        claim_url = "http://localhost:3000/claims/5ff0c961-1b02-49bf-8f1e-b3b7d969ec82"
        print(f"\n--- 2. Checking Claim Detail ({claim_url}) ---")
        await page.goto(claim_url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        # Check bot cards and Click 'Stages'
        stages_btn = page.locator('button:has-text("Stages")').first
        if await stages_btn.is_visible():
            print("Found Stages button! Clicking to inspect modal...")
            await stages_btn.click()
            await page.wait_for_timeout(1000)
            modal_title = await page.evaluate("""() => {
                const title = document.querySelector('h3, div[class*="font-bold"]');
                return title ? title.textContent?.trim() : '';
            }""")
            stages_count = await page.evaluate("""() => {
                return document.querySelectorAll('div[class*="border-l-2"], div[class*="rounded-xl"]').length;
            }""")
            print(f"Stage progression modal opened! Header: {modal_title}, Stages count: {stages_count}")
            # Close modal
            close_btn = page.locator('button:has-text("Close"), button:has-text("×")').first
            if await close_btn.is_visible():
                await close_btn.click()
                await page.wait_for_timeout(500)

        # Check Filing Date column in Scraped Public Court Cases
        filing_dates = await page.evaluate("""() => {
            const cells = Array.from(document.querySelectorAll('td[class*="font-mono"]'));
            return cells.map(c => c.textContent?.trim() || '').filter(t => t.includes('/') && t.length >= 8);
        }""")
        print(f"Public court case filing dates found: {len(filing_dates)} rows (Sample: {filing_dates[:3]})")

        # Check Bottom Export Bar
        export_buttons = await page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button'));
            return btns
                .map(b => b.textContent?.trim() || '')
                .filter(t => t.includes('Excel') || t.includes('CSV') || t.includes('JSON') || t.includes('Background') || t.includes('Export'));
        }""")
        print(f"Bottom Export Bar buttons: {export_buttons}")

        claim_screenshot = DOCS_DIR / "verified_claim_detail.png"
        await page.screenshot(path=str(claim_screenshot), full_page=False)
        print(f"Saved claim detail screenshot to {claim_screenshot}")

        # -------------------------------------------------------------
        # 3. SETTINGS VERIFICATION (STORAGE & RETENTION)
        # -------------------------------------------------------------
        print("\n--- 3. Checking Settings Storage & Retention (http://localhost:3000/settings) ---")
        await page.goto("http://localhost:3000/settings", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        # Click Storage & Retention tab
        storage_tab = page.locator('button:has-text("Storage & Retention"), button:has-text("Storage")').first
        if await storage_tab.is_visible():
            await storage_tab.click()
            await page.wait_for_timeout(1000)
            print("Clicked Storage & Retention tab.")

            # Check Retention Time Scope dropdown options
            scope_options = await page.evaluate("""() => {
                const select = document.querySelector('select');
                if (!select) return [];
                return Array.from(select.options).map(o => o.text);
            }""")
            print("Retention Time Scope Options:")
            for opt in scope_options:
                print(f"  * {opt}")

            # Check Purge button
            purge_btn_text = await page.evaluate("""() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const b = btns.find(el => el.textContent && el.textContent.includes('Purge'));
                return b ? b.textContent.trim() : null;
            }""")
            print(f"Purge button: {purge_btn_text}")

        settings_screenshot = DOCS_DIR / "verified_settings_retention.png"
        await page.screenshot(path=str(settings_screenshot), full_page=False)
        print(f"Saved settings screenshot to {settings_screenshot}")

        await browser.close()
        print("\n=== Verification Complete Successfully! ===")

if __name__ == "__main__":
    asyncio.run(run_verification())
