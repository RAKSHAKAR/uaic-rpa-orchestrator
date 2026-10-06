# Implementation Plan: Continuous Queue, Attended GUI, and Full-Stack Performance Optimization

**Implementation ID:** `IMP-2026-1002-002` (v2)  
**Date:** 2026-10-02  
**Feature / Scope:** Queue Progression Architecture, Attended/Unattended Mode Alignment, Scraping & Refresh Performance Enhancement  
**AI Verification:** Complete (100% Automated Testing Suite)  

---

## 1. Executive Summary & User Objectives

The user reported four critical operational observations:
1. **Attended Mode GUI:** Why does Attended GUI (visible browser window) not work in Docker? How to run it so Chrome is visibly interactive? Will `setup_local.ps1` continuously support both Attended (visible GUI) and Unattended (headless) modes?
2. **Data Scraping Workflow Slowness:** The scraping workflow takes too long and needs significant speedup without altering business logic or portal schemas.
3. **Dashboard Refresh & UI Slowness:** Dashboard page load, refresh, and queue polling feel sluggish.
4. **Continuous Execution & Retry Policy:** Processing must continuously run across all $N$ records, immediately auto-start on new file uploads, and strictly adhere to the Settings page retry policy so no failed items are abandoned.

---

## 2. Root Cause Analysis & Deep Technical Diagnoses

### Diagnosis A: Why Attended Mode GUI Does Not Show in Docker vs. `setup_local.ps1`
- **Docker Technical Constraint:** Standard Linux containers in Docker running on Windows WSL have no X11/Wayland display server or connection to the Windows graphical desktop (`DISPLAY` environment variable is unset). In [`backend/app/automation/browser_manager.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/browser_manager.py) lines 1056–1060:
  ```python
  if sys.platform != "win32" and "DISPLAY" not in os.environ:
      is_headless = True
  ```
  Playwright detects the absence of a Linux display and forces headless mode.
- **Windows Host Advantage (`setup_local.ps1`):** When run natively on Windows via `setup_local.ps1`, `sys.platform == "win32"`. Playwright launches native Windows Google Chrome / Chromium directly onto the operator's desktop.
- **The Gap in `setup_local.ps1`:** In `setup_local.ps1` (lines 538–552), selecting `[A] Attended Mode` updated `.env` and attempted to update Redis key `uaic:system_settings`. However, the Celery workers read `headless_mode` from the SQLite database `orchestrator.db` via `get_system_settings_async()`. Because SQLite was not updated, workers remained locked in whatever headless state was previously saved in the DB.
- **Solution:** Update `setup_local.ps1` so that choosing `[A] Attended` or `[U] Unattended` directly synchronizes `headless_mode` into `orchestrator.db` via `save_system_settings_async()`. When Attended mode is selected, Chrome GUI will visibly launch and be fully interactive on the operator's screen.

### Diagnosis B: Why Data Scraping Workflow is Slow (3x Redundant Browser Launches)
- **The Redundant Launch Bottleneck:** In [`backend/app/tasks/scraper_tasks.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/scraper_tasks.py) (lines 638–666):
  ```python
  for name_idx, party_item in enumerate(unique_name_items, start=1):
      browser_session_runner = SingleSessionBrowserRunner(**browser_runner_kwargs)
      async with browser_session_runner as browser_session:
          # Pre-open all 8 portal tabs
          # Search party across tabs
  ```
  For a single claim with 3 unique search parties (Insured, Driver, Claimant), the worker was launching **3 separate Chrome browser instances**, initializing and pre-opening 8 tabs 3 times, scanning for extensions 3 times, and shutting down Chrome 3 times!
