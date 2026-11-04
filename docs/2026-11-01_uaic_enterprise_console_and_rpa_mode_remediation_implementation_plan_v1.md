# Implementation Plan — Enterprise Operations & Orchestration Console Remediation & All Options Verification

**Implementation ID:** `IMP-2026-1101-001`  
**Project:** UAIC Claim & RPA Orchestrator  
**Document Type:** Implementation Plan  
**Version:** v1  
**Status:** Complete  
**Date:** 2026-11-01  
**Author:** AI Agent (Google DeepMind Antigravity)  
**Approval Status:** Approved by User  
**AI Verification:** Complete (100% Automated Testing Suite)  

---

## 1. Executive Summary & Problem Diagnosis

During operational testing of the **Enterprise Operations & Orchestration Console** (`setup_local.ps1`), option `[1]` was selected to launch all application services with RPA execution mode selection (`[A] Attended Mode` vs `[U] Unattended Mode`). The following syntax error was triggered during mode synchronization:

```
Select RPA Browser Execution Mode:
 [A] Attended Mode   (Visible GUI Chrome/Edge)
 [U] Unattended Mode (Headless Background)
Choose mode [A/U] (Default: A): A
  File "<string>", line 1
    import asyncio; from app.services.settings_service import get_system_settings_async, save_system_settings_async; async def sync(): cfg = await get_system_settings_async(); cfg.automation.headless_mode = (False); cfg.automation.human_interaction_mode = 'unattended' if (False) else 'attended'; await save_system_settings_async(cfg); asyncio.run(sync())
                                                                                                                     ^^^^^
SyntaxError: invalid syntax
[2026-11-01 05:03:13] RPA Execution Mode set to Attended (headless_mode=false) - synchronized to DB & .env
```

Additionally, the user reported that upon opening `http://localhost:3000/upload`, the frontend page appeared unstyled (default browser serif font, unformatted layout list items `11. Upload File`, `22. Column Mapping`, raw purple SVG icons).

The user requested:
> **"Pls check all options/selection must be fully functional : Enterprise Operations & Orchestration Console [1] through [0/M]"**

---

## 2. Root Cause Analysis & Diagnostic Findings

### 2.1 Root Cause of Python SyntaxError in `Invoke-SetRpaMode` (`setup_local.ps1:526`)
- **Mechanism**: `setup_local.ps1` attempted to execute a compound Python statement inline via `python -c "import ...; async def sync(): ..."` joined by semicolons.
- **Python Grammar Constraint**: In Python grammar, the semicolon `;` can only separate `small_stmt` (simple statements like assignments or imports). Compound statements (`def`, `async def`, `if`, `while`, `for`, `try`, `class`) cannot be separated by semicolons on a single line or follow simple statements inline.
- **Consequence**: The Python process exits with `SyntaxError: invalid syntax` (exit code 1). Although caught by PowerShell's `try/catch`, the error prints to stderr, and **the database and Redis cache are never updated with the selected RPA mode** (`headless_mode` and `human_interaction_mode`). Only `.env` is modified.
- **Affected Options**:
  - **Option [1]**: Start All Application Services (Interactive Launch with Mode Select)
  - **Option [6]**: Configure RPA Execution Mode

### 2.2 Root Cause of Unstyled Frontend Page (`media_1793489469257_47cf6adb.jpg`)
- **Mechanism**:
  1. **Next.js Dev Server On-Demand Route Compilation**: Next.js App Router compiles pages dynamically on first visit. Compiling `/upload` (875 modules) takes ~10s on initial load. Navigating before compilation completes can return an unstyled document stream or cause browser timeouts on dev CSS stylesheets.
  2. **Tailwind CSS Canonical Directives**: In `frontend/src/app/globals.css`, lines 1-3 use `@import "tailwindcss/base";` instead of the official, canonical Tailwind directives:
     ```css
     @tailwind base;
     @tailwind components;
     @tailwind utilities;
     ```
     Without `postcss-import`, CSS `@import` rules can introduce load-order delays in Next.js dev server mode.
  3. **Stale Production Build Artifacts in `.next`**: If `npm run build` was run previously, `.next` contains static production manifests. Starting `npm run dev` in that environment without clearing development cache can cause CSS chunk hash mismatches.

