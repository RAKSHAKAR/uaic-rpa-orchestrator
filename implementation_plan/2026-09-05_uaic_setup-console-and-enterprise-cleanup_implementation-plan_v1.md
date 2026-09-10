# Implementation Plan — Complete Validation of Setup Console Actions 1–9 + Enterprise Time-Based Data Cleanup

Implementation ID:   IMP-2026-0905-004
Project:             UAIC Claim & RPA Orchestrator
Module:              setup-console / backend / automation / database / cleanup / audit
Feature / Issue:     Complete Validation of Setup Console Actions 1–9 & Enterprise Time-Based Data Cleanup Engine
Document Type:       Implementation Plan
Version:             v1
Status:              Approved (User blanket approval granted for 2-hour autonomous execution)
Created:             2026-09-05
Last Updated:        2026-09-05
AI Agent:            Antigravity
Approval Status:     Approved
Approved By:         User
Approval Date:       2026-09-05
Human Verified:      Pending User Verification
Verified By:         Pending
Verification Date:   Pending

---

## 1. Problem Statement & Operational Objective

Direct system inspection and the user directive `Complete Validation of Setup Console Actions 1–9 + Enterprise Time-Based Data Cleanup.md` identified critical gaps in operational data management and console orchestration:

1. **Incomplete Cleanup Operations**:
   - `clean_history.py` and `POST /api/v1/claims/clean` only wiped `match_pairs`, `scraped_court_cases`, `claim_records`, and `ingestion_batches`.
   - **Outbound Notification Delivery History** (`notifications` table) was never deleted, leaving stale delivery receipts and message logs.
   - Audit logs (`audit_logs`), error screenshots (`error_screenshots`), log files, and export files remained orphaned or unmanaged.
   - No category multi-selection existed; cleanup was an unconfigurable all-or-nothing wipe.
   - No time-based scoping existed; users could not purge data for the **Current Month**, Previous Month, or specific date windows.
   - No dry-run preview or confirmation step was presented to operators before deletion.
   - No reconciliation was performed to verify that dependent records, dashboard aggregations, and query caches were properly aligned.

2. **Setup Console Actions 1–9 Production-Grade Validation**:
   - Option [3] in `setup_local.ps1` must be upgraded from a basic script runner into an **Enterprise Data Cleanup & Retention Engine**.
   - Every console action `[1]` through `[9]` must be systematically audited, hardened, tested in realistic combination scenarios (e.g. Stop -> Start -> Monitor -> Diagnostics, Purge -> Install -> Test, Attended vs. Unattended mode switches), and verified end-to-end.

---

## 2. Technical Architecture & Component Design

