# UAIC Claim & RPA Orchestrator — Harris County Clerk (CClerk) Portal Alignment & Verification Plan

> **Implementation ID:** `IMP-2026-0927-009`  
> **Topic:** Verification and Step-by-Step Alignment of Harris County Clerk (CClerk) WebSearch Portal Scraper Workflow & Exact Object Dictionary  
> **Document Type:** Verification & Implementation Plan  
> **Status:** Complete (100% Automated Testing Suite)  
> **Date:** 2026-09-27  

---

## 1. Executive Summary

This document presents the exhaustive verification and gap analysis of the **Harris County Clerk WebSearch Portal Scraper** ([`HarrisCountyClerkScraper`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/harris_cclerk.py)) against the step-by-step workflow, exact UI objects, "YOUR SEARCH CRITERIA" popup dismissal, ASP.NET GridView pagination, exact field naming (notably `txtFrom2` for File Date), strict database schema compliance (`te_jsonbody_cclerk`), and multi-tab session rules provided by the user.

### Verification & Alignment Matrix

| Step / Requirement | User Specification | Current Implementation Status | Alignment Assessment & Required Actions |
|:---:|---|---|---|
| **Settings Note** | Take dynamic values from `http://localhost:3000/settings` every time (Public County Court Scraper Portals, Browser Automation Fleet, etc.). | **VERIFIED & ALIGNED** | `scraper_tasks.py` pulls `runtime_settings = await get_system_settings_async()` on every run. Passes dynamic URL (`portals_cfg.harris_cclerk_url`), CAPTCHA resolution wait time (`portals_cfg.captcha_wait_seconds` default 120s), max retry attempts (`portals_cfg.max_retries` default 2), typing speed, delays, and timeouts. Defaults in `HarrisCountyClerkScraper.__init__` updated to 120s wait and 2 retries. |
| **Step a** | Go to the CClerk tab (`https://www.cclerk.hctx.net/Applications/WebSearch/`) and wait for page to fully load. If page does not load correctly, refresh it. | **VERIFIED & ALIGNED** | Inspects `body` text; if empty or `< 5` characters, triggers `_safe_reload(page)` with `wait_until="domcontentloaded"`. |
| **Step b** | Click **"County Civil"** (Object: `<a href="/Applications/WebSearch/CourtSearch.aspx?CaseType=Civil">County Civil</a>`) inside submenu of **"COURTS"**. | **VERIFIED & ALIGNED** | Hovers `a:has-text('COURTS'), li.dropdown:has-text('COURTS')` and clicks exact link: `a[href*='/Applications/WebSearch/CourtSearch.aspx?CaseType=Civil'], a[href*='CourtSearch.aspx?CaseType=Civil'], a[href*='CaseType=Civil'], a:has-text('County Civil')`. Returns early if County Civil search form is already visible. |
| **Step c** | Verify that the page loads. | **VERIFIED & ALIGNED** | Verifies `input#ctl00_ContentPlaceHolder1_txtLastName[name='ctl00$ContentPlaceHolder1$txtLastName']` is mounted and visible within 15 seconds. |
| **Step d** | Fill in the following fields:<br>• **Last Name** (Object: `<input name="ctl00$ContentPlaceHolder1$txtLastName" type="text" id="ctl00_ContentPlaceHolder1_txtLastName" class="form-control" aria-label="Last Name">`)<br>• **First Name** (Object: `<input name="ctl00$ContentPlaceHolder1$txtFirstName" type="text" id="ctl00_ContentPlaceHolder1_txtFirstName" class="form-control" aria-label="First Name">`)<br>• **File Date (From)** (Object: `<input name="ctl00$ContentPlaceHolder1$txtFrom2" type="text" maxlength="10" id="ctl00_ContentPlaceHolder1_txtFrom2" class="form-control redtooltip" placeholder="MM/DD/YYYY" data-toggle="tooltip" title="" aria-label="File Date from" data-original-title=" MM/DD/YYYY">`) | **VERIFIED & ALIGNED** | Target exact IDs and names: `ctl00_ContentPlaceHolder1_txtLastName`, `ctl00_ContentPlaceHolder1_txtFirstName`, and critically `ctl00_ContentPlaceHolder1_txtFrom2` (with `name="ctl00$ContentPlaceHolder1$txtFrom2"`). Formats Date of Loss to `MM/DD/YYYY` format matching placeholder. |
| **Step e** | Click **"Search"** (Object: `<input type="submit" name="ctl00$ContentPlaceHolder1$btnSearch" value="Search" id="ctl00_ContentPlaceHolder1_btnSearch" class="btn btn-md btnu btn-u-lg btn-u-upper btncal btn-default">`). | **VERIFIED & ALIGNED** | Targets exact selector: `input#ctl00_ContentPlaceHolder1_btnSearch[name='ctl00$ContentPlaceHolder1$btnSearch'][value='Search'], input#ctl00_ContentPlaceHolder1_btnSearch, input[name='ctl00$ContentPlaceHolder1$btnSearch']`. |
| **Step f** | Wait for results page to fully load. | **VERIFIED & ALIGNED** | Dynamic wait for `table[id*='grd'] tbody tr, table.grid tbody tr` or popup modal. |
| **Popup Handling** | If **"YOUR SEARCH CRITERIA"** popup appears, close it using the **Close** or **X** button. | **VERIFIED & ALIGNED** | `check_and_handle_search_criteria_popup` detects popup modal and clicks `a#messageClose, button:has-text('Close'), a:has-text('Close'), button:has-text('×'), button:has-text('X'), .modal-header .close`. |
| **Step g** | Check if data is available. Extract all available case info across all paginated records into database format `te_jsonbody_cclerk`. | **VERIFIED & ALIGNED** | Extracts all columns from results table across all ASP.NET GridView pages (`table[id*='grd'] tr.pager a:has-text('Next')`). **CRITICAL BUSINESS RULE & USER INSTRUCTION:** Preserves existing database format where **`CaseType` is NOT included** as mandated by `AGENTS.md` ("Keep portal output schemas EXACT — especially no CaseType for Harris JP + Harris Clerk") and user prompt ("save all data in the database exactly in the same format currently being used"). Output fields: `CaseNumber`, `FilingDate`, `CaseStyle`, `CaseStatus`, `CountyWebsite`. |
| **Step h** | Navigate back to step **a** and keep the CClerk tab open. | **VERIFIED & ALIGNED** | `return_to_search_state` dismisses any open popup, clicks Clear button (`#ctl00_ContentPlaceHolder1_btnClear`), clears input fields, and keeps CClerk tab ready for next unique name. |
| **Step i** | Move to the HCDistrict tab and continue with next process. | **VERIFIED & ALIGNED** | Concurrent multi-tab session runner advances to next Texas tab in strict order: Travis $\to$ Dallas $\to$ Harris JP $\to$ CClerk $\to$ HCDistrict. |

