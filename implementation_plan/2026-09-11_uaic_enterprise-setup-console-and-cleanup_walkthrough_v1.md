# Enterprise Setup Console (Options 1–9 & M) & Data Cleanup Engine — Walkthrough

> **Status:** Complete  
> **Implementation ID:** `IMP-2026-0911-002`  
> **AI Verification:** Complete (100% Automated Testing Suite)  
> **Execution Date:** September 11, 2026  

---

## 1. Executive Summary

This engineering delivery successfully finalized and audited the **UAIC Enterprise Setup Console** (`setup_local.ps1`, `setup.ps1`, `scripts/setup.py`) and implemented the **Enterprise Time-Based Multi-Select Data Cleanup Engine** (`backend/app/services/cleanup_service.py`, `backend/app/scripts/clean_history.py`).

Per strict user mandate, **all verification was performed 100% autonomously via comprehensive automated test suites** across PowerShell AST syntax, process filtering, port conflict scanners, dynamic browser matrices, safety invariants, and database cascade deletion. **Zero manual steps were required from the user.**

---

## 2. Key Architecture & Features Implemented

### 2.1 Option [1]: Start All Services & Port Conflict Pre-Flight
- Added pre-flight port conflict scanning (`Invoke-CheckPortConflicts`) before launching any child services.
- Probes target application ports (`3000`, `8000`, `5555`, `6379`, `5432`, `1080`, `1025`) using native `Get-NetTCPConnection` and reports occupying PIDs/Process Names.
- Supported non-interactive parameter `-CheckPorts` for programmatic health pre-flights.
- Supports Attended GUI (visible Chrome) vs Unattended Headless launch modes.

### 2.2 Option [2]: Safe Process Termination & Explicit MailDev Shutdown
- Upgraded `Invoke-KillAllServices` using `Get-CimInstance Win32_Process` to inspect command lines and safely terminate only application workers (`uvicorn`, `celery`, `flower`, `maildev`, `next dev`), never touching unrelated system processes.
- Enforced explicit termination and port release verification for MailDev (Ports `1080` Web UI and `1025` SMTP).
- Added `-StopAll` CLI switch for automated pipeline shutdowns.

### 2.3 Option [3]: Enterprise Time-Based Multi-Select Data Cleanup Engine
- Built a time-scoped, multi-category cleanup engine supporting:
  - **9 Data Categories:** Claims, Queue Items, Scraped Court Cases, Fuzzy Match Results, Guidewire Activity Payloads, Notifications Delivery History, Audit/Telemetry Records, Operational Logs, Redis Caches.
  - **Flexible Time Windows:** `current_month` (dynamically calculated `1st of current month 00:00:00` to current moment), `1_day`, `7_days`, `14_days`, `30_days`, `90_days`, `6_months`, `1_year`, `all_time`, and custom date ranges.
  - **Dry-Run Preview:** Simulates deletions and returns exact counts without database mutation.
  - **Strict Cascade Deletion:** Eliminates child records (cases, matches, screenshots, notifications) when deleting claims to guarantee zero orphan records.
  - **Cache & Redis Invalidation:** Safely purges dashboard metrics (`cache:*`, `metrics:*`, `stats:*`, `dashboard:*`) with robust 1.0s socket connect timeouts to prevent worker deadlocks when Redis is offline.
  - **CLI & REST API:** Fully exposed via `python -m app.scripts.clean_history` and `POST /api/v1/claims/clean`.

### 2.4 Option [4]: Dynamic Browser Matrix & Conditional Chromium Installation
- Implemented `Test-BrowserAvailability` to inspect host environments for Google Chrome and Microsoft Edge.
- **Critical Requirement Fulfilled:** Playwright bundled Chromium installation is **completely bypassed** when Google Chrome or Microsoft Edge is detected or configured in `.env` (`PLAYWRIGHT_CHANNEL=chrome`).
- Dynamic selection allows operators to select Chromium, Google Chrome, or Microsoft Edge interactively.

### 2.5 Option [5]: Safe Folder Purge Invariants
- Upgraded `Invoke-PurgeDependencyFolders` to clean `.venv`, `node_modules`, `.next`, `.turbo`, and pytest/ruff build caches.
- **Strict Invariant Maintained:** Protected directories (`implementation_plan`, `PowerAutomateSolutions`, `Testing files`, `anticaptcha-plugin_v0.83`, `.agents`), source code, and credentials (`.env`, `.env.local`) are explicitly verified and protected from purging.

### 2.6 Option [6]: RPA Mode Toggle
- Toggles between Attended GUI (visible browser, CAPTCHA inspection) and Unattended Headless (Docker/CI).
- Persisted to Redis and local settings, and strictly honored by `ChromeSession` startup.

### 2.7 Option [7]: Diagnostics & Zero Unraisable Warning Resolution
- **Root Cause Identified & Fixed:** Playwright driver in `ChromeSession.start()` spawned an OS pipe driver before verifying Chrome executable existence on disk. When resolution failed, the pipe handle was orphaned; event loop closure triggered `ValueError: I/O operation on closed pipe` captured by `sys.unraisablehook`.
- **Solution:** Added pre-validation of Chrome executable path and defensive `try...except` cleanup in `ChromeSession.start()`.
- **Warning Invariant:** Removed `ignore::pytest.PytestUnraisableExceptionWarning` from `pyproject.toml`. Zero warnings are suppressed.
- `Invoke-RunTestSuite` coordinates 5 diagnostic passes (Pytest, Ruff, TypeScript, Docker Compose, PowerShell AST).

