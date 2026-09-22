import asyncio
import sys
from pathlib import Path

# Add backend to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.automation.browser_manager import ChromeSession, ExtensionManager, run_browser_coroutine

async def test():
    ext_path = ExtensionManager.resolve_extension_path(None)
    print(f"Extension path: {ext_path}")

    # Ensure profile configured and pinned
    ChromeSession.configure_and_pin_profile(
        api_key="b1e626e2ef30b5b29b63486c4786358c",
        extension_path=ext_path,
    )

    session = ChromeSession(
        headless=False,
        extension_path=ext_path,
        anticaptcha_api_key="b1e626e2ef30b5b29b63486c4786358c",
        browser_engine="chrome",
    )

    print("Starting ChromeSession...")
    ctx = await session.start()
    page = await ctx.new_page()
    await page.goto("http://127.0.0.1:8000/api/v1/settings/browser-test-page")
    
    sws = ctx.service_workers
    print(f"Active Service Workers count: {len(sws)}")
    for sw in sws:
        print(f"  SW URL: {sw.url}")
    
    print(f"session.extension_loaded: {session.extension_loaded}")
    print(f"session.extension_id: {session.extension_id}")
    print(f"session.service_worker_active: {session.service_worker_active}")

    # Check Preferences file
    pref_path = Path(session.profile_to_use) / "Default" / "Preferences"
    if pref_path.is_file():
        import json
        with open(pref_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        pinned_exts = data.get("extensions", {}).get("pinned_extensions", [])
        pinned_actions = data.get("toolbar", {}).get("pinned_actions", [])
        print(f"Preferences pinned_extensions: {pinned_exts}")
        print(f"Preferences pinned_actions: {pinned_actions}")

    await page.wait_for_timeout(2000)
    await session.close()
    print("Session closed successfully.")

if __name__ == "__main__":
    asyncio.run(test())
