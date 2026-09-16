# Implementation Plan — Complete Claim Audit, Provenance & Diagnostic Logs System

**Implementation ID:** `IMP-2026-0917-002`  
**Date:** 2026-09-17  
**Status:** Complete (100% Automated Testing Suite)  
**AI Verification:** Complete (100% Automated Testing Suite)  
**Target Modules:**  
- Database Models: `backend/app/models/claim.py`, `backend/app/models/audit_log.py`, `backend/app/models/error_screenshot.py`  
- Schemas: `backend/app/schemas/claim.py`, `backend/app/schemas/audit.py`  
- Services & Helpers: `backend/app/services/audit_service.py`, `backend/app/automation/base.py`  
- Endpoints: `backend/app/api/v1/endpoints/claims.py`, `backend/app/api/v1/endpoints/ingest.py`  
- Background Workers: `backend/app/tasks/ingest_tasks.py`, `backend/app/tasks/scraper_tasks.py`, `backend/app/tasks/fuzzy_tasks.py`  
- Frontend Types & UI: `frontend/src/types/index.ts`, `frontend/src/app/claims/[id]/page.tsx`, `frontend/src/app/page.tsx`

---

## 1. Requirements & Problem Statement

The user requested:
> *"pls make sure that all kind of logs must be registered. like- record created_on created_by, modified_on, modified_by, and all kind of processing logs, execption logs, etc... and must be show with the respective claims."*

### Current Gaps Identified:
1. **Missing Provenance Columns on `ClaimRecord`:**
   - `created_at` and `updated_at` exist, but there are **no `created_by` or `modified_by`** fields on `ClaimRecord` or in `ClaimResponse`.
   - When a claim is ingested from Excel/CSV or created via API, the creator identity (user email / batch filename / API key) is not persisted directly on the claim row.
   - When workers update claim statuses (scraped, fuzzy matched, failed, retried, or Guidewire pushed), `modified_by` is not tracked.
2. **Scattered Logs vs. Unified Claim Presentation:**
   - Portal execution logs are stored as flat text files in `backend/logs/{claim_id}/{portal_key}/execution.log`.
   - Audit logs are in `audit_logs` table, but lack full end-to-end coverage for individual claim creation during batch ingestion and pipeline lifecycle transitions.
   - Exception logs and stack traces are split across `claim.last_error`, `error_screenshots.exception_message`, and raw files.
   - On the frontend claim detail page (`/claims/[id]`), `created_by`, `modified_on`, and `modified_by` are not displayed. While an audit trail exists, there is no unified **"Processing & Exception Logs"** interactive console where operators can inspect live step-by-step logs, stack traces, and failing stage details directly alongside the claim.

---

## 2. Proposed Architecture & Solution Design

```
                     ┌────────────────────────────────────────────────────────┐
                     │                     ClaimRecord                        │
                     │  - created_at / created_on                             │
                     │  - created_by (user email / batch filename / api)      │
                     │  - updated_at / modified_on                            │
                     │  - modified_by (worker / operator / system)            │
                     └──────────────────────────┬─────────────────────────────┘
                                                │
         ┌──────────────────────────────────────┼──────────────────────────────────────┐
         ▼                                      ▼                                      ▼
┌──────────────────┐                  ┌───────────────────┐                  ┌───────────────────┐
│   Audit Logs     │                  │  Processing Logs  │                  │  Exception Logs   │
│  (AuditLog DB)   │                  │ (File & Telemetry)│                  │(ErrorScreenshots) │
│ - User actions   │                  │ - Stage timings   │                  │ - Stack traces    │
│ - Status changes │                  │ - Scraper steps   │                  │ - Failing portal  │
│ - Guidewire sync │                  │ - Match scores    │                  │ - Screenshots     │
└──────────────────┘                  └───────────────────┘                  └───────────────────┘
```

---

## 3. Proposed Changes

### Component 1: Database Model Enhancements
#### [MODIFY] [backend/app/models/claim.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/models/claim.py)
- Add columns to `ClaimRecord`:
  ```python
  created_by: Mapped[str] = mapped_column(String(100), default="system", index=True)
  modified_by: Mapped[str] = mapped_column(String(100), default="system", index=True)
  ```
- Expose properties / aliases `created_on` (returning `created_at`) and `modified_on` (returning `updated_at`).

