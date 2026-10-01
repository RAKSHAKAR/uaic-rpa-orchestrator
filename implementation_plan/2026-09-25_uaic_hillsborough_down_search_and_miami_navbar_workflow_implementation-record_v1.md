# Implementation Record — Hillsborough Down Search & Miami-Dade Navbar Party Name Selection

**Implementation ID:** IMP-2026-0925-007  
**Project:** UAIC Claim & RPA Orchestrator  
**Module:** County Court Scrapers / Hillsborough County (FL) & Miami-Dade County (FL)  
**Feature / Issue:** Down Search Button & Party/Business Name Verification (Hillsborough) + Navigation Menu "Party Name" Selection (Miami-Dade)  
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

In direct accordance with the user's feedback and requirements, the court automation scrapers for Hillsborough County (`hover.hillsclerk.com`) and Miami-Dade County (`https://www2.miamidadeclerk.gov/ocs`) were hardened to address precise navigational and button interaction behavior:

### 1.1 Hillsborough County (`hover.hillsclerk.com`)
1. **Always Verify "Search by Party or Business Name" is Selected & Active:**
   - Updated `select_party_search_tab(page)` to explicitly check if `#spLastName` is visible and enabled, and whether `#nav-Party-tab` / `button:has-text('Search by Party or Business Name')` is active.
   - If not active, clicks the tab/button/radio (`#nav-Party-tab`, `button:has-text('Search by Party or Business Name' i)`, `a:has-text('Search by Party or Business Name' i)`) and waits for `#spLastName` to be visible and ready before proceeding.
   - Logs: `Step C: 'Search by Party or Business Name' is verified active.`
2. **Click Down Search Button After Filling Data:**
   - Identified that previous generic selector `#btnSubmitPartySearch, #partySearchBtn, button:has-text('Search'), input[value='Search']` with `.first.click()` clicked the top search button because buttons matching "Search" exist earlier in DOM order.
   - Replaced with targeted down search button selection (`#btnSubmitPartySearch`, `#nav-Party #btnSubmitPartySearch`, `#nav-Party button.btn-success:has-text('Search')`, `form#partySearchForm button:has-text('Search')`, or `.last.click()`).
   - Implemented `_safe_click` helper to safely await Playwright coroutines while supporting mock test runners without type errors.
   - Logs: `Step E: Clicking down search button (#btnSubmitPartySearch)...`

### 1.2 Miami-Dade County (`https://www2.miamidadeclerk.gov/ocs`)
1. **Click "Party Name" from Navigation Menu / Navbar:**
   - In Miami-Dade OCS portal, the search categories are hosted in the primary navigation menu / navbar (`Home`, `Single Case Search`, `Local Case`, `State Case`, `Multiple Case Search`, `Party Name`, `Hearings`, `Suggestions`, `Submit Feedback`).
   - Updated `select_party_search_tab(page)` to:
     - Detect and expand responsive mobile navigation toggler (`button.navbar-toggler, button[aria-label='Toggle navigation'], .navbar-toggle, button:has-text('Menu')`) if the navbar links are collapsed.
     - Specifically click "Party Name" from the Navigation Menu / navbar (`nav a:has-text('Party Name')`, `.navbar a:has-text('Party Name')`, `a[href*='#nameSearch']`, `a[href*='nameSearch']`, `ul.nav a:has-text('Party Name')`, `li:has-text('Party Name') a`).
     - Wait for the Party Search panel (`#nameSearch`, `#txtLastName`) to expand and become visible.
     - Click "Refresh" if available to reset form inputs.
     - Verify `#txtLastName` is ready before proceeding to data filling.

---

## 2. File Change Log

| File | Change Description |
|---|---|
| `backend/app/automation/florida/hillsborough.py` | Hardened `select_party_search_tab` to verify "Search by Party or Business Name" selection; updated Step E in `search_by_party_name` to target down search button (`#btnSubmitPartySearch` / `.last`); added `_safe_click` helper. |
| `backend/app/automation/florida/miami.py` | Updated `select_party_search_tab` to handle responsive navbar toggler and click "Party Name" from the Navigation Menu / navbar (`nav a:has-text('Party Name')`, `a[href*='#nameSearch']`); added `_safe_click` helper. |
| `backend/tests/test_hillsborough_portal.py` | Updated search button mocks and loc_side_effect; added 2 dedicated unit tests (`test_hillsborough_down_search_button_clicked_not_top_search`, `test_hillsborough_always_checks_party_business_name_selected`). Total 10 tests passing. |
| `backend/tests/test_miami_portal.py` | Added 2 dedicated unit tests (`test_miami_selects_party_name_from_navbar_menu`, `test_miami_expands_responsive_navbar_when_collapsed`). Total 13 tests passing. |
| `AGENTS.md` | Updated baseline test count to 531 tests across 64 test suites. |

---

## 3. Automated Verification Results

- **Hillsborough Dedicated Suite:** 10 passed in 5.06s (100%)
- **Miami-Dade Dedicated Suite:** 13 passed in 2.23s (100%)
- **Full Backend Regression Suite:** 531 passed across 64 suites in 146.52s (100%)
- **Backend Linting (`ruff`):** 0 errors
- **Frontend TypeScript (`tsc`):** 0 errors
- **PowerShell Syntax Validator (`ps1`):** 0 errors
- **Launcher Integrity:** `setup_local.ps1` and `docker-compose.yml` verified clean & unmodified.
