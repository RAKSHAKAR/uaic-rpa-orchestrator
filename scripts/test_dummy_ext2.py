import asyncio
import tempfile
import json
from pathlib import Path
from playwright.async_api import async_playwright

async def run_for(channel_name):
    test_ext_dir = Path("backend/data/test_dummy_ext").resolve()
    temp_profile = tempfile.mkdtemp(prefix=f"test_dummy_{channel_name or 'chromium'}_")

    async with async_playwright() as p:
        kwargs = {
            "user_data_dir": temp_profile,
            "headless": False,
            "ignore_default_args": ["--disable-extensions"],
            "args": [
                f"--disable-extensions-except={test_ext_dir}",
                f"--load-extension={test_ext_dir}",
                "--no-sandbox"
            ]
        }
        if channel_name:
            kwargs["channel"] = channel_name

        ctx = await p.chromium.launch_persistent_context(**kwargs)
        page = await ctx.new_page()
        await page.goto("https://example.com")
        await asyncio.sleep(2)
        print(f"[{channel_name or 'Chromium'}] SW count:", len(ctx.service_workers))
        for sw in ctx.service_workers:
            print(f"  [{channel_name or 'Chromium'}] SW URL:", sw.url)
        await ctx.close()

async def main():
    await run_for(None)
    await run_for("msedge")

if __name__ == '__main__':
    asyncio.run(main())
