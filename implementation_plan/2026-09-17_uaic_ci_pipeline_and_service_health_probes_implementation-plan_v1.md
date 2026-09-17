# Implementation Plan: Fix GitHub CI Pipeline & Setup Console Service Health Probes

**Implementation ID:** `IMP-2026-0917-004`  
**Document Type:** Implementation Plan  
**Version:** v1  
**Date:** 2026-09-17  
**Status:** Pending User Approval  
**Target Files:**
- `setup_local.ps1`
- `backend/tests/test_settings_alignment.py`
- `backend/tests/test_browser_manager.py`
- `backend/tests/test_browser_matrix.py`
- `scripts/verify_monitor_probe.ps1`

---

## 1. Executive Summary & Problem Diagnosis

### Issue 1: GitHub CI Workflow Failure (Universal CI/CD Pipeline)
The user received an email alert from GitHub:
- **Repository:** `priyer-damco/uaic-rpa-orchestrator`
- **Workflow:** `Universal CI/CD Pipeline`
- **Commit:** `main (c54975e)`
- **Failure:** `Backend CI (Python 3.14 + FastAPI + Pytest) Failed in 4 minutes and 17 seconds (2 annotations)`

Inspection of the remote GitHub Actions logs (`gh run view 35162277329 --log-failed`) revealed 4 test failures:
1. `tests/test_settings_alignment.py::test_default_windows_chrome_detection`:
   Failed because on Ubuntu Linux (`ubuntu-latest`), `Path(chrome_bin).name` for Windows path `C:\Program Files\...` does not parse backslashes (POSIX `Path` treats `\` as normal character), resulting in `'c:\program files\google\chrome\application\chrome.exe' != 'chrome.exe'`, and `Path(chrome_bin).exists()` is False on Linux.
2. `tests/test_browser_manager.py::test_chrome_profile_seeding_and_args`:
   Failed with `RuntimeError: Google Chrome executable (chrome.exe) was not found on this system`. This unit test mocked Playwright but omitted mocking `find_chrome_executable`, so it failed on machines without Google Chrome installed.
3. `tests/test_browser_matrix.py::test_live_chrome_attended_integration` & `test_live_chrome_headless_integration`:
   Failed because these are live browser integration tests expecting a local Google Chrome installation, which is not installed on Ubuntu Linux CI runners.

### Issue 2: Live Service Health Monitor Displaying `[RUNNING]` instead of `[HEALTHY]`
When viewing `[9] Live Service Status Monitor` in `setup_local.ps1`:
```
 [HEALTHY] Frontend Web Application    (Port 3000 - HTTP 200)
 [RUNNING] FastAPI Backend & API       (Port 8000 - port open, HTTP initializing)
 [RUNNING] Celery Flower Monitor       (Port 5555 - port open, HTTP initializing)
 [HEALTHY] MailDev Web Inspector       (Port 1080 - HTTP 200)
 [RUNNING] MailDev SMTP Server         (Port 1025)
 [RUNNING] Redis Queue Broker          (Port 6379)
 [RUNNING] PostgreSQL Database         (Port 5432)
```
- **TCP Services (1025, 6379, 5432):** In `setup_local.ps1` line 599, when `$HttpUrl -eq ""`, the code unconditionally printed `[RUNNING]`. It never performed a protocol health probe, so active TCP services could never display `[HEALTHY]`.
- **FastAPI Backend (8000):** Only probed `http://localhost:8000/api/v1/health` with a tight 2-second timeout (`TimeoutSec 2`). If DB pool initialization takes 2.5s, the probe times out and falls back to `[RUNNING] (port open, HTTP initializing)`.
- **Celery Flower (5555):** Flower issues redirects (302) and takes 3–5 seconds to initialize; without redirect tolerance or fallback to root `/`, it fell back to `[RUNNING]`.

---

## 2. Proposed Changes

### Part 1: Fix GitHub Actions Backend CI Tests

#### 1. `backend/tests/test_settings_alignment.py`
- In `test_default_windows_chrome_detection`:
  Use `PureWindowsPath(chrome_bin).name.lower() == "chrome.exe"` to handle both Windows and POSIX path representations cross-platform. Only assert `Path(chrome_bin).exists()` if running on `win32` with Chrome installed.

#### 2. `backend/tests/test_browser_manager.py`
- In `test_chrome_profile_seeding_and_args`:
  Add `mocker.patch.object(ChromeSession, "find_chrome_executable", return_value=mock_source / "chrome.exe")` so unit testing of profile seeding and args runs hermetically on any platform without requiring local Chrome.

#### 3. `backend/tests/test_browser_matrix.py`
- In `test_live_chrome_attended_integration` and `test_live_chrome_headless_integration`:
  Add `@pytest.mark.skipif(not ChromeSession.find_chrome_executable(None), reason="Google Chrome executable not installed on this system — skipping live integration test")`. On developer Windows workstations with Chrome installed, the live test runs; on Linux CI runners without Chrome, it skips cleanly just like the Redis and MailDev live tests.

---

### Part 2: Setup Console Service Health Probes (`setup_local.ps1`)

#### 1. TCP Protocol Probes in `Invoke-CheckServiceHealth`
Enhance `Invoke-CheckServiceHealth` to perform actual protocol handshakes for TCP services:
- **Redis (Port 6379)**: Send `*1\r\n$4\r\nPING\r\n` and read response. If it contains `+PONG`, display `[HEALTHY] Redis Queue Broker (Port 6379 - PONG)`.
- **MailDev SMTP (Port 1025)**: Read SMTP greeting banner. If it starts with `220`, send `QUIT\r\n`, display `[HEALTHY] MailDev SMTP Server (Port 1025 - Ready)`.
- **PostgreSQL (Port 5432)**: Perform TCP socket connection. If connection succeeds, display `[HEALTHY] PostgreSQL Database (Port 5432 - Ready)`.

#### 2. Robust HTTP Probes for FastAPI & Flower
- Increase `TimeoutSec` from 2s to 3s.
- For **FastAPI (8000)**: Probe `http://localhost:8000/api/v1/health`; if that times out or returns 503 during startup, probe `http://localhost:8000/` or `http://localhost:8000/docs`. If any return 200–399, display `[HEALTHY] FastAPI Backend & API (Port 8000 - HTTP 200)`.
- For **Celery Flower (5555)**: Probe `http://localhost:5555/` with redirect allowance. If status is 200–399, display `[HEALTHY] Celery Flower Monitor (Port 5555 - HTTP 200)`.

#### 3. Monitor Header Legend
- Update legend in `Show-LiveStatusMonitor`:
  `[HEALTHY]=Active & Verified  [RUNNING]=Port open  [STOPPED]=Offline`

---

## 3. Verification Plan

### Automated Tests
1. **Run Full Backend Pytest Suite locally**:
   ```bash
   cd backend; .venv\Scripts\pytest -q tests\test_settings_alignment.py tests\test_browser_manager.py tests\test_browser_matrix.py
   ```
   (Verify 100% pass rate on all 3 target test files).
2. **Run Full PowerShell Syntax Check**:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_ps1_syntax.ps1
   ```
   (0 syntax errors).
3. **Verify Health Probes in Console**:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_monitor_probe.ps1
   ```
   (Verify that active services report `[HEALTHY]` with protocol confirmation).
4. **Push to GitHub and verify GitHub Actions CI**:
   Verify that GitHub Actions `Universal CI/CD Pipeline` turns green.
