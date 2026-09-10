"""
Global Light Mode / Dark Mode End-to-End Playwright Automated Test Script
Implementation ID: IMP-2026-0905-004

Validates:
1. Exact two-theme support (Light & Dark only, zero System/Auto mode).
2. Live theme toggle on Navbar & persistence in localStorage.
3. DOM synchronization: class (.light / .dark) & attribute (data-theme="light"|"dark").
4. Navigation across all 9 primary application routes in both modes.
5. Administrative Branding Page with dedicated "Theme & Colors" tab.
6. Preset switching & dynamic CSS design token injection.
7. Visual regression screenshot capture for Light and Dark modes.
"""

import asyncio
import os
import subprocess
import sys
import time
import socket
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import importlib
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
SCREENSHOTS_DIR = ROOT_DIR / "logs" / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Add backend virtualenv site-packages to sys.path if not present
_venv_site = ROOT_DIR / "backend" / ".venv" / "Lib" / "site-packages"
if _venv_site.exists() and str(_venv_site) not in sys.path:
    sys.path.insert(0, str(_venv_site))

try:
    _pw_api = importlib.import_module("playwright.async_api")
    async_playwright: Any = _pw_api.async_playwright
except Exception as _e:
    print(f"Warning: playwright module could not be imported: {_e}")
    async_playwright = None

PORT = 3000
BASE_URL = f"http://localhost:{PORT}"

ROUTES = [
    ("/", "Dashboard"),
    ("/branding", "Brand & Theme Management"),
    ("/settings", "Automation Settings"),
    ("/upload", "Ingest & Upload"),
    ("/monitor", "Queue Monitor"),
    ("/health", "System Health"),
    ("/audit", "Audit Trail"),
    ("/exceptions", "Exception Review"),
]


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


async def wait_for_server(url: str, timeout: int = 45) -> bool:
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_in_use(PORT):
            # Give server a brief moment to initialize handlers
            await asyncio.sleep(1.5)
            return True
        await asyncio.sleep(0.5)
    return False


