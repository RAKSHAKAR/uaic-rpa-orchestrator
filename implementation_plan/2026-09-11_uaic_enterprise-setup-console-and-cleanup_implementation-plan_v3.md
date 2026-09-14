# Implementation Plan

**Implementation ID:**   IMP-2026-0911-007  
**Project:**             UAIC Claim & RPA Orchestrator  
**Module:**              Enterprise Setup Console (Options 1–9, [M]), Real Process Management, Data Cleanup Engine  
**Feature / Issue:**     Prompt 02 — Enterprise Setup Console (Options 1–9) & Enterprise Time-Based Data Cleanup  
**Document Type:**       Implementation Plan  
**Version:**             v3  
**Status:**              Complete  
**Created:**             2026-09-11  
**AI Agent:**            Antigravity (Advanced Agentic Coding)  
**Approval Status:**     Approved  
**Approved By:**         User  
**Approval Date:**       2026-09-11  
**AI Verification:**     Complete (100% Automated Testing Suite)  

---

## 1. Problem & Executive Summary

The user has submitted Milestone **02 - ENTERPRISE SETUP CONSOLE (OPTIONS 1-9) & DATA CLEANUP** with two primary core pillars:
1. **Console Architecture & Process Management**:
   - Audit and finalize PowerShell and Python setup console scripts (`setup_local.ps1`, `setup.ps1`, and supporting scripts) to ensure all options operate on real process management (e.g., supporting `setup-local.ps1` and `setup_local.ps1` interchangeably).
   - **[1] Start All Services:** Support Interactive Launch (Attended GUI vs Unattended Headless). Check port conflicts before starting.
   - **[2] Stop All Services:** Safely terminate Ports 3000, 8000, 5555, 6379, 5432, Celery, and explicitly stop MailDev (Ports 1080, 1025).
   - **[4] Install Dependencies:** Support Python 3.14.7, Node, and Playwright. DO NOT install bundled Chromium if host Google Chrome is selected for RPA. Support Chromium, Google Chrome, and Edge dynamically.
   - **[5] Purge Folders:** Delete `.venv`, `node_modules`, `.next`, `.turbo`, `__pycache__`, caches safely without touching source code or credentials. Check and preserve all 5 protected user directories.
   - **[6] RPA Mode:** Toggle Attended (GUI) vs Unattended (Headless). Ensure the backend honors this setting in both `.env` and runtime DB/Redis settings.
   - **[7] Diagnostics:** Run Pytest, Ruff, TypeScript checks. Do not hide `PytestUnraisableExceptionWarnings`. Fix any underlying issues causing `PytestUnraisableExceptionWarning`.
   - **[8] Docker:** Start/stop containerized stack safely with an interactive management submenu.
   - **[9] Live Monitor:** Show real health checks (not just open ports) for Frontend, Backend, Redis (PING), Celery (Worker processes), Flower, and MailDev (HTTP + SMTP banner probe).
   - **[M] MailDev:** Open localhost:1080 and verify SMTP/HTTP health before launching browser.
2. **Option [3] - Enterprise Data Cleanup**:
   - Transform Option 3 into a time-based, multi-select cleanup engine.
   - **Categories:** Multi-select for Claims, Queue Data, Scraped Cases, Fuzzy Matches, Guidewire Data, Notifications, Telemetry, Logs, Caches, and all operational data (18 categories).
   - **Time Scope:** Support **Current Month** (dynamically calculated from 1st of month 00:00:00 to now), Previous Month, Current Quarter, Previous Quarter, Current Year, Days, Weeks, Months, Years, and Custom Date Ranges.
   - **Safety:** Require a Dry-Run preview. Require explicit confirmation. Implement transactional rollback.
   - **Reconciliation:** Relationship-aware cascade deletion (e.g., Notification Delivery History deleted when parent claims are deleted). Invalidate Dashboard and Redis caches post-cleanup.

---

## 2. Gap Analysis & Existing State Audit

