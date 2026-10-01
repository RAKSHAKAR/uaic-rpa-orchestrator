import asyncio
import tempfile
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    repo_root = Path(__file__).resolve().parent.parent
    ext_path = str((repo_root / "anticaptcha-plugin_v0.83").resolve())
    temp_dir = tempfile.mkdtemp(prefix="test_dallas_anticaptcha_")

    print(f"Launching Bundled Chromium with AntiCaptcha: {ext_path}")
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=temp_dir,
            headless=False,
            ignore_default_args=["--disable-extensions"],
            args=[
                f"--disable-extensions-except={ext_path}",
                f"--load-extension={ext_path}",
                "--no-sandbox"
            ]
        )
        print("Service workers count:", len(ctx.service_workers))
        for sw in ctx.service_workers:
            print("  SW URL:", sw.url)

        page = await ctx.new_page()
        print("Navigating to Dallas Smart Search...")
        await page.goto("https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29", wait_until="domcontentloaded")
        await asyncio.sleep(4)

        # Check for reCAPTCHA and AntiCaptcha badge
        content = await page.content()
        has_recaptcha = "recaptcha" in content.lower()
        has_anticaptcha_injected = "anticaptcha" in content.lower() or "antcpt" in content.lower()
        print(f"Page loaded. Has reCAPTCHA in DOM: {has_recaptcha}")
        print(f"Has AntiCaptcha injected in DOM: {has_anticaptcha_injected}")

        await page.screenshot(path="implementation_plan/Images/dallas_chromium_anticaptcha_test.png")
        print("Saved screenshot to implementation_plan/Images/dallas_chromium_anticaptcha_test.png")
        await ctx.close()

if __name__ == '__main__':
    asyncio.run(main())
