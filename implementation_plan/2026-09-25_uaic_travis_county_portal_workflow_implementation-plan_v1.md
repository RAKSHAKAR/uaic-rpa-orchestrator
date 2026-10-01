# Implementation Plan — Travis County Court Portal Workflow

**Implementation ID:** IMP-2026-0925-004  
**Project:** UAIC Claim & RPA Orchestrator  
**Module:** County Court Scrapers / Travis County Odyssey Portal (TX)  
**Feature / Issue:** Prompt 4 — Travis County Portal Workflow Implementation & Hardening  
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

The objective is to implement and harden the Travis County civil court portal workflow (`TravisScraper` in `backend/app/automation/texas/travis.py`) using the existing application architecture, without rebuilding the scraper, and without breaking existing database or Guidewire schemas.

The workflow must:
1. Dynamically retrieve all configurations from Settings (`http://localhost:3000/settings` / DB), including Travis portal URL (`https://odysseyweb.traviscountytx.gov/Portal/`), browser engine, CAPTCHA wait seconds, max retry/refresh attempts, storage provider, screenshots, and logging.
2. In the queue runner, retrieve all unique names upfront from the Unique Names API.
3. Launch the browser once, open the Travis tab, and process unique names strictly one by one (`Name 1` -> Complete -> `Name 2` -> Complete -> `Name 3` -> Complete), keeping the browser open between unique names.
4. Execute the complete Travis search workflow:
   - **Step A:** Go to Travis tab, wait for page to fully load; refresh and wait again if not loaded correctly.
   - **Step B:** Click "Smart Search".
   - **Step C:** Verify that the page loads.
   - **Step D:** Enter required current unique-name data into Search Input.
   - **Step E & H:** CAPTCHA integration using dynamically configured "CAPTCHA Resolution Wait (Seconds)". Wait for verification result.
   - **Step F:** If CAPTCHA verification fails/times out: refresh page, wait for load, return to search state, re-enter current search data, and retry up to configured Max Retry & Refresh Attempts without silently proceeding.
   - **Step G:** Detect "Session timeout warning" modal; if it appears, click "Continue session", wait for page, resume from appropriate step, and preserve current unique name.
   - **Step I:** Once CAPTCHA verification succeeds, immediately click "Submit".
   - **Step J:** Wait for result page/grid to load.
   - **Step K:** Extract ALL available columns: Case Number, Case Style, Case Type, Filing Date, Case Status, Access Level, and any additional fields dynamically discovered from table headers.
   - **Step L:** Extract all result pages and records across Kendo UI pagination without stopping at page 1.
   - **Step M:** Save using existing database format (`te_jsonbody_travis` on `ClaimRecord` and `ScrapedCourtCase` rows with full `raw_payload`).
5. Return tab to search state between unique names, keep browser open, and process next unique name without relaunching browser.
6. Close browser and tabs only after ALL unique names complete for the queue record.

---

## 2. Gap Analysis & Proposed Architectural Upgrades

| Requirement Section | Current Implementation in `travis.py` | Required Prompt 4 Implementation | Gap / Action Required |
|---|---|---|---|
| **Section 1: Dynamic Settings** | Reads `portals_cfg.travis_url` via `scraper_tasks.py` | Must dynamically read from `SystemSettingsModel` (`http://localhost:3000/settings`), including CAPTCHA wait & Max Retries | ✅ Preserved; ensure `captcha_wait_seconds` and `max_attempts` govern the retry loop |
| **Section 2: Sequential Queue** | Session runner iterates parties | Process strictly one by one on single open tab, keep browser open | ✅ Reused across unique names; return to clean search state between names |
| **Section 3: Step A (Open Travis)** | Direct `page.goto` to `Dashboard/29` with 1.5s timeout | Wait for DOM content; if blank or not loaded, reload & re-wait | ⚠️ Add `navigate_to_search(page)` with blank-body detection and reload backoff |
| **Section 3: Steps B & C (Smart Search)** | Navigates directly via URL | Step B: Click "Smart Search", Step C: Verify page loads | ⚠️ Implement `click_smart_search(page)` and `verify_search_page_loaded(page)` |
| **Section 3: Step D (Search Input)** | Directly fills `#caseCriteria_SearchCriteria` | Enter current unique-name data into Search Input | ✅ Reinforced with biometric typing |
| **Section 3: Step G (Session Timeout)** | No session timeout detection | Detect "Session timeout warning" and click "Continue session" | ⚠️ Implement `check_and_handle_session_timeout(page)` before and during waits |
| **Section 3: Steps E, F, H (CAPTCHA Retry Loop)** | Single CAPTCHA attempt; returns `[]` on timeout | Use configured CAPTCHA wait seconds, retry on failure with page refresh & re-entry up to Max Retry Attempts | ⚠️ Implement full CAPTCHA retry/refresh loop respecting `captcha_wait_seconds` and `max_attempts` |
| **Section 3: Step I (Submit)** | Clicks `#btnSSSubmit` | Immediately click "Submit" once CAPTCHA succeeds | ✅ Preserved and reinforced |
| **Section 3: Step J, K (Extract All Columns)** | Extracts 5 hardcoded fields | Extract ALL available columns: Case Number, Case Style, Case Type, Filing Date, Case Status, Access Level, and any extra headers | ⚠️ Add dynamic header discovery (`thead th, .k-grid-header th`) and include `AccessLevel` |
| **Section 3: Step L (Pagination)** | Multi-page loop | Extract all result pages and records without stopping at page 1 | ✅ Preserved and reinforced |
| **Section 4: Next Unique Name** | Simple reset link click at end | Return to Travis search, keep tab open, process next name | ⚠️ Implement `return_to_search_state(page)` |

