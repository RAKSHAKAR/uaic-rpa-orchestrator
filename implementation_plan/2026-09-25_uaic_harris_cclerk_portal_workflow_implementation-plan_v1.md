# Implementation Plan: Harris County Clerk (CClerk) Portal Workflow Hardening

**Implementation ID:** `IMP-2026-0925-008`  
**Date:** 2026-09-25  
**Reference Document:** PROMPT 7 — HARRIS COUNTY CLERK / CCLERK PORTAL  
**Status:** Pending User Confirmation  
**Governing Skill:** `diagnose-plan-confirm-execute`  

---

## 1. Executive Summary & Objective

The objective of this task is to implement and harden the **Harris County Clerk (CClerk)** civil court portal workflow in `backend/app/automation/texas/harris_cclerk.py` to achieve 100% compliance with **PROMPT 7 — HARRIS COUNTY CLERK / CCLERK PORTAL**, while preserving the existing application architecture, database persistence (`te_jsonbody_cclerk` on `ClaimRecord` and `ScrapedCourtCase` ORM records), and strict API schema contracts.

### Critical Parity & Architectural Constraints:
1. **Dynamic Settings Integration:** All runtime parameters (CClerk URL, browser engine, storage provider, screenshot preferences, logging, retry/refresh configurations) must be loaded dynamically from Settings (`http://localhost:3000/settings` / DB). Default CClerk URL: `https://www.cclerk.hctx.net/Applications/WebSearch/`. No hardcoded endpoints or credentials.
2. **Sequential Unique Name Processing & Tab Reuse:** Unique names for the current queue record are processed strictly one by one. The browser session is launched once; the CClerk tab is opened once and reused across all unique names (`Name 1` ➔ Complete CClerk ➔ Reset Search State ➔ `Name 2` ➔ Complete CClerk ➔ Reset Search State ➔ `Name 3`). The tab and browser close **only after all unique names** for the claim/queue record are completed.
3. **STRICT SCHEMA ENFORCEMENT (NO `CaseType`):** Per `AGENTS.md` and repository test contracts (`test_scraper_pagination.py:335`, `test_v4_parity.py:201`, `test_attended_unattended_parity.py:94`), Harris County Clerk dictionary keys MUST strictly be:
   ```json
   ["CaseNumber", "CaseStyle", "FilingDate", "CaseStatus", "CountyWebsite"]
   ```
   **`CaseType` MUST NOT be included** in the output dictionary. While raw column extraction captures all table data for telemetry and logging, the final output dictionary returned to Guidewire and persisted in `te_jsonbody_cclerk` must omit `CaseType`.
4. **Preserve Existing Navigation Test Contracts:** Existing tests in `test_harris_cclerk_navigation.py` specifically mock and assert:
   - `_navigate_to_county_civil`: Hovering `a:has-text('COURTS')` when form not visible (`test_tc_hcc_001_courts_nav_hover`).
   - Clicking `a:has-text('County Civil')` (`test_tc_hcc_002_county_civil_link_clicked`).
   - Waiting for `#ctl00_ContentPlaceHolder1_txtLastName` with `wait_for(state="visible", timeout=15000)` (`test_tc_hcc_003_form_wait_for_visible`).
   All existing test mocks and signatures must be strictly preserved.

---

## 2. Gap Analysis & Proposed Solutions

