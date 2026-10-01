import asyncio
import tempfile
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    repo_root = Path(__file__).resolve().parent.parent
    ext_path = str((repo_root / "anticaptcha-plugin_v0.83").resolve())
    temp_dir = tempfile.mkdtemp(prefix="test_pw_ext_")
    print("Extension path:", ext_path)
    print("Exists:", Path(ext_path).is_dir())

    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=temp_dir,
            headless=False,
            channel="chrome",
            ignore_default_args=["--disable-extensions"],
            args=[
                f"--disable-extensions-except={ext_path}",
                f"--load-extension={ext_path}",
                "--no-sandbox"
            ]
        )
        print("Service workers count:", len(ctx.service_workers))
        for sw in ctx.service_workers:
            print("SW:", sw.url)
        print("Background pages count:", len(ctx.background_pages))
        for bg in ctx.background_pages:
            print("BG:", bg.url)

        page = await ctx.new_page()
        await page.goto("https://antcpt.com/blank.html")
        await asyncio.sleep(4)
        print("Service workers count after wait:", len(ctx.service_workers))
        for sw in ctx.service_workers:
            print("SW after wait:", sw.url)

        # Check if content script injected anything into the page
        injected = await page.evaluate("() => typeof window.antiCapApiKey !== 'undefined' || typeof window.AC_KEY !== 'undefined'")
        print("Injected into page:", injected)

        await page.screenshot(path="implementation_plan/Images/test_pw_ext_screen.png")
        await ctx.close()

if __name__ == '__main__':
    asyncio.run(main())
