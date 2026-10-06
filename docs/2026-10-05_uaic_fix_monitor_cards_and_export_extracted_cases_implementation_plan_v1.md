# Implementation Plan: Fix Queue Monitor Stat Cards & Restore Extracted Cases in Export

**Implementation ID:** `IMP-2026-1005-002`  
**Project:** UAIC Claim & RPA Orchestrator  
**Module:** Distributed Task & Bot Queue Monitor (`/monitor`) / Claims Export Service  
**Document Type:** Implementation Plan  
**Version:** v1  
**Created:** 2026-10-05  
**AI Agent:** Antigravity  
**Status:** Complete  
**AI Verification:** Complete (100% Automated Testing Suite)  

---

## 1. Problem Diagnosis & Root Causes

### Issue A: Queue Monitor Cards Always Displaying "0"
- **User Observation**: Top stat cards on `http://localhost:3000/monitor` ("Ingest Queue", "Scraper Queue", "Matcher Queue", "Guidewire Queue", "Active Workers") always show `0`. The user asks what the purpose of these cards is and why we do not have statistics for **Completed Cases**, **Cases Extracted**, and **In Progress**.
- **Root Cause**:
  1. In `frontend/src/app/monitor/page.tsx` (lines 589–702), the 5 cards are bound to `queueStatus?.queues?.ingest`, `queueStatus?.queues?.scrapers`, `queueStatus?.queues?.matcher`, `queueStatus?.queues?.notifications`, and `queueStatus?.workers_online`.
  2. In `backend/app/api/v1/endpoints/queue.py`, `_get_redis_queues_sync()` queries `r.llen(q_name)` from Redis raw message lists. In this architecture, Redis message queues only hold transient tasks for milliseconds when jobs are dispatched to Celery workers; once picked up or stored in SQLite, Redis queue lengths return to `0`.
  3. When running in local dev / SQLite with workers idle or local execution, all Redis queue lengths are `0`.
  4. The page was never querying `api.getClaimStats()` (which aggregates real database claim records, portal throughput, and court cases), leaving the cards displaying empty zeros.

### Issue B: "Cases Extracted" Missing from Export
- **User Observation**: In the Queue Monitor table, there is a column titled **"Cases Extracted"** (which shows the number of cases extracted across the 8 portals). When downloading the export file (Excel, CSV, JSON) from `http://localhost:3000/monitor`, the extracted cases column is completely missing.
- **Root Cause**:
  1. In `backend/app/api/v1/endpoints/claims.py` (`export_claims`, lines 955–989) and `backend/app/tasks/export_tasks.py` (`_generate_export_data`, lines 90–115), the `export_rows` dictionary defines claim fields, party names, and portal bot statuses, but **completely omits**:
     - `"Cases Extracted"` (the total count of court cases found across all 8 portals)
     - `"Extracted Case Numbers"` (comma-separated list of scraped court case numbers)
     - `"Extracted Case Styles"` (semicolon-separated list of scraped case styles)
     - `"Guidewire Pushed"` (`Yes` / `No`)
     - `"Guidewire Activity ID"`
  2. In Excel export (`.xlsx`), there was no secondary sheet detailing the individual court cases (case number, case style, filing date, case status, case type, county/website), so users downloading an Excel export could not inspect the extracted court case records.

### Issue C: Spellcheck Warnings in `@[current_problems]`
- **Root Cause**: The IDE's CSpell (Code Spell Checker) extension flags domain-specific proper nouns (`BRYNOL`, `Cornjhia`, `DATEFILED`, `pythonpath`) in `docs/2026-10-05_uaic_fix_slow_and_failed_claims_verified_record_v1.md` as unknown words with severity `info`. These are dictionary hints and not syntax or code errors.

---

## 2. Proposed Technical Solution & Implementation Architecture

### Phase 1: Real Operational Telemetry for Queue Monitor StatCards
1. **Frontend Integration (`frontend/src/app/monitor/page.tsx`)**:
   - Update `fetchData` to call `api.getClaimStats()` in parallel with `api.getQueueStatus()` and `api.getClaims()`.
   - Replace the 5 empty Redis buffer cards with 5 high-impact, operational claim lifecycle cards:
     1. **Total Ingested / Queued**: `stats?.total_claims ?? total` (Subtext: `${stats?.new ?? 0} queued · ${stats?.in_progress ?? 0} active`)
     2. **In Progress (Active RPA)**: `stats?.in_progress ?? 0` (Subtext: `Active scraping & matching`)
     3. **Completed & Matched**: `(stats?.completed ?? 0) + (stats?.match_found ?? 0) + (stats?.no_match_found ?? 0)` (Subtext: `${stats?.match_found ?? 0} matches · ${stats?.no_match_found ?? 0} clean`)
     4. **Cases Extracted**: `stats?.total_cases_extracted ?? 0` (Subtext: `Discovered across 8 court portals`)
     5. **Exceptions & Failed**: `(stats?.failed ?? 0) + (stats?.manual_review ?? 0)` (Subtext: `${stats?.manual_review ?? 0} review · ${stats?.failed ?? 0} failed`)
   - Make each card interactively filter the table upon click:
     - Clicking "In Progress" filters table to `SCRAPING_IN_PROGRESS`.
     - Clicking "Completed & Matched" filters table to `COMPLETED,MATCH_FOUND,NO_MATCH_FOUND`.
     - Clicking "Cases Extracted" filters table to `MATCH_FOUND,COMPLETED`.
     - Clicking "Exceptions & Failed" filters table to `FAILED,MANUAL_REVIEW`.
     - Clicking "Total Ingested" resets all filters.