| Prompt 7 Requirement | Current State in `harris_cclerk.py` | Gap / Deficiency | Target Implementation Solution (`IMP-2026-0925-008`) |
|---|---|---|---|
| **1. Dynamic Settings** | Inherits `BaseCourtScraper(base_url)` with hardcoded default. | Scraper does not document or enforce reading dynamic settings at runtime. | Ensure dynamic settings are injected via `scraper_tasks.py` (`portals_cfg.harris_cclerk_url`, `settings.captcha_wait_seconds`, `settings.browser_engine`, `settings.max_attempts`). Scraper handles custom runtime URLs cleanly. |
| **2. Queue & Unique Names** | `SingleSessionBrowserRunner` passes parties into `execute_portal_searches`. | Basic reset between names. | Implement `return_to_search_state(page)` to reset form inputs or click clear/reset before next unique name without closing or reopening the tab. |
| **3. Step A: Tab Loading & Refresh** | Direct `page.goto` without blank body detection or retry/reload. | If page fails to load or body is blank, does not reload. | Check DOM container & body text; if blank or unresponsive, execute `_safe_reload(page)`, wait, and verify before continuing. |
| **3. Step B & C: COURTS -> County Civil** | `_navigate_to_county_civil` hovers "COURTS" and clicks "County Civil". | Works for initial load, but lacks robust checks if already on County Civil search form. | Keep existing logic for backward compatibility with `test_harris_cclerk_navigation.py` while adding resilient fallback selectors and verifying form readiness. |
| **3. Step D: Fill Inputs** | Fills `txtLastName`, `txtFirstName`, `txtDateFrom`. | Basic selectors; lacks safe input verification and date normalization. | Target `#ctl00_ContentPlaceHolder1_txtLastName`, `#ctl00_ContentPlaceHolder1_txtFirstName`, `#ctl00_ContentPlaceHolder1_txtDateFrom`. Normalize date of loss to `MM/dd/yyyy`. |
| **3. Step E: Search Button** | Clicks `#ctl00_ContentPlaceHolder1_btnSearch`. | Basic click without safe await helper. | Use safe click helper targeting `#ctl00_ContentPlaceHolder1_btnSearch`, `input[type='submit'][value*='SEARCH' i]`. |
| **3. Step F: Wait for Result Page** | Fixed `page.wait_for_timeout(3000)`. | Lacks dynamic grid/results readiness detection. | Wait for results grid (`table[id*='grd']`, `table.grid`, `.dataTables_wrapper`, or "No Cases Found" text) with dynamic timeout. |
| **3. Step G: All-Column Extraction** | Extracts hardcoded columns 0, 1, 2, 5. | Does not extract dynamic headers or additional columns like Citation. | Dynamically scan table headers; extract Case Number, Case Style (sanitizing `[-\\/|]`), Filing Date, Case Status, Citation, and raw fields. **Strictly omit `CaseType`** from final dict. |
| **3. Step H: Pagination** | Checks `table[id*='grd'] tr.pager a`. | Can throw if element is mock without awaitable click; limited pager selectors. | Add robust ASP.NET PostBack pagination loop (`tr.pager a`, `a:has-text('Next')`, `a:has-text('>')`) with duplicate prevention. |
| **3. Step I: "YOUR SEARCH CRITERIA" Popup** | Not implemented in `harris_cclerk.py`. | If "YOUR SEARCH CRITERIA" modal appears, scraper does not detect or cross/close it. | Implement `check_and_handle_search_criteria_popup(page)` detecting "YOUR SEARCH CRITERIA" / "NO CASES MATCHED" and clicking `a#messageClose`, `button:has-text('Close')`, or `×`. |
| **3. Step J: Database Persistence** | Result dict returned to `session_runner.py` / `scraper_tasks.py`. | Standard persistence in `te_jsonbody_cclerk` and `ScrapedCourtCase`. | Preserve exact dictionary schema: `{"CaseNumber", "CaseStyle", "FilingDate", "CaseStatus", "CountyWebsite"}`. |
| **4. Next Unique Name** | Handled in `session_runner.py`. | Form might retain previous search data. | Implement `return_to_search_state(page)` to clear inputs and prepare tab for next unique name. |
| **5. Browser Closing** | Closed in `SingleSessionBrowserRunner.__aexit__`. | Already follows single-session browser lifecycle. | Verify tab and browser context stay open across all unique names and close only after claim completion. |
| **6. Testing** | 3 navigation tests in `test_harris_cclerk_navigation.py`. | Missing dedicated unit tests for popup handling, pagination, all-column extraction, return to search state, and refresh. | Create comprehensive test suite `test_harris_cclerk_portal.py` covering all Prompt 7 steps. |

---

## 3. Detailed Workflow Steps