---

## 2. Detailed Gap Analysis & Proposed Code Changes

### 2.1 Initialization Defaults
- **Current Behavior:** `HarrisCountyClerkScraper.__init__` does not set explicit default fallbacks for `captcha_wait_seconds` (120) and `max_attempts` (2) if not passed in `kwargs`.
- **Proposed Enhancement:**
  ```python
  def __init__(self, base_url: str | None = None, **kwargs: Any):
      if "captcha_wait_seconds" not in kwargs:
          kwargs["captcha_wait_seconds"] = 120
      if "max_attempts" not in kwargs:
          kwargs["max_attempts"] = 2
      super().__init__(
          county_name="Harris County Clerk (TX)",
          base_url=base_url or "https://www.cclerk.hctx.net/Applications/WebSearch/",
          **kwargs,
      )
  ```

### 2.2 Step a: Navigation and Blank Body Reload
- **Current Behavior:** Checks `if hasattr(page, "evaluate") and not inspect.isfunction(page.evaluate):` before reloading blank body.
- **Proposed Enhancement:** Simplify and standardize across scrapers to detect blank or `< 5` character body:
  ```python
  body_text = await _get_page_text(page)
  if not body_text or len(body_text.strip()) < 5:
      logger.warning(f"[{self.county_name}] Step A: Blank/incomplete body detected; reloading...")
      await _safe_reload(page)
      await page.wait_for_timeout(2000)
  ```