---

### Component 2: Pydantic Schema Enhancements
#### [MODIFY] [backend/app/schemas/claim.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/schemas/claim.py)
- Update `ClaimResponse` to include:
  ```python
  created_by: str = "system"
  modified_by: str = "system"
  created_on: datetime | None = None
  modified_on: datetime | None = None
  ```
- Update `ClaimCreate` and `ClaimUpdate` schemas to accept optional `created_by` and `modified_by`.
- Create a new unified schema `ClaimLogsSummaryResponse` containing:
  - `claim_id`: str
  - `claim_number`: str
  - `created_on`: datetime
  - `created_by`: str
  - `modified_on`: datetime
  - `modified_by`: str
  - `audit_logs`: list[AuditLogResponse]
  - `processing_logs`: list[dict] (aggregated timeline across scrapers, matching, and queue)
  - `exception_logs`: list[dict] (exceptions with stack trace, failing portal, error screenshot URL, timestamp)
  - `portal_logs`: dict[str, str] (raw log text per portal)

---

### Component 3: Service & Task Logging Upgrades
#### [MODIFY] [backend/app/services/audit_service.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/services/audit_service.py)
- Ensure helper `append_claim_processing_log(claim_id: str, stage: str, message: str, level: str = "INFO", details: dict | None = None)` handles writing to structured file logs and `AuditLog` when level is `WARNING`, `ERROR`, or `EXCEPTION`.

#### [MODIFY] [backend/app/tasks/ingest_tasks.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/ingest_tasks.py)
- When inserting claims, set `created_by = batch.filename` (or uploader user email), `modified_by = "system:ingestion"`.
- Log audit event `CLAIM_CREATED` for each ingested claim with claim number and batch ID.

#### [MODIFY] [backend/app/tasks/scraper_tasks.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/scraper_tasks.py)
- Update `claim.modified_by = "worker:scrapers"` whenever the worker changes claim status or records scraped cases.
- Record detailed exception logs when scraping fails (storing failing URL, exception class, line number, and linking to `ErrorScreenshot`).

#### [MODIFY] [backend/app/tasks/fuzzy_tasks.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/tasks/fuzzy_tasks.py)
- Update `claim.modified_by = "worker:fuzzy_matcher"` or `"worker:guidewire_sync"`.
- Log processing steps and any matching or Guidewire HTTP exceptions.

---

### Component 4: API Endpoint Enhancements
#### [MODIFY] [backend/app/api/v1/endpoints/claims.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/api/v1/endpoints/claims.py)
- In `_map_claim_to_response()`: populate `created_by`, `modified_by`, `created_on`, `modified_on`.
- In `create_claim()`: populate `created_by = ctx["user_email"]`, `modified_by = ctx["user_email"]`.
- In `update_claim()`: update `modified_by = ctx["user_email"]`.
- In `start_claim_automation()`, `stop_claim_automation()`, `push_claim_guidewire()`, `run_claim_single_bot()`, `retry_failed_claim()`: update `modified_by = ctx["user_email"]`.
- Add new endpoint: `GET /api/v1/claims/{claim_id}/combined-logs`:
  Returns structured record metadata (`created_on`, `created_by`, `modified_on`, `modified_by`), audit events, processing logs, and exception diagnostics in a single unified response.

---

### Component 5: Frontend Types & UI Enhancements
#### [MODIFY] [frontend/src/types/index.ts](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/types/index.ts)
- Add `created_by?: string`, `modified_by?: string`, `created_on?: string`, `modified_on?: string` to `Claim` interface.
- Add interfaces for `ClaimCombinedLogs`, `ProcessingLogEntry`, `ExceptionLogEntry`.

#### [MODIFY] [frontend/src/app/claims/[id]/page.tsx](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/claims/%5Bid%5D/page.tsx)
1. **Claim 360 Context Card:**
   - Display a dedicated **"Provenance & Ownership"** block:
     - **Created On:** formatted date & time
     - **Created By:** user email / batch source badge with User icon
     - **Modified On:** formatted date & time
     - **Modified By:** worker / user badge