```
[Start Queue Record]
       │
       ▼
[Retrieve All Unique Names]
       │
       ▼
[Launch Browser Engine Once (Dynamic Settings: Chrome/Edge/Chromium, Headless/Attended)]
       │
       ▼
[Open CClerk Tab (base_url: https://www.cclerk.hctx.net/Applications/WebSearch/)]
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│ FOR EACH UNIQUE NAME SEQUENTIALLY (Name 1, Name 2, Name 3)   │
│                                                             │
│   Step A: Go to CClerk Tab & Wait for Full Page Load        │
│           (If unresponsive or blank body: Reload & Wait)     │
│                                                             │
│   Step B: Click "County Civil" inside submenu of "COURTS"   │
│           (Hover "COURTS" -> Click "County Civil")          │
│                                                             │
│   Step C: Verify County Civil Search Page Loaded            │
│           (Verify #ctl00_ContentPlaceHolder1_txtLastName)   │
│                                                             │
│   Step D: Fill Form Inputs with Unique Name Data            │
│           - Last Name                                       │
│           - First Name                                      │
│           - File Date (From) (DOL normalized to MM/dd/yyyy) │
│                                                             │
│   Step E: Click "Search" Button                             │
│           (#ctl00_ContentPlaceHolder1_btnSearch)            │
│                                                             │
│   Step F: Wait for Result Page / Grid                       │
│                                                             │
│   Step I: Check for "YOUR SEARCH CRITERIA" Popup            │
│           (If present: Click Close / Cross and continue)    │
│                                                             │
│   Step G: Extract ALL Available Columns                     │
│           (Case Number, Case Style, Filing Date, Status,    │
│            Citation, dynamic headers; STRICTLY NO CaseType) │
│                                                             │
│   Step H: ASP.NET GridView Pagination Loop                  │
│           (Traverse Next pages, extract every row)          │
│                                                             │
│   Step J: Structure Results for Database Persistence        │
│           (te_jsonbody_cclerk & ScrapedCourtCase)           │
│                                                             │
│   Section 4: Return to Search State (Reset Form)            │
│              (Keep CClerk tab open, keep browser open)      │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
[All Unique Names Completed]
       │
       ▼
[Close CClerk Tab -> Close Browser Context -> Complete Queue Record]
```

---

## 4. Technical Specifications & Code Changes

### A. Safe Coroutine & Mock Helpers
To guarantee zero `TypeError: 'MagicMock' object can't be awaited` across Playwright runtime and pytest mock environments, define safe wrappers:
- `_safe_is_visible(locator)`
- `_safe_count(locator)`
- `_safe_get_attribute(locator, attr)`
- `_safe_inner_text(locator)`
- `_safe_click(locator)`
- `_safe_reload(page)`
- `_get_page_text(page)`

### B. Navigation & Submenu Flow (Steps A, B, C)
```python
async def _navigate_to_county_civil(self, page: Page) -> None:
    """Step A, B, C: Navigate to County Civil search form."""
    form = page.locator("#ctl00_ContentPlaceHolder1_txtLastName, input[name*='txtLastName']")
    
    # If not already visible, navigate to base_url and follow COURTS -> County Civil
    await page.goto(self.base_url, wait_until="domcontentloaded")
    await page.wait_for_timeout(1500)
    
    # Reload if body is blank
    body_text = await _get_page_text(page)
    if not body_text.strip():
        logger.warning(f"[{self.county_name}] Blank page body detected; reloading...")
        await _safe_reload(page)
        await page.wait_for_timeout(2000)
        
    if not await _safe_count(form) > 0 or not await _safe_is_visible(form.first):
        courts_menu = page.locator("a:has-text('COURTS')")
        if await _safe_count(courts_menu) > 0:
            hover_fn = getattr(courts_menu.first, "hover", None)
            if callable(hover_fn):
                res = hover_fn()
                if inspect.isawaitable(res):
                    await res
            await page.wait_for_timeout(500)
        
        civil_link = page.locator("a:has-text('County Civil')")
        if await _safe_count(civil_link) > 0:
            click_fn = getattr(civil_link.first, "click", None)
            if callable(click_fn):
                res = click_fn()
                if inspect.isawaitable(res):
                    await res
            await page.wait_for_timeout(1500)
            
        if await _safe_count(form) > 0:
            wait_fn = getattr(form.first, "wait_for", None)
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
            "#messageModal, .modal-dialog:has-text('SEARCH CRITERIA')"
        )
        if await _safe_count(popup_loc) > 0 and await _safe_is_visible(popup_loc):
            close_btn = page.locator(
                "a#messageClose, button:has-text('Close'), a:has-text('Close'), "
                "button:has-text('×'), button:has-text('X'), .modal-header .close, "
                "button[aria-label*='Close' i], #btnCriteriaClose, button:has-text('OK')"
            )
            if await _safe_count(close_btn) > 0 and await _safe_is_visible(close_btn):
                logger.info(f"[{self.county_name}] 'YOUR SEARCH CRITERIA' popup detected; closing...")
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
        
        # Clear form inputs if visible
        for input_sel in [
            "#ctl00_ContentPlaceHolder1_txtLastName",
            "#ctl00_ContentPlaceHolder1_txtFirstName",
            "#ctl00_ContentPlaceHolder1_txtDateFrom",
        ]:
            loc = page.locator(input_sel)
            if await _safe_count(loc) > 0 and await _safe_is_visible(loc):
                clear_fn = getattr(loc.first, "clear", None)
                if callable(clear_fn):
                    res = clear_fn()
                    if inspect.isawaitable(res):
                        await res
                else:
                    fill_fn = getattr(loc.first, "fill", None)
                    if callable(fill_fn):
                        res = fill_fn("")
                        if inspect.isawaitable(res):
                            await res
    except Exception as e:
        logger.debug(f"[{self.county_name}] Return to search state note: {e}")
```

