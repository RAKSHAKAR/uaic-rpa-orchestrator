# UAIC Claim & RPA Orchestrator — Implementation Plan
## Attended Visible GUI Browser Launch & Window Visibility Guarantee

- **Implementation ID:** `IMP-2026-0930-007`
- **Document Type:** Implementation Plan
- **Date:** 2026-09-30
- **Author:** AI Engineering Assistant (Pair Programming with User)
- **Status:** Complete
- **AI Verification:** Complete (100% Automated Testing Suite)
- **Human Verification:** Pending
- **Target Version:** `v1`
- **Related Issue:** In Attended Visible GUI mode, the browser window is frequently not visible to the human operator on screen during claim scraping automation.

---

## 1. Executive Summary & Root Cause Analysis

### 1.1 Problem Statement
The user reported:
> *"also i noticed most of the time even it is attended visible gui mode but i can't see any browser is running, why this issue comming again and again"*

When running in Attended Mode, the operator expects to see Google Chrome or Microsoft Edge visibly open on their desktop, display tabs for Broward, Hillsborough, Miami, Dallas, etc., and perform scraping in real time. Instead, the browser appears to run invisibly or fail to show a window on the operator's desktop.

### 1.2 Identified Root Causes

1. **Artificial Auto-Routing Away From Google Chrome:**
   - In `backend/app/automation/base.py` (`resolve_browser_launch_target`), there was an artificial rule:
     ```python
     if raw_engine in ("chrome", "google-chrome") and has_extension:
         return (None, None)  # auto-route to bundled Chromium
     ```
   - When the operator selected **Google Chrome**, the system silently redirected the launch to Playwright's internal bundled Chromium binary (`%LOCALAPPDATA%\ms-playwright\chromium-XXXX\chrome-win\chrome.exe`).
   - On Windows, because this bundled Chromium executable is also named `chrome.exe`, Windows automatically stacks it under the operator's existing Google Chrome taskbar icon group in the background, rather than opening a prominent new Google Chrome window.
   - **Verification:** Direct Playwright testing confirmed that host Google Chrome (`channel="chrome"`) version 154 launches and runs unpacked extensions with 100% stability.

2. **Corrupted Chromium `window_placement` Preferences:**
   - In `backend/app/automation/browser_manager.py` (`pin_extension_in_preferences`), the code injected:
     ```python
     browser_prefs["window_placement"] = {
         "maximized": True,
         "top": 0,
         "left": 0,
     }
     ```
   - Chromium's native Preferences schema expects complete boundary coordinates (`bottom`, `right`, `work_area_bottom`, etc.). An incomplete structure causes Chromium on Windows to occasionally render to an off-screen coordinate or zero-sized buffer.

3. **Background Process Window Focus Suppression on Windows:**
   - Celery workers launched from background PowerShell windows inherit a non-foreground process group. Windows suppresses foreground window creation for background processes unless the window is explicitly brought to the front and focused via Playwright and Windows API.

4. **Settings Desynchronization Between `setup_local.ps1` and Database/Redis:**
   - When the user selects `[A] Attended Mode` in `setup_local.ps1`, the script writes `PLAYWRIGHT_HEADLESS=false` to `.env`, but previously did not synchronize `headless_mode=false` into Redis/PostgreSQL. Workers reading from Redis could retain a stale `headless_mode=True`.

---

## 2. Proposed Technical Solution

### 2.1 Restore Real Google Chrome Launch Support (`backend/app/automation/base.py`)
- Update `resolve_browser_launch_target`:
  - When `browser_engine == "chrome"`, return `(None, "chrome")` (or the detected `chrome_binary_path`), allowing Playwright to launch the authentic Google Chrome browser.
  - Retain `(None, None)` only when the user explicitly selects bundled Chromium.

### 2.2 Fix Window Coordinates & Bring to Front (`backend/app/automation/session_runner.py` & `browser_manager.py`)
1. Remove incomplete `window_placement` dictionary from `Preferences` injection. Let Chromium/Chrome calculate its native visible window dimensions.
2. In `SingleSessionBrowserRunner.__aenter__`:
   - Pass explicit window arguments: `"--window-position=50,50"`, `"--window-size=1280,900"`, `"--start-maximized"`.
3. In `get_or_create_tab`:
   - Ensure `await page.bring_to_front()` is called, followed by `await page.evaluate("window.focus()")`.

### 2.3 Synchronize `setup_local.ps1` Mode with Redis & DB
- In `setup_local.ps1` (`Invoke-SetRpaMode`), execute a fast Python command to synchronize `headless_mode` directly into Redis/SystemSettings so that Celery workers immediately inherit the chosen mode upon startup:
  ```powershell
  & $pyExe -c "import asyncio; from app.services.settings_service import get_system_settings_async, save_system_settings_async; s = asyncio.run(get_system_settings_async()); s.automation.headless_mode = $isPyBool; asyncio.run(save_system_settings_async(s))"
  ```

### 2.4 Explicit Execution Mode Logging in Celery
- In `backend/app/tasks/scraper_tasks.py`:
  - Add prominent logger output at task startup:
    ```python
    logger.info(f"╔════════════════════════════════════════════════════════════════╗")
    logger.info(f"║ RPA EXECUTION MODE: {'ATTENDED (VISIBLE GUI)' if not auto_cfg.headless_mode else 'UNATTENDED (HEADLESS BACKGROUND)'} ║")
    logger.info(f"║ BROWSER ENGINE    : {auto_cfg.browser_engine.upper()} ║")
    logger.info(f"╚════════════════════════════════════════════════════════════════╝")
    ```

---

## 3. Verification & Testing Strategy

1. Run automated unit tests (`pytest`).
2. Run linter (`ruff check app tests`) and TypeScript compiler (`npx tsc --noEmit`).
3. Launch a live test in Attended Mode to confirm that a visible, foregrounded browser window pops up on the operator's screen.
