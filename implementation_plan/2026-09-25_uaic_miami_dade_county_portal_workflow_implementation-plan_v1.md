# Implementation Plan — Miami-Dade County Court Portal Workflow

**Implementation ID:** IMP-2026-0925-003  
**Project:** UAIC Claim & RPA Orchestrator  
**Module:** County Court Scrapers / Miami-Dade County Clerk (FL)  
**Feature / Issue:** Prompt 3 — Miami-Dade County Portal Workflow Implementation & Hardening  
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

The objective is to implement and harden the Miami-Dade County civil court portal workflow (`MiamiDadeScraper` in `backend/app/automation/florida/miami.py`) using the existing application architecture, without rebuilding the scraper, without duplicate authentication/configuration logic, and without breaking existing database or Guidewire schemas.

The workflow must:
1. Dynamically retrieve all configurations from Settings (`http://localhost:3000/settings` / DB). Never hardcode credentials.
2. In the queue runner, retrieve all unique names upfront from the Unique Names API.
3. Launch the browser once, open the Miami-Dade portal tab, and process unique names sequentially one-by-one (`Name 1` -> Complete -> `Name 2` -> Complete -> `Name 3` -> Complete), keeping the browser open between unique names.
4. Open the Miami-Dade tab, wait for load, and reload/retry if blank or unresponsive.
5. Only perform login if the account is NOT already logged in:
   - **Step A:** Click "Register/Login", wait for page load.
   - **Step B:** Verify login page loads; fill User ID / Email and Password from Settings.
   - **Step C:** Click "LOGIN", wait for page load.
   - **Step D:** Dismiss/handle browser "Save your password" popup if it appears without blocking the workflow.
6. Verify portal URL: ensure the tab remains or redirects to configured Miami-Dade portal (`https://www2.miamidadeclerk.gov/ocs`); navigate back if diverted to identity provider.
7. Execute Search Workflow:
   - **Step A:** Click "Party Name".
   - **Step B:** Click "Refresh".
   - **Step C:** Fill First Name, Last Name, and Filing Date Range From (using current unique name only).
   - **Step D:** Click "Search".
   - **Step E:** Wait for result page to load (50s parity wait ceiling).
   - **Step F:** Verify "Table View" is enabled; if not enabled, click and enable it.
   - **Step G:** Extract ALL available columns (Local Case Number, State Case Number, Section, Case Type, Filing Date, Case Status, Case Style, and any additional columns from headers).
   - **Step H:** Extract ALL paginated data without stopping at page 1.
   - **Step I:** If "YOUR SEARCH CRITERIA" popup appears, close popup and continue workflow without error.
   - **Step J:** Save results using existing database format (`fl_jsonbody_miami` on `ClaimRecord` and `ScrapedCourtCase` rows with `raw_payload`).
8. Return tab to search state between unique names, keep browser open, and process next unique name without re-authenticating unnecessarily.
9. Close browser and tabs only after ALL unique names complete for the queue record.

---

## 2. Gap Analysis & Proposed Architectural Upgrades

| Requirement Section | Current Implementation in `miami.py` | Required Prompt 3 Implementation | Gap / Action Required |
|---|---|---|---|
| **Section 1: Dynamic Settings** | Reads `portals_cfg.miami_url`, `username`, `password`, `requires_login` via `scraper_tasks.py` | Must dynamically read from `SystemSettingsModel` (`http://localhost:3000/settings`) without hardcoded values | ✅ Preserved and reinforced; fallback defaults align with settings schema |
| **Section 2: Sequential Queue** | Single session runner iterates parties | Retrieve unique names upfront, run sequentially on open Miami tab | ✅ Reused across unique names; return to clean search state between names |
| **Section 3: Open Miami-Dade** | Direct `page.goto` with 1s timeout | Wait for DOM content; if blank or not loaded, reload & re-wait | ⚠️ Add `navigate_to_search(page)` with blank-body detection and reload backoff |
| **Section 4: Login Steps A–D** | Naive inline login check (`page_text` inner text) | Check authenticated state first; if not logged in: Step A click "Register/Login", Step B fill User/Pass, Step C click "LOGIN", Step D handle "Save your password" popup | ⚠️ Implement `ensure_authenticated(page)` with discrete steps A–D and popup dismissal |
| **Section 5: Verify Portal URL** | Partial check for `usermanagementservices` | Verify URL is at configured Miami portal; navigate back if redirected | ⚠️ Add explicit `verify_portal_url(page)` step |
| **Section 6: Search Steps A–D** | Clicks `rdoPerson`, fills inputs, submits | Step A: Click "Party Name", Step B: Click "Refresh", Step C: Fill inputs, Step D: Click "Search" | ⚠️ Implement Step A ("Party Name") and Step B ("Refresh") before data entry |
| **Section 6: Step F (Table View)** | Extracts from Card View only | Verify "Table View" is enabled; if not, click and enable Table View | ⚠️ Implement Step F Table View detection and auto-toggle |
| **Section 6: Step G & H (Columns & Pagination)** | Extracts fixed card labels, 10-page limit | Extract ALL available columns dynamically from table headers + full pagination | ⚠️ Extract from Table View dynamically (Local Case No, State Case No, Section, Case Type, Filing Date, Case Status, etc.) with card view fallback |
| **Section 6: Step I (Criteria Popup)** | No popup dismissal | Detect "YOUR SEARCH CRITERIA" popup, close it, and continue | ⚠️ Add `check_and_dismiss_search_criteria_popup(page)` |
| **Section 7: Tab Reset & Reuse** | Does not reset inputs between party runs | Clear inputs, re-assert Party Name search state, keep tab open | ⚠️ Implement `return_to_search_state(page)` |

