import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    images_dir = os.path.join(base_dir, "implementation_plan", "Images")
    os.makedirs(images_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1600, "height": 1100})
        page = await context.new_page()

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
            await delivery_sec.scroll_into_view_if_needed()
            await page.wait_for_timeout(1000)

            # Click Recipient column header
            recip_header = page.locator("#delivery-history-section th:has-text('Recipient')").first
            if await recip_header.count() > 0:
                print("Sorting by Recipient...")
                await recip_header.click()
                await page.wait_for_timeout(1500)
                path = os.path.join(images_dir, "notification_delivery_history_sorted_recipient.png")
                await page.screenshot(path=path, full_page=False)
                print(f"Saved: {path}")

            # Click Event column header
            event_header = page.locator("#delivery-history-section th:has-text('Event')").first
            if await event_header.count() > 0:
                print("Sorting by Event...")
                await event_header.click()
                await page.wait_for_timeout(1500)
                path = os.path.join(images_dir, "notification_delivery_history_sorted_event.png")
                await page.screenshot(path=path, full_page=False)
                print(f"Saved: {path}")

            # Click Status column header
            status_header = page.locator("#delivery-history-section th:has-text('Status')").first
            if await status_header.count() > 0:
                print("Sorting by Status...")
                await status_header.click()
                await page.wait_for_timeout(1500)
                path = os.path.join(images_dir, "notification_delivery_history_sorted_status.png")
                await page.screenshot(path=path, full_page=False)
                print(f"Saved: {path}")

        await browser.close()
        print("Done capturing notification sorting views!")

if __name__ == "__main__":
    asyncio.run(main())
