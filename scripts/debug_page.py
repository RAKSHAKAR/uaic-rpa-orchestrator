import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    output_dir = Path(__file__).resolve().parent.parent / "implementation_plan" / "Images"
    output_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 960})

        print("Navigating to settings...")
        await page.goto("http://localhost:3000/settings", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # Click Browser Automation & Fleet tab
        elem = page.locator("button:has-text('Browser Automation & Fleet')").first
        await elem.click()
        await page.wait_for_timeout(1000)

        main_el = page.locator("main")

        # 1. Top Section: Browser Engine
        await main_el.evaluate("el => el.scrollTop = 0")
        await page.wait_for_timeout(500)
        await page.screenshot(path=str(output_dir / "01_browser_engine_step1.png"))
        print("Captured 01_browser_engine_step1.png")

        # 2. Step 2 & Step 3: Speed & CAPTCHA Setup
        await main_el.evaluate("el => el.scrollTop = 800")
        await page.wait_for_timeout(500)
        await page.screenshot(path=str(output_dir / "02_step2_speed_step3_captcha.png"))
        print("Captured 02_step2_speed_step3_captcha.png")

        # 3. Step 3 details: Pinning card & diagnostics
        await main_el.evaluate("el => el.scrollTop = 1600")
        await page.wait_for_timeout(500)
        await page.screenshot(path=str(output_dir / "03_step3_pinning_and_diagnostics.png"))
        print("Captured 03_step3_pinning_and_diagnostics.png")

        # 4. Step 4: Live Launch Verification Test
        await main_el.evaluate("el => el.scrollTop = 2400")
        await page.wait_for_timeout(500)
        await page.screenshot(path=str(output_dir / "04_step4_live_launch_verification.png"))
        print("Captured 04_step4_live_launch_verification.png")

        # 5. Step 5 & 6: Concurrency Fleet & Proxy
        await main_el.evaluate("el => el.scrollTop = 3200")
        await page.wait_for_timeout(500)
        await page.screenshot(path=str(output_dir / "05_step5_fleet_concurrency_parity.png"))
        print("Captured 05_step5_fleet_concurrency_parity.png")

        await browser.close()
        print("All visual screenshots successfully captured!")

if __name__ == "__main__":
    asyncio.run(main())
