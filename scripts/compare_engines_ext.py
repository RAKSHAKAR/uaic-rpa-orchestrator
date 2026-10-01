import asyncio
import tempfile
from pathlib import Path
from playwright.async_api import async_playwright

async def test_engine(name, channel=None, exe=None):
    repo_root = Path(__file__).resolve().parent.parent
    ext_path = str((repo_root / "anticaptcha-plugin_v0.83").resolve())
    temp_dir = tempfile.mkdtemp(prefix=f"test_pw_ext_{name}_")

    print(f"\n--- Testing {name} ---")
    async with async_playwright() as p:
        kwargs = {
            "user_data_dir": temp_dir,
            "headless": False,
            "ignore_default_args": ["--disable-extensions"],
            "args": [
                f"--disable-extensions-except={ext_path}",
                f"--load-extension={ext_path}",
                "--no-sandbox"
            ]
        }
        if channel:
            kwargs["channel"] = channel
        if exe:
            kwargs["executable_path"] = exe

        try:
            ctx = await p.chromium.launch_persistent_context(**kwargs)
            print(f"[{name}] Service workers: {len(ctx.service_workers)}")
            for sw in ctx.service_workers:
                print(f"[{name}] SW: {sw.url}")
            page = await ctx.new_page()
            await page.goto("https://antcpt.com/blank.html")
            await asyncio.sleep(2)
            print(f"[{name}] Service workers after page load: {len(ctx.service_workers)}")
            for sw in ctx.service_workers:
                print(f"[{name}] SW: {sw.url}")
            await ctx.close()
        except Exception as e:
            print(f"[{name}] Error: {e}")

async def main():
    await test_engine("Bundled Chromium", channel=None)
    await test_engine("Microsoft Edge", channel="msedge")
    await test_engine("Google Chrome", channel="chrome")

if __name__ == '__main__':
    asyncio.run(main())