### E. Strict Schema All-Column Extraction (Steps G & H)
Extract all columns while enforcing:
```python
results.append({
    "CaseNumber": case_num,
    "FilingDate": filing_date,
    "CaseStyle": case_style or f"{l_name}, {f_name}",
    "CaseStatus": case_status,
    "CountyWebsite": self.base_url,
})
# NOTE: CaseType is strictly omitted from dictionary keys!
```

---

## 5. Verification & Test Plan

1. **Preserve Existing Tests:**
   - Run `tests/test_harris_cclerk_navigation.py` (all 3 tests pass).
   - Run `tests/test_scraper_pagination.py` (strict schema test passes).
   - Run `tests/test_v4_parity.py` (V4 parity passes).
2. **New Dedicated Test Suite (`tests/test_harris_cclerk_portal.py`):**
   - `test_step_a_page_loading_and_reload()`: Tests initial load and automatic reload on blank page.
   - `test_step_b_c_courts_county_civil_navigation()`: Tests COURTS hover and County Civil submenu click.
   - `test_step_d_form_filling_with_dol()`: Tests filling Last Name, First Name, and normalized File Date (From).
   - `test_step_e_f_search_submit_and_wait()`: Tests Search button click and result page waiting.
   - `test_step_i_search_criteria_popup_dismissal()`: Tests detection and dismissal of "YOUR SEARCH CRITERIA" modal.
   - `test_step_g_strict_schema_all_column_extraction()`: Tests table extraction and asserts `CaseType` is NOT in dictionary keys.
   - `test_step_h_pagination_traversal()`: Tests ASP.NET GridView postback pagination traversal.
   - `test_section_4_return_to_search_state()`: Tests returning to clean search state between unique names without closing tab.
   - `test_dynamic_settings_configuration()`: Tests scraper initialization with custom dynamic URL and parameters.
3. **Full Automated Verification:**
   - `pytest` across all suites (target: 531+ passing tests, 0 failures).
   - `ruff check app tests` (0 errors).
   - `npx tsc --noEmit` (0 errors).
   - `scripts/check_ps1_syntax.ps1` (0 errors).
4. **Documentation Deliverables:**
   - Implementation Record, Test Report, and Validation Artifact in `implementation_plan/`.
   - Update `AGENTS.md` test counts and status.

---

## 6. User Confirmation Request

Per the `diagnose-plan-confirm-execute` governing rule (`NO APPROVAL = NO IMPLEMENTATION`):
Please confirm if you approve this implementation plan to begin code modifications for `harris_cclerk.py` and create the dedicated test suite.
