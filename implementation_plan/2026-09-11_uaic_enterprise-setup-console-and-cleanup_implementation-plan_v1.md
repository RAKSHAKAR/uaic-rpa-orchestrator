# Implementation Record

**Implementation ID:**   IMP-2026-0911-002  
**Project:**             UAIC Claim & RPA Orchestrator  
**Module:**              Enterprise Setup Console (Options 1-9, [M]), Real Process Management, Data Cleanup Engine  
**Feature / Issue:**     Enterprise Setup Console (Options 1-9) & Data Cleanup Full Audit, Gap Remediation, and Productionization  
**Document Type:**       Implementation Plan  
**Version:**             v2  
**Status:**              Awaiting Approval  
**Created:**             2026-09-11  
**AI Agent:**            Antigravity (Advanced Agentic Coding)  
**Approval Status:**     Pending  
**Approved By:**         Pending  
**Approval Date:**       Pending  
**Verification Status:** AI Generated — Awaiting Human Approval  

---

## 1. Problem & Executive Summary

The user requested a full audit, remediation, and finalization of the Enterprise Setup Console scripts (`setup_local.ps1`, `setup.ps1`, `clean_history.py`, etc.) ensuring all menu options [1] through [9] and [M] operate on real Windows process management rather than blind executions:
- **[1] Start All Services:** Interactive launch (Attended GUI vs Unattended Headless mode) with pre-flight port conflict detection and resolution.
- **[2] Stop All Services:** Safely terminate Ports 3000, 8000, 5555, 6379, 5432, Celery, and explicitly terminate MailDev (Ports 1080, 1025) and verify release.
- **[3] Enterprise Data Cleanup:** Time-based, multi-select cleanup engine (Claims, Queue Data, Scraped Cases, Fuzzy Matches, Guidewire Data, Notifications, Telemetry, Logs, Caches) with dynamic Current Month, Days, Weeks, Months, Years, Custom Ranges. Require Dry-Run preview, explicit confirmation, transactional rollback, relationship-aware cascade deletion (including notification delivery history), and cache invalidation.
- **[4] Install Dependencies:** Support Python 3.14.7, Node, and Playwright. **CRITICAL:** Do NOT install bundled Chromium if host Google Chrome is selected for RPA; dynamically support Chromium, Google Chrome, and Edge.
- **[5] Purge Folders:** Delete `.venv`, `node_modules`, `.next`, and build caches safely without touching source code, credentials, or protected folders.
- **[6] RPA Mode:** Toggle Attended (GUI) vs Unattended (Headless); ensure backend honors this setting.
- **[7] Diagnostics:** Run Pytest, Ruff, TypeScript, PS1 checks. Fix underlying root causes for `PytestUnraisableExceptionWarning` rather than hiding them.
- **[8] Docker:** Manage containerized stack safely.
- **[9] Live Monitor:** Show real HTTP/TCP health checks for Frontend, Backend, Redis, Celery, Flower, MailDev.
- **[M] MailDev:** Open localhost:1080 and verify SMTP/HTTP health.

> [!IMPORTANT]
> **User Mandate:** The user will **NOT** perform manual verification. All options, cleanup behaviors, process management, port checks, warnings, and browser matrix scenarios must be validated through an exhaustive, 100% automated test suite and verification harnesses created and executed autonomously by the AI agent.

---

## 2. Technical Findings & Root Cause Analysis

### Finding 1 — Missing Option [7] Diagnostic Function in `setup_local.ps1`
- **Root Cause:** Line 472 routes `"7" { Invoke-RunTestSuite; Read-Host ... }`, but `function Invoke-RunTestSuite` was never defined in `setup_local.ps1`. Invoking Option [7] threw `CommandNotFoundException`.
- **Resolution:** Implement `Invoke-RunTestSuite` executing all 5 diagnostic steps: Pytest, Ruff, TypeScript (`tsc --noEmit`), Docker compose config, and PowerShell AST syntax check (`check_ps1_syntax.ps1`).

