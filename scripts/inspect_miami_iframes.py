import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto("https://www2.miamidadeclerk.gov/ocs", wait_until="domcontentloaded", timeout=25000)
            await asyncio.sleep(2)
            
            frames = page.frames
            print("Total frames:", len(frames))
            for idx, f in enumerate(frames):
                print(f"Frame {idx}: url={f.url}")
                
            res_vis = await page.evaluate('''() => {
                const f = document.querySelector('iframe[src*="recaptcha/api2/anchor" i], iframe[src*="turnstile" i], iframe[src*="hcaptcha" i]');
                if (f && f.offsetParent !== null) return { found: true, src: f.src };
                const any_f = Array.from(document.querySelectorAll('iframe')).map(fr => fr.src);
                return { found: false, all_iframes: any_f };
            }''')
            print("res_vis result:", res_vis)
            
            # Check reCAPTCHA / CAPTCHA on the page
            captcha_check = await page.evaluate('''() => {
                return {
                    has_grecaptcha: typeof window.grecaptcha !== 'undefined',
                    has_recaptcha_el: !!document.querySelector('.g-recaptcha, #RecaptchaField1, [data-sitekey]'),
                    has_turnstile: typeof window.turnstile !== 'undefined',
                    has_hcaptcha: typeof window.hcaptcha !== 'undefined'
                };
            }''')
            print("captcha_check:", captcha_check)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
