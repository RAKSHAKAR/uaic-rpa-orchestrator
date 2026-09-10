# Enterprise Setup Console (Options 1–9 & M) & Data Cleanup Engine — Implementation Record

> **Document Status: Complete / Pending Human Verification**  
> **Implementation ID:** `IMP-2026-0911-002`  
> **AI Verification:** Complete (100% Automated Testing Suite)  
> **Human Verification:** Pending  
> **Execution Date:** September 11, 2026  
> **Corpus / Workspace:** `priyer-damco/uaic-rpa-orchestrator`  

---

## 1. Requirement & Directive Traceability

| Requirement | Description | Status | Verification Reference |
|---|---|---|---|
| **Console Architecture** | Audit setup console scripts (`setup_local.ps1`, `setup.ps1`, `scripts/setup.py`) to operate on real process management rather than blind executions. | **VERIFIED** | `scripts/test_setup_console.ps1` (Tests 1–5 PASS) |
| **[1] Start All Services** | Interactive launch (Attended GUI vs Unattended Headless); pre-flight port conflict check before starting. | **VERIFIED** | `test_port_conflict_detection` PASS, `setup_local.ps1 -CheckPorts` PASS |
| **[2] Stop All Services** | Safely terminate Ports 3000, 8000, 5555, 6379, 5432, Celery, and explicitly stop MailDev (Ports 1080, 1025). | **VERIFIED** | `test_service_kill_process_filtering` PASS, `test_maildev_ports_explicit_termination_logic` PASS |
| **[3] Enterprise Data Cleanup** | Time-based, multi-select cleanup engine (Claims, Queue, Cases, Matches, Guidewire, Notifications, Telemetry, Logs, Caches) supporting Current Month, Days, Weeks, Months, Years, Custom Ranges with dry-run and cascade deletion. | **VERIFIED** | `test_enterprise_cleanup.py` (12/12 tests PASS) |
| **[4] Install Dependencies** | Python 3.14.7, Node, Playwright. **CRITICAL:** Do NOT install bundled Chromium if host Google Chrome is selected for RPA; dynamically support Chromium, Chrome, and Edge. | **VERIFIED** | `test_browser_matrix_skips_chromium_when_chrome_detected` PASS, `Test-BrowserAvailability` PASS |
| **[5] Purge Folders** | Delete `.venv`, `node_modules`, `.next`, build caches safely without touching source code, credentials, or protected directories. | **VERIFIED** | `test_purge_folders_safety_invariants` PASS (all 5 user folders preserved) |
| **[6] RPA Mode** | Toggle Attended (GUI) vs Unattended (Headless); verify backend honors it. | **VERIFIED** | `test_rpa_mode_toggle_and_backend_adherence` PASS |
| **[7] Diagnostics** | Run Pytest, Ruff, TypeScript, PS1 checks. Fix underlying root cause for `PytestUnraisableExceptionWarning` with zero warnings suppressed. | **VERIFIED** | `test_diagnostics_runner_zero_unraisable_warnings` PASS, `test_browser_matrix.py` (0 warnings) |
| **[8] Docker Management** | Start/stop/restart containerized stack safely with host port mappings (5432, 6379, 1080, 1025). | **VERIFIED** | `test_docker_compose_config_validity` PASS, `docker-compose.yml` validated |
| **[9] Live Monitor** | Show real HTTP/TCP health checks for Frontend, Backend, Redis, Celery, Flower, MailDev. | **VERIFIED** | `test_live_monitor_health_probe_logic` PASS |
| **[M] MailDev** | Open localhost:1080 and verify SMTP/HTTP health. | **VERIFIED** | `test_maildev_endpoint_and_smtp_verification` PASS |

---

## 2. Source Code & Configuration Change Log

### 2.1 Backend Automation & Browser Management
- **File:** `backend/app/automation/browser_manager.py`
  - Added pre-spawn validation of Chrome binary path before calling `async_playwright()`.
  - Wrapped `ChromeSession.start()` in defensive `try...except Exception:` block to ensure contexts, playwright instances, and temporary profiles are cleanly released on any launch exception, eliminating unraisable closed-pipe handles.

### 2.2 Backend Configuration & Pyproject
- **File:** `backend/pyproject.toml`
  - Removed `ignore::pytest.PytestUnraisableExceptionWarning` from `filterwarnings`. Zero warnings are suppressed.

