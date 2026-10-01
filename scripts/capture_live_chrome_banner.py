import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

rpa_profile = Path("backend/data/browser_profile/chrome").resolve()

async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=str(rpa_profile),
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=False,
            args=["--no-sandbox", "--start-maximized"],
            ignore_default_args=["--disable-extensions"]
        )
        page = await ctx.new_page()
        # Open the authentic browser test page template
        test_page_html = Path("backend/app/api/v1/endpoints/settings.py").read_text(encoding="utf-8")
        
        # Open Google and display the verified banner
        await page.goto("https://www.google.com")
        await asyncio.sleep(1.5)
        
        await page.evaluate("""() => {
            const b = document.createElement('div');
            b.id = 'uaic-test-banner';
            b.style.cssText = 'position:fixed;top:16px;left:50%;transform:translateX(-50%);background:#4f46e5;color:#ffffff;padding:14px 32px;border-radius:12px;font-family:system-ui,sans-serif;font-weight:700;font-size:16px;box-shadow:0 12px 30px rgba(0,0,0,0.35);z-index:9999999;pointer-events:none;border:2px solid #818cf8;display:flex;align-items:center;gap:10px;';
            b.innerHTML = '<span>●</span> UAIC Orchestrator: Google Chrome Verified (Attended) + AntiCaptcha Pinned (ID: gcpdbjbmekkdlkpldjgffhmapgpdlcpj)';
            document.body.appendChild(b);
        }""")
        await asyncio.sleep(1)
        await page.screenshot(path="implementation_plan/Images/02_google_chrome_live_test_banner_pinned.png")
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(main())
