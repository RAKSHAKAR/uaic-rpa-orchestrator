# Implementation Plan — Dallas County Court Portal Workflow

**Implementation ID:** IMP-2026-0925-005  
**Project:** UAIC Claim & RPA Orchestrator  
**Module:** County Court Scrapers / Dallas County Odyssey Portal (TX)  
**Feature / Issue:** Prompt 5 — Dallas County Portal Workflow Implementation & Hardening  
**Document Type:** Implementation Plan  
**Version:** v1  
**Status:** Complete  
**AI Verification:** Complete (100% Automated Testing Suite)  
**Created:** 2026-09-25  
**Last Updated:** 2026-09-25  
**AI Agent:** Antigravity  
**Approval Status:** Approved by User  
**Approved By:** User  
**Approval Date:** 2026-09-25  

---

## 1. Problem Statement & Objective

The objective is to implement and harden the Dallas County civil court portal workflow (`DallasScraper` in `backend/app/automation/texas/dallas.py`) using the existing application architecture, without rebuilding the scraper, and without breaking existing database or Guidewire schemas.

The workflow must:
1. Dynamically retrieve all configurations from Settings (`http://localhost:3000/settings` / DB), including Dallas portal URL (`https://courtsportal.dallascounty.org/DALLASPROD/Home/`), browser engine, CAPTCHA wait seconds, max retry/refresh attempts, storage provider, screenshots, and logging.
2. In the queue runner, retrieve all unique names upfront from the Unique Names API.
3. Launch the browser once, open the Dallas tab, and keep the browser and tab open across unique names.
4. Process unique names strictly **one by one sequentially** (`Name 1` ➔ Complete Dallas ➔ `Name 2` ➔ Complete Dallas ➔ `Name 3` ➔ Complete Dallas). Never process unique names concurrently.
5. Search workflow:
   - **Step A:** Go to Dallas tab, wait for load, reload & wait again if body empty or unresponsive.
   - **Step B:** Click "Smart Search".
   - **Step C:** Verify Smart Search page loads.
   - **Step D:** Enter current unique-name data into Search Input (`LastName,FirstName`).
   - **Step E & H:** CAPTCHA integration respecting dynamically configured "CAPTCHA Resolution Wait (Seconds)".
   - **Step F:** On CAPTCHA failure/timeout, reload page, re-enter query, and retry up to "Max Retry & Refresh Attempts" without silently proceeding.
   - **Step G:** Detect Tyler Technologies "Session timeout warning" modal; if present, click "Continue session", wait for page, and resume without losing party state or advancing to next name.
   - **Step I:** After successful CAPTCHA verification, immediately click "Submit" (`#btnSSSubmit`).
   - **Step J:** Wait for results page (wait for grid or "No cases match your search" with parity wait ceiling).
   - **Step K:** Extract ALL available columns: Case Number, Case Style (sanitized of `[-\\/|]` matching V4 parity), Case Type, Filing Date, Case Status, Access Level, and any dynamic custom headers.
   - **Step L:** Extract all result pages and records across Kendo UI pagination without stopping at page 1.
   - **Step M:** Save using existing database format (`te_jsonbody_dallas` on `ClaimRecord` and `ScrapedCourtCase` ORM rows).
6. Return tab to Dallas search between unique names (`return_to_search_state(page)`), keep browser open, and process next unique name without relaunching browser.
7. Close browser and tabs only after ALL unique names complete for the queue record.

---

## 2. Gap Analysis & Proposed Architectural Upgrades

