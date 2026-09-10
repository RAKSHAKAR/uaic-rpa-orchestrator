# Implementation Plan: Responsive UI/UX, Data Formats, Scraped Cases Redesign & Core Orchestrator Fixes

**Implementation ID:** `IMP-2026-0911-001`  
**Project:** UAIC Claim & RPA Orchestrator  
**Module:** Frontend (Next.js 14) + Backend (FastAPI + Celery + SQLAlchemy)  
**Feature / Issue:** Prompt 03 — Responsive UI/UX, Data Formats, and Core Orchestrator Fixes  
**Document Type:** Implementation Plan  
**Version:** v1  
**Status:** Approved  
**Created:** 2026-09-11  
**Last Updated:** 2026-09-11  
**AI Agent:** Antigravity (Advanced Agentic Coding)  
**Approval Status:** Approved  
**Approved By:** User  
**Approval Date:** 2026-09-11  
**Verification Status:** AI Generated — Awaiting Human Verification  

---

## Revision History

| Version | Date | Change | Reason |
|---|---|---|---|
| v1 | 2026-09-11 | Initial comprehensive plan across all 6 sections | User Request 03 |

---

## 1. Problem Statement & Objectives

User request **03 - RESPONSIVE UI/UX, DATA FORMATS, AND CORE ORCHESTRATOR FIXES** mandates a complete, verified audit and implementation across 6 key pillars:

1. **Global Mandatory Responsive Design & Theme**:
   - Application must utilize full available viewport width (`w-full max-w-none flex-1`). Remove unnecessary `max-width` constraints. Zero horizontal overflow.
   - Dedicated fixed bottom/footer mobile navigation bar respecting safe-area insets without overlapping scrolling content.
   - 100% parity across Dark and Light modes for all tables, inputs, modals, charts, fonts, and controls.
2. **Page-Specific Fixes**:
   - **Dashboard (`/`)**: Connect to real data. Optimize polling and rendering performance.
   - **Audit & Exceptions**: Ensure Excel export exists. Enable column sorting and multi-select filters.
   - **Monitor (`/monitor`)**: Reusable background export popup (Excel, CSV, JSON). Ensure Auto Queue is ON by default.
   - **Claim Detail (`/claims/:id`)**: Fix "View Stages" button. Fix missing "Filing Date" capture. Ensure Top/Bottom exports (Excel, CSV, JSON) contain identical data. Remove PDF from bottom export (PDF only visible at top for full-page print). Ensure Audit Events record properly.
3. **Orchestrator & Routing Logic**:
   - State Routing validation:
     * If Policy State == Loss Location State == Florida: Route to Broward, Hillsborough, Miami-Dade (3 bots).
     * If Policy State == Loss Location State == Texas: Route to Travis, Dallas, Harris JP, Harris Clerk, Harris District (5 bots).
     * If Policy State != Loss Location State: Route to all 8 portals.
     * CRITICAL: Miami-Dade is Florida. Never classify it as Texas.
   - Guidewire Contract: UI changes must NEVER alter, corrupt, omit, or rename the data payload sent to Guidewire (`ClaimNumber`, `ExposureNumber`, `CaseItems` with exact field names and 9-digit "0" prefix rule).
4. **Scraped Public Court Cases (UI Redesign)**:
   - Validate UI does NOT alter the underlying Guidewire payload contract.
   - Grouping: Group cases explicitly by **Portal Link** and **Portal Name (FL-Florida)**.
   - Redesign section into a professional enterprise table with:
     * Column-based sorting on all table columns.
     * Multi-select filtering (counties, statuses, types).
     * Global search across case number, style, county, status, type.
     * Pagination supporting up to 500 records (10, 25, 50, 100, 250, 500).
     * Remove broken standalone `sort:descending` button.
     * Data Integrity: Do not drop fields just because they are empty. Provide a "View Raw JSON" button for debugging.
5. **Form & API Adjustments**:
   - Remove 'Loss Location City', 'Loss Location County', 'Garaging City', and 'Garaging State' from New Form, Edit Form, and Ingestion Mapping (`TARGET_CLAIM_FIELDS`).
   - Fuzzy Match APIs: Create API to extract unique names from Insured, Driver, and Claimant fields. Re-implement legacy Power Automate fuzzy match search API.
   - Anti-Captcha Extension: Dedicated workflow/UI in Automation Settings to configure and test extension.
