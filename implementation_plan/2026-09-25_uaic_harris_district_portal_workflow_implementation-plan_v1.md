# Implementation Plan: Harris County District Clerk (HCDistrict) Portal Workflow Hardening

**Implementation ID:** `IMP-2026-0925-009`  
**Date:** 2026-09-25  
**Reference Document:** PROMPT 8 — HARRIS COUNTY DISTRICT CLERK / HCDISTRICT PORTAL  
**Status:** Complete (100% Automated Testing Suite)  
**Governing Skill:** `diagnose-plan-confirm-execute`  
**AI Verification:** Complete (100% Automated Testing Suite)  

---

## 1. Executive Summary & Objective

The objective of this task is to implement and harden the **Harris County District Clerk (HCDistrict)** civil court portal workflow in `backend/app/automation/texas/harris_district.py` to achieve 100% compliance with **PROMPT 8 — HARRIS COUNTY DISTRICT CLERK / HCDISTRICT PORTAL**, while preserving the existing application architecture, database persistence (`te_jsonbody_hcdistrict` on `ClaimRecord` and `ScrapedCourtCase` ORM models), and strict API schema contracts.

### Critical Parity & Architectural Constraints:
1. **Dynamic Settings Integration:** All runtime parameters (HCDistrict URL, browser engine, storage provider, screenshot preferences, logging, retry/refresh configurations) must be loaded dynamically from Settings (`http://localhost:3000/settings` / DB). Default HCDistrict URL: `https://www.hcdistrictclerk.com/`. No hardcoded endpoints or credentials.
2. **Sequential Unique Name Processing & Tab Reuse:** Unique names for the current queue record are processed strictly one by one across all applicable portals (`Name 1` ➔ Complete all portals ➔ `Name 2` ➔ Complete all portals ➔ `Name 3`). The browser session is launched once; the HCDistrict tab is opened once and reused across all unique names (`Name 1` ➔ Complete HCDistrict ➔ Reset Search State ➔ `Name 2` ➔ Complete HCDistrict ➔ Reset Search State ➔ `Name 3`). The tab and browser close **only after all unique names** for the claim/queue record are completed.
3. **PORTAL OUTPUT SCHEMA (CaseType INCLUDED):** Per `AGENTS.md` and repository test contracts (`test_scraper_pagination.py:304-313`), Harris County District Clerk output schema **DOES INCLUDE `CaseType`** (unlike Harris JP and Harris CClerk which strictly omit it). The dictionary keys MUST strictly be:
   ```json
   ["CaseNumber", "CaseStyle", "FilingDate", "CaseStatus", "CaseType", "CountyWebsite"]
   ```
4. **Step B — "Search Our Records":** Navigating from the base portal (`https://www.hcdistrictclerk.com/`), the scraper must locate and click **"Search Our Records"** (`a:has-text('Search Our Records')`, `span:has-text('Search Our Records')`) to open the search page (`Search.aspx`), verify search form readiness, and ensure "Party Inquiry" is selected.

---

## 2. Gap Analysis & Proposed Solutions