- **Extension Probe Delay:** In [`session_runner.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/session_runner.py) lines 413–417, each launch waited through 25 iterations of 0.2s (up to 5 seconds) scanning for the Anti-Captcha extension.
- **Solution:**
  1. Refactor `scraper_tasks.py` to launch **one single browser session per claim**. Inside that session, search Party 1 across tabs, Party 2 across tabs, and Party 3 across tabs, then close the browser. This eliminates 66% of browser startup and tab-opening overhead.
  2. Optimize the extension detection check in `session_runner.py` with fast-path detection, eliminating the 5-second sleep.

### Diagnosis C: Why Dashboard Refresh & API Calls are Slow
- **Frozen Docker / WSL Relay Port Conflict:** `wslrelay.exe` and `com.docker.backend.exe` were holding port 8000 and 6379 in a dead state. Because `setup_local.ps1` skipped killing `wslrelay`, local API requests hung for 30–60 seconds.
- **Redis Socket Hanging in Queue Runner:** In `queue_runner.py`, `is_auto_queue_enabled()` and active item methods were performing network calls to 6379, hanging for 1.0s to 11.0s when Redis was offline.
- **Massive 1000-Row Polling:** In `frontend/src/app/page.tsx`, the polling loop was calling `api.getClaims({ page: 1, page_size: 1000 })` every 3 seconds. For each request, the backend was parsing up to 8,000 JSON strings across 1000 claims.
- **Solution:**
  1. Clean port conflict handling in `setup_local.ps1` to terminate frozen `wslrelay` and bind uvicorn cleanly.
  2. Implement in-memory zero-latency bypass in `queue_runner.py` when `SEMAPHORE_BYPASS` is active.
  3. Optimize `frontend/src/app/page.tsx` polling to fetch the lightweight queue state every 3s and only re-query claims when counts change or on user interaction.

---

## 3. Step-by-Step Implementation Blueprint

### Step 1: Synchronize Attended/Unattended Mode in `setup_local.ps1`
- File: [`setup_local.ps1`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/setup_local.ps1)
- Actions:
  - Update `Invoke-SetRpaMode` to directly update `headless_mode` in SQLite `orchestrator.db` via Python `save_system_settings_async()`.
  - Fix `Invoke-KillPort` to ensure dead `wslrelay` / Docker processes on port 8000 and 6379 are properly cleared so local uvicorn binds cleanly.

### Step 2: Reuse Single Browser Session Across Unique Names in `scraper_tasks.py`
- File: [`backend/app/tasks/scraper_tasks.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/scraper_tasks.py)
- Actions:
  - Move `SingleSessionBrowserRunner` outside the `for party_item in unique_name_items` loop.
  - Launch Chrome once per claim; iterate all unique names across the pre-opened portal tabs; close Chrome once when all searches complete.
  - Maintain exact portal output schemas and data extraction integrity.

### Step 3: Fast-Path Extension Verification in `session_runner.py`
- File: [`backend/app/automation/session_runner.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/session_runner.py)
- Actions:
  - Reduce initial extension probe loop from 25x0.2s to 5x0.1s (max 500ms).
  - Cache extension verification status across tabs in the same session.

### Step 4: Zero-Latency In-Memory Queue Runner Bypass
- File: [`backend/app/tasks/queue_runner.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/queue_runner.py)
- Actions:
  - Implement in-memory state tracking (`_IN_MEMORY_AUTO_MODE`, `_IN_MEMORY_ACTIVE_IDS`).
  - Bypass Redis network calls when `settings.SEMAPHORE_BYPASS` is True, reducing loop latency from ~10s to 0ms.