### Finding 2 — Root Cause of `PytestUnraisableExceptionWarning` in `test_browser_matrix.py`
- **Root Cause:**
  1. In `tests/test_browser_matrix.py`, `mocker.patch("playwright.async_api.async_playwright")` patched the global library path instead of `app.automation.browser_manager.async_playwright`. Because `browser_manager.py` did `from playwright.async_api import async_playwright`, the mock missed, causing real Playwright to spawn a `node.exe` driver with OS pipes.
  2. In `app.automation.browser_manager.ChromeSession.start()`, `self.playwright` was initialized before checking `find_chrome_executable`. When `find_chrome_executable` returned `None`, it threw `RuntimeError` without closing `self.playwright`.
  3. When the test completed and the event loop closed, Python's GC destroyed the orphaned pipe transport, raising `ValueError: I/O operation on closed pipe` inside `BaseSubprocessTransport.__del__`.
- **Resolution:**
  1. Add defensive cleanup to `ChromeSession.start()`: `try...except Exception: if self.playwright: await self.playwright.stop(); self.playwright = None; raise`.
  2. Correct the mock target in `test_browser_matrix.py` to `"app.automation.browser_manager.async_playwright"`.
  3. Remove `"ignore::pytest.PytestUnraisableExceptionWarning"` from `backend/pyproject.toml`.

### Finding 3 — Option [4] Unconditionally Downloaded Playwright Chromium
- **Root Cause:** Lines 224-225 unconditionally ran `playwright install chromium` regardless of whether system Google Chrome was detected or configured.
- **Resolution:** Build dynamic browser detection in PowerShell and Python checking Registry and Program Files for Google Chrome (`chrome.exe`), Microsoft Edge (`msedge.exe`), and Playwright Chromium. If Google Chrome or Edge is detected and configured, skip `playwright install chromium`.

### Finding 4 — Option [2] Failed to Kill Uvicorn & Celery Processes
- **Root Cause:** `Get-Process` in Windows PowerShell does not populate the `CommandLine` property (always `$null`). Celery and Uvicorn run as `python.exe`. Filtering with `$_.CommandLine -like "*$rootDir*"` matched zero processes, leaving orphaned workers running.
- **Resolution:** Use `Get-CimInstance Win32_Process` to query processes whose `CommandLine` contains `uvicorn`, `celery`, `flower`, or paths within `$rootDir`. Explicitly terminate MailDev processes and Docker container `uaic_maildev` on ports 1080 and 1025 and verify socket release.

### Finding 5 — Redis Offline Timeout Hang During Cleanup
- **Root Cause:** `redis.Redis.from_url(...)` in `clean_history.py` and `cleanup_service.py` omitted socket connect timeouts, blocking for 60-120 seconds on Windows when Redis was offline.
- **Resolution:** Add `socket_connect_timeout=1.0, socket_timeout=1.0` to fail over immediately with a warning. Invalidate dashboard metrics caches post-cleanup.

### Finding 6 — Missing Non-Interactive CLI Handlers in `setup_local.ps1`
- **Root Cause:** Parameter switches (`-RunTests`, `-Clean`, `-CleanHistory`, `-PurgeDeps`, `-InstallDeps`, `-CheckPorts`) lacked execution blocks before entering the interactive loop.
- **Resolution:** Wire up CLI switch dispatchers so the entire script can be operated headlessly by automated test harnesses and CI pipelines.

---

## 3. Proposed Changes

### Component 1: Setup Console & Process Management

#### [MODIFY] [setup_local.ps1](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/setup_local.ps1)
- Implement `Invoke-CheckPortConflicts` for Option [1] (reporting PID and process before starting).
- Rewrite `Invoke-KillAllServices` for Option [2] using `Get-CimInstance Win32_Process` to terminate Python/Node processes by CommandLine; explicitly terminate MailDev (Ports 1080/1025) and Docker container `uaic_maildev`.
- Implement `Invoke-RunTestSuite` for Option [7] with 5 verification steps (Pytest, Ruff, TypeScript, Docker, PS1 syntax).
- Update `Invoke-InstallDependencies` for Option [4] with dynamic browser detection; skip Playwright Chromium if Google Chrome is selected/detected.
- Add cache directories (`.ruff_cache`, `.pytest_cache`, `.turbo`, `__pycache__`) to `Invoke-PurgeDependencyFolders` for Option [5].
- Add CLI switch execution blocks for `-RunTests`, `-CheckPorts`, `-StopAll`, `-StartAll`, `-Clean`, `-CleanHistory`, `-PurgeDeps`, `-InstallDeps`.