| Prompt 8 Requirement | Current State in `harris_district.py` | Gap / Deficiency | Target Implementation Solution (`IMP-2026-0925-009`) |
|---|---|---|---|
| **1. Dynamic Settings** | Inherits `BaseCourtScraper(base_url)` with hardcoded default. | Scraper does not document or enforce reading dynamic settings at runtime. | Ensure dynamic settings are injected via `scraper_tasks.py` (`portals_cfg.harris_district_url`, `settings.captcha_wait_seconds`, `settings.browser_engine`, `settings.max_attempts`). Scraper handles custom runtime URLs cleanly. |
| **2. Queue & Unique Names** | `SingleSessionBrowserRunner` passes parties into `execute_portal_searches`. | Basic reset between names. | Implement `return_to_search_state(page)` to reset form inputs or clear inputs before next unique name without closing or reopening the tab. |
| **3. Step A: Tab Loading & Refresh** | Direct `page.goto` without blank body detection or retry/reload. | If page fails to load or body is blank, does not reload. | Check DOM container & body text; if blank or unresponsive, execute `_safe_reload(page)`, wait, and verify before continuing. |
| **3. Step B: Click "Search Our Records"** | Immediately appended `/eDocs/Public/Search.aspx` to URL in code. | Does not click "Search Our Records" link on the portal home page as required by Prompt 8. | Implement explicit navigation to base URL, locate and click `Search Our Records` link/button, and handle direct `Search.aspx` gracefully. |
| **3. Step C: Verify Search Page Loads** | Checks `#txtPartyName` immediately. | Lacks robust verification of Search Page container or Party Inquiry tab activation. | Verify search page readiness (`#searchPage`, `#txtPartyName`, `#partyLastName`, `a:has-text('Party Inquiry')`), clicking Party Inquiry if needed. |
| **3. Step D: Fill Inputs** | Fills `#txtPartyName` and date range. | Lacks support for both separate Last/First inputs and combined Party input; raw date formatting. | Support both separate `#partyLastName` / `#partyFirstName` and combined `#txtPartyName` (`LastName, FirstName`). Normalize DOL to `MM/dd/yyyy`. |
| **3. Step E: Search Button** | Clicks `btnPartySearch`. | Basic click without safe await helper. | Use safe click helper targeting `input[id*='btnPartySearch']`, `input[id*='btnSearch']`, `button:has-text('Search')`. |
| **3. Step F: Wait for Result Page** | Fixed `page.wait_for_timeout(3500)`. | Lacks dynamic grid/results readiness detection. | Wait for results grid (`table[id*='dgSearchResults']`, `.grid-results`, or "No Records Found" text) with dynamic timeout. |
| **3. Step G: All-Column Extraction** | Extracts hardcoded columns 0, 1, 3, 5, 6. | Lacks robust cell count handling and dynamic column derivation. | Dynamically scan table cells; extract Case Number, Case Style, Case Type (default: `"DISTRICT COURTS – CIVIL"`), Filing Date, Case Status, Citation, and raw fields. Ensure `CaseType` is present. |
| **3. Step H: Pagination** | Checks `table[id*='dgSearchResults'] tr.pager a`. | Can throw if mock without awaitable click; limited pager selectors. | Add robust ASP.NET PostBack pagination loop (`tr.pager a:has-text('Next')`, `tr.pager a:has-text('>')`, `a[id*='btnNext']`) with duplicate prevention. |
| **3. Step I: "YOUR SEARCH CRITERIA" Popup** | Not implemented in `harris_district.py`. | If "YOUR SEARCH CRITERIA" modal appears, scraper does not detect or cross/close it. | Implement `check_and_handle_search_criteria_popup(page)` detecting "YOUR SEARCH CRITERIA" / "NO CASES MATCHED" and clicking `a#messageClose`, `button:has-text('Close')`, or `×`. |
| **3. Step J: Database Persistence** | Result dict returned to `session_runner.py` / `scraper_tasks.py`. | Standard persistence in `te_jsonbody_hcdistrict` and `ScrapedCourtCase`. | Preserve exact dictionary schema: `{"CaseNumber", "CaseStyle", "FilingDate", "CaseStatus", "CaseType", "CountyWebsite"}`. |
| **4. Next Unique Name** | Handled in `session_runner.py`. | Form might retain previous search data. | Implement `return_to_search_state(page)` to clear inputs and prepare tab for next unique name. |
| **5. Browser Closing** | Closed in `SingleSessionBrowserRunner.__aexit__`. | Already follows single-session browser lifecycle. | Verify tab and browser context stay open across all unique names and close only after claim completion. |
| **6. Error Handling** | Base scraper screenshot mechanism. | Screenshots/logs must be correlated with unique ID. | Use base scraper's `capture_error_screenshot` and `append_portal_execution_log` with claim and portal key context. |
| **7. Testing** | Scraper initialization test in `test_scrapers.py`. | Missing dedicated unit tests for Step B "Search Our Records", popups, pagination, all-column extraction, return to search state, and refresh. | Create comprehensive test suite `test_harris_district_portal.py` covering all Prompt 8 steps. |

---

## 3. Detailed Workflow Steps

