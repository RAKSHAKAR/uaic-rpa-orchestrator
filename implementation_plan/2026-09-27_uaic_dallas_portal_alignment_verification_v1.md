# UAIC Claim & RPA Orchestrator — Dallas County Portal Alignment & Verification Plan

> **Implementation ID:** `IMP-2026-0927-008`  
> **Topic:** Verification and Step-by-Step Alignment of Dallas County Odyssey Portal Scraper Workflow & Exact Object Dictionary  
> **Document Type:** Verification & Implementation Plan  
> **Status:** Complete (100% Automated Testing Suite)  
> **Date:** 2026-09-27  

---

## 1. Executive Summary

This document presents the exhaustive verification and gap analysis of the **Dallas County Court Portal Scraper** ([`DallasScraper`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/dallas.py)) against the step-by-step workflow, exact UI objects, CAPTCHA handling exceptions, Session Timeout Warning recovery, dynamic settings extraction, all-column extraction (including `CaseType`), and multi-tab session rules provided by the user.

### Verification & Alignment Matrix

| Step / Requirement | User Specification | Current Implementation Status | Alignment Assessment & Required Actions |
|:---:|---|---|---|
| **Settings Note** | Take dynamic values from `http://localhost:3000/settings` every time (Public County Court Scraper Portals, Browser Automation Fleet, etc.). | **VERIFIED & ALIGNED** | `scraper_tasks.py` pulls `runtime_settings = await get_system_settings_async()` on every run. Passes dynamic URL (`portals_cfg.dallas_url`), CAPTCHA resolution wait time (`portals_cfg.captcha_wait_seconds` default 120s), max retry attempts (`portals_cfg.max_retries` default 2), typing speed, delays, and timeouts. Defaults in `DallasScraper.__init__` updated to 120s wait and 2 retries. |
| **Step a** | Open Dallas tab (`https://courtsportal.dallascounty.org/DALLASPROD/Home/`) and wait for page to fully load. If page does not load correctly, refresh it. | **VERIFIED & ALIGNED** | Inspects `body` text; if empty or `< 5` characters, triggers `_safe_reload(page)` with `wait_until="domcontentloaded"`. Correctly navigates to `/DALLASPROD/Home/Dashboard/29`. |
| **Step b** | Click **"Smart Search"** (Object: `<a tabindex="0" class="btn btn-lg btn-default portlet-buttons" href="/DALLASPROD/Home/Dashboard/29"><img ... src="/DALLASPROD/Content/images/dashboard/Icon_SmartSearch.svg"><br><br>Smart Search<p class="btn-description">Search for court records.</p></a>`). | **VERIFIED & ALIGNED** | Configured with exact object selectors: `a.portlet-buttons[href*='/DALLASPROD/Home/Dashboard/29'], a.portlet-buttons[href*='Dashboard/29'], a[href*='/DALLASPROD/Home/Dashboard/29'], a.portlet-buttons, a.btn:has-text('Smart Search'), a:has-text('Smart Search')`. Returns early if search input is already mounted and visible. |
| **Step c** | Verify that the page loads. | **VERIFIED & ALIGNED** | `verify_search_page_loaded` verifies that `#caseCriteria_SearchCriteria` (with `name="caseCriteria.SearchCriteria"`) is mounted and visible within 15 seconds. |
| **Step d** | Enter required data in **Search Input** text box (Object: `<fieldset><input autofocus="" class="form-control" ... id="caseCriteria_SearchCriteria" maxlength="100" name="caseCriteria.SearchCriteria" placeholder="" type="text" value=""><label for="caseCriteria_SearchCriteria">* Enter a Record Number or Name in Last, First Middle Suffix Format</label></fieldset>`). | **VERIFIED & ALIGNED** | Configured with exact attribute selectors: `input#caseCriteria_SearchCriteria[name='caseCriteria.SearchCriteria'], input#caseCriteria_SearchCriteria, #caseCriteria_SearchCriteria, input[name='caseCriteria.SearchCriteria']` (notice `name="caseCriteria.SearchCriteria"` has a dot, not an underscore). Formats search query as `f"{l_name}, {f_name}".strip(", ")` conforming to the required `Last, First` format. |
| **Step e** | Click the CAPTCHA checkbox if CAPTCHA solving has not started automatically then click on checkbox (Object: `<div class="rc-anchor-center-item rc-anchor-checkbox-holder"><span class="recaptcha-checkbox goog-inline-block recaptcha-checkbox-unchecked rc-anchor-checkbox" role="checkbox" aria-checked="false" id="recaptcha-anchor" tabindex="0" dir="ltr" aria-labelledby="recaptcha-anchor-label">...</span></div>`). | **VERIFIED & ALIGNED** | Targets exact object: `#recaptcha-anchor, .rc-anchor-checkbox, span[role='checkbox'], .rc-anchor-checkbox-holder`. Inspects `aria-checked == "false"` or `.recaptcha-checkbox-unchecked`; if Anti-Captcha has not started automatically solving, triggers anchor click. |
| **Step f** | Wait for CAPTCHA to be solved and for verification checkmark to appear (`recaptcha-checkbox-checked`, `aria-checked="true"`, or `g-recaptcha-response > 25`). | **VERIFIED & ALIGNED** | `detect_and_handle_captcha` actively monitors Anti-Captcha `.antigate_solver` and verifies response tokens. |
| **Exception 1** | If CAPTCHA verification fails, refresh browser page and repeat process starting from step **c**. | **VERIFIED & ALIGNED** | If `detect_and_handle_captcha` returns `False`, executes page reload, waits backoff, re-engages Smart Search, verifies page load (step c), and repeats input/solve loop. |
| **Exception 2** | If **"Session timeout warning"** appears, click **"Continue session"**. If automatically navigated to home page, restart from step **b**; otherwise continue from step **c**. | **VERIFIED & ALIGNED** | `check_and_handle_session_timeout` clicks `button:has-text('Continue session')`, `a:has-text('Continue session')`. If URL redirected to portal root home page (`/DALLASPROD/Home/` without `Dashboard/29`), re-triggers step **b** (`click_smart_search`) and verifies step **c**. |
| **Exception 3** | Default **"CAPTCHA Resolution Wait (Seconds)"** is set to **120**. If not solved within this time, perform hard refresh of page. Continue retry process up to configured **"Max Retry & Refresh Attempts"**, default **2**. | **VERIFIED & ALIGNED** | Respects `self.captcha_wait_seconds` (default 120s from Settings) and `self.max_attempts` (default 2 from Settings). Triggers hard refresh on timeout and repeats up to max attempts. |
| **Step g** | Once CAPTCHA is solved, immediately click **"Submit"** (Object: `<input name="Search" id="btnSSSubmit" class="btn btn-primary pull-right" value="Submit" type="submit">`). | **VERIFIED & ALIGNED** | Configured with exact selector: `input#btnSSSubmit[name='Search'][value='Submit'], input#btnSSSubmit[value='Submit'], input#btnSSSubmit, #btnSSSubmit, input[name='Search'][value='Submit']`. Triggers immediate click upon verified token. |
| **Step h** | Wait for results page to fully load. | **VERIFIED & ALIGNED** | Dynamic wait for `.k-grid-content tbody tr, table.k-selectable tbody tr, table tbody tr, .k-grid, :has-text('no cases match your search')`. |
| **Step i** | Extract all available case info (`Case Number`, `Case Style`, `Case Type`, `Filing Date`, `Case Status`, `Access Level`, + any extra dynamic columns across all paginated records); persist to DB format `te_jsonbody_dallas`. | **VERIFIED & ALIGNED** | Discovers headers dynamically from `.k-grid-header thead th`; parses table rows; sanitizes case style; extracts all columns. **IMPORTANT SCHEMA RULE:** In Dallas County, unlike Harris JP, **`CaseType` IS extracted and included** (`CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`, `AccessLevel`) as required by the user prompt and `AGENTS.md`. |
| **Step j** | Navigate back to Dallas portal (`https://courtsportal.dallascounty.org/DALLASPROD/Home/`) or restart from step **a** keeping Dallas tab open. | **VERIFIED & ALIGNED** | Multi-portal orchestrator maintains concurrent open tabs across all portals in attended session. `return_to_search_state` resets Dallas tab to Smart Search ready for the next unique name without closing the tab. |
| **Step k** | Move to the Harris JP tab and continue with the next process. | **VERIFIED & ALIGNED** | Enforced by multi-portal fleet orchestrator (`session_runner.py` / `scraper_tasks.py`). |