| Requirement Section | Current Implementation in `dallas.py` | Required Prompt 5 Implementation | Gap / Action Required |
|---|---|---|---|
| **Section 1: Dynamic Settings** | Reads `portals_cfg.dallas_url` via `scraper_tasks.py` | Must dynamically read from `SystemSettingsModel` (`http://localhost:3000/settings`), including CAPTCHA wait & Max Retries | ✅ Preserved; ensure `captcha_wait_seconds` and `max_attempts` govern the retry loop |
| **Section 2: Queue & Unique Names** | Queue runner processes claims; names processed in loop | Must process unique names strictly one-by-one sequentially on dedicated Dallas tab with browser reuse | ✅ Enforce sequential tab reuse; verify no concurrent name runs |
| **Section 3: Step A (Navigate & Reload)** | Direct `page.goto` without blank body detection | Navigate to Dallas portal, wait for DOM content; if blank or unresponsive, reload and wait | ⚠️ Implement `navigate_to_search(page)` with `_get_page_text` and `_safe_reload` |
| **Section 3: Steps B & C (Smart Search)** | Appends `/Dashboard/29` directly to URL | Explicitly click "Smart Search" link/button and verify `#caseCriteria_SearchCriteria` visibility | ⚠️ Implement `click_smart_search(page)` and `verify_search_page_loaded(page)` |
| **Section 3: Step D (Search Input)** | Fills `caseCriteria_SearchCriteria` | Biometric data entry with formatted `LastName,FirstName` into SearchCriteria | ✅ Refactor into standardized Step D |
| **Section 3: Step G (Session Timeout)** | Missing | Detect Tyler Technologies "Session timeout warning" modal, click "Continue session", wait, and resume current search | ⚠️ Implement `check_and_handle_session_timeout(page)` |
| **Section 3: Steps E, F, H (CAPTCHA Loop)** | Single attempt; returns `[]` on failure | Multi-attempt retry loop respecting `captcha_wait_seconds` and `max_attempts`; reloads page, returns to search, re-enters name, retries | ⚠️ Implement structured CAPTCHA retry/refresh loop with TIMEOUT stage recording |
| **Section 3: Step I (Immediate Submit)** | Clicks `#btnSSSubmit` | Immediately click "Submit" after CAPTCHA verification succeeds | ✅ Ensure immediate click without extraneous delays |
| **Section 3: Step J (Result Wait)** | 25 iterations (10s) wait | Dynamic predicate wait loop with 50s wait ceiling for grid rows or "No cases match" | ✅ Harden wait loop to 50s ceiling with timeout modal guard |
| **Section 3: Step K (All-Column Extraction)** | Extracts 5 hardcoded columns | Extract Case Number, Case Style (sanitized of `[-\\/|]`), Case Type, Filing Date, Case Status, Access Level, and any dynamic headers discovered from `thead th` | ⚠️ Implement dynamic header discovery and Access Level extraction |
| **Section 3: Step L (Multi-Page Pagination)** | Breaks at page > 10; uses `all_inner_texts` | Traverse all Kendo UI pagination pages (`.k-pager-wrap a[title='Go to the next page']`) up to safety ceiling with dual cell extraction (`all_inner_texts` + individual cell fallback) | ⚠️ Standardize pagination loop with dual extraction and 10-page ceiling |
| **Section 3: Step M (Database Persistence)** | Saves to `te_jsonbody_dallas` | Preserves `te_jsonbody_dallas` format and `ScrapedCourtCase` ORM persistence | ✅ Preserved strictly |
| **Section 4: Next Unique Name** | Clicks `#tcControllerLink_0` | Structured `return_to_search_state(page)`: clears inputs, checks timeout, prepares for next name | ⚠️ Implement `return_to_search_state(page)` |
| **Section 5: Browser Teardown** | Session runner closes browser | Closes browser and tabs only after all unique names complete | ✅ Preserved via session runner lifecycle |

---

## 3. Step-by-Step Implementation Details

### Step 3.1: Harden `backend/app/automation/texas/dallas.py`
1. **Safe Await Helpers:**
   - Include safe inspect helpers: `_safe_is_visible`, `_safe_count`, `_safe_get_attribute`, `_safe_inner_text`, `_safe_reload`, `_get_page_text`.
2. **`navigate_to_search(self, page: Page)` (Step A):**
   - Navigate to base URL, append `/Dashboard/29` if navigating directly, wait for `domcontentloaded`.
   - Check page body text; if blank/empty, reload via `_safe_reload(page)` and wait.
3. **`click_smart_search(self, page: Page)` & `verify_search_page_loaded(self, page: Page)` (Steps B & C):**
   - Check if search criteria input is already visible; if not, click "Smart Search" link/button (`#tcControllerLink_0`, `a:has-text('Smart Search')`, etc.).
   - Wait for `#caseCriteria_SearchCriteria` to become visible within timeout.
