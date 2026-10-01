import asyncio
import os
import sys

from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            # Capture console logs and network requests
            page.on("console", lambda msg: print(f"[BROWSER CONSOLE] {msg.type}: {msg.text}"))
            page.on("request", lambda req: print(f"[NET REQ] {req.method} {req.url}") if "miami" in req.url else None)
            page.on("response", lambda res: print(f"[NET RES] {res.status} {res.url}") if "miami" in res.url else None)
            
            print("1. Navigating...")
            await page.goto("https://www2.miamidadeclerk.gov/ocs", wait_until="domcontentloaded", timeout=25000)
            await asyncio.sleep(2)
            
            # Click Party Name tab
            party_link = page.locator("span.subitem-color[role='button']:has-text('Party Name'), span:has-text('Party Name')")
            if await party_link.count() > 0:
                await party_link.first.click()
                await asyncio.sleep(1)
                
            last_inp = page.locator("input#partyLastName")
            first_inp = page.locator("input#partyFirstName")
            date_from = page.locator("input#filingDateFrom")
            date_to = page.locator("input#filingDateTo")
            
            await last_inp.fill("User")
            await first_inp.fill("Test")
            await date_from.fill("2024-10-01")
            await date_to.fill("2026-10-01")
            
            # Check form validity
            is_valid = await page.evaluate('''() => {
                const form = document.querySelector('form');
                if (!form) return 'no form';
                return {
                    checkValidity: form.checkValidity(),
                    last_validity: document.getElementById('partyLastName')?.validity?.valid,
                    last_val: document.getElementById('partyLastName')?.value,
                    btn_type: document.querySelector('button.button-green')?.type
                };
            }''')
            print("Form validity:", is_valid)
            
            # Click Search
            btn = page.locator("button.btn.button-green[type='submit'], button.button-green")
            print("Clicking Search button...")
            await btn.first.click()
            await asyncio.sleep(5)
            
            # Inspect DOM changes
            print("Current URL:", page.url)
            html_snapshot = await page.content()
            print("Has 'Search Results':", "search results" in html_snapshot.lower())
            print("Has 'No records' or similar:", "no records" in html_snapshot.lower() or "no cases" in html_snapshot.lower() or "table" in html_snapshot.lower())
            
            # Look for any alerts, error messages, or validation errors
            errors = await page.evaluate('''() => {
                const errs = [];
                document.querySelectorAll('.invalid-feedback, .error, .alert, .text-danger, span[class*=\"error\"]').forEach(el => {
                    if (el.innerText.trim()) errs.push({ tag: el.tagName, class: el.className, text: el.innerText.trim() });
                });
                return errs;
            }''')
            print("Validation errors on page:", errors)
            
        except Exception as e:
            print("Error:", e)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