---

## 2. Detailed Gap Analysis & Proposed Code Changes

### 2.1 Initialization Defaults
- **Current Behavior:** `DallasScraper.__init__` does not set fallback defaults for `captcha_wait_seconds` (120) and `max_attempts` (2) if not passed in `kwargs`.
- **Proposed Enhancement:**
  ```python
  def __init__(self, base_url: str | None = None, **kwargs: Any):
      if "captcha_wait_seconds" not in kwargs:
          kwargs["captcha_wait_seconds"] = 120
      if "max_attempts" not in kwargs:
          kwargs["max_attempts"] = 2
      super().__init__(
          county_name="Dallas County (TX)",
          base_url=base_url or "https://courtsportal.dallascounty.org/DALLASPROD/Home/",
          **kwargs,
      )
  ```

### 2.2 Step a: Body Content Validation & Reload Fallback
- **Current Behavior:** In `DallasScraper.navigate_to_search`, it checks `if not body_text.strip():`.
- **Proposed Enhancement:** Check for empty or `< 5` characters to catch partially rendered blank shells:
  ```python
  body_text = await _get_page_text(page)
  if not body_text or len(body_text.strip()) < 5:
      logger.warning(f"[{self.county_name}] Blank/incomplete page body detected; reloading...")
      await _safe_reload(page)
      await page.wait_for_timeout(2000)
  ```