2. **Comprehensive "Claim Logs & Diagnostic Center":**
   - Enhance the bottom section with tabs:
     - **Tab 1: Audit Trail** (Chronological user & system actions)
     - **Tab 2: Processing Logs** (Live pipeline execution events, timing, scraper steps)
     - **Tab 3: Exception & Error Logs** (Dedicated error card showing exact stack trace, error stage, error screenshot thumbnail, and retry details)
     - **Tab 4: Portal Console Logs** (Terminal viewer for raw execution logs per portal with search & copy)

#### [MODIFY] [frontend/src/app/page.tsx](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/page.tsx)
- In the claims dashboard table, show `Created By` alongside `Ingested Date` (or in a dedicated column / expanded tooltip) so operators can see who created and last modified each claim.

---

## 4. Verification Plan

### Automated Tests
1. **New Unit & Integration Tests:**
   - Verify `created_by` and `modified_by` are set on claim creation (via API and batch ingestion).
   - Verify `modified_by` is updated on claim edit, scraper completion, matching, and Guidewire push.
   - Verify `GET /api/v1/claims/{id}/combined-logs` returns complete audit, processing, and exception logs.
2. **Full Pytest Suite:**
   ```bash
   cd backend && .venv\Scripts\pytest --tb=short -q
   ```
3. **Backend Lint:**
   ```bash
   cd backend && .venv\Scripts\ruff check app tests
   ```
4. **Frontend TypeScript Check:**
   ```bash
   cd frontend && npx tsc --noEmit
   ```
5. **PowerShell Syntax Check:**
   ```bash
   powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"
   ```

### Manual & Visual Verification
- Open `/claims/[id]` in the browser using the browser subagent.
- Verify `Created On`, `Created By`, `Modified On`, `Modified By` are displayed clearly.
- Verify the new tabbed **Logs & Diagnostic Center** displays audit logs, processing logs, exception details, and portal console outputs.
- Capture a screenshot into `implementation_plan/Images/` and record browser video into `implementation_plan/Recording/`.

---

## 5. Verification Report & Visual Evidence

### 5.1 Automated Test Execution Results (100% Pass)
- **Backend Pytest Suite:** 441 passed across 33 test suites (including newly authored [test_claim_logs_and_provenance.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/tests/test_claim_logs_and_provenance.py)).
  ```bash
  .venv\Scripts\pytest --tb=short -q
  # Output: 441 passed in 49.32s (100% pass)
  ```
- **Backend Linting:**
  ```bash
  .venv\Scripts\ruff check app tests
  # Output: All checks passed!
  ```
- **Frontend TypeScript Compilation:**
  ```bash
  cd frontend && npx tsc --noEmit
  # Output: 0 errors
  ```
- **Frontend ESLint:**
  ```bash
  cd frontend && npm run lint
  # Output: ✔ No ESLint warnings or errors
  ```
- **PowerShell Syntax Check:**
  ```bash
  powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"
  # Output: All 9 scripts validated with 0 syntax errors
  ```

### 5.2 Browser Subagent Visual Verification Artifacts
- **Dashboard Provenance Table:** [implementation_plan/Images/dashboard_claims_provenance_table.png](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/implementation_plan/Images/dashboard_claims_provenance_table.png)
- **Claim 360 Provenance Overview:** [implementation_plan/Images/claim_360_provenance_overview.png](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/implementation_plan/Images/claim_360_provenance_overview.png)
- **Tab 1 — Audit Trail:** [implementation_plan/Images/claim_logs_tab1_audit_trail.png](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/implementation_plan/Images/claim_logs_tab1_audit_trail.png)
- **Tab 2 — Processing Logs:** [implementation_plan/Images/claim_logs_tab2_processing_logs.png](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/implementation_plan/Images/claim_logs_tab2_processing_logs.png)
- **Tab 3 — Exceptions & Errors:** [implementation_plan/Images/claim_logs_tab3_exceptions_errors.png](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/implementation_plan/Images/claim_logs_tab3_exceptions_errors.png)
- **Tab 4 — Portal Console Terminal:** [implementation_plan/Images/claim_logs_tab4_portal_console.png](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/implementation_plan/Images/claim_logs_tab4_portal_console.png)
- **Full Video Session Recording:** [implementation_plan/Recording/2026-09-17_claim_logs_and_provenance_verification.webp](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/implementation_plan/Recording/2026-09-17_claim_logs_and_provenance_verification.webp)

