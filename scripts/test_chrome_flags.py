import asyncio
import tempfile
from pathlib import Path
from playwright.async_api import async_playwright

async def test_chrome_flags(flag_name, extra_args=[], ignore_args=["--disable-extensions"]):
    repo_root = Path(__file__).resolve().parent.parent
    ext_path = str((repo_root / "anticaptcha-plugin_v0.83").resolve())
    temp_dir = tempfile.mkdtemp(prefix="test_chrome_flag_")

    args = [
        f"--disable-extensions-except={ext_path}",
        f"--load-extension={ext_path}",
        "--no-sandbox"
    ] + extra_args

    async with async_playwright() as p:
        try:
            ctx = await p.chromium.launch_persistent_context(
                user_data_dir=temp_dir,
                headless=False,
                channel="chrome",
                ignore_default_args=ignore_args,
                args=args,
            )
            sw_count = len(ctx.service_workers)
            for sw in ctx.service_workers:
                sw_count += 1
            page = await ctx.new_page()
            await page.goto("https://antcpt.com/blank.html")
            await asyncio.sleep(2)
            sw_count_after = len(ctx.service_workers)
            sw_urls = [sw.url for sw in ctx.service_workers]
            print(f"[{flag_name}] SW count: {sw_count_after}, URLs: {sw_urls}")
            await ctx.close()
            return sw_count_after > 0
        except Exception as e:
            print(f"[{flag_name}] Error: {e}")
            return False

async def main():
    # Test 1: Just --load-extension without --disable-extensions-except
    repo_root = Path(__file__).resolve().parent.parent
    ext_path = str((repo_root / "anticaptcha-plugin_v0.83").resolve())
    temp_dir = tempfile.mkdtemp(prefix="test_cf1_")
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=temp_dir,
            headless=False,
            channel="chrome",
            ignore_default_args=["--disable-extensions"],
            args=[f"--load-extension={ext_path}"]
        )
        print("Test 1 (only load-extension): SW count =", len(ctx.service_workers))
        await ctx.close()

    # Test 2: ignore ALL default args
    temp_dir = tempfile.mkdtemp(prefix="test_cf2_")
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=temp_dir,
            headless=False,
            channel="chrome",
            ignore_default_args=True,
            args=[
                f"--load-extension={ext_path}",
                "--no-sandbox",
            ]
        )
        print("Test 2 (ignore_default_args=True): SW count =", len(ctx.service_workers))
        for sw in ctx.service_workers:
            print("  SW URL:", sw.url)
        await ctx.close()

if __name__ == '__main__':
    asyncio.run(main())
