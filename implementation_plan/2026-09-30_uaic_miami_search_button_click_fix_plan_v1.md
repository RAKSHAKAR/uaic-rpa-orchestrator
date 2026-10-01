# Implementation Plan: Miami-Dade County Search Button Click & Submission Fix

**Implementation ID:** `IMP-2026-0930-003`  
**Date:** 2026-09-30  
**County Portal:** Miami-Dade County Civil Court (`https://www2.miamidadeclerk.gov/ocs`)  
**Target File:** `backend/app/automation/florida/miami.py`  
**Test File:** `backend/tests/test_miami_portal.py`  
**Reference Solutions:**
- Power Automate V4 Desktop Flow: `implementation_plan/v4_subflows/Subflow_Miami.robin`
- Power Automate V4 ControlRepository: `ControlRepository_7bdb415f-2aae-45a6-96a0-7ad7cf77de42.json`
- Live React Bundle Source: `backend/app/scripts/miami_bundle.js` (`PartyNameSearch`, `DisplaySearchResults`)

---

## 1. Problem Statement & User Observation
The user reported:
> *"here also it is not clicking on serach button"*

Accompanied by a screenshot of the live Miami-Dade civil court portal (`www2.miamidadeclerk.gov/ocs`):
- Authenticated session: `Welcome, Apoorv N.`
- Menu: `Party Name Search`
- Form fields filled:
  - Radio: `Person's Name`
  - Last Name: `MARTINEZ`
  - First Name: `MARIA`
  - Filing Date Range From: `02/27/2022`
  - Filing Date Range To: `09/30/2026`
- **Observed Glitch:** The `Filing Date Range To` input has an active blue focus glow and dotted border; the green `[SEARCH]` button sits unclicked at the bottom, and automation halts or returns empty without submitting.

---

## 2. Root Cause Analysis (Deep Dive)

### Root Cause 1: CAPTCHA False-Positive Deadlock in `search_by_party_name`
1. In `backend/app/automation/florida/miami.py` (lines 743–761):
   ```python
   # CAPTCHA verification if triggered
   captcha_ok = await self.detect_and_handle_captcha(page, wait_seconds=self.captcha_wait_seconds)
   if not captcha_solved:
       logger.error(f"[{self.county_name}] CAPTCHA verification failed...")
       return []
   ```
2. In the Miami-Dade React frontend (`miami_bundle.js` line 1331332):
   - The React app uses `useRecaptcha('submit')` from `react-google-recaptcha-v3`, which embeds an invisible Google reCAPTCHA v3 script and iframe into `<head>`.
   - When AntiCaptcha extension is installed, `.antigate_solver` or the reCAPTCHA iframe matches the scan in `base.py:detect_and_handle_captcha`.
3. `detect_and_handle_captcha` believes a challenge is present and sits in a 30-second polling loop waiting for:
   - AntiCaptcha extension solve flag,
   - `g-recaptcha-response` textarea > 25 characters, or
   - A checked checkbox.
4. **However, on Miami-Dade's search form:**
   - As decompiled from `PartyNameSearch` in `miami_bundle.js`:
     ```javascript
     if (!(nt != null && nt.isLoggedIn) && (_t = await at(), !_t)) {
         _e(!0);
         return;
     }
     ```
     For authenticated users (`Welcome, Apoorv N.`), reCAPTCHA execution is **completely bypassed** by Miami-Dade's own application code!
   - There is NO visible checkbox, NO Turnstile, and NO hCaptcha challenge on this form.
   - Power Automate V4 (`Subflow_Miami.robin`, lines 77–101) explicitly had the CAPTCHA check **DISABLED** for Miami-Dade.
5. **Consequence:** `detect_and_handle_captcha` sits for 30s, fails, retries, fails again, and returns `[]` **WITHOUT EVER REACHING Step g (the Search button click)!**

### Root Cause 2: Focus Trapping & Lack of Formik `blur` Revalidation
- In the screenshot, `Filing Date Range To` is focused with a dotted border.
- The form is powered by Formik with Yup validation (`partyNameSearchSchema` with `validateOnBlur: true`).
- In Power Automate V4 (`Subflow_Miami.robin`, lines 59, 61, 69), `UnfocusAfterPopulate: True` was explicitly configured.
- Without unfocusing / blurring the date input, Formik does not fire validation on the field, leaving the form in an uncommitted state.

### Root Cause 3: Search Button & Formik Submission
- The submit button from `miami_bundle.js` is:
  ```javascript
  <button class="btn button-green d-flex align-items-center" type="submit" disabled={isSubmitting}>
      <FaSearch className="me-1" /> Search
  </button>
  ```