| Item | Existing State | Required State | Action Planned |
|---|---|---|---|
| **Script Alias** | Only `setup_local.ps1` and `setup.ps1` exist. Calling `setup-local.ps1` fails. | `setup-local.ps1` must be supported seamlessly. | Create `setup-local.ps1` forwarding wrapper passing all parameters to `setup_local.ps1`. |
| **Option [9] Live Health Checks** | Checks TCP port connection for 6379, 1025, 5432. Celery Worker is not explicitly checked. | Real application-level health checks (Redis PING, SMTP 220 banner, Celery Worker process detection). | Upgrade `Invoke-CheckServiceHealth` with socket protocol probes (Redis PING -> PONG, SMTP banner probe, Celery worker process detection). |
| **Option [M] MailDev Inspection** | Launches `http://localhost:1080` in browser directly. | Verifies HTTP (1080) and SMTP (1025) health before launching. | Add live health verification probe before launching browser in Option [M]. |
| **Option [8] Docker Submenu** | Simple `[U]p / [D]own / [R]estart` prompt. | Comprehensive containerized stack management (Infra vs Full Stack, Purge, Status). | Implement structured Docker management submenu in Option [8]. |
| **Time Scope Scenarios** | `current_month`, `previous_month`, `last_n_*`, `custom_range` supported. | Support `current_quarter`, `previous_quarter`, `current_year` dynamically. | Add quarter and year calculators to `resolve_time_window` in `cleanup_service.py` and `clean_history.py`. |
| **Option [6] RPA Sync** | Modifies `backend/.env`. | Synchronize `.env` AND persisted runtime settings (`SystemSettings` in Redis/DB). | Call Python settings service update snippet during `Invoke-SetRpaMode` to ensure instant worker synchronization. |
| **Purge Folders Scope** | Purges `.venv`, `node_modules`, `.next`, `.turbo`, backend caches. | Purge root `.pytest_cache` and any orphan temporary files; preserve 5 protected user directories. | Include root `.pytest_cache` in purge targets; reinforce protected folder invariants. |
| **Frontend API Integration** | Cleanup endpoints exist on FastAPI backend (`/api/v1/cleanup/*`), but not typed in frontend. | Type-safe `cleanupApi` client in `frontend/src/lib/api.ts` and `frontend/src/types/index.ts`. | Add `CleanupCategory`, `CleanupPreview`, `CleanupExecute` types and `cleanupApi` to frontend. |

---

## 3. Proposed Changes

### Component 1: PowerShell Console Architecture & Process Management
#### [NEW] [setup-local.ps1](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/setup-local.ps1)
- Create PowerShell forwarding script to delegate execution directly to `setup_local.ps1` preserving all CLI switches (`-StartAll`, `-StopAll`, `-CleanHistory`, `-PurgeDeps`, `-InstallDeps`, `-RunTests`, `-CheckPorts`, `-Mode`, `-NoPrompt`, `-LogFile`).

#### [MODIFY] [setup_local.ps1](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/setup_local.ps1)
- **Enhanced Live Health Probes (`Invoke-CheckServiceHealth`)**:
  - Add Redis protocol probe: send `*1\r\n$4\r\nPING\r\n` over TCP socket to port 6379; verify `+PONG` response -> report `[HEALTHY] Redis Queue Broker (Port 6379 - PING/PONG OK)`.
  - Add SMTP banner probe: connect to port 1025, read initial greeting banner (`220 ...`), send `QUIT\r\n` -> report `[HEALTHY] MailDev SMTP Server (Port 1025 - SMTP Ready)`.
  - Add Celery Worker probe: inspect running processes for `celery` worker with PID and active queue list.
- **Enhanced Option [M] (MailDev Console)**:
  - Probe and display MailDev Web (1080) and SMTP (1025) status before opening `http://localhost:1080` in default browser.
- **Enhanced Option [6] (RPA Mode Toggle)**:
  - Update `backend/.env` AND trigger Python synchronization of `SystemSettings.automation.headless_mode` in Redis so background workers pick it up immediately.
- **Enhanced Option [8] (Docker Management Submenu)**:
  - Provide clear choices: [1] Start Infrastructure (PostgreSQL, Redis, MailDev), [2] Stop Infrastructure, [3] Start Full Stack, [4] Stop & Purge Containers/Volumes, [5] Container Health Status, [B] Back to Menu.
- **Enhanced Option [5] (Purge Folders)**:
  - Add root `.pytest_cache` to purge candidate list while strictly verifying that the 5 protected user directories (`implementation_plan`, `PowerAutomateSolutions`, `Testing files`, `anticaptcha-plugin_v0.83`, `.agents`) are never modified.

