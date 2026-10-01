# Implementation Plan: Fleet-Aware Ingestion & Ordered Pending Queue Concurrency

**Implementation ID:** `IMP-2026-0925-011`  
**Date:** 2026-09-25  
**Author:** AI Agent (Antigravity)  
**Status:** Pending User Approval  
**Lifecycle Stage:** Diagnose & Plan  

---

## 1. Executive Summary & User Problem

### User Problem
When a user uploads a spreadsheet containing 10 claims via `/upload`:
1. All 10 claims immediately changed status to `SCRAPING_IN_PROGRESS` (or subsequently `FAILED` due to browser concurrency timeout), even when Fleet size was set to **1x**.
2. Because all 10 claims were simultaneously dispatched, **0 claims** remained in `NEW` status, resulting in the **"ORDERED PENDING QUEUE (FIFO PRIORITY)"** displaying **`0 Waiting / No Pending Queue Items`**.
3. **Expected Behavior:**
   - When Fleet is set to **1x**: Exactly **1 claim** must auto-start execution (`SCRAPING_IN_PROGRESS`), and the remaining **9 claims** must remain in `NEW` status so they appear in the Ordered Pending Queue (FIFO Priority) with count **`9 Waiting`**.
   - When Fleet is set to **2x**: Exactly **2 claims** must auto-start execution (`SCRAPING_IN_PROGRESS`), and the remaining **8 claims** must remain in `NEW` status with count **`8 Waiting`**.
   - When active claims complete or fail, the auto-queue runner sequentially picks up the next claim(s) from the pending queue in strict FIFO order until all claims are completed.

---

## 2. Root Cause Analysis

### Investigation Findings
1. **`backend/app/tasks/ingest_tasks.py` (Lines 176–187):**
   ```python
   # CURRENT FLAWED LOGIC in _async_parse_and_ingest():
   from app.tasks.queue_runner import is_auto_queue_enabled
   if is_auto_queue_enabled():
       for claim in all_active_claims:  # <-- SENDS ALL 10 CLAIMS AT ONCE!
           celery_app.send_task(
               "app.tasks.scraper_tasks.orchestrate_court_scrapers_task",
               args=[claim.id],
               queue="scrapers",
           )
   ```
   - When an Excel/CSV file was ingested, the code iterated over **all** claims in the batch and immediately dispatched Celery tasks for all of them.
   - Celery workers picked up all 10 tasks and set `claim.record_status = RecordStatusEnum.SCRAPING_IN_PROGRESS`.
   - Because 0 claims were left in `RecordStatusEnum.NEW`, `/api/v1/queue/live` reported `total_pending = 0` and empty `pending_items`.
   - Furthermore, Claim 1 acquired the single browser slot semaphore, while Claims 2–10 timed out waiting for the browser slot and failed with: `"Fleet concurrency limit reached (max=1). Claim timed out waiting for an available browser slot."`

2. **Contrast with Working Components:**
   - In `backend/app/api/v1/endpoints/queue.py` (`seed_demo_claims`), 10 claims are inserted as `RecordStatusEnum.NEW`, and then `celery_app.send_task("app.tasks.queue_runner.advance_auto_queue_task", queue="default")` is invoked.
   - `advance_auto_queue_task` properly queries `max_concurrent_claims` (the Fleet size), calculates `available_slots = max_concurrency - active_running_claims`, selects only up to `available_slots` claims in FIFO order (`created_at ASC`), marks only those claims as `SCRAPING_IN_PROGRESS`, and dispatches them.
   - The remaining claims stay in `RecordStatusEnum.NEW`, appearing in the dashboard's Ordered Pending Queue.
   - When a running claim finishes, `advance_auto_queue_task` is triggered to pick the next `NEW` claim sequentially.

3. **Secondary Flood Vulnerabilities Identified:**
   - `backend/app/api/v1/endpoints/claims.py` (`bulk_retry_claims`): When `auto_enabled` is True, it loops over all retried claims and dispatches all of them immediately without checking `available_slots`.
   - `backend/app/api/v1/endpoints/queue.py` (`retrigger_failed_claims`): When retriggering failed/stuck claims, it was dispatching up to 50 claims directly to `scrapers` queue instead of delegating to `advance_auto_queue_task`.

---

## 3. Architecture & Target Design

```
+---------------------------------------------------------------------------------------------------+
| UPLOAD EXCEL / CSV (e.g., 10 claims)                                                               |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
| backend/app/tasks/ingest_tasks.py                                                                 |
| 1. Parse spreadsheet, validate & normalize rows                                                   |
| 2. Insert all 10 claims with record_status = RecordStatusEnum.NEW                                 |
| 3. session.commit()                                                                               |
| 4. If auto_queue is ENABLED:                                                                      |
|    Trigger advance_auto_queue_task (DO NOT loop dispatch scrapers!)                               |
| 5. If auto_queue is DISABLED:                                                                     |
|    Keep all 10 claims in NEW status (0 running, 10 waiting)                                       |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
| backend/app/tasks/queue_runner.py -> _async_advance_auto_queue()                                  |
| 1. Read max_concurrency from settings (Fleet size: 1x, 2x, 3x, 5x, 10x)                           |
| 2. Count current active claims (SCRAPING_IN_PROGRESS)                                             |
| 3. available_slots = max(0, max_concurrency - active_count)                                       |
| 4. Pick up to available_slots claims with record_status == NEW (FIFO: created_at ASC)             |
| 5. Set selected claims -> SCRAPING_IN_PROGRESS and dispatch to Celery                              |
| 6. Commit to DB                                                                                   |
+---------------------------------------------------------------------------------------------------+
                  |                                                           |
                  v                                                           v
+----------------------------------+                        +----------------------------------+
| ACTIVE EXECUTION FLEET           |                        | ORDERED PENDING QUEUE (FIFO)     |
| Fleet = 1x: 1 Claim Running      |                        | Fleet = 1x: 9 Claims Waiting     |
| Fleet = 2x: 2 Claims Running     |                        | Fleet = 2x: 8 Claims Waiting     |
+----------------------------------+                        +----------------------------------+
                  |                                                           |
                  | When Worker Finishes (Scraper/Fuzzy Matcher)              |
                  +----------------------------------------------------------->
                    Calls advance_auto_queue_task -> Picks next FIFO claim!
```

