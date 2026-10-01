import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            page.on("console", lambda msg: print(f"[CONSOLE {msg.type}] {msg.text}"))
            page.on("pageerror", lambda err: print(f"[PAGEERROR] {err}"))
            
            await page.goto("https://www2.miamidadeclerk.gov/ocs", wait_until="domcontentloaded")
            await asyncio.sleep(2)
            
            party_link = page.locator("span.subitem-color[role='button']:has-text('Party Name'), span:has-text('Party Name')")
            if await party_link.count() > 0:
                await party_link.first.click()
                await asyncio.sleep(1)
            
            # Fill inputs
            await page.locator("input#partyLastName").fill("User")
            await page.locator("input#partyFirstName").fill("Test")
            await page.locator("input#filingDateFrom").fill("2024-10-01")
            await page.locator("input#filingDateTo").fill("2026-10-01")
            await asyncio.sleep(1)
            
            # Check form validity and react state
            diag = await page.evaluate('''() => {
                const form = document.querySelector('form');
                const btn = document.querySelector('button.btn.button-green[type="submit"]');
                return {
                    formCheckValidity: form ? form.checkValidity() : null,
                    formValidationMessage: form ? Array.from(form.elements).filter(e => !e.checkValidity()).map(e => ({ name: e.name, id: e.id, msg: e.validationMessage })) : [],
                    btnDisabled: btn ? btn.disabled : null,
                    grecaptcha: typeof window.grecaptcha,
                    grecaptchaReady: window.grecaptcha && window.grecaptcha.ready ? true : false,
                };
            }''')
            print("Form diagnostic before click:", diag)
            
            # Add submit and click listeners
            await page.evaluate('''() => {
                window.__submitFired = false;
                window.__clickFired = false;
                const form = document.querySelector('form');
                if (form) {
                    form.addEventListener('submit', (e) => {
                        window.__submitFired = true;
                        window.__defaultPrevented = e.defaultPrevented;
                        console.log('FORM SUBMIT EVENT FIRED! defaultPrevented=', e.defaultPrevented);
                    });
                }
                const btn = document.querySelector('button.btn.button-green[type="submit"]');
                if (btn) {
                    btn.addEventListener('click', (e) => {
                        window.__clickFired = true;
                        console.log('BUTTON CLICK EVENT FIRED!');
                    });
                }
            }''')
            
            btn = page.locator("button.btn.button-green[type='submit']")
            print("Clicking button via Playwright...")
            await btn.click()
            await asyncio.sleep(2)
            
            after_click = await page.evaluate('''() => ({
                clickFired: window.__clickFired,
                submitFired: window.__submitFired,
                defaultPrevented: window.__defaultPrevented,
                url: window.location.href,
                formCheckValidity: document.querySelector('form')?.checkValidity(),
                validationErrors: Array.from(document.querySelectorAll('.invalid-feedback, .error, .text-danger')).map(e => e.innerText)
            })''')
            print("After Playwright click:", after_click)
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
