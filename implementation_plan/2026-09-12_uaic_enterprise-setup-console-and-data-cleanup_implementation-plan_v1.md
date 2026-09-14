# Implementation Plan: Enterprise Setup Console (Options 1-9) & Data Cleanup Engine

**Implementation ID:** IMP-2026-0912-004  
**Module:** DevOps / Setup Console & Enterprise Data Retention Service  
**Date:** 2026-09-12  
**Status:** Complete  
**Approval Status:** Approved  
**Approved By:** User  
**Approval Date:** 2026-09-12  
**Target Runtime:** Python 3.14.7 + Next.js 14 + PowerShell AST  
**Author:** Antigravity (Advanced AI Coding Assistant)

---

## 1. Executive Summary & Problem Statement

The user has requested auditing, upgrading, and finalizing the **Enterprise Setup Console (Options 1–9 + [M] MailDev)** and transforming **Option [3]** into a complete enterprise data-retention and cleanup engine:
1. **Setup Console Architecture (Options 1–9 + [M]):** Ensure all console operations perform real, robust process lifecycle management rather than blind terminal launches.
   - **[1] Start All Services:** Interactive launch with Attended (GUI) vs Unattended (Headless) mode selection; pre-flight port conflict checking and auto-resolution; Docker infrastructure initialization (PostgreSQL, Redis, MailDev).
   - **[2] Stop / Kill All Services:** Safely terminate Ports 3000, 8000, 5555, 6379, 5432, Celery workers/beat/flower, and **MUST explicitly terminate MailDev (Ports 1080 and 1025)** with port release verification.
   - **[4] Install Dependencies:** Support Python 3.14.7, Node, and Playwright. **CRITICAL:** Do NOT install bundled Playwright Chromium if system Google Chrome (or Edge) is selected for RPA. When Chromium is selected, check whether bundled Chromium is already installed; if missing, show complete instructions and install it. If system Chrome is selected, provide full instructions on how to test in Chromium if desired.
   - **[5] Purge Folders:** Safely delete `.venv`, `node_modules`, `.next`, `.turbo`, `.pytest_cache`, `.ruff_cache`, and `__pycache__` while guaranteeing that the 5 protected user directories (`implementation_plan`, `PowerAutomateSolutions`, `Testing files`, `anticaptcha-plugin_v0.83`, `.agents`), source code, and credentials are never touched.
   - **[6] RPA Mode:** Toggle Attended (GUI) vs Unattended (Headless), persisting to `.env` (`PLAYWRIGHT_HEADLESS`) and database `SystemSettings.automation.headless_mode`. Dynamically display the active RPA mode in the console banner header.
   - **[7] Diagnostics:** Run Pytest (all test suites), Ruff, TypeScript, Docker Compose, and PowerShell AST syntax. Root-cause resolution of `PytestUnraisableExceptionWarning` via proactive event loop transport garbage collection in `conftest.py` with zero warnings suppressed in `pyproject.toml`.
   - **[8] Docker:** Safe containerized stack management (Start Infra, Stop Infra, Start Full Stack, Clean Reset, Container Status).
   - **[9] Live Monitor:** Real health checks (HTTP probes, TCP probes, Redis PING, SMTP Banner) for Frontend, Backend, Redis, Celery Worker PID, Celery Beat PID, Flower, and MailDev.
   - **[M] MailDev:** Probe HTTP (1080) and SMTP (1025); report health; open localhost:1080 if available or provide instructions to start if offline.

2. **Enterprise Data Cleanup & Retention (Option [3]):**
   - **Categories:** Multi-select across all 18 operational categories (Claims, Queue, Court Cases, Fuzzy Matches, Guidewire Activities, Notifications, Notification Deliveries, Telemetry, Bot History, Dashboard Metrics, Run History, App Logs, Scraper Logs, Temp Caches, Generated Exports, Redis Runtime, All Operational, All Supported).
   - **Time Scope:** Support Days, Weeks, Months, Years, Custom Range, Before Date, After Date, and dynamic **Current Month**, Previous Month, Current Quarter, Previous Quarter, and Current Year.
   - **Safety:** Mandatory Dry-Run preview; explicit confirmation before deletion; transactional rollback with database backup before mutation.
   - **Reconciliation & Referential Integrity:** Fix the identified gap where standalone notifications (e.g. test emails or system alerts without `claim_id`) were skipped during cleanup, and ensure cascade deletion of all child records (`Notification`, `MatchPair`, `ScrapedCourtCase`, `FilteredOutCase`, `ErrorScreenshot`, `GuidewireActivity`) when parent `ClaimRecord` items are deleted. Systematic cache invalidation for Redis queues and Dashboard metrics (`cache:*`, `metrics:*`, `stats:*`, `dashboard:*`).

