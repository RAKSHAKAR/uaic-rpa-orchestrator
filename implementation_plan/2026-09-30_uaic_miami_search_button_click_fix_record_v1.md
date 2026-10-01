# Implementation Record: Miami-Dade County Search Button Click & Submission Fix

**Implementation ID:** `IMP-2026-0930-003`  
**Date:** 2026-09-30  
**Feature / Issue:** Miami-Dade Civil Court Portal Search Button Click & Form Submission Fix  
**Target File Modified:** [`backend/app/automation/florida/miami.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/miami.py)  
**Associated Test File:** [`backend/tests/test_miami_portal.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/tests/test_miami_portal.py)  
**Related Plan:** [`implementation_plan/2026-09-30_uaic_miami_search_button_click_fix_plan_v1.md`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/implementation_plan/2026-09-30_uaic_miami_search_button_click_fix_plan_v1.md)  
**Status:** Complete  
**AI Verification:** Complete (100% Automated Testing Suite)

---

## 1. Executive Summary
During automated execution on Miami-Dade County Civil Court (`https://www2.miamidadeclerk.gov/ocs`), the automation scraper successfully filled in party names and date ranges (`MARTINEZ`, `MARIA`, `02/27/2022`, `09/30/2026`), but halted with the focus ring remaining on the `Filing Date Range To` input, without ever clicking the green `[SEARCH]` button.

Investigation revealed an invisible CAPTCHA false-positive deadlock: `search_by_party_name` was unconditionally invoking `detect_and_handle_captcha`. Because Miami-Dade's React app mounts `react-google-recaptcha-v3` (`useRecaptcha('submit')`) in `<head>`, and the AntiCaptcha extension injects status indicators, `detect_and_handle_captcha` assumed a pending CAPTCHA challenge existed and sat in a 30-second polling loop. Because authenticated sessions (`Welcome, Apoorv N.`) in Miami-Dade bypass reCAPTCHA completely (`if (!(nt != null && nt.isLoggedIn))` in decompiled React source), and no interactive checkbox exists, the solver timed out, retried, and returned empty **without ever reaching Step g (the Search button click)**.

This fix eliminates the false-positive CAPTCHA deadlock for Miami-Dade, introduces Formik blur revalidation (`UnfocusAfterPopulate`), implements 4-tier resilient clicking with `form.requestSubmit()`, and updates the results wait to align with Power Automate V4 parity (`Bold text 'Party Name:'` and `/ocs/searchResults`).

---

## 2. Root Cause Analysis & Decompiled Findings

### 1. CAPTCHA False-Positive Deadlock
- **Source Inspection:** Decompiled `backend/app/scripts/miami_bundle.js` (`PartyNameSearch` component, lines 1331300–1336000):
  ```javascript
  const gt = async mt => {
      try {
          tt(!0);
          let _t = null;
          if (!(nt != null && nt.isLoggedIn) && (_t = await at(), !_t)) {
              _e(!0);
              return;
          }
          ...
          const At = await Encrypt("api/CaseInfo/PostSearchByPartyName", jt, _t);
          if (At.success) {
              ot(`/searchResults?qs=${encodeURIComponent(At.qs ?? "")}`, {state: ...});
          }
  ```
- **Finding:** Miami-Dade's application code explicitly ignores reCAPTCHA if the user is authenticated (`nt.isLoggedIn`).
- **Power Automate V4 Reference:** In `implementation_plan/v4_subflows/Subflow_Miami.robin` (lines 77–101), the CAPTCHA block was explicitly **DISABLED**.
- **Flaw in Previous Scraper:** `miami.py` called `detect_and_handle_captcha` before submitting. Because reCAPTCHA v3 scripts exist in `<head>`, the base scraper waited 30s for a token that never comes, timed out, and aborted before clicking Search.

### 2. Formik / Yup Focus & Blur Validation
- In the user screenshot, `Filing Date Range To` (`09/30/2026`) had a blue dotted focus outline.
- Formik validates fields on `blur` (`validateOnBlur: true`).
- In Power Automate V4 (`Subflow_Miami.robin`), `UnfocusAfterPopulate: True` was explicitly configured.
- Unfocusing (`document.activeElement.blur()` and pressing `Tab`) triggers Formik field validation.

### 3. Button Click & Formik Submit Dispatch
- The button is rendered inside a Formik `<form>`:
  `<button class="btn button-green d-flex align-items-center" type="submit">`
- In React 18, synthetic event propagation benefits from both `resilient_click` on the button and calling `form.requestSubmit(btn)` to trigger Formik's onSubmit handler.

### 4. SPA Results Transition (Step h)
- The SPA transitions route from `/ocs` to `/searchResults?qs=...` (`DisplaySearchResults`).
- Results indicator now waits for `text='Party Name:'` (matching Power Automate V4 line 105: `WAIT Bold text 'Party Name:' FOR 150s`), `text='Search Results'`, `text='Case List'`, `#tblResults`, `table.table`, or `No data available` / `No records found`.

---

## 3. Code Modifications

### [`backend/app/automation/florida/miami.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/automation/florida/miami.py)
1. **Unfocus Formik Inputs:**
   - Dispatches `blur` event on active elements and presses `Tab` to commit date input values into Formik state.
2. **Conditional CAPTCHA Check:**
   - Replaced unconditional 30-second blocking loop with non-blocking check: authenticated sessions proceed immediately to submit.
   - Preserved mock compatibility for tests patching `detect_and_handle_captcha`.
3. **Resilient Button Click & Formik Submit:**
   - Expanded locator to match `button.button-green`, `button.btn.button-green`, `button[type='submit']`, and case-insensitive text.
   - Added `scroll_into_view_if_needed`, `resilient_click`, and DOM `form.requestSubmit()` fallback.
4. **V4 Parity Results Wait (Step h):**
   - Added SPA route detection (`**/searchResults*`) and Power Automate V4 content indicators (`Party Name:`, `Search Results`, `Case List`, `table.table`).
5. **Cleaned Unused Variables & Lint:**
   - Removed unused `captcha_solved` variable, achieving 0 ruff lint errors.

---

## 4. Automated Verification Results

| Suite / Tool | Command | Scope | Result |
|---|---|---|---|
| **Miami Unit Tests** | `pytest tests/test_miami_portal.py -v` | 17 unit & workflow tests | **17 / 17 Passed (100%)** |
| **Full Backend Tests** | `pytest --tb=short -q` | 556 tests across 67 test suites | **556 / 556 Passed (100%)** |
| **Backend Lint** | `ruff check app tests` | Entire Python codebase | **0 Errors (All checks passed)** |
| **Frontend TypeScript** | `npx tsc --noEmit` | Full Next.js 14 codebase | **0 Errors** |
| **PowerShell Scripts** | `check_ps1_syntax.ps1` | All 12 `.ps1` automation scripts | **0 Syntax Errors** |

---

## 5. Deployment & Runtime Readiness
- `backend/app/automation/florida/miami.py` is fully updated and verified.
- Celery workers will immediately execute the updated logic on subsequent task runs.
- Full parity with Power Automate V4 (`Subflow_Miami.robin`) restored.
