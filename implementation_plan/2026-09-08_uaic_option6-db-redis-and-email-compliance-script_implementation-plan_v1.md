# Implementation Plan: Option [6] DB/Redis Persistence + find_uaic_emails.py Compliance Script

**Implementation ID:** `IMP-2026-0908-001`  
**Date:** September 8, 2026  
**Status:** `READY_FOR_CONFIRMATION`  
**Author:** DeepMind Antigravity AI  
**Reference Gap Analysis:** [`2026-09-08_uaic_setup-console-honest-gap-analysis_v1.md`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/implementation_plan/2026-09-08_uaic_setup-console-honest-gap-analysis_v1.md)  
**Reference Prompt:** `implementation_plan/ChatGPT_Prompt/Mandatory Task Completion, Error Resolution, Skills & Technology Documentation Requirements.md`

> [!IMPORTANT]
> **GOVERNANCE NOTICE**: Per AGENTS.md — NO APPROVAL = NO IMPLEMENTATION.
> This plan must be explicitly approved by the user before any code changes are made.

---

## 1. Executive Summary

This plan closes the **two remaining gaps** from the approved `IMP-2026-0906-003` plan that were
identified in the honest gap analysis (`DOC-2026-0908-001-GAP`):

| Gap | Approved Plan Ref | Status Before This Plan |
|-----|------------------|------------------------|
| **B1** — Option [6] RPA Mode only persists to `.env`; does NOT sync to DB/Redis | Plan §2.3 | ❌ Partial |
| **B2** — `find_uaic_emails.py` compliance script does not exist | Plan §3.1 Step 6 | ❌ Missing |

Both items are explicitly required by the approved Sep 6 plan and the ChatGPT Prompt
"Mandatory Task Completion" requirements (Section 1, Rule 2 and Rule 6).

---

## 2. Gap B1 — Option [6] DB/Redis Persistence

### 2.1 Diagnosis

**Current behavior** (`setup_local.ps1` lines 414–451):
```powershell
# Invoke-SetRpaMode currently only:
Set-Content -Path $envFile ...   # writes PLAYWRIGHT_HEADLESS to backend/.env
$env:PLAYWRIGHT_HEADLESS = ...   # sets the PowerShell process env var
```

**Why this is insufficient:**  
The Celery workers and FastAPI backend read `headless_mode` from `SystemSettings` at startup
(loaded from Redis key `uaic:system:settings:v4` via `get_system_settings_async()`). 
If a worker is already running, changing `.env` has **zero effect** on that worker — it only
takes effect on next restart. The proper persistence channel is:

```
POST /api/v1/settings  →  save_system_settings_async()  →  Redis key uaic:system:settings:v4
```

**Confirmed from codebase audit:**
- `backend/app/schemas/settings.py` line 49: `headless_mode: bool = Field(default=False, ...)`
- `backend/app/services/settings_service.py` line 181: `save_system_settings_async()` writes `SystemSettings` to Redis key `uaic:system:settings:v4`
- `backend/app/api/v1/endpoints/settings.py` line 54-60: `POST /api/v1/settings` calls `save_system_settings_async(payload)`

### 2.2 Proposed Change — setup_local.ps1

Add a **best-effort API sync** after the `.env` update in `Invoke-SetRpaMode`.
The API call is wrapped in a try/catch so that if the backend is not running (e.g. during
initial startup before services launch), it fails gracefully with a warning rather than
blocking the user.

**Logic:**
1. Update `.env` as today (unchanged)
2. Set PowerShell env var as today (unchanged)
3. **NEW**: Attempt `GET /api/v1/settings` to fetch current settings object
4. **NEW**: Patch `headless_mode` field and `POST /api/v1/settings` with the updated object
5. On success: log "RPA mode synced to API, Redis, and DB"
6. On failure (backend offline): log "Note: Backend not running — .env updated. Mode will sync on next startup."

**File to modify:** [`setup_local.ps1`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/setup_local.ps1)  
**Function:** `Invoke-SetRpaMode` (lines 414–451)  
**Change size:** ~15 lines added after line 449

### 2.3 Why This Approach (Not a Direct Redis Write)

The PowerShell script **must not** write directly to Redis — that would bypass the `SystemSettings`
schema, validation, and audit trail. The correct and safe pattern is to call the existing
`POST /api/v1/settings` API endpoint which:
- Validates the full settings object via Pydantic
- Writes to Redis atomically
- Preserves all other settings fields unchanged
- Triggers the audit log event

---

## 3. Gap B2 — find_uaic_emails.py Compliance Script

### 3.1 Diagnosis

