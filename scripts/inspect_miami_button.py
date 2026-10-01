import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            print("Navigating to Miami OCS...")
            await page.goto("https://www2.miamidadeclerk.gov/ocs", wait_until="domcontentloaded", timeout=25000)
            await asyncio.sleep(2)
            
            # Click Party Name tab if needed
            party_link = page.locator("span.subitem-color[role='button']:has-text('Party Name'), span:has-text('Party Name')")
            if await party_link.count() > 0:
                await party_link.first.click()
                await asyncio.sleep(1)
            
            # Inspect all buttons with Search
            btns = await page.evaluate('''() => {
                const results = [];
                const all = document.querySelectorAll('button, input[type="submit"], input[type="button"], a.btn');
                for (const b of all) {
                    results.push({
                        tag: b.tagName,
                        type: b.getAttribute('type'),
                        id: b.id,
                        className: b.className,
                        innerText: b.innerText,
                        disabled: b.disabled,
                        offsetParent: b.offsetParent !== null,
                        outerHTML: b.outerHTML.substring(0, 250)
                    });
                }
                return results;
            }''')
            print("Found total buttons:", len(btns))
            for b in btns:
                txt = (b.get('innerText') or '').lower()
                id_ = (b.get('id') or '').lower()
                cls = (b.get('className') or '').lower()
                if 'search' in txt or 'search' in id_ or 'search' in cls:
                    print("SEARCH BUTTON MATCH:", b)
                    
            # Also inspect form validation / onsubmit / Formik state
            form_info = await page.evaluate('''() => {
                const form = document.querySelector('form');
                if (!form) return { has_form: false };
                return {
                    has_form: true,
                    action: form.action,
                    method: form.method,
                    id: form.id,
                    className: form.className,
                    num_inputs: form.querySelectorAll('input').length,
                    inputs: Array.from(form.querySelectorAll('input')).map(i => ({
                        id: i.id,
                        name: i.name,
                        type: i.type,
                        value: i.value,
                        required: i.required
                    }))
                };
            }''')
            print("FORM INFO:", form_info)
        except Exception as e:
            print("Error:", e)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
