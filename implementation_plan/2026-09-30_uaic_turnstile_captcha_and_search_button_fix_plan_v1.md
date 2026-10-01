# Implementation Plan: Turnstile CAPTCHA Detection & Search Button Click Fix

**Implementation ID:** `IMP-2026-0930-001`  
**Date:** 2026-09-30  
**Status:** `Proposed - Awaiting Human Approval`  
**Target Systems:** `backend/app/automation/base.py`, `backend/app/automation/florida/broward.py`

---

## 1. Problem Statement & User Evidence

### 1.1 User Observation
The user observed and reported:
> *"captcha issolved but not clicking on search button"*

Along with an uploaded screenshot from live execution on Broward County Clerk (`https://www.browardclerk.org/Web2`):
- Party Name search fields filled: Last Name `MARTINEZ`, First Name `MARIA`, Date From `2/27/2022`.
- Cloudflare Turnstile CAPTCHA is clearly solved with blue checkmark: `[✓] Verify you are human`.
- AntiCaptcha extension status box below Turnstile explicitly displays: `[Logo] Solved`.
- The green **Search** button (`#PersonSearchResults`) and **Reset** button (`#btnResetByName`) are present directly below the CAPTCHA.
- However, the automation was stuck or did not click the **Search** button.

---

## 2. Root Cause Analysis (RCA)

Our inspection of `backend/app/automation/base.py` and `backend/app/automation/florida/broward.py` identified two compounding root causes:

### Root Cause 1: CAPTCHA Resolution Wait Loop Ignores Extension `is_solved` and Fails to Detect Turnstile Solution
In `BaseCourtScraper.detect_and_handle_captcha()` (`backend/app/automation/base.py` lines 866–935):
1. **`is_solved` is evaluated but never used**:
   ```javascript
   const is_solved = cls.includes("solved") || st.includes("solved") || txt.includes("solved");
   return { exists: true, in_process: in_proc, solved: is_solved };
   ```
   The Python loop only checks `is_in_proc`:
   ```python
   if is_in_proc:
       continue
   ```
   It completely omits checking `solver_status.get("solved")`! Even though AntiCaptcha displayed "Solved" on screen, the loop ignored this signal.
2. **False assumption in Turnstile frame check**:
   ```python
   turnstile_success = "success" in body_txt.lower()
   ```
   Cloudflare Turnstile's frame body text is `"Verify you are human"` — it **never** contains the literal string `"success"`.
3. **Turnstile Frame Binding Collision**:
   The Broward portal page contains **four** distinct forms, each with a `.cf-turnstile` widget (`#nameSearch`, `#businessSearch`, `#caseSearchForm`, `#citationSearchForm`). Scanning `page.frames` with a simple loop overwrote `turnstile_frame` with the *last* frame (the hidden Citation tab's frame), completely missing the active Party Name frame.
4. **Token Check Was Too Narrow**:
   The loop only looked for `input[name="cf-turnstile-response"]` without checking:
   - `window.turnstile.getResponse()`
   - `window.__turnstileInitParameters.responses` (injected by the AntiCaptcha extension)
   - Iframe checkmark status (`input[type="checkbox"]:checked`, `[aria-checked="true"]`, SVG checkmark)
5. **Consequence**:
   `detect_and_handle_captcha` ran for the full 120-second timeout and returned `False`. In `broward.py`, if `detect_and_handle_captcha` returns `False`, the bot assumes CAPTCHA failed, **never reaches Step G (click search)**, and instead refreshes the page or aborts!

### Root Cause 2: `resilient_click` Selected `.last` Element & Generic `button:has-text('Search')` Selector Mismatch
1. In `resilient_click` (`backend/app/automation/base.py` line 161):
   ```python
   last_loc = getattr(locator, "last", locator)
   target = getattr(last_loc, "first", last_loc)
   ```
   `resilient_click` explicitly selected `.last` instead of `.first` or the visible element.
2. In `broward.py` line 301:
   ```python
   search_btn = page.locator(
       "button#PersonSearchResults, "
       "button[name='PersonSearchResults'], "
       "input#PersonSearchResults, "
       "#PersonSearchResults, "
       "button:has-text('Search')"
   )
   ```
   Because `button:has-text('Search')` was included in the selector, it matched all 4 search buttons on the page:
   - Button 1: `#PersonSearchResults` (Party Name tab - VISIBLE)
   - Button 2: `#BusinessSearchResults` (Business tab - HIDDEN)
   - Button 3: `#CaseNumberSearchResults` (Case Number tab - HIDDEN)
   - Button 4: `#CitationSearchResults` (Citation tab - HIDDEN)
3. Combining `locator.last` with this multi-match selector caused `resilient_click` to target Button 4 (`#CitationSearchResults` in the hidden Citation tab). Playwright timed out waiting for it to be visible, direct click failed on form validation of the hidden form, and `#PersonSearchResults` was never clicked.

---

## 3. Proposed Remediation Plan

### 3.1 Fix `backend/app/automation/base.py` (`detect_and_handle_captcha`)
1. **Honor AntiCaptcha `solved` state**:
   If `solver_status.get("solved")` is `True` and `not is_in_proc`, immediately declare CAPTCHA solved and return `True`.
2. **Multi-Source Turnstile Detection**:
   Evaluate:
   - `window.__turnstileInitParameters.responses` (populated by AntiCaptcha `turnstile_interceptor.js`).
   - `window.turnstile.getResponse()` (official Turnstile JS API).
   - Any input or textarea with name/id containing `"turnstile"` or `"cf-chl"` having value length > 20.
3. **Turnstile Frame Checkmark Verification**:
   Inspect all Turnstile frames (not just the last one) for `input[type="checkbox"]:checked`, `[aria-checked="true"]`, SVG checkmark icon (`svg.mark`, `#success-icon`, `svg[class*="success"]`), or checkmark elements.

### 3.2 Fix `backend/app/automation/base.py` (`resilient_click`)
1. Change `last_loc = getattr(locator, "last", locator)` to `target = getattr(locator, "first", locator)`.
2. If `locator` matches multiple elements, inspect and prioritize the first element that is currently visible in the DOM (`is_visible() == True`).

### 3.3 Fix `backend/app/automation/florida/broward.py` (Search Button Submission)
1. Eliminate loose `button:has-text('Search')` from the selector.
2. Specific target:
   ```python
   search_btn = page.locator(
       "#personSearchForm button#PersonSearchResults, "
       "#nameSearch button#PersonSearchResults, "
       "button#PersonSearchResults, "
       "#personSearchForm button[type='submit']"
   )
   ```
3. After `resilient_click(search_btn)`, dispatch a direct DOM click and FormValidation trigger to `#PersonSearchResults` to guarantee submission even if the browser window is out of focus or resized.

---

## 4. Verification Plan

1. **Automated Unit & Integration Tests**:
   - Run backend test suite: `.venv\Scripts\pytest tests/test_automation.py tests/test_broward_portal.py -v`
   - Run full test suite: `.venv\Scripts\pytest --tb=short -q`
2. **Lint & Type Checks**:
   - Python linting: `.venv\Scripts\ruff check app tests`
   - TypeScript validation: `npx tsc --noEmit` in `frontend/`
   - PowerShell launcher check: `scripts\check_ps1_syntax.ps1`
3. **Automated DOM Simulation**:
   - Verify `detect_and_handle_captcha` returns `True` immediately when `.antigate_solver.solved` or Turnstile checkmark is present.
   - Verify `resilient_click` targets the visible Party Name search button and ignores inactive tab buttons.
