import asyncio
import tempfile
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    repo_root = Path(__file__).resolve().parent.parent
    ext_path = str((repo_root / "anticaptcha-plugin_v0.83").resolve())
    temp_profile = tempfile.mkdtemp(prefix="test_cdp_chrome_")

    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=temp_profile,
            headless=False,
            channel="chrome",
            args=["--no-sandbox"]
        )
        page = await ctx.new_page()
        
        # Test CDP session
        try:
            cdp = await ctx.new_cdp_session(page)
            print("CDP session created!")
            res = await cdp.send("Extensions.loadUnpacked", {"path": ext_path})
            print("Extensions.loadUnpacked result:", res)
            
            await asyncio.sleep(2)
            print("Service workers count after CDP load:", len(ctx.service_workers))
            for sw in ctx.service_workers:
                print("  SW URL:", sw.url)
        except Exception as e:
            print("CDP Error:", e)

        await ctx.close()

if __name__ == '__main__':
    asyncio.run(main())
