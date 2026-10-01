import asyncio
import tempfile
import json
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    test_ext_dir = Path("backend/data/test_dummy_ext").resolve()
    test_ext_dir.mkdir(parents=True, exist_ok=True)
    
    # Write minimal manifest
    manifest = {
        "manifest_version": 3,
        "name": "Minimal Dummy Extension",
        "version": "1.0",
        "background": {
            "service_worker": "sw.js"
        }
    }
    (test_ext_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (test_ext_dir / "sw.js").write_text('console.log("Dummy SW active!");', encoding="utf-8")

    temp_profile = tempfile.mkdtemp(prefix="test_dummy_")

    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=temp_profile,
            headless=False,
            channel="chrome",
            ignore_default_args=["--disable-extensions"],
            args=[
                f"--disable-extensions-except={test_ext_dir}",
                f"--load-extension={test_ext_dir}",
                "--no-sandbox"
            ]
        )
        print("Service workers count:", len(ctx.service_workers))
        for sw in ctx.service_workers:
            print("  SW URL:", sw.url)
        page = await ctx.new_page()
        await page.goto("https://example.com")
        await asyncio.sleep(2)
        print("Service workers count after wait:", len(ctx.service_workers))
        for sw in ctx.service_workers:
            print("  SW URL after wait:", sw.url)
        await ctx.close()

if __name__ == '__main__':
    asyncio.run(main())