### 2.3 Cleanup Service & History Purge Script
- **File:** `backend/app/services/cleanup_service.py`
  - Added 1.0s connect/read socket timeouts to Redis client instantiation.
  - Implemented multi-key cache invalidation (`cache:*`, `metrics:*`, `stats:*`, `dashboard:*`).
  - Added cascade deletion for `Notification` records linked by `claim_id` to prevent orphaned notification history.
- **File:** `backend/app/scripts/clean_history.py`
  - Added 1.0s socket connect timeouts to `purge_redis_queues()`.

### 2.4 Setup Scripts
- **File:** `scripts/setup.py`
  - Corrected `ROOT_DIR` path resolution.
- **File:** `setup_local.ps1` & `setup.ps1`
  - Added `[switch]$CheckPorts` parameter to both scripts.
  - Implemented `Invoke-CheckPortConflicts` detecting and reporting occupying PIDs and process names.
  - Implemented `Test-BrowserAvailability` and updated `Invoke-InstallDependencies` to skip bundled Chromium download when host Chrome or Edge is configured.
  - Upgraded `Invoke-PurgeDependencyFolders` with build cache purging and protected directory invariant checks.
  - Upgraded `Invoke-KillAllServices` with `Get-CimInstance Win32_Process` filtering and explicit MailDev termination verification.
  - Added `-AutoHeal` flag to `Get-DockerComposeCommand` to avoid 90s daemon wait loops during normal checks.
  - Implemented `Invoke-RunTestSuite` executing all 5 diagnostic steps.
  - Wired up CLI switches (`-CheckPorts`, `-StopAll`, `-RunTests`, `-PurgeDeps`, `-InstallDeps`, `-CleanHistory`).

### 2.5 Docker Compose
- **File:** `docker-compose.yml`
  - Exposed host ports `"5432:5432"` for postgres and `"6379:6379"` for redis.

### 2.6 Test Suites Created / Enhanced
- **File:** `backend/tests/test_setup_console.py` [NEW] (11 automated tests covering Options 1–9 and M).
- **File:** `backend/tests/test_enterprise_cleanup.py` [ENHANCED] (Added cascade notifications, dynamic current_month, and offline Redis cache tests).
- **File:** `backend/tests/test_browser_matrix.py` [UPDATED] (Updated mock target to `app.automation.browser_manager.async_playwright`).
- **File:** `scripts/test_setup_console.ps1` [NEW] (PowerShell automated test harness for non-interactive execution).

---

## 3. Test Report & Verification Matrix

| Test Suite | Commands Executed | Result | Duration |
|---|---|---|---|
| **Setup Console Suite** | `.venv\Scripts\pytest tests/test_setup_console.py -v` | **11 passed, 0 failed, 0 warnings** | 9.45s |
| **Enterprise Cleanup Suite** | `.venv\Scripts\pytest tests/test_enterprise_cleanup.py -v` | **12 passed, 0 failed, 0 warnings** | 21.75s |
| **Browser Matrix Suite** | `.venv\Scripts\pytest tests/test_browser_matrix.py -v` | **10 passed, 0 failed, 0 warnings** | 0.52s |
| **PowerShell Test Harness** | `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\test_setup_console.ps1` | **5/5 tests passed (AST, Ports, StopAll, CleanHistory, RunTests)** | ~60s |
| **Python Code Quality** | `.venv\Scripts\ruff check app tests` | **All checks passed (0 errors)** | <1s |
| **Frontend Type Checking** | `npx tsc --noEmit` | **0 errors** | ~3s |
| **PowerShell AST Validation**| `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_ps1_syntax.ps1` | **0 errors across all 6 scripts** | ~2s |

---

## 4. Invariants Verification

1. **Protected Folders Invariant:** All 5 protected user directories (`implementation_plan`, `PowerAutomateSolutions`, `Testing files`, `anticaptcha-plugin_v0.83`, `.agents`) exist, are intact, and are guarded against folder purge operations.
2. **Zero Warning Suppression:** `PytestUnraisableExceptionWarning` is unsuppressed in `pyproject.toml`.
3. **No Breaking Changes:** All API endpoints, Guidewire payload schemas, court scraper schemas, and date conversion logic (1899-12-30 base) remain strictly preserved.
4. **Persistent Setup Console:** `setup_local.ps1` remains fully interactive when executed without command-line switches.
