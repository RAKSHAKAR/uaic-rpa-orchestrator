# Implementation Record

**Implementation ID:**   IMP-2026-0909-001  
**Project:**             UAIC Claim & RPA Orchestrator  
**Module:**              Setup Console, Test Suite, Browser Automation  
**Feature / Issue:**     Enterprise Setup Console Audit & Finalization (Options 1-9 + Data Cleanup)  
**Document Type:**       Implementation Plan  
**Version:**             v1  
**Status:**              Awaiting Approval  
**Created:**             2026-09-09  
**AI Agent:**            Antigravity (Claude Sonnet 4.6 Thinking)  
**Approval Status:**     Pending  

---

## Problem / Request

Full audit and finalization of the Enterprise Setup Console (`setup_local.ps1`) and supporting Python scripts. All 9 options + [M] must be production-grade with real process management, not blind executions.

---

## Current State — Audited Sep 9, 2026

### COMPLETE (No Changes Needed)

| Option | Function | Status |
|--------|----------|--------|
| [2] Stop All Services | Kills 3000, 8000, 5555, 1080, 1025, 6379, 5432 + Celery + Docker stop | DONE |
| [3] Enterprise Cleanup | 18 categories, 10 time scopes, dry-run, cascade delete, reconciliation | DONE |
| [5] Purge Folders | .venv, node_modules, .next, caches + protected dirs | DONE |
| [6] RPA Mode | .env + API sync to Redis/DB | DONE |
| [8] Docker | Up/Down/Restart/Status submenu | DONE |
| [M] MailDev | Opens browser to localhost:1080 | DONE |
| [0] Exit | Clean exit | DONE |

### GAPS REQUIRING FIXES

#### GAP-1 (CRITICAL): Option [4] — Playwright Chromium installed unconditionally

Current code (lines 192-193 of setup_local.ps1):
```powershell
Write-LogMessage "Installing Playwright Chromium browser distribution..." "INFO"
& $pyExe -m playwright install chromium
```
The Chrome detection below (lines 196-204) is purely informational — it never prevents the Playwright Chromium download. This violates the user requirement: "DO NOT install bundled Chromium if the system Google Chrome is selected for RPA."

Also: Edge browser (`playwright install msedge`) is never offered.

#### GAP-2 (MEDIUM): Option [7] — PytestUnraisableExceptionWarning suppressed, not fixed

pyproject.toml line 64:
```toml
"ignore::pytest.PytestUnraisableExceptionWarning",
```
User requirement: "Do not hide PytestUnraisableExceptionWarnings. Fix underlying issues."

The `clean_async_transports` gc.collect() fixture + requires_redis/requires_maildev skip logic
should already prevent these warnings. The suppression was added as a catch-all but never
verified if it's still needed. Must be removed and tested.

#### GAP-3 (MEDIUM): Option [7] — Missing PS1 syntax check step

`Invoke-RunTestSuite` runs only 4 steps: Pytest, Ruff, TypeScript, Docker Compose.
It never runs `scripts\check_ps1_syntax.ps1`. The user's own test commands in AGENTS.md
explicitly include PS1 syntax check.

#### GAP-4 (MEDIUM): Option [9] — Port-only checks, not real HTTP health checks

`Invoke-CheckPortStatus` only uses `Get-NetTCPConnection -State Listen`.
Port open does NOT mean the service is responding. A FastAPI app in startup or crash loop
would show as [RUNNING]. User requirement: "real health checks... for Frontend, Backend, 
Redis, Celery, Flower, and MailDev."

#### GAP-5 (MINOR): Option [1] — No pre-start conflict report

`Invoke-StartAllServices` calls `Invoke-KillAllServices -Quiet` which silently kills
conflicting processes without reporting which ones were in use. User requirement: "Check
port conflicts before starting."

---

## Proposed Changes

### [MODIFY] `setup_local.ps1`

#### Change 1 — `Invoke-InstallDependencies` (Option [4]): Smart browser selection

Replace unconditional `playwright install chromium` with an interactive browser selector:

```
Select browser for RPA automation:
  [1] Playwright Bundled Chromium  (download, recommended for Unattended/headless)
  [2] System Google Chrome         (no download, use existing Chrome install)
  [3] Microsoft Edge               (download Edge WebDriver via Playwright)
```

Logic:
- Option [2]: Verify Chrome exists at standard paths. If found, write PLAYWRIGHT_CHANNEL=chrome 
  to backend/.env. Do NOT run playwright install. Show success.
- Option [3]: Run `playwright install msedge`, write PLAYWRIGHT_CHANNEL=msedge to .env.
- Option [1] (default): Run `playwright install chromium`, clear PLAYWRIGHT_CHANNEL in .env.

Also: When PLAYWRIGHT_CHANNEL is already set in .env, pre-select the matching option.

#### Change 2 — `Invoke-StartAllServices` (Option [1]): Pre-start conflict report

