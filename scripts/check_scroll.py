import asyncio
from playwright.async_api import async_playwright

async def check_scroll():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1600, "height": 1000})
        await page.goto("http://localhost:3000/settings", wait_until="load")
        await page.wait_for_timeout(2000)
        
        btn = page.locator("button:has-text('Email & Notifications')").first
        await btn.click()
        await page.wait_for_timeout(1000)
        
        info = await page.evaluate("""() => {
            const hist = document.getElementById('delivery-history-section');
            const rect = hist ? hist.getBoundingClientRect() : null;
            
            // Find scrollable ancestors
            let el = hist;
            const scrollables = [];
            while (el) {
                const overflowY = window.getComputedStyle(el).overflowY;
                if (overflowY === 'auto' || overflowY === 'scroll' || el === document.body || el === document.documentElement) {
                    scrollables.push({
                        tag: el.tagName,
                        id: el.id,
                        className: el.className,
                        scrollHeight: el.scrollHeight,
                        clientHeight: el.clientHeight,
                        scrollTop: el.scrollTop
                    });
                }
                el = el.parentElement;
            }
            return { rect, scrollables, windowScrollY: window.scrollY, maxScroll: document.documentElement.scrollHeight - window.innerHeight };
        }""")
        print("Info:", info)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(check_scroll())