### 2.3 Step b: Exact "Smart Search" Object & Landing Page Handling
- **User Specification:**
  `<a tabindex="0" class="btn btn-lg btn-default portlet-buttons" href="/DALLASPROD/Home/Dashboard/29"><img style="max-height:96px; max-width:96px;" src="/DALLASPROD/Content/images/dashboard/Icon_SmartSearch.svg"><br><br>Smart Search<p stlye="word-wrap: break-word" class="btn-description">Search for court records.</p></a>`
- **Proposed Enhancement:**
  Update `click_smart_search` to target these exact selectors:
  ```python
  search_input = page.locator(
      "input#caseCriteria_SearchCriteria[name='caseCriteria.SearchCriteria'], "
      "input#caseCriteria_SearchCriteria, "
      "#caseCriteria_SearchCriteria, "
      "input[name='caseCriteria.SearchCriteria'], "
      "input[name='caseCriteria_SearchCriteria'], "
      "#SearchCriteria"
  )
  if await _safe_count(search_input) > 0 and await _safe_is_visible(search_input):
      logger.info(f"[{self.county_name}] Step B: Smart Search input already visible; proceeding.")
      return

  smart_search_link = page.locator(
      "a.portlet-buttons[href*='/DALLASPROD/Home/Dashboard/29'], "
      "a.portlet-buttons[href*='Dashboard/29'], "
      "a[href*='/DALLASPROD/Home/Dashboard/29'], "
      "a.portlet-buttons, "
      "a.btn:has-text('Smart Search'), "
      "a:has-text('Smart Search'), "
      "button:has-text('Smart Search'), "
      "#tcControllerLink_0"
  )
  ```

### 2.4 Step d: Search Input Exact Selectors & Query Format
- **User Specification:**
  `<fieldset><input autofocus="" class="form-control" data-val="true" data-val-length="Please enter a value for search criteria 100 characters or less." data-val-length-max="100" data-val-required="Please enter a value for search criteria." id="caseCriteria_SearchCriteria" maxlength="100" name="caseCriteria.SearchCriteria" placeholder="" type="text" value=""><label for="caseCriteria_SearchCriteria">* Enter a Record Number or Name in Last, First Middle Suffix Format</label></fieldset>`
- **Proposed Enhancement:**
  Target exact name and ID attributes:
  ```python
  search_input = page.locator(
      "input#caseCriteria_SearchCriteria[name='caseCriteria.SearchCriteria'], "
      "input#caseCriteria_SearchCriteria, "
      "#caseCriteria_SearchCriteria, "
      "input[name='caseCriteria.SearchCriteria'], "
      "input[name='caseCriteria_SearchCriteria'], "
      "#SearchCriteria"
  )
  ```
  Format party query as `f"{l_name}, {f_name}".strip(", ")` conforming to the required `Last, First` format.

### 2.5 Exception 2: Session Timeout Warning & Home Page Redirect Recovery
- **User Specification:**
  If "Session timeout warning" appears, click "Continue session". If the website navigates to home page, restart from step **b**; otherwise continue from step **c**.
- **Proposed Enhancement:**
  Enhance `check_and_handle_session_timeout`:
  ```python
  timeout_modal = page.locator(
      "div:has-text('Session timeout warning'), "
      ".modal:has-text('Session timeout warning'), "
      "div:has-text('extend your session')"
  )
  if await _safe_count(timeout_modal) > 0 and await _safe_is_visible(timeout_modal):
      continue_btn = page.locator(
          "button:has-text('Continue session'), "
          "a:has-text('Continue session'), "
          "input[value*='Continue session' i]"
      )
      if await _safe_count(continue_btn) > 0 and await _safe_is_visible(continue_btn):
          logger.warning(f"[{self.county_name}] Step G / Exception 2: 'Session timeout warning' detected; clicking 'Continue session'...")
          click_fn = getattr(continue_btn.first, "click", None)
          if callable(click_fn):
              res = click_fn()
              if inspect.isawaitable(res):
                  await res
          wait_fn = getattr(page, "wait_for_timeout", None)
          if callable(wait_fn):
              res = wait_fn(1500)
              if inspect.isawaitable(res):
                  await res
          
          # Exception 2 check: if website redirected to home page, restart from step b
          raw_url = getattr(page, "url", None)
          curr_url = raw_url if isinstance(raw_url, str) else ""
          if curr_url and "Dashboard/29" not in curr_url:
              logger.info(f"[{self.county_name}] Redirected to portal home; restarting from Smart Search (Step b)...")
              await self.click_smart_search(page)
              await self.verify_search_page_loaded(page)
          return True
  ```