4. **`check_and_handle_session_timeout(self, page: Page) -> bool` (Step G):**
   - Detect modal text matching "Session timeout warning" / "extend your session".
   - Click "Continue session", wait 1500ms, return `True`.
5. **`return_to_search_state(self, page: Page)` (Section 4):**
   - Clear search input if present, check for session timeout modal, or click "Smart Search" controller link to reset view cleanly for next unique name.
6. **`search_by_party_name(...)` (Steps D through M):**
   - Format query: `LastName,FirstName`.
   - CAPTCHA loop:
     - For attempt in `1..max_attempts`:
       - Check session timeout modal.
       - Enter search query using `biometric_fill` (Step D).
       - Wait for CAPTCHA using `captcha_wait_seconds` (Steps E & H).
       - If verified: break loop and proceed to Step I.
       - If failed: record TIMEOUT stage, reload page via `_safe_reload`, wait backoff, click Smart Search, and retry (Step F).
     - If not verified after max attempts: return `[]`.
   - Immediate Submit: click `#btnSSSubmit` (Step I).
   - Result Wait: poll for results grid or "no cases match your search" with timeout modal checking (Step J).
   - All-Column Extraction: dynamically discover `thead th` headers; extract Case Number, Case Style (sanitized), Case Type, Filing Date, Case Status, Access Level, and discovered headers (Step K). Support both `all_inner_texts` and individual cell fallback.
   - Multi-Page Pagination: traverse Kendo UI pager up to 10 pages (Step L).
   - Clean state return: invoke `return_to_search_state(page)` (Section 4).

### Step 3.2: Create Dedicated Test Suite `backend/tests/test_dallas_portal.py`
Create unit and workflow tests verifying:
1. `test_navigate_to_search_loads_content`: Navigation and blank page reload (Step A).
2. `test_click_smart_search_and_verify_page`: Smart Search click & page load verification (Steps B & C).
3. `test_check_and_handle_session_timeout`: Session timeout warning detection and "Continue session" (Step G).
4. `test_return_to_search_state_clears_inputs`: Input reset between unique names (Section 4).
5. `test_captcha_success_and_immediate_submit`: Immediate Submit upon CAPTCHA success (Steps E & I).
6. `test_captcha_failure_and_retry_loop`: Retry/refresh loop on CAPTCHA timeout (Steps F & H).
7. `test_extract_all_columns_including_access_level_and_dynamic_headers`: Discovery of dynamic headers and extraction of all columns including Access Level (Step K).
8. `test_pagination_traversal`: Kendo UI multi-page pagination traversal (Step L).
9. `test_dallas_persistence_format`: Strict schema conformance matching `te_jsonbody_dallas` (Step M).

---

## 4. Verification & Validation Plan

### Automated Testing Commands
```bash
# 1. Dedicated Dallas test suite
cd backend
.venv\Scripts\pytest tests/test_dallas_portal.py -v

# 2. Existing pagination regression suites
.venv\Scripts\pytest tests/test_pagination_behavior.py tests/test_scraper_pagination.py -v

# 3. Full backend regression suite (518 tests across 63 suites)
.venv\Scripts\pytest --tb=short -q

# 4. Code quality & linting (0 errors)
.venv\Scripts\ruff check app tests

# 5. Frontend TypeScript check (0 errors)
cd ..\frontend
npx tsc --noEmit

# 6. PowerShell syntax check (0 errors)
cd ..
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"

# 7. Infrastructure integrity check
git status setup_local.ps1 docker-compose.yml
```

---

## 5. Traceability & Governance Deliverables

Upon receiving explicit user approval:
1. Implement changes in `backend/app/automation/texas/dallas.py`.
2. Create test suite in `backend/tests/test_dallas_portal.py`.
3. Execute full automated test suite and static analysis.
4. Update plan status to `Complete` with `**AI Verification:** Complete (100% Automated Testing Suite)`.
5. Generate `implementation_plan/2026-09-25_uaic_dallas_county_portal_workflow_implementation-record_v1.md`.
6. Generate `implementation_plan/2026-09-25_uaic_dallas_county_portal_workflow_test-report_v1.md`.
7. Generate `implementation_plan/2026-09-25_uaic_dallas_county_portal_workflow_validation_v1.md`.
8. Update `AGENTS.md` test counts.