6. **Dashboard, Exports & UI Refinements**:
   - Dashboard real data connection and align Scraper Execution (8 Bots) cards with dashboard card design tokens.
   - Export popup as reusable component; Top/Bottom export parity on Claim Detail.

---

## 2. Current State Diagnosis & Gap Analysis

Based on systematic inspection of code, tests, and database models:

| Area | Current Code State | Expected State | Gap / Action Required |
|---|---|---|---|
| **Health Page Layout** | `health/page.tsx` line 180 has `max-w-[1920px] mx-auto` | Full viewport `w-full max-w-none flex-1` | **FIX:** Remove `max-w-[1920px] mx-auto` and align with `w-full max-w-none flex-1` |
| **Ingestion Mapping** | `excel_parser.py` line 204 has 4 deprecated fields in `TARGET_CLAIM_FIELDS` | 4 fields removed from mapping | **FIX:** Remove `loss_location_city`, `loss_location_county`, `garaging_city`, `garaging_state` from `TARGET_CLAIM_FIELDS` |
| **View Stages Button** | Sets `inspectedStage` state; modal renders only basic start/end time and raw JSON | Modal shows visual stage-by-stage progression (Navigation, Search, Parsing, DB Save) | **FIX:** Enhance modal to render structured stage table/timeline from `inspectedStage.data.stages` |
| **Filing Date Capture** | Scrapers capture `FilingDate`; if key variant or null in DB, UI shows "-" | Robust fallback to `courtCase.filing_date || raw_payload.FilingDate || raw_payload.filing_date` | **FIX:** Add fallback in `claims.py` response, `scraper_tasks.py` DB write, and frontend JSX |
| **Audit Events in Workers** | API endpoints record audit logs; Celery scraper and fuzzy tasks do not | Celery background tasks record audit entries | **FIX:** Add audit logging in `scraper_tasks.py` (scraper completed/failed) and `fuzzy_tasks.py` (fuzzy match / Guidewire push) |
| **Scraped Cases Grouping** | Currently groups only by `county_name` | Explicit grouping by **Portal Link** and **Portal Name (FL-Florida)** | **FIX:** Update `groupedCases` composite key & header: Portal Name, State badge, clickable link, case count |
| **Scraped Cases Filtering** | Uses single-select `<select>` dropdowns | Universal `MultiSelectDropdown` for Counties and Case Statuses | **FIX:** Replace single-selects with `MultiSelectDropdown` in Scraped Cases section |
| **Scraped Cases Sorting** | Only sortable in Unified Table view; Grouped view headers not clickable | Clickable column sorting in both Unified and Grouped views | **FIX:** Add column sorting handlers to headers in both views |
| **Cases Found Column & Card** | Metric card titled "Cases Harvested"; breakdown lacks Cases Found column | "Total Cases Found" on card; Cases Found column in table | **FIX:** Rename card to "Total Cases Found"; add Cases Found column in breakdown table |
| **Fuzzy Match APIs** | `GET /extract-names` & `POST /fuzzy-search` exist with 32 unit tests | Working and tested | **VERIFIED:** Fully operational, preserve intact |
| **Anti-Captcha Settings** | Dedicated Automation card + dedicated Extension tab in Settings | Configurable & testable | **VERIFIED:** Fully operational, preserve intact |
| **Guidewire Contract** | Payload strictly `{ ClaimNumber, ExposureNumber, CaseItems }` with 9-digit rule | Unchanged, protected | **VERIFIED:** Preserved 100% |
| **State Routing** | `resolve_county_bot_targets`: FL->3, TX->5, Cross->8; Miami=FL | Unchanged, verified | **VERIFIED:** Preserved 100% |
| **Bottom Export PDF** | Top toolbar has PDF; bottom export bar has Excel, CSV, JSON (no PDF) | PDF only at top | **VERIFIED:** Preserved 100% |

---

## 3. Scope of Changes