2. **Backend Enhancements (`backend/app/schemas/queue.py` & `backend/app/api/v1/endpoints/queue.py`)**:
   - Add `total_claims: int = 0` and `total_cases_extracted: int = 0` to `QueueStatusResponse`.
   - Update `get_queue_status()` to populate `total_claims` and `total_cases_extracted` directly from the database so that both endpoints (`/api/v1/queue/status` and `/api/v1/claims/stats`) provide accurate operational figures.

### Phase 2: Comprehensive Export with "Cases Extracted" & Court Case Details
1. **Synchronous Export (`backend/app/api/v1/endpoints/claims.py`)**:
   - Update `export_claims()`:
     - For each claim, resolve court cases using `_map_claim_to_response(c).court_cases`.
     - Add columns to `export_rows`:
       - `"Cases Extracted"`: Integer count of extracted cases (`len(cases)`).
       - `"Extracted Case Numbers"`: Comma-separated list of case numbers.
       - `"Extracted Case Styles"`: Semicolon-separated list of case styles.
       - `"Guidewire Pushed"`: `"Yes"` if `c.activity_id or c.record_status == 'COMPLETED'` else `"No"`.
       - `"Guidewire Activity ID"`: `c.activity_id or ""`.
     - For Excel format (`.xlsx`):
       - Sheet 1: **"Claims Summary"** (all claims with the new `"Cases Extracted"` column and case metadata).
       - Sheet 2: **"All Extracted Cases"** (tabular breakdown of every extracted court case: Claim Number, Exposure Number, Case Number, Case Style, County, Filing Date, Case Status, Case Type, Source URL).
     - For CSV & JSON:
       - Include `"Cases Extracted"`, `"Extracted Case Numbers"`, `"Extracted Case Styles"`, `"Guidewire Pushed"`, and `"Guidewire Activity ID"`.
2. **Asynchronous Background Export (`backend/app/tasks/export_tasks.py`)**:
   - Mirror the exact same column additions and multi-sheet Excel generation in `_generate_export_data()` to ensure 100% parity between instant downloads and large-dataset async streaming exports.

---

## 3. Step-by-Step Implementation Plan

| Step | Action | Files Affected |
|---|---|---|
| **Step 1** | Enhance `QueueStatusResponse` schema with `total_claims` and `total_cases_extracted`. | `backend/app/schemas/queue.py` |
| **Step 2** | Update `get_queue_status` endpoint to populate claim counts and total extracted court cases. | `backend/app/api/v1/endpoints/queue.py` |
| **Step 3** | Update synchronous claim export to include `"Cases Extracted"`, case summaries, and two-sheet Excel workbook. | `backend/app/api/v1/endpoints/claims.py` |
| **Step 4** | Update asynchronous Celery export task to mirror the new export schema and multi-sheet Excel output. | `backend/app/tasks/export_tasks.py` |
| **Step 5** | Update Queue Monitor page to fetch `api.getClaimStats()` and render dynamic operational cards with interactive filtering. | `frontend/src/app/monitor/page.tsx` |
| **Step 6** | Run automated testing suite (`pytest`, `ruff`, `tsc --noEmit`, `check_ps1_syntax.ps1`). | Entire test suite |
| **Step 7** | Perform browser visual verification with `browser_subagent` and archive screenshots into `docs/`. | `docs/` |

---

## 4. Verification Plan

1. **Automated Verification**:
   - `backend\.venv\Scripts\pytest -k "export or queue"`: Verify export and queue endpoints.
   - `ruff check app tests ..\e2e\backend`: Ensure 0 lint errors.
   - `npx tsc --noEmit` in `frontend/`: Ensure 0 TypeScript errors.
   - `powershell scripts\check_ps1_syntax.ps1`: Ensure 0 syntax errors.
2. **Live Export Verification**:
   - Query `/api/v1/claims/export?format=xlsx` and `/api/v1/claims/export?format=csv`.
   - Inspect output columns with python script: confirm `"Cases Extracted"`, `"Extracted Case Numbers"`, `"Extracted Case Styles"` exist with exact values.
3. **Browser Visual Verification**:
   - Open `http://localhost:3000/monitor`.
   - Verify top cards show non-zero operational values:
     - In Progress > 0 (or real DB count)
     - Completed & Matched > 0
     - Cases Extracted > 0
     - Total Ingested > 0
   - Capture screenshot and store in `docs/queue_monitor_real_stats.png`.