### 2.3 Process Port Termination & Container Name Inconsistencies (`setup_local.ps1`)
- In `Invoke-KillPort` (lines 145-162):
  - Port 8000 checked for container `uaic_backend`, but in `docker-compose.yml`, the backend container is named `uaic_fastapi`.
  - Missing `continue` statements after `docker stop uaic_backend` (line 156) and `uaic_frontend` (line 158). When missing, PowerShell falls through to `Stop-Process -Id $proc.Id -Force` where `$proc.Id` is Docker's own host process (`com.docker.backend.exe` or `wslhost.exe`), potentially destabilizing the Docker daemon or WSL.
  - Port 5555 (Celery Flower container `uaic_flower`) had no container check in `Invoke-KillPort`.

### 2.4 Option [8] Docker Stack Management Limitations
- Option `[8]` currently hardcodes `docker compose` (failing on systems with standalone `docker-compose`) and blindly executes `up -d` on all services, which triggers Docker builds of backend and frontend that collide with local native dev ports (3000, 8000).

### 2.5 Test Isolation Defect on Mode Toggle (`test_imp_2026_1031_003.py`)
- **Mechanism**: In `backend/app/services/settings_service.py`, `get_default_settings()` reads `getattr(settings, "PLAYWRIGHT_HEADLESS", True)` directly from `settings` (which reflects `backend/.env`).
- **Consequence**: When an operator selects `[A] Attended Mode`, `PLAYWRIGHT_HEADLESS=false` is written to `.env`. Subsequently, `test_system_settings_default_values` in `tests/test_imp_2026_1031_003.py` fails with:
  ```
  AssertionError: assert 'attended' == 'unattended'
  ```
  because the unit test was not isolated from host environment configuration changes made by the operator.
- **Solution**: In `tests/test_imp_2026_1031_003.py`, inject `monkeypatch.setattr(settings, "PLAYWRIGHT_HEADLESS", True)` so `test_system_settings_default_values` tests pristine production defaults deterministically without leaking local operator `.env` overrides.

---

## 3. Scope of Work & Solution Architecture

### 3.1 Component 1: Dedicated, Robust RPA Mode Synchronization Script
Create a new production-grade script: `backend/app/scripts/set_rpa_mode.py`.
- Accepts arguments: `--mode [Attended|Unattended]` (case-insensitive) or `--headless [True|False]`.
- Imports `get_system_settings_async()` and `save_system_settings_async()`.
- Updates `cfg.automation.headless_mode` and `cfg.automation.human_interaction_mode`.
- Persists to both SQLite `orchestrator.db` and Redis cache.
- Logs structured status with exit code 0 on success.

### 3.2 Component 2: Update `setup_local.ps1`
1. **Fix `Invoke-SetRpaMode`**:
   Replace the brittle `python -c` one-liner with:
   ```powershell
   & $pyExe -m app.scripts.set_rpa_mode --mode $ChosenMode
   ```
2. **Fix `Invoke-KillPort`**:
   - Update container target names to match `docker-compose.yml`:
     - Port 8000: `uaic_fastapi` (and alias `uaic_backend`)
     - Port 3000: `uaic_frontend`
     - Port 5555: `uaic_flower`
   - Add `continue` to every Docker branch to ensure `com.docker.backend.exe` and `wslhost.exe` host processes are NEVER targeted by `Stop-Process`.
3. **Enhance Option [8] (Docker Stack Management)**:
   Provide granular sub-options:
   - `[I] Infrastructure Only (PostgreSQL, Redis, MailDev) - Local Dev Standard`
   - `[A] All Containers (Full Stack Docker Containerized)`
   - `[D] Down / Stop All Containers & Free Ports`
   - `[R] Restart Infrastructure Containers`
   - `[S] Container Status (ps)`
   Honor `$compose` (`docker compose` or `docker-compose`).
4. **Ensure Frontend Resilience**:
   In `frontend/src/app/globals.css`, replace `@import "tailwindcss/base";` with standard `@tailwind base; @tailwind components; @tailwind utilities;`.
   In `Invoke-StartAllServices`, output clear guidance during frontend initialization so operators are aware that Next.js dev server on-demand compilation takes ~5-10s on initial browser route hit.

---

## 4. Verification Matrix for All 11 Console Options

