# Implementation Plan: Stale Celery Worker Restart & Scraper Session Hardening

Implementation ID:   IMP-2026-0925-002
Project:             UAIC Claim & RPA Orchestrator
Module:              Celery Worker Fleet, Scraper Session Runner, Claim Telemetry & Dashboard Queue
Feature / Issue:     Stale Celery Worker In-Memory Cache, NameError 'KNOWN_ANTICAPTCHA_IDS', Dynamic Settings Parity & Portal Tab Navigation
Document Type:       Implementation Plan
Version:             v2
Status:              Complete
Created:             2026-09-25
Last Updated:        2026-09-25
AI Agent:            Antigravity
Approval Status:     Approved by User
Approved By:         User
Approval Date:       2026-09-25
AI Verification:     Complete (100% Automated Testing Suite)
Human Verification:  Pending Human Verification

---

## 1. Problem Statement & User Findings

The user uploaded `sample_claims - Florida.xlsx` and reported:
1. **AntiCaptcha works in Settings test launch, but browser launches without AntiCaptcha in workflow**:
   - In Settings (`/settings`), the Test Launch succeeds with the green banner: `CHROME Live Launch Verified Successfully (Worker: Active, ID: gcpdbjbmekkdlkpldjgffhmapgpdlcpj)`.
   - In the real scraping workflow, Chrome launched without AntiCaptcha active on the toolbar.
2. **Browser is not navigating to all court portal sites for data search and scraping**:
   - In the real scraping workflow, tabs were not actively navigating across county court portals.
3. **Queue items still not appearing in "Ordered Pending Queue (FIFO Priority)"**:
   - Dashboard showed `Failed / Retried: 10 (Ready to retrigger)` and `Ordered Pending Queue: 0 WAITING`.
4. **Scraper Error on Claim #800227314**:
   - `Browser automation session failure for Claim 800227314: name 'KNOWN_ANTICAPTCHA_IDS' is not defined`
5. **Claim Detail Diagnostic Notice**:
   - `Browser automation stages not recorded — this claim was processed via Mock / Seed mode or a legacy pipeline. Stages 1–7 (Browser Launch through Database Commit) require a real-time scraper run from the Attended or Headless worker. Only fuzzy_matching and guidewire_trigger stages are available.`

---

## 2. Root Cause Analysis (Deep Diagnostic)

### 2.1 Stale Celery Worker Pool in Memory
- Process inspection confirmed:
  ```
  Celery Workers:
    Worker PID 30436: started 9/24/2026 7:38:33 PM (Stale in-memory code)
    Worker PID 26148: started 9/24/2026 7:38:33 PM (Stale in-memory code)
  Celery Beat:
    Beat PID 26152: started 9/24/2026 7:38:33 PM
    Beat PID 7548: started 9/24/2026 7:38:33 PM
  Celery Flower:
    Flower PID 25412: started 9/24/2026 7:38:34 PM
    Flower PID 29956: started 9/24/2026 7:38:34 PM
  ```
- **The Celery workers were launched over 6 hours ago (7:38 PM).**
- Celery worker processes load Python modules once into memory at process boot and never re-read them from disk.
- When `sample_claims - Florida.xlsx` was uploaded, the 7:38 PM worker picked up Claim `#800227314` and executed the un-restarted `session_runner.py` from memory, raising `NameError: name 'KNOWN_ANTICAPTCHA_IDS' is not defined`.
- This crashed the session immediately, transitioning all 10 claims to `FAILED`. Because the claims became `FAILED` instead of `NEW`, the "Ordered Pending Queue (FIFO Priority)" showed 0 waiting items, and stages 1–7 were never recorded.

### 2.2 Divergence Between Settings Test Launch & Scraper Workflow
- **Settings Test Launch (`settings.py`)**: Uses `ChromeSession` from `browser_manager.py`. It calls `ChromeSession.configure_and_pin_profile()`, pins `Preferences` without copying `Secure Preferences` (preventing HMAC corruption), and probes `chrome://extensions` via `developerPrivate.getExtensionsInfo`. It works 100%.
- **Scraper Workflow (`session_runner.py`)**: `SingleSessionBrowserRunner` had custom browser launching code that:
  1. Copied `Secure Preferences` into temporary worker profiles. In Google Chrome, copying `Secure Preferences` invalidates HMAC integrity signatures, causing Chrome to reject or reset unpacked extensions.
  2. Failed to pin `Preferences` with `ChromeSession.pin_extension_in_preferences()`.
  3. Did not probe `chrome://extensions` registry.

