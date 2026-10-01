# Implementation Plan — Hillsborough Down Search & Miami-Dade Navbar Party Name Selection

**Implementation ID:** IMP-2026-0925-007  
**Project:** UAIC Claim & RPA Orchestrator  
**Module:** County Court Scrapers / Hillsborough County (FL) & Miami-Dade County (FL)  
**Feature / Issue:** Down Search Button & Party/Business Name Verification (Hillsborough) + Navigation Menu "Party Name" Selection (Miami-Dade)  
**Document Type:** Implementation Plan  
**Version:** v1  
**Status:** Complete  
**Created:** 2026-09-25  
**AI Agent:** Antigravity  
**AI Verification:** Complete (100% Automated Testing Suite)  

---

## 1. Executive Summary & Problem Diagnosis

Based on live operational analysis of the court scraping workflows on `hover.hillsclerk.com` (Hillsborough) and `https://www2.miamidadeclerk.gov/ocs` (Miami-Dade), two specific behavioral gaps were identified in the automation scrapers:

1. **Hillsborough County (`hover.hillsclerk.com`):**
   - **Diagnosis:** The scraper was using a broad locator (`#btnSubmitPartySearch, #partySearchBtn, button:has-text('Search'), input[value='Search']`) with `.first.click()`. Because the portal header / navigation area contains search buttons and buttons containing the word "Search" earlier in document order (including the "Search by Party or Business Name" tab itself), `.first.click()` clicked the top search button instead of the submit button at the bottom of the data fields.
   - **Requirement:**
     1. Always check that **"Search by Party or Business Name"** is selected/active before filling data. If not selected, click/select it and verify active state.
     2. Fill the party inputs (`spLastName`, `spFirstName`, `spDateFiledAfter`).
     3. Click the **down search button** (`#btnSubmitPartySearch` / bottom search button below the form fields) to retrieve court cases, never the top search button.

2. **Miami-Dade County (`https://www2.miamidadeclerk.gov/ocs`):**
   - **Diagnosis:** In the Miami-Dade OCS portal, the search categories are hosted in the primary navigation menu / navbar (`Home`, `Single Case Search`, `Local Case`, `State Case`, `Multiple Case Search`, `Party Name`, `Hearings`, `Suggestions`, `Submit Feedback`). The previous scraper targeted generic selectors or radio buttons without explicitly clicking "Party Name" from the Navigation Menu / navbar. If "Party Name" is not clicked from the navbar, the party search panel (`#nameSearch`) is not expanded, causing data filling and case extraction to fail or fall back.
   - **Requirement:**
     1. Explicitly select or click **"Party Name"** from the Navigation Menu / navbar (`a[href*='#nameSearch']`, `nav a:has-text('Party Name')`, `.navbar a:has-text('Party Name')`, `ul.nav a:has-text('Party Name')`, `li:has-text('Party Name') a`).
     2. If a responsive/collapsed navigation menu exists (e.g. `button.navbar-toggler`), expand it if needed before selecting "Party Name".
     3. Verify that the Party Name search section (`#nameSearch` / `#txtLastName`) is displayed/active.
     4. Proceed to click Refresh, fill party inputs, and execute search.

---

## 2. Technical Architecture & Implementation Steps

### 2.1 Hillsborough County (`backend/app/automation/florida/hillsborough.py`)
1. **Hardened `select_party_search_tab(page)`:**
   - Verify if "Search by Party or Business Name" is already active:
     - Check if `#spLastName` is visible and enabled.
     - Check if `#nav-Party-tab`, `button:has-text('Search by Party or Business Name')`, or `[aria-controls*='Party']` has `.active`, `aria-selected="true"`, or `checked`.
   - If not active, click `#nav-Party-tab, button:has-text('Search by Party or Business Name'), a:has-text('Search by Party or Business Name')`.
   - Wait for `#spLastName` to be visible with an explicit confirmation log: `"Step C: 'Search by Party or Business Name' verified selected and active."`