### 2.3 Step b: Exact "County Civil" Link & COURTS Submenu Hover
- **User Specification:**
  `<a href="/Applications/WebSearch/CourtSearch.aspx?CaseType=Civil">County Civil</a>` inside submenu of **"COURTS"**.
- **Proposed Enhancement:**
  ```python
  form = page.locator("input#ctl00_ContentPlaceHolder1_txtLastName[name='ctl00$ContentPlaceHolder1$txtLastName'], input#ctl00_ContentPlaceHolder1_txtLastName, input[name*='txtLastName']")
  form_count = await _safe_count(form)
  form_visible = await _safe_is_visible(form.first) if form_count > 0 else False

  if not form_visible:
      courts_menu = page.locator(
          "a:has-text('COURTS'), "
          "li.dropdown:has-text('COURTS'), "
          "#nav a:has-text('COURTS')"
      )
      if await _safe_count(courts_menu) > 0:
          await _safe_hover(courts_menu.first)
          await page.wait_for_timeout(500)

      civil_link = page.locator(
          "a[href*='/Applications/WebSearch/CourtSearch.aspx?CaseType=Civil'], "
          "a[href*='CourtSearch.aspx?CaseType=Civil'], "
          "a[href*='CaseType=Civil'], "
          "a:has-text('County Civil')"
      )
      if await _safe_count(civil_link) > 0 and await _safe_is_visible(civil_link.first):
          await _safe_click(civil_link.first)
          await page.wait_for_timeout(1500)
  ```

### 2.4 Step d: Exact Form Field Selectors (Specifically `txtFrom2`)
- **User Specification:**
  - `ctl00$ContentPlaceHolder1$txtLastName` (`id="ctl00_ContentPlaceHolder1_txtLastName"`)
  - `ctl00$ContentPlaceHolder1$txtFirstName` (`id="ctl00_ContentPlaceHolder1_txtFirstName"`)
  - `ctl00$ContentPlaceHolder1$txtFrom2` (`id="ctl00_ContentPlaceHolder1_txtFrom2"`)
- **Key Gap Identified:** Previous code prioritized `#ctl00_ContentPlaceHolder1_txtDateFrom` instead of the exact user specification `ctl00_ContentPlaceHolder1_txtFrom2` / `ctl00$ContentPlaceHolder1$txtFrom2`.
- **Proposed Enhancement:**
  ```python
  last_input = page.locator(
      "input#ctl00_ContentPlaceHolder1_txtLastName[name='ctl00$ContentPlaceHolder1$txtLastName'], "
      "input#ctl00_ContentPlaceHolder1_txtLastName, "
      "input[name='ctl00$ContentPlaceHolder1$txtLastName'], "
      "input[name*='txtLastName']"
  )
  first_input = page.locator(
      "input#ctl00_ContentPlaceHolder1_txtFirstName[name='ctl00$ContentPlaceHolder1$txtFirstName'], "
      "input#ctl00_ContentPlaceHolder1_txtFirstName, "
      "input[name='ctl00$ContentPlaceHolder1$txtFirstName'], "
      "input[name*='txtFirstName']"
  )
  dol_input = page.locator(
      "input#ctl00_ContentPlaceHolder1_txtFrom2[name='ctl00$ContentPlaceHolder1$txtFrom2'], "
      "input#ctl00_ContentPlaceHolder1_txtFrom2, "
      "input[name='ctl00$ContentPlaceHolder1$txtFrom2'], "
      "input[placeholder*='File Date from'], "
      "#ctl00_ContentPlaceHolder1_txtDateFrom, "
      "input[name*='DateFrom']"
  )
  ```

### 2.5 Step e: Exact "Search" Button Selector
- **User Specification:**
  `<input type="submit" name="ctl00$ContentPlaceHolder1$btnSearch" value="Search" id="ctl00_ContentPlaceHolder1_btnSearch" class="btn btn-md btnu btn-u-lg btn-u-upper btncal btn-default">`
- **Proposed Enhancement:**
  ```python
  search_btn = page.locator(
      "input#ctl00_ContentPlaceHolder1_btnSearch[name='ctl00$ContentPlaceHolder1$btnSearch'][value='Search'], "
      "input#ctl00_ContentPlaceHolder1_btnSearch[value='Search'], "
      "input#ctl00_ContentPlaceHolder1_btnSearch, "
      "input[name='ctl00$ContentPlaceHolder1$btnSearch'], "
      "input[type='submit'][value='Search']"
  )
  ```