#### [MODIFY] [scripts/setup.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/scripts/setup.py)
- Fix `ROOT_DIR` path resolution from `os.path.dirname(__file__)` to `os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))`.

### Component 2: Browser Management & Diagnostics

#### [MODIFY] [backend/app/automation/browser_manager.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/browser_manager.py)
- In `ChromeSession.start()`: wrap initialization in `try...except Exception:` block to stop and nullify `self.playwright` on failure, preventing orphaned pipe handles and GC warnings.

#### [MODIFY] [backend/tests/test_browser_matrix.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/tests/test_browser_matrix.py)
- Fix `async_playwright` mock target to `"app.automation.browser_manager.async_playwright"`.

#### [MODIFY] [backend/pyproject.toml](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/pyproject.toml)
- Remove `"ignore::pytest.PytestUnraisableExceptionWarning"` to guarantee zero unraisable warnings across the test suite.

### Component 3: Enterprise Data Cleanup Engine

#### [MODIFY] [backend/app/scripts/clean_history.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/scripts/clean_history.py)
- Add `socket_connect_timeout=1.0, socket_timeout=1.0` to Redis client initialization to eliminate offline hanging.

#### [MODIFY] [backend/app/services/cleanup_service.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/services/cleanup_service.py)
- Add Redis connection timeouts (`1.0s`).
- Invalidate dashboard analytics cache keys post-cleanup.
- Add cascade-deletion handling for `Notification` records linked by `claim_id` to prevent orphan rows.

### Component 4: Automated Testing Harnesses & Test Suites

#### [NEW] [backend/tests/test_setup_console.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/tests/test_setup_console.py)
- Dedicated automated test suite testing all console behaviors programmatically:
  - `test_port_conflict_detection`: Verifies port detection logic identifies listening sockets on 8000, 3000, 1080, 1025, 5555, 6379, 5432.
  - `test_service_kill_process_filtering`: Verifies process filtering criteria against Win32_Process attributes (`CommandLine`, `ProcessId`, executable name) for Uvicorn, Celery, Flower, Node, and MailDev.
  - `test_browser_matrix_skips_chromium_when_chrome_detected`: Validates that when system Google Chrome is selected/detected, Playwright Chromium installation is skipped, and verifies browser executable path resolution.
  - `test_purge_folders_safety_invariants`: Tests that purge candidate lists strictly exclude source code (`backend/app`, `frontend/src`), configuration (`.env`, `.env.local`), and protected directories (`implementation_plan`, `PowerAutomateSolutions`, `Testing files`, `anticaptcha-plugin_v0.83`, `.agents`), and accurately targets `.venv`, `node_modules`, `.next`, `.ruff_cache`, `.pytest_cache`.
  - `test_rpa_mode_toggle_and_backend_adherence`: Tests toggling Attended vs Unattended mode via `settings_service` and verifies `get_system_settings_async()` returns the exact boolean flag and `ChromeSession` propagates `headless` accordingly.
  - `test_diagnostics_runner_zero_unraisable_warnings`: Executes diagnostic check runners and verifies that no `PytestUnraisableExceptionWarning` is raised or suppressed.
  - `test_docker_compose_config_validity`: Validates `docker-compose.yml` structural integrity, service definitions, volume mappings, and environment variables.
  - `test_live_monitor_health_probe_logic`: Tests real HTTP/TCP health probe logic against running/stopped mock servers for Backend (8000), Frontend (3000), Flower (5555), MailDev (1080/1025), and Redis (6379).
  - `test_maildev_endpoint_and_smtp_verification`: Tests probe logic for MailDev HTTP (1080) and SMTP (1025) endpoints.

#### [MODIFY] [backend/tests/test_enterprise_cleanup.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/tests/test_enterprise_cleanup.py)
- Add tests for:
  - `test_execute_cleanup_cascade_notifications_and_children`: Seeds claim with ScrapedCourtCase, MatchPair, ErrorScreenshot, and NotificationDeliveryHistory; runs claim cleanup; asserts all child records are removed and 0 orphans remain.
  - `test_time_window_current_month_dynamic`: Validates boundary logic on various mock dates across leap years and month boundaries.
  - `test_cleanup_transactional_rollback`: Injects a simulated database exception mid-transaction; asserts session rolls back, no partial data loss occurs, and an error is returned.
  - `test_cleanup_cache_invalidation_redis_offline`: Asserts cleanup runs cleanly and gracefully logs warning without freezing when Redis is offline (timeout = 1.0s).