---

## 2. Root Cause Analysis of Existing Gaps

1. **Cleanup Referential Integrity & Standalone Records Gap:**
   - In `backend/app/services/cleanup_service.py`, when claims were selected (`target_claim_ids` populated), queries for child tables used `where(T.claim_id.in_(target_claim_ids))`. If a notification or court case was created in the time window but had `claim_id=None` (e.g. Test Email, system alerts) or belonged to a claim created in a different month, it was skipped!
   - Conversely, when `claims` was selected but child categories were not in `cats`, `calculate_cleanup_preview` did not count the cascaded child records, causing a mismatch between preview and actual deletion counts.
2. **Browser Engine Matrix Transparency in Option [4]:**
   - In `setup_local.ps1`, when `CurrentChannel` was `chromium`, it unconditionally executed `& $pyExe -m playwright install chromium` even if bundled Chromium was already present on disk in `%LOCALAPPDATA%\ms-playwright`.
   - When Google Chrome was selected, instructions on how to manually install/test bundled Chromium if desired were not presented clearly to the user.
3. **Active RPA Mode Banner & Celery Beat in Live Monitor:**
   - The interactive menu header in `setup_local.ps1` displayed a static banner without reflecting the dynamically loaded active RPA mode from `.env` / database.
   - `Show-LiveStatusMonitor` monitored the Celery Worker process PID, but omitted Celery Beat Scheduler process detection.
4. **Option [M] MailDev Handling:**
   - If MailDev was offline, Option [M] reported OFFLINE but proceeded to open the browser to `localhost:1080`, resulting in a browser connection error. It should offer to start the container or provide instructions before launching.

---

## 3. Detailed Implementation Tasks

### Component 1: Enterprise Data Cleanup Service (`backend/app/services/cleanup_service.py` & `clean_history.py`)
- [MODIFY] `backend/app/services/cleanup_service.py`:
  - Update `calculate_cleanup_preview` and `execute_enterprise_cleanup` to handle both direct category selection AND cascade relationships:
    - For `Notification`: If `notifications` in `cats`, delete all notifications in the time window OR with `claim_id.in_(target_claim_ids)`. If only `notification_deliveries` in `cats`, delete sent/failed notifications in the time window OR with `claim_id.in_(target_claim_ids)`. If neither in `cats` but `claims` is selected, cascade delete notifications with `claim_id.in_(target_claim_ids)`.
    - For `ScrapedCourtCase` & `FilteredOutCase`: If `court_cases` in `cats`, delete cases in the time window OR with `claim_id.in_(target_claim_ids)`. If not in `cats` but `claims` selected, cascade delete.
    - For `MatchPair`: If `fuzzy_matches` in `cats`, delete matches in the time window OR with `claim_id.in_(target_claim_ids)`. If not in `cats` but `claims` selected, cascade delete.
    - For `ErrorScreenshot`: If `bot_history` in `cats`, delete screenshots in the time window OR with `claim_id.in_(target_claim_ids)`. If not in `cats` but `claims` selected, cascade delete.
    - For `GuidewireActivity`: If `guidewire_activities` in `cats`, delete activities in the time window OR with `claim_id.in_(target_claim_ids)`. If not in `cats` but `claims` selected, cascade delete.
  - Update `calculate_cleanup_preview` to use identical filtering logic so preview counts and actual deleted counts match 100%.
  - Post-cleanup cache invalidation: Guarantee Redis key purging (`cache:*`, `metrics:*`, `stats:*`, `dashboard:*`) and Celery queue flushdb.
- [MODIFY] `backend/app/scripts/clean_history.py`:
  - Enhance interactive prompts with complete instructions, category listing, multi-select parsing (numbers and keys), time scope options, dry-run display, and explicit confirmation.

