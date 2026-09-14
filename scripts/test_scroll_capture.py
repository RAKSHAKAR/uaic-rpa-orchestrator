import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import shutil

output_dir = Path(__file__).resolve().parent.parent / "implementation_plan" / "Images"

async def test_capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1600, "height": 1000},
            device_scale_factor=2,
        )
        page = await context.new_page()

        print("Navigating to http://localhost:3000/settings ...")
        await page.goto("http://localhost:3000/settings", wait_until="load")

        # Wait for tab buttons to appear
        email_btn = page.locator("button:has-text('Email & Notifications')").first
        await email_btn.wait_for(state="visible", timeout=20000)
        await email_btn.click()
        await page.wait_for_timeout(1500)

        # 1. Template Studio - Editor Mode
        tpl_section = page.locator("text=Dynamic Email Template Studio & Designer").first
        await tpl_section.evaluate("el => el.scrollIntoView({ behavior: 'instant', block: 'start' })")
        await page.evaluate("window.scrollBy(0, -20);")
        await page.wait_for_timeout(600)
        p_tpl_edit = output_dir / "settings_template_studio_editor.png"
        await page.screenshot(path=str(p_tpl_edit))
        print("Captured editor:", p_tpl_edit)

        # 2. Switch to Live Preview Tab and wait for preview to finish rendering
        preview_btn = page.locator("button:has-text('Live Preview')").first
        await preview_btn.click()
        # Wait until 'Rendering dynamic template preview...' disappears
        await page.wait_for_timeout(2000)
        p_tpl_prev = output_dir / "settings_template_studio_preview.png"
        await page.screenshot(path=str(p_tpl_prev))
        print("Captured preview:", p_tpl_prev)

        # 3. Delivery History Section - scroll cleanly to start
        hist_section = page.locator("#delivery-history-section").first
        await hist_section.evaluate("el => el.scrollIntoView({ behavior: 'instant', block: 'start' })")
        await page.evaluate("window.scrollBy(0, -20);")
        await page.wait_for_timeout(800)
        p_hist = output_dir / "settings_delivery_history_view.png"
        await page.screenshot(path=str(p_hist))
        print("Captured history:", p_hist)
        shutil.copy2(p_hist, output_dir / "AE-024_outbound_delivery_history.png")

        # 4. View Receipt Modal
        receipt_btn = page.locator("button:has-text('View Receipt')").first
        await receipt_btn.click()
        modal_title = page.locator("text=Email Delivery Receipt & Provenance").first
        await modal_title.wait_for(state="visible", timeout=5000)
        await page.wait_for_timeout(800)
        p_modal = output_dir / "settings_delivery_receipt_modal.png"
        await page.screenshot(path=str(p_modal))
        print("Captured receipt modal:", p_modal)

        await browser.close()
        print("Done!")

if __name__ == '__main__':
    asyncio.run(test_capture())