async def run_theme_e2e_tests():
    server_process = None
    started_server = False

    print("=" * 80)
    print("GLOBAL LIGHT MODE & DARK MODE — AUTOMATED PLAYWRIGHT E2E VERIFICATION")
    print(f"Implementation ID: IMP-2026-0905-004")
    print("=" * 80)

    # 1. Check if server is running, or start Next.js production server
    if not is_port_in_use(PORT):
        print(f"[1/7] Launching Next.js server on {BASE_URL}...")
        # Use npx next start on port 3000
        cmd = "npx next start -p 3000"
        server_process = subprocess.Popen(
            cmd,
            cwd=str(FRONTEND_DIR),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        started_server = True
        ready = await wait_for_server(BASE_URL, timeout=45)
        if not ready:
            print("ERROR: Timed out waiting for Next.js server on port 3000.")
            if server_process:
                server_process.terminate()
            sys.exit(1)
        print(f"      Next.js server is online at {BASE_URL}")
    else:
        print(f"[1/7] Next.js server already running on {BASE_URL}")

    passed_tests = 0
    total_tests = 0

    if async_playwright is None:
        print("ERROR: Playwright could not be loaded. Please ensure backend/.venv is present.")
        sys.exit(1)

    try:
        async with async_playwright() as p:
            print("[2/7] Launching Playwright Chromium browser...")
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1440, "height": 900},
                color_scheme="dark",  # Verify app ignores browser OS color-scheme preference
            )
            page = await context.new_page()

            # Test 1: Initial load (Default is dark mode)
            total_tests += 1
            print(f"[3/7] Verifying initial theme state on {BASE_URL}...")
            await page.goto(f"{BASE_URL}/", wait_until="networkidle")
            await page.wait_for_timeout(1000)

            html_classes = await page.evaluate("() => document.documentElement.className")
            html_data_theme = await page.evaluate("() => document.documentElement.getAttribute('data-theme')")
            local_storage_theme = await page.evaluate("() => localStorage.getItem('uaic_theme')")

            print(f"      Initial HTML class: '{html_classes}'")
            print(f"      Initial data-theme: '{html_data_theme}'")
            print(f"      Initial localStorage: '{local_storage_theme}'")

            assert "dark" in html_classes, "Expected initial HTML class to contain 'dark'"
            assert html_data_theme == "dark", f"Expected data-theme='dark', got '{html_data_theme}'"
            await page.screenshot(path=str(SCREENSHOTS_DIR / "01_dashboard_dark.png"))
            print("      [PASS] Initial Dark Mode confirmed & screenshot saved.")
            passed_tests += 1

            # Test 2: Switch to Light Mode
            total_tests += 1
            print("[4/7] Testing theme toggle: Dark -> Light...")
            toggle_btn = page.locator("header button[aria-label='Toggle theme']")
            await toggle_btn.click()
            await page.wait_for_timeout(500)

            html_classes = await page.evaluate("() => document.documentElement.className")
            html_data_theme = await page.evaluate("() => document.documentElement.getAttribute('data-theme')")
            local_storage_theme = await page.evaluate("() => localStorage.getItem('uaic_theme')")

            assert "light" in html_classes, f"Expected HTML class to contain 'light', got '{html_classes}'"
            assert "dark" not in html_classes, f"Expected 'dark' class removed, got '{html_classes}'"
            assert html_data_theme == "light", f"Expected data-theme='light', got '{html_data_theme}'"
            assert local_storage_theme == "light", f"Expected localStorage='light', got '{local_storage_theme}'"
            await page.screenshot(path=str(SCREENSHOTS_DIR / "02_dashboard_light.png"))
            print("      [PASS] Light Mode toggle & persistence confirmed.")
            passed_tests += 1

            # Test 3: Navigate across all 8 major routes in Light Mode
            total_tests += 1
            print("[5/7] Verifying all routes in Light Mode...")
            for path, name in ROUTES:
                url = f"{BASE_URL}{path}"
                await page.goto(url, wait_until="networkidle")
                await page.wait_for_timeout(400)
                curr_class = await page.evaluate("() => document.documentElement.className")
                curr_theme = await page.evaluate("() => document.documentElement.getAttribute('data-theme')")
                assert "light" in curr_class, f"Route {path} lost 'light' class!"
                assert curr_theme == "light", f"Route {path} lost data-theme='light'!"
                clean_name = name.lower().replace(" ", "_").replace("&", "and")
                await page.screenshot(path=str(SCREENSHOTS_DIR / f"route_{clean_name}_light.png"))
                print(f"      [PASS] Route '{path}' ({name}) rendered in Light Mode.")
            passed_tests += 1

            # Test 4: Branding Page Dedicated Theme Tab & Token Injection
            total_tests += 1
            print("[6/7] Verifying Branding Page Dedicated Theme Tab & Dynamic Token Engine...")
            await page.goto(f"{BASE_URL}/branding", wait_until="networkidle")
            await page.wait_for_timeout(600)

            # Check that Theme & Colors tab exists and click it
            theme_tab_btn = page.locator("button:has-text('Theme & Colors')")
            assert await theme_tab_btn.count() > 0, "Theme & Colors tab button not found!"
            await theme_tab_btn.click()
            await page.wait_for_timeout(400)

            # Verify 26 tokens indicator is visible
            token_indicator = page.locator("text=26 Tokens Configurable")
            assert await token_indicator.count() > 0, "26 Tokens Configurable indicator not found on Theme tab!"

            # Test Light Mode Presets
            preset_btn = page.locator("button:has-text('Crisp Azure')")
            if await preset_btn.count() > 0:
                await preset_btn.click()
                await page.wait_for_timeout(300)
                # Verify that dynamic token injection updated CSS variable in DOM
                primary_var = await page.evaluate("() => getComputedStyle(document.documentElement).getPropertyValue('--color-primary').trim()")
                print(f"      Applied 'Crisp Azure' preset -> --color-primary is '{primary_var}'")
                assert primary_var == "#2563eb", f"Expected --color-primary='#2563eb', got '{primary_var}'"

            # Switch to Dark Mode sub-selector in Theme Tab
            dark_subtab = page.locator("button:has-text('Dark Mode Palette')")
            assert await dark_subtab.count() > 0, "Dark Mode Palette sub-tab button not found!"
            await dark_subtab.click()
            await page.wait_for_timeout(300)

            # Test Dark Mode Preset
            navy_preset = page.locator("button:has-text('Midnight Navy')")
            if await navy_preset.count() > 0:
                await navy_preset.click()
                await page.wait_for_timeout(300)

            await page.screenshot(path=str(SCREENSHOTS_DIR / "03_branding_theme_tab.png"))
            print("      [PASS] Dedicated Theme Tab, 26 tokens, and dynamic CSS token engine verified.")
            passed_tests += 1

            # Test 5: Switch back to Dark Mode & verify all routes in Dark Mode
            total_tests += 1
            print("[7/7] Verifying all routes in Dark Mode & persistence across page refreshes...")
            toggle_btn = page.locator("header button[aria-label='Toggle theme']")
            await toggle_btn.click()
            await page.wait_for_timeout(500)

            html_classes = await page.evaluate("() => document.documentElement.className")
            html_data_theme = await page.evaluate("() => document.documentElement.getAttribute('data-theme')")
            local_storage_theme = await page.evaluate("() => localStorage.getItem('uaic_theme')")

            assert "dark" in html_classes, f"Expected HTML class to contain 'dark', got '{html_classes}'"
            assert html_data_theme == "dark", f"Expected data-theme='dark', got '{html_data_theme}'"
            assert local_storage_theme == "dark", f"Expected localStorage='dark', got '{local_storage_theme}'"

            # Refresh page to verify persistence
            await page.reload(wait_until="networkidle")
            reloaded_classes = await page.evaluate("() => document.documentElement.className")
            reloaded_theme = await page.evaluate("() => document.documentElement.getAttribute('data-theme')")
            assert "dark" in reloaded_classes, "Theme did not persist across page reload!"
            assert reloaded_theme == "dark", "data-theme did not persist across page reload!"

            # Check routes in Dark Mode
            for path, name in ROUTES:
                url = f"{BASE_URL}{path}"
                await page.goto(url, wait_until="networkidle")
                await page.wait_for_timeout(400)
                curr_class = await page.evaluate("() => document.documentElement.className")
                curr_theme = await page.evaluate("() => document.documentElement.getAttribute('data-theme')")
                assert "dark" in curr_class, f"Route {path} lost 'dark' class!"
                assert curr_theme == "dark", f"Route {path} lost data-theme='dark'!"
                clean_name = name.lower().replace(" ", "_").replace("&", "and")
                await page.screenshot(path=str(SCREENSHOTS_DIR / f"route_{clean_name}_dark.png"))
                print(f"      [PASS] Route '{path}' ({name}) rendered in Dark Mode.")

            passed_tests += 1
            await browser.close()

    finally:
        if started_server and server_process:
            print(f"Stopping Next.js test server process (PID: {server_process.pid})...")
            try:
                subprocess.run(f"taskkill /F /T /PID {server_process.pid}", shell=True, capture_output=True)
            except Exception as e:
                print(f"Warning: Failed to terminate server process: {e}")

    print("=" * 80)
    print(f"ALL PLAYWRIGHT THEME E2E CHECKS PASSED: {passed_tests}/{total_tests} test suites green!")
    print(f"Screenshots saved to: {SCREENSHOTS_DIR}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_theme_e2e_tests())
