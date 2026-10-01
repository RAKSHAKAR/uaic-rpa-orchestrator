# Implementation Plan: AntiCaptcha Service Worker Verification & Error Logging Hierarchy

**Implementation ID:** `IMP-2026-0925-004`  
**Project:** UAIC Claim & RPA Orchestrator  
**Module:** Automation Settings, ChromeSession Extension Manager, Toolbar Pinning & Profile Setup  
**Date:** 2026-09-25  
**Author:** Antigravity AI Engineering Assistant  
**Status:** Ready for Review  
**AI Verification:** In Progress  
**Human Verification:** Pending Human Verification  

---

## 1. Problem Statement & User Diagnosis

### 1.1 Observed Issue
When clicking **"Configure & Pin"** under **Toolbar Pinning & Profile Setup** on `/settings`:
* The status remained `Pending Setup`.
* An error banner was displayed:
  > **`AntiCaptcha extension configured, but service worker verification timed out or was not detected.`**

### 1.2 User Prompt Requirements (`ManualPrompt.txt` Lines 317–323)
* **Note 1 (Error Handling & Hierarchy):**
  * On any error or stopper during execution:
    * Capture page error screenshot and store in `backend/screenshots/{category}/{identity}/` maintaining strict folder hierarchy when error screenshot capture is enabled.
    * Save detailed execution logs in `backend/logs/{category}/{identity}/execution.log` maintaining folder hierarchy for developer root-cause analysis.
* **Note 2 (Governance & Documentation):**
  * Update skills, flows, and documentation; save implementation plan in `implementation_plan/`; run 100% automated test suite (pytest, ruff, tsc, ps1) with visual verification.

---

## 2. Root Cause Analysis (RCA)

1. **Manifest V3 Lazy Service Worker Activation:**
   * In Chromium MV3, extension background service workers are event-driven and lazy-loaded.
   * `ChromeSession.start()` in `backend/app/automation/browser_manager.py` loops for up to 3.0 seconds (15 iterations × 200ms) checking `context.service_workers`. If the service worker has not yet awakened, `detected_id` evaluates to `None`.
   * The secondary fallback probe navigates to `chrome://extensions` and queries `window.chrome.developerPrivate`. In modern Chromium without explicit test flags, automated access to `chrome://extensions` is blocked by browser security, resulting in `extension_loaded = False` and `service_worker_active = False`.

2. **Active Wakeup Probe Solution:**
   * Directly navigating a probe page to `chrome-extension://{known_id}/popup_v3.html` immediately returns HTTP 200 and forces Chromium's extension manager to spawn and register the background service worker in under 500ms.

3. **Stale Profile Locks on Dedicated Setup Profile:**
   * `setup_extension_endpoint` targets `backend/data/browser_profile/chrome`.
   * If an orphan Chrome process or previous test run left a `SingletonLock`, Playwright throws exitCode 21 (profile in use), causing the verification coroutine to fail silently.
   * `ChromeSession.clean_profile_locks_and_orphans()` must be executed before launching the setup verification session.

4. **Razor-Thin Asyncio Timeout (20.0s):**
   * On Windows under Celery and development server load, a cold browser start with extension loading can take between 15s and 22s.
   * `asyncio.wait_for(session.start(), timeout=20.0)` triggers premature `TimeoutError`. Raising the timeout to **45.0s** eliminates false-negative timeouts.

5. **Diagnostic Error Logging & Screenshot Capture:**
   * If any failure occurs during setup verification, capture an error screenshot to `backend/screenshots/setup/` and write structured diagnostic logs to `backend/logs/setup/execution.log` per `ManualPrompt.txt`.

---

## 3. Proposed Changes & Implementation Scope

### Component 1: Active Extension Wake-up in `browser_manager.py`
* **File:** [`backend/app/automation/browser_manager.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/browser_manager.py)
* **Changes:**
  * In `ChromeSession.start()`, if `_scan_for_extension()` does not detect a service worker in the initial check, proactively probe `chrome-extension://{kid}/popup_v3.html` across all `KNOWN_ANTICAPTCHA_IDS`.
  * Verify HTTP 200 response and awaken the service worker thread.
  * Ensure `service_worker_active` and `extension_loaded` are set to `True` upon successful popup verification.

### Component 2: Profile Sanitation & Headroom in `settings.py`
* **File:** [`backend/app/api/v1/endpoints/settings.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/api/v1/endpoints/settings.py)
* **Changes:**
  * Clean profile locks and terminate orphan processes on `persistent_dir` before starting verification.
  * Increase `asyncio.wait_for` timeout from 20.0s to 45.0s.
  * If verification fails, capture diagnostic screenshot to `backend/screenshots/setup/error_setup.png` and record structured logs in `backend/logs/setup/execution.log`.
  * Ensure settings update (`extension_setup_verified = True`) is persisted and returned.

---

## 4. Verification & Testing Plan

1. **Backend Automated Tests:**
   * Run pytest suite: `.venv\Scripts\pytest tests/test_extension_pinning_and_setup.py tests/test_browser_manager.py tests/test_api.py -v`
   * Run full pytest suite (475 tests).
   * Run `ruff check app tests`.
2. **Frontend Type Check:**
   * Run `npx tsc --noEmit`.
3. **PowerShell Syntax Check:**
   * Run `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_ps1_syntax.ps1`.
4. **Live Verification:**
   * Execute live test against `POST /api/v1/settings/setup-extension` to verify `verified: true`, `service_worker_active: true`, and `toolbar_action_verified: true`.
   * Capture verification evidence.
