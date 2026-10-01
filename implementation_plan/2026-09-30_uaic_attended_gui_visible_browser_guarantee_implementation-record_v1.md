# UAIC Orchestrator — Implementation Record: Attended Visible GUI Browser Guarantee & Diagnostics Fix

**Document ID:** `IMP-2026-0930-007`  
**Reference Plan:** [implementation_plan/2026-09-30_uaic_attended_gui_visible_browser_guarantee_plan_v1.md](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/implementation_plan/2026-09-30_uaic_attended_gui_visible_browser_guarantee_plan_v1.md)  
**Date:** 2026-09-30  
**Status:** Completed  
**AI Verification:** Complete (100% Automated Testing Suite)  
**Human Verification:** Pending  

---

## 1. Executive Summary

The operator reported a recurring usability issue where, despite selecting **Attended Visible GUI Mode**, the desktop browser window did not consistently appear on screen during RPA automation runs (*"also i noticed most of the time even it is attended visible gui mode but i can't see any browser is running, why this issue comming again and again"*).

A comprehensive architectural and environment diagnosis identified four compounding root causes across browser engine routing, Chromium window preferences, background process focus, and Redis settings synchronization. All four issues have been resolved, and real Google Chrome now launches prominently on screen with the AntiCaptcha extension active, maximized, and focused.

---

## 2. Root Cause Analysis & Diagnostic Findings

1. **Artificial Engine Downgrade to Bundled Chromium:**
   - In `backend/app/automation/base.py` and `backend/app/automation/session_runner.py`, an override forced `raw_engine = "chromium"` / `(None, None)` whenever an unpacked extension was detected on Windows.
   - When Playwright launched bundled Chromium (`ms-playwright\chromium-XXXX\chrome-win\chrome.exe`), Windows treated its processes as secondary or grouped them behind existing Chrome instances, preventing a standard Google Chrome window from appearing prominently.
2. **Corrupted Chromium `window_placement` Preferences:**
   - In `backend/app/automation/browser_manager.py` (lines 568–572) and `backend/app/automation/base.py` (lines 1251–1255), code injected a partial JSON dictionary into Chrome's profile `Preferences`:
     ```json
     "browser": {
       "window_placement": {
         "maximized": true,
         "top": 0,
         "left": 0
       }
     }
     ```
   - On Windows, Chromium expects complete placement metrics (`bottom`, `right`, `work_area_bottom`, etc.). Injecting this incomplete structure caused Chromium's window manager to occasionally render off-screen or in a hidden/zero-size virtual buffer.
3. **Unconditional `--disable-gpu` Flag:**
   - `SingleSessionBrowserRunner` passed `--disable-gpu` unconditionally. In visible desktop GUI mode on Windows, disabling hardware acceleration forces software rasterization, causing rendering latency and occasional invisible or occluded windows on multi-monitor / high-DPI displays.
4. **Celery Worker Desktop Focus & Settings Desynchronization:**
   - Celery workers spawned from background terminal sessions open child browser processes without foreground window activation.
   - In `setup_local.ps1`, selecting `[A] Attended Mode` updated `.env` (`PLAYWRIGHT_HEADLESS=false`), but did not synchronize the Redis key `uaic:system_settings`. Consequently, workers reading from Redis would retain whatever previous headless state was cached in Redis.

---

## 3. Code Modifications Applied

### 3.1. Browser Target Resolution (`backend/app/automation/base.py`)
- Removed the automatic redirect from Google Chrome to bundled Chromium.
- Real Google Chrome (`C:\Program Files\Google\Chrome\Application\chrome.exe`) or channel `"chrome"` is now used directly with unpacked extensions:
  ```python
  if raw_engine in ("chrome", "google-chrome"):
      if chrome_binary_path and os.path.isfile(chrome_binary_path) and ("chrome" in chrome_binary_path.lower() or "google" in chrome_binary_path.lower()):
          return (chrome_binary_path, None)
      chrome_exe = find_chrome_executable()
      if chrome_exe and os.path.isfile(chrome_exe):
          return (chrome_exe, None)
      return (None, "chrome")
  ```

