# Implementation Plan: Task Queue & Telemetry Tab Functionality Verification & Hardening

**Implementation ID:** `IMP-2026-1003-006`  
**Date:** October 3, 2026  
**Document Type:** Implementation Plan (`v1`)  
**Status:** Awaiting User Approval  
**Component:** Frontend (`/settings` Task Queue & Telemetry Tab) + Backend (`queue.py`, `settings.py`, Celery Queue Telemetry)

---

## 1. Executive Summary & Objective

The user requested that the **"Task Queue & Telemetry"** tab functionality in the UAIC Orchestrator Settings (`http://localhost:3000/settings`) be fully working, verified, and tested across all operational layers:
1. **Live Celery Cluster Telemetry & Queue Depths:**
   - Real-time stat cards: *Workers Online*, *Active Running Tasks*, *Pending Queue Backlog*, and *Failed / Stuck Tasks*.
   - Live queue breakdown pills: `ingest`, `scrapers`, `matcher`, `notifications`, `default` channels.
   - Interactive **Refresh Status** trigger.
2. **Celery Worker Queues & Failure Alerts Configuration:**
   - Setting *Max Celery Task Retries* (0–10).
   - Setting *Task Retry Backoff Delay (Seconds)* (5–300s).
   - Setting *Ingestion Database Flush Batch Size* (5–100).
   - Setting *Critical Exception Alert Email*.
   - Setting *Auto-Retrigger Failed Claims & Scrapers* toggle switch.
   - Setting *Failed Claims Retrigger Interval (Minutes)* with quick preset buttons (`5m`, `15m`, `30m`, `60m`).
3. **Durable Persistence & End-to-End Orchestration:**
   - Ensuring settings persist cleanly to SQLite database via `POST /api/v1/settings` with optimistic locking.
   - Ensuring periodic tasks and Celery workers read dynamically from `get_system_settings_async()`.

---

## 2. Root Cause & Gap Analysis

### Gap 1: Telemetry Metrics Hardcoded to Zero in Backend
- **Code:** In `backend/app/api/v1/endpoints/queue.py` lines 138–145:
  ```python
  return QueueStatusResponse(
      active_tasks=0,
      pending_tasks=sum(queues.values()),
      failed_tasks=0,
      completed_tasks=0,
      queues=queues,
      workers_online=workers_online,
  )
  ```
- **Symptom:** The Task Queue & Telemetry tab always displays `0 Active Running Tasks`, `0 Failed / Stuck Tasks`, and `0 Completed Tasks`, even when claims are actively scraping or in failed state!
- **Fix:** In `get_queue_status()`, query the database for live claim record states:
  - `active_tasks`: Count claims with `SCRAPING_IN_PROGRESS`.
  - `failed_tasks`: Count claims with `FAILED`.
  - `completed_tasks`: Count claims with `SCRAPING_COMPLETED`, `COMPLETED`, `MATCH_FOUND`, or `NO_MATCH_FOUND`.
  - `pending_tasks`: Combine Redis broker queue lengths with database pending claims (`max(sum(queues.values()), count(NEW))`).

### Gap 2: Standby & Active Engine State Visibility
- When running in local development mode without a background Redis/Celery worker daemon, `workers_online` is 0, displaying "Standby". The UI subtitle should clearly differentiate between "Cluster nodes active" and "Standby (Auto-Queue/Local Fleet Armed)" so the operator understands execution readiness.

### Gap 3: Preset Buttons & Settings Save Validation
- Verify that clicking the retry interval preset buttons (`5m`, `15m`, `30m`, `60m`) updates the state, highlights the active button, and properly saves to `TaskQueueSettings` in the backend.
- Ensure `POST /api/v1/queue/retrigger` can be triggered and responds with structured retriggered counts.

---

## 3. Scope of Implementation

### Backend Changes:
1. **`backend/app/api/v1/endpoints/queue.py`**:
   - Update `get_queue_status()` to inject `db: AsyncSession = Depends(get_db)` and calculate live task metrics from the database (`active_tasks`, `failed_tasks`, `completed_tasks`, `pending_tasks`).
   - Ensure Redis queue depth check does not hang if Redis is offline (already protected by `_REDIS_STATUS_OFFLINE_UNTIL` and short socket timeouts).

### Frontend Changes:
1. **`frontend/src/app/settings/page.tsx`**:
   - In `activeTab === "queue"`, ensure `fetchQueueStatus()` refreshes smoothly and displays actual metrics.
   - Update StatCard subtitle logic so 0 workers online displays "Fleet Armed / Standby" instead of a generic fallback.
   - Ensure preset buttons `[5m, 15m, 30m, 60m]` highlight correctly against `failed_claims_retry_interval_minutes`.

---

## 4. Verification & Testing Strategy

### Step 1: Automated Integration Test Script (`scripts/verify_task_queue_telemetry_tab.py`)
1. `GET /api/v1/queue/status` -> assert `active_tasks`, `pending_tasks`, `failed_tasks`, `completed_tasks`, `queues`, and `workers_online` return valid integers.
2. `POST /api/v1/settings` -> update queue settings:
   - `max_task_retries = 3`
   - `task_retry_delay_seconds = 45`
   - `batch_chunk_size = 30`
   - `auto_retry_failed_scrapes = True`
   - `failed_claims_retry_interval_minutes = 30`
3. Verify settings are reflected in `GET /api/v1/settings`.
4. `POST /api/v1/queue/retrigger` -> assert structured response with `retriggered_count`.
5. Restore original queue settings.

### Step 2: Playwright Headless/GUI Browser Verification
1. Navigate to `http://localhost:3000/settings`.
2. Click **"Task Queue & Telemetry"** tab.
3. Assert header "Live Celery Cluster Telemetry & Queue Depths" is visible.
4. Verify all 4 stat cards render numeric values.
5. Click **"Refresh Status"** -> verify spin animation and live refresh.
6. Verify individual Celery queue pills (`ingest`, `scrapers`, `matcher`, `notifications`, `default`).
7. Click preset button `15m` -> verify input value is `15`.
8. Toggle "Auto-Retrigger Failed Claims & Scrapers" switch.
9. Click "Save Settings" -> verify success toast.
10. Capture full-page screenshot to `docs/task_queue_telemetry_verified.png`.

### Step 3: Lint & Build Health Checks
- `ruff check app tests` (0 errors)
- `npx tsc --noEmit` (0 errors)
- `check_ps1_syntax.ps1` (0 errors)

---

## 5. Definition of Done
- Real live task telemetry reported in `GET /api/v1/queue/status` instead of hardcoded zeroes.
- Queue tab UI verified interactively with zero errors or visual glitches.
- Automated test script passes 100%.
- Verified record and visual proof saved to `docs/`.