### 2.6 Step g: Exact "Submit" Button Selector
- **User Specification:**
  `<input name="Search" id="btnSSSubmit" class="btn btn-primary pull-right" value="Submit" type="submit">`
- **Proposed Enhancement:**
  ```python
  submit_btn = page.locator(
      "input#btnSSSubmit[name='Search'][value='Submit'], "
      "input#btnSSSubmit[value='Submit'], "
      "input#btnSSSubmit, "
      "#btnSSSubmit, "
      "input[name='Search'][value='Submit'], "
      "input[type='submit'][value*='Submit' i], "
      "button:has-text('Submit')"
  )
  ```

### 2.7 Step i: Preservation of `CaseType` in Dallas Schema
- **Requirement:** `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`, `AccessLevel`, + dynamic headers. Database storage key: `te_jsonbody_dallas`.
- **Status:** Already verified in `dallas.py` lines 494–501.

---

## 3. Implementation Steps

1. **Update `backend/app/automation/texas/dallas.py`**:
   - `__init__`: Default `captcha_wait_seconds=120`, `max_attempts=2`.
   - `navigate_to_search`: Check body text length `< 5` and reload.
   - `click_smart_search`: Use exact object selectors for `/DALLASPROD/Home/Dashboard/29`.
   - `verify_search_page_loaded`: Use exact attribute selectors for `#caseCriteria_SearchCriteria`.
   - `check_and_handle_session_timeout`: Handle "Continue session" and check for `/Home/` redirect recovery.
   - `return_to_search_state`: Clear exact search input and click reset link.
   - `search_by_party_name`: Use formatted `f"{l_name}, {f_name}"`, exact search input selector, exact `btnSSSubmit` selector, and retry loop.

2. **Update Tests in `backend/tests/test_dallas_portal.py`**:
   - Add unit test verifying default settings (120s wait, 2 retries).
   - Add unit test verifying short body `< 5` triggers reload.
   - Add unit test verifying exact portlet-button selector for Smart Search.
   - Add unit test verifying session timeout redirect recovery.
   - Add unit test verifying exact submit button selector.

3. **Execute Comprehensive Automated Testing Suite**:
   - `pytest tests/test_dallas_portal.py -v`
   - `pytest tests/test_multi_portal_execution_order.py -v`
   - `pytest --tb=short -q` (580+ tests)
   - `ruff check app tests`
   - `npx tsc --noEmit`
   - `powershell -ExecutionPolicy Bypass -File scripts\check_ps1_syntax.ps1`

---

## 4. Verification Plan & Results

### Automated Verification Gates
- **Pytest**: 14/14 tests in `test_dallas_portal.py` pass; 7/7 in `test_multi_portal_execution_order.py` pass; 588/588 across the entire backend suite pass (100% pass rate).
- **Ruff Lint**: 0 errors (`ruff check app tests`).
- **Frontend TypeScript**: 0 errors (`npx tsc --noEmit`).
- **PowerShell Syntax**: 0 errors across 12 scripts (`scripts\check_ps1_syntax.ps1`).

---

## 5. Execution & Verification Report

### Implementation Summary
- **Implementation ID:** `IMP-2026-0927-008`
- **File Modified:** [`backend/app/automation/texas/dallas.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/texas/dallas.py)
- **Test File Modified:** [`backend/tests/test_dallas_portal.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/tests/test_dallas_portal.py)

### Automated Test Runs & Output Evidence
1. **Dallas Portal Test Suite:**
   ```
   tests\test_dallas_portal.py .............. [100%]
   14 passed in 2.95s
   ```
2. **Multi-Portal Execution Order Test Suite:**
   ```
   tests\test_multi_portal_execution_order.py ....... [100%]
   7 passed in 7.47s
   ```
3. **Full Backend Pytest Suite:**
   ```
   588 passed in 88.52s (100% pass rate)
   ```
4. **Ruff Lint Check:**
   ```
   All checks passed!
   ```
5. **Frontend TypeScript Check:**
   ```
   npx tsc --noEmit: exited 0 (0 errors)
   ```
6. **PowerShell Syntax Check:**
   ```
   12 scripts verified, 0 syntax errors
   ```

**AI Verification:** Complete (100% Automated Testing Suite)

