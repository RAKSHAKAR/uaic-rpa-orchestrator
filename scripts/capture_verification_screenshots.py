import asyncio
import os
import sys
from playwright.async_api import async_playwright

async def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    images_dir = os.path.join(base_dir, "implementation_plan", "Images")
    os.makedirs(images_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1600, "height": 1100})
        page = await context.new_page()

        # ----------------------------------------------------
        # 1. Claim Detail Page Verification (FST-004)
        # ----------------------------------------------------
        claim_url = "http://localhost:3000/claims/1469bd79-fea4-4bcd-a98c-fd016b94efda"
        print(f"Navigating to {claim_url}...")
        await page.goto(claim_url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        # Scroll to Claim Logs & Diagnostic Center
        logs_header = page.locator("h3:has-text('Claim Logs & Diagnostic Center')").first
        if await logs_header.count() > 0:
            print("Found Claim Logs & Diagnostic Center header, scrolling...")
            await logs_header.scroll_into_view_if_needed()
            await page.wait_for_timeout(1000)

            # Screenshot audit logs latest first
            audit_latest_path = os.path.join(images_dir, "claim_audit_logs_sorted_latest.png")
            await page.screenshot(path=audit_latest_path, full_page=False)
            print(f"Saved: {audit_latest_path}")

            # Toggle sort button
            sort_toggle = page.locator("button:has-text('Latest First'), button:has-text('Oldest First')").first
            if await sort_toggle.count() > 0:
                print(f"Clicking sort toggle: {await sort_toggle.text_content()}...")
                await sort_toggle.click()
                await page.wait_for_timeout(1000)
                audit_oldest_path = os.path.join(images_dir, "claim_audit_logs_sorted_oldest.png")
                await page.screenshot(path=audit_oldest_path, full_page=False)
                print(f"Saved: {audit_oldest_path}")

                # Toggle back to latest
                await sort_toggle.click()
                await page.wait_for_timeout(500)

            # Click Processing Logs tab
            proc_tab = page.locator("button:has-text('Processing Logs')").first
            if await proc_tab.count() > 0:
                print("Clicking Processing Logs tab...")
                await proc_tab.click()
                await page.wait_for_timeout(1000)
                proc_logs_path = os.path.join(images_dir, "claim_processing_logs_sorted.png")
                await page.screenshot(path=proc_logs_path, full_page=False)
                print(f"Saved: {proc_logs_path}")

        # ----------------------------------------------------
        # 2. Settings Tab (Email & Notifications -> Delivery History Section)
        # ----------------------------------------------------
        settings_url = "http://localhost:3000/settings"
        print(f"Navigating to {settings_url}...")
        await page.goto(settings_url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        # Click Email & Notifications tab
        email_tab = page.locator("button:has-text('Email & Notifications')").first
        if await email_tab.count() > 0:
            print("Clicking Email & Notifications tab...")
            await email_tab.click()
            await page.wait_for_timeout(1500)

        # Scroll to Section 7 (#delivery-history-section)
        delivery_sec = page.locator("#delivery-history-section").first
        if await delivery_sec.count() > 0:
            print("Found #delivery-history-section, scrolling...")
            await delivery_sec.scroll_into_view_if_needed()
            await page.wait_for_timeout(1000)

            # Capture default view
            notif_def_path = os.path.join(images_dir, "notification_delivery_history_default.png")
            await page.screenshot(path=notif_def_path, full_page=False)
            print(f"Saved: {notif_def_path}")

            # Click Recipient column header
            recip_header = page.locator("#delivery-history-section button:has-text('Recipient')").first
            if await recip_header.count() > 0:
                print("Sorting by Recipient...")
                await recip_header.click()
                await page.wait_for_timeout(1000)
                notif_recip_path = os.path.join(images_dir, "notification_delivery_history_sorted_recipient.png")
                await page.screenshot(path=notif_recip_path, full_page=False)
                print(f"Saved: {notif_recip_path}")

            # Click Event column header
            event_header = page.locator("#delivery-history-section button:has-text('Event')").first
            if await event_header.count() > 0:
                print("Sorting by Event...")
                await event_header.click()
                await page.wait_for_timeout(1000)
                notif_event_path = os.path.join(images_dir, "notification_delivery_history_sorted_event.png")
                await page.screenshot(path=notif_event_path, full_page=False)
                print(f"Saved: {notif_event_path}")

            # Click Status column header
            status_header = page.locator("#delivery-history-section button:has-text('Status')").first
            if await status_header.count() > 0:
                print("Sorting by Status...")
                await status_header.click()
                await page.wait_for_timeout(1000)
                notif_status_path = os.path.join(images_dir, "notification_delivery_history_sorted_status.png")
                await page.screenshot(path=notif_status_path, full_page=False)
                print(f"Saved: {notif_status_path}")

        await browser.close()
        print("Complete visual verification capture finished successfully!")

if __name__ == "__main__":
    asyncio.run(main())