### 3.2. Elimination of Corrupted `window_placement` (`browser_manager.py` & `base.py`)
- Removed `browser_prefs["window_placement"]` from both `ChromeSession.pin_extension_in_preferences()` and `BaseCourtScraper._launch_persistent_browser()`.
- Chrome now computes native window placement cleanly based on active display geometry.

### 3.3. Attended Launch Arguments & Window Focus (`backend/app/automation/session_runner.py`)
- Differentiated launch flags between headless and visible attended execution:
  ```python
  is_headless = self.headless
  launch_args = [
      "--disable-blink-features=AutomationControlled",
      "--disable-background-timer-throttling",
      "--disable-backgrounding-occluded-windows",
      "--disable-renderer-backgrounding",
      "--disable-dev-shm-usage",
  ]
  if is_headless:
      launch_args.append("--disable-gpu")
      launch_args.append("--window-size=1920,1080")
  else:
      launch_args.extend([
          "--start-maximized",
          "--window-position=50,50" if self.worker_id is None else f"--window-position={50 + (35 * (self.worker_id or 0)) % 400},{50 + (30 * (self.worker_id or 0)) % 300}",
          "--window-size=1280,900",
      ])
  ```
- Preserved `engine_key = "chrome"` without Windows-specific Chromium overrides.
- In `__aenter__` and `get_or_create_tab`, added `await page.bring_to_front()` and `await page.evaluate("window.focus()")` to guarantee the browser window surfaces to the foreground.

### 3.4. Operational Banner Logging (`backend/app/tasks/scraper_tasks.py`)
- Added clear visual banner logging before browser session launch:
  ```
  =======================================================
   CLAIM 0123456789 - RPA AUTOMATION LAUNCHING
   MODE:    ATTENDED (VISIBLE GUI)
   ENGINE:  CHROME
   PORTALS (3): broward, hillsborough, miami
  =======================================================
  ```

### 3.5. Launcher Settings Synchronization (`setup_local.ps1`)
- Updated `Invoke-StartAllServices` to synchronize the chosen RPA mode directly into Redis `uaic:system_settings` before launching Celery workers, ensuring zero discrepancy between `.env` and Redis cache.

---

## 4. Automated Verification Results

| Verification Test Suite | Command | Result | Details |
|---|---|---|---|
| **PowerShell Syntax** | `powershell -File scripts\check_ps1_syntax.ps1` | **PASS (0 errors)** | All 12 PowerShell scripts verified clean |
| **Python Linter** | `.venv\Scripts\ruff check app tests` | **PASS (0 errors)** | Zero lint or formatting warnings |
| **TypeScript Compiler** | `npx tsc --noEmit` (frontend) | **PASS (0 errors)** | Strict TypeScript compilation verified |
| **Browser Management Suites** | `pytest tests/test_browser_manager.py ...` | **PASS (32/32)** | 100% pass across browser manager & pinning tests |
| **Full Pytest Suite** | `.venv\Scripts\pytest -q` | **PASS (599/599)** | 100% pass rate across all 67 backend test suites |
| **Live Attended Launch Verification** | `python app\scripts\test_runner_profile.py` | **PASS (Exit 0)** | Google Chrome launched in visible GUI mode with AntiCaptcha verified in 2.5s |

---

## 5. Protected Assets Preservation Checklist

- [x] `implementation_plan/` intact and updated with plan and implementation record
- [x] `PowerAutomateSolutions/` completely untouched (V4 authoritative Robin references preserved)
- [x] `Testing files/` completely untouched
- [x] `anticaptcha-plugin_v0.83/` completely untouched
- [x] `.agents/` completely untouched
- [x] `setup_local.ps1` remains interactive and persistent (never auto-exits)
- [x] `docker-compose.yml` validated and untouched
- [x] State routing logic, DOL date conversion, and 9-digit claim rules 100% preserved