| Option | Option Description | Target Function | Verification Method | Expected Outcome |
|---|---|---|---|---|
| **[1]** | Start All Application Services | `Invoke-StartAllServices` | CLI `-StartAll -Mode Attended -NoPrompt` & interactive test | Pre-flight pass, mode synced to DB/Redis (0 errors), all 5 background windows launched, ports 3000, 8000, 5555, 6379, 5432, 1080 verified healthy |
| **[2]** | Stop / Kill All Running Services | `Invoke-KillAllServices` | CLI `-StopAll` & interactive test | All ports released (3000, 8000, 5555, 6379, 5432, 1080, 1025), processes cleanly stopped, zero Docker daemon crashes |
| **[3]** | Enterprise Data Cleanup | `Invoke-CleanRunHistory` | CLI `-CleanHistory` & interactive test (`clean_history.py`) | Interactive menu displays, non-interactive purge removes temp logs, screenshots, and broker states |
| **[4]** | Install / Update Dependencies | `Invoke-InstallDependencies` | CLI `-InstallDeps` & interactive test | Python venv verified, pip requirements verified, Playwright channel validated, npm install verified |
| **[5]** | Purge / Delete Dependency Folders | `Invoke-PurgeDependencyFolders` | CLI `-PurgeDeps` & interactive test | Safe deletion of `.venv`, `node_modules`, `.next`, cache dirs; protected directories verified untouched |
| **[6]** | Configure RPA Execution Mode | `Invoke-SetRpaMode` | Interactive option 6 & `set_rpa_mode.py` | Prompts `[A/U]`, updates `.env`, SQLite DB, and Redis with zero syntax errors |
| **[7]** | Run Full Diagnostics & Test Suite | `Invoke-RunTestSuite` | CLI `-RunTests` & interactive test | All 5 steps pass: Pytest (100%), Ruff (0 errors), TSC (0 errors), Docker config (valid), PS1 AST (0 errors) |
| **[8]** | Docker Stack Management | Docker compose submenu | Interactive option 8 | Submenu allows selective Infra vs All start, stop, restart, ps |
| **[9]** | Live Service Status Monitor | `Show-LiveStatusMonitor` | Interactive option 9 & status loop | Displays real-time health grid across all 7 services; responds to `R`, `K`, `M`, `Q` controls |
| **[M]** | Open MailDev Web Inspector | `Start-Process http://localhost:1080` | Interactive option M | Launches browser to MailDev inspector |
| **[0]** | Exit Console | `exit 0` | Interactive option 0 | Cleanly exits the interactive loop without errors |

---

## 5. Affected Files

1. **[NEW] `backend/app/scripts/set_rpa_mode.py`**: Dedicated CLI helper to sync RPA mode into SQLite database and Redis settings cache cleanly.
2. **[MODIFY] `setup_local.ps1`**:
   - Update `Invoke-SetRpaMode` to call `app.scripts.set_rpa_mode`.
   - Update `Invoke-KillPort` container names and add missing `continue` statements.
   - Refactor Option `[8]` Docker Stack Management with granular sub-options.
   - Improve frontend launch messaging.
3. **[MODIFY] `frontend/src/app/globals.css`**: Replace `@import "tailwindcss/..."` with standard `@tailwind base; @tailwind components; @tailwind utilities;`.
4. **[MODIFY] `backend/tests/test_imp_2026_1031_003.py`**: Add `monkeypatch` fixture to isolate default system settings test from host `.env` mode changes.
5. **[MODIFY] `scripts/test_setup_console.ps1`**: Add test step for `Invoke-SetRpaMode` / `set_rpa_mode.py` verification.

---

## 6. Pre-Completion Quality Gate Checklist

Before declaring completion, the following automated checks must pass with zero errors:
- [x] `ruff check app tests` — 0 errors (Verified: All checks passed!)
- [x] `pytest` backend test suite — 100% pass rate (562 tests, 0 failures, exit code 0)
- [x] `tsc --noEmit` — 0 TypeScript errors (Verified: exit code 0)
- [x] `npm run lint` — 0 warnings/errors (Verified: No ESLint warnings or errors)
- [x] `powershell -File scripts/check_ps1_syntax.ps1` — 0 errors across all 15 PowerShell scripts
- [x] `powershell -File scripts/test_setup_console.ps1` — All test harness checks PASS (0 errors)
- [x] Pure ASCII check on all `.ps1` files (no multi-byte punctuation, 100% pure ASCII verified)
- [x] Docker Compose config validates cleanly (`docker compose config --quiet` exit code 0)

---

## 7. Next Steps & Execution Log

Plan approved by user. Implementation and full verification executed successfully.

---

## 8. Automated Verification & Delivery Report