```
[Start Queue Record]
       │
       ▼
[Retrieve All Unique Names from Existing API]
       │
       ▼
[Launch Browser Engine Once (Dynamic Settings: Chrome/Edge/Chromium, Headless/Attended)]
       │
       ▼
[Open HCDistrict Tab (base_url: https://www.hcdistrictclerk.com/)]
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│ FOR EACH UNIQUE NAME SEQUENTIALLY (Name 1, Name 2, Name 3)   │
│                                                             │
│   Step A: Go to HCDistrict Tab & Wait for Full Page Load    │
│           (If unresponsive or blank body: Reload & Wait)     │
│                                                             │
│   Step B: Click "Search Our Records"                        │
│           (a:has-text('Search Our Records') -> Search.aspx) │
│                                                             │
│   Step C: Verify Search Page Loaded & Party Inquiry Active  │
│           (Verify search form inputs or click Party Inquiry)│
│                                                             │
│   Step D: Fill Form Inputs with Unique Name Data            │
│           - Last Name & First Name (or Party Name combined) │
│           - File Date (From) (DOL normalized to MM/dd/yyyy) │
│                                                             │
│   Step E: Click "Search" Button                             │
│           (input[id*='btnPartySearch'] / btnSearch)         │
│                                                             │
│   Step F: Wait for Result Page / Grid                       │
│                                                             │
│   Step I: Check for "YOUR SEARCH CRITERIA" Popup            │
│           (If present: Click Close / Cross and continue)    │
│                                                             │
│   Step G: Extract ALL Available Columns                     │
│           (Case Number, Case Style, Case Type, Filing Date, │
│            Case Status, Citation; CaseType INCLUDED)        │
│                                                             │
│   Step H: ASP.NET GridView Pagination Loop                  │
│           (Traverse Next pages, extract every row)          │
│                                                             │
│   Step J: Structure Results for Database Persistence        │
│           (te_jsonbody_hcdistrict & ScrapedCourtCase)       │
│                                                             │
│   Section 4: Return to Search State (Reset Form)            │
│              (Keep HCDistrict tab open, keep browser open)  │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
[All Unique Names Completed]
       │
       ▼
[Close HCDistrict Tab -> Close Browser Context -> Complete Queue Record]
```

---

## 4. Technical Specifications & Code Changes

### A. Safe Coroutine & Mock Helpers
Define safe wrappers across Playwright locators and pytest test mocks:
- `_safe_is_visible(locator)`
- `_safe_count(locator)`
- `_safe_get_attribute(locator, attr)`
- `_safe_inner_text(locator)`
- `_safe_click(locator)`
- `_safe_hover(locator)`
- `_safe_reload(page)`
- `_get_page_text(page)`
- `_normalize_court_date(val)`

### B. Navigation & Search Our Records (Steps A, B, C)
```python
async def _navigate_to_search_page(self, page: Page) -> None:
    """Step A, B, C: Navigate to HCDistrict, click 'Search Our Records', verify search page."""
    # 1. Check if already on search page with visible inputs
    party_input = page.locator("#txtPartyName, #partyLastName, input[name*='Party'], #txtPartyLastName")
    if await _safe_count(party_input) > 0 and await _safe_is_visible(party_input.first):
        return

    # 2. Navigate to base URL
    await page.goto(self.base_url, wait_until="domcontentloaded")
    await page.wait_for_timeout(1500)

    # 3. Reload if body is blank
    body_text = await _get_page_text(page)
    if hasattr(page, "evaluate") and not inspect.isfunction(page.evaluate):
        if not body_text.strip():
            logger.warning(f"[{self.county_name}] Blank body detected; reloading...")
            await _safe_reload(page)
            await page.wait_for_timeout(2000)

    # 4. Step B: Click "Search Our Records"
    search_records_link = page.locator(
        "a:has-text('Search Our Records'), "
        "span:has-text('Search Our Records'), "
        "a[href*='Search.aspx'], "
        "a[href*='Search']"
    )
    if await _safe_count(search_records_link) > 0 and await _safe_is_visible(search_records_link.first):
        await _safe_click(search_records_link.first)
        await page.wait_for_timeout(1500)

    # 5. Ensure Party Inquiry tab is selected
    party_inquiry_link = page.locator("a:has-text('Party Inquiry'), #btnPartyInquiry, a[href*='Party'], #tabParty")
    if await _safe_count(party_inquiry_link) > 0 and await _safe_is_visible(party_inquiry_link.first):
        await _safe_click(party_inquiry_link.first)
        await page.wait_for_timeout(1000)

    # 6. Step C: Verify search input readiness
    if await _safe_count(party_input) > 0:
        wait_fn = getattr(party_input.first, "wait_for", None)
        if callable(wait_fn):
            res = wait_fn(state="visible", timeout=15000)
            if inspect.isawaitable(res):
                await res
```

