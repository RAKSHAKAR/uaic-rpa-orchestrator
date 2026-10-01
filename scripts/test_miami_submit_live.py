import asyncio
import os
import sys

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            print("1. Navigating to Miami OCS...")
            await page.goto("https://www2.miamidadeclerk.gov/ocs", wait_until="domcontentloaded", timeout=25000)
            await asyncio.sleep(2)
            
            # Click Party Name tab
            party_link = page.locator("span.subitem-color[role='button']:has-text('Party Name'), span:has-text('Party Name')")
            if await party_link.count() > 0:
                print("Clicking Party Name tab...")
                await party_link.first.click()
                await asyncio.sleep(1)
                
            # Fill inputs exactly like miami.py
            last_inp = page.locator("input#partyLastName, #partyLastName")
            first_inp = page.locator("input#partyFirstName, #partyFirstName")
            date_from = page.locator("input#filingDateFrom, #filingDateFrom")
            date_to = page.locator("input#filingDateTo, #filingDateTo")
            
            print("Filling inputs...")
            await last_inp.fill("User")
            await first_inp.fill("Test")
            await date_from.fill("2024-10-01")
            await date_to.fill("2026-10-01")
            await asyncio.sleep(1)
            
            # Check values
            vals = await page.evaluate('''() => ({
                last: document.getElementById('partyLastName')?.value,
                first: document.getElementById('partyFirstName')?.value,
                from: document.getElementById('filingDateFrom')?.value,
                to: document.getElementById('filingDateTo')?.value,
            })''')
            print("Current input values in DOM:", vals)
            
            # Check search button
            btn = page.locator("button.btn.button-green[type='submit'], button.button-green")
            btn_cnt = await btn.count()
            print("Search button count:", btn_cnt)
            if btn_cnt > 0:
                print("Button visible:", await btn.first.is_visible())
                print("Button outerHTML:", await btn.first.evaluate("el => el.outerHTML"))
                print("Button disabled:", await btn.first.evaluate("el => el.disabled"))
                
                # Try clicking
                print("Attempting to click button with Playwright click()...")
                await btn.first.click()
                await asyncio.sleep(3)
                
                # Check current URL and DOM
                print("URL after click:", page.url)
                body_txt = await page.inner_text("body")
                print("Body snippet after click:", body_txt[:300].replace('\n', ' '))
                
                # Check if searchResults or table appeared
                results_table = page.locator("table, .table, #tblResults, #partyResultsTable")
                print("Results elements count:", await results_table.count())
                print("Visible challenge frame count:", await page.locator("iframe[src*='recaptcha/api2/bframe']:visible").count())
                print("Search route reached:", "searchresults" in page.url.lower())
        except Exception as e:
            print("Exception during test:", e)
            raise
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
