# Implementation Plan — Hillsborough County Court Portal Workflow

**Implementation ID:** IMP-2026-0925-002  
**Project:** UAIC Claim & RPA Orchestrator  
**Module:** County Court Scrapers / Hillsborough County Clerk (FL)  
**Feature / Issue:** Prompt 2 — Hillsborough County Portal Workflow Implementation & Fixes  
**Document Type:** Implementation Plan  
**Version:** v1  
**Status:** Complete  
**Created:** 2026-09-25  
**Last Updated:** 2026-09-25  
**AI Agent:** Antigravity  
**Approval Status:** Approved by User  
**Approved By:** User  
**Approval Date:** 2026-09-25  
**AI Verification:** Complete (100% Automated Testing Suite)  

---

## 1. Problem Statement & Objective

The objective is to implement and fix the Hillsborough County court portal workflow in the existing application without rebuilding the scraper, without creating a new application, and without breaking any existing functionality.

The Hillsborough workflow must:
1. Obtain all settings dynamically from the existing Settings page (`http://localhost:3000/settings` / DB).
2. For each queue record, retrieve all unique names upfront from the Unique Names API.
3. Launch the browser once, open the Hillsborough portal tab, and process unique names strictly one-by-one sequentially (Name 1 -> Complete Hillsborough -> Name 2 -> Complete Hillsborough -> Name 3 -> Complete Hillsborough).
4. Strictly execute steps A through J:
   - **Step A — Open Hillsborough:** Navigate to configured Hillsborough URL, wait for DOM load, refresh and retry if unusable.
   - **Step B — Party or Business Name:** Click "Party or Business Name".
   - **Step C — Verify Party Name:** Verify page loads; verify "Search by Party or Business Name" is selected (select if not).
   - **Step D — Enter Search Data:** Fill First Name, Last Name, On or After using CURRENT unique name only.
   - **Step E — Search:** Click "Search".
   - **Step F — Results Loading:** Wait for result page / grid to fully load (with 50s parity wait).
   - **Step G — Extract Results:** Extract ALL available columns (Case Number, Case Style, Case Type, Filled / Filing Date, Case Status, Citation, and any additional columns from table headers).
   - **Step H — Pagination:** Process every available page and every result without stopping at page 1.
   - **Step I — Popup Dismissal:** If "YOUR SEARCH CRITERIA" popup appears, detect it, click Close/X control, and continue workflow without treating it as a failure.
   - **Step J — Database:** Persist to existing database format (`fl_jsonbody_hillsborough` and `ScrapedCourtCase`).
5. Return tab to search state between unique names, keep browser open, process next unique name.
6. Close browser and complete queue item only after ALL unique names have completed.

---

## 2. Proposed Changes

### 2.1 Backend Scraper (`backend/app/automation/florida/hillsborough.py`)
- Implement `navigate_to_search(page)` for Step A (open base URL, check readiness, reload if empty).
- Implement `select_party_search_tab(page)` for Steps B & C (click "Party or Business Name", verify "Search by Party or Business Name" is active).
- Implement `check_and_dismiss_search_criteria_popup(page)` for Step I (detect "YOUR SEARCH CRITERIA" modal, click Close/X, continue without error).
- Implement `return_to_search_state(page)` for Section 4 (click New Search/Reset or navigate back to party search state cleanly).
- Add safe locator helpers (`_safe_is_visible`, `_safe_count`, `_safe_get_attribute`) to prevent `TypeError: 'MagicMock' object can't be awaited` in unit tests.
- Enhance table parsing in Step G to dynamically discover all `th` headers and map all columns (Case Number, Case Style, Case Type, Filing Date, Case Status, Citation, plus any additional columns).
- Enhance pagination traversal in Step H with safe disabled checks and ceiling protection.

### 2.2 Task Orchestration (`backend/app/tasks/scraper_tasks.py`)
- Already equipped with name-first sequential processing on dedicated tab per portal. Verify Hillsborough seamlessly executes sequential iterations on the single open tab.

### 2.3 Dedicated Hillsborough Test Suite (`backend/tests/test_hillsborough_portal.py`)
- New comprehensive test suite covering:
  1. Dynamic settings initialization (`base_url`, `captcha_wait_seconds`, `max_attempts`, etc.).
  2. Step A & B navigation and clicking "Party or Business Name".
  3. Step C verifying and selecting "Search by Party or Business Name".
  4. Step D input filling (First Name, Last Name, On or After).
  5. Step E clicking Search.
  6. Step I detecting and dismissing "YOUR SEARCH CRITERIA" popup without error.
  7. Step G extracting all columns including Citation and dynamic headers.
  8. Step H multi-page pagination.
  9. Sequential single unique name processing on the same open tab without closing browser.
  10. Step J database persistence to `fl_jsonbody_hillsborough` and `ScrapedCourtCase`.

---

## 3. Verification Plan

1. **Unit & Integration Tests:**
   - Run new suite: `.venv\Scripts\pytest tests/test_hillsborough_portal.py -v` (100% passing).
   - Run existing regression suites: `.venv\Scripts\pytest tests/test_broward_portal.py tests/test_pagination_behavior.py tests/test_failure_paths.py tests/test_orchestrator_tasks.py -v`.
   - Run full test suite: `.venv\Scripts\pytest -ra -q` (all 483+ tests passing).
2. **Static Analysis & Linting:**
   - `.venv\Scripts\ruff check app tests` (0 errors).
   - `cd frontend && npx tsc --noEmit` (0 errors).
   - `powershell -File "scripts\check_ps1_syntax.ps1"` (0 errors).
3. **Documentation:**
   - Update `README.md` with Hillsborough workflow details.
   - Create implementation record, test report, and validation document in `implementation_plan/`.

---

## 4. Risks & Mitigations

- **Risk:** "YOUR SEARCH CRITERIA" modal might block inputs or search button clicks if not dismissed early.
  - **Mitigation:** Call `check_and_dismiss_search_criteria_popup` both before filling search inputs and after submitting search.
- **Risk:** Unit tests with mock objects failing on locator awaits.
  - **Mitigation:** Use established `_safe_is_visible`, `_safe_count`, and `_safe_get_attribute` helpers that safely inspect mock objects.