#### [NEW] [scripts/test_setup_console.ps1](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/scripts/test_setup_console.ps1)
- Automated PowerShell test harness executing non-interactively:
  - AST syntax check of `setup_local.ps1` and `setup.ps1`.
  - Validation of CLI parameter switches (`-CheckPorts`, `-StopAll`, `-RunTests`, `-CleanHistory`).
  - Validation of port conflict detection and process termination logic.
  - Validation of MailDev port 1080/1025 stopping logic.

---

## 4. 100% Automated Verification Strategy (Zero Manual Steps)

The table below details how every option and requirement is verified **purely through automated test execution**:

| Menu Option / Requirement | Automated Test Case / Script | Verification Assertion |
|---|---|---|
| **[1] Start Services & Port Check** | `test_setup_console.py::test_port_conflict_detection`<br>`scripts/test_setup_console.ps1` | Sockets on ports 8000/3000/1080 detected; reports conflicting PID and process name before start. |
| **[2] Stop Services & MailDev** | `test_setup_console.py::test_service_kill_process_filtering`<br>`scripts/test_setup_console.ps1 -StopAll` | Win32_Process filtering kills target PIDs; explicitly checks and verifies ports 1080 and 1025 released. |
| **[3] Enterprise Cleanup: Categories** | `test_enterprise_cleanup.py::test_categories_expansion`<br>`test_cleanup_api_endpoints` | All 10 categories expandable; multi-select returns accurate categorization. |
| **[3] Enterprise Cleanup: Time Scope** | `test_enterprise_cleanup.py::test_time_window_resolution`<br>`test_time_window_current_month_dynamic` | Dynamic Current Month correctly calculates `YYYY-MM-01 00:00:00` to current moment; handles month boundaries. |
| **[3] Enterprise Cleanup: Dry-Run & Safety** | `test_enterprise_cleanup.py::test_calculate_cleanup_preview_no_mutations`<br>`clean_history.py --dry-run` | Zero records mutated; returns accurate record counts; unconfirmed execution rejected with 400. |
| **[3] Enterprise Cleanup: Rollback** | `test_enterprise_cleanup.py::test_cleanup_transactional_rollback` | Database transaction rolls back on exception; no partial records deleted. |
| **[3] Enterprise Cleanup: Cascade** | `test_enterprise_cleanup.py::test_execute_cleanup_claim_cascades`<br>`test_execute_cleanup_cascade_notifications_and_children` | Deleting parent Claim cascades to ScrapedCourtCase, MatchPair, ErrorScreenshot, and Notification; 0 orphans left. |
| **[3] Enterprise Cleanup: Caches** | `test_enterprise_cleanup.py::test_dashboard_stats_reconciled_after_cleanup`<br>`test_cleanup_cache_invalidation_redis_offline` | Dashboard stats reconciled immediately; Redis offline handled within 1.0s without hanging. |
| **[4] Install Dependencies: Chrome** | `test_setup_console.py::test_browser_matrix_skips_chromium_when_chrome_detected`<br>`test_browser_matrix.py` | Google Chrome detected in registry/disk; Playwright Chromium download skipped. |
| **[5] Purge Folders: Safety** | `test_setup_console.py::test_purge_folders_safety_invariants` | Purge lists target only `.venv`, `node_modules`, `.next`, cache dirs; protected user dirs & `.env` are immune. |
| **[6] RPA Mode: Headless Toggle** | `test_setup_console.py::test_rpa_mode_toggle_and_backend_adherence`<br>`test_settings_alignment.py` | `rpa_headless=False` sets Attended GUI; `True` sets Headless; backend reads and applies setting. |
| **[7] Diagnostics: Zero Warnings** | `pytest -ra -q --asyncio-mode=auto`<br>`test_browser_matrix.py` | 0 `PytestUnraisableExceptionWarning` emitted; pyproject.toml suppression removed; 172 passed, 10 skipped. |
| **[7] Diagnostics: Linters & Syntax** | `ruff check app tests`<br>`npx tsc --noEmit`<br>`check_ps1_syntax.ps1` | Zero Ruff errors, zero TypeScript errors, zero PowerShell AST errors. |
| **[8] Docker: Safe Management** | `test_setup_console.py::test_docker_compose_config_validity` | `docker-compose.yml` validated for service topology, health checks, environment parameters. |
| **[9] Live Monitor: Real Health** | `test_setup_console.py::test_live_monitor_health_probe_logic`<br>`test_health_detailed.py` | Probes send real HTTP GET to `/health` and TCP pings; status, latency, and down-state parsed correctly. |
| **[M] MailDev: Health & Port 1080** | `test_setup_console.py::test_maildev_endpoint_and_smtp_verification`<br>`test_email_notifications.py` | HTTP port 1080 and SMTP port 1025 probe logic returns healthy when running, down when stopped. |