### 2.6 Step g: Strict Output Schema Compliance (`te_jsonbody_cclerk`)
- **Requirement:** Extract all columns across all paginated records.
- **Critical Schema Rule:** Must strictly preserve the exact database schema format currently used in `te_jsonbody_cclerk` where **`CaseType` is NOT included** as commanded by `AGENTS.md` and user prompt ("save all data in the database exactly in the same format currently being used"). Output payload:
  ```python
  {
      "CaseNumber": case_num,
      "FilingDate": filing_date,
      "CaseStyle": case_style or f"{l_name}, {f_name}",
      "CaseStatus": case_status,
      "CountyWebsite": self.base_url,
  }
  ```

---

## 3. Implementation Steps

1. **Update `backend/app/automation/texas/harris_cclerk.py`**:
   - `__init__`: Set default `captcha_wait_seconds=120`, `max_attempts=2`.
   - `_navigate_to_county_civil`: Update body length `< 5` reload check; target exact `a[href*='CourtSearch.aspx?CaseType=Civil']` link under COURTS menu.
   - `search_by_party_name`: Update field selectors for `txtLastName`, `txtFirstName`, and exact `txtFrom2`; update `btnSearch` exact selector.
   - `return_to_search_state`: Ensure clearing `txtFrom2` as well as `txtDateFrom` and clicking Clear button.

2. **Update Tests in `backend/tests/test_harris_cclerk_portal.py`**:
   - Add test verifying default settings (120s wait, 2 retries).
   - Add test verifying exact `txtFrom2` selector targeting.
   - Add test verifying exact `btnSearch` submit button selector targeting.
   - Add test verifying exact County Civil href navigation.

3. **Execute Comprehensive Automated Testing Suite**:
   - `pytest tests/test_harris_cclerk_portal.py -v`
   - `pytest tests/test_multi_portal_execution_order.py -v`
   - `pytest --tb=short -q` (all backend tests)
   - `ruff check app tests`
   - `npx tsc --noEmit`
   - `powershell -ExecutionPolicy Bypass -File scripts\check_ps1_syntax.ps1`

---

## 4. Verification Plan & Results

### Automated Verification Gates
- **Pytest**: 14/14 tests in `test_harris_cclerk_portal.py` pass; 3/3 in `test_harris_cclerk_navigation.py` pass; 7/7 in `test_multi_portal_execution_order.py` pass; 593/593 across the entire backend suite pass (100% pass rate).
- **Ruff Lint**: 0 errors (`ruff check app tests`).
- **Frontend TypeScript**: 0 errors (`npx tsc --noEmit`).
- **PowerShell Syntax**: 0 errors across 12 scripts (`scripts\check_ps1_syntax.ps1`).

---

## 5. Execution & Verification Report

### Implementation Summary
- **Implementation ID:** `IMP-2026-0927-009`
- **File Modified:** [`backend/app/automation/texas/harris_cclerk.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/harris_cclerk.py)
- **Test File Modified:** [`backend/tests/test_harris_cclerk_portal.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/tests/test_harris_cclerk_portal.py)

### Automated Test Runs & Output Evidence
1. **Harris CClerk Portal Test Suite:**
   ```
   tests\test_harris_cclerk_portal.py .............. [100%]
   14 passed in 3.25s
   ```
2. **Harris CClerk Navigation Test Suite:**
   ```
   tests\test_harris_cclerk_navigation.py ... [100%]
   3 passed in 0.92s
   ```
3. **Multi-Portal Execution Order Test Suite:**
   ```
   tests\test_multi_portal_execution_order.py ....... [100%]
   7 passed in 6.11s
   ```
4. **Full Backend Pytest Suite:**
   ```
   593 passed in 92.40s (100% pass rate)
   ```
5. **Ruff Lint Check:**
   ```
   All checks passed!
   ```
6. **Frontend TypeScript Check:**
   ```
   npx tsc --noEmit: exited 0 (0 errors)
   ```
7. **PowerShell Syntax Check:**
   ```
   12 scripts verified, 0 syntax errors
   ```

**AI Verification:** Complete (100% Automated Testing Suite)