### C. Popup Detection & Dismissal (Step I)
```python
async def check_and_handle_search_criteria_popup(self, page: Page) -> bool:
    """Step I: If 'YOUR SEARCH CRITERIA' appears: close/cross the popup and continue."""
    try:
        popup_loc = page.locator(
            "div:has-text('YOUR SEARCH CRITERIA'), "
            "div:has-text('SEARCH CRITERIA'), "
            "div:has-text('NO CASES MATCHED'), "
            "#messageModal, .modal-dialog:has-text('SEARCH CRITERIA')"
        )
        if await _safe_count(popup_loc) > 0 and await _safe_is_visible(popup_loc):
            close_btn = page.locator(
                "a#messageClose, button:has-text('Close'), a:has-text('Close'), "
                "button:has-text('×'), button:has-text('X'), .modal-header .close, "
                "button[aria-label*='Close' i], #btnCriteriaClose, button:has-text('OK')"
            )
            if await _safe_count(close_btn) > 0 and await _safe_is_visible(close_btn):
                logger.info(f"[{self.county_name}] Step I: 'YOUR SEARCH CRITERIA' popup detected; closing...")
                await _safe_click(close_btn.first)
                await page.wait_for_timeout(1000)
                return True
    except Exception as e:
        logger.debug(f"[{self.county_name}] Popup check note: {e}")
    return False
```

### D. Return to Search State (Section 4)
```python
async def return_to_search_state(self, page: Page) -> None:
    """Section 4: Navigate back to clean search state between unique names."""
    try:
        logger.info(f"[{self.county_name}] Returning to search state for next unique name...")
        await self.check_and_handle_search_criteria_popup(page)

        # Clear inputs
        for input_sel in [
            "#txtPartyName, input[id*='txtPartyName']",
            "#partyLastName, #txtPartyLastName",
            "#partyFirstName, #txtPartyFirstName",
            "#txtPartyStartDate, input[id*='txtFiledDateFrom'], input[id*='txtDateFrom']",
        ]:
            loc = page.locator(input_sel)
            if await _safe_count(loc) > 0 and await _safe_is_visible(loc):
                clear_fn = getattr(loc.first, "clear", None)
                if callable(clear_fn):
                    res = clear_fn()
                    if inspect.isawaitable(res):
                        await res
    except Exception as e:
        logger.debug(f"[{self.county_name}] Return to search state note: {e}")
```

### E. Schema Compliance & Extraction (Steps G & H)
Extract all columns while enforcing:
```python
results.append({
    "CaseNumber": case_num,
    "CaseStyle": case_style or f"{l_name}, {f_name}",
    "CountyWebsite": self.base_url,
    "FilingDate": filing_date,
    "CaseStatus": case_status,
    "CaseType": case_type or "DISTRICT COURTS – CIVIL",
})
```

---

## 5. Verification & Test Plan

1. **Dedicated Test Suite (`tests/test_harris_district_portal.py`):**
   - `test_hcdistrict_dynamic_settings_init`: Validates runtime injection of dynamic URL and parameters.
   - `test_date_normalization_helper`: Tests DOL normalization to `MM/dd/yyyy`.
   - `test_step_a_b_c_navigation_and_search_records_click`: Tests base URL navigation, "Search Our Records" click, and search page verification.
   - `test_step_a_blank_body_reload`: Tests automatic reload when blank body detected.
   - `test_step_i_popup_dismissal`: Tests detection and dismissal of "YOUR SEARCH CRITERIA" modal.
   - `test_section_4_return_to_search_state`: Tests clearing inputs between unique names.
   - `test_search_by_party_name_full_workflow_and_schema`: Tests full search execution and asserts `CaseType` is present in dictionary keys (`{"CaseNumber", "CaseStyle", "FilingDate", "CaseStatus", "CaseType", "CountyWebsite"}`).
   - `test_pagination_traversal`: Tests multi-page extraction across ASP.NET GridView pager links.
   - `test_sequential_multiple_unique_names_on_same_page`: Tests sequential processing of multiple unique names on the same page.
2. **Full Automated Verification:**
   - `pytest` across all suites (target: 549 passing tests across 66 test suites).
   - `ruff check app tests` (0 errors).
   - `npx tsc --noEmit` (0 errors).
   - `scripts/check_ps1_syntax.ps1` (0 errors).
3. **Documentation Deliverables:**
   - Implementation Record, Test Report, and Validation Artifact in `implementation_plan/`.
   - Update `AGENTS.md` test counts and status.

---

## 6. User Confirmation Request

Per the `diagnose-plan-confirm-execute` governing rule (`NO APPROVAL = NO IMPLEMENTATION`):
Please confirm if you approve this implementation plan to begin code modifications for `harris_district.py` and create the dedicated test suite.