---

## 3. Detailed Technical Implementation Steps

### 3.1. Safe Await Helpers (`backend/app/automation/texas/travis.py`)
Add `_safe_is_visible`, `_safe_count`, `_safe_get_attribute`, and `_safe_inner_text` helpers to ensure Playwright async locators and `unittest.mock.MagicMock` objects evaluate safely without `TypeError: 'MagicMock' object can't be awaited`.

### 3.2. Step A: Open Travis (`navigate_to_search`)
- Navigate to `self.base_url`.
- Wait for DOM readiness (`main`, `.wrapper`, `#content`, `body`).
- Inspect body inner text; if blank/empty, reload with backoff.

### 3.3. Steps B & C: Smart Search Navigation (`click_smart_search`, `verify_search_page_loaded`)
- Check if already on Smart Search page (`#caseCriteria_SearchCriteria` visible).
- If not on search input view:
  - Locate and click "Smart Search" (`a:has-text('Smart Search')`, `button:has-text('Smart Search')`, `#tcControllerLink_0`, `a[href*='Dashboard/29']`).
  - Wait for Smart Search container to load.
- Verify Search Input (`#caseCriteria_SearchCriteria, #SearchCriteria, input[name='caseCriteria_SearchCriteria']`) is visible.

### 3.4. Step G: Session Timeout Guard (`check_and_handle_session_timeout`)
- Inspect for modal dialogs containing: `"Session timeout warning"`, `"extend your session"`, `"Continue session"`.
- If detected: click `"Continue session"` button (`button:has-text('Continue session')`, `a:has-text('Continue session')`), wait for page, resume search.

### 3.5. Steps D, E, F, H, I: Search Input & CAPTCHA Retry Loop
- Enter current unique-name query: `query = f"{l_name},{f_name}".strip(", ")`.
- For attempt `1` to `self.max_attempts`:
  - Fill search input with `self.biometric_fill(search_input.first, query)`.
  - Check for session timeout warning.
  - Execute `self.detect_and_handle_captcha(page, wait_seconds=self.captcha_wait_seconds)`.
  - If CAPTCHA verified:
    - Step I: Immediately click **"Submit"** (`#btnSSSubmit, input#btnSSSubmit, input[type='submit'][value*='Submit' i]`).
    - Break out of CAPTCHA retry loop.
  - If CAPTCHA verification fails/times out:
    - Log warning: `f"[Travis County (TX)] CAPTCHA attempt {attempt}/{self.max_attempts} failed."`.
    - If `attempt < self.max_attempts`:
      - Refresh page (`page.reload(wait_until="domcontentloaded")`).
      - Wait for reload backoff.
      - Return to search state and re-enter data.
    - If `attempt == self.max_attempts`:
      - Do NOT silently continue as though CAPTCHA succeeded; record stage timeout and return `[]`.

### 3.6. Steps J, K, L, M: Results, All-Column Extraction, Pagination & Persistence
- Wait for results grid (`.k-grid-content tbody tr, table.k-selectable tbody tr, table tbody tr`) or "no cases match your search" banner with 50s wait ceiling.
- Discover all column headers dynamically (`thead th, .k-grid-header th`).
- Extract: Case Number, Case Style (sanitized), Case Type, Filing Date, Case Status, Access Level, plus any extra discovered headers into the dictionary.
- Traverse all Kendo UI pagination pages (`.k-pager-wrap a[title='Go to the next page']:not(.k-state-disabled)`) until all pages are extracted.
- Call `return_to_search_state(page)` to prepare tab for next unique name.
- Store results for `te_jsonbody_travis` and `ScrapedCourtCase`.

---

## 4. Verification and Testing Strategy

1. **Dedicated Test Suite (`backend/tests/test_travis_portal.py`):**
   - `test_navigate_to_search_loads_content`: Tests DOM wait and blank body reload.
   - `test_click_smart_search_and_verify_page`: Tests clicking "Smart Search" and verifying input readiness.
   - `test_check_and_handle_session_timeout`: Tests detecting and clicking "Continue session".
   - `test_search_input_entry`: Tests filling Search Input with current unique name.
   - `test_captcha_success_and_immediate_submit`: Tests CAPTCHA success followed immediately by Submit.
   - `test_captcha_failure_and_retry_loop`: Tests reload & retry up to Max Retry Attempts on CAPTCHA failure.
   - `test_captcha_timeout_returns_empty`: Verifies failure returns `[]` without silent success.
   - `test_extract_all_columns_including_access_level`: Tests extraction of Case Number, Case Style, Case Type, Filing Date, Case Status, Access Level, and dynamic headers.
   - `test_pagination_traversal`: Tests multi-page Kendo UI traversal.
   - `test_return_to_search_state`: Tests tab reset between unique names.
   - `test_travis_persistence_format`: Tests `te_jsonbody_travis` database compatibility.
2. **Regression Testing:**
   - Execute full backend test suite (`pytest --tb=short -q`) ensuring 100% pass rate.
   - Execute `ruff check app tests` ensuring 0 errors.
   - Execute frontend TypeScript check (`npx tsc --noEmit`) ensuring 0 errors.
   - Execute PowerShell syntax checks (`scripts\check_ps1_syntax.ps1`) ensuring 0 errors.
   - Validate `setup_local.ps1` and `docker-compose.yml` integrity.

---

## 5. Governance Checklist
- [x] No code modifications before explicit user approval.
- [x] Implementation Plan saved to `implementation_plan/`.
- [x] Unique Implementation ID assigned (`IMP-2026-0925-004`).
- [x] Preserve existing API contracts, database keys (`te_jsonbody_travis`), and Guidewire models.
- [x] All 5 protected directories remain intact.