### 2.3 Portal Tabs Not Navigating in `session_runner.py`
- In `backend/app/automation/session_runner.py`:
  ```python
  async def get_or_create_tab(self, portal_key: str, url: str) -> Page:
      ...
      page = await self.context.new_page()
      # BUG: page.goto(url) was NEVER called!
      self.tabs[portal_key] = page
      return page
  ```
  `get_or_create_tab` took `url: str`, but never called `await page.goto(url)`. Tabs remained on `about:blank` during initialization!

---

## 3. Implementation Plan & Proposed Solutions

### 3.1 Unify `SingleSessionBrowserRunner` with `ChromeSession` Parity
In `backend/app/automation/session_runner.py`:
- Align browser launching with `ChromeSession`'s proven architecture:
  - Call `ChromeSession.configure_and_pin_profile()` to ensure engine profiles and toolbar pins are valid.
  - Do NOT copy `Secure Preferences` across profile directories to eliminate HMAC integrity corruption.
  - Call `ChromeSession.pin_extension_in_preferences(pref_file, KNOWN_ANTICAPTCHA_IDS)` directly on the worker profile.
  - Define `KNOWN_ANTICAPTCHA_IDS` at module top-level and inside local fallbacks.
  - Include `chrome://extensions` fallback probe via `developerPrivate.getExtensionsInfo`.

### 3.2 Fix Active Portal Tab Navigation
In `SingleSessionBrowserRunner.get_or_create_tab()`:
- Actively navigate each tab upon creation:
  ```python
  if url and url != "about:blank":
      await page.goto(url, wait_until="domcontentloaded")
  ```
- This ensures Step 1 actively opens and loads Broward, Hillsborough, and Miami-Dade in their respective tabs, visible to the operator in Attended GUI mode.

### 3.3 Dynamic Settings Parity Check
- Verify `scraper_tasks.py` passes all settings from `get_system_settings_async()` to `SingleSessionBrowserRunner`:
  - `browser_engine`, `chrome_binary_path`, `headless_mode`, `chrome_user_data_dir`, `chrome_extension_dir`, `anticaptcha_api_key`, `typing_speed_mode`, `typing_delay_ms`, `action_pacing_ms`, `stealth_clicks`, and `proxy_server`.

### 3.4 Celery Worker Fleet Clean Restart
- Terminate stale Celery worker processes (PIDs 30436, 26148), stale beats (PIDs 26152, 7548), and stale flower monitors (PIDs 25412, 29956).
- Relaunch fresh Celery worker:
  ```powershell
  python -m celery -A app.core.celery_app.celery_app worker -E --loglevel=info -Q ingest,scrapers,matcher,notifications,default --pool=threads --concurrency=10
  ```
- Relaunch fresh Celery beat:
  ```powershell
  python -m celery -A app.core.celery_app.celery_app beat --loglevel=info
  ```

### 3.5 Re-enqueue & Retrigger the 10 Florida Claims
- Trigger `/api/v1/queue/retrigger` to reset the 10 Florida claims (`#800227314`, `#100317408`, etc.) from `FAILED` to `NEW`.
- Confirm they immediately appear in "Ordered Pending Queue (FIFO Priority)" with priority tags (`★ #1 NEXT`, `#2`, `#3...`) and `Florida` badge.
- Run scraping and verify:
  1. Chrome opens in Attended GUI mode with AntiCaptcha pinned on the toolbar.
  2. All 3 tabs navigate to their respective Florida court portals.
  3. Stages 1–7 are recorded and displayed on `/claims/[id]`.

---

## 4. Testing & Verification Checklist

- [x] `pytest tests/test_plan_verification.py` passes (100% - 26 passed)
- [x] `pytest tests/test_settings_workflow_parity.py` passes (100% - 3 passed)
- [x] `ruff check app tests` passes (0 errors)
- [x] `npx tsc --noEmit` passes (0 errors)
- [x] Fresh Celery worker process verified running with current Python module code
- [x] 10 Florida claims retriggered and verified in "Ordered Pending Queue (FIFO Priority)"
- [x] Visual verification of live dashboard and claim detail page captured to `implementation_plan/Images/`
- [x] Video recording captured to `implementation_plan/Recording/`
