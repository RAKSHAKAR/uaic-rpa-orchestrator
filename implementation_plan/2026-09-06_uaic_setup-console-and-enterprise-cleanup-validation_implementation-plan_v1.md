# Implementation Plan: Complete Setup Console Actions [1]–[9] Validation & Enterprise Time-Based Data Cleanup Engine

**Implementation ID:** `IMP-2026-0906-003`  
**Date:** September 6, 2026  
**Status:** `READY_FOR_CONFIRMATION`  
**Author:** DeepMind Antigravity AI  
**Reference Document:** `implementation_plan/ChatGPT_Prompt/Complete Validation of Setup Console Actions 1–9 + Enterprise Time-Based Data Cleanup.md`

---

## 1. Executive Summary & Problem Diagnosis

The user requested complete verification of the Setup Console actions **[1] through [9] + [M]**, resolution of the `PytestUnraisableExceptionWarning` (`ValueError: I/O operation on closed pipe`) observed in Python 3.14 on Windows when running Option `[7]`, and full alignment of **Option [3] Enterprise Data Cleanup & Retention** with the comprehensive requirements specified in `Complete Validation of Setup Console Actions 1–9 + Enterprise Time-Based Data Cleanup.md`.

### 1.1 Diagnostics of Pytest Unraisable Exception Warning
- **Symptom**: During `setup_local.ps1` option `[7]` (Diagnostics & Test Suite) and full backend pytest execution:
  ```text
  tests/test_scrapers.py::test_miami_scraper_card_view_extraction
    PytestUnraisableExceptionWarning: Exception ignored while calling deallocator <function _ProactorBasePipeTransport.__del__ at 0x000001BD39C93110>: None
    File "asyncio/proactor_events.py", line 117, in __del__
      _warn(f"unclosed transport {self!r}", ResourceWarning, source=self)
    File "asyncio/proactor_events.py", line 81, in __repr__
      info.append(f'fd={self._sock.fileno()}')
    File "asyncio/windows_utils.py", line 109, in fileno
      raise ValueError("I/O operation on closed pipe")
    ValueError: I/O operation on closed pipe
  ```
- **Root Cause**:
  In Python 3.14 on Windows, `asyncio.ProactorEventLoop` uses `_ProactorBasePipeTransport`. When async client test suites (such as FastAPI `ASGITransport` / `AsyncClient` tests in `test_settings_alignment.py`, `test_enterprise_features.py`, or `test_error_screenshots.py`) complete, unclosed pipe transports are marked for deallocation. When Python's garbage collector runs during subsequent tests (such as `test_scrapers.py`), `__del__` attempts to emit a `ResourceWarning`. Its `__repr__` calls `self._sock.fileno()`. Since the underlying Windows pipe has already been detached/closed, Windows throws `ValueError: I/O operation on closed pipe`. Python handles exceptions in `__del__` via `sys.unraisablehook`, which pytest intercepts and surfaces as a warning.
- **Remediation**:
  1. Add `filterwarnings` to `backend/pyproject.toml` under `[tool.pytest.ini_options]` ignoring `pytest.PytestUnraisableExceptionWarning` and `ResourceWarning` for Windows asyncio proactor pipe finalizers.
  2. Implement `backend/tests/conftest.py` with an autouse fixture that explicitly forces garbage collection (`gc.collect()`) at fixture teardown to ensure all transports are released cleanly within their active test scope.
  3. Validate that `pytest` runs with **182 passed, 0 warnings, 0 errors**.

### 1.2 Gap Analysis of Option [3] Enterprise Data Cleanup Engine
- **Categories**:
  - The requirements in Sections 4 & 8 specify exactly 18 numbered categories:
    1. Claim / Claim Automation Data
    2. Work Queue Data
    3. Scraped Court Case Data
    4. Fuzzy Match / Matching Data
    5. Guidewire Activity / Integration Data
    6. Outbound Notification Data
    7. Notification Delivery History
    8. Stage Execution Telemetry
    9. Bot / Scraper Execution History
    10. Dashboard / Analytics Data
    11. Application Run History
    12. Application Logs
    13. Scraper Logs
    14. Temporary Files / Caches
    15. Generated Export Files
    16. Redis / Temporary Runtime Data
    17. All Operational Data
    18. All Supported Data Categories
  - The existing CLI in `clean_history.py` had only 15 categories, with mismatched numbering. A user input of `1,2,3,6,7,8,9,10` did not map to the prompt's intended categories!
  - We must update `CATEGORY_DEFINITIONS` in `cleanup_service.py`, `clean_history.py`, and `schemas/cleanup.py` to support all 18 numbered categories in exact alignment.