- Submitting a Formik React 18 form requires:
  1. Unfocusing inputs so Formik state syncs.
  2. Scrolling button into view and clicking with `resilient_click`.
  3. Direct DOM dispatch via `form.requestSubmit(btn)` which properly fires React 18 / Formik submit validation handlers.

### Root Cause 4: Results Indicator in Step h
- Currently, `results_indicator` in `miami.py` looks for generic `div.card` and `div[class*='result']`.
- On submit, the Miami-Dade React SPA transitions from `/ocs` to `/searchResults?qs=...` (`DisplaySearchResults`).
- The results indicator should wait for:
  1. URL containing `searchResults` (`/ocs/searchResults`), AND
  2. Concrete results content matching Power Automate V4 (`Bold text 'Party Name:'`, `Search Results`, `Case List`, `table.table`, or `No data available` / `No records found`).

---

## 3. Detailed Implementation Steps

### Step 1: Remove False-Positive CAPTCHA Block in `search_by_party_name`
- In `backend/app/automation/florida/miami.py`:
  - Miami-Dade search does not have a pre-submit CAPTCHA.
  - Remove the pre-submit `detect_and_handle_captcha` blocking loop.
  - If a visible CAPTCHA or blocking modal ever appears (e.g. rate limit), handle it gracefully without aborting before attempting search submit.
  - Power Automate V4 Parity: directly fills fields and proceeds straight to clicking `Search`.

### Step 2: Unfocus Inputs After Filling
- After filling `last_input`, `first_input`, `date_from_input`, and `date_to_input`:
  - Dispatch `blur` event and press Tab to unfocus the date field:
    ```python
    await _safe_eval(page, "() => { if (document.activeElement) document.activeElement.blur(); }")
    await page.keyboard.press("Tab")
    await page.wait_for_timeout(300)
    ```

### Step 3: Multi-Tier Resilient Search Button Click & Formik Submit
- Ensure locator matches all variations of the button:
  - `button.button-green`
  - `button.btn.button-green`
  - `button[type='submit']:has-text('Search')`
  - `button:has-text('Search')`
  - `button:has-text('SEARCH')`
- Perform 4-tier click:
  1. `await search_btn.first.scroll_into_view_if_needed(timeout=2000)`
  2. `await resilient_click(search_btn.first, page=page, timeout_ms=5000)`
  3. Formik DOM dispatch fallback:
     ```javascript
     (() => {
         const btn = document.querySelector('button.button-green') ||
                     document.querySelector('button.btn.button-green') ||
                     document.querySelector('button[type="submit"]');
         if (btn) { btn.focus(); btn.click(); }
         const form = document.querySelector('form');
         if (form && typeof form.requestSubmit === 'function') {
             try { form.requestSubmit(btn || undefined); } catch(e) {}
         }
     })()
     ```

### Step 4: Robust Results Indicator (Power Automate V4 Parity)
- Wait for route change or results container:
  - `page.wait_for_url("**/searchResults*", timeout=min(self.timeout_ms, 45000))` (with fallback if SPA doesn't trigger full URL event).
  - Wait for content indicators:
    - `text='Party Name:'` (Power Automate V4 line 105: `Bold text 'Party Name:'`)
    - `text='Search Results'` (Power Automate V4 line 117)
    - `text='Case List'`
    - `#tblResults, table.table, table.dataTable`
    - `div:has-text('No data available'), div:has-text('No records found'), div:has-text('0 records')`
  - Wait for any `.spinner-border` on the button to disappear.

---

## 5. Verification Plan

### Automated Test Suite:
1. `backend/.venv/Scripts/pytest tests/test_miami_portal.py -v` (all 17 Miami tests passing).
2. Full backend test suite: `backend/.venv/Scripts/pytest -q` (all 556 tests passing).
3. Backend lint: `backend/.venv/Scripts/ruff check app tests` (0 errors).
4. Frontend TypeScript: `cd frontend; npx tsc --noEmit` (0 errors).
5. PowerShell syntax: `powershell -File scripts/check_ps1_syntax.ps1` (0 errors).

---

## 6. Risk Assessment & Safety Guardrails
- **Zero API Contract Changes:** All existing endpoint contracts remain unchanged.
- **Zero Data Loss:** No claim records modified or deleted.
- **Power Automate V4 Parity:** Exactly mirrors `Subflow_Miami.robin` where CAPTCHA checking is disabled on the search form and `Bold text 'Party Name:'` is the authoritative completion signal.
