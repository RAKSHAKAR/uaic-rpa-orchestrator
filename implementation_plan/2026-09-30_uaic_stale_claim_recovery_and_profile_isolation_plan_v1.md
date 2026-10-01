# Implementation Plan: Stale Claim Auto-Recovery & Profile Downgrade Resilience

**Implementation ID:** `IMP-2026-0930-001`  
**Document:** `implementation_plan/2026-09-30_uaic_stale_claim_recovery_and_profile_isolation_plan_v1.md`  
**Author:** Antigravity Engineering Agent  
**Date:** 2026-09-30  
**Status:** Pending User Confirmation (NO APPROVAL = NO IMPLEMENTATION)

---

## 1. Problem Statement & User Impact

### Symptom
The user reported that after setting the system to **Attended GUI mode**, no visible browser window was executing on their desktop, even though the dashboard displayed:
* **Active Execution Fleet:** `(1 / 1 Busy)`
* **Active Worker #1:** `#100298095 TIFFANY LATONYA YOUNG`
* **Timer:** Ticking up (e.g. `11s`, `Active`) with a pulsing green `"Parallel RPA Running"` badge.

### Root Cause Analysis
1. **Stale Zombie Claim Deadlock:**
   * Claim `#100298095` was originally started at `05:57:11 AM UTC` (>13 hours ago).
   * When Celery was previously stopped or restarted, Claim `#100298095` was left permanently with status `SCRAPING_IN_PROGRESS` in the database.
   * Because `max_concurrent_claims = 1`, `available_slots = max_concurrency - len(active_claims) = 1 - 1 = 0`.
   * `queue_runner.py` logged `"All 1 worker slots are active (1 in progress). Waiting."` and completely deadlocked the FIFO queue from advancing to the next 497 pending claims.
   * No task was actually executing in Celery (`active_tasks: 0`). The UI timer was merely counting local elapsed time in the browser based on the claim's status.

2. **Browser Profile Downgrade Crash (`exitCode=33`):**
   * When claim `#100301036` was dispatched, `SingleSessionBrowserRunner` resolved `browser_engine="chrome"` with `has_extension=True`.
   * On Windows, `resolve_browser_launch_target` deliberately auto-routes to bundled Chromium (`None, None`) because modern Windows Chrome blocks unpacked `--load-extension`.
   * However, `SingleSessionBrowserRunner` passed the Google Chrome persistent profile directory (`backend/data/browser_profile/chrome`) to bundled Chromium.
   * Bundled Chromium (v124) detected that this directory had been modified by a newer host Chrome version, attempted to downgrade, was blocked with `Access is denied (0x5)`, and crashed immediately with `exitCode=33`.
   * `ChromeSession` in `browser_manager.py` already had profile isolation for this scenario (`target_dir = self.get_persistent_profile_dir("chromium")`), but `SingleSessionBrowserRunner` in `session_runner.py` was missing this isolation check.

3. **Incomplete Claim Stop Endpoint:**
   * In `/api/v1/claims/{id}/stop`, cancelling a claim marked the DB record as `FAILED`, but did not call `remove_active_queue_item_id(claim_id)` in Redis nor trigger `celery_app.send_task("app.tasks.queue_runner.advance_auto_queue_task")` to immediately dispatch the next queue item.

---

## 2. Proposed Architecture & Remediation

### 2.1 Stale Claim Auto-Reconciliation in `queue_runner.py`
Before calculating `available_slots` in `_async_advance_auto_queue()`:
1. Query all claims in `SCRAPING_IN_PROGRESS`.
2. Inspect active Celery worker tasks via `celery_app.control.inspect().active()` (or Redis lock TTL).
3. If a claim in `SCRAPING_IN_PROGRESS` has been in progress for longer than `STALE_CLAIM_TIMEOUT_MINUTES` (default: 10 minutes) AND has no active task in the Celery worker fleet:
   * Mark `claim.record_status = RecordStatusEnum.FAILED`.
   * Set `claim.last_error = "Recovered from stale uncompleted session (process interrupted or worker restarted)"`.
   * Log an audit event `STALE_CLAIM_RECOVERED`.
   * Remove it from active Redis IDs.
4. This ensures that anytime Celery or the machine restarts, all zombie claims are automatically cleaned up on the very first queue cycle.

### 2.2 Profile Isolation in `SingleSessionBrowserRunner` (`session_runner.py`)
Mirror the proven profile isolation from `ChromeSession`:
```python
if (self.browser_engine or "chrome").lower() in ("chrome", "google-chrome") and has_extension:
    # On Windows, resolve_browser_launch_target uses bundled Chromium for extension compatibility.
    # Route profile to 'chromium' subfolder to prevent Chromium exitCode=33 downgrade crash.
    engine_key = "chromium"
```
Ensure that bundled Chromium exclusively uses its own dedicated profile and never collides with host Google Chrome profile caches.

### 2.3 Stop Endpoint Queue Signal (`claims.py`)
In `stop_single_claim()` (`POST /api/v1/claims/{claim_id}/stop`):
1. Call `remove_active_queue_item_id(claim.id)` in Redis.
2. If `is_auto_queue_enabled()` is True:
   * Dispatch `celery_app.send_task("app.tasks.queue_runner.advance_auto_queue_task", queue="default")`.
3. This guarantees that user-cancelling a claim instantly frees the worker slot and launches the next claim without requiring manual intervention.

---

## 3. Files Impacted

| File | Change Summary |
|---|---|
| [`backend/app/tasks/queue_runner.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/queue_runner.py) | Add `_reconcile_stale_in_progress_claims()` before evaluating available slots in `_async_advance_auto_queue()` |
| [`backend/app/automation/session_runner.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/session_runner.py) | Add engine profile re-routing to `"chromium"` when `browser_engine == "chrome"` and extension is active |
| [`backend/app/api/v1/endpoints/claims.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/api/v1/endpoints/claims.py) | Call `remove_active_queue_item_id()` and dispatch `advance_auto_queue_task` in `stop_single_claim()` |
| [`backend/tests/test_queue_runner.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/tests/test_queue_runner.py) | Unit tests verifying stale claim auto-recovery and stop endpoint queue advancement |

---

## 4. Verification & Testing Strategy

1. **Unit & Regression Testing**:
   * Run full backend test suite: `.venv\Scripts\pytest tests/test_queue_runner.py tests/test_browser_matrix.py -v`
   * Run full 554 backend test suite: `.venv\Scripts\pytest --tb=short -q` (100% pass target)
   * Verify zero Python lint issues: `.venv\Scripts\ruff check app tests`
   * Verify TypeScript compilation: `cd frontend && npx tsc --noEmit`
2. **Operational Simulation**:
   * Seed a claim in `SCRAPING_IN_PROGRESS` with timestamp 20 minutes in the past.
   * Trigger queue advance; verify the stale claim is automatically recovered to `FAILED`, the slot is freed, and the next item processes without deadlock.
   * Verify `SingleSessionBrowserRunner` launches in Attended GUI without downgrade exitCode 33 errors.

---

## 5. Definition of Done Checklist

- [ ] `queue_runner.py` reconciles stale `SCRAPING_IN_PROGRESS` claims automatically
- [ ] `session_runner.py` isolates profile directory when extension is loaded to prevent exitCode 33
- [ ] `claims.py` triggers queue advancement and frees Redis slot on claim stop
- [ ] Pytest passes (554+ tests, 100%)
- [ ] Ruff lint clean (0 errors)
- [ ] Frontend TypeScript clean (`npx tsc --noEmit` clean)
- [ ] Implementation Record and Walkthrough created in `implementation_plan/`