---

## 3. Detailed Technical Implementation Steps

### 3.1. Safe Await Helpers (`backend/app/automation/florida/miami.py`)
Add `_safe_is_visible`, `_safe_count`, `_safe_get_attribute`, and `_safe_inner_text` helpers to ensure Playwright async locators and `unittest.mock.MagicMock` objects evaluate safely without `TypeError: 'MagicMock' object can't be awaited`.

### 3.2. Step 3: Open Miami-Dade Navigation (`navigate_to_search`)
- Navigate to `self.base_url`.
- Wait for `#content`, `main`, `#main-content`, `form`, or `body`.
- Inspect body inner text; if empty/blank, trigger `page.reload(wait_until="domcontentloaded")` with parity backoff.

### 3.3. Step 4 & 5: Authenticated Session & Login (`ensure_authenticated`, `verify_portal_url`)
- Check logged-in indicators: `"Welcome,"`, `"My Desk"`, `"Logout"`, `"Sign Out"`, `#lnkLogout`.
- If already logged in: log info and proceed.
- If not logged in and credentials provided:
  - **Step A:** Locate and click "Register/Login" (`a:has-text('Register/Login')`, `button:has-text('Register/Login')`, `#lnkLogin`, `a[href*='Login' i]`). Wait for login form.
  - **Step B:** Verify login inputs exist (`#txtUserName`, `input[type='email']`, `#txtPassword`, `input[type='password']`). Fill `self.username` and `self.password`.
  - **Step C:** Click "LOGIN" (`#btnLogin`, `button:has-text('LOGIN')`, `input[type='submit'][value*='Login' i]`).
  - **Step D:** Dismiss "Save your password" bubble/dialog (send Escape key, dismiss password prompt modals if present).
- Verify portal URL: if tab redirected to `usermanagementservices` or login portal, navigate back to `self.base_url`.

### 3.4. Step 6: Search Workflow (`search_by_party_name`)
- Check and dismiss any leftover "YOUR SEARCH CRITERIA" dialog.
- **Step A:** Click "Party Name" tab / radio (`a:has-text('Party Name')`, `button:has-text('Party Name')`, `#rdoPerson`, `label:has-text("Person's Name")`).
- **Step B:** Click "Refresh" (`button:has-text('Refresh')`, `a:has-text('Refresh')`, `#btnRefresh`, `input[value*='Refresh' i]`) to reset form state.
- **Step C:** Fill First Name, Last Name, and Filing Date Range From (`#filingDateFrom`).
- **Step D:** Click "Search" (`#btnSearch`, `button:has-text('Search')`, `input[type='submit'][value*='Search' i]`).
- **Step E:** Wait for result container (`#tblResults`, `table.table`, `.card-body`, `.case-card`, `#partyResultsTable`, `.dataTables_empty`, `div:has-text('No records found')`) with 50s wait ceiling.
- Dismiss any "YOUR SEARCH CRITERIA" popup appearing after search submission (Step I).
- **Step F:** Verify "Table View" is active:
  - Check if table is visible. If not visible and Table View toggle exists (`button:has-text('Table View')`, `a:has-text('Table View')`, `button[title*='Table' i]`, `a[title*='Table' i]`, `#btnTableView`), click it.
- **Step G & H:** Extract ALL columns across ALL pages:
  - Table rows discovery with dynamic `thead th` header extraction.
  - Extract: Local Case Number, State Case Number, Section, Case Type, Filing Date, Case Status, Case Style, and any additional columns.
  - Card view fallback parsing to ensure zero data loss.
  - Full DataTables / Pagination traversal until next button is disabled.
- **Step J:** Format results for `fl_jsonbody_miami` and `ScrapedCourtCase`.
- **Section 7:** Call `return_to_search_state(page)` to clear search inputs and re-assert the Party Name view for the next unique name.

---

## 4. Verification and Testing Strategy

1. **Dedicated Test Suite (`backend/tests/test_miami_portal.py`):**
   - `test_navigate_to_search_loads_content`: Tests DOM wait and blank body reload.
   - `test_ensure_authenticated_skips_when_logged_in`: Verifies no-op when already authenticated.
   - `test_ensure_authenticated_login_flow`: Tests Step A click Register/Login, Step B fill credentials, Step C submit, Step D save-password dismissal.
   - `test_verify_portal_url_redirects_back`: Tests redirection back to OCS portal if left on identity provider.
   - `test_dismiss_search_criteria_popup`: Tests popup detection and dismissal.
   - `test_search_by_party_name_table_view_and_columns`: Tests Step A (Party Name), Step B (Refresh), Step C (Inputs), Step D (Search), Step F (Table View), Step G (all-column extraction).
   - `test_search_by_party_name_pagination`: Tests Step H traversal across multiple pages.
   - `test_return_to_search_state`: Tests Section 7 tab reset between unique names.
   - `test_miami_database_persistence_format`: Tests Step J database format alignment.
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
- [x] Unique Implementation ID assigned (`IMP-2026-0925-003`).
- [x] Preserve existing API contracts, database keys (`fl_jsonbody_miami`), and Guidewire models.
- [x] All 5 protected directories remain intact.
