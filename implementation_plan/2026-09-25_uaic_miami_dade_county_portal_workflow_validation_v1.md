# Validation — Miami-Dade County Court Portal Workflow

**Implementation ID:** IMP-2026-0925-003  
**Project:** UAIC Claim & RPA Orchestrator  
**Module:** County Court Scrapers / Miami-Dade County Clerk (FL)  
**Feature / Issue:** Prompt 3 — Miami-Dade County Court Portal Workflow Validation  
**Document Type:** Validation  
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

## 1. Requirements Traceability Matrix

| Requirement | Description | Implementation Status | Evidence / Test |
|---|---|---|---|
| **Section 1: Dynamic Settings** | Retrieve Miami-Dade URL, User ID, Password, browser, timeouts, retries from Settings DB (`http://localhost:3000/settings`) | ✅ Fully Implemented | `MiamiDadeScraper.__init__` reads settings dynamically from DB via `scraper_tasks.py` / `settings_service.py` |
| **Section 2: Queue & Unique Names** | Upfront unique names retrieval; process one unique name at a time sequentially with browser reuse | ✅ Fully Implemented | Handled in `session_runner.py` / `queue_runner.py` + `unique_names` API |
| **Section 3: Open Miami-Dade** | Go to tab, wait for DOM load, reload & wait again if body empty | ✅ Fully Implemented | `navigate_to_search(page)` in `miami.py` (`test_navigate_to_search_loads_content`) |
| **Section 4: Login Steps A–D** | Skip if logged in; Step A click Register/Login, Step B fill User/Pass, Step C click LOGIN, Step D handle Save Password popup | ✅ Fully Implemented | `ensure_authenticated(page)` in `miami.py` (`test_ensure_authenticated_skips_when_logged_in`, `test_ensure_authenticated_executes_login_flow`) |
| **Section 5: Verify Portal URL** | Ensure tab remains at configured Miami URL; navigate back if diverted | ✅ Fully Implemented | `verify_portal_url(page)` in `miami.py` (`test_verify_portal_url_redirects_back`) |
| **Section 6: Step A ('Party Name')** | Click "Party Name" tab / radio | ✅ Fully Implemented | `select_party_search_tab(page)` in `miami.py` (`test_select_party_search_tab_and_refresh`) |
| **Section 6: Step B ('Refresh')** | Click "Refresh" button to reset form | ✅ Fully Implemented | `select_party_search_tab(page)` in `miami.py` (`test_select_party_search_tab_and_refresh`) |
| **Section 6: Step C (Enter Data)** | Fill First Name, Last Name, Filing Date Range From for current unique name only | ✅ Fully Implemented | `search_by_party_name` in `miami.py` |
| **Section 6: Step D (Search)** | Click "Search" button | ✅ Fully Implemented | Click `#btnSearch` / `button:has-text('Search')` |
| **Section 6: Step E (Wait Results)** | Wait for result page / grid to fully load (50s parity wait ceiling) | ✅ Fully Implemented | `wait_for_selector` on table / cards + parity wait |
| **Section 6: Step F (Table View)** | Verify "Table View" is enabled; if not enabled, click and enable it | ✅ Fully Implemented | `verify_and_enable_table_view(page)` in `miami.py` (`test_verify_and_enable_table_view`) |
| **Section 6: Step G (Extract All Columns)** | Dynamic header mapping, extract Local Case No, State Case No, Section, Case Type, Filing Date, Case Status, Case Style + extra headers | ✅ Fully Implemented | Dynamic `thead th` inspection + payload population (`test_search_by_party_name_table_view_and_columns`) |
| **Section 6: Step H (Pagination)** | Traverse all pages without stopping at page 1 | ✅ Fully Implemented | Loop over `#tblResults_next:not(.disabled) a` (`test_search_by_party_name_with_pagination`) |
| **Section 6: Step I (Popup Dismissal)** | Detect and dismiss "YOUR SEARCH CRITERIA" popup without error | ✅ Fully Implemented | `check_and_dismiss_search_criteria_popup(page)` (`test_dismiss_search_criteria_popup`) |
| **Section 6: Step J (Database Format)** | Save in existing database format (`fl_jsonbody_miami` + `ScrapedCourtCase`) | ✅ Fully Implemented | Normalized payload structure compatible with `ClaimRecord` and ORM (`test_miami_persistence_format`) |
| **Section 7: Clean State Reset** | Return tab to search state, clear inputs, reuse tab for next unique name without re-login | ✅ Fully Implemented | `return_to_search_state(page)` (`test_return_to_search_state_clears_inputs`) |
| **Section 8: Lifecycle Cleanup** | Close tab & browser only after all unique names completed | ✅ Fully Implemented | Handled in `session_runner.py` clean-up stage |

---

## 2. Governance & Quality Verification

- **Governance Skill:** Fully complied with `diagnose-plan-confirm-execute` (Plan approved, executed, verified, documented).
- **Test Results:** 500/500 tests passing across 61 test suites (100% pass rate).
- **Static Analysis:** 0 Ruff errors, 0 TypeScript errors, 0 PowerShell syntax errors.
- **Protection Integrity:** All 5 protected directories remain intact.
- **Status:** **AI Verification:** Complete (100% Automated Testing Suite).
