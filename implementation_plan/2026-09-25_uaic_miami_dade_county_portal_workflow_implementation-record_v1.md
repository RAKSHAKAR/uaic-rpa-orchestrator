# Implementation Record — Miami-Dade County Court Portal Workflow

**Implementation ID:** IMP-2026-0925-003  
**Project:** UAIC Claim & RPA Orchestrator  
**Module:** County Court Scrapers / Miami-Dade County Clerk (FL)  
**Feature / Issue:** Prompt 3 — Miami-Dade County Court Portal Workflow  
**Document Type:** Implementation Record  
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

## 1. Summary of Work Performed

In strict compliance with **PROMPT 3 — MIAMI-DADE COUNTY PORTAL**, the Miami-Dade County civil court portal scraper (`backend/app/automation/florida/miami.py`) was enhanced and hardened to execute the complete multi-step workflow without breaking existing interfaces, data schemas, or system configurations:

1. **Dynamic Settings Integration (Section 1):**
   - Retrieves portal configuration dynamically from `get_system_settings_async()` (`http://localhost:3000/settings`).
   - Retrieves `portals.miami_url` (`https://www2.miamidadeclerk.gov/ocs`), `portals.miami_username`, `portals.miami_password`, `portals.miami_requires_login`, browser engine, retry counts, and screenshot settings. No credentials are hardcoded.

2. **Sequential Unique Names Execution (Section 2):**
   - Integrates with the upfront unique names deduplication pipeline (`POST /api/v1/matches/unique-names`).
   - Reuses the configured browser and Miami-Dade tab across unique names (`Name 1` ➔ Complete Miami-Dade ➔ `Name 2` ➔ Complete Miami-Dade ➔ `Name 3` ➔ Complete Miami-Dade).

3. **Step-by-Step Portal Navigation & Authentication (Sections 3, 4, 5):**
   - **Open Miami-Dade (`navigate_to_search`):** Navigates to configured Miami-Dade portal URL, waits for DOM content, and automatically reloads/retries if a blank page body is detected.
   - **Login Workflow (`ensure_authenticated`):** Checks for authenticated session tokens (`"Welcome,"`, `"My Desk"`, `"Logout"`). Skips login if already authenticated.
     - **Step A:** Locates and clicks "Register/Login", waiting for login form.
     - **Step B:** Verifies login inputs and enters User ID and Password dynamically from Settings.
     - **Step C:** Clicks "LOGIN" button and waits for navigation.
     - **Step D:** Dismisses browser "Save your password" bubble/dialog (via Escape key / prompt dismissal) without blocking execution.
   - **Verify Portal URL (`verify_portal_url`):** Verifies that the tab redirects/remains at the configured portal URL (`self.base_url`), navigating back if diverted to identity provider services.

4. **Search Workflow (Section 6):**
   - **Step A (`select_party_search_tab`):** Clicks "Party Name" tab / radio selector.
   - **Step B:** Clicks "Refresh" button to reset form state cleanly.
   - **Step C:** Fills First Name, Last Name, and Filing Date Range From (`#filingDateFrom`) using current unique name only.
   - **Step D:** Clicks "Search" button.
   - **Step E:** Waits for result container/grid to fully load with the 50s parity wait ceiling.
   - **Step F (`verify_and_enable_table_view`):** Checks if "Table View" is active; clicks and enables Table View if not active.
   - **Step G (All-Column Extraction):** Discovers all column headers dynamically (`thead th`) and extracts Local Case Number, State Case Number, Section, Case Type, Filing Date, Case Status, Case Style, plus any extra discovered columns, with Card View fallback.
   - **Step H (DataTables Pagination):** Traverses all DataTables pages via `#tblResults_next:not(.disabled) a` without stopping at page 1.
   - **Step I (`check_and_dismiss_search_criteria_popup`):** Detects "YOUR SEARCH CRITERIA" modal dialogues, clicks Close/X button or presses Escape, and smoothly resumes without error.
   - **Step J (Database Persistence):** Returns case dictionaries normalized for `fl_jsonbody_miami` on `ClaimRecord` and persists to `ScrapedCourtCase` ORM models.

5. **Tab Reuse and Lifecycle (Sections 7 & 8):**
   - Implemented `return_to_search_state(page)` to clear input fields and reset the form for the next unique name without re-logging in.
   - Closes browser and tabs only after all unique names complete for the queue record.

---

## 2. Modified & Created Files

| File | Type | Changes |
|---|---|---|
| `backend/app/automation/florida/miami.py` | Modified | Added safe await helpers, `navigate_to_search`, `ensure_authenticated` (Steps A–D), `verify_portal_url`, `select_party_search_tab` (Steps A & B), `check_and_dismiss_search_criteria_popup`, `verify_and_enable_table_view` (Step F), dynamic table header discovery, and DataTables pagination loop. |
| `backend/tests/test_miami_portal.py` | Created | Added 11 comprehensive unit and workflow tests verifying Steps A–J, login steps, popup dismissal, Table View enable, all-column extraction, pagination, tab reuse, and persistence. |
| `implementation_plan/2026-09-25_uaic_miami_dade_county_portal_workflow_implementation-plan_v1.md` | Updated | Updated plan metadata to Complete / Approved by User. |
| `implementation_plan/2026-09-25_uaic_miami_dade_county_portal_workflow_implementation-record_v1.md` | Created | Documented implementation details and compliance matrix. |
| `implementation_plan/2026-09-25_uaic_miami_dade_county_portal_workflow_test-report_v1.md` | Created | Full test results report across unit, integration, and regression suites. |
| `implementation_plan/2026-09-25_uaic_miami_dade_county_portal_workflow_validation_v1.md` | Created | Step-by-step verification and requirements traceability matrix. |
| `AGENTS.md` | Updated | Updated test count to 500 tests across 61 test suites. |

---

## 3. Verification Summary

- **Miami-Dade Dedicated Tests:** 11/11 passed in 3.67s (`pytest tests/test_miami_portal.py`).
- **Full Backend Suite:** 500/500 tests passed across 61 test suites (100% pass rate).
- **Backend Code Quality:** 0 Ruff errors (`ruff check app tests`).
- **Frontend Type Safety:** 0 TypeScript compiler errors (`npx tsc --noEmit`).
- **PowerShell Syntax Check:** 0 syntax errors across all 10 scripts (`check_ps1_syntax.ps1`).
- **Core Orchestrator Files:** `setup_local.ps1` and `docker-compose.yml` verified intact.
