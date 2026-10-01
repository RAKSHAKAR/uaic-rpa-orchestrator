# Implementation Plan: Broward County Court Search Submit & Glossary Table Exclusion Fix

**Implementation ID:** `IMP-2026-0930-002`  
**Date:** 2026-09-30  
**Status:** Proposed - Awaiting Human Confirmation  
**Document Type:** Implementation Plan (v1)  
**Author:** AI Agent (Antigravity)  
**Target File:** `backend/app/automation/florida/broward.py`  
**Reference File:** `implementation_plan/v4_subflows/Subflow_Broward.robin` (Authoritative Power Automate V4)  

---

## 1. Executive Summary & Root Cause Analysis

### User Observation
During live bot execution on Broward County (`https://www.browardclerk.org/Web2`), the Cloudflare Turnstile CAPTCHA solved successfully (`[✓] Verify you are human` and AntiCaptcha reported `Solved`), but the green `Search` button (`#PersonSearchResults`) was either not clicked or did not submit, leaving the form sitting filled on the screen. Simultaneously, the database recorded 12 fake "cases" for MARIA MARTINEZ (`CaseNumber: CACE`, `CaseStyle: Civil Action Central`).

### Detailed Root Cause Breakdown
1. **Bootstrap FormValidation Date Format Rejection:**
   - On `https://www.browardclerk.org/Web2`, the `filingDateOnOrAfterP` input is validated by Bootstrap FormValidation:
     ```javascript
     filingDateOnOrAfterP: {
         row: '.col-sm-4',
         validators: {
             date: {
                 message: 'Date From is invalid or an invalid date range',
                 format: 'MM/DD/YYYY',
                 max: 'filingDateOnOrBeforeP'
             }
         }
     }
     ```
   - In `fill_search_fields`, the raw Date of Loss was entered as `2/27/2022` (single-digit month `M/DD/YYYY`).
   - Bootstrap FormValidation's date validator strictly requires two-digit month `MM/DD/YYYY` (`02/27/2022`). Because `2/27/2022` failed format validation, FormValidation's `click` handler intercepted `#PersonSearchResults`, blocked submission (`e.preventDefault()`), and prevented navigation!
   - Furthermore, `filingDateOnOrAfterP` is a KendoDatePicker widget (`$('#filingDateOnOrAfterP').kendoDatePicker(...)`). Setting the DOM input directly without updating the Kendo widget or invoking `$('#personSearchForm').formValidation('revalidateField', 'filingDateOnOrAfterP')` left the field in an unvalidated state.

2. **Premature Extraction of Static Glossary Helper Table:**
   - On `/Web2`, there is an informational static helper table (`<table class="table">`) with headers `['Case Prefix', 'Court Type', 'Example']` and rows:
     `CACE | Civil Action Central | CACE15085978`
     `COCE | County Civil Central | COCE15085978`
   - In `broward.py`, Step H waited for generic `table.table tbody tr, table tbody tr`. Because this static glossary table is ALREADY present on `/Web2`, `wait_for_selector` resolved instantly (0 ms).
   - Step K then extracted the 12 rows from the glossary table, mistaking `CACE` for `CaseNumber` and `Civil Action Central` for `CaseStyle`!
   - Step Section 4 then called `await self.return_to_search_state(page)` which reloaded `https://www.browardclerk.org/Web2`.

3. **V4 Parity Alignment:**
   - In Power Automate V4 (`Subflow_Broward.robin`):
     - Line 55: Dispatches `document.getElementById("PersonSearchResults").click()`.
     - Form POSTS to `https://www.browardclerk.org//Web2/CaseSearchECA/PersonSearchResults` and navigates to `/Web2/CaseSearchECA/Results?TYPE=GetCaseSearchByName_ECA&INPUT=...`.
     - Line 63: Extracts rows from the results table where `td:eq(0) > div > button` is the Case Number button.

---

## 2. Proposed Changes

### File: `backend/app/automation/florida/broward.py`

#### Change 1: Normalize DOL Date to Strict `MM/DD/YYYY` and Revalidate Form
- Add helper to format any valid date string (`M/D/YYYY`, `YYYY-MM-DD`, etc.) to strict two-digit `MM/DD/YYYY` (e.g. `2/27/2022` -> `02/27/2022`).
- In `fill_search_fields`:
  - Format `clean_dol` to `MM/DD/YYYY`.
  - Fill the DOM input and update the KendoDatePicker widget via `page.evaluate`:
    ```javascript
    const el = document.getElementById('filingDateOnOrAfterP');
    if (el) {
        el.value = dol;
        if (window.$) {
            const kw = $(el).data('kendoDatePicker');
            if (kw) {
                kw.value(dol);
                kw.trigger('change');
            }
        }
    }
    ```
  - Revalidate all party search fields with Bootstrap FormValidation:
    ```javascript
    if (window.$ && $('#personSearchForm').data('formValidation')) {
        const fv = $('#personSearchForm').data('formValidation');
        fv.revalidateField('lastName');
        fv.revalidateField('firstName');
        if (dol) fv.revalidateField('filingDateOnOrAfterP');
    }
    ```

#### Change 2: Robust Search Button Submission
- In Step G:
  - Revalidate fields right before click.
  - Dispatch direct JavaScript click on `document.getElementById("PersonSearchResults").click()`.
  - Also invoke Playwright `search_btn.first.click(force=True)`.
  - Check if form has active validation errors and log them.

#### Change 3: Step H Wait for True Results & Navigation
- Wait for URL navigation away from initial search form (`/PersonSearchResults` or `/Results` in URL) OR specific results elements:
  - Selector: `table:has(th:has-text("Case Number")), #PersonSearchResultsTable, table tbody tr td:first-child button, :has-text("No records found"), :has-text("No cases found")`.
  - Strictly DO NOT use generic `table.table tbody tr` which matches the static glossary table!

#### Change 4: Step J & K Filter Out Glossary Prefix Tables
- When extracting rows:
  - Inspect table headers. If headers contain `"Case Prefix"` or `"Court Type"` without `"Case Number"`, skip the table!
  - If cell 0 is `"CACE"`, `"COCE"`, `"CASE PREFIX"`, or any known glossary prefix, skip the row!
  - Validate that Case Number matches valid court case format (contains digits or is a link/button, not pure prefix like `"CACE"`).

---

## 3. Verification Plan

1. **Automated Unit Tests:**
   - Run `backend/.venv\Scripts\pytest backend/tests/test_broward_portal.py` (ensure 13/13 pass).
   - Run full test suite: `backend/.venv\Scripts\pytest -q` (ensure all 554 pass).
2. **Lint & Type Checks:**
   - Run `backend/.venv\Scripts\ruff check app tests` (0 errors).
   - Run `npm --prefix frontend run lint` & `npx tsc --noEmit` (0 errors).
   - Run `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_ps1_syntax.ps1` (0 errors).
3. **Live Verification:**
   - Re-test Broward portal search with `MARIA MARTINEZ` and DOL `02/27/2022`.
   - Verify that `#PersonSearchResults` triggers form submission, navigates to results, and does NOT scrape the static glossary table.

---

## 4. User Confirmation Required
As mandated by engineering governance (`AGENTS.md` & `diagnose-plan-confirm-execute`), code edits will begin once you confirm approval of this plan.