### Component 2: Setup Console (`setup_local.ps1`)
- [MODIFY] `setup_local.ps1`:
  - **Banner:** Dynamically query active RPA mode from `.env` (`PLAYWRIGHT_HEADLESS`) and display `Active RPA Engine Mode: [Attended (GUI)]` or `[Unattended (Headless)]` in `Show-EnterpriseMenu`.
  - **Option [1]:** Verify pre-flight port conflicts with interactive conflict resolution; ensure mode propagates to worker window title and backend environment.
  - **Option [2]:** Stop all services and explicitly terminate MailDev (Ports 1080 and 1025) across Docker container (`uaic_maildev`) and local processes (`node.exe`, `maildev.exe`). Verify port release with clean status report. Ensure idempotency when services are already stopped.
  - **Option [4]:**
    - When system Google Chrome (or Edge) is selected: Skip bundled Chromium download (0MB overhead); display clear instructions: `"Note: Host Google Chrome is active. Bundled Chromium download skipped. To test in Chromium: Select Chromium in Settings or run: .venv\Scripts\python -m playwright install chromium"`.
    - When Chromium is selected: Inspect `$browsers.BundledChromiumInstalled`. If already installed, report path and verify without downloading; if missing, display instructions and install it cleanly.
  - **Option [6]:** Ensure RPA mode toggle synchronizes `.env` and `save_system_settings_async`.
  - **Option [7]:** Run Pytest, Ruff, TypeScript, Docker Compose, and PowerShell syntax validation with zero suppressed warnings.
  - **Option [9]:** Add Celery Beat Scheduler process detection alongside Celery Worker PID in `Show-LiveStatusMonitor`.
  - **Option [M]:** Probe HTTP (1080) and SMTP (1025); if healthy, open browser; if offline, display status and offer to start Docker infrastructure before launching browser.

### Component 3: Test Suite (`backend/tests/`)
- [MODIFY] `backend/tests/test_enterprise_cleanup.py`:
  - Add test for standalone notification cleanup (notifications with `claim_id=None`).
  - Add test for cascade deletion of child notifications, cases, matches, and screenshots when parent claim is deleted.
  - Add test verifying that preview counts and execution counts match 100%.
- [MODIFY] `backend/tests/test_setup_console.py`:
  - Add test validating Celery Beat process detection logic.
  - Add test verifying MailDev explicit termination and port verification logic.
  - Add test verifying Chromium conditional installation logic and instruction formatting.

### Component 4: Documentation Synchronization
- [MODIFY] `README.md`:
  - Update Setup Console documentation detailing Options 1–9, MailDev integration, dynamic RPA mode switching, and the Enterprise Data Cleanup & Retention engine.

---

## 4. Verification Plan

### Automated Tests
1. **Backend Test Suite (Pytest):**
   ```bash
   cd backend
   .venv\Scripts\pytest -ra -q --asyncio-mode=auto
   ```
   *Expected:* 100% pass (282+ tests, 0 failures, 0 `PytestUnraisableExceptionWarning`).
2. **Backend Code Quality Linter (Ruff):**
   ```bash
   .venv\Scripts\ruff check app tests
   ```
   *Expected:* 0 errors.
3. **Frontend TypeScript Compilation:**
   ```bash
   cd frontend
   npx tsc --noEmit
   ```
   *Expected:* 0 errors.
4. **PowerShell AST Syntax Validation:**
   ```bash
   powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"
   ```
   *Expected:* 0 errors across all `.ps1` scripts.
5. **Docker Compose Configuration Validation:**
   ```bash
   docker compose config --quiet
   ```
   *Expected:* Code 0 (valid YAML and schemas).

### Interactive / Integration Checks
1. Execute `clean_history.py --dry-run` to verify preview generation.
2. Run standalone and cascade deletion scenarios and verify zero orphan records.
3. Test `setup_local.ps1` with `-CheckPorts`, `-Status`, and `-RunTests` switches.

---
**Execution Status:** Complete (100% Automated Testing Suite)  
**Related Documents:**  
- Walkthrough: [2026-09-12_uaic_enterprise-setup-console-and-data-cleanup_walkthrough_v1.md](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/implementation_plan/2026-09-12_uaic_enterprise-setup-console-and-data-cleanup_walkthrough_v1.md)  
- Implementation Record: [2026-09-12_uaic_enterprise-setup-console-and-data-cleanup_implementation-record_v1.md](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/implementation_plan/2026-09-12_uaic_enterprise-setup-console-and-data-cleanup_implementation-record_v1.md)  
- Plan Document: `implementation_plan/2026-09-12_uaic_enterprise-setup-console-and-data-cleanup_implementation-plan_v1.md`  
**AI Verification:** Complete (100% Automated Testing Suite)