The approved Sep 5 plan (`IMP-2026-0905-004`) verification step explicitly states:
> "Run `find_uaic_emails.py` (0 `@uaic.com` occurrences)"

This script does not exist. We have already confirmed (via `grep_search`) that **0 `@uaic.com`
occurrences** exist in the codebase today — but the verification step cannot be reproducibly run
by the user without the script.

### 3.2 What the Script Must Do

The script scans all Python (`.py`), TypeScript (`.ts`, `.tsx`), PowerShell (`.ps1`),
and configuration files for hardcoded `@uaic.com` email addresses. These are forbidden
because:
- `@uaic.com` is a fictional test domain that must never appear in production code
- All email fields must use configurable values from `SystemSettings` or env vars

**Output format:**
```
Scanning codebase for @uaic.com occurrences...
Checked 247 files across backend/, frontend/, scripts/

RESULT: 0 occurrences found — CLEAN ✅
```

If any are found:
```
RESULT: 3 occurrences found — ACTION REQUIRED ❌
  backend/app/services/email_service.py:42 → "test@uaic.com"
  ...
```

### 3.3 Proposed File

**New file:** [`backend/app/scripts/find_uaic_emails.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/scripts/find_uaic_emails.py)  
**Location:** `backend/app/scripts/` (matches existing script placement of `clean_history.py`)  
**Size:** ~60 lines  
**Execution:** `cd backend && .venv\Scripts\python app/scripts/find_uaic_emails.py`

---

## 4. Verification Plan

### 4.1 Automated Verification After Implementation

| Step | Command | Expected Result |
|------|---------|----------------|
| Ruff lint | `cd backend && .venv\Scripts\ruff check app tests` | 0 errors |
| Pytest suite | `cd backend && .venv\Scripts\pytest -q` | 182 passed, 0 warnings |
| TypeScript | `cd frontend && npx tsc --noEmit` | 0 errors |
| PS1 syntax | `scripts\check_ps1_syntax.ps1` | 0 errors |
| find_uaic_emails.py | `cd backend && .venv\Scripts\python app/scripts/find_uaic_emails.py` | 0 occurrences, exit 0 |

### 4.2 Manual Verification (DB/Redis Sync — requires running backend)

1. Start services via Option [1]
2. Wait for FastAPI to be healthy at `http://localhost:8000`
3. Run Option [6] and choose `[U]` (Unattended)
4. Verify `backend/.env` shows `PLAYWRIGHT_HEADLESS=true`
5. Verify `GET http://localhost:8000/api/v1/settings` returns `"headless_mode": true`
6. Run Option [6] again and choose `[A]` (Attended)
7. Verify `GET http://localhost:8000/api/v1/settings` returns `"headless_mode": false`

### 4.3 Graceful Offline Behavior

1. Stop all services (Option [2])
2. Run Option [6] and choose `[U]`
3. Verify `.env` is updated AND a yellow `WARNING` message is shown ("Backend not running")
4. No crash or blocking

---

## 5. Files to Be Changed

| File | Type | Change |
|------|------|--------|
| [`setup_local.ps1`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/setup_local.ps1) | MODIFY | Add API sync block to `Invoke-SetRpaMode` (~15 lines after line 449) |
| [`backend/app/scripts/find_uaic_emails.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/scripts/find_uaic_emails.py) | **NEW** | Create compliance scanner script (~60 lines) |

**No other files are modified.** This plan is minimal and targeted — it closes only the two
identified gaps without touching any other working code.

---

## 6. Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| API call fails (backend offline) | Expected during initial startup | Wrapped in try/catch, fails gracefully with warning |
| GET + POST settings inadvertently resets a field | Low | We GET the full current object, patch only `headless_mode`, then POST the full object back |
| find_uaic_emails.py exits non-zero when occurrences found | Expected | This is intentional — CI/CD can use exit code as a gate |
| PS1 syntax errors introduced | Very low | Will be validated by `check_ps1_syntax.ps1` after change |

---

## 7. User Review & Confirmation Required

> [!IMPORTANT]
> Per AGENTS.md engineering governance rules:
> **No source code changes will be made until the user explicitly approves this plan.**
>
> Please review Section 2 (Option [6] fix) and Section 3 (find_uaic_emails.py) above.
> Reply with **"approved"** or **"yes"** to proceed with implementation.

**Scope confirmation:** This plan touches exactly **2 files**:
1. `setup_local.ps1` — 15 new lines in `Invoke-SetRpaMode`
2. `backend/app/scripts/find_uaic_emails.py` — new 60-line script

No API endpoints, no database schema, no frontend files, no test files are changed.
