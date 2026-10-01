import subprocess
import time
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.automation.browser_manager import ChromeSession, ExtensionManager
from app.services.settings_service import get_system_settings_sync
from playwright.sync_api import sync_playwright

def main():
    settings = get_system_settings_sync()
    broward_url = settings.portals.broward_url or "https://www.browardclerk.org/"
    hillsborough_url = settings.portals.hillsborough_url or "https://hover.hillsclerk.com/"
    miami_url = settings.portals.miami_url or "https://www2.miamidadeclerk.gov/ocs"

    chrome_exe = str(ChromeSession.find_chrome_executable())
    ext_path = ExtensionManager.resolve_extension_path()
    profile_dir = ChromeSession.get_persistent_profile_dir("chrome")

    print("================================================================")
    print("  MANUAL PORTAL WALKTHROUGH — FLORIDA PORTAL INITIALIZER")
    print("================================================================")
    print(f"Browser Engine: Google Chrome ({chrome_exe})")
    print(f"Profile Dir:    {profile_dir}")
    print(f"Extension Path: {ext_path}")
    print("----------------------------------------------------------------")
    print(f"Tab 1 (Broward):      {broward_url}")
    print(f"Tab 2 (Hillsborough): {hillsborough_url}")
    print(f"Tab 3 (Miami-Dade):   {miami_url}")
    print("================================================================")

    print("Syncing AntiCaptcha credentials...")
    if ext_path and settings.automation.anticaptcha_api_key:
        ExtensionManager.sync_api_key(ext_path, settings.automation.anticaptcha_api_key, settings.automation)

    print("Configuring profile & pinning extension...")
    ChromeSession.configure_and_pin_profile(api_key=settings.automation.anticaptcha_api_key, extension_path=ext_path)
    ChromeSession.clean_profile_locks_and_orphans(profile_dir)

    cmd = [
        chrome_exe,
        "--remote-debugging-port=9222",
        f"--user-data-dir={profile_dir}",
        f"--load-extension={ext_path}",
        "--disable-blink-features=AutomationControlled",
        "--no-first-run",
        "--no-default-browser-check",
        "--start-maximized",
        broward_url,
    ]

    flags = 0
    if sys.platform == "win32":
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

    print("Launching persistent Chrome GUI window...")
    proc = subprocess.Popen(cmd, creationflags=flags)
    print(f"Chrome GUI process active with PID {proc.pid}")

    # Wait for CDP endpoint to become ready
    print("Waiting for Chrome to initialize remote debugging port 9222...")
    connected = False
    for attempt in range(15):
        time.sleep(1)
        try:
            with sync_playwright() as p:
                b = p.chromium.connect_over_cdp("http://localhost:9222", timeout=3000)
                b.close()
                connected = True
                break
        except Exception:
            pass

    if not connected:
        print("WARNING: Could not connect over CDP immediately, Chrome might already be open.")

    print("\nConnecting to open the portals one by one in tabs...")
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]

        # Tab 1: Broward
        if len(context.pages) > 0:
            tab1 = context.pages[0]
            if "broward" not in tab1.url.lower():
                print(f"Navigating Tab 1 to Broward: {broward_url}")
                tab1.goto(broward_url, wait_until="domcontentloaded", timeout=45000)
        else:
            tab1 = context.new_page()
            tab1.goto(broward_url, wait_until="domcontentloaded", timeout=45000)
        print(f"[OK] Tab 1: Broward loaded ({tab1.url})")

        # Tab 2: Hillsborough
        print(f"\nOpening Tab 2 (Hillsborough): {hillsborough_url} ...")
        time.sleep(2)
        tab2 = context.new_page()
        try:
            tab2.goto(hillsborough_url, wait_until="domcontentloaded", timeout=45000)
            print(f"[OK] Tab 2: Hillsborough loaded ({tab2.url})")
        except Exception as e:
            print(f"[INFO] Tab 2 navigation: {e}")

        # Tab 3: Miami-Dade
        print(f"\nOpening Tab 3 (Miami-Dade): {miami_url} ...")
        time.sleep(2)
        tab3 = context.new_page()
        try:
            tab3.goto(miami_url, wait_until="domcontentloaded", timeout=45000)
            print(f"[OK] Tab 3: Miami-Dade loaded ({tab3.url})")
        except Exception as e:
            print(f"[INFO] Tab 3 navigation: {e}")

        time.sleep(2)
        print("\nBringing Tab 1 (Broward) to front...")
        try:
            tab1.bring_to_front()
        except Exception:
            pass

        print("\n================================================================")
        print("  ALL 3 FLORIDA TABS ARE OPEN AND READY IN THE BROWSER!")
        print("  - Tab 1: Broward County Court Portal")
        print("  - Tab 2: Hillsborough County Court Portal (HOVER)")
        print("  - Tab 3: Miami-Dade County Court Portal (OCS)")
        print("  Chrome will remain open permanently for manual walkthrough.")
        print("================================================================")

if __name__ == "__main__":
    main()
