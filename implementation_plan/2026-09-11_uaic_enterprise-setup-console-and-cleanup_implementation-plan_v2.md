# Implementation Plan

**Implementation ID:**   IMP-2026-0911-006  
**Project:**             UAIC Claim & RPA Orchestrator  
**Module:**              Enterprise Setup Console (Options 1–9, [M]), Real Process Management, Data Cleanup Engine  
**Feature / Issue:**     Prompt 02 — Enterprise Setup Console (Options 1–9) & Data Cleanup  
**Document Type:**       Implementation Plan  
**Version:**             v2  
**Status:**              Approved by User (Prompt Pipeline Execution)  
**Created:**             2026-09-11  
**AI Agent:**            Antigravity (Advanced Agentic Coding)  
**Approval Status:**     Approved  
**Approved By:**         User  
**Approval Date:**       2026-09-11  
**AI Verification:**     Complete (100% Automated Testing Suite)  

---

## 1. Problem & Executive Summary

The user requested execution of the prompt pipeline, specifically:
`Approved all, Pls proceed and make everything funcation. Note: Always work for upgradtion/enhancement, don't delete existing things if that is working and even not working then fix that and make those working`

Following the prompt pipeline in `Prompt Processning.txt`, the next sequential milestone is **02 - ENTERPRISE SETUP CONSOLE (OPTIONS 1-9) & DATA CLEANUP** (`02_Enterprise_Setup_Console_and_Cleanup.md`).

### Gap Analysis from Diagnostic Runs:
1. **Docker Stop NativeCommandError in `setup_local.ps1`:**
   - In `setup_local.ps1` line 420, `docker stop uaic_maildev 2>$null | Out-Null` executes unconditionally when the Docker daemon is online.
   - When the `uaic_maildev` container does not exist, Docker returns exit code 1 and writes to stderr, which triggers a PowerShell `NativeCommandError` terminating exception under `$ErrorActionPreference = "Stop"`.
   - This caused `scripts/test_setup_console.ps1` Test 3/5 (`Stop All Services`) to fail with exit code 1.
2. **Bundled Chromium Inspection in Option [4]:**
   - Option [4] correctly skips downloading Playwright Chromium when host Google Chrome is selected, but needs to inspect and report whether bundled Playwright Chromium is already installed on the host and provide explicit instructions if testing on Chromium is desired.
3. **Data Retention & Cascade Integration for New Persistence Entities:**
   - Prompt 01 introduced `GuidewireActivity` and `FilteredOutCase` in `backend/app/models/guidewire.py`.
   - `backend/app/services/cleanup_service.py` must be upgraded to include these new entities in `calculate_cleanup_preview()` and `execute_enterprise_cleanup()`, ensuring that cleaning claims, guidewire activities, or court cases purges both tables cleanly and maintains relational integrity.

---

## 2. Proposed Changes

### Component 1: Enterprise Setup Console (`setup_local.ps1`)
#### [MODIFY] [setup_local.ps1](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/setup_local.ps1)
- In `Stop-AllServices`: Check if `uaic_maildev` exists via `docker ps -aq -f "name=^uaic_maildev$"` before calling `docker stop` or `docker rm`, wrapped in `try {} catch {}`.
- In `Test-BrowserAvailability`: Inspect `ms-playwright` folder in `%LOCALAPPDATA%` for installed `chromium-*` directories.
- In `Invoke-InstallDependencies`: Display whether bundled Chromium is detected and show full instructions for installing it (`playwright install chromium`).

### Component 2: Enterprise Data Cleanup Service (`cleanup_service.py`)
#### [MODIFY] [cleanup_service.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/services/cleanup_service.py)
- Import `GuidewireActivity` and `FilteredOutCase` from `app.models.guidewire`.
- In `calculate_cleanup_preview`:
  - When `guidewire_activities` is selected, count `GuidewireActivity` records.
  - When `court_cases` is selected, count `FilteredOutCase` records.
- In `execute_enterprise_cleanup`:
  - In transaction, delete `GuidewireActivity` records for targeted claim IDs or time range.
  - Delete `FilteredOutCase` records for targeted claim IDs or time range.
  - Include deleted counts in `records_deleted` response.

---

## 3. Verification Plan

### Automated Tests:
1. `powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\test_setup_console.ps1"`:
   - Must pass all 5/5 tests (AST syntax, port conflict scanner, stop all services, clean history, diagnostics runner) with exit code 0.
2. `pytest backend/tests/test_setup_console.py backend/tests/test_enterprise_cleanup.py backend/tests/test_guidewire_models.py -v`:
   - All 29 unit tests must pass.
3. `ruff check app tests` (0 errors).
4. `npx tsc --noEmit` (0 errors).
5. `powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"` (0 errors across 8 `.ps1` files).
