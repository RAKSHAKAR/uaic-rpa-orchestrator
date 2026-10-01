import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto("https://www2.miamidadeclerk.gov/ocs", wait_until="domcontentloaded", timeout=25000)
            await asyncio.sleep(2)
            
            # Click Party Name tab
            party_link = page.locator("span.subitem-color[role='button']:has-text('Party Name'), span:has-text('Party Name')")
            if await party_link.count() > 0:
                await party_link.first.click()
                await asyncio.sleep(1)
                
            # Inspect all elements before filling
            before_spans = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('.errorText, span[class*=\"error\"]')).map(s => ({
                    html: s.outerHTML,
                    parent: s.parentElement ? s.parentElement.outerHTML.substring(0, 150) : null,
                    visible: s.offsetParent !== null
                }));
            }''')
            print("Spans before filling:", before_spans)
            
            # What is .errorText? In Bootstrap/React, is '*' just the required field indicator?
            # E.g. <span class="errorText ps-1 fw-bold">*</span> on "Last Name *" !
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