### Component 2: Enterprise Data Cleanup Engine
#### [MODIFY] [backend/app/services/cleanup_service.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/services/cleanup_service.py)
- In `resolve_time_window()`:
  - Add support for `current_quarter` (dynamically calculated from 1st day of current quarter to now).
  - Add support for `previous_quarter` (1st to last day of previous quarter).
  - Add support for `current_year` (January 1st of current year 00:00:00 to now).

#### [MODIFY] [backend/app/scripts/clean_history.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/scripts/clean_history.py)
- Update `MENU_TIME_SCOPES` to include `current_quarter`, `previous_quarter`, and `current_year`.

#### [MODIFY] [backend/app/schemas/cleanup.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/schemas/cleanup.py)
- Ensure Pydantic schema validation allows the new time scope values.

### Component 3: Frontend API & Types
#### [MODIFY] [frontend/src/types/index.ts](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/types/index.ts)
- Add TypeScript interfaces for `CleanupCategory`, `CleanupPreviewRequest`, `CleanupPreviewResponse`, `CleanupExecuteRequest`, `CleanupExecuteResponse`.

#### [MODIFY] [frontend/src/lib/api.ts](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/lib/api.ts)
- Export `cleanupApi` with `getCategories()`, `preview()`, and `execute()`.

### Component 4: Test Suite & Verification
#### [MODIFY] [backend/tests/test_setup_console.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/tests/test_setup_console.py)
- Add unit tests verifying `setup-local.ps1` existence and syntax.
- Add unit tests verifying Redis socket PING and SMTP socket banner probe helpers.

#### [MODIFY] [backend/tests/test_enterprise_cleanup.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/tests/test_enterprise_cleanup.py)
- Add unit tests verifying `current_quarter`, `previous_quarter`, and `current_year` time window resolution.

---

## 4. Verification Plan

### Automated Tests
1. **PowerShell Setup Console Test Harness**:
   - `powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\test_setup_console.ps1"`
   - Verifies AST syntax across `setup_local.ps1`, `setup-local.ps1`, and `setup.ps1` (0 errors).
   - Tests `-CheckPorts`, `-StopAll`, `-CleanHistory`, and `-RunTests`.
2. **PowerShell AST Syntax Check across all repository scripts**:
   - `powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"` (0 errors).
3. **Backend Unit & Integration Tests**:
   - `cd backend && .venv\Scripts\pytest tests/test_setup_console.py tests/test_enterprise_cleanup.py tests/test_guidewire_models.py -v`
   - All tests passing with 0 warnings/errors.
4. **Code Quality & Type Checking**:
   - `cd backend && .venv\Scripts\ruff check app tests` (0 errors).
   - `cd frontend && npx tsc --noEmit` (0 errors).
5. **Docker Compose Validation**:
   - `docker compose config --quiet` (valid configuration).

---

## 5. Acceptance Criteria Checklist

- [ ] `setup-local.ps1` and `setup_local.ps1` both execute cleanly with real process management.
- [ ] Option [1] checks port conflicts before starting and supports interactive RPA mode selection.
- [ ] Option [2] safely kills application ports, processes, and explicitly stops/verifies MailDev (1080/1025).
- [ ] Option [3] supports 18 multi-select categories, dynamic Current Month, Quarters, Years, dry-run preview, explicit confirmation, cascade-delete, and cache invalidation.
- [ ] Option [4] detects Google Chrome, Edge, and bundled Chromium dynamically; skips Chromium download when system Chrome is active.
- [ ] Option [5] purges `.venv`, `node_modules`, `.next`, and build caches safely without touching source code, credentials, or the 5 protected folders.
- [ ] Option [6] toggles Attended vs Unattended mode and synchronizes both `.env` and runtime settings.
- [ ] Option [7] runs diagnostics without suppressing `PytestUnraisableExceptionWarning`.
- [ ] Option [8] manages Docker infrastructure and stack safely with interactive controls.
- [ ] Option [9] performs real health checks (HTTP, SMTP banner, Redis PING, Celery worker detection).
- [ ] Option [M] verifies MailDev health before opening browser.
- [ ] All automated tests (pytest, ruff, tsc, ps1) pass with 100% success rate.