---

## 4. Detailed Implementation Steps

### Step 1: Fix Ingest Dispatch in `backend/app/tasks/ingest_tasks.py`
- Replace lines 176–188 in `_async_parse_and_ingest()`:
  - Remove the blind loop `for claim in all_active_claims: celery_app.send_task(...)`.
  - When `is_auto_queue_enabled()` is True:
    - Send `app.tasks.queue_runner.advance_auto_queue_task` to Celery `default` queue.
    - Log: `Auto-queue is ENABLED. Ingested {len(all_active_claims)} claims as NEW status. Triggered advance_auto_queue_task to dispatch claims matching fleet concurrency capacity ({max_concurrency}x).`
  - When `is_auto_queue_enabled()` is False:
    - Leave all claims in `RecordStatusEnum.NEW` for manual or queue-runner trigger.

### Step 2: Harmonize Bulk Retry & Retrigger Endpoints
- **`backend/app/api/v1/endpoints/claims.py` (`bulk_retry_claims`):**
  - Compute `available_slots = max(0, max_concurrency - active_count)` when `auto_enabled` is True (identical to `bulk_start_claims`).
  - Dispatch up to `available_slots` claims immediately with `SCRAPING_IN_PROGRESS`.
  - Leave remaining claims in `RecordStatusEnum.NEW` so they queue into FIFO and get picked up sequentially as workers complete.
- **`backend/app/api/v1/endpoints/queue.py` (`retrigger_failed_claims`):**
  - Reset claims to `RecordStatusEnum.NEW`.
  - If `is_auto_queue_enabled()`, trigger `advance_auto_queue_task` to respect fleet limits instead of dispatching up to 50 simultaneous browser tasks.

### Step 3: Automated Unit & Integration Tests
- Add comprehensive test cases in `backend/tests/test_fleet_concurrency.py` (or dedicated test suite `test_fleet_ingest_queue.py`):
  1. **Test Ingestion with Fleet = 1x:**
     - Mock/configure settings with `max_concurrent_claims = 1`.
     - Ingest 10 claims.
     - Verify exactly 1 claim transitions to `SCRAPING_IN_PROGRESS`.
     - Verify 9 claims remain in `RecordStatusEnum.NEW`.
     - Verify `/api/v1/queue/live` returns `total_pending_count == 9` and `active_items` length `== 1`.
  2. **Test Ingestion with Fleet = 2x:**
     - Configure settings with `max_concurrent_claims = 2`.
     - Ingest 10 claims.
     - Verify exactly 2 claims transition to `SCRAPING_IN_PROGRESS`.
     - Verify 8 claims remain in `RecordStatusEnum.NEW`.
     - Verify `/api/v1/queue/live` returns `total_pending_count == 8` and `active_items` length `== 2`.
  3. **Test Sequential Queue Advance:**
     - Complete Claim 1.
     - Run `advance_auto_queue_task()`.
     - Verify Claim 2 transitions from `NEW` to `SCRAPING_IN_PROGRESS`.
     - Verify pending queue decreases from 9 to 8.

---

## 5. Automated Verification Plan

### Test Suite Execution
```bash
# 1. Backend targeted test suite
cd backend
.venv\Scripts\pytest tests/test_fleet_concurrency.py tests/test_column_mapping_ingest.py tests/test_plan_verification.py -q

# 2. Complete backend test suite (all suites)
.venv\Scripts\pytest --tb=short -q

# 3. Python linter (zero errors)
.venv\Scripts\ruff check app tests

# 4. Frontend TypeScript check (zero errors)
cd ..\frontend
npx tsc --noEmit

# 5. PowerShell script syntax verification
cd ..
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"
```

---

## 6. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Celery task execution delay when calling `advance_auto_queue_task` | Ingest commits claims to DB *before* sending `advance_auto_queue_task` to Celery, eliminating race conditions. |
| Ingest batch status showing processing before queue finishes | `batch.status` records ingestion completion (`COMPLETED`), while claims transition through the scraper lifecycle independently. |
| Multiple rapid file uploads causing slot contention | `_async_advance_auto_queue` uses database status counting and Redis semaphore synchronization, guaranteeing concurrency bounds cannot be exceeded. |

---

## 7. Confirmation & Proceed Question

In accordance with the Universal AI Engineering Governance rules (`AGENTS.md` and `diagnose-plan-confirm-execute`), code changes will **only** commence after your explicit approval.
