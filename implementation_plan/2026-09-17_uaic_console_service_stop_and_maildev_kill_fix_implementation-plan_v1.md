# Implementation Plan: Fix Service Stop & MailDev Kill in Setup Console

**Implementation ID:** `IMP-2026-0917-003`  
**Document Type:** Implementation Plan  
**Version:** v1  
**Date:** 2026-09-17  
**Status:** Pending User Approval  
**Target Files:**
- `setup_local.ps1`
- `scripts/test_setup_console.ps1`

---

## 1. Executive Summary & Root Cause Analysis

### User Problem
When executing Option `[2] Stop / Kill All Running Services` in `setup_local.ps1`, the console reports:
```
[2026-09-17 04:48:24] Stopping all services, killing processes, and clearing ports...
[2026-09-17 04:48:37] All services stopped and infrastructure purged.
Press Enter to return...:
```
However, upon inspecting `[9] Live Service Status Monitor` (or pressing `[K] Stop Services` inside the monitor), **MailDev Web Inspector (Port 1080)** continues to be reported as:
```
 [RUNNING] MailDev Web Inspector       (Port 1080 - port open, HTTP initializing)
```
even though the MailDev container is actually stopped and offline. Furthermore, pressing `[K]` inside the monitor appears not to resolve the status.

### Root Cause Diagnosis

1. **False Positive Port Detection via Unfiltered TCP Connection Query (`Invoke-CheckServiceHealth`)**:
   In `setup_local.ps1` line 537:
   ```powershell
   if (Get-NetTCPConnection -LocalPort $Port -ErrorAction Ignore) { $portOpen = $true }
   ```
   `Get-NetTCPConnection` without `-State Listen` matches **any** TCP connection record involving local port 1080. When a browser visits `http://localhost:1080` (e.g. via Option `[M]`) or when previous HTTP health checks connect, terminating the MailDev container places the socket into `TIME_WAIT` or `CLOSE_WAIT` (RFC 793 standard 2MSL duration, 30–120 seconds in Windows).
   - Because `Get-NetTCPConnection -LocalPort 1080` finds this `TIME_WAIT` record, it sets `$portOpen = $true`.
   - Next, lines 548–558 trigger `Invoke-WebRequest -Uri "http://localhost:1080"`.
   - Because the server is actually stopped, connection is refused and throws an exception caught by `catch {}`.
   - In `catch {}`, line 557 outputs:
     `[RUNNING] MailDev Web Inspector (Port 1080 - port open, HTTP initializing)`!
   - Making that failed HTTP request in turn creates another closed socket record, perpetuating the false positive cycle.

2. **Docker Host Proxy Process Filter Bypass (`Invoke-KillPort`)**:
   In `setup_local.ps1` lines 139–141:
   ```powershell
   if ($proc.Name -match "^(wsl|wslhost|docker|com\.docker)" -or $proc.ProcessName -match "^(wsl|wslhost|docker|com\.docker)") {
       continue
   }
   ```
   When Docker Desktop forwards port 1080, 1025, 5432, or 6379, the host-side listening process is `docker-proxy.exe` or `com.docker.backend.exe`. `Invoke-KillPort` explicitly skipped them. If a container was left running, `Invoke-KillPort` did not terminate it.

3. **MailDev Port Verification Check Also Checked TIME_WAIT (`Invoke-KillAllServices`)**:
   In `setup_local.ps1` lines 424–428:
   ```powershell
   if ((Get-NetTCPConnection -LocalPort 1080 -ErrorAction SilentlyContinue) -or (Get-NetTCPConnection -LocalPort 1025 -ErrorAction SilentlyContinue)) {
       $maildevReleased = $false
   }
   ```
   Because `-State Listen` was omitted here too, `$maildevReleased` was falsely marked as `$false`, suppressing the green release confirmation message.

4. **Port Conflict Check False Alarms (`Invoke-CheckPortConflicts`)**:
   In `setup_local.ps1` line 154:
   ```powershell
   $conns = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
   ```
   Checking without `-State Listen` causes `Invoke-CheckPortConflicts` to report false conflict warnings for recently closed ports.