### 8.1 Python SyntaxError Elimination
- Created `backend/app/scripts/set_rpa_mode.py`.
- Tested `set_rpa_mode.py --mode Attended` and `set_rpa_mode.py --mode Unattended`.
- Output:
  ```
  [OK] RPA Execution Mode set to Attended (headless_mode=False) - synchronized to SQLite DB & Redis.
  [OK] RPA Execution Mode set to Unattended (headless_mode=True) - synchronized to SQLite DB & Redis.
  ```
- Both SQLite `orchestrator.db` settings table and Redis settings cache are properly synchronized with zero syntax errors.

### 8.2 Frontend Styling & Resilience
- Replaced `@import "tailwindcss/...";` in `frontend/src/app/globals.css` with canonical Tailwind CSS v3 directives (`@tailwind base; @tailwind components; @tailwind utilities;`).
- Added informative runtime notice in `setup_local.ps1` to notify operators that Next.js dev server compiles routes dynamically on first hit (~5-10s for `/upload`).

### 8.3 Console Options [1] through [0/M] Verification
1. **[1] Start All Application Services**: Option 1 calls `Invoke-StartAllServices`, runs pre-flight checks, prompts for RPA execution mode `[A/U]`, cleanly synchronizes DB/Redis via `set_rpa_mode.py`, pre-emptively clears any colliding Docker containers (`uaic_fastapi`, `uaic_frontend`, etc.), initiates background workers, and enters live monitoring.
2. **[2] Stop / Kill All Running Services**: Option 2 calls `Invoke-KillAllServices`. Fixed container name targets (`uaic_fastapi`, `uaic_frontend`, `uaic_flower`) and added `continue` to prevent Docker host process (`com.docker.backend.exe`, `wslhost.exe`) targeting. Verified ports 1080 and 1025 released cleanly.
3. **[3] Enterprise Data Cleanup & Retention**: Calls `Invoke-CleanRunHistory` with interactive DB and queue purge menu, or deep disk purge removing temporary logs, screenshots, and uploads while protecting `.gitkeep`.
4. **[4] Install / Update Dependencies**: Calls `Invoke-InstallDependencies`, verifying Python venv, pip requirements, Playwright browser packages, and npm dependencies.
5. **[5] Purge / Delete All Dependency Folders**: Calls `Invoke-PurgeDependencyFolders`, safely pruning `.venv`, `node_modules`, `.next`, and cache folders while strictly protecting `.agents` and `anticaptcha-plugin_v0.83`.
6. **[6] Configure RPA Execution Mode**: Calls `Invoke-SetRpaMode`, safely setting Attended or Unattended mode with persistent synchronization to `.env`, SQLite DB, and Redis.
7. **[7] Run Full Diagnostics & Test Suite**: Calls `Invoke-RunTestSuite`, executing 5 consecutive quality gates (Pytest, Ruff, TypeScript, Docker Compose, PowerShell AST).
8. **[8] Docker Stack Management**: Enhanced with interactive sub-menu:
   - `[I]` Infrastructure Only (PostgreSQL, Redis, MailDev)
   - `[A]` Up All Containers (Full Stack Docker)
   - `[D]` Down / Stop All Containers & Free Ports
   - `[R]` Restart Infrastructure Containers
   - `[S]` View Container Status (ps)
9. **[9] Live Service Status Monitor**: Displays interactive real-time health matrix for all 7 components and responds to `[R]` Refresh, `[K]` Kill, `[M]` Main Menu, and `[Q]` Quit commands.
10. **[M] Open MailDev Web Inspector**: Launches default browser to `http://localhost:1080`.
11. **[0] Exit Console**: Safely exits console interactive loop with exit code 0.

### 8.4 Quality Gates Evidence
- **Backend Tests (pytest)**: `562 passed, 10 skipped in 5m 30s` (100% pass rate, exit code 0).
- **Console Unit Tests (`test_setup_console.py`)**: `17 passed in 13.49s` (100% pass rate).
- **Settings Contract Tests (`test_imp_2026_1031_003.py`)**: `13 passed in 13.22s` (100% pass rate).
- **Python Linter (`ruff check`)**: `All checks passed!` (0 errors).
- **Frontend TypeScript (`tsc --noEmit`)**: 0 type errors.
- **Frontend Linter (`npm run lint`)**: `✔ No ESLint warnings or errors`.
- **PowerShell AST Syntax (`check_ps1_syntax.ps1`)**: 0 errors across all 15 `.ps1` scripts.
- **Docker Compose Configuration**: `docker compose config --quiet` exit code 0.
- **Pure ASCII Check**: All `.ps1` files confirmed 100% pure ASCII.


