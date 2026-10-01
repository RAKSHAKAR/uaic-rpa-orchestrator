import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def capture():
    output_dir = Path(__file__).resolve().parent.parent / "implementation_plan" / "Images"
    output_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 1080})
        page = await context.new_page()

        page.on("console", lambda msg: print(f"[CONSOLE {msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: print(f"[PAGE ERROR] {err}"))

        print("Navigating to http://localhost:3000/settings...")
        await page.goto("http://localhost:3000/settings", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        # Click the "Browser Automation & Fleet" tab
        print("Clicking 'Browser Automation & Fleet' tab...")
        automation_btn = page.locator("button:has-text('Browser Automation'), button:has-text('Automation')").first
        await automation_btn.wait_for(state="visible", timeout=25000)
        await automation_btn.click()
        await page.wait_for_timeout(1000)

        # Wait for Browser Engine card
        print("Waiting for Browser Engine & Runtime Environment...")
        engine_elem = page.locator("text=Browser Engine & Runtime Environment").first
        await engine_elem.wait_for(state="visible", timeout=15000)
        print("Browser Engine located.")

        # 1. Top Section (Engine, Execution Timing & Biometric Stealth Clicks)
        top_path = output_dir / "01_browser_engine_and_timing_dynamics.png"
        await page.screenshot(path=str(top_path))
        print(f"Captured top section: {top_path}")

        # 2. CAPTCHA Solver & Extension Setup (including reCAPTCHA v3 slider, auxiliary options, challenge toggles)
        captcha_elem = page.locator("text=CAPTCHA Solver & Extension Setup").first
        if await captcha_elem.count() > 0:
            await captcha_elem.scroll_into_view_if_needed()
            await page.wait_for_timeout(800)
            captcha_path = output_dir / "02_anticaptcha_complete_configuration.png"
            await page.screenshot(path=str(captcha_path))
            print(f"Captured CAPTCHA complete configuration: {captcha_path}")

        # 3. Live Browser Launch Verification Test
        launch_elem = page.locator("text=Live Browser Launch Verification Test").first
        if await launch_elem.count() > 0:
            await launch_elem.scroll_into_view_if_needed()
            await page.wait_for_timeout(800)
            launch_path = output_dir / "03_live_browser_launch_test.png"
            await page.screenshot(path=str(launch_path))
            print(f"Captured Live Launch Test: {launch_path}")

        # 4. RPA Fleet Concurrency, Workflow Parity Guarantee & Proxy Gateway
        proxy_elem = page.locator("text=Proxy Gateway Egress Status").first
        if await proxy_elem.count() > 0:
            await proxy_elem.scroll_into_view_if_needed()
            await page.wait_for_timeout(800)
            fleet_path = output_dir / "04_rpa_fleet_and_proxy_status.png"
            await page.screenshot(path=str(fleet_path))
            print(f"Captured Fleet & Proxy Status: {fleet_path}")

        # 5. Full page screenshot
        full_path = output_dir / "05_browser_automation_full_console.png"
        await page.screenshot(path=str(full_path), full_page=True)
        print(f"Captured full page: {full_path}")

        await browser.close()
        print("Done capturing all screenshots.")

if __name__ == "__main__":
    asyncio.run(capture())
