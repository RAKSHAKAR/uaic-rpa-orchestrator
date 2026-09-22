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

        url = "http://localhost:3000/exceptions"
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2500)

        # 1. Screenshot of Table View with Inspect button
        inspect_btn = page.locator("button:has-text('Inspect')").first
        await inspect_btn.wait_for(state="visible", timeout=10000)
        table_path = os.path.join(images_dir, "exceptions_inspect_button_table.png")
        await page.screenshot(path=table_path, full_page=False)
        print(f"Saved: {table_path}")

        # 2. Click Inspect button
        print("Clicking Inspect button...")
        await inspect_btn.click()
        await page.wait_for_timeout(1000)

        # Wait for modal header
        modal_header = page.locator("h3:has-text('Candidate Match Inspection & Resolution')").first
        await modal_header.wait_for(state="visible", timeout=5000)

        modal_open_path = os.path.join(images_dir, "exceptions_match_inspection_modal_open.png")
        await page.screenshot(path=modal_open_path, full_page=False)
        print(f"Saved: {modal_open_path}")

        # 3. Enter Adjuster Legal Justification Notes
        notes_textarea = page.locator("textarea").first
        if await notes_textarea.count() > 0:
            justification = (
                "Cross-referenced incident police docket with insured vehicle identification number (VIN) "
                "and claimant driver license records. Approved for Guidewire sync."
            )
            await notes_textarea.fill(justification)
            await page.wait_for_timeout(500)

            reviewer_input = page.locator("input[placeholder='Claims Adjuster']").first
            if await reviewer_input.count() > 0:
                await reviewer_input.fill("Senior Adjuster Jane Vance")
                await page.wait_for_timeout(500)

            notes_path = os.path.join(images_dir, "exceptions_match_inspection_modal_notes.png")
            await page.screenshot(path=notes_path, full_page=False)
            print(f"Saved: {notes_path}")

        await browser.close()
        print("Capture completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
