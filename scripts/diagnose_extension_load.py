import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from playwright.async_api import async_playwright
from app.automation.browser_manager import ChromeSession, ExtensionManager, KNOWN_ANTICAPTCHA_IDS

async def main():
    print("--- Diagnosing Extension Loading in Playwright ---")
    session = ChromeSession(
        headless=False,
        browser_engine="chrome",
        load_extension=True,
    )
    print(f"Extension Path: {session.extension_path}")
    print(f"Manifest exists: {(session.extension_path / 'manifest.json').is_file() if session.extension_path else False}")
    
    ctx = await session.start()
    print(f"Browser launched with profile: {session.profile_to_use}")
    print(f"Service workers count: {len(ctx.service_workers)}")
    for sw in ctx.service_workers:
        print(f" - SW URL: {sw.url}")
    print(f"Background pages count: {len(ctx.background_pages)}")
    for bg in ctx.background_pages:
        print(f" - BG URL: {bg.url}")

    page = await ctx.new_page()
    await page.goto("chrome://extensions")
    await asyncio.sleep(2)
    # Check what extensions are listed in chrome://extensions
    title = await page.title()
    print(f"chrome://extensions title: {title}")
    
    # Check if AntiCaptcha is in DOM of chrome://extensions
    content = await page.content()
    print(f"'AntiCaptcha' in chrome://extensions: {'anticaptcha' in content.lower()}")
    print(f"'fignfifoniblkonapihmkfakmlgkbkcf' in content: {'fignfifoniblkonapihmkfakmlgkbkcf' in content}")
    print(f"'gcpdbjbmekkdlkpldjgffhmapgpdlcpj' in content: {'gcpdbjbmekkdlkpldjgffhmapgpdlcpj' in content}")

    # Inspect preferences file
    pref_file = session.profile_to_use / "Default" / "Preferences"
    print(f"Preferences exists: {pref_file.is_file()}")
    if pref_file.is_file():
        pref_text = pref_file.read_text(encoding="utf-8")
        print(f"Preferences length: {len(pref_text)}")
        import json
        p_json = json.loads(pref_text)
        print("pinned_extensions in prefs:", p_json.get("extensions", {}).get("pinned_extensions"))
        print("pinned_actions in prefs:", p_json.get("toolbar", {}).get("pinned_actions"))

    await page.screenshot(path="implementation_plan/Images/diag_chrome_extensions.png")
    print("Saved screenshot to implementation_plan/Images/diag_chrome_extensions.png")
    
    await asyncio.sleep(5)
    await session.stop()

if __name__ == "__main__":
    asyncio.run(main())