### 2.8 Options [8], [9], [M]: Docker Management, Live Health Monitor & MailDev
- Added host port mappings `5432:5432` (Postgres) and `6379:6379` (Redis) to `docker-compose.yml`.
- `Get-DockerComposeCommand` with `-AutoHeal` flag prevents 90-second timeouts during normal health checks.
- Live Health Monitor tests HTTP and TCP endpoints across Frontend, Backend, Redis, Celery, Flower, and MailDev.
- MailDev inspector verifies Ports `1080` (Web UI) and `1025` (SMTP).

---

## 3. Automated Test Verification Results

### 3.1 Backend Test Suite: `test_setup_console.py` (11 Tests, 100% Pass)
```
tests/test_setup_console.py::test_port_conflict_detection PASSED
tests/test_setup_console.py::test_service_kill_process_filtering PASSED
tests/test_setup_console.py::test_maildev_ports_explicit_termination_logic PASSED
tests/test_setup_console.py::test_browser_matrix_skips_chromium_when_chrome_detected PASSED
tests/test_setup_console.py::test_find_chrome_executable_resolution PASSED
tests/test_setup_console.py::test_purge_folders_safety_invariants PASSED
tests/test_setup_console.py::test_rpa_mode_toggle_and_backend_adherence PASSED
tests/test_setup_console.py::test_diagnostics_runner_zero_unraisable_warnings PASSED
tests/test_setup_console.py::test_docker_compose_config_validity PASSED
tests/test_setup_console.py::test_live_monitor_health_probe_logic PASSED
tests/test_setup_console.py::test_maildev_endpoint_and_smtp_verification PASSED

============================= 11 passed in 9.45s ==============================
```

### 3.2 Backend Test Suite: `test_enterprise_cleanup.py` (12 Tests, 100% Pass)
```
tests/test_enterprise_cleanup.py::test_time_window_calculation PASSED
tests/test_enterprise_cleanup.py::test_dry_run_preview PASSED
tests/test_enterprise_cleanup.py::test_execute_cleanup_claims_and_cascade PASSED
tests/test_enterprise_cleanup.py::test_execute_cleanup_queue_only PASSED
tests/test_enterprise_cleanup.py::test_execute_cleanup_all_operational PASSED
tests/test_enterprise_cleanup.py::test_execute_cleanup_custom_range PASSED
tests/test_enterprise_cleanup.py::test_clean_history_script_dry_run PASSED
tests/test_enterprise_cleanup.py::test_clean_history_script_execute PASSED
tests/test_enterprise_cleanup.py::test_cleanup_api_endpoint PASSED
tests/test_enterprise_cleanup.py::test_execute_cleanup_cascade_notifications_and_children PASSED
tests/test_enterprise_cleanup.py::test_time_window_current_month_dynamic PASSED
tests/test_enterprise_cleanup.py::test_cleanup_cache_invalidation_redis_offline PASSED

============================= 12 passed in 21.75s =============================
```

### 3.3 Backend Test Suite: `test_browser_matrix.py` (10 Tests, 100% Pass)
```
tests/test_browser_matrix.py::test_channel_defaults_to_chrome PASSED
tests/test_browser_matrix.py::test_channel_msedge PASSED
tests/test_browser_matrix.py::test_channel_chromium PASSED
tests/test_browser_matrix.py::test_channel_invalid PASSED
tests/test_browser_matrix.py::test_system_chrome_path PASSED
tests/test_browser_matrix.py::test_find_chrome_executable_found PASSED
tests/test_browser_matrix.py::test_find_chrome_executable_not_found PASSED
tests/test_browser_matrix.py::test_session_runner_channel PASSED
tests/test_browser_matrix.py::test_env_channel_propagation PASSED
tests/test_browser_matrix.py::test_extension_dir_with_channel PASSED

============================= 10 passed in 0.52s ==============================
```

### 3.4 PowerShell Automated Harness: `scripts/test_setup_console.ps1`
```
=======================================================================
      Enterprise Setup Console Automated Test Harness (PS1)            
=======================================================================
  [PASS] AST Syntax (setup_local.ps1 & setup.ps1)
  [PASS] Port Conflict Scanner (-CheckPorts)
  [PASS] Stop All Services (-StopAll, Ports 1080/1025 Verified Free)
  [PASS] Clean Run History (-CleanHistory)
  [PASS] Diagnostics Runner (-RunTests)
=======================================================================
ALL AUTOMATED POWERSHELL SETUP CONSOLE TESTS PASSED (0 FAILURES)!
```

### 3.5 Code Quality, Type Checking & AST Validation
- **Ruff Linter:** `ruff check app tests` -> **All checks passed (0 errors)**.
- **Frontend TypeScript:** `npx tsc --noEmit` -> **0 errors**.
- **PowerShell AST Syntax Check:** `scripts/check_ps1_syntax.ps1` -> **0 errors across all 6 `.ps1` scripts**.

---

## 4. Operational Commands Reference

```powershell
# Interactive Setup Console
.\setup_local.ps1

# Non-Interactive Pre-Flight Port Conflict Check
.\setup_local.ps1 -CheckPorts

# Safe Process Termination (kills all app processes, frees ports 3000, 8000, 5555, 6379, 5432, 1080, 1025)
.\setup_local.ps1 -StopAll

# Clean Run History (purges queues, clears operational logs, resets claim statuses)
.\setup_local.ps1 -CleanHistory

# Automated Diagnostics Suite (Pytest, Ruff, TypeScript, Docker, AST)
.\setup_local.ps1 -RunTests

# Enterprise Time-Based Data Cleanup CLI
python -m app.scripts.clean_history --categories all_operational --time-scope current_month --dry-run
python -m app.scripts.clean_history --categories claims,notifications --time-scope 30_days --confirm
```
