import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Launch headed or headless with network logging
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            page.on("request", lambda r: print(f"[REQ] {r.method} {r.url}") if "miami" in r.url or "api" in r.url else None)
            page.on("response", lambda r: print(f"[RES] {r.status} {r.url}") if "miami" in r.url or "api" in r.url else None)
            page.on("dialog", lambda d: print(f"[DIALOG] {d.type}: {d.message}"))
            
            print("1. Go to OCS...")
            await page.goto("https://www2.miamidadeclerk.gov/ocs", wait_until="domcontentloaded", timeout=25000)
            await asyncio.sleep(2)
            
            # Click Party Name tab
            party_link = page.locator("span.subitem-color[role='button']:has-text('Party Name'), span:has-text('Party Name')")
            if await party_link.count() > 0:
                await party_link.first.click()
                await asyncio.sleep(1)
                
            # Fill inputs
            print("2. Filling inputs...")
            await page.locator("input#partyLastName").fill("SMITH")
            await page.locator("input#partyFirstName").fill("JOHN")
            await page.locator("input#filingDateFrom").fill("2020-01-01")
            await page.locator("input#filingDateTo").fill("2026-10-01")
            await asyncio.sleep(1)
            
            # Click search button
            btn = page.locator("button.btn.button-green[type='submit']")
            print("3. Clicking search button...")
            await btn.click()
            
            # Wait up to 10 seconds and check DOM
            for sec in range(10):
                await asyncio.sleep(1)
                curr_url = page.url
                has_results = await page.evaluate('''() => {
                    const text = document.body.innerText;
                    return {
                        url: window.location.href,
                        has_results_text: text.includes('Search Results') || text.includes('Party Name:'),
                        has_table: !!document.querySelector('table'),
                        has_spinner: !!document.querySelector('.spinner, .loading, .loader'),
                        modal: !!document.querySelector('.modal.show'),
                        modal_text: document.querySelector('.modal.show')?.innerText
                    };
                }''')
                print(f"Sec {sec+1}: {has_results}")
                if has_results['has_results_text'] or has_results['has_table'] or "searchresults" in curr_url.lower():
                    print("SUCCESS! Results appeared or navigated!")
                    break
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