### A. Enterprise Cleanup Service (`backend/app/services/cleanup_service.py`)
A unified, transactional, relationship-aware cleanup service:
1. **Data Categories**:
   - `claims`: `claim_records` + cascade to `match_pairs`, `scraped_court_cases`, `error_screenshots`, linked `notifications`.
   - `queue`: Claims with status `NEW`, `SCRAPING_IN_PROGRESS`, `INGESTION_PENDING` + Redis queues.
   - `court_cases`: `scraped_court_cases` + cascade to `match_pairs`.
   - `fuzzy_matches`: `match_pairs`.
   - `guidewire_activities`: Claims with `activity_id IS NOT NULL`.
   - `notifications`: All `notifications` table records.
   - `notification_deliveries`: `notifications` with status `SENT`/`FAILED` or delivery receipts.
   - `telemetry`: `audit_logs` (protecting the cleanup's own audit log).
   - `error_screenshots`: `error_screenshots` table and associated screenshot files.
   - `app_logs`: `logs/setup_*.log` and `logs/*.log` (protecting `.gitkeep`).
   - `scraper_logs`: Temporary scraper artifacts/logs.
   - `temp_caches`: Bytecode, pytest cache, ruff cache, next cache, temporary media storage.
   - `generated_exports`: Export files (`exports/`, `test_export.*`, `scratch_test_*`).
   - `redis_runtime`: Flush Redis task queues and result keys.
   - `all_operational`: Blanket selection of all operational categories.
2. **Time Scopes**:
   - `current_month`: Dynamic start of month (e.g. `2026-09-01 00:00:00`) to current execution timestamp.
   - `previous_month`: 1st day 00:00:00 to last day 23:59:59 of previous calendar month.
   - `last_n_days`, `last_n_weeks`, `last_n_months`, `last_n_years`.
   - `custom_range`: User-defined `start_date` to `end_date`.
   - `before_date` / `after_date`.
   - `all_time`: No time restriction.
3. **Dry-Run Preview**:
   - Calculates record counts and file counts without mutating database state.
4. **Relationship-Aware Transactional Execution**:
   - Deletes leaf/dependent records first to preserve referential integrity.
   - Executes inside `session.begin()` transaction with automatic rollback on error.
   - Records an immutable audit log entry for the cleanup itself in `audit_logs`.
   - Invalidates Redis caches and reconciles dashboard stats.

### B. Interactive Python CLI (`backend/app/scripts/clean_history.py`)
- Upgraded with rich interactive terminal menus and CLI parameter flags (`--categories`, `--time-scope`, `--dry-run`, `--confirm`).
- Formats and displays the Dry-Run Preview table, prompts for explicit `[Y/N]` confirmation, executes the cleanup, and prints the full post-execution reconciliation report.

### C. Operations Console (`setup_local.ps1`)
- Renames Option [3] to:
  `[3] Enterprise Data Cleanup & Retention (Categories, Time-Based Scopes, Dry-Run & Audit)`
- Updates `Invoke-CleanRunHistory` to invoke the interactive Enterprise Cleanup Engine.
- Validates and hardens Actions `[1]` through `[9]` across both Attended GUI and Unattended Headless modes.

### D. REST API Endpoints (`backend/app/api/v1/endpoints/cleanup.py`)
- `GET /api/v1/cleanup/categories`: List categories and current record counts.
- `POST /api/v1/cleanup/preview`: Dry-run preview calculation.
- `POST /api/v1/cleanup/execute`: Perform enterprise cleanup with audit logging and reconciliation report.
- `POST /api/v1/claims/clean`: Delegated to the unified cleanup engine for backwards compatibility.

---

## 3. Implementation Steps

1. **Step 1: Backend Cleanup Service** (`backend/app/services/cleanup_service.py`):
   - Implement category registry, time scope calculators, dry-run preview, and transactional execution.
2. **Step 2: API Endpoints & Schemas** (`backend/app/schemas/cleanup.py`, `backend/app/api/v1/endpoints/cleanup.py`):
   - Add Pydantic schemas and FastAPI router endpoints; register router in `backend/app/main.py`.
   - Wire `claims.py` clean endpoint into `cleanup_service`.
3. **Step 3: CLI Script Enhancement** (`backend/app/scripts/clean_history.py`):
   - Build interactive terminal menu with multi-select categories, time scopes, dry-run preview, confirmation, and reconciliation report.
   - Support CLI arguments for automated testing.
4. **Step 4: Operations Console Hardening** (`setup_local.ps1`):
   - Update menu Option [3] and `Invoke-CleanRunHistory`.
   - Verify actions [1], [2], [4], [5], [6], [7], [8], [9].
5. **Step 5: Automated Testing**:
   - Write comprehensive test suite `backend/tests/test_enterprise_cleanup.py` (unit, integration, dry-run, time-scoping, cascade deletion, reconciliation).
6. **Step 6: Quality Gates & Verification**:
   - Run full `pytest` suite.
   - Run `ruff check app tests`.
   - Run `npx tsc --noEmit` and `npm run build`.
   - Run `check_ps1_syntax.ps1`.
   - Run `find_uaic_emails.py`.
7. **Step 7: Documentation & Audit**:
   - Write walkthrough and implementation record in `implementation_plan/`.

---

## 4. Verification Plan

| Test Case | Description | Verification Method |
|---|---|---|
| **C01** | Dry-run preview calculation | Test asserts 0 database deletions occur during dry-run |
| **C02** | Current Month dynamic calculation | Test asserts start of month 00:00:00 to now |
| **C03** | Notification history cleanup | Verifies `notifications` and delivery receipts are actually removed |
| **C04** | Cascade relationship deletion | Verifies deleting claims purges linked cases, match pairs, screenshots |
| **C05** | Telemetry cleanup with audit preservation | Verifies audit logs cleaned while the cleanup log itself is saved |
| **C06** | Dashboard reconciliation | Verifies claim stats endpoint reflects exact remaining count |
| **C07** | Idempotency | Running identical cleanup twice returns 0 deleted on second run |
| **C08** | Console Actions [1]-[9] | Script syntax, process management, diagnostics, and monitoring verified |
