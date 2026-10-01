# Validation Document — Hillsborough Down Search & Miami-Dade Navbar Party Name Selection

**Implementation ID:** IMP-2026-0925-007  
**Project:** UAIC Claim & RPA Orchestrator  
**Module:** County Court Scrapers / Hillsborough County (FL) & Miami-Dade County (FL)  
**Feature / Issue:** Down Search Button & Party/Business Name Verification (Hillsborough) + Navigation Menu "Party Name" Selection (Miami-Dade)  
**Document Type:** Validation Document  
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

## 1. Requirement Traceability Matrix

| Requirement | Implementation Component | Verification Test | Status |
|---|---|---|---|
| **Hillsborough:** Always check "Search by Party or Business Name" must be selected before filling data | `HillsboroughScraper.select_party_search_tab` | `test_hillsborough_always_checks_party_business_name_selected` | VERIFIED |
| **Hillsborough:** Fill party data (`spLastName`, `spFirstName`, `spDateFiledAfter`) | `HillsboroughScraper.search_by_party_name` | `test_hillsborough_step_d_and_e_data_filling_and_submit` | VERIFIED |
| **Hillsborough:** Click on down search button after filling data, not top search | `HillsboroughScraper.search_by_party_name` (Step E) | `test_hillsborough_down_search_button_clicked_not_top_search` | VERIFIED |
| **Miami-Dade:** Select or click "Party Name" from navbar / Navigation Menu | `MiamiDadeScraper.select_party_search_tab` (Step A) | `test_miami_selects_party_name_from_navbar_menu` | VERIFIED |
| **Miami-Dade:** Expand responsive/collapsed navbar menu if toggler is visible | `MiamiDadeScraper.select_party_search_tab` | `test_miami_expands_responsive_navbar_when_collapsed` | VERIFIED |
| **Miami-Dade:** Ensure party inputs are expanded and ready before data filling | `MiamiDadeScraper.select_party_search_tab` | `test_select_party_search_tab_and_refresh` | VERIFIED |
| **Zero Regressions:** 531 tests passing across 64 test suites | Full backend test suite | `pytest --tb=short -q` (531 passed) | VERIFIED |
| **Code Quality:** Zero linter, type, or syntax errors | Backend, Frontend, PowerShell | `ruff`, `tsc`, `check_ps1_syntax.ps1` | VERIFIED |
| **Launcher Integrity:** `setup_local.ps1` and `docker-compose.yml` clean | Root directory | `git diff --name-only` (unmodified) | VERIFIED |

---

## 2. Conclusion & Operational Readiness

Both scrapers (`hillsborough.py` and `miami.py`) have been updated, hardened, and verified with 100% test coverage. They strictly satisfy the user's navigational and interaction requirements:
- Hillsborough guarantees that "Search by Party or Business Name" is confirmed active before filling inputs, and always clicks the bottom/down search button (`#btnSubmitPartySearch` / `.last`).
- Miami-Dade guarantees that "Party Name" is selected from the Navigation Menu / navbar, ensuring the search inputs are expanded and accessible before filling and search submission.