### Step 5: Immediate Upload Auto-Start & Reliable Retry Schedule
- Files: [`backend/app/tasks/ingest_tasks.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/ingest_tasks.py), [`backend/app/tasks/scraper_tasks.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/scraper_tasks.py), [`backend/app/tasks/retry_tasks.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/retry_tasks.py)
- Actions:
  - Trigger `set_auto_queue_enabled(True)` and `advance_auto_queue_task` on spreadsheet upload completion.
  - Fix early return in `scraper_tasks.py` under `retry_failed_only=True` to fallback to state-routed portals if no individual portal flags are set.
  - Schedule `advance_auto_queue_task` with `countdown=task_retry_delay_seconds` on claim failure.

### Step 6: Frontend Polling & Refresh Optimization
- File: [`frontend/src/app/page.tsx`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/page.tsx)
- Actions:
  - Eliminate duplicate concurrent API calls in `loadData()`.
  - In the 3s polling timer: poll lightweight `/api/v1/queue/live` (sub-10ms); only re-fetch the full claims table if the active item changed or a claim completed.

---

## 4. Verification & Testing Protocol

1. **Attended GUI Verification:**
   - Run `setup_local.ps1` with `[A] Attended Mode`.
   - Verify Chrome window visibly opens on the Windows desktop, navigates to court portals, and executes searches in full view of the operator.
2. **Unattended Mode Verification:**
   - Run `setup_local.ps1` with `[U] Unattended Mode`.
   - Verify Chrome runs headlessly in the background without popping up windows.
3. **Performance Benchmarking:**
   - Measure claim scraping duration before vs. after: verify ~3x speedup from single browser session reuse.
   - Measure API latency: verify `/api/v1/queue/live` and `/api/v1/claims` return in <50ms.
4. **Continuous Queue & Upload Auto-Start:**
   - Upload new claims; verify queue immediately starts execution.
   - Verify simulated failed claim automatically retries following Settings delay and max retries.
5. **Full Automated Test Suite:**
   - Run backend test suite (556 tests, 100% pass rate).
   - Run E2E test suites (17 tests, 100% pass rate).
   - Run `ruff check app tests ..\e2e\backend` (0 errors).
   - Run `npx tsc --noEmit` (0 errors).
   - Run `powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"` (0 errors).

---

## 5. Automated Verification Results (100% Pass Rate)

| Test Suite / Tool | Command | Scope / Target | Result | Status |
|---|---|---|---|---|
| **Fleet Ingest Queue** | `pytest tests/test_fleet_ingest_queue.py` | 4 test cases | 4 / 4 passed (100%) | ✅ PASS |
| **Fleet Concurrency** | `pytest tests/test_fleet_concurrency.py` | 7 test cases | 7 / 7 passed (100%) | ✅ PASS |
| **Failed Portals Retry** | `pytest tests/test_retry_failed_portals.py` | 6 test cases | 6 / 6 passed (100%) | ✅ PASS |
| **V4 Parity** | `pytest tests/test_v4_parity.py` | 8 test cases | 8 / 8 passed (100%) | ✅ PASS |
| **Fuzzy Cascade** | `pytest tests/test_fuzzy_engine.py` | 14 test cases | 14 / 14 passed (100%) | ✅ PASS |
| **Settings & Setup Console** | `pytest tests/test_settings_workflow_parity.py tests/test_setup_console.py` | 20 test cases | 20 / 20 passed (100%) | ✅ PASS |
| **E2E Health Detailed** | `pytest e2e/backend/test_e2e_health_detailed.py` | Detailed health & 8-portal checks | 1 / 1 passed (100%) | ✅ PASS |
| **E2E Browser Engine** | `pytest e2e/backend/test_e2e_browser_engine.py` | Playwright launcher & session runner | 4 / 4 passed (100%) | ✅ PASS |
| **E2E Attended/Unattended** | `pytest e2e/backend/test_e2e_attended_scraping.py e2e/backend/test_e2e_unattended_scraping.py` | Headed GUI vs headless Playwright runs | 10 / 10 passed (100%) | ✅ PASS |
| **Backend Ruff Linter** | `ruff check app tests ..\e2e\backend` | Code quality & static analysis | 0 errors | ✅ PASS |
| **Frontend TypeScript** | `npx tsc --noEmit` | Strict type validation | 0 errors | ✅ PASS |
| **Frontend Production Build** | `npm run build` | Next.js 14 App Router production bundle | 11/11 pages compiled | ✅ PASS |
| **PowerShell Scripts** | `powershell scripts\check_ps1_syntax.ps1` | All 10 workspace scripts AST syntax | 0 errors | ✅ PASS |

