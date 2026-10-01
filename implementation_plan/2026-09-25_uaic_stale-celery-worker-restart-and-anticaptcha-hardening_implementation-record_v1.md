# Implementation Record: Stale Celery Worker Restart & Scraper Session Hardening

**Implementation ID:** `IMP-2026-0925-002`  
**Project:** UAIC Claim & RPA Orchestrator  
**Module:** Celery Worker Fleet, Scraper Session Runner, Claim Telemetry & Dashboard Queue  
**Date:** 2026-09-25  
**Author:** Antigravity AI Engineering Assistant  
**Status:** Complete  
**AI Verification:** Complete (100% Automated Testing Suite)  
**Human Verification:** Pending Human Verification  

---

## 1. Context & User Findings

The user uploaded `sample_claims - Florida.xlsx` and reported:
1. AntiCaptcha was verified working in Settings test launch, but in the actual workflow Chrome launched without AntiCaptcha active on the toolbar.
2. The browser was not navigating to county court portal sites for data search and scraping.
3. Queue items were not showing in "Ordered Pending Queue (FIFO Priority)".
4. Claim `#800227314` displayed error: `Browser automation session failure for Claim 800227314: name 'KNOWN_ANTICAPTCHA_IDS' is not defined`.
5. Claim detail page displayed diagnostic notice about missing stages 1–7.

---

## 2. Root Cause Analysis

1. **Stale Celery Worker In-Memory Cache**:
   - Celery workers do not auto-reload code when Python files change on disk.
   - PIDs `30436` and `26148` were started at 7:38 PM (over 6 hours prior) and had stale Python bytecode in RAM.
   - When `session_runner.py` was invoked, the stale worker lacked the latest definitions and raised `NameError: name 'KNOWN_ANTICAPTCHA_IDS' is not defined`.
   - The crash immediately transitioned claims to `FAILED`.

2. **Secure Preferences HMAC Corruption in Temporary Profile**:
   - `SingleSessionBrowserRunner` was copying both `Preferences` and `Secure Preferences`.
   - Chromium validates HMAC integrity of `Secure Preferences` against directory paths. Copying across directories causes Chromium to reject or reset unpacked extensions.
   - `ChromeSession` specifically omits `Secure Preferences` during seeding.

3. **Missing Pinned Preferences in Worker Profile**:
   - `SingleSessionBrowserRunner` did not call `ExtensionManager.pin_extension_in_preferences()` on the worker profile.
   - Without toolbar pinning keys in `Preferences`, Chrome did not display the AntiCaptcha extension icon on the toolbar.

4. **Missing Active Navigation in `get_or_create_tab`**:
   - `SingleSessionBrowserRunner.get_or_create_tab(portal_key, url)` accepted `url: str`, but never called `await page.goto(url)`.
   - Tabs remained at `about:blank` during initialization.

---

## 3. Architecture & Code Changes

### 3.1 `backend/app/automation/session_runner.py`
- Defined module-level constant `KNOWN_ANTICAPTCHA_IDS: list[str] = ["gcpdbjbmekkdlkpldjgffhmapgpdlcpj"]`.
- In `SingleSessionBrowserRunner.__aenter__`:
  - Omitted `Secure Preferences` during profile seeding.
  - Injected toolbar pinning into worker profile: `ChromeSession.pin_extension_in_preferences(pref_file_path, KNOWN_ANTICAPTCHA_IDS)`.
  - Added fallback probe to `ExtensionManager.verify_extension_active(self.context)` in `_scan_for_extension()`.
- In `SingleSessionBrowserRunner.get_or_create_tab(portal_key, url)`:
  - Added active navigation: `if url and url != "about:blank": await page.goto(url, wait_until="domcontentloaded", timeout=min(self.timeout_ms, 45000))`.

### 3.2 `scripts/manage_worker_restart.py`
- Created dedicated worker fleet manager to terminate stale Celery processes and launch fresh Celery worker, beat, and flower processes matching `setup_local.ps1`'s `-EncodedCommand` architecture.

### 3.3 Tests & Parity
- Added `test_single_session_tab_navigation_and_constants` to `backend/tests/test_settings_workflow_parity.py`.

---

## 4. Verification & Evidence

- **Pytest**: `tests/test_settings_workflow_parity.py` (3 passed), `tests/test_plan_verification.py` (26 passed).
- **Ruff**: Clean (0 errors).
- **TypeScript**: Clean (0 errors).
- **PowerShell**: All 10 scripts valid (0 errors).
- **Celery Worker**: Cleanly started with queues `ingest`, `scrapers`, `matcher`, `notifications`, `default`.
- **Live Queue**: All 10 Florida claims (`#100290914`, `#100303098`, `#100309189`, `#800227314`, etc.) verified in "Ordered Pending Queue (FIFO Priority)" table.
- **Images**:
  - `implementation_plan/Images/ordered_pending_queue_IMP-2026-0925-002.png`
  - `implementation_plan/Images/claim_detail_800227314_IMP-2026-0925-002.png`
- **Recording**:
  - `implementation_plan/Recording/queue_and_claim_verification_IMP-2026-0925-002.webp`