---

## 5. Automated Execution Sequence

Upon user approval, Antigravity will autonomously execute the following automated test commands in sequence and capture outputs:

```bash
# 1. PowerShell AST Syntax Verification across all repository scripts
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"

# 2. Setup Console & Process Management Automated Test Suite
cd backend
.venv\Scripts\pytest tests\test_setup_console.py -ra -q --asyncio-mode=auto

# 3. Enterprise Data Cleanup Test Suite (Categories, Scopes, Cascades, Rollback, Caches)
.venv\Scripts\pytest tests\test_enterprise_cleanup.py -ra -q --asyncio-mode=auto

# 4. Browser Matrix & Unraisable Warning Root Cause Fix Test
.venv\Scripts\pytest tests\test_browser_matrix.py -ra -q --asyncio-mode=auto

# 5. Full Backend Test Suite (Guarantee 172+ passed, 10 skipped, ZERO unraisable warnings)
.venv\Scripts\pytest -ra -q --asyncio-mode=auto

# 6. Python Linter
.venv\Scripts\ruff check app tests

# 7. Frontend TypeScript Type-Checking
cd ..\frontend
npx tsc --noEmit

# 8. PowerShell Setup Console Non-Interactive Test Harness
cd ..
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\test_setup_console.ps1"

# 9. Enterprise Clean History CLI Non-Interactive Execution Test
cd backend
.venv\Scripts\python -m app.scripts.clean_history --dry-run --categories all_operational --time-scope current_month

# 10. Final Local Dev Script Syntax Check
cd ..
powershell -NoProfile -ExecutionPolicy Bypass -File "setup_local.ps1" -CheckPorts
```

---

## 6. Acceptance Criteria

- [ ] `setup_local.ps1` and `setup.ps1` pass PowerShell AST parser with 0 errors.
- [ ] Option [1] checks port conflicts before starting and logs PID/process details if ports are in use.
- [ ] Option [2] terminates Python (Uvicorn, Celery, Flower) and Node via Win32_Process and explicitly stops MailDev (ports 1080, 1025).
- [ ] Option [3] functions as an enterprise cleanup engine with multi-category selection, dynamic current month / custom time scopes, dry-run preview, transactional rollback, cascade deletion of child records (including notifications), and cache invalidation.
- [ ] Option [4] dynamically inspects Chrome, Edge, Chromium and skips Playwright Chromium installation when system Google Chrome is selected/detected.
- [ ] Option [5] safely purges `.venv`, `node_modules`, `.next`, and build caches without touching source code or credentials.
- [ ] Option [6] toggles Attended vs Unattended RPA mode and backend `get_system_settings_async()` honors it.
- [ ] Option [7] runs all diagnostics without hiding `PytestUnraisableExceptionWarning`.
- [ ] Root cause of `PytestUnraisableExceptionWarning` in `test_browser_matrix.py` and `browser_manager.py` is permanently resolved.
- [ ] Option [8] validates Docker stack safely.
- [ ] Option [9] displays live HTTP/TCP health probe results.
- [ ] Option [M] validates MailDev HTTP (1080) and SMTP (1025) health.
- [ ] All 182+ backend tests pass with 0 unraisable warnings.
- [ ] Zero manual verification required from the user — all acceptance criteria validated via automated tests.

---

**No application source code has been modified yet.**  
**Plan updated in:** `implementation_plan/2026-09-11_uaic_enterprise-setup-console-and-cleanup_implementation-plan_v1.md`  
Please review the 100% automated test verification plan and confirm your approval so I may begin implementation and automated execution.