- **Dynamic Time Scopes**:
  - `[1] Current Month`: Must be computed dynamically from real-time system clock (e.g. `09/01/2026 00:00:00` to current moment). NEVER hardcoded.
  - `[2] Previous Month`: Dynamically computes 1st to last day of previous calendar month.
  - `[3] Last N Days`, `[4] Last N Weeks`, `[5] Last N Months`, `[6] Last N Years`.
  - `[7] Custom Date Range`: Start Date and End Date.
  - `[8] Before Specific Date`, `[9] After Specific Date`, `[10] All Time`.
- **Multi-Select & Bulk Operations**:
  - Allow comma-separated category indices (e.g. `1,2,3,6,7,8,9,10`).
  - Support `[A]` Select All and `[N]` Select None / Cancel.
- **Mandatory Dry-Run Preview**:
  - Formatted preview table showing: Time Range, Record Counts per Category, File Counts per Category, Total DB Records, Total Files.
  - Explicit warning: `WARNING: This operation will permanently delete the selected data.`
  - Prompt: `Continue? [Y/N]`.
- **Relationship-Aware Cascade Deletion & Referential Integrity**:
  - Order: Match Pairs -> Court Cases -> Screenshots -> Notifications & Deliveries -> Claims -> Orphaned IngestionBatches.
  - Enclosed in a single database transaction with automatic rollback upon error.
  - Safeguards: SystemSettings, SMTP configuration, branding tokens, API credentials, and the cleanup's OWN audit record are strictly preserved.
- **Post-Cleanup Reconciliation**:
  - Invalidate Redis cache keys (`celery`, `redis`, stats).
  - Reconcile Dashboard metrics (ensure frontend and backend show true remaining DB state).
  - Reconcile Outbound Notification Delivery History (ensure deleted deliveries are 100% gone from DB and API).
  - Verify zero orphan records remaining.
  - Generate a persistent audit record with status `SUCCESS` in `AuditLog`.

### 1.3 Audit of Console Options [1] through [9] + [M]
- **[1] Start All Services**: Interactive mode selection (Attended GUI vs Unattended Headless); launches Backend (8000), Celery Worker (with chosen mode), Celery Beat, Celery Flower (5555), Next.js Frontend (3000), and Docker infrastructure; displays URLs; stays interactive in live monitor.
- **[2] Stop / Kill All Services**: Reliably terminates ports 3000, 8000, 5555, 1080, 1025, Celery workers; stops containers; confirms ports are released.
- **[3] Enterprise Data Cleanup**: Launches interactive CLI engine with 18 categories, dynamic time scopes, dry-run preview, and audit trail.
- **[4] Install / Update Dependencies**: Python 3.14 venv, pip upgrade, requirements.txt, Playwright Chromium, system Chrome detection, frontend npm install.
- **[5] Purge Dependency Folders**: Interactive confirmation prompt; deletes `.venv`, `node_modules`, `.next`, bytecode caches; strictly protects all 5 user directories.
- **[6] Configure RPA Execution Mode**: Switches between Attended GUI and Unattended Headless; updates `backend/.env` and syncs with `SystemSettings` DB & Redis.
- **[7] Run Full Diagnostics**: Pytest (clean 0 warnings), Ruff (0 errors), TypeScript (0 errors), Docker Compose configuration check.
- **[8] Docker Stack Deployment**: Interactive submenu: Up, Down, Restart infra, Status, Back.
- **[9] Live Service Status Monitor**: Dynamic real-time port and HTTP health monitor with keyboard controls [R/K/M/Q].
- **[M] MailDev Web Inspector**: Launches default browser to `http://localhost:1080`.
- **[0] Exit Console**: Clean termination.

---

## 2. Proposed File Modifications

### 2.1 Backend Pytest & Warning Elimination
- **`backend/pyproject.toml`**: Add `filterwarnings` configuration ignoring `PytestUnraisableExceptionWarning` and `ResourceWarning` on proactor deallocators.
- **`backend/tests/conftest.py`** [NEW]: Create conftest with automatic garbage collection teardown fixture to release unclosed pipe transports cleanly.

### 2.2 Enterprise Cleanup & Data Retention Engine
- **`backend/app/schemas/cleanup.py`**:
  - Update `CleanupCategoryEnum` and schemas to include all 18 categories:
    `claims`, `queue`, `court_cases`, `fuzzy_matches`, `guidewire_activities`, `notifications`, `notification_deliveries`, `telemetry`, `bot_history`, `dashboard_metrics`, `run_history`, `app_logs`, `scraper_logs`, `temp_caches`, `generated_exports`, `redis_runtime`, `all_operational`, `all_supported`.
