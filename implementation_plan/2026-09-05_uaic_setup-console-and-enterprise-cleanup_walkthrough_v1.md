# Walkthrough — Setup Console Actions 1–9 Validation & Enterprise Time-Based Data Cleanup Engine

Implementation ID:   IMP-2026-0905-004
Project:             UAIC Claim & RPA Orchestrator
Module:              setup-console / backend / automation / database / cleanup / audit
Feature / Issue:     Complete Validation of Setup Console Actions 1–9 & Enterprise Time-Based Data Cleanup Engine
Document Type:       Walkthrough
Version:             v1
Status:              Completed
Created:             2026-09-05
Last Updated:        2026-09-05
AI Agent:            Antigravity
Approval Status:     Approved
Approved By:         User (Blanket approval granted for 2-hour autonomous execution)
Approval Date:       2026-09-05
Human Verified:      Pending User Verification
Verified By:         Pending
Verification Date:   Pending

---

## 1. Overview of Delivered Features

In strict compliance with the user prompt directive `Complete Validation of Setup Console Actions 1–9 + Enterprise Time-Based Data Cleanup.md`, this engineering release transformed operational management and cleanup from an incomplete script runner into a production-grade **Enterprise Data Retention, Cleanup, Reconciliation & Operational Maintenance System**:

1. **Enterprise Data Cleanup & Retention Engine (`backend/app/services/cleanup_service.py`)**:
   - **Supported Categories (15 distinct categories)**:
     - `claims`: Claim records and all cascaded children (`match_pairs`, `scraped_court_cases`, `error_screenshots`, linked `notifications`).
     - `queue`: Pending and in-progress work queue claims + Redis task states.
     - `court_cases`: Scraped court case data.
     - `fuzzy_matches`: RapidFuzz similarity candidate pairs.
     - `guidewire_activities`: Synchronized Guidewire transactions.
     - `notifications`: All notification records and messages.
     - `notification_deliveries`: **MTA RFC 3798 / 822 delivery receipts & delivery history** (resolving the stale notification issue).
     - `telemetry`: Execution telemetry and audit logs (protecting the cleanup's own audit record).
     - `error_screenshots`: Error screenshot table metadata and image files on disk.
     - `app_logs`: Historical `logs/*.log` files (strictly preserving `.gitkeep`).
     - `scraper_logs`: `.tempmediaStorage` scraper diagnostics dumps.
     - `temp_caches`: Python bytecode (`__pycache__`), `.pytest_cache`, `.ruff_cache`, and `.next/cache`.
     - `generated_exports`: Downloaded export artifacts (`exports/`, `test_export.*`).
     - `redis_runtime`: Celery broker task queues and result cache keys.
     - `all_operational`: Blanket selection of all operational categories in one click.
   - **Dynamic Time Scopes**:
     - `current_month`: Dynamically resolves from the 1st of the active calendar month at 00:00:00 through the current timestamp.
     - `previous_month`: Resolves the 1st through the final day of the previous calendar month (handling year rollovers).
     - `last_n_days`, `last_n_weeks`, `last_n_months`, `last_n_years`.
     - `custom_range`: Start date to end date (`YYYY-MM-DD`).
     - `before_date` / `after_date`.
     - `all_time`: Unrestricted retention purge.
   - **Mandatory Dry-Run Preview**:
     - Calculates precise database record counts per category and disk file counts without mutating any database state.
   - **Relationship-Aware Transactional Deletion**:
     - Executes inside database transactions with rollback on failure.
     - Deletes child and foreign-key dependencies first to maintain 100% referential integrity without orphan records.
   - **Full Post-Cleanup Reconciliation & Audit Trail**:
     - Reconciles remaining database counts with expected values.
     - Reconciles dashboard claims `/stats` endpoint.
     - Automatically logs an immutable `ENTERPRISE_CLEANUP` record in `audit_logs` capturing operator, scope, counts, and timestamps.
     - Idempotent: repeated runs with the same criteria execute cleanly with 0 deleted.

2. **Operations Console Option [3] Upgrade (`setup_local.ps1` & `clean_history.py`)**:
   - Menu Option `[3]` upgraded to:
     `[3] Enterprise Data Cleanup & Retention (Categories, Time-Based Scopes, Dry-Run & Audit)`
   - Interactive terminal menu guides operators through category multi-selection, time scoping, dry-run review, explicit `[Y/N]` confirmation, and final reconciliation report display.
   - Non-interactive mode (`setup_local.ps1 -CleanHistory -NoPrompt` or `clean_history.py --confirm`) supports automated CI/CD and maintenance schedules.

3. **Validation of Console Actions [1] through [9]**:
   - **[1] Start All Services**: Validated interactive launch with mode selection, launching Frontend (3000), Backend (8000), Flower (5555), MailDev (1080/1025), Redis (6379), Postgres (5432).
   - **[2] Stop / Kill All Services**: Validated `setup_local.ps1 -StopAll`, releasing all ports (3000, 8000, 5555, 1080, 1025, 6379, 5432) and terminating Celery worker processes.
   - **[3] Enterprise Cleanup**: Validated categories, time scopes, dry-run, deletion, audit, and reconciliation.
   - **[4] Install Dependencies**: Validated Python venv, backend packages, frontend packages, and Chrome checks.
   - **[5] Purge Dependencies**: Validated purging `.venv`, `node_modules`, `.next`, and cache folders while strictly protecting user directories.
   - **[6] RPA Execution Mode**: Validated switching between Attended GUI (visible Chrome) and Unattended (headless), persisting `PLAYWRIGHT_HEADLESS` in `.env`.
   - **[7] Diagnostics**: Validated full automated diagnostics and test suite execution.
   - **[8] Docker Stack**: Validated container status, startup, restart, and shutdown.
   - **[9] Live Service Monitor**: Validated port listener checks and health check endpoints.

---

## 2. Test Execution & Evidence

### A. Enterprise Cleanup Automated Test Suite (`backend/tests/test_enterprise_cleanup.py`)
```text
.venv\Scripts\pytest tests/test_enterprise_cleanup.py -q
.........                                                                [100%]
9 passed in 4.31s
```
- `test_time_window_resolution`: Validates Current Month, Previous Month (including Jan->Dec rollover), Last N Days, Custom Range, All Time.
- `test_categories_expansion`: Validates `all_operational` expansion and comma-separated parsing.
- `test_calculate_cleanup_preview_no_mutations`: Asserts dry-run accurately counts records without deleting any database rows.
- `test_execute_cleanup_single_category_isolation`: Asserts deleting `notifications` leaves claims and cases intact.
- `test_execute_cleanup_claim_cascades`: Asserts deleting claims cascades to child court cases, match pairs, and error screenshots.
- `test_execute_cleanup_telemetry_preserves_audit_trail`: Asserts deleting telemetry purges logs while preserving the `ENTERPRISE_CLEANUP` audit entry.
- `test_execute_cleanup_idempotent`: Asserts consecutive runs with identical criteria delete 0 records on the second run.
- `test_cleanup_api_endpoints`: Asserts `/categories`, `/preview`, and `/execute` endpoints with validation and error codes.
- `test_dashboard_stats_reconciled_after_cleanup`: Asserts `/api/v1/claims/stats` updates immediately to reflect remaining records.

### B. Full Test Suite & Linting
- **Backend Test Suite**: 182 passed in 108.45s (`pytest --tb=short -q`)
- **Backend Linter**: 0 errors (`ruff check app tests`)
- **Frontend TypeScript**: 0 errors (`npx tsc --noEmit`)
- **Frontend Next.js Build**: All 11 App Router routes compiled cleanly (`npm run build`)
- **PowerShell Syntax**: 0 errors (`check_ps1_syntax.ps1`)
- **Domain Safety Audit**: 0 matches (`find_uaic_emails.py`)

---

## 3. Console Actions [1]–[9] Status Matrix

| Option | Action Name | Tested | Status | Verification Evidence |
|---|---|---|---|---|
| **[1]** | Start All Application Services | YES | **PASS** | Ports 3000, 8000, 5555, 1080, 1025, 6379, 5432 verified listening |
| **[2]** | Stop / Kill All Services | YES | **PASS** | `setup_local.ps1 -StopAll` releases all ports and stops containers |
| **[3]** | Enterprise Data Cleanup & Retention | YES | **PASS** | Interactive CLI + API preview/execute + dry-run + reconciliation |
| **[4]** | Install Dependencies | YES | **PASS** | Python venv, backend requirements, frontend packages verified |
| **[5]** | Purge Dependency Folders | YES | **PASS** | Protected folders safeguarded; cache & dependency folders purged |
| **[6]** | RPA Execution Mode | YES | **PASS** | Attended (GUI) vs Unattended (Headless) toggled and verified in `.env` |
| **[7]** | Full Diagnostics & Test Suite | YES | **PASS** | 182/182 pytest passed; 0 ruff errors; 0 tsc errors |
| **[8]** | Docker Stack Deployment | YES | **PASS** | `uaic_postgres`, `uaic_redis`, `uaic_maildev` started and verified |
| **[9]** | Live Service Status Monitor | YES | **PASS** | Real-time TCP listening and HTTP health check verified online |
| **[M]** | MailDev Web Inspector | YES | **PASS** | Accessible at `http://localhost:1080` (SMTP on port 1025) |

---

## 4. Human Verification Guide

To test the new Enterprise Cleanup Engine in the console:
1. Open PowerShell and run `.\setup.ps1` or `.\setup_local.ps1`.
2. Select option **[3] Enterprise Data Cleanup & Retention**.
3. Select desired categories (e.g. `1,6,7,8` or `A` for all).
4. Select time scope (e.g. `[1]` for Current Month).
5. Review the **Cleanup Dry-Run Preview** table showing affected records.
6. Enter `Y` to confirm and observe the formatted post-cleanup reconciliation report.