5. **Slow Docker Teardown Using `--rmi local` on Every Stop**:
   In `setup_local.ps1` line 438–439:
   `docker compose down --volumes --rmi local --remove-orphans` attempts to remove local Docker images every time services are stopped, which is slow, risky, and causes hangs or container-stop timeouts.

---

## 2. Proposed Changes & Enhancements

### Component: Setup & Operations Launcher (`setup_local.ps1`)

#### 1. Bulletproof Service Health Detection (`Invoke-CheckServiceHealth`)
- Change port detection to check **strictly for `Listen` state**:
  ```powershell
  $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
  ```
- Add a fast non-blocking TCP socket connection fallback (`TcpClient.BeginConnect`) with a 200ms timeout for non-elevated or restricted environments.
- In the HTTP probe logic:
  - If the port is open and `Invoke-WebRequest` succeeds (status 200–399), mark `[HEALTHY]`.
  - If `Invoke-WebRequest` fails with a connection error (e.g., connection refused), re-verify if the port is still in `Listen` state. If not, report `[STOPPED]`.
  - Only if the port is verified actively `Listen`ing but HTTP probe returns an initializing status, display `[RUNNING] ... (port open, HTTP initializing)`.

#### 2. Enhanced Port Killer (`Invoke-KillPort`)
- Query listeners with `-State Listen`.
- If the listener's owning process is Docker or WSL (`docker-proxy`, `wslhost`, `com.docker`):
  - Directly stop and remove the associated container:
    - Port 1080 or 1025: `docker stop -t 1 uaic_maildev; docker rm -f uaic_maildev`
    - Port 5432: `docker stop -t 1 uaic_postgres`
    - Port 6379: `docker stop -t 1 uaic_redis`
- For any native host process (Python, Node, MailDev CLI), terminate forcefully with `Stop-Process -Id $proc.Id -Force`.

#### 3. Deterministic & Fast Service Teardown (`Invoke-KillAllServices`)
- Unconditionally stop all UAIC containers via fast 1-second timeout:
  `docker stop -t 1 uaic_maildev uaic_postgres uaic_redis uaic_fastapi uaic_celery_worker uaic_celery_beat uaic_frontend 2>$null`
  `docker rm -f uaic_maildev uaic_postgres uaic_redis uaic_fastapi uaic_celery_worker uaic_celery_beat uaic_frontend 2>$null`
- Use clean `docker compose down --remove-orphans` without `--rmi local` (preserving images so starts are instantaneous).
- Update MailDev release verification check to query `-State Listen`.
- Ensure clean port release feedback is printed.

#### 4. Clean Port Conflict Scanner (`Invoke-CheckPortConflicts`)
- Update `Get-NetTCPConnection` to query `-State Listen` so `TIME_WAIT` sockets do not cause false conflict warnings.

#### 5. Enhanced Key `[K]` Handler in Monitor Loop
- In `Show-EnterpriseMenu` (Options `1` and `9`), when `[kK]` is pressed:
  - Print a clear progress message: `Stopping all services and clearing ports...`
  - Execute `Invoke-KillAllServices -Quiet`
  - Wait 1.5 seconds for socket tables to settle
  - Immediately re-render the monitor displaying all services as `[STOPPED]`.

---

## 3. Verification Plan

### Automated Tests
1. **PowerShell AST Syntax Check**:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"
   ```
   (Must pass with 0 errors across all scripts).
2. **Setup Console Test Harness**:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\test_setup_console.ps1"
   ```
   (Must pass AST Syntax, Port Conflict Scanner, and Stop All Services tests).
3. **Backend Pytest Suite**:
   ```powershell
   cd backend; .venv\Scripts\pytest -q tests\test_setup_console.py
   ```
   (Must pass 100% of tests).

### Manual / CLI Verification
1. Run `setup_local.ps1 -CheckPorts` to verify 0 false-positive conflicts.
2. Run `Invoke-CheckServiceHealth` across ports 3000, 8000, 5555, 1080, 1025, 6379, 5432 to verify that every offline service correctly displays `[STOPPED]`.
3. Test key `[K]` in `Show-LiveStatusMonitor` to ensure clean transition to `[STOPPED]`.