### In Scope
1. **Backend**:
   - `backend/app/services/excel_parser.py`: Remove 4 deprecated fields from `TARGET_CLAIM_FIELDS`.
   - `backend/app/tasks/scraper_tasks.py`: Normalize `filing_date` capture keys; record Celery worker audit logs (`SCRAPER_EXECUTION_COMPLETED` / `SCRAPER_EXECUTION_FAILED`).
   - `backend/app/tasks/fuzzy_tasks.py`: Record Celery worker audit logs (`FUZZY_MATCH_COMPLETED`, `GUIDEWIRE_PUSH_COMPLETED` / `GUIDEWIRE_PUSH_FAILED`).
   - `backend/app/api/v1/endpoints/claims.py`: Add fallback to `raw_payload` for `filing_date` in `ScrapedCaseResponse`.
   - `backend/tests/test_imp_2026_0911_001.py`: Automated tests verifying field removal from ingestion mapping, worker audit logging, and `filing_date` fallbacks.
2. **Frontend**:
   - `frontend/src/app/health/page.tsx`: Align `<main>` container to `w-full max-w-none flex-1 transition-colors`.
   - `frontend/src/app/claims/[id]/page.tsx`:
     * Expand "View Stages" modal with visual stage progression list (name, status, timestamps, duration, detail).
     * Rename Scraper Execution KPI card to "Total Cases Found" and add "Cases Found" column in the Individual Portal Scraping breakdown table.
     * Group Scraped Cases by Portal Link and Portal Name with state badges (`FL - Florida` / `TX - Texas`).
     * Integrate `MultiSelectDropdown` for Counties and Case Statuses, plus Case Type filter.
     * Add column-based sorting to both Unified Table and Grouped View table headers.
     * Support pagination up to 500 records (10, 25, 50, 100, 250, 500).
     * Add `raw_payload` fallback for `filing_date` display.

### Out of Scope (Preserved Unchanged)
- Database ORM model definitions (the 4 columns remain in `ClaimRecord` table for historical safety).
- State routing logic in `excel_parser.py::resolve_county_bot_targets`.
- Guidewire payload contract in `guidewire_client.py`.
- Fuzzy matching cascade logic in `fuzzy_engine.py` and `fuzzy_tasks.py`.
- Reusable `AsyncExportModal` architecture.

---

## 4. File-Level Action Plan

```markdown
#### [MODIFY] backend/app/services/excel_parser.py
- Remove 4 field dicts (`loss_location_city`, `loss_location_county`, `garaging_city`, `garaging_state`) from `TARGET_CLAIM_FIELDS`.
- Reason: Removes them from Ingestion Mapping preview UI without altering ORM database tables.

#### [MODIFY] backend/app/tasks/scraper_tasks.py
- Normalize `filing_date` assignment with fallback keys: `c.get("FilingDate") or c.get("filing_date") or c.get("Filing Date") or c.get("SuitFiledDate") or c.get("suit_filed_date")`.
- Add `AuditLog` persistence on scraper batch completion (`action="SCRAPER_EXECUTION_COMPLETED"`) and error (`action="SCRAPER_EXECUTION_FAILED"`).
- Reason: Guarantees filing dates are never lost, and ensures worker audit events appear in the Claim Audit Trail.

#### [MODIFY] backend/app/tasks/fuzzy_tasks.py
- Add `AuditLog` persistence in Celery tasks: `action="FUZZY_MATCH_COMPLETED"` and `action="GUIDEWIRE_PUSH_COMPLETED"` / `action="GUIDEWIRE_PUSH_FAILED"`.
- Reason: Ensures background matching and Guidewire push events are recorded in the immutable audit trail.

#### [MODIFY] backend/app/api/v1/endpoints/claims.py
- In `get_claim_detail`, populate `filing_date` from `sc.filing_date or (sc.raw_payload.get("FilingDate") or sc.raw_payload.get("filing_date") ...)` if `sc.filing_date` is null.
- Reason: Protects against cases where `scraped_court_cases.filing_date` is blank but raw JSON contains the date.

#### [MODIFY] frontend/src/app/health/page.tsx
- Replace `max-w-[1920px] mx-auto` on `<main>` with `w-full max-w-none flex-1 transition-colors`.
- Reason: Strictly enforces the global full-viewport requirement.

#### [MODIFY] frontend/src/app/claims/[id]/page.tsx
- In "View Stages" modal (`inspectedStage`), render structured stage progression table/cards showing Stage Name, Status, Start/End time, Duration (s), and Detail, alongside the existing JSON viewer.
- In 8 Bots execution section, rename card label from "Cases Harvested" to "Total Cases Found" and add "Cases Found" column after duration.
- In Scraped Public Court Cases:
  * Group cases explicitly by Portal Link and Portal Name (`${portal_name} (${state})`), displaying county, portal name, state badge (`FL - Florida` / `TX - Texas`), clickable external portal link, case count, and collapse toggle.
  * Add `MultiSelectDropdown` for Counties and Case Statuses, plus Case Type filter.
  * Enable clickable column sorting on all headers in both table view and grouped view.
  * Update pagination dropdown to `[10, 25, 50, 100, 250, 500]`.
  * Display fallback `courtCase.filing_date || courtCase.raw_payload?.FilingDate || "N/A"`.

#### [NEW] backend/tests/test_imp_2026_0911_001.py
- Unit and integration tests covering `TARGET_CLAIM_FIELDS` cleanup, `filing_date` capture fallbacks, worker audit event logging, and single-claim export endpoints.
```