Before calling `Invoke-KillAllServices -Quiet`, scan and report conflicts:
```powershell
$conflictPorts = @(3000, 8000, 5555, 1080, 1025, 6379, 5432)
foreach ($p in $conflictPorts) {
    $conn = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction Ignore
    if ($conn) {
        $proc = Get-Process -Id $conn[0].OwningProcess -ErrorAction Ignore
        Write-LogMessage "  Port $p occupied by: $($proc.Name) (PID: $($proc.Id))" "WARNING" "DarkYellow"
    }
}
```

#### Change 3 — `Invoke-RunTestSuite` (Option [7]): Add PS1 syntax check

Add step 5 after Docker Compose check:
```powershell
Write-LogMessage "5/5 Running PowerShell Syntax Check..." "INFO"
$ps1CheckScript = Join-Path $rootDir "scripts\check_ps1_syntax.ps1"
if (Test-Path $ps1CheckScript) {
    powershell -NoProfile -ExecutionPolicy Bypass -File $ps1CheckScript
    if ($LASTEXITCODE -eq 0) {
        Write-LogMessage "PowerShell Syntax: 0 ERRORS." "SUCCESS"
    } else {
        Write-LogMessage "PowerShell Syntax: Errors detected." "ERROR"
    }
} else {
    Write-LogMessage "PowerShell Syntax: scripts\check_ps1_syntax.ps1 not found. Skipped." "WARNING"
}
```

Also update the count header from "4/4" to "4/5" for Docker step.

#### Change 4 — `Show-LiveStatusMonitor` (Option [9]): Real HTTP health checks

Replace `Invoke-CheckPortStatus` with `Invoke-CheckServiceHealth`:
- HTTP services (3000, 8000, 5555, 1080): Attempt `Invoke-WebRequest -TimeoutSec 2`
  - StatusCode 200-299 → `[HEALTHY]` (green)
  - Port open but HTTP fails → `[RUNNING]` (yellow) 
  - Port closed → `[STOPPED]` (dark gray)
- TCP-only services (1025, 6379, 5432): Port check only (binary protocols)
  - Port open → `[RUNNING]` (green)
  - Port closed → `[STOPPED]` (dark gray)

Health check URLs:
- Port 3000: `http://localhost:3000` (Next.js)
- Port 8000: `http://localhost:8000/api/v1/health` (FastAPI health endpoint)
- Port 5555: `http://localhost:5555` (Flower)
- Port 1080: `http://localhost:1080` (MailDev web UI)

---

### [MODIFY] `backend/pyproject.toml`

#### Change 5 — Remove PytestUnraisableExceptionWarning suppression

```diff
 filterwarnings = [
-    "ignore::pytest.PytestUnraisableExceptionWarning",
     "ignore::pytest.PytestUnhandledThreadExceptionWarning",
     "ignore::ResourceWarning",
 ]
```

If removing this filter causes pytest failures, the root cause must be fixed (proper
aiosqlite engine disposal in test fixtures), NOT re-suppressed.

---

## Testing Plan

| Test | Command | Expected |
|------|---------|----------|
| Pytest (no suppression) | `.venv\Scripts\python.exe -m pytest --tb=short -q` | Pass, 0 warnings |
| Ruff | `.venv\Scripts\ruff check app tests` | 0 errors |
| TypeScript | `npx tsc --noEmit` | 0 errors |
| PS1 syntax | `powershell -File scripts\check_ps1_syntax.ps1` | 0 errors |
| Option [4] Chrome test | Interactive run, select [2] | No playwright install, PLAYWRIGHT_CHANNEL=chrome |
| Option [7] full run | From console | 5 steps including PS1 check |
| Option [9] services up | From console | [HEALTHY] shown for HTTP services |
| Option [1] with conflict | Port 8000 in use | Conflict reported before kill |

---

## Risks

| Risk | Mitigation |
|------|-----------|
| Removing warning suppression reveals real failures | Run pytest without filter first (separate step), fix root cause if needed |
| Invoke-WebRequest slow in Option [9] | TimeoutSec 2 per check; total max overhead ~8s for 4 HTTP checks |
| Chrome path detection misses non-standard installs | Add registry query fallback |

---

## Rollback

- Changes are in `setup_local.ps1` and `pyproject.toml` only
- Both are version-controlled; `git checkout` restores in seconds
- No DB or schema changes

---

## Acceptance Criteria

- [ ] Option [4] does NOT run `playwright install chromium` when user selects system Chrome
- [ ] Option [4] supports Chromium / Chrome / Edge selection
- [ ] Option [7] runs 5 steps including PS1 syntax check
- [ ] `pyproject.toml` no longer suppresses `PytestUnraisableExceptionWarning`
- [ ] Pytest suite passes with 0 warnings (verified without suppression)
- [ ] Option [9] shows [HEALTHY]/[RUNNING]/[STOPPED] with real HTTP probing
- [ ] Option [1] reports port conflicts before clearing them

---

**No application code has been modified yet.**
**Awaiting user approval before any implementation.**
