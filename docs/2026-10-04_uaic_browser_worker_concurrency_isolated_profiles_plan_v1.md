# Implementation Plan: Browser Worker Concurrency Isolation & Settings Adherence

**Implementation ID:** `IMP-2026-1004-002`  
**Date:** 2026-10-04  
**Status:** Complete  
**AI Verification:** Complete (100% Automated Testing Suite)  
**Human Verification:** Awaiting Human Verification  
**Target:** `backend/app/tasks/scraper_tasks.py` & `backend/app/automation/session_runner.py`

---

## 1. Problem Statement & Root Cause Diagnosis

### Symptom
When the Celery worker fleet is running with `max_concurrent_claims: 10`, 10 worker threads are dispatched concurrently. However, parallel browser execution fails across worker threads with:
```
playwright._impl._errors.TargetClosedError: BrowserType.launch_persistent_context: Target page, context or browser has been closed
exitCode=21
```

### Root Cause Analysis
1. In `backend/app/tasks/scraper_tasks.py` (lines 579–598), `browser_runner_kwargs` is constructed from DB settings (`get_system_settings_async()`), including `headless`, `browser_engine`, `timeout_ms`, etc.
2. However, `browser_runner_kwargs` does **not** specify `worker_id` or `isolated_profile`.
3. In `backend/app/automation/session_runner.py` (line 251):
   ```python
   if self.worker_id is None and not self.isolated_profile and not ChromeSession.is_profile_locked(canonical_profile):
       self.profile_to_use = str(canonical_profile)
       self.is_temp_profile = False
   ```
4. When 10 parallel threads invoke `__aenter__` simultaneously, all 10 threads check `is_profile_locked` in the same millisecond before any Chromium process has started.
5. All 10 threads select the exact same directory: `backend/data/browser_profile/chromium`.
6. When Chromium processes 2 through 10 attempt to start with an already-locked user data directory, Chromium immediately aborts with exit code 21.

---

## 2. Proposed Changes & Implementation Strategy

### A. Update `scraper_tasks.py` to Pass Worker Concurrency Context
In `backend/app/tasks/scraper_tasks.py`:
- Pass `worker_id=str(claim.id)` and `isolated_profile=(max_concurrency > 1)` into `browser_runner_kwargs`.
- Ensure each concurrent worker thread receives a dedicated, pre-seeded profile directory (`tempfile.mkdtemp(prefix=f"uaic_worker_{claim.id[:8]}_")`).

### B. Harden `session_runner.py` Multi-Process Profile Selection
In `backend/app/automation/session_runner.py`:
- Sanitize worker ID for directory prefix safety.
- When `isolated_profile` is active or `worker_id` is supplied, ensure the isolated profile is properly pre-seeded with AntiCaptcha extension configuration and toolbar pinning from the master canonical profile.
- Verify `__aexit__` reliably removes temporary isolated directories via `shutil.rmtree(self.profile_to_use, ignore_errors=True)`.

### C. Strict Settings Page Adherence Verification
Ensure all parameters from `GET /api/v1/settings` are respected:
- `automation.max_concurrent_claims` (1 to 10) controls queue dispatcher limits.
- `automation.headless_mode` controls browser visibility (Headless vs. Attended GUI).
- `automation.browser_engine` (chrome, chromium, edge) controls binary resolution.
- `automation.typing_speed_mode`, `typing_delay_ms`, `action_pacing_ms`, and `stealth_clicks` are passed to typing actuators.
- `automation.anticaptcha_api_key` and plugin flags (`rc2`, `rc3`, `hcaptcha`, `turnstile`) are preserved across all isolated worker profiles.

---

## 3. Verification Plan

1. **Unit & Integration Tests:**
   - Run `pytest backend/tests/test_browser_manager.py` and `pytest backend/tests/test_fleet_concurrency.py`.
2. **Full Test Suite & Static Analysis:**
   - Run `pytest --tb=short -q` (must maintain 100% pass rate).
   - Run `ruff check backend/app backend/tests` (0 errors).
   - Run `tsc --noEmit` in frontend (0 errors).
   - Run `scripts/check_ps1_syntax.ps1` (0 errors).
3. **Live Fleet Concurrency Test:**
   - Restart the Celery worker and verify that multiple parallel browser instances launch simultaneously in isolated profiles without exit code 21 collisions.
   - Verify that claims advance and update their scraping stage timings.
4. **Documentation & Verified Record:**
   - Record all results in `docs/2026-10-04_uaic_browser_worker_concurrency_isolated_profiles_verified_record_v1.md`.