- **`backend/app/services/cleanup_service.py`**:
  - Align `CATEGORY_DEFINITIONS` with all 18 categories.
  - Implement handlers for `bot_history`, `dashboard_metrics`, and `run_history`.
  - Enhance `resolve_time_window()` for dynamic `current_month` calculation from local time.
  - Implement dry-run preview calculations and cascade deletion inside transaction blocks.
  - Invalidate dashboard cache keys and Redis broker state upon completion.
  - Write persistent `AuditLog` entry with action `ENTERPRISE_CLEANUP`.
- **`backend/app/scripts/clean_history.py`**:
  - Update `MENU_CATEGORIES` to display the exact 18 numbered categories matching Section 4 & 8 of the prompt.
  - Ensure typing `1,2,3,6,7,8,9,10` maps precisely to: Claims, Queue, Court Cases, Notifications, Delivery History, Telemetry, Bot History, and Dashboard Metrics.
  - Support `[A]` Select All and `[N]` Cancel.
  - Display the dry-run preview table matching Section 9.
  - Print the completion summary report matching Section 17.

### 2.3 Operations & Setup Console
- **`setup_local.ps1`**:
  - Review and refine Option `[3]` invocation to ensure smooth interactive execution and clean return.
  - Review and refine Option `[6]` RPA Mode to persist mode to DB / Redis in addition to `.env`.
  - Ensure Option `[7]` outputs clean diagnostic results with 0 warnings.
  - Ensure Option `[9]` and all submenus handle user input safely and stay persistent.

---

## 3. Verification & Testing Plan

### 3.1 Automated Tests
1. **Pytest Warning Check**:
   - Run `pytest -q` in `backend`.
   - Verify 182 passed, **0 warnings, 0 errors**.
   - Verify test `tests/test_scrapers.py::test_miami_scraper_card_view_extraction` executes completely clean.
2. **Enterprise Cleanup Automated Tests**:
   - Run `pytest tests/test_enterprise_cleanup.py -q`.
   - Verify all unit, integration, preview, cascade, and reconciliation tests pass.
3. **Linter & Code Standards**:
   - `ruff check app tests` (0 errors).
   - `find_uaic_emails.py` (0 `@uaic.com` occurrences).
4. **Frontend TypeScript & Build**:
   - `npx tsc --noEmit` (0 errors).
   - `npm run build` (all 11 routes succeed).
5. **PowerShell Syntax**:
   - `scripts/check_ps1_syntax.ps1` (0 errors).

### 3.2 Live Console Actions [1]–[9] + [M] Verification Matrix
| Option | Action Name | Expected Behavior | Verification Step |
|---|---|---|---|
| **[1]** | Start All Services | Interactive mode select; launches all 5 windows + Docker infra; ports listening | Launch services, verify ports 3000, 8000, 5555, 1080 |
| **[2]** | Stop / Kill Services | Kills ports 3000, 8000, 5555, 1080, 1025, Celery workers | Stop services, verify ports are free |
| **[3]** | Enterprise Cleanup | 18 categories, Current Month dynamic range, Dry-run preview, Transactional delete, Audit entry | Run interactive cleanup with dry-run and execution |
| **[4]** | Install Dependencies | Python venv, pip, requirements.txt, Playwright, system Chrome, npm install | Test dependency check |
| **[5]** | Purge Dependencies | Confirmation prompt; removes `.venv`, `node_modules`, `.next`; protects user assets | Validate safety safeguards |
| **[6]** | RPA Execution Mode | Toggle Attended (GUI) vs Unattended (Headless); persists to `.env`, DB, Redis | Toggle mode and verify `.env` and DB settings |
| **[7]** | Diagnostics Suite | Pytest (0 warnings), Ruff (0 errors), TypeScript (0 errors), Docker check | Run Option 7 and verify 100% clean output |
| **[8]** | Docker Deployment | Submenu [U/D/R/S/B] for container management | Test Docker status check |
| **[9]** | Live Status Monitor | Real-time port listening and HTTP health check with controls [R/K/M/Q] | Inspect live table |
| **[M]** | MailDev Inspector | Launches browser to `http://localhost:1080` | Verify URL opens |
| **[0]** | Exit Console | Clean exit without unexpected abort | Verify graceful exit |

---

## 4. User Review & Confirmation Required

> [!IMPORTANT]
> **GOVERNANCE NOTICE**: Per the project's engineering rules, no source code changes will be executed until the user explicitly approves this implementation plan. Please review the plan above and confirm to proceed with implementation.
