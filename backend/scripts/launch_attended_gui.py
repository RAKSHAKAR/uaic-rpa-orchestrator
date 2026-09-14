"""Interactive Desktop Launcher for Attended Browser Verification.
Run directly in an interactive PowerShell or CMD console to see the visible Chromium browser window.
"""

import asyncio
import os
import sys

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright
from app.services.settings_service import get_system_settings_sync

async def main():
    print("=" * 70)
    print("  UAIC Orchestrator - Interactive Attended GUI Browser Launcher")
    print("=" * 70)
    
    settings = get_system_settings_sync()
    auto_cfg = settings.automation
    print(f"[*] Active Mode: {'Headless (Background)' if auto_cfg.headless_mode else 'Attended (Visible GUI)'}")
    print(f"[*] AntiCaptcha Key: {auto_cfg.anticaptcha_api_key[:8]}... configured")
    print(f"[*] Launching visible Chromium browser window onto your desktop...")
    
    p = await async_playwright().start()
    # Force visible GUI (headless=False)
    browser = await p.chromium.launch(
        headless=False,
        args=["--start-maximized", "--window-position=80,80"]
    )
    context = await browser.new_context(no_viewport=True)
    page = await context.new_page()
    
    print("[+] Navigating to UAIC Orchestrator Dashboard: http://localhost:3000")
    await page.goto("http://localhost:3000")
    await page.bring_to_front()
    
    # Inject banner
    await page.evaluate("""() => {
        const div = document.createElement('div');
        div.style.cssText = 'position:fixed;top:20px;left:50%;transform:translateX(-50%);background:#10b981;color:#ffffff;padding:14px 32px;border-radius:12px;font-family:system-ui,sans-serif;font-weight:700;font-size:16px;box-shadow:0 12px 30px rgba(0,0,0,0.4);z-index:9999999;border:2px solid #34d399;';
        div.innerText = 'UAIC Attended GUI Mode: Live Desktop Browser Verified';
        document.body.appendChild(div);
    }""")
    
    print("[+] Browser window is now open on your desktop!")
    print("[*] Keeping window open for 15 seconds so you can see it...")
    for remaining in range(15, 0, -1):
        print(f"    Closing in {remaining}s...", end="\r", flush=True)
        await asyncio.sleep(1)
    
    print("\n[*] Closing test browser session.")
    await browser.close()
    await p.stop()
    print("[+] Attended verification complete.")

if __name__ == "__main__":
    asyncio.run(main())