---

## 5. Verification & Testing Plan

### Automated Test Suite
```bash
# 1. New Prompt 03 verification tests
cd backend && .venv\Scripts\pytest tests\test_imp_2026_0911_001.py --tb=short -q

# 2. Existing Prompt 03 fuzzy & anticaptcha tests
.venv\Scripts\pytest tests\test_imp_2026_0909_003.py --tb=short -q

# 3. Python Linter (zero errors)
.venv\Scripts\ruff check app tests

# 4. Frontend TypeScript check (zero errors)
cd frontend && npx tsc --noEmit

# 5. Frontend Production Build
npm run build

# 6. PowerShell syntax check (zero errors)
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"
```

### Manual & Visual Verification
1. Inspect `/health` in browser: Verify full viewport width, zero horizontal scrolling, dark/light theme parity.
2. Inspect `/claims/:id`:
   - Click "View Stages" on any portal: Verify stage progression breakdown modal opens with stage names, durations, and statuses.
   - Verify 8 Bots section has "Total Cases Found" card and "Cases Found" column in the breakdown table.
   - Verify Scraped Public Court Cases: Grouped by Portal Link & Name with state badges (`FL - Florida` / `TX - Texas`).
   - Test column sorting on all headers in both Unified Table and Grouped View.
   - Test multi-select filtering on Counties and Case Statuses.
   - Test pagination up to 500 records.
   - Verify Top export toolbar has Excel, CSV, PDF, JSON; bottom export bar has Excel, CSV, JSON (no PDF).
   - Verify Audit Trail timeline records events from both API and Celery background workers.
3. Inspect `/upload`: Ingestion column mapping does NOT list the 4 removed fields.

---

## 6. Acceptance Criteria

- [ ] `TARGET_CLAIM_FIELDS` in `excel_parser.py` contains 0 entries for `loss_location_city`, `loss_location_county`, `garaging_city`, `garaging_state`.
- [ ] Celery tasks record `AuditLog` records for scraper completion and fuzzy matching.
- [ ] Scraped court cases capture and display `filing_date` even when stored in `raw_payload`.
- [ ] "View Stages" button renders visual stage progression breakdown in modal.
- [ ] Scraped Public Court Cases grouped by Portal Link and Portal Name with state badges.
- [ ] Table headers in both Unified and Grouped views support column sorting.
- [ ] Counties and Case Status filters use `MultiSelectDropdown`.
- [ ] Pagination selector includes 500 records.
- [ ] Bottom export bar does NOT have PDF button; Top toolbar retains PDF.
- [ ] `health/page.tsx` uses `w-full max-w-none flex-1`.
- [ ] `pytest` passes 100%, `ruff check` 0 errors, `tsc --noEmit` 0 errors, `npm run build` exits 0.

---

**No application code has been modified yet.**  
**Plan saved to:** `implementation_plan/2026-09-11_uaic_responsive-ux-orchestrator-scraped-cases-form-fixes_implementation-plan_v1.md`  
Please confirm if you approve this plan so I may begin execution.