2. **Explicit Down Search Button Click in `search_by_party_name`:**
   - Replace generic `.first.click()` with targeted down search selection:
     ```python
     # Step E: Click Down Search Button
     t_sub_start = datetime.now()
     down_search_btn = page.locator(
         "#btnSubmitPartySearch, "
         "#nav-Party #btnSubmitPartySearch, "
         "#nav-Party button[type='submit'], "
         "#nav-Party button.btn-success:has-text('Search'), "
         "#nav-Party button:has-text('Search'), "
         "form#partySearchForm button:has-text('Search')"
     )
     if await _safe_count(down_search_btn) > 0 and await _safe_is_visible(down_search_btn):
         logger.info(f"[{self.county_name}] Step E: Clicking down search button (#btnSubmitPartySearch)...")
         await down_search_btn.last.click()
     else:
         fallback_btn = page.locator("#btnSubmitPartySearch, #partySearchBtn, button:has-text('Search'), input[value='Search']")
         if await _safe_count(fallback_btn) > 0:
             logger.info(f"[{self.county_name}] Step E: Clicking down search button (fallback last)...")
             await fallback_btn.last.click()
     ```
   - Guarantees the button clicked is the submit button below the form fields, never the top search button.

### 2.2 Miami-Dade County (`backend/app/automation/florida/miami.py`)
1. **Explicit Navigation Menu "Party Name" Click in `select_party_search_tab(page)`:**
   - Detect collapsed responsive navbar toggler (`button.navbar-toggler, button[aria-label='Toggle navigation'], .navbar-toggle, button:has-text('Menu')`). If visible and navbar links are hidden, click toggler to reveal the menu.
   - Click "Party Name" specifically targeting the Navigation Menu / navbar:
     ```python
     # Step A: Click "Party Name" from Navigation Menu / Navbar
     nav_party_link = page.locator(
         "nav a:has-text('Party Name'), "
         ".navbar a:has-text('Party Name'), "
         "a[href*='#nameSearch'], "
         "a[href*='nameSearch'], "
         "ul.nav a:has-text('Party Name'), "
         "li:has-text('Party Name') a, "
         "a:has-text('Party Name'), "
         "button:has-text('Party Name')"
     )
     ```
   - Click the navigation item and wait for the Party Search panel (`#nameSearch`, `#txtLastName`) to become visible:
     ```python
     await nav_party_link.first.click()
     await page.wait_for_timeout(1000)
     last_input = page.locator("#txtLastName, input[name='txtLastName']")
     await last_input.first.wait_for(state="visible", timeout=15000)
     ```
   - Step B: Click "Refresh" button if present to reset inputs.
   - Verify `#txtLastName` is ready for input before data filling.

---

## 3. Testing & Verification Strategy

1. **Unit & Workflow Tests:**
   - Update `backend/tests/test_hillsborough_portal.py`:
     - Test that `select_party_search_tab` strictly verifies "Search by Party or Business Name" is active.
     - Test that `search_by_party_name` clicks the down search button (`#btnSubmitPartySearch` / `.last`) and not any top button.
   - Update `backend/tests/test_miami_portal.py`:
     - Test that `select_party_search_tab` clicks "Party Name" from the navigation menu / navbar (`nav a:has-text('Party Name')`, `a[href*='#nameSearch']`).
     - Test that responsive navbar toggler is handled if collapsed.
2. **Regression Testing:**
   - Run `tests/test_hillsborough_portal.py` and `tests/test_miami_portal.py`.
   - Run full regression suite: `.venv\Scripts\pytest --tb=short -q` (confirming all 527+ tests pass).
   - Run `ruff check app tests` (0 errors).
   - Run `npx tsc --noEmit` (0 errors).
   - Run `check_ps1_syntax.ps1` (0 errors).
   - Verify `setup_local.ps1` and `docker-compose.yml` remain unmodified and intact.

---

## 4. Deliverables Checklist

- [ ] Implementation Plan: `implementation_plan/2026-09-25_uaic_hillsborough_down_search_and_miami_navbar_workflow_implementation-plan_v1.md`
- [ ] Code modifications: `backend/app/automation/florida/hillsborough.py`
- [ ] Code modifications: `backend/app/automation/florida/miami.py`
- [ ] Test updates: `backend/tests/test_hillsborough_portal.py`
- [ ] Test updates: `backend/tests/test_miami_portal.py`
- [ ] Implementation Record: `implementation_plan/2026-09-25_uaic_hillsborough_down_search_and_miami_navbar_workflow_implementation-record_v1.md`
- [ ] Test Report: `implementation_plan/2026-09-25_uaic_hillsborough_down_search_and_miami_navbar_workflow_test-report_v1.md`
- [ ] Validation Document: `implementation_plan/2026-09-25_uaic_hillsborough_down_search_and_miami_navbar_workflow_validation_v1.md`
- [ ] Update `AGENTS.md` test counts
