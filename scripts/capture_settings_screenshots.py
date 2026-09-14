"""Capture full-resolution, high-quality screenshots of the Settings page:
- Email Provider Selection (6 cards: Mock, MailDev, Direct MX, SMTP, Graph, SES)
- Microsoft Graph and Amazon SES configuration inputs with eye toggles
- Template Studio & Designer (Editor Mode and Framed Live Preview Mode)
- Outbound Notification Delivery History table cleanly framed
- Email Delivery Receipt inspection modal with high-contrast darkened backdrop
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import shutil

output_dir = Path(__file__).resolve().parent.parent / "implementation_plan" / "Images"
output_dir.mkdir(parents=True, exist_ok=True)


async def capture_settings():
    print("Launching Playwright to inspect and capture Settings page...")
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
        print("Waiting for 'Email & Notifications' tab...")
        email_btn = page.locator("button:has-text('Email & Notifications')").first
        await email_btn.wait_for(state="visible", timeout=20000)
        print("Clicking 'Email & Notifications' tab...")
        await email_btn.click()
        await page.wait_for_timeout(1000)

        # Wait for Email Provider section
        await page.locator("text=Outbound Email Provider Configuration").first.wait_for(state="visible", timeout=10000)
        print("Email configuration section visible.")

        # 1. Outbound Email Provider Configuration
        p1 = output_dir / "settings_email_providers_view.png"
        await page.evaluate("window.scrollTo(0, 0);")
        await page.wait_for_timeout(500)
        await page.screenshot(path=str(p1), full_page=False)
        print(f"Captured: {p1}")

        # 2. Microsoft Graph API
        graph_card = page.locator("text=Microsoft Graph API").first
        if await graph_card.is_visible():
            await graph_card.click()
            await page.locator("text=Azure AD / M365 Tenant ID").first.wait_for(state="visible", timeout=5000)
            await page.wait_for_timeout(500)
            p2 = output_dir / "settings_microsoft_graph_view.png"
            await page.screenshot(path=str(p2), full_page=False)
            print(f"Captured: {p2}")

        # 3. Amazon SES API
        ses_card = page.locator("text=Amazon SES API").first
        if await ses_card.is_visible():
            await ses_card.click()
            await page.locator("text=AWS Region").first.wait_for(state="visible", timeout=5000)
            await page.wait_for_timeout(500)
            p3 = output_dir / "settings_amazon_ses_view.png"
            await page.screenshot(path=str(p3), full_page=False)
            print(f"Captured: {p3}")

        # 4. Template Studio - Editor Mode
        print("Inspecting Template Studio...")
        template_title = page.locator("text=Dynamic Email Template Studio & Designer").first
        await template_title.wait_for(state="visible", timeout=10000)

        # Wait for template selector pills to load from backend
        tpl_pill = page.locator("button:has-text('Court Case Match Found'), button:has-text('Guidewire Activity Created')").first
        await tpl_pill.wait_for(state="visible", timeout=10000)
        await tpl_pill.click()
        await page.wait_for_timeout(800)

        # Switch to Editor Mode if not active
        editor_btn = page.locator("button:has-text('Editor & Design')").first
        if await editor_btn.is_visible():
            await editor_btn.click()
            await page.wait_for_timeout(500)

        # Wait for rendered preview card to contain real content (not blank)
        preview_card = page.locator(".max-w-xl").first
        await preview_card.wait_for(state="visible", timeout=10000)

        # Scroll to template studio section cleanly
        await page.evaluate("""
            const section = document.getElementById('template-studio-section');
            if (section) {
                section.scrollIntoView({ behavior: 'instant', block: 'start' });
            }
        """)
        await page.wait_for_timeout(600)
        p_tpl_edit = output_dir / "settings_template_studio_editor.png"
        await page.screenshot(path=str(p_tpl_edit), full_page=False)
        print(f"Captured: {p_tpl_edit}")

        # 5. Template Studio - Fullscreen Live Preview Tab
        preview_btn = page.locator("button:has-text('Live Preview')").first
        await preview_btn.wait_for(state="visible", timeout=5000)
        await preview_btn.click()
        await page.wait_for_timeout(800)

        # Wait for live preview container
        live_preview_card = page.locator(".max-w-2xl").first
        await live_preview_card.wait_for(state="visible", timeout=10000)

        # Scroll to template studio section again for clean framing
        await page.evaluate("""
            const section = document.getElementById('template-studio-section');
            if (section) {
                section.scrollIntoView({ behavior: 'instant', block: 'start' });
            }
        """)
        await page.wait_for_timeout(600)
        p_tpl_prev = output_dir / "settings_template_studio_preview.png"
        await page.screenshot(path=str(p_tpl_prev), full_page=False)
        print(f"Captured: {p_tpl_prev}")

        # 6. Outbound Notification Delivery History
        print("Waiting for Notification Delivery History table records...")
        table_row = page.locator("table tbody tr").first
        await table_row.wait_for(state="visible", timeout=15000)

        print("Scrolling cleanly to Delivery History section...")
        await page.evaluate("""
            const section = document.getElementById('delivery-history-section');
            if (section) {
                section.scrollIntoView({ behavior: 'instant', block: 'start' });
            }
        """)
        await page.wait_for_timeout(800)
        p4 = output_dir / "settings_delivery_history_view.png"
        await page.screenshot(path=str(p4), full_page=False)
        print(f"Captured: {p4}")

        # Also update AE-024 table screenshot
        p_ae024_table = output_dir / "AE-024_outbound_delivery_history.png"
        shutil.copy2(p4, p_ae024_table)
        print(f"Copied to: {p_ae024_table}")

        # 7. Delivery Receipt Modal
        print("Locating 'View Receipt' button for a SENT notification...")
        # Find a View Receipt button on a row with SENT status or first row
        receipt_btns = page.locator("button:has-text('View Receipt')")
        btn_count = await receipt_btns.count()
        print(f"Found {btn_count} 'View Receipt' buttons.")

        if btn_count > 0:
            # Click the second button (which corresponds to SENT smtp record with full receipt) if available, else first
            target_btn = receipt_btns.nth(1) if btn_count > 1 else receipt_btns.first
            await target_btn.click()
            await page.wait_for_timeout(600)

            # Ensure modal is visible
            modal_title = page.locator("text=Email Delivery Receipt & Provenance").first
            await modal_title.wait_for(state="visible", timeout=5000)
            await page.locator("text=Raw Receipt JSON Payload").first.wait_for(state="visible", timeout=5000)
            await page.wait_for_timeout(500)

            p5 = output_dir / "settings_delivery_receipt_modal.png"
            await page.screenshot(path=str(p5), full_page=False)
            print(f"Captured: {p5}")

        await browser.close()
        print("Finished capture_settings execution successfully.")


if __name__ == "__main__":
    asyncio.run(capture_settings())
